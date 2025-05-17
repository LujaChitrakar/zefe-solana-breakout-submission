from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import Field
from .serializers import FieldSerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

# At the top of settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


user = get_user_model()


# Create your views here.
from user.serializers import (
    UserProfileSerializer,
    TelegramUserSerializer,
    UserFeedbackSerializer,
    UserSerializer,
)
from user.models import UserProfile, User, UserFeedback, Field
from events.models import BaseEvent, UserEvent


import requests
import hashlib
import hmac
import time


from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import User, UserProfile, Field, UserField
from events.models import BaseEvent, UserEvent
import hashlib
import hmac
import time
import os


class TelegramLoginView(APIView):
    """
    Endpoint to handle Telegram login data from the web widget
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get auth data from request
        auth_data = request.data
        
        # Extract critical fields
        telegram_id = auth_data.get('id')
        first_name = auth_data.get('first_name', '')
        last_name = auth_data.get('last_name', '')
        username = auth_data.get('username', '')
        photo_url = auth_data.get('photo_url', '')
        auth_date = auth_data.get('auth_date', 0)
        hash_value = auth_data.get('hash', '')
        is_staff = auth_data.get('is_staff', False)
        
        # In production, validate the hash
        if not settings.DEBUG:
            if not self._validate_telegram_hash(auth_data):
                return Response({
                    'status': 'ERROR',
                    'message': 'Invalid authentication data'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check auth_date is recent (within 24 hours)
            if time.time() - int(auth_date) > 86400:
                return Response({
                    'status': 'ERROR',
                    'message': 'Authentication too old'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username or f"tg_{telegram_id}",
                'name': f"{first_name} {last_name}".strip(),
                'photo_url': photo_url,
                'is_staff': is_staff,
                'source':'TELEGRAM'
            }
        )
        
        # If user was found but not created, update fields
        if not created:
            user.name = f"{first_name} {last_name}".strip()
            if photo_url:  # Only update if photo_url is provided
                user.photo_url = photo_url
            if username:  # Only update if username is provided
                user.username = username
            user.is_staff = is_staff    
            user.save()
        
        # Create or update profile using the same safe approach as in TelegramMockLoginView
        try:
            profile = UserProfile.objects.get(user=user)
            # Update existing profile with only valid fields
            profile.position = 'DEVELOPER'  # Default position
            profile.city = 'California'
            profile.save()
            profile_created = False
        except UserProfile.DoesNotExist:
            # Create new profile with only valid fields
            profile = UserProfile.objects.create(
                user=user,
                position='DEVELOPER',
                city='San Francisco'
            )
            profile_created = True
        
        # Add user to admin events (if they exist)
        admin_events = BaseEvent.objects.filter(created_by_admin=True)
        for event in admin_events:
            UserEvent.objects.get_or_create(
                user=user, 
                base_event=event,
                defaults={
                    "title": event.name,
                    "description": "",
                    "code": event.code
                }
            )
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'SUCCESS',
            'message': 'Login successful',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'telegram_id': telegram_id,
                    'photo_url': user.photo_url,
                    'is_new_user': created
                }
               
            }
        }, status=status.HTTP_200_OK)
    
    def _validate_telegram_hash(self, auth_data):
        """Validate Telegram authentication data hash"""
        # Get bot token from settings
        # bot_token = settings.TELEGRAM_BOT_TOKEN
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        
        # Remove hash from data for validation
        data_to_check = auth_data.copy()
        hash_to_validate = data_to_check.pop('hash', '')
        
        # Create data check string
        data_check_list = []
        for key in sorted(data_to_check.keys()):
            data_check_list.append(f"{key}={data_to_check[key]}")
        data_check_string = '\n'.join(data_check_list)
        
        # Create secret key by SHA256 of bot token
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash using HMAC-SHA256
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return computed_hash == hash_to_validate
    
    def test_bot_token(self):
        """Test and print Telegram bot information using the configured token"""
        import requests
        
        # Get bot token from settings
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Make API request to Telegram
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        
        # Print results for debugging
        print(f"Bot Token Test Results:")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Bot is valid!")
            print(f"Bot ID: {bot_info['id']}")
            print(f"Bot Name: {bot_info['first_name']}")
            print(f"Bot Username: @{bot_info['username']}")
            return {
                'valid': True,
                'bot_info': bot_info
            }
        else:
            print(f"❌ Bot token is invalid!")
            print(f"Error: {response.text}")
            return {
                'valid': False,
                'error': response.text
            }
    

class WebLoginWithTelegramView(APIView):
    """
    Endpoint to handle Telegram login for web application users
    This creates users with source='WEB' despite using Telegram authentication
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get auth data from request
        auth_data = request.data
        
        # Extract critical fields
        telegram_id = auth_data.get('id')
        first_name = auth_data.get('first_name', '')
        last_name = auth_data.get('last_name', '')
        username = auth_data.get('username', '')
        photo_url = auth_data.get('photo_url', '')
        auth_date = auth_data.get('auth_date', 0)
        hash_value = auth_data.get('hash', '')
        is_staff = auth_data.get('is_staff', False)
        
        # In production, validate the hash
        if not settings.DEBUG:
            if not self._validate_telegram_hash(auth_data):
                return Response({
                    'status': 'ERROR',
                    'message': 'Invalid authentication data'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check auth_date is recent (within 24 hours)
            if time.time() - int(auth_date) > 86400:
                return Response({
                    'status': 'ERROR',
                    'message': 'Authentication too old'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username or f"tg_{telegram_id}",
                'name': f"{first_name} {last_name}".strip(),
                'photo_url': photo_url,
                'is_staff': is_staff,
                'source': 'WEB'  # Set source to WEB for web users
            }
        )
        
        # If user was found but not created, update fields
        if not created:
            user.name = f"{first_name} {last_name}".strip()
            if photo_url:  # Only update if photo_url is provided
                user.photo_url = photo_url
            if username:  # Only update if username is provided
                user.username = username
            user.is_staff = is_staff
            user.source = 'WEB'  # Ensure source is set to WEB    
            user.save()
        
        # Create or update profile
        try:
            profile = UserProfile.objects.get(user=user)
            # Update existing profile with default values if needed
            profile_created = False
        except UserProfile.DoesNotExist:
            # Create new profile with default values
            profile = UserProfile.objects.create(
                user=user,
                position='DEVELOPER',
                city='San Francisco'
            )
            profile_created = True
        
        # Add user to admin events (if they exist)
        admin_events = BaseEvent.objects.filter(created_by_admin=True)
        for event in admin_events:
            UserEvent.objects.get_or_create(
                user=user, 
                base_event=event,
                defaults={
                    "title": event.name,
                    "description": "",
                    "code": event.code
                }
            )
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        # Get user fields for response
        user_fields = []
        try:
            for field in user.user_fields.all():
                user_fields.append({
                    'id': field.field.id,
                    'name': field.field.name
                })
        except Exception as e:
            print(f"Error retrieving user fields: {str(e)}")
        
        return Response({
            'status': 'SUCCESS',
            'message': 'Web login successful',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'telegram_id': telegram_id,
                    'photo_url': user.photo_url,
                    'is_new_user': created,
                    'source': user.source,
                    'user_fields': user_fields
                }
            }
        }, status=status.HTTP_200_OK)
    
    def _validate_telegram_hash(self, auth_data):
        """Validate Telegram authentication data hash"""
        # Get bot token from settings
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Remove hash from data for validation
        data_to_check = auth_data.copy()
        hash_to_validate = data_to_check.pop('hash', '')
        
        # Create data check string
        data_check_list = []
        for key in sorted(data_to_check.keys()):
            data_check_list.append(f"{key}={data_to_check[key]}")
        data_check_string = '\n'.join(data_check_list)
        
        # Create secret key by SHA256 of bot token
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash using HMAC-SHA256
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return computed_hash == hash_to_validate
    

