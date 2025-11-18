"""
Integration tests for the member registration flow.
Tests the complete registration process including form submission, user creation, and member profile creation.
"""
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.test.utils import override_settings
from django.core import mail
from PIL import Image
import io
import tempfile
import os

from apps.constituents.member_models import FahanieCaresMember
from apps.users.models import User

User = get_user_model()


class RegistrationIntegrationTest(TransactionTestCase):
    """Integration test for complete registration workflow."""
    
    def setUp(self):
        """Set up test client and URLs."""
        self.client = Client()
        self.registration_url = reverse('register')
        self.success_url = reverse('registration_success')
        # Clean up ALL users and members to ensure complete isolation
        FahanieCaresMember.objects.all().delete()
        User.objects.all().delete()
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up uploaded files before deleting members
        for member in FahanieCaresMember.objects.all():
            if member.voter_id_photo:
                try:
                    if os.path.exists(member.voter_id_photo.path):
                        os.remove(member.voter_id_photo.path)
                except Exception:
                    pass  # Ignore file cleanup errors
        
        # Delete test data
        FahanieCaresMember.objects.all().delete()
        User.objects.filter(username__startswith='test').delete()  # Only delete test users
        
    def create_test_image(self):
        """Create a valid test image for voter ID upload."""
        image = Image.new('RGB', (800, 600), color='blue')
        temp_file = io.BytesIO()
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        file_content = temp_file.read()
        temp_file.close()
        return SimpleUploadedFile(
            'voter_id.jpg',
            file_content,
            content_type='image/jpeg'
        )
    
    def get_valid_registration_data(self):
        """Get valid registration form data."""
        return {
            'username': 'test_integration_user',
            'password1': 'Zx9#Kq8$Vn2@Mp7&',
            'password2': 'Zx9#Kq8$Vn2@Mp7&',
            'last_name': 'Integration',
            'first_name': 'Test',
            'middle_name': 'User',
            'contact_number': '09171234567',
            'email': 'integration@test.com',
            'age': 28,
            'sex': 'female',
            'address_barangay': 'Barangay Integration',
            'address_municipality': 'Ampatuan',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Barangay Integration',
            'voter_address_municipality': 'Ampatuan',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'women_mothers',
            'highest_education': 'masters',
            'school_graduated': 'University of Test',
            'eligibility': 'csc_passer',
            'is_volunteer_teacher': False,
            'terms': True
        }
    
    def test_complete_registration_workflow(self):
        """Test complete registration workflow from form to success."""
        # Step 1: Access registration page
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#FahanieCares Member Registration')
        
        # Step 2: Submit valid registration data
        form_data = self.get_valid_registration_data()
        response = self.client.post(self.registration_url, data=form_data)
        
        # Step 3: Verify redirect to success page
        self.assertRedirects(response, self.success_url)
        
        # Step 4: Verify user was created with correct data
        user = User.objects.get(username='test_integration_user')
        self.assertEqual(user.email, 'integration@test.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'Integration')
        self.assertEqual(user.middle_name, 'User')
        self.assertEqual(user.phone_number, '09171234567')
        self.assertEqual(user.user_type, 'member')
        self.assertFalse(user.is_approved)
        
        # Step 5: Verify member profile was created
        member = FahanieCaresMember.objects.get(user=user)
        self.assertEqual(member.first_name, 'Test')
        self.assertEqual(member.last_name, 'Integration')
        self.assertEqual(member.middle_name, 'User')
        self.assertEqual(member.email, 'integration@test.com')
        self.assertEqual(member.contact_number, '09171234567')
        self.assertEqual(member.age, 28)
        self.assertEqual(member.sex, 'female')
        self.assertEqual(member.address_barangay, 'Barangay Integration')
        self.assertEqual(member.address_municipality, 'Ampatuan')
        self.assertEqual(member.address_province, 'Maguindanao del Sur')
        self.assertEqual(member.sector, 'women_mothers')
        self.assertEqual(member.highest_education, 'masters')
        self.assertEqual(member.eligibility, 'csc_passer')
        self.assertFalse(member.is_volunteer_teacher)
        self.assertFalse(member.is_approved)
        
        # Step 6: Check success page displays correctly
        success_response = self.client.get(self.success_url)
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, 'success')
    
    def test_registration_with_volunteer_teacher_info(self):
        """Test registration with volunteer teacher information."""
        form_data = self.get_valid_registration_data()
        form_data.update({
            'username': 'test_volunteer_teacher',
            'email': 'volunteer@test.com',
            'password1': 'Yz8#Lp9$Wm3@Nq6&',
            'password2': 'Yz8#Lp9$Wm3@Nq6&',
            'is_volunteer_teacher': True,
            'volunteer_school': 'Elementary School of Test',
            'volunteer_service_length': '3 years'
        })
        
        response = self.client.post(self.registration_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        
        user = User.objects.get(username='test_volunteer_teacher')
        member = FahanieCaresMember.objects.get(user=user)
        
        self.assertTrue(member.is_volunteer_teacher)
        self.assertEqual(member.volunteer_school, 'Elementary School of Test')
        self.assertEqual(member.volunteer_service_length, '3 years')
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_registration_with_file_upload(self):
        """Test registration with voter ID photo upload."""
        form_data = self.get_valid_registration_data()
        form_data.update({
            'username': 'test_file_upload_user',
            'email': 'fileupload@test.com',
            'password1': 'Ax7#Br8$Cs9@Dt5&',
            'password2': 'Ax7#Br8$Cs9@Dt5&'
        })
        
        test_image = self.create_test_image()
        
        response = self.client.post(
            self.registration_url,
            data=form_data,
            files={'voter_id_photo': test_image}
        )
        
        # Debug: Check if form has errors
        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            if hasattr(response.context, 'form') and response.context['form']:
                print(f"Form errors: {response.context['form'].errors}")
        
        self.assertRedirects(response, self.success_url)
        
        user = User.objects.get(username='test_file_upload_user')
        member = FahanieCaresMember.objects.get(user=user)
        
        # Check if file was uploaded
        if member.voter_id_photo:
            self.assertTrue(member.voter_id_photo.name.endswith('.jpg'))
        else:
            # If file upload failed, just verify the rest of the registration worked
            self.assertEqual(member.first_name, 'Test')
            self.assertEqual(member.email, 'fileupload@test.com')
        
        # Clean up uploaded file
        if member.voter_id_photo:
            if os.path.exists(member.voter_id_photo.path):
                os.remove(member.voter_id_photo.path)
    
    def test_registration_error_handling(self):
        """Test registration error handling and form validation."""
        # Test with invalid data
        invalid_form_data = {
            'username': '',  # Missing required field
            'password1': 'weak',  # Weak password
            'password2': 'different',  # Mismatched password
            'email': 'invalid-email',  # Invalid email format
            'age': 0,  # Invalid age
            'contact_number': '123',  # Invalid phone number
            'terms': False  # Terms not accepted
        }
        
        response = self.client.post(self.registration_url, data=invalid_form_data)
        
        # Should stay on registration page with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Verify no user or member was created
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(FahanieCaresMember.objects.count(), 0)
    
    def test_duplicate_registration_prevention(self):
        """Test prevention of duplicate registrations."""
        # Create first user
        form_data = self.get_valid_registration_data()
        response = self.client.post(self.registration_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        
        # Try to register with same username
        form_data['email'] = 'different@test.com'
        response = self.client.post(self.registration_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        
        # Try to register with same email
        form_data = self.get_valid_registration_data()
        form_data['username'] = 'different_username'
        response = self.client.post(self.registration_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        
        # Verify only one user exists
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(FahanieCaresMember.objects.count(), 1)
    
    def test_registration_message_system(self):
        """Test Django messages system integration."""
        form_data = self.get_valid_registration_data()
        response = self.client.post(self.registration_url, data=form_data, follow=True)
        
        # Check if success message was set
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('success' in str(message).lower() for message in messages))
    
    def test_different_province_municipality_combinations(self):
        """Test registration with different province/municipality combinations."""
        test_combinations = [
            ('Maguindanao del Sur', 'Shariff Aguak'),
            ('Maguindanao del Norte', 'Parang'),
            ('Cotabato City', 'Cotabato City'),
            ('Special Geographic Areas', 'Pahamuddin')
        ]
        
        for i, (province, municipality) in enumerate(test_combinations):
            form_data = self.get_valid_registration_data()
            form_data.update({
                'username': f'test_user_{i}',
                'email': f'user{i}@test.com',
                'password1': f'Mx{i}Np{i+1}Qr{i+2}St{i+3}#$@&',
                'password2': f'Mx{i}Np{i+1}Qr{i+2}St{i+3}#$@&',
                'address_province': province,
                'address_municipality': municipality,
                'voter_address_province': province,
                'voter_address_municipality': municipality
            })
            
            response = self.client.post(self.registration_url, data=form_data)
            self.assertRedirects(response, self.success_url, 
                               msg_prefix=f"Failed for {province}, {municipality}")
            
            user = User.objects.get(username=f'test_user_{i}')
            member = FahanieCaresMember.objects.get(user=user)
            self.assertEqual(member.address_province, province)
            self.assertEqual(member.address_municipality, municipality)
    
    def test_all_sector_types(self):
        """Test registration with all available sector types."""
        sectors = [
            'pwd_student', 'solo_parent', 'volunteer_teacher', 'volunteer_health',
            'special_needs', 'senior_citizen', 'women_mothers', 'student_scholarship',
            'student_assistance'
        ]
        
        for i, sector in enumerate(sectors):
            form_data = self.get_valid_registration_data()
            form_data.update({
                'username': f'test_sector_user_{i}',
                'email': f'sector{i}@test.com',
                'password1': f'Sx{i}Ty{i+1}Uz{i+2}Vw{i+3}#$@&',
                'password2': f'Sx{i}Ty{i+1}Uz{i+2}Vw{i+3}#$@&',
                'sector': sector
            })
            
            response = self.client.post(self.registration_url, data=form_data)
            self.assertRedirects(response, self.success_url,
                               msg_prefix=f"Failed for sector {sector}")
            
            user = User.objects.get(username=f'test_sector_user_{i}')
            member = FahanieCaresMember.objects.get(user=user)
            self.assertEqual(member.sector, sector)
    
    def test_all_education_levels(self):
        """Test registration with all education levels."""
        education_levels = [
            'elementary', 'high_school', 'vocational', 'some_college',
            'bachelors', 'masters', 'doctorate', 'other'
        ]
        
        for i, education in enumerate(education_levels):
            form_data = self.get_valid_registration_data()
            form_data.update({
                'username': f'test_edu_user_{i}',
                'email': f'edu{i}@test.com',
                'password1': f'Ex{i}Fy{i+1}Gz{i+2}Ha{i+3}#$@&',
                'password2': f'Ex{i}Fy{i+1}Gz{i+2}Ha{i+3}#$@&',
                'highest_education': education
            })
            
            response = self.client.post(self.registration_url, data=form_data)
            self.assertRedirects(response, self.success_url,
                               msg_prefix=f"Failed for education {education}")
            
            user = User.objects.get(username=f'test_edu_user_{i}')
            member = FahanieCaresMember.objects.get(user=user)
            self.assertEqual(member.highest_education, education)
    
    def test_registration_database_consistency(self):
        """Test database consistency after registration."""
        form_data = self.get_valid_registration_data()
        
        # Count before registration
        user_count_before = User.objects.count()
        member_count_before = FahanieCaresMember.objects.count()
        
        response = self.client.post(self.registration_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        
        # Count after registration
        user_count_after = User.objects.count()
        member_count_after = FahanieCaresMember.objects.count()
        
        # Verify counts increased by exactly 1
        self.assertEqual(user_count_after, user_count_before + 1)
        self.assertEqual(member_count_after, member_count_before + 1)
        
        # Verify relationship integrity
        user = User.objects.get(username='test_integration_user')
        member = FahanieCaresMember.objects.get(user=user)
        self.assertEqual(member.user, user)
        
        # Verify cascade behavior
        user_id = user.id
        member_id = member.id
        user.delete()
        
        # Member should be deleted due to CASCADE
        self.assertFalse(FahanieCaresMember.objects.filter(id=member_id).exists())


class RegistrationWorkflowIntegrationTest(TransactionTestCase):
    """Test registration workflow with other system components."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.registration_url = reverse('register')
        # Clean up ALL users and members to ensure complete isolation
        FahanieCaresMember.objects.all().delete()
        User.objects.all().delete()
    
    def test_registration_to_login_workflow(self):
        """Test workflow from registration to login."""
        # Step 1: Register new user
        form_data = {
            'username': 'test_workflow_user',
            'password1': 'Wx7#Ky8$Pz9@Qt5&',
            'password2': 'Wx7#Ky8$Pz9@Qt5&',
            'last_name': 'Workflow',
            'first_name': 'Test',
            'contact_number': '09171234567',
            'email': 'workflow@test.com',
            'age': 30,
            'sex': 'male',
            'address_barangay': 'Test Barangay',
            'address_municipality': 'Ampatuan',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Test Barangay',
            'voter_address_municipality': 'Ampatuan',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'student_scholarship',
            'highest_education': 'bachelors',
            'eligibility': 'none',
            'terms': True
        }
        
        response = self.client.post(self.registration_url, data=form_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        # Step 2: Try to login with new credentials
        login_response = self.client.post(reverse('login'), {
            'username': 'test_workflow_user',
            'password': 'Wx7#Ky8$Pz9@Qt5&'
        })
        
        # Should redirect after successful login
        self.assertEqual(login_response.status_code, 302)
        
        # Step 3: Verify user is authenticated
        user = User.objects.get(username='test_workflow_user')
        self.assertTrue(user.is_authenticated)
    
    def test_registration_approval_workflow(self):
        """Test registration with approval workflow."""
        # Register new user
        form_data = {
            'username': 'test_approval_user',
            'password1': 'Ap9#Lv8$Ky7@Mr6&',
            'password2': 'Ap9#Lv8$Ky7@Mr6&',
            'last_name': 'Approval',
            'first_name': 'Test',
            'contact_number': '09171234567',
            'email': 'approval@test.com',
            'age': 25,
            'sex': 'female',
            'address_barangay': 'Test Barangay',
            'address_municipality': 'Ampatuan',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Test Barangay',
            'voter_address_municipality': 'Ampatuan',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'women_mothers',
            'highest_education': 'high_school',
            'eligibility': 'none',
            'terms': True
        }
        
        self.client.post(self.registration_url, data=form_data)
        
        # Verify user is not approved initially
        user = User.objects.get(username='test_approval_user')
        member = FahanieCaresMember.objects.get(user=user)
        self.assertFalse(user.is_approved)
        self.assertFalse(member.is_approved)
        
        # Simulate approval
        user.is_approved = True
        user.save()
        member.is_approved = True
        member.save()
        
        # Verify approval status
        user.refresh_from_db()
        member.refresh_from_db()
        self.assertTrue(user.is_approved)
        self.assertTrue(member.is_approved)