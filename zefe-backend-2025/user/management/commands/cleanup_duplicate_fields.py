from django.core.management.base import BaseCommand
from django.db.models import Count
from user.models import Field, UserField

class Command(BaseCommand):
    help = 'Clean up duplicate Field records'

    def handle(self, *args, **options):
        # Find fields with duplicate names
        duplicates = Field.objects.values('name').annotate(
            count=Count('id')).filter(count__gt=1)
        
        self.stdout.write(f"Found {duplicates.count()} fields with duplicates")
        
        for duplicate in duplicates:
            name = duplicate['name']
            fields = Field.objects.filter(name=name).order_by('id')
            
            if not fields:
                continue
                
            # Keep the first one, use it as the primary field
            primary_field = fields.first()
            self.stdout.write(f"Processing duplicates for '{name}' - keeping ID {primary_field.id}")
            
            # For all other duplicates
            for field in fields[1:]:
                self.stdout.write(f"  - Moving references from field ID {field.id} to {primary_field.id}")
                
                # Move all UserField references to the primary field
                UserField.objects.filter(field=field).update(field=primary_field)
                
                # Delete the duplicate field
                self.stdout.write(f"  - Deleting duplicate field ID {field.id}")
                field.delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate fields'))