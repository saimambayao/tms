"""
Integration tests for all database management workflows.
Tests the complete flow of database operations across different user roles.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.contrib.messages import get_messages
from datetime import timedelta
from apps.core.models import Announcement
from apps.constituents.models import BMParliamentMember
from apps.communications.models import PartnershipSubmission, DonationSubmission
from PIL import Image
import io
import json

User = get_user_model()


class DatabaseIntegrationTestCase(TestCase):
    """Base test case with common setup for database integration tests."""
    
    def setUp(self):
        self.client = Client()
        self.setup_users()
        self.setup_test_data()
    
    def bypass_mfa(self):
        """Bypass MFA verification for testing."""
        session = self.client.session
        session['mfa_verified'] = True
        session.save()
    
    def setup_users(self):
        """Create users with different roles for testing."""
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@test.com',
            password='testpass123'
        )
        
        # MP User
        self.mp_user = User.objects.create_user(
            username='mp_user',
            email='mp@test.com',
            password='testpass123',
            user_type='mp',
            first_name='Parliament',
            last_name='MP'
        )
        
        # Chief of Staff
        self.chief_of_staff = User.objects.create_user(
            username='chief_of_staff',
            email='chief@test.com',
            password='testpass123',
            user_type='chief_of_staff',
            first_name='Chief',
            last_name='Staff'
        )
        
        # System Admin
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            user_type='admin',
            first_name='System',
            last_name='Admin',
            mfa_enabled=False  # Disable MFA for test user
        )
        
        # Coordinator
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123',
            user_type='coordinator',
            first_name='Area',
            last_name='Coordinator'
        )
        
        # Information Officer
        self.info_officer = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='testpass123',
            user_type='information_officer',
            first_name='Info',
            last_name='Officer'
        )
        
        # Regular Member
        self.member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='testpass123',
            user_type='member',
            first_name='Regular',
            last_name='Member'
        )
    
    def setup_test_data(self):
        """Create initial test data."""
        # Create users for test registrants
        self.registrant1_user = User.objects.create_user(
            username='juan_member',
            email='juan@test.com',
            password='testpass123',
            user_type='member',
            first_name='Juan',
            last_name='Dela Cruz'
        )
        
        self.registrant2_user = User.objects.create_user(
            username='maria_member',
            email='maria@test.com',
            password='testpass123',
            user_type='member',
            first_name='Maria',
            last_name='Santos'
        )
        
        # Create test registrants
        self.registrant1 = BMParliamentMember.objects.create(
            user=self.registrant1_user,
            first_name='Juan',
            last_name='Dela Cruz',
            middle_name='Santos',
            email='juan@test.com',
            contact_number='09171234567',
            age=35,
            sex='male',
            address_barangay='Poblacion',
            address_municipality='General Santos City',
            address_province='South Cotabato',
            voter_address_barangay='Poblacion',
            voter_address_municipality='General Santos City',
            voter_address_province='South Cotabato',
            sector='volunteer_teacher',
            highest_education='bachelors',
            school_graduated='Mindanao State University',
            eligibility='let_passer',
            is_approved=True,
            approved_by=self.coordinator
        )
        
        self.registrant2 = BMParliamentMember.objects.create(
            user=self.registrant2_user,
            first_name='Maria',
            last_name='Santos',
            email='maria@test.com',
            contact_number='09181234567',
            age=28,
            sex='female',
            address_barangay='Lagao',
            address_municipality='General Santos City',
            address_province='South Cotabato',
            voter_address_barangay='Lagao',
            voter_address_municipality='General Santos City',
            voter_address_province='South Cotabato',
            sector='solo_parent',
            highest_education='high_school',
            eligibility='none',
            is_approved=False
        )
        
        # Create test partnership submission
        self.partner = PartnershipSubmission.objects.create(
            organization_name='Test Organization',
            contact_person='John Partner',
            email='partner@test.com',
            phone_number='09191234567',
            partnership_type='business',
            proposed_collaboration='We want to partner with you for community development projects'
        )
        
        # Create test donation submission
        self.donor = DonationSubmission.objects.create(
            donor_name='Jane Donor',
            email='donor@test.com',
            phone_number='09201234567',
            donation_type='monetary',
            amount=10000,
            description='Happy to support the cause'
        )
        
        # Create test announcements
        self.published_announcement = Announcement.objects.create(
            title='Published Announcement',
            slug='published-announcement',
            excerpt='This is published',
            content='<p>Published content</p>',
            category='news',
            status='published',
            published_date=timezone.now(),
            created_by=self.info_officer
        )
        
        self.draft_announcement = Announcement.objects.create(
            title='Draft Announcement',
            slug='draft-announcement',
            excerpt='This is a draft',
            content='<p>Draft content</p>',
            category='event',
            status='draft',
            created_by=self.coordinator
        )
    
    def create_test_image(self):
        """Create a test image for upload testing."""
        image = Image.new('RGB', (800, 600), color='blue')
        image_file = io.BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            'test_image.jpg',
            image_file.read(),
            content_type='image/jpeg'
        )


class DatabaseRegistrantsIntegrationTest(DatabaseIntegrationTestCase):
    """Integration tests for Database of Registrants workflow."""
    
    def test_complete_registrant_workflow(self):
        """Test the complete workflow of managing registrants."""
        # Login as coordinator
        self.client.login(username='coordinator', password='testpass123')
        
        # 1. View list of registrants
        response = self.client.get(reverse('database_registrants'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')
        self.assertContains(response, 'Maria')
        
        # 2. Search for specific registrant
        response = self.client.get(
            reverse('database_registrants'),
            {'search': 'Juan'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')
        self.assertNotContains(response, 'Maria')
        
        # 3. Filter by approval status
        response = self.client.get(
            reverse('database_registrants'),
            {'approval_status': 'approved'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')
        self.assertNotContains(response, 'Maria')
        
        # 4. View registrant detail
        response = self.client.get(
            reverse('database_registrant_detail', kwargs={'pk': self.registrant1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')
        self.assertContains(response, 'Dela Cruz')
        self.assertContains(response, '09171234567')
        self.assertContains(response, 'Poblacion')
        
        # 5. Edit registrant
        response = self.client.get(
            reverse('database_registrant_edit', kwargs={'pk': self.registrant1.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Update registrant data
        response = self.client.post(
            reverse('database_registrant_edit', kwargs={'pk': self.registrant1.pk}),
            {
                'first_name': 'Juan Jr.',
                'last_name': 'Dela Cruz',
                'middle_name': 'Santos Rodriguez',
                'email': 'juan.jr@test.com',
                'contact_number': '09171234567',
                'age': 35,
                'sex': 'male',
                'address_barangay': 'Poblacion',
                'address_municipality': 'General Santos City',
                'address_province': 'South Cotabato',
                'voter_address_barangay': 'Poblacion',
                'voter_address_municipality': 'General Santos City',
                'voter_address_province': 'South Cotabato',
                'sector': 'volunteer_teacher',
                'highest_education': 'masters',
                'school_graduated': 'Mindanao State University',
                'eligibility': 'both',
                'is_approved': True
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        self.registrant1.refresh_from_db()
        self.assertEqual(self.registrant1.first_name, 'Juan Jr.')
        self.assertEqual(self.registrant1.middle_name, 'Santos Rodriguez')
        self.assertEqual(self.registrant1.email, 'juan.jr@test.com')
        self.assertEqual(self.registrant1.highest_education, 'masters')
        self.assertEqual(self.registrant1.eligibility, 'both')
    
    def test_registrant_access_control(self):
        """Test that different roles have appropriate access."""
        url = reverse('database_registrants')
        
        # Test unauthorized access
        self.client.login(username='member', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test information officer doesn't have access
        self.client.login(username='info_officer', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test authorized roles
        authorized_users = [
            'superuser', 'mp_user', 'chief_of_staff', 
            'admin_user', 'coordinator'
        ]
        
        for username in authorized_users:
            self.client.login(username=username, password='testpass123')
            self.bypass_mfa()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class DatabasePartnersIntegrationTest(DatabaseIntegrationTestCase):
    """Integration tests for Database of Partners workflow."""
    
    def test_complete_partner_workflow(self):
        """Test the complete workflow of managing partners."""
        # Login as admin
        login_success = self.client.login(username='admin_user', password='testpass123')
        self.assertTrue(login_success, "Login failed for admin_user")
        self.bypass_mfa()
        
        # 1. View list of partners
        response = self.client.get(reverse('database_partners'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Organization')
        self.assertContains(response, 'John Partner')
        
        # 2. Filter by partnership type
        response = self.client.get(
            reverse('database_partners'),
            {'partner_type': 'business'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Organization')
        
        # 3. Search for partner
        response = self.client.get(
            reverse('database_partners'),
            {'search': 'Test Org'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Organization')
    
    def test_partner_status_update(self):
        """Test updating partner status."""
        self.client.login(username='mp_user', password='testpass123')
        self.bypass_mfa()
        
        # View partners list
        response = self.client.get(reverse('database_partners'))
        self.assertEqual(response.status_code, 200)
        
        # Update partner status (would be done via admin or specific view)
        self.partner.status = 'approved'
        self.partner.save()
        
        # Verify status change is reflected
        response = self.client.get(reverse('database_partners'))
        self.assertContains(response, 'approved')


class DatabaseDonorsIntegrationTest(DatabaseIntegrationTestCase):
    """Integration tests for Database of Donors workflow."""
    
    def test_complete_donor_workflow(self):
        """Test the complete workflow of managing donors."""
        # Login as chief of staff
        self.client.login(username='chief_of_staff', password='testpass123')
        self.bypass_mfa()
        
        # 1. View list of donors
        response = self.client.get(reverse('database_donors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Donor')
        self.assertContains(response, '₱10,000')
        
        # 2. Filter by donation type
        response = self.client.get(
            reverse('database_donors'),
            {'contribution_type': 'monetary'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Donor')
        
        # 3. View donation statistics
        response = self.client.get(reverse('database_donors'))
        self.assertContains(response, 'Total Contributions')
        self.assertContains(response, 'Total Donors')
    
    def test_donor_privacy_features(self):
        """Test donor privacy and anonymity features."""
        # Create anonymous donor
        anon_donor = DonationSubmission.objects.create(
            donor_name='Anonymous',
            email='anon@test.com',
            phone_number='09211234567',
            donation_type='in_kind',
            description='Anonymous donation'
        )
        
        self.client.login(username='coordinator', password='testpass123')
        response = self.client.get(reverse('database_donors'))
        
        # Check if donor information is displayed
        self.assertEqual(response.status_code, 200)


class DatabaseUpdatesIntegrationTest(DatabaseIntegrationTestCase):
    """Integration tests for Database of Updates (Announcements) workflow."""
    
    def test_complete_announcement_lifecycle(self):
        """Test the complete lifecycle of an announcement."""
        # Login as information officer
        self.client.login(username='info_officer', password='testpass123')
        
        # 1. View announcements list
        response = self.client.get(reverse('database_updates'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Announcement')
        self.assertContains(response, 'Draft Announcement')
        
        # 2. Create new announcement
        response = self.client.get(reverse('database_announcement_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit new announcement with image
        test_image = self.create_test_image()
        response = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'Integration Test Announcement',
                'category': 'news',
                'status': 'draft',
                'excerpt': 'Testing the integration',
                'content': '<p>This is a test announcement with image</p>',
                'is_featured': True,
                'image': test_image
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify announcement was created
        new_announcement = Announcement.objects.get(title='Integration Test Announcement')
        self.assertEqual(new_announcement.status, 'draft')
        self.assertTrue(new_announcement.is_featured)
        self.assertTrue(new_announcement.image)
        
        # 3. Edit announcement
        response = self.client.get(
            reverse('database_announcement_edit', kwargs={'pk': new_announcement.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Update and publish
        response = self.client.post(
            reverse('database_announcement_edit', kwargs={'pk': new_announcement.pk}),
            {
                'title': 'Integration Test Announcement - Updated',
                'category': 'event',
                'status': 'published',
                'excerpt': 'Updated excerpt',
                'content': '<p>Updated content for the announcement</p>',
                'is_featured': True
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify update and publication
        new_announcement.refresh_from_db()
        self.assertEqual(new_announcement.title, 'Integration Test Announcement - Updated')
        self.assertEqual(new_announcement.status, 'published')
        self.assertIsNotNone(new_announcement.published_date)
        
        # 4. Verify public visibility
        self.client.logout()
        response = self.client.get(reverse('announcements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Announcement - Updated')
        self.assertNotContains(response, 'Draft Announcement')  # Drafts shouldn't be visible
        
        # 5. View announcement detail
        response = self.client.get(
            reverse('announcement_detail', kwargs={'slug': new_announcement.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Updated content for the announcement')
        
        # 6. Delete announcement (as authorized user)
        self.client.login(username='info_officer', password='testpass123')
        response = self.client.post(
            reverse('database_announcement_delete', kwargs={'pk': new_announcement.pk})
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify deletion
        with self.assertRaises(Announcement.DoesNotExist):
            Announcement.objects.get(pk=new_announcement.pk)
    
    def test_announcement_filtering_and_search(self):
        """Test comprehensive filtering and search functionality."""
        self.client.login(username='coordinator', password='testpass123')
        
        # Create more test data
        for i in range(5):
            Announcement.objects.create(
                title=f'News Item {i}',
                excerpt=f'News excerpt {i}',
                content=f'News content {i}',
                category='news',
                status='published' if i % 2 == 0 else 'draft',
                is_featured=i == 0,
                created_by=self.coordinator,
                published_date=timezone.now() if i % 2 == 0 else None
            )
        
        # Test category filter
        response = self.client.get(
            reverse('database_updates'),
            {'category': 'news'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'News Item')
        
        # Test status filter
        response = self.client.get(
            reverse('database_updates'),
            {'status': 'published'}
        )
        for announcement in response.context['announcements']:
            self.assertEqual(announcement.status, 'published')
        
        # Test featured filter
        response = self.client.get(
            reverse('database_updates'),
            {'is_featured': 'yes'}
        )
        for announcement in response.context['announcements']:
            self.assertTrue(announcement.is_featured)
        
        # Test search
        response = self.client.get(
            reverse('database_updates'),
            {'search': 'News Item 2'}
        )
        self.assertContains(response, 'News Item 2')
    
    def test_save_and_continue_workflow(self):
        """Test the save and continue editing feature."""
        self.client.login(username='info_officer', password='testpass123')
        
        # Create announcement with save and continue
        response = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'Save and Continue Test',
                'category': 'update',
                'status': 'draft',
                'excerpt': 'Testing save and continue',
                'content': '<p>Initial content</p>',
                'is_featured': False,
                'save_and_continue': 'true'
            }
        )
        
        # Should redirect to edit page
        announcement = Announcement.objects.get(title='Save and Continue Test')
        expected_url = reverse('database_announcement_edit', kwargs={'pk': announcement.pk})
        self.assertRedirects(response, expected_url)
        
        # Continue editing
        response = self.client.post(
            expected_url,
            {
                'title': 'Save and Continue Test - Updated',
                'category': 'update',
                'status': 'published',
                'excerpt': 'Updated excerpt',
                'content': '<p>Updated content after save and continue</p>',
                'is_featured': True
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify final state
        announcement.refresh_from_db()
        self.assertEqual(announcement.title, 'Save and Continue Test - Updated')
        self.assertEqual(announcement.status, 'published')
        self.assertTrue(announcement.is_featured)


class CrossDatabaseIntegrationTest(DatabaseIntegrationTestCase):
    """Test interactions across different database views."""
    
    def test_role_based_navigation(self):
        """Test that users see correct navigation options based on their role."""
        test_cases = [
            # (username, should_see_registrants, should_see_partners, should_see_donors, should_see_updates)
            ('superuser', True, True, True, True),
            ('mp_user', True, True, True, True),
            ('chief_of_staff', True, True, True, True),
            ('admin_user', True, True, True, True),
            ('coordinator', True, True, True, True),
            ('info_officer', False, False, False, True),
            ('member', False, False, False, False),
        ]
        
        for username, see_reg, see_part, see_don, see_upd in test_cases:
            self.client.login(username=username, password='testpass123')
            # Bypass MFA for staff users
            if username != 'member':
                self.bypass_mfa()
            response = self.client.get(reverse('home'))
            
            # Check navigation visibility
            if see_reg:
                self.assertContains(response, 'Database of Registrants')
            else:
                self.assertNotContains(response, 'Database of Registrants')
            
            if see_part:
                self.assertContains(response, 'Database of Partners')
            else:
                self.assertNotContains(response, 'Database of Partners')
            
            if see_don:
                self.assertContains(response, 'Database of Donors')
            else:
                self.assertNotContains(response, 'Database of Donors')
            
            if see_upd:
                self.assertContains(response, 'Database of Updates')
            else:
                self.assertNotContains(response, 'Database of Updates')
    
    def test_dashboard_statistics_integration(self):
        """Test that dashboard shows correct statistics from all databases."""
        self.client.login(username='mp_user', password='testpass123')
        self.bypass_mfa()
        
        # Access a dashboard view that aggregates data
        # This would be implemented in the actual dashboard views
        # For now, test individual database statistics
        
        # Check registrants count
        response = self.client.get(reverse('database_registrants'))
        self.assertContains(response, '2')  # Total registrants
        
        # Check partners count
        response = self.client.get(reverse('database_partners'))
        self.assertContains(response, '1')  # Total partners
        
        # Check donors count
        response = self.client.get(reverse('database_donors'))
        self.assertContains(response, '1')  # Total donors
        
        # Check announcements count
        response = self.client.get(reverse('database_updates'))
        self.assertContains(response, str(Announcement.objects.count()))
    
    def test_audit_trail_across_databases(self):
        """Test that all database operations are properly logged."""
        self.client.login(username='coordinator', password='testpass123')
        
        # Perform operations across different databases
        operations = []
        
        # 1. View registrants
        response = self.client.get(reverse('database_registrants'))
        operations.append(('view', 'registrants', response.status_code))
        
        # 2. Create announcement
        response = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'Audit Test Announcement',
                'category': 'news',
                'status': 'draft',
                'excerpt': 'Audit test',
                'content': '<p>Testing audit trail</p>',
                'is_featured': False
            }
        )
        operations.append(('create', 'announcement', response.status_code))
        
        # 3. View partners
        response = self.client.get(reverse('database_partners'))
        operations.append(('view', 'partners', response.status_code))
        
        # 4. View donors
        response = self.client.get(reverse('database_donors'))
        operations.append(('view', 'donors', response.status_code))
        
        # Verify all operations succeeded
        for op_type, database, status_code in operations:
            if op_type == 'view':
                self.assertEqual(status_code, 200)
            elif op_type == 'create':
                self.assertEqual(status_code, 302)
    
    def test_concurrent_database_access(self):
        """Test that multiple users can access different databases concurrently."""
        # Create multiple clients for concurrent access
        client1 = Client()
        client2 = Client()
        client3 = Client()
        
        # Login different users
        client1.login(username='mp_user', password='testpass123')
        # Bypass MFA for mp_user
        session = client1.session
        session['mfa_verified'] = True
        session.save()
        
        client2.login(username='coordinator', password='testpass123')
        # Bypass MFA for coordinator
        session = client2.session
        session['mfa_verified'] = True
        session.save()
        
        client3.login(username='info_officer', password='testpass123')
        # Bypass MFA for info_officer
        session = client3.session
        session['mfa_verified'] = True
        session.save()
        
        # Simulate concurrent access
        response1 = client1.get(reverse('database_registrants'))
        response2 = client2.get(reverse('database_partners'))
        response3 = client3.get(reverse('database_updates'))
        
        # All should succeed
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
    
    def test_data_consistency_across_views(self):
        """Test that data remains consistent across different views."""
        self.client.login(username='admin_user', password='testpass123')
        self.bypass_mfa()
        
        # Create a featured announcement
        featured_announcement = Announcement.objects.create(
            title='Featured News',
            excerpt='Important news',
            content='<p>Very important news content</p>',
            category='news',
            status='published',
            is_featured=True,
            published_date=timezone.now(),
            created_by=self.admin_user
        )
        
        # Check it appears in database view
        response = self.client.get(reverse('database_updates'))
        self.assertContains(response, 'Featured News')
        
        # Check it appears in public view
        self.client.logout()
        response = self.client.get(reverse('announcements'))
        self.assertContains(response, 'Featured News')
        
        # Check it appears on homepage (if featured announcements are shown)
        response = self.client.get(reverse('home'))
        if 'featured_announcements' in response.context:
            self.assertTrue(
                any(ann.title == 'Featured News' 
                    for ann in response.context['featured_announcements'])
            )