class TelegramMockLoginView(APIView):
    """
    Test endpoint for Telegram login simulation in Postman
    NOT FOR PRODUCTION USE
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get basic user data from request
        telegram_id = request.data.get('telegram_id')
        
        if not telegram_id:
            return Response({
                'status': 'ERROR',
                'message': 'telegram_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Optional fields for creating/updating user
        name = request.data.get('name', f'Test User {telegram_id}')
        username = request.data.get('username', f'testuser_{telegram_id}')
        photo_url = request.data.get('photo_url', '')
        is_staff = request.data.get('is_staff', False) 
        
        # Create or get user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username,
                'name': name,
                'photo_url': photo_url,
                'is_staff': is_staff 
            }
        )
        
        # Update fields if user exists
        if not created:
            user.name = name
            user.username = username
            if photo_url:
                user.photo_url = photo_url
            user.is_staff = is_staff     
            user.save()

        
        # Create or update profile
        # Only use fields that exist in your UserProfile model
        position = request.data.get('position', 'DEVELOPER')
        city = request.data.get('city', 'San Francisco')
        bio = request.data.get('bio', '') 
        chain_ecosystem = request.data.get('chain_ecosystem', '')  # Add this line
        
        
        # Check if the profile exists
        try:
            profile = UserProfile.objects.get(user=user)
            # Update existing profile
            profile.position = position
            profile.city = city
            profile.bio = bio 
            profile.save()
            profile_created = False
        except UserProfile.DoesNotExist:
            # Create new profile with only valid fields
            profile = UserProfile.objects.create(
                user=user,
                position=position,
                city=city,
                bio=bio, 
                chain_ecosystem=chain_ecosystem if chain_ecosystem else None  
            )
            profile_created = True
        
        # Add fields if they're provided
        if 'fields' in request.data and isinstance(request.data['fields'], list):
            # Clear existing fields first (optional)
            UserField.objects.filter(user=user).delete()
            
            # Add new fields
            for field_name in request.data['fields']:
                try:
                    # First try to get the field by name
                    field = Field.objects.filter(name=field_name).first()
                    if not field:
                        # If field doesn't exist, create it
                        field = Field.objects.create(name=field_name, code=field_name)
                    # Create user-field relation
                    UserField.objects.get_or_create(user=user, field=field)
                except Exception as e:
                    print(f"Error adding field {field_name}: {str(e)}")
                    continue
        # Add user to admin events
        admin_events = BaseEvent.objects.filter(created_by_admin=True)
        for event in admin_events:
            UserEvent.objects.get_or_create(
                user=user, 
                base_event=event,
                defaults={
                    "title": event.name,
                    "description": "",
                    "code": event.code
                }
            )
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'SUCCESS',
            'message': 'Mock login successful (FOR TESTING ONLY)',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'telegram_id': telegram_id,
                    'photo_url': user.photo_url,
                    'position': position,
                    'city': city,
                    'created': created
                }
            }
        }, status=status.HTTP_200_OK)

class TestAPIView(APIView):
    """
    Test API view to check if the server is running
    """

    def get(self, request, *args, **kwargs):
        return Response(
            {"status": "success", "message": "Server is running"},
            status=status.HTTP_200_OK,
        )


class TelegramUserCreateView(APIView):
    """
    This is simple init Api that create user from telegram_id and retun access_token and refresh_token
    if user is already created then it will return access_token and refresh_token
    """
    permission_classes = []
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print("Data", json.dumps(data, indent=3))
        telegram_id = data.get("telegram_id")
        if not telegram_id:
            return Response(
                {"status": "FAILURE", "message": "telegram_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(telegram_id=telegram_id).first()
        if not user:
            # If user does not exist, create a new user
            serializer = TelegramUserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        else:
            serializer = TelegramUserSerializer(user)
        refresh = RefreshToken.for_user(user)
        response_obj = {
            "data": serializer.data,
        }

        admin_events = BaseEvent.objects.filter(created_by_admin=True)
        for e in admin_events:
            UserEvent.objects.get_or_create(
                user=user, 
                base_event=e,
                defaults={
                    "title": e.name,
                    "description": " ",
                    "code": e.code
                }
            )

        response_obj["data"]["access_token"] = str(refresh.access_token)
        response_obj["data"]["refresh_token"] = str(refresh)
        return Response(response_obj, status=status.HTTP_200_OK)

class UserPositionsView(APIView):
    def get(self, request):
        from user.models import UserProfile
        return Response({
            'positions': [pos[0] for pos in UserProfile.USER_POSITION]
        })

class UserProfileView(APIView):
    """
    Create and Get User Profile Data
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the User Profile
        """
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(user_profile)

        data = {**user_serializer.data, "user_profile": profile_serializer.data}

        return Response(
            {
                "status": "success",
                "created": created,
                "data": data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        """
        Update User Profile
        """
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_fields = ["name", "username", "email", "photo_url", "telegram_id"]
        for field in user_fields:
            if field in request.data:
                setattr(user, field, request.data.pop(field))
        user.save()

        serializer = UserProfileSerializer(
            user_profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Re-serialize both user and user_profile for consistent response
        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(user_profile)

        data = {**user_serializer.data, "user_profile": profile_serializer.data}

        return Response(
            {
                "status": "success",
                "created": created,
                "data": data,
            },
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )

class UserOnboardingView(APIView):
    """
    Handle user onboarding after Telegram login
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request):
        user = request.user
        data = request.data

         # Check email uniqueness before updating user
        if 'email' in data:
            email = data.get('email')
            # Only check if the email is different from the user's current email
            if email != user.email:  
                # Check if another user has this email
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response({
                        'status': 'ERROR',
                        'message': 'Email already in use',
                        'field': 'email'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update User model fields
        if 'full_name' in data:
            user.name = data.get('full_name')
        if 'telegram_username' in data:
            user.username = data.get('telegram_username')
        if 'avatar_url' in data:
            user.photo_url = data.get('avatar_url')
        if 'email' in data:
            user.email = data.get('email')
        user.save()
        
        # Get or create UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update profile fields from request data
        if 'city' in data:
            profile.city = data.get('city')
        if 'bio' in data:
            profile.bio = data.get('bio')
        if 'position' in data:
            profile.position = data.get('position')
        if 'project_name' in data:
            profile.project_name = data.get('project_name')
        if 'chain_ecosystem' in data:
            profile.chain_ecosystem = data.get('chain_ecosystem')
        if 'twitter_username' in data:
            profile.twitter_account = data.get('twitter_username')
        if 'linkedin_url' in data:
            profile.linkedin_url = data.get('linkedin_url')
        if 'email' in data:
             profile.email = data.get('email')
        if 'wallet_address' in data:
            profile.wallet_address = data.get('wallet_address')
        if 'telegram_account' in data:
            profile.telegram_account = data.get('telegram_account')
        elif 'telegram_username' in data:
            profile.telegram_account = data.get('telegram_username')
        if 'company_name' in data:
            profile.company_name = data.get('company_name')
        if 'gender' in data:
            profile.gender = data.get('gender')
        
        profile.save()
        
        # Handle verticals/fields
        if 'verticals' in data and isinstance(data['verticals'], list):
            # Clear existing fields
            UserField.objects.filter(user=user).delete()
            
            # Add new fields
            for field_name in data['verticals']:
                field, _ = Field.objects.get_or_create(name=field_name)
                UserField.objects.get_or_create(user=user, field=field)
        
        # Get updated user fields for response
        user_fields = Field.objects.filter(field_users__user=user).values_list('name', flat=True)
        
        # Return updated profile data
        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(profile)
        
        return Response({
            'status': 'SUCCESS',
            'message': 'Profile updated successfully',
            'data': {
                **user_serializer.data,
                'user_profile': profile_serializer.data,
                'verticals': list(user_fields)
            }
        })
    
    def put(self, request):
        """Update user profile during onboarding process"""
        user = request.user
        data = request.data
        
        # Check email uniqueness before updating user
        if 'email' in data:
            email = data.get('email')
            # Only check if the email is different from the user's current email
            if email != user.email:  
                # Check if another user has this email
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response({
                        'status': 'ERROR',
                        'message': 'Email already in use',
                        'field': 'email'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update User model fields
        if 'full_name' in data:
            user.name = data.get('full_name')
        if 'telegram_username' in data:
            user.username = data.get('telegram_username')
        if 'avatar_url' in data:
            user.photo_url = data.get('avatar_url')
        if 'email' in data:
            user.email = data.get('email')
        user.save()
        
        # Get or create UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update profile fields from request data
        if 'city' in data:
            profile.city = data.get('city')
        if 'bio' in data:
            profile.bio = data.get('bio')
        if 'position' in data:
            profile.position = data.get('position')
        if 'project_name' in data:
            profile.project_name = data.get('project_name')
        if 'chain_ecosystem' in data:
            profile.chain_ecosystem = data.get('chain_ecosystem')
        if 'twitter_username' in data:
            profile.twitter_account = data.get('twitter_username')
        if 'linkedin_url' in data:
            profile.linkedin_url = data.get('linkedin_url')
        if 'telegram_account' in data:
            profile.telegram_account = data.get('telegram_account')
        elif 'telegram_username' in data:
            profile.telegram_account = data.get('telegram_username')
        if 'company_name' in data:
            profile.company_name = data.get('company_name')
        if 'gender' in data:
            profile.gender = data.get('gender')
        if 'email' in data:
            profile.email = data.get('email')
        if 'wallet_address' in data:
            profile.wallet_address = data.get('wallet_address')
        if 'telegram_account' in data:
            profile.telegram_account = data.get('telegram_account')
        if 'company_name' in data:
            profile.company_name = data.get('company_name')
        if 'gender' in data:
            profile.gender = data.get('gender')
        
        profile.save()
        
        # Handle verticals/fields
        if 'verticals' in data and isinstance(data['verticals'], list):
            # Clear existing fields
            UserField.objects.filter(user=user).delete()
            
            # Add new fields
            for field_name in data['verticals']:
                field, _ = Field.objects.get_or_create(name=field_name)
                UserField.objects.get_or_create(user=user, field=field)
        
        # Get updated user fields for response
        user_fields = Field.objects.filter(field_users__user=user).values_list('name', flat=True)
        
        # Return updated profile data
        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(profile)
        
        return Response({
            'status': 'SUCCESS',
            'message': 'Profile updated successfully during onboarding',
            'data': {
                **user_serializer.data,
                'user_profile': profile_serializer.data,
                'verticals': list(user_fields)
            }
        })

class UserFeedbackView(APIView):
    """
    Create and Get User Feedback Data
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle the feedback creation
        """
        user = request.user
        # Validate and serialize the incoming feedback data
        serializer = UserFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            # Add the authenticated user as the feedback user
            serializer.save(user=user)
            return Response(
                {
                    "status": "success",
                    "msg": "Feedback created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"status": "error", "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request, *args, **kwargs):
        """
        Fetch all feedback for the logged-in user
        """
        user_feedbacks = UserFeedback.objects.filter(user=request.user).first()
        serializer = UserFeedbackSerializer(user_feedbacks)
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )

class FieldListView(APIView):
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        fields = Field.objects.all()
        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data)


class WebUserProfileView(APIView):
    """
    API endpoint for web users to retrieve and update their profile information.
    Returns comprehensive user data including all profile fields.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retrieve full user profile information for web interface"""
        user = request.user
        
        try:
            # Get user profile - create if it doesn't exist
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Safely get user fields with categories
            user_fields = []
            try:
                if hasattr(user, 'user_fields'):
                    for user_field in user.user_fields.all().select_related('field'):
                        field_data = {
                            'id': user_field.field.id,
                            'name': user_field.field.name
                        }
                        # Only add category if it exists
                        if hasattr(user_field.field, 'category'):
                            field_data['category'] = user_field.field.category
                        user_fields.append(field_data)
            except Exception as field_error:
                print(f"Error getting user fields: {str(field_error)}")
                # Continue without fields data
            
            # Safely build user data with getattr to handle missing attributes
            user_data = {
                'id': user.id,
                'uuid': str(getattr(user, 'uuid', '')),
                'email': getattr(user, 'email', ''),
                'name': getattr(user, 'name', ''),
                'username': getattr(user, 'username', ''),
                'telegram_id': getattr(user, 'telegram_id', ''),
                'photo_url': getattr(user, 'photo_url', ''),
                'is_active': getattr(user, 'is_active', True),
                'is_staff': getattr(user, 'is_staff', False)
            }
            
            # Only add date_joined if it exists
            if hasattr(user, 'date_joined'):
                user_data['date_joined'] = user.date_joined
            
            # Safely build profile data
            profile_data = {
                'bio': getattr(profile, 'bio', None),
                'position': getattr(profile, 'position', None),
                'project_name': getattr(profile, 'project_name', None),
                'city': getattr(profile, 'city', None),
                'telegram_account': getattr(profile, 'telegram_account', None),
                'linkedin_url': getattr(profile, 'linkedin_url', None),
                'twitter_account': getattr(profile, 'twitter_account', None),
                'email': getattr(profile, 'email', None),
                'company_name': getattr(profile, 'company_name', None),
                'wallet_address': getattr(profile, 'wallet_address', None)
            }
            
            # Only add gender if it exists
            if hasattr(profile, 'gender'):
                profile_data['gender'] = profile.gender
            
            # Build final response data
            response_data = {
                'user': user_data,
                'profile': profile_data,
                'fields': user_fields
            }
            
            # Safely add requests counts
            try:
                if hasattr(user, 'received_requests'):
                    response_data['received_requests_count'] = user.received_requests.filter(status='pending').count()
                if hasattr(user, 'sent_requests'):
                    response_data['sent_requests_count'] = user.sent_requests.filter(status='pending').count()
            except Exception as req_error:
                print(f"Error getting request counts: {str(req_error)}")
                # Continue without these counts
            
            # Safely include profile image URL if available
            if hasattr(profile, 'user_image') and profile.user_image:
                try:
                    response_data['profile']['profile_image_url'] = request.build_absolute_uri(profile.user_image.url)
                except Exception as img_error:
                    print(f"Error getting profile image URL: {str(img_error)}")
                    # Continue without image URL
            
            return Response({
                'status': 'success',
                'message': 'User profile retrieved successfully',
                'data': response_data
            })
            
        except Exception as e:
            import traceback
            print(f"Profile retrieval error: {str(e)}")
            print(traceback.format_exc())  # Print full traceback for debugging
            return Response({
                'status': 'error',
                'message': 'Failed to retrieve user profile',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)