#!/usr/bin/env python
import os
import sys
import django

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.constituents.member_models import FahanieCaresMember

def check_status():
    print('=== Registrant Status Check ===')
    print(f'Total members: {FahanieCaresMember.objects.count()}')
    print(f'Pending: {FahanieCaresMember.objects.filter(status="pending").count()}')
    print(f'Approved: {FahanieCaresMember.objects.filter(status="approved").count()}')
    print(f'Incomplete: {FahanieCaresMember.objects.filter(status="incomplete").count()}')
    print(f'Non-compliant: {FahanieCaresMember.objects.filter(status="non_compliant").count()}')
    print(f'Archived: {FahanieCaresMember.objects.filter(status="archived").count()}')
    print(f'Members with PREG IDs: {FahanieCaresMember.objects.filter(member_id__startswith="PREG").count()}')
    print(f'Members with empty status: {FahanieCaresMember.objects.filter(status="").count()}')
    print(f'Members with null status: {FahanieCaresMember.objects.filter(status__isnull=True).count()}')

    # Check recent members
    print('\n=== Recent Members (last 5) ===')
    recent = FahanieCaresMember.objects.order_by('-created_at')[:5]
    for member in recent:
        print(f'ID: {member.id}, Status: "{member.status}", Member ID: {member.member_id}, Created: {member.created_at}')

if __name__ == '__main__':
    check_status()
