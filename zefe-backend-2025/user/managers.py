from django.contrib.auth.models import BaseUserManager



class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle both admin (email-based) and Telegram users.(telegram_id)
    
    """

    def create_user(self, email=None, telegram_id=None,username=None, photo_url=None, password=None):
        """Create a regular user with either email or telegram_id."""
        if not email and not telegram_id:
            raise ValueError("User must have either an email or Telegram ID")

        user = self.model(
            email=self.normalize_email(email) if email else None,
            telegram_id=telegram_id,
            username=username,
            photo_url=photo_url
        )

        if password:  # Only for email-based users
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create a superuser (admin)."""
        if not email:
            raise ValueError("Superusers must have an email address")

        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user