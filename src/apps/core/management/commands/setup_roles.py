"""
Setup role-based groups and permissions for unified interface.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


class Command(BaseCommand):
    help = 'Set up role-based groups and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up role groups...')

        # Each permission is (app_label, model_name, codename, name)
        roles = {
            'member': {
                'description': 'Registered Members',
                'permissions': [
                    ('constituents', 'constituent', 'view_constituent', 'Can view constituent'),
                    ('constituents', 'constituent', 'add_constituent', 'Can add constituent'),
                    ('constituents', 'constituent', 'change_constituent', 'Can change constituent'),
                    ('referrals', 'referral', 'add_referral', 'Can add referral'),
                    ('referrals', 'referral', 'view_referral', 'Can view referral'),
                    ('chapters', 'chapter', 'view_chapter', 'Can view chapter'),
                ],
            },
            'referral_staff': {
                'description': 'Referral Processing Staff',
                'inherits': 'member',
                'permissions': [
                    ('referrals', 'referral', 'change_referral', 'Can change referral'),
                    ('referrals', 'referral', 'process_referral', 'Can process referrals'),
                    ('referrals', 'referral', 'view_all_referrals', 'Can view all referrals'),
                    ('analytics', 'report', 'view_referral_analytics', 'Can view referral analytics'),
                ],
            },
            'program_admin': {
                'description': 'Program Administration Staff',
                'inherits': 'referral_staff',
                'permissions': [
                    ('services', 'ministryprogram', 'add_ministryprogram', 'Can add ministry program'),
                    ('services', 'ministryprogram', 'change_ministryprogram', 'Can change ministry program'),
                    ('services', 'ministryprogram', 'delete_ministryprogram', 'Can delete ministry program'),
                    ('services', 'ministryprogram', 'manage_program_budget', 'Can manage program budget'),
                    ('analytics', 'report', 'view_program_analytics', 'Can view program analytics'),
                ],
            },
        }

        with transaction.atomic():
            created_groups = {}

            for role_name, role_config in roles.items():
                group, created = Group.objects.get_or_create(name=role_name)
                created_groups[role_name] = group

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
                else:
                    self.stdout.write(f'Group already exists: {role_name}')

                # Correctly unpack 4 values
                for app_label, model_name, codename, name in role_config.get('permissions', []):
                    try:
                        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                        permission, perm_created = Permission.objects.get_or_create(
                            codename=codename,
                            content_type=content_type,
                            defaults={'name': name}
                        )
                        group.permissions.add(permission)

                        if perm_created:
                            self.stdout.write(
                                self.style.SUCCESS(f'  Created permission: {app_label}.{codename}')
                            )

                    except ContentType.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ App/model not found: {app_label}.{model_name} (may need migrations)')
                        )

                # Handle inheritance
                if 'inherits' in role_config:
                    parent_name = role_config['inherits']
                    parent_group = created_groups.get(parent_name)
                    if parent_group:
                        parent_permissions = parent_group.permissions.all()
                        group.permissions.add(*parent_permissions)
                        self.stdout.write(
                            f'  Inherited {parent_permissions.count()} permissions from {parent_name}'
                        )

        self.stdout.write(self.style.SUCCESS('✅ Role groups setup completed!'))
