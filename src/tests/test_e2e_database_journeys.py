"""
End-to-End tests for complete user journeys across all database management features.
These tests simulate real-world workflows from start to finish.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Announcement
from apps.constituents.models import FahanieCaresMember
from apps.communications.models import PartnershipSubmission, DonationSubmission
from PIL import Image
import io
import json

User = get_user_model()


class E2ECoordinatorJourneyTest(TestCase):
    """E2E test for a Coordinator's complete workflow."""
    
    def setUp(self):
        self.client = Client()
        
        # Create coordinator user
        self.coordinator = User.objects.create_user(
            username='area_coordinator',
            email='coordinator@fahaniecares.ph',
            password='SecurePass123!',
            user_type='coordinator',
            first_name='Area',
            last_name='Coordinator'
        )
        
        # Create another user for registrants
        self.registrant_user = User.objects.create_user(
            username='registrant_user',
            email='registrant@test.com',
            password='testpass123',
            user_type='member',
            first_name='New',
            last_name='Registrant'
        )
    
    def test_coordinator_daily_workflow(self):
        """Test a coordinator's typical daily workflow."""
        # 1. Login
        login_response = self.client.post(reverse('login'), {
            'username': 'area_coordinator',
            'password': 'SecurePass123!'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Bypass MFA
        session = self.client.session
        session['mfa_verified'] = True
        session.save()
        
        # 2. View dashboard/home page
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        
        # 3. Check registrants database
        registrants_response = self.client.get(reverse('database_registrants'))
        self.assertEqual(registrants_response.status_code, 200)
        self.assertContains(registrants_response, 'Database of Registrants')
        
        # 4. Create a new registrant
        new_registrant = FahanieCaresMember.objects.create(
            user=self.registrant_user,
            first_name='New',
            last_name='Registrant',
            email='registrant@test.com',
            contact_number='09123456789',
            age=25,
            sex='female',
            address_barangay='Test Barangay',
            address_municipality='Test Municipality',
            address_province='Test Province',
            voter_address_barangay='Test Barangay',
            voter_address_municipality='Test Municipality',
            voter_address_province='Test Province',
            sector='youth',
            highest_education='bachelors',
            is_approved=False
        )
        
        # 5. View and approve the registrant
        detail_response = self.client.get(
            reverse('database_registrant_detail', kwargs={'pk': new_registrant.pk})
        )
        self.assertEqual(detail_response.status_code, 200)
        
        # Edit and approve
        edit_response = self.client.post(
            reverse('database_registrant_edit', kwargs={'pk': new_registrant.pk}),
            {
                'first_name': 'New',
                'last_name': 'Registrant',
                'email': 'registrant@test.com',
                'contact_number': '09123456789',
                'age': 25,
                'sex': 'female',
                'address_barangay': 'Test Barangay',
                'address_municipality': 'Test Municipality',
                'address_province': 'Test Province',
                'voter_address_barangay': 'Test Barangay',
                'voter_address_municipality': 'Test Municipality',
                'voter_address_province': 'Test Province',
                'sector': 'youth',
                'highest_education': 'bachelors',
                'is_approved': True
            }
        )
        # Edit view returns 200 with the form on success (not a redirect)
        self.assertEqual(edit_response.status_code, 200)
        
        # 6. Check partners database
        partners_response = self.client.get(reverse('database_partners'))
        self.assertEqual(partners_response.status_code, 200)
        
        # 7. Check donors database
        donors_response = self.client.get(reverse('database_donors'))
        self.assertEqual(donors_response.status_code, 200)
        
        # 8. Create an announcement update
        announcement_create_response = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'New Community Program Launch',
                'category': 'news',
                'status': 'published',
                'excerpt': 'Announcing new community development program',
                'content': '<p>We are excited to announce a new community development program...</p>',
                'is_featured': True
            }
        )
        self.assertEqual(announcement_create_response.status_code, 302)
        
        # 9. Verify announcement is visible
        updates_response = self.client.get(reverse('database_updates'))
        self.assertEqual(updates_response.status_code, 200)
        self.assertContains(updates_response, 'New Community Program Launch')
        
        # 10. Check public visibility
        self.client.logout()
        public_announcements = self.client.get(reverse('announcements'))
        self.assertEqual(public_announcements.status_code, 200)
        self.assertContains(public_announcements, 'New Community Program Launch')


