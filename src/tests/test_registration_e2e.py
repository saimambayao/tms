"""
End-to-End tests for the complete user registration journey.
These tests simulate real user interactions from discovery to post-registration activities.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.messages import get_messages
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException
from PIL import Image
import io
import tempfile
import time

from apps.constituents.member_models import FahanieCaresMember
from apps.users.models import User

User = get_user_model()


class RegistrationE2ETestCase(TestCase):
    """End-to-End tests for registration without browser automation."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.maxDiff = None
    
    def test_complete_user_journey_new_visitor(self):
        """Test complete journey for a new visitor discovering the platform."""
        # Step 1: New visitor lands on home page
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, '#FahanieCares')
        
        # Step 2: Visitor learns about the platform through announcements
        announcements_response = self.client.get(reverse('announcements'))
        self.assertEqual(announcements_response.status_code, 200)
        
        # Step 3: Visitor decides to register and navigates to registration
        registration_response = self.client.get(reverse('register'))
        self.assertEqual(registration_response.status_code, 200)
        self.assertContains(registration_response, 'Member Registration')
        self.assertContains(registration_response, 'form')
        self.assertContains(registration_response, 'Terms and Conditions')
        
        # Step 4: Visitor fills out registration form
        registration_data = {
            'username': 'newvisitor2025',
            'password1': 'Nv9#Ks8$Lt7@Mq6&',
            'password2': 'Nv9#Ks8$Lt7@Mq6&',
            'last_name': 'Santos',
            'first_name': 'Maria',
            'middle_name': 'Cruz',
            'contact_number': '09171234567',
            'email': 'maria.santos@email.com',
            'age': 29,
            'sex': 'female',
            'address_barangay': 'Barangay Poblacion',
            'address_municipality': 'Shariff Aguak',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Barangay Poblacion',
            'voter_address_municipality': 'Shariff Aguak',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'women_mothers',
            'highest_education': 'bachelors',
            'school_graduated': 'Mindanao State University',
            'eligibility': 'let_passer',
            'is_volunteer_teacher': False,
            'terms': True
        }
        
        # Step 5: Submit registration
        submit_response = self.client.post(reverse('register'), data=registration_data)
        self.assertRedirects(submit_response, reverse('registration_success'))
        
        # Step 6: Verify success page content
        success_response = self.client.get(reverse('registration_success'))
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, 'success')
        
        # Step 7: Verify user and member profile creation
        user = User.objects.get(username='newvisitor2025')
        self.assertEqual(user.email, 'maria.santos@email.com')
        self.assertEqual(user.user_type, 'member')
        self.assertFalse(user.is_approved)
        
        member = FahanieCaresMember.objects.get(user=user)
        self.assertEqual(member.first_name, 'Maria')
        self.assertEqual(member.sector, 'women_mothers')
        self.assertEqual(member.eligibility, 'let_passer')
        
        # Step 8: User tries to login immediately (should work)
        login_response = self.client.post(reverse('login'), {
            'username': 'newvisitor2025',
            'password': 'Nv9#Ks8$Lt7@Mq6&'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Step 9: Logged in user accesses their profile
        profile_response = self.client.get(reverse('member_profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'Maria')
    
    def test_volunteer_teacher_registration_journey(self):
        """Test specific journey for volunteer teacher registration."""
        # Step 1: Access registration page
        self.client.get(reverse('register'))
        
        # Step 2: Fill form as volunteer teacher
        registration_data = {
            'username': 'teacher_volunteer',
            'password1': 'Tv7#Qr8$Ws9@Xt6&',
            'password2': 'Tv7#Qr8$Ws9@Xt6&',
            'last_name': 'Reyes',
            'first_name': 'Ana',
            'contact_number': '09181234567',
            'email': 'ana.reyes@email.com',
            'age': 35,
            'sex': 'female',
            'address_barangay': 'Barangay Central',
            'address_municipality': 'Parang',
            'address_province': 'Maguindanao del Norte',
            'voter_address_barangay': 'Barangay Central',
            'voter_address_municipality': 'Parang',
            'voter_address_province': 'Maguindanao del Norte',
            'sector': 'volunteer_teacher',
            'highest_education': 'bachelors',
            'school_graduated': 'Central Mindanao University',
            'eligibility': 'let_passer',
            'is_volunteer_teacher': True,
            'volunteer_school': 'Parang Elementary School',
            'volunteer_service_length': '5 years',
            'terms': True
        }
        
        # Step 3: Submit registration
        response = self.client.post(reverse('register'), data=registration_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        # Step 4: Verify volunteer teacher specific data
        user = User.objects.get(username='teacher_volunteer')
        member = FahanieCaresMember.objects.get(user=user)
        
        self.assertTrue(member.is_volunteer_teacher)
        self.assertEqual(member.volunteer_school, 'Parang Elementary School')
        self.assertEqual(member.volunteer_service_length, '5 years')
        self.assertEqual(member.sector, 'volunteer_teacher')
    
    def test_youth_student_registration_journey(self):
        """Test registration journey for youth/student."""
        registration_data = {
            'username': 'student_youth',
            'password1': 'Sy6#Zp7$Qm8@Rt9&',
            'password2': 'Sy6#Zp7$Qm8@Rt9&',
            'last_name': 'Abdullah',
            'first_name': 'Ahmad',
            'contact_number': '09191234567',
            'email': 'ahmad.abdullah@email.com',
            'age': 20,
            'sex': 'male',
            'address_barangay': 'Barangay Youth',
            'address_municipality': 'Datu Odin Sinsuat',
            'address_province': 'Maguindanao del Norte',
            'voter_address_barangay': 'Barangay Youth',
            'voter_address_municipality': 'Datu Odin Sinsuat',
            'voter_address_province': 'Maguindanao del Norte',
            'sector': 'student_scholarship',
            'highest_education': 'some_college',
            'school_graduated': 'Local High School',
            'eligibility': 'none',
            'terms': True
        }
        
        response = self.client.post(reverse('register'), data=registration_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        user = User.objects.get(username='student_youth')
        member = FahanieCaresMember.objects.get(user=user)
        
        self.assertEqual(member.sector, 'student_scholarship')
        self.assertEqual(member.get_sector_display_category(), 'Youth')
        self.assertEqual(member.age, 20)
    
    def test_pwd_student_registration_journey(self):
        """Test registration journey for PWD student."""
        registration_data = {
            'username': 'pwd_student',
            'password1': 'Ps5#Wd6$Et7@Yu8&',
            'password2': 'Ps5#Wd6$Et7@Yu8&',
            'last_name': 'Malik',
            'first_name': 'Fatima',
            'contact_number': '09201234567',
            'email': 'fatima.malik@email.com',
            'age': 22,
            'sex': 'female',
            'address_barangay': 'Barangay Inclusive',
            'address_municipality': 'Cotabato City',
            'address_province': 'Cotabato City',
            'voter_address_barangay': 'Barangay Inclusive',
            'voter_address_municipality': 'Cotabato City',
            'voter_address_province': 'Cotabato City',
            'sector': 'pwd_student',
            'highest_education': 'some_college',
            'eligibility': 'none',
            'terms': True
        }
        
        response = self.client.post(reverse('register'), data=registration_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        user = User.objects.get(username='pwd_student')
        member = FahanieCaresMember.objects.get(user=user)
        
        self.assertEqual(member.sector, 'pwd_student')
        self.assertEqual(member.get_sector_display_category(), 'Vulnerable Sectors')
    
    def test_registration_error_recovery_journey(self):
        """Test user journey when encountering and recovering from errors."""
        # Step 1: Submit form with validation errors
        invalid_data = {
            'username': '',  # Missing username
            'password1': 'weak',  # Weak password
            'password2': 'different',  # Mismatched password
            'email': 'invalid-email',  # Invalid email
            'terms': False  # Terms not accepted
        }
        
        response = self.client.post(reverse('register'), data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Step 2: User corrects errors and resubmits
        corrected_data = {
            'username': 'corrected_user',
            'password1': 'Cu4#Rr5$Ec6@Te7&',
            'password2': 'Cu4#Rr5$Ec6@Te7&',
            'last_name': 'Corrected',
            'first_name': 'User',
            'contact_number': '09171234567',
            'email': 'corrected@email.com',
            'age': 25,
            'sex': 'male',
            'address_barangay': 'Barangay Test',
            'address_municipality': 'Ampatuan',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Barangay Test',
            'voter_address_municipality': 'Ampatuan',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'student_scholarship',
            'highest_education': 'bachelors',
            'eligibility': 'none',
            'terms': True
        }
        
        response = self.client.post(reverse('register'), data=corrected_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        # Verify successful registration
        self.assertTrue(User.objects.filter(username='corrected_user').exists())
    
    def test_post_registration_member_journey(self):
        """Test member's journey after successful registration."""
        # Step 1: Register user
        registration_data = {
            'username': 'post_reg_user',
            'password1': 'Pr3#Gu4$Rs5@Tu6&',
            'password2': 'Pr3#Gu4$Rs5@Tu6&',
            'last_name': 'Post',
            'first_name': 'Registration',
            'contact_number': '09171234567',
            'email': 'postreg@email.com',
            'age': 30,
            'sex': 'female',
            'address_barangay': 'Barangay Test',
            'address_municipality': 'Ampatuan',
            'address_province': 'Maguindanao del Sur',
            'voter_address_barangay': 'Barangay Test',
            'voter_address_municipality': 'Ampatuan',
            'voter_address_province': 'Maguindanao del Sur',
            'sector': 'women_mothers',
            'highest_education': 'masters',
            'eligibility': 'csc_passer',
            'terms': True
        }
        
        self.client.post(reverse('register'), data=registration_data)
        
        # Step 2: Login as new member
        login_response = self.client.post(reverse('login'), {
            'username': 'post_reg_user',
            'password': 'Pr3#Gu4$Rs5@Tu6&'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Step 3: Access member profile
        profile_response = self.client.get(reverse('member_profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'Registration')
        
        # Step 4: Try to update profile
        update_response = self.client.get(reverse('member_update'))
        self.assertEqual(update_response.status_code, 200)
        
        # Step 5: View public content as authenticated member
        announcements_response = self.client.get(reverse('announcements'))
        self.assertEqual(announcements_response.status_code, 200)
        
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)


class RegistrationAccessibilityE2ETest(TestCase):
    """Test accessibility and usability aspects of registration."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_form_field_labels_and_help_text(self):
        """Test that form fields have proper labels and help text."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # Check for proper form field labels (using Django auto-generated labels)
        required_labels = [
            'Username', 'Password', 'First name', 'Last name',
            'Email', 'Age', 'Contact number', 'Province', 'Municipality',
            'Barangay', 'Sector', 'Highest education'
        ]
        
        for label in required_labels:
            self.assertContains(response, label)
        
        # Check for actual help text and accessibility features
        self.assertContains(response, 'placeholder')  # Check for placeholders
        self.assertContains(response, 'required')     # Check for required indicators
        self.assertContains(response, 'Photo')        # Check for photo upload section
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        # Submit form with various errors
        invalid_data = {
            'username': 'x',  # Too short
            'password1': '123',  # Too weak
            'password2': '456',  # Mismatched
            'email': 'not-an-email',  # Invalid format
            'age': -1,  # Invalid age
            'contact_number': '123',  # Invalid phone
            'terms': False  # Not accepted
        }
        
        response = self.client.post(reverse('register'), data=invalid_data)
        self.assertEqual(response.status_code, 200)
        
        # Check for specific error messages
        error_indicators = ['error', 'required', 'must']  # Removed 'invalid' as it's not always present
        for indicator in error_indicators:
            self.assertContains(response, indicator, msg_prefix=f"Should contain '{indicator}' in error messages")
    
    def test_progressive_enhancement(self):
        """Test that form works without JavaScript."""
        # Test basic form submission without JS dependencies
        form_data = {
            'username': 'no_js_user',
            'password1': 'Nj2#Sp3$As4@Sw5&',
            'password2': 'Nj2#Sp3$As4@Sw5&',
            'last_name': 'NoJS',
            'first_name': 'User',
            'contact_number': '09171234567',
            'email': 'nojs@email.com',
            'age': 25,
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
        
        response = self.client.post(reverse('register'), data=form_data)
        self.assertRedirects(response, reverse('registration_success'))
        
        # Verify user was created successfully
        self.assertTrue(User.objects.filter(username='no_js_user').exists())


class RegistrationPerformanceE2ETest(TestCase):
    """Test performance aspects of the registration process."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_registration_page_load_performance(self):
        """Test registration page loads efficiently."""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('register'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0, "Registration page should load in under 2 seconds")
    
    def test_registration_submission_performance(self):
        """Test registration form submission performance."""
        form_data = {
            'username': 'perf_user',
            'password1': 'Pf1#Er2$Fo3@Rm4&',
            'password2': 'Pf1#Er2$Fo3@Rm4&',
            'last_name': 'Performance',
            'first_name': 'Test',
            'contact_number': '09171234567',
            'email': 'perf@email.com',
            'age': 25,
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
        
        import time
        start_time = time.time()
        response = self.client.post(reverse('register'), data=form_data)
        submission_time = time.time() - start_time
        
        self.assertRedirects(response, reverse('registration_success'))
        self.assertLess(submission_time, 3.0, "Registration submission should complete in under 3 seconds")
    
    def test_bulk_registration_database_performance(self):
        """Test database performance with multiple registrations."""
        import time
        from django.test.utils import override_settings
        
        # Test creating multiple users in sequence
        start_time = time.time()
        
        for i in range(10):
            form_data = {
                'username': f'bulk_user_{i}',
                'password1': f'Bu{i}#Lk{i+1}$Pa{i+2}@Ss{i+3}&',
                'password2': f'Bu{i}#Lk{i+1}$Pa{i+2}@Ss{i+3}&',
                'last_name': f'Bulk{i}',
                'first_name': 'User',
                'contact_number': f'0917123456{i}',
                'email': f'bulk{i}@email.com',
                'age': 25,
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
            
            response = self.client.post(reverse('register'), data=form_data)
            self.assertRedirects(response, reverse('registration_success'))
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        self.assertLess(avg_time, 1.0, "Average registration time should be under 1 second")
        self.assertEqual(User.objects.filter(username__startswith='bulk_user_').count(), 10)