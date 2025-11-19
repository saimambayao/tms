#!/usr/bin/env python3
"""
Grant highest admin access to Saidamen Mambayao and Farissnoor Edza.
These are the system developers and need full superuser privileges.
"""

import os
import sys
import django

# Setup Django
# Ensure the project root is in Python path for Django to find apps and settings
# This assumes the script is run from the project root or 'src' directory
# If run from 'src', BASE_DIR will be 'src', so adjust settings module if needed.
# For this script, it's assumed to be run from the project root or 'src'
# and the .env file is in the project root.
# Determine settings module based on environment variable
if os.environ.get('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.staff.models import Staff

User = get_user_model()

# Developer accounts to promote
DEVELOPERS = [
    {
        'username': 'saidamen.m',
        'full_name': 'Saidamen Mambayao',
        'email': 'developer1@bmparliament.gov.ph',
        'role': 'SLSO I / OIC Legislative Affairs / System Developer'
    },
    {
        'username': 'farissnoor.e',
        'full_name': 'Farissnoor Edza',
        'email': 'developer2@bmparliament.gov.ph',
        'role': 'IT Staff / Lead Developer'
    },
    {
        'username': 'kristel.f',
        'full_name': 'Kristel Fernando',
        'email': 'kristel.fernando@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
    {
        'username': 'saadalyn.s',
        'full_name': 'Saadalyn Sampulna',
        'email': 'saadalyn@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
    {
        'username': 'hasnah.s',
        'full_name': 'Hasnah Sindatok',
        'email': 'hasnah@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
    {
        'username': 'maleah.k',
        'full_name': 'Maleah Kate',
        'email': 'maleah@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
    {
        'username': 'schejah.s',
        'full_name': 'Schejah Sindatok',
        'email': 'schejah@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
    {
        'username': 'sittie.f',
        'full_name': 'Amiroddin Gayak',
        'email': 'sittie.gayak@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    },
        {
        'username': 'saud.g',
        'full_name': 'Guiamelon Saud',
        'email': 'guiamelonsaud@example.com', # Assuming a generic email for now
        'role': 'System Superuser'
    }
]

ADMINISTRATORS = [
    {
        'username': 'admin.test',
        'full_name': 'Test System Administrator',
        'email': 'admin.test@example.com',
        'role': 'System Administrator'
    }
]

DATA_VIEWERS = [
    # Anne Lidasan moved to ADMINISTRATORS
]

def create_developer_group():
    """Create a System Developers group (for organizational purposes, superusers don't need group permissions)"""
    print("🔧 Creating System Developers group...")
    group, created = Group.objects.get_or_create(
        name='System Developers',
        defaults={'name': 'System Developers'}
    )
    if created:
        print("✅ Created 'System Developers' group")
    else:
        print("ℹ️  'System Developers' group already exists")
    # Superusers get all permissions individually, so no need to add all to this group
    return group

def create_system_admin_group():
    """Create a System Administrator group with specific permissions"""
    print("🔧 Creating System Administrator group...")
    group, created = Group.objects.get_or_create(
        name='System Administrator',
        defaults={'name': 'System Administrator'}
    )
    if created:
        print("✅ Created 'System Administrator' group")
    else:
        print("ℹ️  'System Administrator' group already exists")

    # Define permissions for System Administrator based on docs/rbac_implementation_plan.md
    # This is an educated guess based on common Django app/model names.
    # Adjust as necessary if actual model names differ.
    admin_permissions_codenames = [
        # User Management
        'add_user', 'change_user', 'delete_user', 'view_user',
        'add_group', 'change_group', 'delete_group', 'view_group',
        'add_permission', 'change_permission', 'delete_permission', 'view_permission',
        # Constituent Management
        'add_constituent', 'change_constituent', 'delete_constituent', 'view_constituent',
        'add_bmparliamentmember', 'change_bmparliamentmember', 'delete_bmparliamentmember', 'view_bmparliamentmember',
        # Service Management
        'add_service', 'change_service', 'delete_service', 'view_service',
        # Referral Management
        'add_referral', 'change_referral', 'delete_referral', 'view_referral',
        # Communications
        'add_announcement', 'change_announcement', 'delete_announcement', 'view_announcement',
        'add_contactformsubmission', 'change_contactformsubmission', 'delete_contactformsubmission', 'view_contactformsubmission',
        'add_donationsubmission', 'change_donationsubmission', 'delete_donationsubmission', 'view_donationsubmission',
        'add_emailsubscription', 'change_emailsubscription', 'delete_emailsubscription', 'view_emailsubscription',
        'add_partnershipsubmission', 'change_partnershipsubmission', 'delete_partnershipsubmission', 'view_partnershipsubmission',
        # Dashboards (assuming view access to operational dashboard)
        'view_dashboard', # Assuming a dashboard model or specific view permission
        # System Administration (assuming these are custom permissions or related to core models)
        # These might need to be created as custom permissions if not tied to specific models
        'view_auditlog', # Assuming an AuditLog model
        # #BM Parliament Programs (assuming models like Program, Application)
        'add_program', 'change_program', 'delete_program', 'view_program',
        'add_application', 'change_application', 'delete_application', 'view_application',
        # TDIF Projects (assuming models like Project)
        'add_project', 'change_project', 'delete_project', 'view_project',
        # Ministry Programs (assuming models like MinistryProgram)
        'add_ministryprogram', 'change_ministryprogram', 'delete_ministryprogram', 'view_ministryprogram',
        # Task & Calendar Management (assuming models like Task, CalendarEvent)
        'add_task', 'change_task', 'delete_task', 'view_task',
        'add_calendarevent', 'change_calendarevent', 'delete_calendarevent', 'view_calendarevent',
        # Chapters
        'add_chapter', 'change_chapter', 'delete_chapter', 'view_chapter',
        # Documents
        'add_document', 'change_document', 'delete_document', 'view_document',
        # Notifications
        'add_notification', 'change_notification', 'delete_notification', 'view_notification',
        # Parliamentary
        'add_parliamentaryitem', 'change_parliamentaryitem', 'delete_parliamentaryitem', 'view_parliamentaryitem',
        # Search
        'add_searchquery', 'change_searchquery', 'delete_searchquery', 'view_searchquery',
        # Staff
        'add_staff', 'change_staff', 'delete_staff', 'view_staff',
    ]

    permissions_to_add = []
    for codename in admin_permissions_codenames:
        try:
            app_label, perm_codename = codename.split('.', 1)
            content_type = ContentType.objects.get(app_label=app_label, model__in=Permission.objects.filter(codename=perm_codename).values_list('content_type__model', flat=True))
            perm = Permission.objects.get(content_type=content_type, codename=perm_codename)
            permissions_to_add.append(perm)
        except ContentType.DoesNotExist:
            print(f"  ⚠️  Warning: ContentType for app_label '{app_label}' not found for permission '{codename}'. Skipping.")
        except Permission.DoesNotExist:
            print(f"  ⚠️  Warning: Permission '{codename}' not found. Skipping.")
        except ValueError:
            print(f"  ⚠️  Warning: Invalid permission codename format '{codename}'. Skipping.")

    group.permissions.set(permissions_to_add)
    print(f"✅ Added {len(permissions_to_add)} permissions to System Administrator group")
    
    return group

def create_data_viewer_group():
    """Create a Data Viewers group with only view permissions"""
    print("🔧 Creating Data Viewers group...")
    group, created = Group.objects.get_or_create(
        name='Data Viewers',
        defaults={'name': 'Data Viewers'}
    )
    if created:
        print("✅ Created 'Data Viewers' group")
    else:
        print("ℹ️  'Data Viewers' group already exists")

    # Assign all 'view' permissions to this group
    view_permissions = Permission.objects.filter(codename__startswith='view_')
    group.permissions.set(view_permissions)
    print(f"✅ Added {view_permissions.count()} 'view' permissions to Data Viewers group")
    return group

def grant_superuser_access():
    """Grant superuser access to developer accounts"""
    print("\n👑 Granting superuser access to developers...")
    print("=" * 60)
    
    # Create developer group first (for organizational purposes)
    dev_group = create_developer_group()
    
    promoted_count = 0
    errors = []
    
    for dev in DEVELOPERS:
        try:
            username = dev['username']
            full_name = dev['full_name']
            email = dev['email']
            role = dev['role']
            
            print(f"\n🔍 Processing: {full_name} ({username})")
            
            # Get or create user
            try:
                user = User.objects.get(username=username)
                print(f"  ✅ Found existing user")
            except User.DoesNotExist:
                print(f"  ⚠️  User not found, creating...")
                # Parse name parts
                name_parts = full_name.split()
                first_name = name_parts[0] if name_parts else full_name
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                # For anne.lidasan, set a specific password as requested
                if username == 'anne.lidasan':
                    password_to_set = "Anne2025!"
                else:
                    password_to_set = f"{first_name}2024!"

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password_to_set,
                    first_name=first_name,
                    last_name=last_name
                )
                print(f"  ✅ Created user account")
            
            # Grant superuser privileges
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.user_type = 'superuser' # Explicitly set user_type to superuser
            user.save()
            
            print(f"  👑 Granted SUPERUSER status")
            print(f"  ✅ Granted staff access")
            print(f"  ✅ Account activated")
            
            # Add to developer group
            user.groups.add(dev_group)
            print(f"  👥 Added to System Developers group")
            
            # Grant all individual permissions (belt and suspenders approach for superusers)
            all_permissions = Permission.objects.all()
            user.user_permissions.set(all_permissions)
            print(f"  🔐 Granted {all_permissions.count()} individual permissions")
            
            # Update staff profile if exists
            try:
                staff = Staff.objects.get(full_name=full_name)
                original_position = staff.position
                staff.position = role
                staff.user = user
                staff.save()
                print(f"  📝 Updated staff profile position: '{original_position}' → '{role}'")
            except Staff.DoesNotExist:
                print(f"  ⚠️  No staff profile found for {full_name}")
            
            promoted_count += 1
            print(f"  🎉 {full_name} now has FULL ADMIN ACCESS")
            
        except Exception as e:
            error_msg = f"Error processing {dev.get('full_name', 'Unknown')}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ {error_msg}")
    
    return promoted_count, errors, dev_group

def grant_system_admin_access():
    """Grant System Administrator access to defined accounts"""
    print("\n⚙️ Granting System Administrator access...")
    print("=" * 60)

    admin_group = create_system_admin_group()

    promoted_count = 0
    errors = []

    for admin_user_data in ADMINISTRATORS:
        try:
            username = admin_user_data['username']
            full_name = admin_user_data['full_name']
            email = admin_user_data['email']
            role = admin_user_data['role']

            print(f"\n🔍 Processing: {full_name} ({username})")

            # Get or create user
            try:
                user = User.objects.get(username=username)
                print(f"  ✅ Found existing user")
            except User.DoesNotExist:
                print(f"  ⚠️  User not found, creating...")
                name_parts = full_name.split()
                first_name = name_parts[0] if name_parts else full_name
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=f"{first_name}2024!",
                    first_name=first_name,
                    last_name=last_name
                )
                print(f"  ✅ Created user account")

            # Grant staff privileges (not superuser)
            user.is_superuser = False
            user.is_staff = True
            user.is_active = True
            user.user_type = 'admin' # Set user_type to admin
            user.save()

            print(f"  ✅ Granted staff access")
            print(f"  ✅ Account activated")
            print(f"  🚫 Ensured NOT superuser")

            # Add to System Administrator group
            user.groups.add(admin_group)
            print(f"  👥 Added to System Administrator group")

            # Clear individual permissions to ensure group-based access
            user.user_permissions.clear()
            print(f"  🔐 Cleared individual permissions (access via group)")

            # Update staff profile if exists
            try:
                staff = Staff.objects.get(full_name=full_name)
                original_position = staff.position
                staff.position = role
                staff.user = user
                staff.save()
                print(f"  📝 Updated staff profile position: '{original_position}' → '{role}'")
            except Staff.DoesNotExist:
                print(f"  ⚠️  No staff profile found for {full_name}")

            promoted_count += 1
            print(f"  🎉 {full_name} now has SYSTEM ADMIN ACCESS")

        except Exception as e:
            error_msg = f"Error processing {admin_user_data.get('full_name', 'Unknown')}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    return promoted_count, errors, admin_group

def grant_data_viewer_access():
    """Grant Data Viewer access to defined accounts"""
    print("\n📊 Granting Data Viewer access...")
    print("=" * 60)

    data_viewer_group = create_data_viewer_group()

    promoted_count = 0
    errors = []

    for data_user_data in DATA_VIEWERS:
        try:
            username = data_user_data['username']
            full_name = data_user_data['full_name']
            email = data_user_data['email']
            role = data_user_data['role']

            print(f"\n🔍 Processing: {full_name} ({username})")

            # Get or create user
            try:
                user = User.objects.get(username=username)
                print(f"  ✅ Found existing user")
            except User.DoesNotExist:
                print(f"  ⚠️  User not found, creating...")
                name_parts = full_name.split()
                first_name = name_parts[0] if name_parts else full_name
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=f"{first_name}2024!",
                    first_name=first_name,
                    last_name=last_name
                )
                print(f"  ✅ Created user account")

            # Grant active status, but NOT staff or superuser
            user.is_superuser = False
            user.is_staff = False # Crucial: No admin panel access
            user.is_active = True
            user.save()

            print(f"  ✅ Account activated")
            print(f"  🚫 Ensured NOT superuser or staff (no admin panel access)")

            # Add to Data Viewers group
            user.groups.add(data_viewer_group)
            print(f"  👥 Added to Data Viewers group")

            # Clear individual permissions to ensure group-based access
            user.user_permissions.clear()
            print(f"  🔐 Cleared individual permissions (access via group)")

            # Update staff profile if exists
            try:
                staff = Staff.objects.get(full_name=full_name)
                original_position = staff.position
                staff.position = role
                staff.user = user
                staff.save()
                print(f"  📝 Updated staff profile position: '{original_position}' → '{role}'")
            except Staff.DoesNotExist:
                print(f"  ⚠️  No staff profile found for {full_name}")

            promoted_count += 1
            print(f"  🎉 {full_name} now has DATA VIEWER ACCESS")

        except Exception as e:
            error_msg = f"Error processing {data_user_data.get('full_name', 'Unknown')}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    return promoted_count, errors, data_viewer_group

def verify_admin_access():
    """Verify that developers and system admins have proper access"""
    print(f"\n🔍 Verifying admin access...")
    print("=" * 60)
    
    all_admin_users = DEVELOPERS + ADMINISTRATORS + DATA_VIEWERS
    
    for user_data in all_admin_users:
        username = user_data['username']
        full_name = user_data['full_name']
        
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 {full_name} ({username}):")
            print(f"  🔹 Superuser: {'✅ YES' if user.is_superuser else '❌ NO'}")
            print(f"  🔹 Staff: {'✅ YES' if user.is_staff else '❌ NO'}")
            print(f"  🔹 Active: {'✅ YES' if user.is_active else '❌ NO'}")
            print(f"  🔹 Groups: {', '.join([g.name for g in user.groups.all()]) or 'None'}")
            print(f"  🔹 Individual Permissions: {user.user_permissions.count()}")
            print(f"  🔹 All Permissions (via groups + individual): {user.get_all_permissions().__len__()}")
            
            # Check Django admin access
            can_access_admin = user.is_staff and user.is_active
            print(f"  🔹 Django Admin Access: {'✅ YES' if can_access_admin else '❌ NO'}")
            
        except User.DoesNotExist:
            print(f"  ❌ User {username} not found!")

def update_credentials_file():
    """Update credentials file to reflect developer and system admin status"""
    print(f"\n📝 Updating credentials file...")
    
    staff_members = Staff.objects.all().select_related('user').order_by('full_name')
    
    content = "#BM Parliament Staff Login Credentials\n"
    content += "=" * 60 + "\n"
    content += "Updated from Staff Profiles.csv (Developers promoted to superusers, System Admins added)\n\n"
    
    def generate_password(name):
        first_name = name.strip().split()[0]
        return f"{first_name}2024!"
    
    for staff in staff_members:
        name = staff.full_name
        position = staff.position or "Staff"
        
        # Map division back to display name
        division_display = {
            'legislative_affairs': 'Legislative Affairs',
            'administrative_affairs': 'Administrative Affairs',
            'communications': 'Communications',
            'it_unit': 'IT Unit',
            'mp_office': "MP Gayak's Office"
        }.get(staff.division, staff.division or "Administrative Affairs")
        
        if staff.user:
            username = staff.user.username
            password = generate_password(name)
            email = staff.email or staff.user.email
            
            admin_status = ""
            if username in [dev['username'] for dev in DEVELOPERS]:
                admin_status = " [SUPERUSER/DEVELOPER]"
            elif username in [admin_data['username'] for admin_data in ADMINISTRATORS]:
                admin_status = " [SYSTEM ADMINISTRATOR]"
            elif username in [data_data['username'] for data_data in DATA_VIEWERS]:
                admin_status = " [DATA VIEWER]"
                
        else:
            username = "No account"
            password = "No account"
            email = staff.email or "No email"
            admin_status = ""
        
        content += f"Name: {name}{admin_status}\n"
        content += f"Position: {position}\n"
        content += f"Division: {division_display}\n"
        content += f"Employment Status: {staff.get_employment_status_display() or 'Unknown'}\n"
        content += f"Office: {staff.get_office_display() or 'Unknown'}\n"
        content += f"Phone: {staff.phone_number or 'Not provided'}\n"
        content += f"Username: {username}\n"
        content += f"Password: {password}\n"
        content += f"Email: {email}\n"
        
        if username in [dev['username'] for dev in DEVELOPERS]:
            content += f"Access Level: SUPERUSER - Full Django Admin & System Access\n"
        elif username in [admin_data['username'] for admin_data in ADMINISTRATORS]:
            content += f"Access Level: SYSTEM ADMINISTRATOR - Full Django Admin (non-superuser) & System Access\n"
        elif username in [data_data['username'] for data_data in DATA_VIEWERS]:
            content += f"Access Level: DATA VIEWER - Full Data View Access (No Admin Panel)\n"
        
        content += "-" * 40 + "\n"
    
    content += "\nAccess URLs:\n"
    content += "Staff Portal: http://localhost:8000/staff/\n"
    content += "Django Admin: http://localhost:8000/admin/ (Superusers have full access, System Admins have managed access)\n"
    content += "Login Page: http://localhost:8000/accounts/login/\n\n"
    content += "Notes:\n"
    content += "- Saidamen Mambayao & Farissnoor Edza: SUPERUSERS/DEVELOPERS\n"
    content += "- Test System Administrator: SYSTEM ADMINISTRATOR\n"
    content += "- Data Viewer Account: DATA VIEWER\n"
    content += "- Superusers have full Django admin panel access\n"
    content += "- System Administrators have Django admin panel access based on assigned group permissions\n"
    content += "- Data Viewers have access to view all data through the application's front-end, but cannot access the Django admin panel.\n"
    content += "- Superusers can manage all users, permissions, and system settings\n"
    content += "- New users should change their password on first login\n"
    content += "- Contact developers for system administration needs\n"
    
    with open('staff_login_credentials.txt', 'w') as f:
        f.write(content)
    
    print(f"✅ Updated staff_login_credentials.txt with developer privileges noted")

if __name__ == '__main__':
    print("👑 GRANTING DEVELOPER ADMIN ACCESS")
    print("=" * 60)
    print("Promoting Saidamen Mambayao & Farissnoor Edza to SUPERUSERS")
    print("They are the system developers and need full admin access")
    print("=" * 60)
    
    # Grant superuser access
    promoted_devs, dev_errors, dev_group = grant_superuser_access()
    
    # Grant system administrator access
    promoted_admins, admin_errors, admin_group = grant_system_admin_access()

    # Grant data viewer access
    # No longer calling grant_data_viewer_access as Anne Lidasan is moved
    
    # Verify access
    verify_admin_access()
    
    # Update credentials file
    update_credentials_file()
    
    print(f"\n🎉 ADMIN PROMOTION COMPLETED!")
    print(f"👑 {promoted_devs} developers promoted to SUPERUSER status (including Anne Lidasan)")
    print(f"⚙️ {promoted_admins} system administrators configured")
    print(f"📊 0 data viewers configured")
    print(f"👥 Added to '{dev_group.name}' and '{admin_group.name}' groups")
    print(f"🔐 Access configured based on roles")
    print(f"📝 Credentials file updated with admin privileges")
    
    all_errors = dev_errors + admin_errors
    if all_errors:
        print(f"\n❌ Errors encountered:")
        for error in all_errors:
            print(f"  - {error}")
    else:
        print(f"\n✅ No errors - all specified accounts successfully configured!")
