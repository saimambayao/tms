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

def update_member_status():
    print('=== Updating Member Status and IDs ===')

    # Update members with empty or null status to 'pending'
    members_with_empty_status = FahanieCaresMember.objects.filter(status__in=['', None])
    count_empty = members_with_empty_status.count()
    print(f'Found {count_empty} members with empty/null status')

    for member in members_with_empty_status:
        member.status = 'pending'
        if not member.member_id:
            member.member_id = member._generate_member_id(is_temporary=True)
        member.save(update_fields=['status', 'member_id'])
        print(f'Updated member {member.id}: status="pending", member_id="{member.member_id}"')

    # Update incomplete members without IDs
    incomplete_members = FahanieCaresMember.objects.filter(status='incomplete', member_id__isnull=True)
    count_incomplete = incomplete_members.count()
    print(f'Found {count_incomplete} incomplete members without IDs')

    for member in incomplete_members:
        member.member_id = member._generate_status_id('INC')
        member.save(update_fields=['member_id'])
        print(f'Updated incomplete member {member.id}: member_id="{member.member_id}"')

    # Update non-compliant members without IDs
    non_compliant_members = FahanieCaresMember.objects.filter(status='non_compliant', member_id__isnull=True)
    count_non_compliant = non_compliant_members.count()
    print(f'Found {count_non_compliant} non-compliant members without IDs')

    for member in non_compliant_members:
        member.member_id = member._generate_status_id('NOC')
        member.save(update_fields=['member_id'])
        print(f'Updated non-compliant member {member.id}: member_id="{member.member_id}"')

    print('\n=== Final Status Check ===')
    print(f'Total members: {FahanieCaresMember.objects.count()}')
    print(f'Pending: {FahanieCaresMember.objects.filter(status="pending").count()}')
    print(f'Approved: {FahanieCaresMember.objects.filter(status="approved").count()}')
    print(f'Incomplete: {FahanieCaresMember.objects.filter(status="incomplete").count()}')
    print(f'Non-compliant: {FahanieCaresMember.objects.filter(status="non_compliant").count()}')
    print(f'Members with PREG IDs: {FahanieCaresMember.objects.filter(member_id__startswith="PREG").count()}')
    print(f'Members with INC IDs: {FahanieCaresMember.objects.filter(member_id__startswith="INC").count()}')
    print(f'Members with NOC IDs: {FahanieCaresMember.objects.filter(member_id__startswith="NOC").count()}')
    print(f'Members with no member_id: {FahanieCaresMember.objects.filter(member_id__isnull=True).count()}')

if __name__ == '__main__':
    update_member_status()
