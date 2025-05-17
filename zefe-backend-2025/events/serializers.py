from django.db.models import Q
from rest_framework import serializers
from .models import MeetingInformation, MeetingImage, UserNetwork, BaseEvent

from events.models import UserEvent, UserNetwork, MeetingImage
from user.models import User, UserProfile
from django.utils import timezone
from user.models import UserField
from user.serializers import UserProfileSerializer
import traceback
import logging


from django.utils import timezone
from .models import WalletConnection, NetworkingRequest, SpamReport

from user.serializers import UserSerializer  # Add this if not already imported

# Base serializer for common profile fields
class BaseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        abstract = True


class BaseEventSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseEvent
        fields = ["id", "name", "code", "city", "address", "created_date"]


class JoinEventSerializer(serializers.ModelSerializer):
    base_event = BaseEventSummarySerializer(read_only=True)

    class Meta:
        model = UserEvent
        fields = [
            "id",
            "title",
            "description",
            "code",
            "base_event",
            "created_date",
        ]


class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = ["title", "id", "created_date"]

    def validate_title(self, value):
        user = self.context["request"].user
        if UserEvent.objects.filter(title=value, user=user).exists():
            raise serializers.ValidationError("This event already exists for this user")
        return value

    def create(self, validated_data):
        print("CRAEETE EVENT")
        # breakpoint()
        """
        create QR code for the event and save
        """
        user = self.context["request"].user
        return UserEvent.objects.create(user=user, **validated_data)


class UserRetrieveSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["telegram_id", "user_profile"]


class UserEventRetrieveSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source="user.user_profile", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserEvent
        fields = ["user_profile", "title", "user_id"]


logger = logging.getLogger(__name__)  # Use Django's logging system


class UserNetworkCreateSerializer(serializers.Serializer):
    scanned_user_id = serializers.IntegerField()
    base_event_id = serializers.IntegerField(required=False)

    def get_or_create_user_event(self, user, base_event, title, description, code):
        """
        Helper to get or create a UserEvent.
        Returns (UserEvent instance, created boolean).
        """
        user_event = UserEvent.objects.filter(user=user, base_event=base_event).first()
        if user_event:
            logger.info(
                f"UserEvent already exists for user {user.id} and base_event {base_event.id}"
            )
            return user_event, False

        user_event = UserEvent.objects.create(
            user=user,
            base_event=base_event,
            title=title,
            description=description,
            code=code,
        )
        logger.info(
            f"Created new UserEvent for user {user.id} and base_event {base_event.id}"
        )
        return user_event, True

    def create(self, validated_data):
        scanned_user_id = validated_data.get("scanned_user_id")
        base_event_id = validated_data.get("base_event_id")

        logger.info(
            f"Creating UserNetwork: current_user={self.context['request'].user.id}, scanned_user_id={scanned_user_id}, base_event_id={base_event_id}"
        )
        scanned_user = None
        try:
            scanned_user = User.objects.get(id=scanned_user_id)
        except User.DoesNotExist:
            logger.warning(f"Scanned user {scanned_user_id} does not exist.")
            raise serializers.ValidationError(
                {"scanned_user_id": "Scanned user does not exist."}
            )

        base_event = None
        if base_event_id is not None:
            try:
                base_event = BaseEvent.objects.get(id=base_event_id)
            except BaseEvent.DoesNotExist:
                logger.warning(f"Base event {base_event_id} does not exist.")
                raise serializers.ValidationError(
                    {"base_event_id": "Base event does not exist."}
                )

        current_user = self.context["request"].user
        print("Scanned user", scanned_user)
        # Check if a connection already exists
        existing_connection = UserNetwork.objects.filter(
            Q(scanner=current_user, scanned=scanned_user)
            | Q(scanner=scanned_user, scanned=current_user)
        ).first()
        print("Connection", existing_connection)

        if existing_connection:
            logger.info(
                f"Existing UserNetwork found between user {current_user.id} and user {scanned_user.id}."
            )
            return existing_connection

        # Handle UserEvents if base_event exists
        scanner_user_event = None
        scanned_user_event = None

        if base_event:
            scanner_user_event, created = self.get_or_create_user_event(
                current_user,
                base_event,
                base_event.name,
                " ",
                base_event.code,
            )
            if created:
                logger.info(
                    f"UserEvent created for current_user {current_user.id} at base_event {base_event.id}."
                )
            else:
                logger.info(
                    f"UserEvent already existed for current_user {current_user.id} at base_event {base_event.id}."
                )

            scanned_user_event = UserEvent.objects.filter(
                base_event=base_event, user=scanned_user
            ).first()
            if scanned_user_event:
                logger.info(
                    f"Scanned user {scanned_user.id} has an existing UserEvent for base_event {base_event.id}."
                )
            else:
                logger.info(
                    f"No UserEvent found for scanned user {scanned_user.id} for base_event {base_event.id}."
                )

        # Create the UserNetwork connection
        user_network = UserNetwork.objects.create(
            scanner=current_user,
            scanned=scanned_user,
            base_event=base_event,
            scanner_event_title=(
                scanner_user_event.title if scanner_user_event else None
            ),
            scanned_event_title=(
                scanned_user_event.title if scanned_user_event else None
            ),
        )

        MeetingInformation.objects.get_or_create(
            network=user_network,
            defaults={"summary_note": "", "information_saved_user": scanned_user},
        )

        logger.info(
            f"Successfully created UserNetwork between {current_user.id} and {scanned_user.id} with id {user_network.id}."
        )

        return user_network


class UserNetworkResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNetwork
        fields = ["id", "scanner", "scanned", "base_event", "meeting_date"]


class UserNetworkSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    base_event = BaseEventSummarySerializer()

    class Meta:
        model = UserNetwork
        fields = ["base_event", "user"]

    def get_user(self, obj):
        request = self.context.get("request")
        current_user = request.user if request else None

        if not current_user:
            return None  # Or raise an exception depending on your API design

        # Decide who is the "connected" user (the other one)
        if obj.scanner == current_user:
            connected_user = obj.scanned
        else:
            connected_user = obj.scanner

        user_profile = getattr(connected_user, "user_profile")
        project_name = getattr(user_profile, "project_name")
        city = getattr(user_profile, "city")
        # You can now return a dict (custom fields you want)
        return {
            "id": connected_user.id,
            "uuid": connected_user.uuid,
            "name": connected_user.name,
            "username": connected_user.username,
            "photo_url": connected_user.photo_url,
            "user_profile": {"city": city, "project_name": project_name},
        }


class ConnectionSerializer(BaseProfileSerializer):
    """
    Use UserEvent
    """

    class Meta:
        model = UserProfile
        fields = ["name", "position", "company_name", "city"]


class MeetingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingImage
        fields = ["id", "note", "image", "created_date"]


class MeetingInformationDetailSerializer(serializers.ModelSerializer):
    meeting_images = MeetingImageSerializer(many=True, read_only=True)
    network_id = serializers.IntegerField(source="network.id", read_only=True)
    scanned_user = serializers.SerializerMethodField()
    scanner_user = serializers.SerializerMethodField()

    class Meta:
        model = MeetingInformation
        fields = [
            "id",
            "network_id",
            "summary_note",
            "created_date",
            "meeting_images",
            "scanned_user",
            "scanner_user",
        ]

    def get_scanned_user(self, obj):
        return obj.network.scanned.username

    def get_scanner_user(self, obj):
        return obj.network.scanner.username


class MeetingInformationCreateSerializer(serializers.ModelSerializer):
    meeting_images = MeetingImageSerializer(many=True, required=False)
    network_id = serializers.IntegerField()
    base_event_id = serializers.IntegerField()

    class Meta:
        model = MeetingInformation
        fields = ["summary_note", "meeting_images", "network_id", "base_event_id"]

    def create(self, validated_data):
        meeting_images_data = validated_data.pop("meeting_images", [])
        network_id = validated_data.pop("network_id")
        base_event_id = validated_data.pop("base_event_id")
        summary_note = validated_data.pop("summary_note", "")
        user = self.context["request"].user

        print("Base event Id", base_event_id)
        # Find the correct UserNetwork between the two users for this event
        try:
            network = UserNetwork.objects.get(
                base_event_id=base_event_id, id=network_id
            )
        except UserNetwork.DoesNotExist:
            raise serializers.ValidationError(
                "No valid connection found for this event."
            )

        # Either create or update MeetingInformation
        meeting_info, created = MeetingInformation.objects.update_or_create(
            network=network,
            defaults={"summary_note": summary_note, "information_saved_user": user},
        )

        # Optional: delete old images before saving new ones
        meeting_info.meeting_images.all().delete()

        # Save new images
        for image_data in meeting_images_data:
            MeetingImage.objects.create(meeting_information=meeting_info, **image_data)
        return meeting_info


