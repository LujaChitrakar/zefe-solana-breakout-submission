# authentication.py

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions

class TelegramJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return None

        try:
            # Extract token from Authorization header
            auth_type, token = auth_header.split(' ')
            if auth_type != 'Bearer':
                raise exceptions.AuthenticationFailed('Authorization header must start with "Bearer"')

            # Decode the JWT token (make sure to adjust the secret key and algorithm)
            payload = jwt.decode(token, settings.TELEGRAM_BOT_TOKEN, algorithms=["HS256"])

            # Fetch user info from the token's payload, assuming 'telegram_id' exists in the payload
            telegram_id = payload.get("telegram_id")
            if telegram_id is None:
                raise exceptions.AuthenticationFailed('Telegram ID not found in token')

            # You can query your user model here to authenticate or create the user
            user = User.objects.filter(username=telegram_id).first()
            if not user:
                raise exceptions.AuthenticationFailed('User not found')

            # Return user and token
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