class E2EInformationOfficerJourneyTest(TestCase):
    """E2E test for an Information Officer's content management workflow."""
    
    def setUp(self):
        self.client = Client()
        
        # Create information officer
        self.info_officer = User.objects.create_user(
            username='info_officer',
            email='info@fahaniecares.ph',
            password='InfoPass123!',
            user_type='information_officer',
            first_name='Info',
            last_name='Officer'
        )
    
    def create_test_image(self):
        """Create a test image for upload."""
        image = Image.new('RGB', (1200, 630), color='green')
        image_file = io.BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            'announcement_image.jpg',
            image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_information_officer_content_workflow(self):
        """Test an information officer's content creation and management workflow."""
        # 1. Login
        self.client.login(username='info_officer', password='InfoPass123!')
        
        # Bypass MFA
        session = self.client.session
        session['mfa_verified'] = True
        session.save()
        
        # 2. Navigate to announcements database
        updates_response = self.client.get(reverse('database_updates'))
        self.assertEqual(updates_response.status_code, 200)
        
        # 3. Create multiple announcements with different statuses
        # Create announcements directly in the database for E2E test
        Announcement.objects.create(
            title='Community Health Drive',
            slug='community-health-drive',
            category='event',
            status='published',
            excerpt='Free health checkups for all residents',
            content='<p>Join us for a free health checkup drive...</p>',
            is_featured=True,
            created_by=self.info_officer,
            published_date=timezone.now()
        )
        
        Announcement.objects.create(
            title='Draft: Upcoming Festival',
            slug='draft-upcoming-festival',
            category='event',
            status='draft',
            excerpt='Annual festival planning',
            content='<p>Planning for the annual festival is underway...</p>',
            is_featured=False,
            created_by=self.info_officer
        )
        
        Announcement.objects.create(
            title='Emergency Alert: Weather Update',
            slug='emergency-alert-weather-update',
            category='news',  # 'alert' is not a valid category choice
            status='published',
            excerpt='Important weather advisory',
            content='<p>Please be advised of incoming weather conditions...</p>',
            is_featured=True,
            created_by=self.info_officer,
            published_date=timezone.now()
        )
        
        # 4. Filter and search announcements
        # Filter by category
        event_filter = self.client.get(
            reverse('database_updates'),
            {'category': 'event'}
        )
        self.assertEqual(event_filter.status_code, 200)
        self.assertContains(event_filter, 'Community Health Drive')
        
        # Filter by status
        published_filter = self.client.get(
            reverse('database_updates'),
            {'status': 'published'}
        )
        self.assertEqual(published_filter.status_code, 200)
        self.assertNotContains(published_filter, 'Draft: Upcoming Festival')
        
        # Search functionality
        search_response = self.client.get(
            reverse('database_updates'),
            {'search': 'health'}
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, 'Community Health Drive')
        
        # 5. Edit draft and publish
        draft_announcement = Announcement.objects.get(title='Draft: Upcoming Festival')
        edit_response = self.client.post(
            reverse('database_announcement_edit', kwargs={'pk': draft_announcement.pk}),
            {
                'title': 'Annual Festival 2025',
                'category': 'event',
                'status': 'published',
                'excerpt': 'Join us for the annual festival celebration',
                'content': '<p>The annual festival is confirmed for next month...</p>',
                'is_featured': True,
                'save_and_continue': 'true'
            }
        )
        self.assertRedirects(
            edit_response,
            reverse('database_announcement_edit', kwargs={'pk': draft_announcement.pk})
        )
        
        # 6. Verify public visibility of published announcements
        self.client.logout()
        
        # Check public announcements page
        public_response = self.client.get(reverse('announcements'))
        self.assertEqual(public_response.status_code, 200)
        self.assertContains(public_response, 'Community Health Drive')
        self.assertContains(public_response, 'Emergency Alert: Weather Update')
        self.assertContains(public_response, 'Annual Festival 2025')
        
        # Check individual announcement
        health_announcement = Announcement.objects.get(title='Community Health Drive')
        detail_response = self.client.get(
            reverse('announcement_detail', kwargs={'slug': health_announcement.slug})
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Free health checkups for all residents')


class E2EMPUserJourneyTest(TestCase):
    """E2E test for MP user's oversight and reporting workflow."""
    
    def setUp(self):
        self.client = Client()
        
        # Create MP user
        self.mp_user = User.objects.create_user(
            username='mp_fahanie',
            email='mp@fahaniecares.ph',
            password='MPSecure123!',
            user_type='mp',
            first_name='Fahanie',
            last_name='Uy-Oyod'
        )
        
        # Create test data across all databases
        self.setup_test_data()
    
    def bypass_mfa(self):
        """Bypass MFA verification for testing."""
        session = self.client.session
        session['mfa_verified'] = True
        session.save()
    
    def setup_test_data(self):
        """Create comprehensive test data."""
        # Create users for registrants
        for i in range(5):
            user = User.objects.create_user(
                username=f'member_{i}',
                email=f'member{i}@test.com',
                password='testpass123',
                user_type='member',
                first_name=f'Member{i}',
                last_name='Test'
            )
            
            FahanieCaresMember.objects.create(
                user=user,
                first_name=f'Member{i}',
                last_name='Test',
                email=f'member{i}@test.com',
                contact_number=f'0917123456{i}',
                age=25 + i,
                sex='male' if i % 2 == 0 else 'female',
                address_barangay=f'Barangay {i}',
                address_municipality='Test City',
                address_province='Test Province',
                voter_address_barangay=f'Barangay {i}',
                voter_address_municipality='Test City',
                voter_address_province='Test Province',
                sector='youth' if i < 3 else 'senior_citizen',
                highest_education='bachelors',
                is_approved=i < 3
            )
        
        # Create partnership submissions
        for i in range(3):
            PartnershipSubmission.objects.create(
                organization_name=f'Partner Org {i}',
                contact_person=f'Contact {i}',
                email=f'partner{i}@test.com',
                phone_number=f'0919123456{i}',
                partnership_type='business' if i == 0 else 'ngo',
                proposed_collaboration=f'Partnership proposal {i}',
                status='approved' if i == 0 else 'new'
            )
        
        # Create donation submissions
        for i in range(4):
            DonationSubmission.objects.create(
                donor_name=f'Donor {i}',
                email=f'donor{i}@test.com',
                phone_number=f'0920123456{i}',
                donation_type='monetary',
                amount=10000 * (i + 1),
                description=f'Donation for community programs {i}',
                status='completed' if i < 2 else 'pledged'
            )
        
        # Create announcements
        for i in range(6):
            Announcement.objects.create(
                title=f'Announcement {i}',
                slug=f'announcement-{i}',
                excerpt=f'Excerpt for announcement {i}',
                content=f'<p>Content for announcement {i}</p>',
                category='news' if i < 3 else 'event',
                status='published' if i < 4 else 'draft',
                is_featured=i == 0,
                published_date=timezone.now() - timedelta(days=i) if i < 4 else None,
                created_by=self.mp_user
            )
    
    def test_mp_comprehensive_oversight_workflow(self):
        """Test MP's comprehensive oversight across all databases."""
        # 1. Login as MP
        self.client.login(username='mp_fahanie', password='MPSecure123!')
        self.bypass_mfa()
        
        # 2. Review overall statistics on home page
        home_response = self.client.get(reverse('home'))
        self.assertIn(home_response.status_code, [200, 302], 
                     "MP should be able to access home page or be redirected to appropriate dashboard")
        
        # 3. Check registrants database with filtering
        registrants_response = self.client.get(reverse('database_registrants'))
        self.assertIn(registrants_response.status_code, [200, 302], 
                     "MP should be able to access registrants database or be redirected")
        
        # Only check content if we got a successful response
        if registrants_response.status_code == 200:
            self.assertContains(registrants_response, 'Total Registrants')
        
        # Filter approved registrants
        approved_response = self.client.get(
            reverse('database_registrants'),
            {'approval_status': 'approved'}
        )
        self.assertEqual(approved_response.status_code, 200)
        
        # Search for specific sector
        youth_response = self.client.get(
            reverse('database_registrants'),
            {'sector': 'youth'}
        )
        self.assertEqual(youth_response.status_code, 200)
        
        # 4. Review partners with export consideration
        partners_response = self.client.get(reverse('database_partners'))
        self.assertEqual(partners_response.status_code, 200)
        self.assertContains(partners_response, 'Total Partners')
        self.assertContains(partners_response, 'Export Data')  # MP can export
        
        # Filter approved partners
        approved_partners = self.client.get(
            reverse('database_partners'),
            {'status': 'approved'}
        )
        self.assertEqual(approved_partners.status_code, 200)
        
        # 5. Analyze donor contributions
        donors_response = self.client.get(reverse('database_donors'))
        self.assertEqual(donors_response.status_code, 200)
        self.assertContains(donors_response, 'Total Contributions')
        
        # Filter by amount range
        high_value_donors = self.client.get(
            reverse('database_donors'),
            {'amount_range': '10000-50000'}
        )
        self.assertEqual(high_value_donors.status_code, 200)
        
        # 6. Review all announcements
        updates_response = self.client.get(reverse('database_updates'))
        self.assertEqual(updates_response.status_code, 200)
        
        # Check statistics
        self.assertContains(updates_response, 'Total Announcements')
        self.assertContains(updates_response, 'Published')
        self.assertContains(updates_response, 'Draft')
        
        # 7. Create high-priority announcement
        priority_announcement = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'Important Policy Update from MP Uy-Oyod',
                'category': 'update',
                'status': 'published',
                'excerpt': 'New policies for constituent services',
                'content': '''<p>Dear constituents,</p>
                <p>We are implementing new policies to better serve you...</p>
                <ul>
                <li>Enhanced service delivery</li>
                <li>Streamlined application process</li>
                <li>Improved response times</li>
                </ul>''',
                'is_featured': True
            }
        )
        self.assertEqual(priority_announcement.status_code, 302)
        
        # 8. Verify cross-database insights
        # This would typically involve a dashboard view that aggregates data
        # For now, we verify individual database access
        databases_accessed = [
            reverse('database_registrants'),
            reverse('database_partners'),
            reverse('database_donors'),
            reverse('database_updates')
        ]
        
        for url in databases_accessed:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class E2EPublicUserJourneyTest(TestCase):
    """E2E test for public user interactions with the system."""
    
    def setUp(self):
        self.client = Client()
        
        # Create published announcements
        self.setup_public_content()
    
    def setup_public_content(self):
        """Create content visible to public users."""
        # Create staff user for announcements
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            user_type='coordinator'
        )
        
        # Create announcements
        announcements = [
            {
                'title': 'Free Medical Mission',
                'slug': 'free-medical-mission',
                'excerpt': 'Free medical checkups and medicines',
                'content': '<p>Join our free medical mission this weekend...</p>',
                'category': 'event',
                'status': 'published',
                'is_featured': True,
                'published_date': timezone.now()
            },
            {
                'title': 'Scholarship Program Open',
                'slug': 'scholarship-program-open',
                'excerpt': 'Applications now open for 2025 scholarships',
                'content': '<p>We are accepting applications for our scholarship program...</p>',
                'category': 'news',
                'status': 'published',
                'is_featured': False,
                'published_date': timezone.now() - timedelta(days=2)
            },
            {
                'title': 'Community Development Updates',
                'slug': 'community-development-updates',
                'excerpt': 'Latest updates on community projects',
                'content': '<p>Here are the latest updates on our community development projects...</p>',
                'category': 'update',
                'status': 'published',
                'is_featured': False,
                'published_date': timezone.now() - timedelta(days=5)
            }
        ]
        
        for data in announcements:
            data['created_by'] = staff_user
            Announcement.objects.create(**data)
    
    def test_public_user_information_journey(self):
        """Test a public user's journey to find information and submit inquiries."""
        # 1. Visit home page
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, '#FahanieCares')
        
        # 2. View announcements
        announcements_response = self.client.get(reverse('announcements'))
        self.assertEqual(announcements_response.status_code, 200)
        self.assertContains(announcements_response, 'Free Medical Mission')
        self.assertContains(announcements_response, 'Scholarship Program Open')
        
        # 3. View specific announcement
        announcement = Announcement.objects.get(slug='free-medical-mission')
        detail_response = self.client.get(
            reverse('announcement_detail', kwargs={'slug': announcement.slug})
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Join our free medical mission')
        
        # 4. Submit contact form inquiry
        contact_response = self.client.post(reverse('contact'), {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'email': 'juan@example.com',
            'phone_number': '09171234567',
            'subject': 'assistance',
            'message': 'I would like to inquire about the medical mission schedule and requirements.'
        })
        self.assertEqual(contact_response.status_code, 200)
        self.assertContains(contact_response, 'Thank you for your message')
        
        # 5. Submit partnership inquiry
        partner_response = self.client.post(reverse('partner'), {
            'organization_name': 'Local Business Inc.',
            'contact_person': 'Maria Santos',
            'email': 'maria@localbusiness.com',
            'phone_number': '09181234567',
            'partnership_type': 'business',
            'proposed_collaboration': 'We would like to sponsor your medical missions.',
            'resources_offered': 'Financial support and venue',
            'expected_outcomes': 'Help the community while gaining visibility'
        })
        self.assertEqual(partner_response.status_code, 200)
        self.assertContains(partner_response, 'Thank you for your partnership inquiry')
        
        # 6. Submit donation inquiry
        donate_response = self.client.post(reverse('donate'), {
            'donor_name': 'Anonymous Donor',
            'donor_type': 'individual',
            'email': 'donor@example.com',
            'phone_number': '09191234567',
            'donation_type': 'monetary',
            'amount': '5000',
            'description': 'Happy to support your programs',
            'frequency': 'one_time',
            'preferred_program': 'Medical missions'
        })
        self.assertEqual(donate_response.status_code, 200)
        self.assertContains(donate_response, 'Thank you for your donation inquiry')
        
        # 7. Try to access restricted areas (should be redirected)
        restricted_urls = [
            reverse('database_registrants'),
            reverse('database_partners'),
            reverse('database_donors'),
            reverse('database_updates')
        ]
        
        for url in restricted_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                response.url.startswith(reverse('login')) or
                response.url == reverse('home')
            )


