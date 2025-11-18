#!/usr/bin/env python3
"""
Create test registrants for Database of Registrants functionality testing
"""

import os
import sys
import django
from datetime import date

# Setup Django environment
sys.path.append('/Users/macbookpro/Documents/fahanie-cares/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.constituents.member_models import FahanieCaresMember

User = get_user_model()

def create_test_registrants():
    """Create 3 test registrants with different profiles and approval statuses"""
    
    print("Creating test registrants for Database of Registrants...")
    
    # Test data for 3 different registrants
    test_registrants = [
        {
            'user_data': {
                'username': 'maria_santos_test',
                'email': 'maria.santos@test.email',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'password': 'testpassword123'
            },
            'member_data': {
                'first_name': 'Maria',
                'last_name': 'Santos',
                'middle_name': 'Delgado',
                'contact_number': '+63912-345-6789',
                'email': 'maria.santos@test.email',
                'age': 28,
                'sex': 'female',
                'address_barangay': 'Poblacion',
                'address_municipality': 'Cotabato City',
                'address_province': 'Maguindanao del Sur',
                'voter_address_barangay': 'Poblacion',
                'voter_address_municipality': 'Cotabato City',
                'voter_address_province': 'Maguindanao del Sur',
                'sector': 'women_mothers',
                'highest_education': 'bachelors',
                'school_graduated': 'Notre Dame University',
                'eligibility': 'let_passer',
                'is_volunteer_teacher': False,
                'is_approved': True,
                'approved_date': date.today(),
            }
        },
        {
            'user_data': {
                'username': 'ahmad_ibrahim_test',
                'email': 'ahmad.ibrahim@test.email',
                'first_name': 'Ahmad',
                'last_name': 'Ibrahim',
                'password': 'testpassword123'
            },
            'member_data': {
                'first_name': 'Ahmad',
                'last_name': 'Ibrahim',
                'middle_name': 'Musa',
                'contact_number': '+63923-456-7890',
                'email': 'ahmad.ibrahim@test.email',
                'age': 35,
                'sex': 'male',
                'address_barangay': 'Tamontaka',
                'address_municipality': 'Datu Odin Sinsuat',
                'address_province': 'Maguindanao del Sur',
                'voter_address_barangay': 'Tamontaka',
                'voter_address_municipality': 'Datu Odin Sinsuat',
                'voter_address_province': 'Maguindanao del Sur',
                'sector': 'volunteer_teacher',
                'highest_education': 'masters',
                'school_graduated': 'Mindanao State University',
                'eligibility': 'both',
                'is_volunteer_teacher': True,
                'volunteer_school': 'Tamontaka Elementary School',
                'volunteer_service_length': '3 years',
                'is_approved': False,  # Pending approval
            }
        },
        {
            'user_data': {
                'username': 'fatima_abdullah_test',
                'email': 'fatima.abdullah@test.email',
                'first_name': 'Fatima',
                'last_name': 'Abdullah',
                'password': 'testpassword123'
            },
            'member_data': {
                'first_name': 'Fatima',
                'last_name': 'Abdullah',
                'middle_name': 'Hadji',
                'contact_number': '+63934-567-8901',
                'email': 'fatima.abdullah@test.email',
                'age': 22,
                'sex': 'female',
                'address_barangay': 'Barangay Rosary Heights',
                'address_municipality': 'Cotabato City',
                'address_province': 'Maguindanao del Sur',
                'voter_address_barangay': 'Barangay Rosary Heights',
                'voter_address_municipality': 'Cotabato City',
                'voter_address_province': 'Maguindanao del Sur',
                'sector': 'student_scholarship',
                'highest_education': 'some_college',
                'school_graduated': 'University of Southern Mindanao',
                'eligibility': 'none',
                'is_volunteer_teacher': False,
                'is_approved': True,
                'approved_date': date.today(),
            }
        }
    ]
    
    created_count = 0
    
    for i, registrant_data in enumerate(test_registrants, 1):
        user_data = registrant_data['user_data']
        member_data = registrant_data['member_data']
        
        try:
            # Check if user already exists
            user, user_created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            
            if user_created:
                user.set_password(user_data['password'])
                user.save()
                print(f"✓ Created user: {user.username}")
            else:
                print(f"→ User already exists: {user.username}")
            
            # Check if member profile already exists
            member, member_created = FahanieCaresMember.objects.get_or_create(
                user=user,
                defaults=member_data
            )
            
            if member_created:
                # Set approved_by for approved members
                if member.is_approved:
                    # Get a superuser for approved_by field (create if none exists)
                    superuser = User.objects.filter(is_superuser=True).first()
                    if superuser:
                        member.approved_by = superuser
                        member.save()
                
                created_count += 1
                status = "Approved" if member.is_approved else "Pending"
                print(f"✓ Created test registrant {i}: {member.get_full_name()} - {status}")
            else:
                print(f"→ Member profile already exists: {member.get_full_name()}")
                
        except Exception as e:
            print(f"✗ Error creating registrant {i}: {str(e)}")
    
    print(f"\n🎉 Successfully created {created_count} new test registrants!")
    print(f"📊 Total registrants in database: {FahanieCaresMember.objects.count()}")
    print(f"✅ Approved: {FahanieCaresMember.objects.filter(is_approved=True).count()}")
    print(f"⏳ Pending: {FahanieCaresMember.objects.filter(is_approved=False).count()}")
    
    print(f"\n📝 Test registrants created:")
    for member in FahanieCaresMember.objects.filter(user__username__endswith='_test'):
        status = "✅ Approved" if member.is_approved else "⏳ Pending"
        print(f"   • {member.get_full_name()} ({member.get_sector_display()}) - {status}")

if __name__ == '__main__':
    create_test_registrants()