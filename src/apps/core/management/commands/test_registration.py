from django.core.management.base import BaseCommand
from django.test import RequestFactory
from apps.constituents.member_forms import FahanieCaresMemberRegistrationForm
from apps.constituents.member_models import FahanieCaresMember
from apps.users.models import User
import tempfile


class Command(BaseCommand):
    help = 'Test member registration form to identify issues'

    def handle(self, *args, **options):
        """Test the registration form with sample data"""
        
        # Create test data
        test_data = {
            'username': 'testuser123',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'middle_name': 'Santos',
            'email': 'test@example.com',
            'contact_number': '09123456789',
            'age': 25,
            'sex': 'male',
            'address_barangay': 'Test Barangay',
            'address_municipality': 'Cotabato City',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Test Voter Barangay',
            'voter_address_municipality': 'Cotabato City',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'student_scholarship',
            'highest_education': 'high_school',
            'school_graduated': 'Test High School',
            'eligibility': 'none',
            'is_volunteer_teacher': False,
            'terms': True,
        }
        
        self.stdout.write("Testing registration form...")
        
        try:
            # Test form validation
            form = FahanieCaresMemberRegistrationForm(data=test_data)
            
            if form.is_valid():
                self.stdout.write(
                    self.style.SUCCESS("Form validation: PASSED")
                )
                
                # Test form save
                try:
                    user = form.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"User creation: PASSED - {user.username}")
                    )
                    
                    # Check if member was created
                    try:
                        member = FahanieCaresMember.objects.get(user=user)
                        self.stdout.write(
                            self.style.SUCCESS(f"Member creation: PASSED - {member.id}")
                        )
                        
                        # Clean up test data
                        member.delete()
                        user.delete()
                        self.stdout.write("Test data cleaned up")
                        
                    except FahanieCaresMember.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR("Member creation: FAILED - Member not created")
                        )
                        user.delete()
                        
                except Exception as save_error:
                    self.stdout.write(
                        self.style.ERROR(f"User creation: FAILED - {save_error}")
                    )
                    
            else:
                self.stdout.write(
                    self.style.ERROR("Form validation: FAILED")
                )
                for field, errors in form.errors.items():
                    self.stdout.write(f"  {field}: {errors}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Test failed with exception: {e}")
            )
        
        # Test email uniqueness
        self.stdout.write("\nTesting email uniqueness validation...")
        try:
            # Create a user first
            existing_user = User.objects.create_user(
                username='existing_user',
                email='existing@example.com',
                password='testpass123'
            )
            
            # Try to register with same email
            duplicate_data = test_data.copy()
            duplicate_data['username'] = 'newuser123'
            duplicate_data['email'] = 'existing@example.com'
            
            form = FahanieCaresMemberRegistrationForm(data=duplicate_data)
            if not form.is_valid() and 'email' in form.errors:
                self.stdout.write(
                    self.style.SUCCESS("Email uniqueness validation: PASSED")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("Email uniqueness validation: FAILED")
                )
            
            existing_user.delete()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Email uniqueness test failed: {e}")
            )
        
        self.stdout.write("\nRegistration test completed!")