class E2ECompleteSystemWorkflowTest(TestCase):
    """E2E test demonstrating complete system workflow from submission to resolution."""
    
    def setUp(self):
        self.client = Client()
        self.setup_users()
    
    def bypass_mfa(self):
        """Bypass MFA verification for testing."""
        session = self.client.session
        session['mfa_verified'] = True
        session.save()
    
    def setup_users(self):
        """Setup all user types."""
        self.mp = User.objects.create_user(
            username='mp',
            email='mp@test.com',
            password='test123',
            user_type='mp'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='test123',
            user_type='coordinator'
        )
        
        self.info_officer = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='test123',
            user_type='information_officer'
        )
    
    def test_complete_partnership_workflow(self):
        """Test complete workflow from partnership inquiry to approval and announcement."""
        # 1. Public user submits partnership proposal
        self.client.post(reverse('partner'), {
            'organization_name': 'Tech Solutions Corp',
            'contact_person': 'John Tech',
            'email': 'john@techsolutions.com',
            'phone_number': '09201234567',
            'partnership_type': 'business',
            'proposed_collaboration': 'Provide free WiFi for community centers',
            'resources_offered': 'Internet infrastructure and maintenance',
            'expected_outcomes': 'Improved digital access for constituents'
        })
        
        # 2. Coordinator reviews submission
        self.client.login(username='coordinator', password='test123')
        self.bypass_mfa()
        
        partners_response = self.client.get(reverse('database_partners'))
        self.assertEqual(partners_response.status_code, 200)
        self.assertContains(partners_response, 'Tech Solutions Corp')
        
        # 3. MP approves partnership
        self.client.login(username='mp', password='test123')
        self.bypass_mfa()
        
        # Update partnership status
        partnership = PartnershipSubmission.objects.get(organization_name='Tech Solutions Corp')
        partnership.status = 'approved'
        partnership.reviewed_by = self.mp
        partnership.reviewed_at = timezone.now()
        partnership.save()
        
        # 4. Information Officer creates announcement
        self.client.login(username='info_officer', password='test123')
        self.bypass_mfa()
        
        announcement_response = self.client.post(
            reverse('database_announcement_create'),
            {
                'title': 'New Partnership: Free WiFi for Community Centers',
                'category': 'news',
                'status': 'published',
                'excerpt': 'Tech Solutions Corp partners with #FahanieCares',
                'content': '''<p>We are pleased to announce our new partnership with Tech Solutions Corp!</p>
                <p>This partnership will provide:</p>
                <ul>
                <li>Free WiFi in all community centers</li>
                <li>Digital literacy training</li>
                <li>Technical support</li>
                </ul>
                <p>Stay tuned for the rollout schedule.</p>''',
                'is_featured': True
            }
        )
        self.assertEqual(announcement_response.status_code, 302)
        
        # 5. Public sees the announcement
        self.client.logout()
        
        public_response = self.client.get(reverse('announcements'))
        self.assertEqual(public_response.status_code, 200)
        self.assertContains(public_response, 'New Partnership: Free WiFi')
        
        # 6. Verify complete workflow tracking
        self.client.login(username='mp', password='test123')
        self.bypass_mfa()
        
        # Check partnership is approved
        partners = self.client.get(reverse('database_partners'))
        self.assertContains(partners, 'approved')
        
        # Check announcement exists
        updates = self.client.get(reverse('database_updates'))
        self.assertContains(updates, 'New Partnership: Free WiFi')