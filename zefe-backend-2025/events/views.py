from django.shortcuts import render
from django.db.models import Q, Prefetch

from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from events.serializers import (
    UserEventSerializer,
    UserNetworkSerializer,
    UserNetworkCreateSerializer,
    MeetingInformationCreateSerializer,
    MeetingInformationDetailSerializer
)
from events.serializers import (
    JoinEventSerializer,
    UserNetworkSerializer,
    UserNetworkResponseSerializer,
)
from events.models import UserEvent, UserNetwork, BaseEvent
from events.filters import UserNetworkFilter
from events.utils import normalize_code
from user.models import UserProfile
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.utils import StandardResultsSetPagination
from .models import MeetingInformation, UserNetwork
from .serializers import (
    ConnectedNetworkUserDetailedSerializer,
)
import traceback
from user.models import User

from .models import WalletConnection, NetworkingRequest, SpamReport
from .serializers import (
    WalletConnectionSerializer,
    NetworkingRequestCreateSerializer,
    NetworkingRequestResponseSerializer,
    NetworkingRequestDetailSerializer,
    EventSerializer,
    UserListSerializer
)
from django.utils import timezone
from core.services.solana_service import SolanaService
import uuid
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Case, When, IntegerField
from user.models import User, UserProfile, Field, UserField



