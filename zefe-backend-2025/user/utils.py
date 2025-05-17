from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

from django.db.models import Q

from rest_framework.views import exception_handler
from rest_framework.permissions import SAFE_METHODS
from rest_framework.exceptions import ErrorDetail

from rest_framework.utils import encoders, json
from user.models import User

def create_or_update_telegram_user(data):
    telegram_id = data["id"]
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    username = data.get("username", "")
    active_usernames = data.get("active_usernames", [])

    user, created = User.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={"first_name": first_name, "last_name": last_name, "username": username, "active_usernames": active_usernames},
    )
    return user









def custom_exception_handler_for_mutiple(errors):
    msg = []
    for error in errors:
        for key, value in error.items():
            if key == "non_field_errors":
                msg.append(value[0])
            elif isinstance(value, ErrorDetail):
                msg.append(value.title())
            else:
                msg.append(f"{key.title()} - {value[0]}")
    return msg


