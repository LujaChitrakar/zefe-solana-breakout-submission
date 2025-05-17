from django.core.management.base import BaseCommand
from django.db.models import Q
from user.models import User

class Command(BaseCommand):
    help = 'Update source field for existing users'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting update of user sources...")
        
        # First, check how many users need updating
        total_users = User.objects.count()
        self.stdout.write(f"Found {total_users} total users")
        
        # Update users with telegram_id to TELEGRAM source
        # Avoid comparing with strings since telegram_id is an integer field
        telegram_users = User.objects.filter(
            telegram_id__isnull=False
        ).exclude(telegram_id=0)  # Use integer 0 instead of string '0'
        
        count = telegram_users.update(source='TELEGRAM')
        self.stdout.write(self.style.SUCCESS(f'Updated {count} users to TELEGRAM source'))
        
        # Update remaining users to WEB source
        web_users = User.objects.exclude(source='TELEGRAM')
        web_count = web_users.update(source='WEB')
        self.stdout.write(self.style.SUCCESS(f'Updated {web_count} users to WEB source'))
        
        # Print final counts
        telegram_total = User.objects.filter(source='TELEGRAM').count()
        web_total = User.objects.filter(source='WEB').count()
        admin_total = User.objects.filter(source='ADMIN').count()
        
        self.stdout.write(self.style.SUCCESS(
            f'Final counts - TELEGRAM: {telegram_total}, WEB: {web_total}, ADMIN: {admin_total}'
        ))