class NotificationCountView(APIView):
    """Get count of pending networking requests for the notification badge"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Count pending networking requests received by the user
        # These are messages that need a response (accept, reject, or spam)
        requests_count = NetworkingRequest.objects.filter(
            receiver=request.user,
            status=NetworkingRequest.STATUS_PENDING
        ).count()
        
        return Response({
            'status': 'success',
            'data': {
                'unread_count': requests_count,
                'message': f"You have {requests_count} unread message request{'s' if requests_count != 1 else ''}"
            }
        })


class AttendeesListView(APIView):
    """List and filter attendees for events"""
    permission_classes = []
    
    def get(self, request):
        # Change default from 'WEB' to 'TELEGRAM'
        source = request.query_params.get('source', 'TELEGRAM').upper()

        from user.models import User
        valid_sources = dict(User.USER_SOURCE_CHOICES).keys()
        if source not in valid_sources:
            source = 'TELEGRAM'  # Default to TELEGRAM if invalid source provided

        # Get base queryset
        event_id = request.query_params.get('event')
        
        if event_id:
            # Filter by specific event and add ordering
            users = User.objects.filter(events__id=event_id).exclude(id=request.user.id).distinct().order_by('id')
        else:
            # All users except current user with ordering
            users = User.objects.exclude(id=request.user.id).distinct().order_by('id')
        
        # Apply source filter
        users = users.filter(source=source)
        
        # Apply filters
        # 1. Role/Position filter
        position = request.query_params.get('position')
        if position:
            users = users.filter(user_profile__position=position)
            
        # 2. Fields/Verticals filter
        fields = request.query_params.getlist('fields', [])
        if fields:
            users = users.filter(user_fields__field__id__in=fields).distinct()
            
        # 3. Chain ecosystem filter
        chain = request.query_params.get('chain')
        if chain:
            users = users.filter(user_profile__chain_ecosystem=chain)
            
        # 4. City filter
        cities = request.query_params.getlist('city',[])
        if cities:
            city_query = Q()
            for city in cities:
                city_query |= Q(user_profile__city=city)  # Exact match for choice field
            users = users.filter(city_query)
            
        # 5. Add search functionality
        search = request.query_params.get('search')
        if search:
            users = users.filter(
                Q(name__icontains=search) | 
                Q(username__icontains=search) |
                Q(user_profile__project_name__icontains=search) |
                Q(user_profile__bio__icontains=search)
            ).distinct()
        
        # Maintain ordering after all filters are applied
        users = users.order_by('id')

        total_users_count = users.count()
        
        # Paginate results
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(users, request)

        # Get all spam reports in a single efficient query
        spam_reports = {}
        if request.user.is_staff or request.user.is_superuser:
            spam_reports = {
                report.reported_user_id: report 
                for report in SpamReport.objects.filter(
                    reported_user_id__in=[user.id for user in result_page]
                )
            }
        
        # Get serialized user data with profiles in the same format as UserProfileView
        user_data = []
        for user in result_page:
            # Get user profile
            try:
                profile = user.user_profile
            except:
                profile, _ = UserProfile.objects.get_or_create(user=user)
            
            # Get user fields
            user_fields = []
            for field in user.user_fields.all():
                user_fields.append({
                    'id': field.field.id,
                    'name': field.field.name
                })
            
            # Create base user data dict
            user_info = {
                'id': user.id,
                'email': user.email,
                'uuid': str(user.uuid) if hasattr(user, 'uuid') else None,
                'telegram_id': user.telegram_id,
                'name': user.name,
                'username': user.username,
                'photo_url': user.photo_url,
                'is_active': user.is_active,
                'is_deleted': user.is_deleted,
                'is_staff': user.is_staff,
                'source': user.source,  # Include source in response
                'user_profile': {
                    'position': profile.position,
                    'project_name': profile.project_name if hasattr(profile, 'project_name') else None,
                    'city': profile.city,
                    'telegram_account': profile.telegram_account if hasattr(profile, 'telegram_account') else None,
                    'linkedin_url': profile.linkedin_url if hasattr(profile, 'linkedin_url') else None,
                    'twitter_account': profile.twitter_account if hasattr(profile, 'twitter_account') else None,
                    'email': profile.email if hasattr(profile, 'email') else None,
                    'user_fields': user_fields,
                    'chain_ecosystem': profile.chain_ecosystem if hasattr(profile, 'chain_ecosystem') else None,
                    'company_name': profile.company_name if hasattr(profile, 'company_name') else None,
                    'bio': profile.bio if hasattr(profile, 'bio') else None,
                    'wallet_address': profile.wallet_address if hasattr(profile, 'wallet_address') else None
                }
            }
            
            # Add spam report info only for staff/admin users
            if request.user.is_staff or request.user.is_superuser:
                spam_report = spam_reports.get(user.id)
                user_info['spam_report'] = {
                    'report_count': spam_report.report_count if spam_report else 0,
                    'is_banned': spam_report.is_banned if spam_report else False
                }
            
            user_data.append(user_info)
        
        # Get filter options
        filter_options = {
            'positions': self._get_position_options(),
            'fields': self._get_field_options(),
            'chains': self._get_chain_options(),
            'cities': self._get_city_options(),
            'sources': [{'value': src[0], 'label': src[1]} for src in User.USER_SOURCE_CHOICES]
        }
        
        # Return paginated response
        return paginator.get_paginated_response({
            'status': 'SUCCESS',
            'message': f'{source} Attendees retrieved successfully',
            'total_users': total_users_count,
            'filter_options': filter_options,
            'users': user_data,
            'source': source
        })
    
    # Keep existing helper methods
    def _get_position_options(self):
        """Get all available position options for filtering"""
        try:
            return [{'value': pos[0], 'label': pos[1]} for pos in UserProfile.USER_POSITION]
        except AttributeError:
            return []
    
    def _get_field_options(self):
        """Get all available field/vertical options for filtering"""
        from user.models import Field
        try:
            return list(Field.objects.all().values('id', 'name'))
        except:
            return []
    
    def _get_chain_options(self):
        """Get all available blockchain ecosystem options for filtering"""
        try:
            if hasattr(UserProfile, 'CHAIN_ECOSYSTEM'):
                return [{'value': chain[0], 'label': chain[1]} for chain in UserProfile.CHAIN_ECOSYSTEM]
            return []
        except:
            return []
    
    def _get_city_options(self):
        """Get all available city options from CITY_OPTIONS"""
        from user.models import UserProfile
        try:
            return [{'value': city[0], 'label': city[1]} for city in UserProfile.CITY_OPTIONS]
        except Exception as e:
            print(f"Error getting city options: {str(e)}")
            return []

class SpamReportsView(APIView):
    """View spam reports and banned users"""
    permission_classes = [IsAuthenticated]  # Consider using IsAdminUser here
    
    def get(self, request):
        # Check if user is admin or staff
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'status': 'error',
                'message': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all spam reports
        spam_reports = SpamReport.objects.all().select_related('reported_user')
        
        # Format the data
        reports_data = []
        for report in spam_reports:
            reports_data.append({
                'id': report.id,
                'user_id': report.reported_user.id,
                'user_name': report.reported_user.name,
                'user_username': report.reported_user.username,
                'report_count': report.report_count,
                'is_banned': report.is_banned,
                'last_updated': report.updated_at
            })
        
        return Response({
            'status': 'success',
            'message': 'Spam reports retrieved successfully',
            'data': {
                'reports': reports_data,
                'total_banned': SpamReport.objects.filter(is_banned=True).count(),
                'total_reports': sum(report.report_count for report in spam_reports)
            }
        })
    
    def post(self, request):
        """Admin action to manually ban/unban a user"""
        # Check if user is admin or staff
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'status': 'error',
                'message': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        ban_status = request.data.get('ban', False)
        
        try:
            user = User.objects.get(id=user_id)
            spam_report, created = SpamReport.objects.get_or_create(reported_user=user)
            
            # Update ban status
            spam_report.is_banned = ban_status
            spam_report.save()
            
            return Response({
                'status': 'success',
                'message': f'User {"banned" if ban_status else "unbanned"} successfully',
                'data': {
                    'user_id': user.id,
                    'is_banned': spam_report.is_banned
                }
            })
            
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

class MockTransactionView(APIView):
    """Create mock Solana transactions for testing purposes"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Generate mock transaction ID
            mock_tx_id = f"mock_tx_{uuid.uuid4().hex[:8]}"
            amount = float(request.data.get("amount", 3.0))
            
            # Store this transaction in the user's session for verification
            if not hasattr(request.session, 'mock_transactions'):
                request.session['mock_transactions'] = {}
            
            request.session['mock_transactions'][mock_tx_id] = {
                'amount': amount,
                'created_at': timezone.now().isoformat()
            }
            request.session.modified = True
            
            return Response({
                "status": "success",
                "message": "Mock transaction created",
                "data": {
                    "transaction_id": mock_tx_id,
                    "amount": amount,
                    "status": "confirmed"
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Failed to create mock transaction: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminUserEventListView(generics.ListAPIView):
    """
    List all events created by users

    """

    queryset = UserEvent.objects.all()
    serializer_class = UserEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserEvent.objects.filter(created_by_admin=True)


class EventJoinOrCreateView(generics.ListCreateAPIView):
    serializer_class = JoinEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserEvent.objects.filter(user=self.request.user).filter(base_event__is_active=True)

    def create(self, request, *args, **kwargs):
        title = request.data.get("title")
        city = request.data.get("city")
        address = request.data.get("address")
        description = request.data.get("description")

        if not title:
            return Response(
                {"error": "Title is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate slug-like normalized code
        generated_title = normalize_code(title)
        generated_code = normalize_code(city)
        code = f"{generated_title}_{generated_code}"

        # Get or create BaseEvent based on code + city
        base_event = BaseEvent.objects.filter(code=code, city=city).first()
        if not base_event:
            base_event = BaseEvent.objects.create(
                name=title,
                code=generated_code,
                city=city,
                address=address,
            )

        # Call helper to get or create UserEvent
        user_event, created = self.get_or_create_user_event(
            request.user, base_event, title, description, generated_code
        )

        if not created:
            return Response(
                {"error": "You have already joined this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare and return serialized data
        serializer = self.get_serializer(user_event)
        data = serializer.data
        data["base_event"] = {
            "name": base_event.name,
            "code": base_event.code,
            "city": base_event.city,
            "address": base_event.address,
            "created_date": base_event.created_date,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    def get_or_create_user_event(self, user, base_event, title, description, code):
        """
        Returns a tuple of (UserEvent, created)
        """
        user_event = UserEvent.objects.filter(user=user, base_event=base_event).first()
        if user_event:
            return user_event, False

        user_event = UserEvent.objects.create(
            user=user,
            base_event=base_event,
            title=title,
            description=description,
            code=code,
        )
        return user_event, True


class UserEventRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserEvent.objects.all()
    serializer_class = UserEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserEvent.objects.filter(user=self.request.user)


class UserNetworkCreateView(generics.CreateAPIView):
    serializer_class = UserNetworkCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        response_serializer = UserNetworkResponseSerializer(
            instance, context={"request": request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UserNetworkConnection:
    def __init__(self, user, network):
        self.user = user
        self.network = network


class UserNetworkConnectionView(generics.ListAPIView):
    serializer_class = UserNetworkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserNetworkFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        return (
            UserNetwork.objects.filter(Q(scanner=user) | Q(scanned=user))
            .select_related("scanner", "scanned", "base_event")
            .prefetch_related(
                "scanned__user_profile",
                "scanned__user_fields__field",
                Prefetch(
                    "base_event__user_events",
                    queryset=UserEvent.objects.filter(user=user),
                    to_attr="user_custom_events",
                ),
            )
            .select_related("scanned__user_profile")
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        user = request.user
        qs = self.get_queryset()

        # Extract filter options from scanned users
        cities = qs.values_list("scanned__user_profile__city", flat=True).distinct()
        positions = qs.values_list(
            "scanned__user_profile__position", flat=True
        ).distinct()
        fields = qs.values_list(
            "scanned__user_fields__field__name", flat=True
        ).distinct()
        events = (
            UserEvent.objects.filter(user=user)
            .values_list("title", flat=True)
            .distinct()
        )

        response.data = {
            "filters": {
                "cities": sorted(filter(None, cities)),
                "positions": sorted(filter(None, positions)),
                "fields": sorted(filter(None, fields)),
                "events": sorted(filter(None, events)),
            },
            "connections": response.data,
        }
        return response


class ConnectedNetworkUserDetailedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the connected user's detailed profile
        and the network relationship including meeting images and notes.
        """
        try:
            connected_network_user_id = kwargs["connected_network_user_id"]
            current_user = request.user  # ✅ Correct way
            connected_user = User.objects.filter(id=connected_network_user_id).first()

            if not connected_user:
                return Response({"detail": "Connected user not found."}, status=status.HTTP_404_NOT_FOUND)

            # Now find the UserNetwork BETWEEN current_user and connected_user
            user_network = (
                UserNetwork.objects.select_related("scanner", "scanned", "base_event")
                .prefetch_related(
                    "scanner__user_profile",
                    "scanned__user_profile",
                    "scanner__user_fields__field",
                    "scanned__user_fields__field",
                    Prefetch(
                        "base_event__user_events",
                        queryset=UserEvent.objects.filter(user=request.user),
                        to_attr="user_custom_events",
                    ),
                    "images__meeting_images",  # MeetingInformation and its MeetingImages
                )
                .filter(
                    Q(scanner=current_user, scanned=connected_user)
                    | Q(scanner=connected_user, scanned=current_user)
                )
                .first()
            )

            if not user_network:
                return Response({"detail": "Network connection not found."}, status=status.HTTP_404_NOT_FOUND)
            print("con", connected_user)
            serializer = ConnectedNetworkUserDetailedSerializer(
                {
                    "connected_user": connected_user,
                    "network": user_network,
                },
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("e", e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MeetingInformationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get meeting information for the logged-in user (either as scanner or scanned).
        Optionally filter with `target_user_id` as query param.
        """
        user = request.user
        network_id = kwargs["network_id"]

        # Get the connection (UserNetwork)
        network = (
            UserNetwork.objects.filter(base_event__isnull=False)
            .filter(id=network_id)
            .first()
        )

        if not network:
            return Response(
                {"error": "No connection found between users."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get or create the MeetingInformation
        meeting_info = MeetingInformation.objects.filter(
            network=network
        ).first()

        serializer = MeetingInformationDetailSerializer(meeting_info)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MeetingInformationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MeetingInformationCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        meeting_info = serializer.save()
        response_data = MeetingInformationDetailSerializer(meeting_info).data
        response_data["message"] = "User's selfie and notes has been saved."
        return Response(response_data, status=status.HTTP_201_CREATED)


# Add these views to your existing views.py

class WalletConnectionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = WalletConnectionSerializer(data=request.data)
            
            if serializer.is_valid():
                # Get or create wallet connection
                wallet, created = WalletConnection.objects.update_or_create(
                    user=request.user,
                    defaults={'wallet_address': serializer.validated_data['wallet_address']}
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Wallet connected successfully',
                    'data': {
                        'wallet_address': wallet.wallet_address,
                        'last_connected': wallet.last_connected
                    }
                }, status=status.HTTP_200_OK)
                
            print(f"Wallet connection errors: {serializer.errors}")
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors,
                'detail': str(serializer.errors)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Wallet connection exception: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Server error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendNetworkingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Add debug logging
            print("=== DEBUG: SendNetworkingRequestView ===")
            print(f"Request user: {request.user.id} - {request.user.name or request.user.username}")
            print(f"Request data: {request.data}")
            
            # Create a mutable copy of request.data
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
            # Generate a unique request_id or ensure existing one is unique
            import uuid
            if 'request_id' not in data or not data['request_id']:
                # Generate a new request_id if not provided
                data['request_id'] = f"req_{uuid.uuid4().hex}"
            
            # Check if the request_id already exists and generate a new one if it does
            while NetworkingRequest.objects.filter(request_id=data['request_id']).exists():
                data['request_id'] = f"req_{uuid.uuid4().hex}"
                print(f"Generated new unique request_id: {data['request_id']}")
            
            # Validate required fields for blockchain data
            required_fields = ['receiver', 'note_content']
            
            # Check for required fields
            for field in required_fields:
                if field not in data:
                    return Response({
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if receiver exists
            try:
                receiver = User.objects.get(pk=data.get('receiver'))
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': f'User with ID {data.get("receiver")} does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = NetworkingRequestCreateSerializer(
                data=data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                # Check if sender has already sent a request to this receiver
                receiver_id = serializer.validated_data.get('receiver').id
                if not request.user.is_staff:
                    existing_request = NetworkingRequest.objects.filter(
                        sender=request.user,
                        receiver_id=receiver_id,
                        status=NetworkingRequest.STATUS_PENDING
                    ).exists()
                    
                    if existing_request:
                        return Response({
                            'status': 'error',
                            'message': 'You have already sent a request to this user'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if sender is banned
                if not request.user.is_staff:
                    spam_report = SpamReport.objects.filter(
                        reported_user=request.user, 
                        is_banned=True
                    ).first()
                    
                    if spam_report:
                        return Response({
                            'status': 'error',
                            'message': 'Your account has been banned from sending requests'
                        }, status=status.HTTP_403_FORBIDDEN)
                
                # Check if users are already connected
                existing_connection = NetworkingRequest.objects.filter(
                    (Q(sender=request.user, receiver_id=receiver_id) |
                    Q(sender_id=receiver_id, receiver=request.user)),
                    status=NetworkingRequest.STATUS_ACCEPTED
                ).exists()
                
                if existing_connection:
                    return Response({
                        'status': 'error',
                        'message': 'You are already connected with this user'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Add sender before saving
                networking_request = serializer.save(
                    sender=request.user,
                    status=NetworkingRequest.STATUS_PENDING,
                    # Save blockchain fields with the potentially modified request_id
                    request_id=data.get('request_id'),
                    sender_wallet=data.get('sender_wallet'),
                    receiver_wallet=data.get('receiver_wallet'),
                    escrow_account=data.get('escrow_account'),
                    tx_signature=data.get('tx_signature')
                )
                
                # Log success
                print(f"SUCCESS: Created networking request ID {networking_request.id}")
                
                return Response({
                    'status': 'SUCCESS',
                    'message': 'Networking request sent successfully',
                    'data': NetworkingRequestDetailSerializer(networking_request).data
                }, status=status.HTTP_201_CREATED)
            
            # Handle validation errors
            print(f"ERROR: Serializer validation failed - {serializer.errors}")
            return Response({
                'status': 'FAILURE',
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data',
                'data': {},
                'error_data': serializer.errors,
                'error_message': str(serializer.errors),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Capture and log the full exception
            import traceback
            print(f"CRITICAL ERROR in SendNetworkingRequestView: {str(e)}")
            print(traceback.format_exc())
            
            return Response({
                'status': 'FAILURE',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Server error occurred',
                'data': {},
                'error_data': {},
                'error_message': str(e) if settings.DEBUG else "Internal server error",
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class NetworkingRequestDebugView(APIView):
    """Debug endpoint to check networking request serializer fields"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check what fields are expected in serializer
        serializer = NetworkingRequestCreateSerializer()
        field_info = {name: str(field) for name, field in serializer.fields.items()}
        
        return Response({
            "expected_fields": field_info,
            "model_fields": [f.name for f in NetworkingRequest._meta.fields],
            "your_user_id": request.user.id,
            "available_receivers": list(User.objects.exclude(id=request.user.id).values('id', 'name')[:5])
        })    

class ReceivedNetworkingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NetworkingRequestDetailSerializer
    
    def get_queryset(self):
        return NetworkingRequest.objects.filter(
            receiver=self.request.user,
            status=NetworkingRequest.STATUS_PENDING
        )
    
class WalletDebugView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check what fields are expected in serializer
        serializer = WalletConnectionSerializer()
        field_info = {name: str(field) for name, field in serializer.fields.items()}
        
        return Response({
            "expected_fields": field_info,
            "model_fields": [f.name for f in WalletConnection._meta.fields],
            "your_user_id": request.user.id
        })    


class RespondToNetworkingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, request_id):
        try:
            networking_request = NetworkingRequest.objects.get(
                id=request_id,
                receiver=request.user,
                status=NetworkingRequest.STATUS_PENDING
            )
        except NetworkingRequest.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Networking request not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = NetworkingRequestResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data.get('status')
            networking_request.status = new_status
            
            # Handle refund_transaction_id if provided
            if 'refund_transaction_id' in serializer.validated_data:
                networking_request.refund_transaction_id = serializer.validated_data['refund_transaction_id']
                networking_request.refunded_at = timezone.now()
            
            networking_request.save()
            
            # Update spam reports if marked as spam
            if new_status == NetworkingRequest.STATUS_SPAM:
                spam_report, created = SpamReport.objects.get_or_create(reported_user=networking_request.sender)
                spam_report.report_count += 1
                
                # Ban user if they have 15+ spam reports
                if spam_report.report_count >= 15:
                    spam_report.is_banned = True
                    
                spam_report.save()
                
                # Mark for delayed refund
                networking_request.is_refund_delayed = True
                networking_request.save(update_fields=['is_refund_delayed'])
            
            return Response({
                'status': 'success',
                'message': f'Request marked as {new_status}',
                'data': NetworkingRequestDetailSerializer(networking_request).data
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'error',
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class TransactionStatusView(APIView):
    """Check the status of a Solana transaction"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, transaction_id):
        solana_service = SolanaService()
        
        # Platform wallet address for verification
        platform_wallet = "YourPlatformWalletAddressHere"  # Replace with actual address
        
        # Verify the transaction (simplified)
        is_valid = solana_service.verify_transaction(
            transaction_id=transaction_id,
            amount=None,  # Don't check amount in status endpoint
            recipient=platform_wallet
        )
        
        return Response({
            "transaction_id": transaction_id,
            "is_valid": is_valid,
            "status": "confirmed" if is_valid else "not_found"
        })   
    
class NetworkingHealthCheckView(APIView):
    """
    Debug endpoint to check if networking prerequisites are met
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Check wallet connection
        wallet = WalletConnection.objects.filter(user=user).first()
        
        # Check for a second user to test with
        other_users = User.objects.exclude(id=user.id).values('id', 'name')[:5]
        
        # Check for available events
        events = BaseEvent.objects.all().values('id', 'name', 'code')[:5]
        
        return Response({
            'status': 'success',
            'user_id': user.id,
            'has_wallet': wallet is not None,
            'wallet_address': wallet.wallet_address if wallet else None,
            'available_users': list(other_users),
            'available_events': list(events),
            'instructions': 'Use these IDs in your networking request'
        })    
    

# Add to events/views.py

class SentNetworkingRequestsView(APIView):
    """Get all networking requests sent by the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sent_requests = NetworkingRequest.objects.filter(sender=request.user)
        serializer = NetworkingRequestDetailSerializer(sent_requests, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Sent networking requests retrieved successfully',
            'data': serializer.data
        })

class BrowseUsersView(APIView):
    """Browse other users attending the same events"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get events the current user is attending
        user_events = BaseEvent.objects.filter(attendees=request.user)
        
        # Find other users attending these events
        other_users = User.objects.filter(events__in=user_events).exclude(id=request.user.id).distinct()
        
        # Get fields for filtering
        fields = request.query_params.getlist('fields', [])
        if fields:
            other_users = other_users.filter(fields__id__in=fields)
            
        # Get city for filtering
        city = request.query_params.get('city')
        if city:
            other_users = other_users.filter(city__icontains=city)
        
        # Serialize the result
        serializer = UserListSerializer(other_users, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Users retrieved successfully',
            'data': serializer.data
        })

class FilterUsersView(APIView):
    """Filter users by tags, roles, or interests"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        
        # Filter by fields (interests)
        fields = request.query_params.getlist('fields', [])
        if fields:
            users = users.filter(fields__id__in=fields)
        
        # Filter by position (role)
        position = request.query_params.get('position')
        if position:
            users = users.filter(position=position)
        
        # Filter by tags
        tags = request.query_params.getlist('tags', [])
        if tags:
            users = users.filter(tags__name__in=tags)
        
        serializer = UserListSerializer(users, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Filtered users retrieved successfully',
            'data': serializer.data
        })

class JoinEventByCodeView(APIView):
    """Join an event using its code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, code):
        try:
            event = BaseEvent.objects.get(code=code)
            
            # Check if user is already attending
            if request.user in event.attendees.all():
                return Response({
                    'status': 'success',
                    'message': 'You are already attending this event',
                    'data': EventSerializer(event).data
                })
                
            # Add user to event
            event.attendees.add(request.user)
            
            return Response({
                'status': 'success',
                'message': 'Successfully joined the event',
                'data': EventSerializer(event).data
            })
            
        except BaseEvent.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Event not found with this code'
            }, status=status.HTTP_404_NOT_FOUND)    
        
class MyConnectionsView(APIView):
    """
    Get all connections (accepted networking requests) for the current user.
    A connection is formed when either:
    1. User sends a request that gets accepted
    2. User accepts a request from someone else
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all connections where the current user is either sender or receiver
        # and the status is 'accepted'
        connections = NetworkingRequest.objects.filter(
            (Q(sender=request.user) | Q(receiver=request.user)),
            status=NetworkingRequest.STATUS_ACCEPTED
        ).select_related('sender', 'receiver')
        
        # Prepare the response data
        connection_data = []
        for connection in connections:
            # Determine who the "other person" is in this connection
            other_user = connection.receiver if connection.sender == request.user else connection.sender
            
            # Initialize profile as None
            profile = None
            
            # Get relevant user profile details safely
            try:
                profile = other_user.user_profile
                telegram_account = profile.telegram_account or other_user.username
            except:
                telegram_account = other_user.username
            
            # Get user fields if available
            user_fields = []
            try:
                for field in other_user.user_fields.all():
                    user_fields.append({
                        'id': field.field.id,
                        'name': field.field.name
                    })
            except:
                pass  # No fields available
            
            # Create user data dictionary
            user_data = {
                'id': other_user.id,
                'name': other_user.name,
                'username': other_user.username,
                'photo_url': other_user.photo_url,
                'telegram_account': telegram_account,
                'telegram_id': other_user.telegram_id, 
                'position': getattr(getattr(other_user, 'user_profile', None), 'position', None),
                'bio': getattr(getattr(other_user, 'user_profile', None), 'bio', None),
                'user_fields': user_fields
            }
            
            # Only add profile-related fields if profile exists
            if profile:
                profile_data = {
                    'project_name': getattr(profile, 'project_name', None),
                    'company_name': getattr(profile, 'company_name', None),
                    'city': getattr(profile, 'city', None),
                    'linkedin_url': getattr(profile, 'linkedin_url', None),
                    'twitter_account': getattr(profile, 'twitter_account', None),
                    'wallet_address': getattr(profile, 'wallet_address', None),
                    'chain_ecosystem': getattr(profile, 'chain_ecosystem', None),
                }
                user_data.update(profile_data)
            
            connection_data.append({
                'id': connection.id,
                'connection_date': connection.updated_date,  # When the request was accepted
                'user': user_data,
                'note': connection.note_content,
                # Include whether the current user is the sender or receiver
                'request_direction': 'sent' if connection.sender == request.user else 'received'
            })
        
        return Response({
            'status': 'success',
            'message': 'Connections retrieved successfully',
            'data': connection_data
        })        
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from events.models import NetworkingRequest
from events.serializers import RemoveConnectionSerializer

class RemoveConnectionView(APIView):
    """
    Remove a specific connection with another user.
    This changes the status from 'accepted' to 'removed'.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, connection_id):
        """
        POST request to remove a specific connection.
        The connection_id should be the ID of the NetworkingRequest object.
        
        This doesn't affect any other connections the user might have.
        """
        # Set up context for the serializer
        context = {
            'request': request,
            'connection_id': connection_id
        }
        
        # Validate the request
        serializer = RemoveConnectionSerializer(data=request.data, context=context)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid request',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the validated connection
        connection = serializer.validated_data['connection']
        
        # Update the status to 'removed'
        connection.status = NetworkingRequest.STATUS_REMOVED
        connection.save()
        
        # Return success response
        return Response({
            'status': 'success',
            'message': 'Connection successfully removed',
            'data': {
                'connection_id': connection_id
            }
        }, status=status.HTTP_200_OK)    