class MeetingInformationSerializer(serializers.ModelSerializer):
    meeting_images = MeetingImageSerializer(many=True, read_only=True)
    information_saved_user_id = serializers.IntegerField(
        source="information_saved_user.id", read_only=True
    )

    class Meta:
        model = MeetingInformation
        fields = [
            "id",
            "summary_note",
            "information_saved_user_id",
            "meeting_images",
            "created_date",
            "updated_date",
        ]


class NetworkInformationSerializer(serializers.ModelSerializer):
    # Fields directly from UserNetwork
    base_event = BaseEventSummarySerializer()
    meeting_informations = serializers.SerializerMethodField()

    class Meta:
        model = UserNetwork
        fields = ["id", "base_event", "meeting_informations"]

    def get_meeting_informations(self, obj):
        mis = MeetingInformation.objects.filter(network=obj)
        return MeetingInformationSerializer(mis, many=True, context=self.context).data


class ConnectedUserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "uuid", "name", "username", "user_profile", "photo_url")


class ConnectedNetworkUserDetailedSerializer(serializers.Serializer):
    user = ConnectedUserSerializer(source="connected_user")
    network_information = NetworkInformationSerializer(source="network")



# Add these serializers to your existing serializers.py
# Add to events/serializers.py
class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users with basic info"""
    position = serializers.CharField(source='userprofile.position', read_only=True)
    position_display = serializers.CharField(source='userprofile.get_position_display', read_only=True)
    company = serializers.CharField(source='userprofile.company', read_only=True)
    bio = serializers.CharField(source='userprofile.bio', read_only=True)
    user_fields = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'photo_url', 
                 'position', 'position_display', 'company', 
                 'bio', 'user_fields']
    
    def get_user_fields(self, obj):
        return [{'id': field.field.id, 'name': field.field.name} 
                for field in obj.user_fields.all()]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for BaseEvent model"""
    attendee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseEvent
        fields = ['id', 'name', 'code', 'city', 'address', 
                 'created_date', 'starting_date', 'ending_date', 
                 'attendee_count']
    
    def get_attendee_count(self, obj):
        return obj.attendees.count()

class WalletConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletConnection
        fields = ['wallet_address', 'last_connected']


class NetworkingRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkingRequest
        fields = ['receiver', 'note_content','request_id', 
            'sender_wallet', 'receiver_wallet', 'escrow_account', 
            'tx_signature'
        ]
        
    def validate(self, attrs):

        # request_id = attrs.pop('request_id', None)
        sender = self.context['request'].user
        receiver = attrs.get('receiver')

        if NetworkingRequest.objects.filter(
            Q(sender=sender, receiver=receiver) | 
            Q(sender=receiver, receiver=sender),
            status=NetworkingRequest.STATUS_PENDING
        ).exists():
            raise serializers.ValidationError("A request already exists between you and this user")
            
        # Check if users are already connected (accepted request in either direction)
        if NetworkingRequest.objects.filter(
            Q(sender=sender, receiver=receiver) | 
            Q(sender=receiver, receiver=sender),
            status=NetworkingRequest.STATUS_ACCEPTED
        ).exists():
            raise serializers.ValidationError("You are already connected with this user")
               
        # Check if sender is banned
        spam_report = SpamReport.objects.filter(reported_user=sender, is_banned=True).first()
        if spam_report:
            raise serializers.ValidationError("Your account has been banned due to spam reports")
        
        if sender.id == receiver.id:
          raise serializers.ValidationError({"receiver": "You cannot send a networking request to yourself"})
    
        print("Validation passed")    
        return attrs


