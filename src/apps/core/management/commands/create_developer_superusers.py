from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create superusers for the developers of the portal'

    def handle(self, *args, **options):
        # Create superuser for Saidamen Mambayao
        if not User.objects.filter(username='saidamen.m').exists():
            user1 = User.objects.create_superuser(
                username='saidamen.m',
                email='saidamen.mambayao@fahaniecares.gov.ph',
                password='Saidamen2025!',
                first_name='Saidamen',
                last_name='Mambayao'
            )
            # Set user type to superuser
            user1.user_type = 'superuser'
            user1.is_approved = True
            user1.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: saidamen.m'))
        else:
            self.stdout.write(self.style.WARNING('Superuser saidamen.m already exists'))

        # Create superuser for Farissnoor Edza
        if not User.objects.filter(username='farissnoor.e').exists():
            user2 = User.objects.create_superuser(
                username='farissnoor.e',
                email='farissnoor.edza@fahaniecares.gov.ph',
                password='Farissnoor2025!',
                first_name='Farissnoor',
                last_name='Edza'
            )
            # Set user type to superuser
            user2.user_type = 'superuser'
            user2.is_approved = True
            user2.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: farissnoor.e'))
        else:
            self.stdout.write(self.style.WARNING('Superuser farissnoor.e already exists'))

        self.stdout.write(
            self.style.SUCCESS(
                'Developer superusers created successfully. MFA is bypassed for these accounts.'
            )
        )