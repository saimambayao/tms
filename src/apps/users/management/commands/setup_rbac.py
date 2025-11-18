"""
Management command to set up RBAC permissions, roles, and initial data.
Run with: python manage.py setup_rbac
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from apps.users.models import User, DynamicPermission, RolePermission
from apps.users.permissions import setup_role_groups
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up RBAC permissions, roles, and initial data for #FahanieCares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all permissions and groups before setup',
        )
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Create test users for each role',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up RBAC system...'))
        
        if options['reset']:
            self.reset_permissions()
        
        # Set up Django groups
        self.stdout.write('Creating role groups...')
        setup_role_groups()
        
        # Create dynamic permissions
        self.stdout.write('Creating dynamic permissions...')
        self.create_dynamic_permissions()
        
        # Assign permissions to roles
        self.stdout.write('Assigning permissions to roles...')
        self.assign_role_permissions()
        
        # Create test users if requested
        if options['create_test_users']:
            self.stdout.write('Creating test users...')
            self.create_test_users()
        
        self.stdout.write(self.style.SUCCESS('RBAC setup completed successfully!'))
    
    def reset_permissions(self):
        """Reset all permissions and groups."""
        self.stdout.write('Resetting permissions and groups...')
        
        # Delete all dynamic permissions
        DynamicPermission.objects.all().delete()
        RolePermission.objects.all().delete()
        
        # Reset groups
        Group.objects.filter(name__in=[
            'Superuser',
            'Member of Parliament',
            'Chief of Staff',
            'Parliamentary Office Staff',
            'System Administrator',
            'Coordinator',
            'Information Officer',
            'Chapter Member',
            'Registered User',
        ]).delete()
        
        self.stdout.write(self.style.SUCCESS('Reset completed'))
    
    def create_dynamic_permissions(self):
        """Create all dynamic permissions for the system."""
        permissions_data = [
            # Executive permissions
            {
                'name': 'View Executive Dashboard',
                'codename': 'view_executive_dashboard',
                'description': 'Access to executive-level dashboard with strategic metrics',
                'module': 'executive'
            },
            {
                'name': 'View Executive Reports',
                'codename': 'view_executive_reports',
                'description': 'Access to high-level strategic reports',
                'module': 'executive'
            },
            {
                'name': 'Strategic Oversight',
                'codename': 'strategic_oversight',
                'description': 'View-only access to all system data for strategic decision making',
                'module': 'executive'
            },
            
            # Staff management permissions
            {
                'name': 'Manage Staff',
                'codename': 'manage_staff',
                'description': 'Manage parliamentary staff and their assignments',
                'module': 'staff'
            },
            {
                'name': 'Assign Roles',
                'codename': 'assign_roles',
                'description': 'Assign and modify user roles',
                'module': 'staff'
            },
            {
                'name': 'Approve Critical Actions',
                'codename': 'approve_critical_actions',
                'description': 'Approve high-impact system actions',
                'module': 'staff'
            },
            
            # System administration
            {
                'name': 'Manage System Configuration',
                'codename': 'manage_system_config',
                'description': 'Modify system settings and configuration',
                'module': 'system'
            },
            {
                'name': 'Manage Integrations',
                'codename': 'manage_integrations',
                'description': 'Configure and manage external system integrations',
                'module': 'system'
            },
            {
                'name': 'View Audit Logs',
                'codename': 'view_audit_logs',
                'description': 'Access system audit logs and security events',
                'module': 'system'
            },
            {
                'name': 'Manage Security Settings',
                'codename': 'manage_security',
                'description': 'Configure security settings and policies',
                'module': 'system'
            },
            {
                'name': 'Manage Backups',
                'codename': 'manage_backups',
                'description': 'Manage system backups and recovery',
                'module': 'system'
            },
            
            # Service management
            {
                'name': 'Manage FahanieCares Programs',
                'codename': 'manage_fahaniecares_programs',
                'description': 'Create and manage #FahanieCares service programs',
                'module': 'services'
            },
            {
                'name': 'Manage TDIF Projects',
                'codename': 'manage_tdif_projects',
                'description': 'Manage Tulong Dunong Infrastructure Fund projects',
                'module': 'services'
            },
            {
                'name': 'Manage Ministry Programs',
                'codename': 'manage_ministry_programs',
                'description': 'Coordinate with ministry programs and services',
                'module': 'services'
            },
            {
                'name': 'Approve Service Applications',
                'codename': 'approve_service_applications',
                'description': 'Review and approve constituent service applications',
                'module': 'services'
            },
            
            # Communications
            {
                'name': 'Manage Announcements',
                'codename': 'manage_announcements',
                'description': 'Create, edit, and publish public announcements',
                'module': 'communications'
            },
            {
                'name': 'Manage Content',
                'codename': 'manage_content',
                'description': 'Manage website content and media resources',
                'module': 'communications'
            },
            {
                'name': 'Send Notifications',
                'codename': 'send_notifications',
                'description': 'Send notifications to constituents',
                'module': 'communications'
            },
            {
                'name': 'Manage Newsletter',
                'codename': 'manage_newsletter',
                'description': 'Create and send newsletters',
                'module': 'communications'
            },
            
            # Analytics and reporting
            {
                'name': 'View Operational Reports',
                'codename': 'view_operational_reports',
                'description': 'Access operational performance reports',
                'module': 'analytics'
            },
            {
                'name': 'Export Data',
                'codename': 'export_data',
                'description': 'Export system data for analysis',
                'module': 'analytics'
            },
            {
                'name': 'View Service Analytics',
                'codename': 'view_service_analytics',
                'description': 'Access service delivery analytics',
                'module': 'analytics'
            },
            
            # Chapter management
            {
                'name': 'View Chapter Activities',
                'codename': 'view_chapter_activities',
                'description': 'View activities within chapters',
                'module': 'chapters'
            },
            {
                'name': 'Participate in Chapter Activities',
                'codename': 'participate_chapter_activities',
                'description': 'Participate in chapter events and activities',
                'module': 'chapters'
            },
            {
                'name': 'Manage Chapter Operations',
                'codename': 'manage_chapter_operations',
                'description': 'Manage chapter membership and operations',
                'module': 'chapters'
            },
            
            # Workflow permissions
            {
                'name': 'Manage Workflows',
                'codename': 'manage_workflows',
                'description': 'Design and manage approval workflows',
                'module': 'workflows'
            },
            {
                'name': 'Override Workflow',
                'codename': 'override_workflow',
                'description': 'Override standard workflow processes',
                'module': 'workflows'
            },
            
            # Task and Calendar Management (Staff-specific)
            {
                'name': 'Manage Tasks',
                'codename': 'manage_tasks',
                'description': 'Create, assign, and track office tasks',
                'module': 'tasks'
            },
            {
                'name': 'Manage Calendar',
                'codename': 'manage_calendar',
                'description': 'Schedule and manage office calendar events',
                'module': 'calendar'
            },
            {
                'name': 'Coordinate Schedule',
                'codename': 'coordinate_schedule',
                'description': 'Coordinate schedules across office staff',
                'module': 'calendar'
            },
            {
                'name': 'Manage Office Workflow',
                'codename': 'manage_office_workflow',
                'description': 'Organize and streamline office workflows',
                'module': 'workflow'
            },
            {
                'name': 'Manage Meetings',
                'codename': 'manage_meetings',
                'description': 'Schedule and coordinate office meetings',
                'module': 'meetings'
            },
            {
                'name': 'Coordinate Events',
                'codename': 'coordinate_events',
                'description': 'Plan and coordinate office events',
                'module': 'events'
            },
            {
                'name': 'Manage Appointments',
                'codename': 'manage_appointments',
                'description': 'Schedule and manage MP appointments',
                'module': 'appointments'
            },
            {
                'name': 'View Calendar',
                'codename': 'view_calendar',
                'description': 'View office calendar and schedules',
                'module': 'calendar'
            },
            {
                'name': 'View Tasks',
                'codename': 'view_tasks',
                'description': 'View assigned tasks and progress',
                'module': 'tasks'
            },
        ]
        
        created_count = 0
        for perm_data in permissions_data:
            perm, created = DynamicPermission.objects.update_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description'],
                    'module': perm_data['module'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created permission: {perm.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new permissions'))
    
    def assign_role_permissions(self):
        """Assign dynamic permissions to roles."""
        role_permissions_mapping = {
            'superuser': [
                # All permissions - ultimate control
                'view_executive_dashboard',
                'view_executive_reports',
                'strategic_oversight',
                'manage_staff',
                'assign_roles',
                'approve_critical_actions',
                'manage_workflows',
                'override_workflow',
                'view_audit_logs',
                'manage_system_config',
                'manage_integrations',
                'manage_security',
                'manage_backups',
                'view_operational_reports',
                'export_data',
                'view_service_analytics',
                'manage_fahaniecares_programs',
                'manage_tdif_projects',
                'manage_ministry_programs',
                'approve_service_applications',
                'manage_announcements',
                'manage_content',
                'send_notifications',
                'manage_newsletter',
                'view_chapter_activities',
                'participate_chapter_activities',
                'manage_chapter_operations',
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
            ],
            'mp': [
                'view_executive_dashboard',
                'view_executive_reports',
                'strategic_oversight',
                'view_audit_logs',
                'view_operational_reports',
                'view_service_analytics',
                'view_calendar',
                'view_tasks',
            ],
            'chief_of_staff': [
                'view_executive_dashboard',
                'view_executive_reports',
                'manage_staff',
                'assign_roles',
                'approve_critical_actions',
                'manage_workflows',
                'override_workflow',
                'view_audit_logs',
                'view_operational_reports',
                'export_data',
                'view_service_analytics',
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
            ],
            'staff': [
                # Base staff permissions only - minimal access for parliamentary staff
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
            ],
            'admin': [
                # All base staff permissions
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
                # PLUS System administration capabilities
                'manage_system_config',
                'manage_integrations',
                'view_audit_logs',
                'manage_security',
                'manage_backups',
                'view_operational_reports',
                'export_data',
                'manage_fahaniecares_programs',
                'manage_tdif_projects',
                'manage_ministry_programs',
                'approve_service_applications',
            ],
            'coordinator': [
                # All base staff permissions
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
                # PLUS Service coordination capabilities
                'manage_fahaniecares_programs',
                'manage_tdif_projects',
                'manage_ministry_programs',
                'approve_service_applications',
                'view_operational_reports',
                'export_data',
                'view_service_analytics',
                'manage_chapter_operations',
            ],
            'info_officer': [
                # All base staff permissions
                'manage_tasks',
                'manage_calendar',
                'coordinate_schedule',
                'manage_office_workflow',
                'manage_meetings',
                'coordinate_events',
                'manage_appointments',
                'view_calendar',
                'view_tasks',
                # PLUS Communication management capabilities
                'manage_announcements',
                'manage_content',
                'send_notifications',
                'manage_newsletter',
                'view_service_analytics',
            ],
            'chapter_member': [
                'view_chapter_activities',
                'participate_chapter_activities',
            ],
            'registered_user': [
                # Basic users have no dynamic permissions by default
            ],
        }
        
        created_count = 0
        for role, permission_codenames in role_permissions_mapping.items():
            for codename in permission_codenames:
                try:
                    permission = DynamicPermission.objects.get(codename=codename)
                    role_perm, created = RolePermission.objects.get_or_create(
                        role=role,
                        permission=permission,
                        defaults={'is_active': True}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f"  Assigned {permission.name} to {role}")
                except DynamicPermission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"  Permission {codename} not found")
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} role-permission assignments'))
    
    def create_test_users(self):
        """Create test users for each role."""
        test_users = [
            {
                'username': 'superuser_test',
                'email': 'superuser@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Superuser',
                'user_type': 'superuser',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'mp_test',
                'email': 'mp@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'MP',
                'user_type': 'mp',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'chief_test',
                'email': 'chief@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Chief',
                'user_type': 'chief_of_staff',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'staff_test',
                'email': 'staff@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Staff',
                'user_type': 'staff',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'admin_test',
                'email': 'admin@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Admin',
                'user_type': 'admin',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'coordinator_test',
                'email': 'coordinator@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Coordinator',
                'user_type': 'coordinator',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'info_officer_test',
                'email': 'info@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'InfoOfficer',
                'user_type': 'info_officer',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'member_test',
                'email': 'member@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'Member',
                'user_type': 'chapter_member',
                'password': 'FahanieCares2024!'
            },
            {
                'username': 'user_test',
                'email': 'user@fahaniecares.ph',
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'registered_user',
                'password': 'FahanieCares2024!'
            },
        ]
        
        for user_data in test_users:
            password = user_data.pop('password')
            user, created = User.objects.update_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.is_approved = True
                user.save()
                
                # Assign to appropriate group
                from apps.users.permissions import assign_user_to_role_group
                assign_user_to_role_group(user)
                
                self.stdout.write(
                    self.style.SUCCESS(f"  Created test user: {user.username} ({user.user_type})")
                )