# UPDATED: Removed refund_transaction_id
class NetworkingRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkingRequest
        fields = ['id', 'status']
        read_only_fields = ['id']
        
    def validate_status(self, value):
        valid_responses = [
            NetworkingRequest.STATUS_ACCEPTED,
            NetworkingRequest.STATUS_REJECTED,
            NetworkingRequest.STATUS_SPAM
        ]
        
        if value not in valid_responses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_responses)}")
            
        return value


# UPDATED: Removed transaction_id and amount_staked
class NetworkingRequestDetailSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    receiver_details = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = NetworkingRequest
        fields = [
            'id', 'sender_details', 'receiver_details', 'note_content',
            'status', 'created_date', 'refunded_at', 'request_id', 
            'sender_wallet', 'receiver_wallet', 'escrow_account', 
            'tx_signature'
        ]

    def get_sender_details(self, obj):
        # Create serializer for sender with request_id added
        serializer = UserWithWalletSerializer(obj.sender)
        data = serializer.data
        data['request_id'] = str(obj.request_id or obj.id)  # Add request ID to sender details
        return data
        
    def get_receiver_details(self, obj):
        # Create serializer for receiver with request_id added
        serializer = UserWithWalletSerializer(obj.receiver)
        data = serializer.data
        data['request_id'] = str(obj.request_id or obj.id)  # Add request ID to receiver details
        return data
     

from rest_framework import serializers
from events.models import NetworkingRequest
from django.db.models import Q

class RemoveConnectionSerializer(serializers.Serializer):
    """
    Serializer for removing a single connection between users.
    """
    def validate(self, attrs):
        connection_id = self.context.get('connection_id')
        user = self.context.get('request').user
        
        if not connection_id:
            raise serializers.ValidationError("Connection ID is required")
        
        try:
            # Find the connection that the user wants to remove
            connection = NetworkingRequest.objects.get(
                Q(sender=user) | Q(receiver=user),
                id=connection_id,
                status=NetworkingRequest.STATUS_ACCEPTED
            )
            attrs['connection'] = connection
            return attrs
            
        except NetworkingRequest.DoesNotExist:
            raise serializers.ValidationError("Connection not found or you don't have permission to remove it")        
        
class UserWithWalletSerializer(UserSerializer):
    """Extends UserSerializer to include wallet address (if available)"""
    wallet_address = serializers.SerializerMethodField()
    # request_id = serializers.IntegerField(source='request.id', read_only=True, default=None)
    
    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['wallet_address']
    
    def get_wallet_address(self, user):
        try:
            # First check for WalletConnection
            if hasattr(user, 'wallet'):
                return user.wallet.wallet_address
            
             # If not found, check user_profile
            if hasattr(user, 'user_profile') and user.user_profile.wallet_address:
                return user.user_profile.wallet_address
            
            # If not found, check user_profile
            if hasattr(user, 'user_profile') and user.user_profile.wallet_address:
                return user.user_profile.wallet_address
                
            return None
        except Exception as e:
            print(f"Error getting wallet address: {str(e)}")
            return None

class NetworkingRequestDetailSerializer(serializers.ModelSerializer):
    sender_details = UserWithWalletSerializer(source='sender', read_only=True)
    receiver_details = UserWithWalletSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = NetworkingRequest
        fields = [
            'id', 'sender_details', 'receiver_details', 'note_content',
            'status', 'created_date', 'refunded_at'
        ]

    # def get_sender_details(self, obj):
    #         # Create serializer for sender with request_id added
    #         serializer = UserWithWalletSerializer(obj.sender)
    #         data = serializer.data
    #         data['request_id'] = str(obj.id)  # Add request ID to sender details
    #         return data
        
    # def get_receiver_details(self, obj):
    #         # Create serializer for receiver with request_id added
    #         serializer = UserWithWalletSerializer(obj.receiver)
    #         data = serializer.data
    #         data['request_id'] = str(obj.id)  # Add request ID to receiver details
    #         return data        