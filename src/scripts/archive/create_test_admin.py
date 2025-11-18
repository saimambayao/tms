#!/usr/bin/env python3
"""
Create test admin user for Database of Registrants testing
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/macbookpro/Documents/fahanie-cares/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_admin():
    """Create a test admin user with proper permissions"""
    
    print("Creating test admin user for Database of Registrants testing...")
    
    # Create superuser for testing
    admin_data = {
        'username': 'admin_test',
        'email': 'admin@fahaniecares.test',
        'first_name': 'Test',
        'last_name': 'Administrator',
        'password': 'testadmin123',
        'is_superuser': True,
        'is_staff': True,
        'user_type': 'admin'
    }
    
    try:
        # Check if admin user already exists
        user, created = User.objects.get_or_create(
            username=admin_data['username'],
            defaults={
                'email': admin_data['email'],
                'first_name': admin_data['first_name'],
                'last_name': admin_data['last_name'],
                'is_superuser': admin_data['is_superuser'],
                'is_staff': admin_data['is_staff'],
                'user_type': admin_data.get('user_type', 'admin')
            }
        )
        
        if created:
            user.set_password(admin_data['password'])
            user.save()
            print(f"✓ Created test admin user: {user.username}")
            print(f"  📧 Email: {user.email}")
            print(f"  🔑 Password: {admin_data['password']}")
            print(f"  👑 Superuser: {user.is_superuser}")
            print(f"  📋 User Type: {getattr(user, 'user_type', 'admin')}")
        else:
            print(f"→ Admin user already exists: {user.username}")
            print(f"  📧 Email: {user.email}")
            print(f"  👑 Superuser: {user.is_superuser}")
    
    except Exception as e:
        print(f"✗ Error creating admin user: {str(e)}")
        return
    
    # Create MP user for testing
    mp_data = {
        'username': 'mp_test',
        'email': 'mp@fahaniecares.test',
        'first_name': 'MP',
        'last_name': 'Test Account',
        'password': 'testmp123',
        'is_staff': True,
        'user_type': 'mp'
    }
    
    try:
        mp_user, mp_created = User.objects.get_or_create(
            username=mp_data['username'],
            defaults={
                'email': mp_data['email'],
                'first_name': mp_data['first_name'],
                'last_name': mp_data['last_name'],
                'is_staff': mp_data['is_staff'],
                'user_type': mp_data.get('user_type', 'mp')
            }
        )
        
        if mp_created:
            mp_user.set_password(mp_data['password'])
            mp_user.save()
            print(f"✓ Created test MP user: {mp_user.username}")
            print(f"  📧 Email: {mp_user.email}")
            print(f"  🔑 Password: {mp_data['password']}")
            print(f"  📋 User Type: {getattr(mp_user, 'user_type', 'mp')}")
        else:
            print(f"→ MP user already exists: {mp_user.username}")
    
    except Exception as e:
        print(f"✗ Error creating MP user: {str(e)}")
    
    print(f"\n🎉 Test users ready for Database of Registrants testing!")
    print(f"📊 Total users: {User.objects.count()}")
    print(f"\n🔐 Login credentials for testing:")
    print(f"   Admin: admin_test / testadmin123")
    print(f"   MP: mp_test / testmp123")
    print(f"\n🌐 Access Database of Registrants at: http://localhost:3000/database/registrants/")

if __name__ == '__main__':
    create_test_admin()