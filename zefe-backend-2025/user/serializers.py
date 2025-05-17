# django core import
from django.contrib.auth.password_validation import validate_password

# third party app import
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import traceback

# app import
from user.models import User, UserProfile, Field, UserField, UserFeedback

from .models import Field

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['id', 'name', 'code', 'description']

class UserFeedbackSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True)

    class Meta:
        model = UserFeedback
        fields = ["id", "description", "image"]


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list with profile details"""
    position = serializers.CharField(source='userprofile.position', read_only=True)
    position_display = serializers.CharField(source='userprofile.get_position_display', read_only=True)
    company = serializers.CharField(source='userprofile.company', read_only=True)
    city = serializers.CharField(source='userprofile.city', read_only=True)
    bio = serializers.CharField(source='userprofile.bio', read_only=True)
    chain_ecosystem = serializers.CharField(source='userprofile.chain_ecosystem', read_only=True)
    chain_ecosystem_display = serializers.CharField(source='userprofile.get_chain_ecosystem_display', read_only=True)
    
    # Change field name from "fields" to "user_fields"
    user_fields = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'username', 'photo_url', 
            'position', 'position_display', 'company', 'city', 
            'bio', 'chain_ecosystem', 'chain_ecosystem_display', 
            'user_fields'  # Using the renamed field here
        ]
    
    # Rename method from get_fields() to get_user_fields()
    def get_user_fields(self, obj):
        user_fields = obj.user_fields.select_related('field').all()
        return [{'id': uf.field.id, 'name': uf.field.name} for uf in user_fields]
    

class TelegramUserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(required=True, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "telegram_id", "name", "username", "photo_url"]

    def validate_telegram_id(self, value):
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("A user with this id already exists.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "uuid",
            "telegram_id",
            "name",
            "username",
            "photo_url",
            "is_active",
            "is_deleted",
            "is_staff",
        ]


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ["id", "name"]


class UserFieldSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)  # Serialize field details
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(), write_only=True, source="field"
    )

    class Meta:
        model = UserField
        fields = ["id", "user", "field", "field_id"]  # Send field_id in requests


class UserProfileSerializer(serializers.ModelSerializer):
    selected_fields = serializers.ListField(
        required=False,
        write_only=True,
        child=serializers.IntegerField(),
    )
    user_fields = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "position",
            "project_name",
            "city",
            "telegram_account",
            "linkedin_url",
            "twitter_account",
            "email",
            "selected_fields",
            "user_fields",
            "company_name",
            "bio",               # Add this
            "wallet_address" 
        ]

    def create(self, validated_data):
        selected_fields = validated_data.pop("selected_fields", [])
        user_profile = super().create(validated_data)

        # Create UserField relations
        for field_id in selected_fields:
            field = Field.objects.get(id=field_id)
            UserField.objects.create(user=user_profile.user, field=field)

        return user_profile

    def update(self, instance, validated_data):
        """
        Update UserProfile and related User fields smartly.
        """
        user = instance.user  # Related User model

        # Handle selected fields first
        selected_fields = validated_data.pop("selected_fields", None)

        email = validated_data.get("email", None)

        if user.email != email and email:
            already_exists = User.objects.filter(email=email).exclude(id=user.id).first()
            if already_exists:
                    raise serializers.ValidationError(
                        f"User with the email already exists, Please try any other email."
                    )


        # Update the rest of the UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update selected fields (many-to-many via UserField)
        if selected_fields is not None:
            UserField.objects.filter(user=user).delete()
            for field_id in selected_fields:
                try:
                    field = Field.objects.filter(id=field_id).first()
                    if field:
                        UserField.objects.create(user=user, field=field)
                except Field.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Field ID {field_id} does not exist."
                    )
        return instance


    def get_user_fields(self, obj):
        """
        Retrieve related UserFields with field name.
        """
        user_fields = obj.user.user_fields.all()
        return [{"id": uf.field.id, "name": uf.field.name} for uf in user_fields]


class UserRegisterSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        password = validated_data.pop("password")

        # Create User instance
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Hash password
        user.save()
        # Create UserProfile instance
        UserProfile.objects.create(user=user, **profile_data)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Check if the user is marked as deleted
        if self.user.is_deleted:
            raise serializers.ValidationError("This account has been deactivated.")
        return data
