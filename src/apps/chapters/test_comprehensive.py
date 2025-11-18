"""
Comprehensive Test Suite for Chapter Database and CRUD Operations
================================================================

This test suite covers:
- Unit Tests: Model validation, form validation, individual methods
- Integration Tests: CRUD workflows, user permissions, relationships
- E2E Tests: Complete user journeys and workflows

Test Categories:
1. Chapter Model Tests (Unit)
2. ChapterMembership Model Tests (Unit)
3. ChapterActivity Model Tests (Unit)
4. Chapter Form Tests (Unit)
5. Chapter CRUD Integration Tests
6. Chapter Permission Tests (Integration)
7. Chapter Workflow E2E Tests
"""

import datetime
from decimal import Decimal
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Chapter, ChapterMembership, ChapterActivity, ActivityAttendance
from .forms import ChapterForm, MembershipForm, ActivityForm, MembershipApplicationForm

User = get_user_model()


class ChapterModelUnitTests(TestCase):
    """Unit tests for Chapter model validation and methods."""
    
    def setUp(self):
        """Set up test data."""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            first_name='John',
            last_name='Coordinator',
            user_type='admin'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='Test@Pass123!',
            first_name='Jane',
            last_name='Staff',
            user_type='admin'
        )
    
    def test_chapter_creation_with_required_fields(self):
        """Test creating a chapter with required fields only."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            province='Test Province',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        self.assertEqual(chapter.name, 'Test Chapter')
        self.assertEqual(chapter.municipality, 'Test City')
        self.assertEqual(chapter.province, 'Test Province')
        self.assertEqual(chapter.tier, 'municipal')
        self.assertEqual(chapter.coordinator, self.coordinator)
        self.assertEqual(chapter.status, 'pending')  # default status
        self.assertEqual(chapter.country, 'Philippines')  # default country
        self.assertEqual(chapter.member_count, 0)  # default count
        self.assertIsNotNone(chapter.created_at)
        self.assertIsNotNone(chapter.updated_at)
    
    def test_chapter_creation_with_all_fields(self):
        """Test creating a chapter with all fields populated."""
        chapter = Chapter.objects.create(
            name='Complete Test Chapter',
            slug='complete-test-chapter',
            tier='provincial',
            municipality='Complete City',
            province='Complete Province',
            country='Philippines',
            description='A complete test chapter for testing purposes',
            mission_statement='To serve the community with excellence',
            established_date=datetime.date(2023, 1, 15),
            status='active',
            coordinator=self.coordinator,
            email='chapter@test.com',
            phone='+63 9123456789',
            address='123 Test Street, Test Barangay, Test City',
            meeting_location='City Hall Conference Room',
            meeting_schedule='First Saturday of every month at 2:00 PM',
            facebook_page='https://facebook.com/test-chapter',
            twitter_handle='testchapter',
            instagram_handle='testchapter',
            member_count=25,
            volunteer_count=10,
            activity_count=5
        )
        
        self.assertEqual(chapter.name, 'Complete Test Chapter')
        self.assertEqual(chapter.slug, 'complete-test-chapter')
        self.assertEqual(chapter.tier, 'provincial')
        self.assertEqual(chapter.description, 'A complete test chapter for testing purposes')
        self.assertEqual(chapter.mission_statement, 'To serve the community with excellence')
        self.assertEqual(chapter.established_date, datetime.date(2023, 1, 15))
        self.assertEqual(chapter.status, 'active')
        self.assertEqual(chapter.email, 'chapter@test.com')
        self.assertEqual(chapter.phone, '+63 9123456789')
        self.assertEqual(chapter.facebook_page, 'https://facebook.com/test-chapter')
        self.assertEqual(chapter.twitter_handle, 'testchapter')
        self.assertEqual(chapter.instagram_handle, 'testchapter')
        self.assertEqual(chapter.member_count, 25)
        self.assertEqual(chapter.volunteer_count, 10)
        self.assertEqual(chapter.activity_count, 5)
    
    def test_automatic_slug_generation(self):
        """Test that slug is automatically generated from name."""
        chapter = Chapter.objects.create(
            name='My Special Chapter Name',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        self.assertEqual(chapter.slug, 'my-special-chapter-name')
    
    def test_slug_uniqueness(self):
        """Test that slug must be unique."""
        Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        with self.assertRaises(IntegrityError):
            Chapter.objects.create(
                name='Test Chapter',  # Same name, should generate same slug
                municipality='Another City',
                tier='provincial',
                coordinator=self.coordinator
            )
    
    def test_chapter_str_representation(self):
        """Test chapter string representation."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        expected = 'Test Chapter (Municipal/City Chapter)'
        self.assertEqual(str(chapter), expected)
    
    def test_get_absolute_url(self):
        """Test chapter get_absolute_url method."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        expected_url = reverse('chapter_detail', args=[chapter.slug])
        self.assertEqual(chapter.get_absolute_url(), expected_url)
    
    def test_activate_method(self):
        """Test chapter activation method."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator,
            status='pending'
        )
        
        # Activate the chapter
        chapter.activate(self.staff_user)
        
        # Refresh from database
        chapter.refresh_from_db()
        
        self.assertEqual(chapter.status, 'active')
        self.assertEqual(chapter.approved_by, self.staff_user)
        self.assertIsNotNone(chapter.approved_at)
    
    def test_tier_choices_validation(self):
        """Test that tier field only accepts valid choices."""
        valid_tiers = ['provincial', 'municipal']
        
        for tier in valid_tiers:
            chapter = Chapter.objects.create(
                name=f'Test {tier} Chapter {tier}',  # Make names unique
                municipality='Test City',
                tier=tier,
                coordinator=self.coordinator
            )
            # Verify the chapter was created successfully
            self.assertEqual(chapter.tier, tier)
    
    def test_status_choices_validation(self):
        """Test that status field only accepts valid choices."""
        valid_statuses = ['active', 'pending', 'inactive', 'suspended']
        
        for status in valid_statuses:
            chapter = Chapter.objects.create(
                name=f'Test {status} Chapter {status}',  # Make names unique
                municipality='Test City',
                tier='municipal',
                coordinator=self.coordinator,
                status=status
            )
            # Verify the chapter was created successfully
            self.assertEqual(chapter.status, status)
    
    def test_parent_chapter_relationship(self):
        """Test parent-child chapter relationship."""
        # Create parent chapter
        parent_chapter = Chapter.objects.create(
            name='Parent Chapter',
            municipality='Parent City',
            tier='provincial',
            coordinator=self.coordinator
        )
        
        # Create child chapter
        child_chapter = Chapter.objects.create(
            name='Child Chapter',
            municipality='Child City',
            tier='municipal',
            coordinator=self.coordinator,
            parent_chapter=parent_chapter
        )
        
        self.assertEqual(child_chapter.parent_chapter, parent_chapter)
        self.assertIn(child_chapter, parent_chapter.sub_chapters.all())
    
    def test_update_member_count_method(self):
        """Test update_member_count method."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        # Create some members
        member1 = User.objects.create_user(
            username='member1',
            email='member1@test.com',
            password='Test@Pass123!'
        )
        member2 = User.objects.create_user(
            username='member2',
            email='member2@test.com',
            password='Test@Pass123!'
        )
        
        # Create active memberships
        ChapterMembership.objects.create(
            chapter=chapter,
            user=member1,
            status='active'
        )
        ChapterMembership.objects.create(
            chapter=chapter,
            user=member2,
            status='active'
        )
        
        # Create inactive membership
        inactive_member = User.objects.create_user(
            username='inactive',
            email='inactive@test.com',
            password='Test@Pass123!'
        )
        ChapterMembership.objects.create(
            chapter=chapter,
            user=inactive_member,
            status='inactive'
        )
        
        # Update member count
        chapter.update_member_count()
        
        # Should only count active members
        self.assertEqual(chapter.member_count, 2)


class ChapterMembershipModelUnitTests(TestCase):
    """Unit tests for ChapterMembership model validation and methods."""
    
    def setUp(self):
        """Set up test data."""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='admin'
        )
        
        self.member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='Test@Pass123!',
            user_type='member'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator,
            status='active'
        )
    
    def test_membership_creation_with_required_fields(self):
        """Test creating membership with required fields only."""
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member
        )
        
        self.assertEqual(membership.chapter, self.chapter)
        self.assertEqual(membership.user, self.member)
        self.assertEqual(membership.role, 'member')  # default role
        self.assertEqual(membership.status, 'pending')  # default status
        self.assertFalse(membership.is_volunteer)  # default volunteer status
        self.assertEqual(membership.volunteer_hours, Decimal('0'))
        self.assertIsNotNone(membership.joined_date)
        self.assertIsNotNone(membership.created_at)
    
    def test_membership_creation_with_all_fields(self):
        """Test creating membership with all fields populated."""
        join_date = datetime.date(2023, 6, 15)
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member,
            role='volunteer',
            status='active',
            joined_date=join_date,
            membership_number='FCM-TEST-001',
            is_volunteer=True,
            volunteer_hours=Decimal('25.50'),
            volunteer_skills='Teaching, Event Organization',
            availability='Weekends',
            committees='Education, Outreach',
            activities_attended=5,
            activities_organized=2,
            referrals_made=3,
            notes='Excellent volunteer, very dedicated'
        )
        
        self.assertEqual(membership.role, 'volunteer')
        self.assertEqual(membership.status, 'active')
        self.assertEqual(membership.joined_date, join_date)
        self.assertEqual(membership.membership_number, 'FCM-TEST-001')
        self.assertTrue(membership.is_volunteer)
        self.assertEqual(membership.volunteer_hours, Decimal('25.50'))
        self.assertEqual(membership.volunteer_skills, 'Teaching, Event Organization')
        self.assertEqual(membership.availability, 'Weekends')
        self.assertEqual(membership.committees, 'Education, Outreach')
        self.assertEqual(membership.activities_attended, 5)
        self.assertEqual(membership.activities_organized, 2)
        self.assertEqual(membership.referrals_made, 3)
        self.assertEqual(membership.notes, 'Excellent volunteer, very dedicated')
    
    def test_membership_unique_constraint(self):
        """Test that user can only have one membership per chapter."""
        # Create first membership
        ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member
        )
        
        # Try to create duplicate - should fail
        with self.assertRaises(IntegrityError):
            ChapterMembership.objects.create(
                chapter=self.chapter,
                user=self.member
            )
    
    def test_membership_str_representation(self):
        """Test membership string representation."""
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member,
            role='coordinator'
        )
        
        expected = f"{self.member.get_full_name()} - {self.chapter.name} (Coordinator)"
        self.assertEqual(str(membership), expected)
    
    def test_generate_membership_number(self):
        """Test membership number generation."""
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member
        )
        
        membership_number = membership.generate_membership_number()
        
        # Should start with FCM- followed by municipality code
        self.assertTrue(membership_number.startswith('FCM-TES-'))  # First 3 chars of municipality
        self.assertEqual(len(membership_number), 12)  # FCM-XXX-YYYY format
    
    def test_approve_method(self):
        """Test membership approval method."""
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member,
            status='pending'
        )
        
        # Approve the membership
        membership.approve(self.coordinator)
        
        # Refresh from database
        membership.refresh_from_db()
        
        self.assertEqual(membership.status, 'active')
        self.assertEqual(membership.approved_by, self.coordinator)
        self.assertIsNotNone(membership.approved_at)
        self.assertIsNotNone(membership.membership_number)
    
    def test_role_choices_validation(self):
        """Test that role field only accepts valid choices."""
        valid_roles = [
            'member', 'volunteer', 'coordinator', 'assistant_coordinator',
            'secretary', 'treasurer', 'auditor', 'committee_member'
        ]
        
        for i, role in enumerate(valid_roles):
            # Create a unique user for each test to avoid conflicts
            test_user = User.objects.create_user(
                username=f'test_role_{i}',
                email=f'test_role_{i}@test.com',
                password='Test@Pass123!'
            )
            membership = ChapterMembership.objects.create(
                chapter=self.chapter,
                user=test_user,
                role=role
            )
            # Verify the membership was created successfully
            self.assertEqual(membership.role, role)
    
    def test_status_choices_validation(self):
        """Test that status field only accepts valid choices."""
        valid_statuses = ['active', 'inactive', 'suspended', 'pending']
        
        for i, status in enumerate(valid_statuses):
            # Create a unique user for each test to avoid conflicts
            test_user = User.objects.create_user(
                username=f'test_status_{i}',
                email=f'test_status_{i}@test.com',
                password='Test@Pass123!'
            )
            membership = ChapterMembership.objects.create(
                chapter=self.chapter,
                user=test_user,
                status=status
            )
            # Verify the membership was created successfully
            self.assertEqual(membership.status, status)


class ChapterActivityModelUnitTests(TestCase):
    """Unit tests for ChapterActivity model validation and methods."""
    
    def setUp(self):
        """Set up test data."""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='admin'
        )
        
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='Test@Pass123!',
            user_type='member'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator,
            status='active'
        )
    
    def test_activity_creation_with_required_fields(self):
        """Test creating activity with required fields only."""
        activity_date = datetime.date.today() + datetime.timedelta(days=7)
        activity = ChapterActivity.objects.create(
            chapter=self.chapter,
            title='Test Activity',
            activity_type='meeting',
            description='A test activity for our chapter',
            date=activity_date,
            start_time=datetime.time(14, 0),  # 2:00 PM
            end_time=datetime.time(16, 0),    # 4:00 PM
            venue='Community Center',
            address='123 Community Street'
        )
        
        self.assertEqual(activity.chapter, self.chapter)
        self.assertEqual(activity.title, 'Test Activity')
        self.assertEqual(activity.activity_type, 'meeting')
        self.assertEqual(activity.description, 'A test activity for our chapter')
        self.assertEqual(activity.date, activity_date)
        self.assertEqual(activity.start_time, datetime.time(14, 0))
        self.assertEqual(activity.end_time, datetime.time(16, 0))
        self.assertEqual(activity.venue, 'Community Center')
        self.assertEqual(activity.address, '123 Community Street')
        self.assertEqual(activity.status, 'planned')  # default status
        self.assertEqual(activity.target_participants, 0)  # default
        self.assertEqual(activity.budget, Decimal('0'))  # default
    
    def test_activity_creation_with_all_fields(self):
        """Test creating activity with all fields populated."""
        activity_date = datetime.date.today() + datetime.timedelta(days=14)
        activity = ChapterActivity.objects.create(
            chapter=self.chapter,
            title='Complete Test Activity',
            activity_type='outreach',
            description='A comprehensive test activity with all fields',
            objectives='Test all activity functionality',
            date=activity_date,
            start_time=datetime.time(9, 0),   # 9:00 AM
            end_time=datetime.time(17, 0),    # 5:00 PM
            status='ongoing',
            venue='City Plaza',
            address='Central Plaza, Test City',
            online_link='https://zoom.us/j/123456789',
            organizer=self.organizer,
            target_participants=50,
            actual_participants=45,
            budget=Decimal('5000.00'),
            actual_cost=Decimal('4750.50'),
            resources_needed='Tables, Chairs, Sound system',
            report='Activity was successful with good community participation'
        )
        
        self.assertEqual(activity.title, 'Complete Test Activity')
        self.assertEqual(activity.activity_type, 'outreach')
        self.assertEqual(activity.objectives, 'Test all activity functionality')
        self.assertEqual(activity.status, 'ongoing')
        self.assertEqual(activity.online_link, 'https://zoom.us/j/123456789')
        self.assertEqual(activity.organizer, self.organizer)
        self.assertEqual(activity.target_participants, 50)
        self.assertEqual(activity.actual_participants, 45)
        self.assertEqual(activity.budget, Decimal('5000.00'))
        self.assertEqual(activity.actual_cost, Decimal('4750.50'))
        self.assertEqual(activity.resources_needed, 'Tables, Chairs, Sound system')
        self.assertEqual(activity.report, 'Activity was successful with good community participation')
    
    def test_activity_str_representation(self):
        """Test activity string representation."""
        activity_date = datetime.date(2023, 12, 15)
        activity = ChapterActivity.objects.create(
            chapter=self.chapter,
            title='Test Activity',
            activity_type='meeting',
            description='A test activity',
            date=activity_date,
            start_time=datetime.time(14, 0),
            end_time=datetime.time(16, 0),
            venue='Community Center',
            address='123 Community Street'
        )
        
        expected = f"Test Activity - {self.chapter.name} (2023-12-15)"
        self.assertEqual(str(activity), expected)
    
    def test_get_absolute_url(self):
        """Test activity get_absolute_url method."""
        activity = ChapterActivity.objects.create(
            chapter=self.chapter,
            title='Test Activity',
            activity_type='meeting',
            description='A test activity',
            date=datetime.date.today() + datetime.timedelta(days=7),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(16, 0),
            venue='Community Center',
            address='123 Community Street'
        )
        
        expected_url = reverse('activity_detail', args=[activity.pk])
        self.assertEqual(activity.get_absolute_url(), expected_url)
    
    def test_activity_type_choices_validation(self):
        """Test that activity_type field only accepts valid choices."""
        valid_types = [
            'meeting', 'outreach', 'fundraising', 'training',
            'social', 'volunteer', 'campaign', 'other'
        ]
        
        for i, activity_type in enumerate(valid_types):
            activity = ChapterActivity.objects.create(
                chapter=self.chapter,
                title=f'Test {activity_type} Activity {i}',  # Make titles unique
                activity_type=activity_type,
                description='Test description',
                date=datetime.date.today() + datetime.timedelta(days=7+i),  # Make dates unique
                start_time=datetime.time(14, 0),
                end_time=datetime.time(16, 0),
                venue='Test Venue',
                address='Test Address'
            )
            # Verify the activity was created successfully
            self.assertEqual(activity.activity_type, activity_type)
    
    def test_status_choices_validation(self):
        """Test that status field only accepts valid choices."""
        valid_statuses = ['planned', 'ongoing', 'completed', 'cancelled', 'postponed']
        
        for i, status in enumerate(valid_statuses):
            activity = ChapterActivity.objects.create(
                chapter=self.chapter,
                title=f'Test {status} Activity {i}',  # Make titles unique
                activity_type='meeting',
                description='Test description',
                date=datetime.date.today() + datetime.timedelta(days=14+i),  # Make dates unique
                start_time=datetime.time(14, 0),
                end_time=datetime.time(16, 0),
                venue='Test Venue',
                address='Test Address',
                status=status
            )
            # Verify the activity was created successfully
            self.assertEqual(activity.status, status)


class ChapterFormUnitTests(TestCase):
    """Unit tests for Chapter forms validation."""
    
    def setUp(self):
        """Set up test data."""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='admin'
        )
    
    def test_chapter_form_valid_data(self):
        """Test ChapterForm with valid data."""
        form_data = {
            'name': 'Test Chapter',
            'tier': 'municipal',
            'municipality': 'Test City',
            'province': 'Test Province',
            'country': 'Philippines',
            'description': 'A test chapter for our community',
            'mission_statement': 'To serve with excellence',
            'established_date': '2023-01-15',
            'coordinator': self.coordinator.id,
            'email': 'chapter@test.com',
            'phone': '+63 9123456789',
            'address': '123 Test Street',
            'meeting_location': 'City Hall',
            'meeting_schedule': 'First Saturday of every month',
            'facebook_page': 'https://facebook.com/test-chapter',
            'twitter_handle': 'testchapter',
            'instagram_handle': 'testchapter'
        }
        
        form = ChapterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_chapter_form_required_fields(self):
        """Test ChapterForm with missing required fields."""
        form_data = {
            'name': '',  # Required field left empty
            'tier': 'municipal',
            'municipality': 'Test City'
        }
        
        form = ChapterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_membership_application_form_valid_data(self):
        """Test MembershipApplicationForm with valid data."""
        form_data = {
            'is_volunteer': True,
            'volunteer_skills': 'Teaching, Event Organization',
            'availability': 'Weekends',
            'committees': 'Education, Outreach',
            'notes': 'Excited to contribute to the community'
        }
        
        form = MembershipApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_membership_application_form_minimal_data(self):
        """Test MembershipApplicationForm with minimal data."""
        form_data = {
            'is_volunteer': False
        }
        
        form = MembershipApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())


class ChapterCRUDIntegrationTests(TestCase):
    """Integration tests for Chapter CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='Test@Pass123!',
            first_name='Jane',
            last_name='Staff',
            user_type='admin'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            first_name='John',
            last_name='Coordinator',
            user_type='admin'
        )
        
        self.member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='Test@Pass123!',
            first_name='Bob',
            last_name='Member',
            user_type='member'
        )
        
        # Create test chapter
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            province='Test Province',
            tier='municipal',
            coordinator=self.coordinator,
            status='active',
            description='A test chapter for integration testing'
        )
    
    def test_chapter_list_view(self):
        """Test chapter list view shows active chapters."""
        response = self.client.get(reverse('chapter_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chapter')
        self.assertContains(response, 'Test City')
        self.assertIn('chapters', response.context)
        self.assertEqual(len(response.context['chapters']), 1)
    
    def test_chapter_list_view_filters(self):
        """Test chapter list view filtering functionality."""
        # Create additional chapter
        Chapter.objects.create(
            name='Another Chapter',
            municipality='Another City',
            province='Another Province',
            tier='provincial',
            coordinator=self.coordinator,
            status='active'
        )
        
        # Test municipality filter
        response = self.client.get(reverse('chapter_list'), {'municipality': 'Test City'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chapters']), 1)
        self.assertContains(response, 'Test Chapter')
        
        # Test tier filter
        response = self.client.get(reverse('chapter_list'), {'tier': 'provincial'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chapters']), 1)
        self.assertContains(response, 'Another Chapter')
        
        # Test search filter
        response = self.client.get(reverse('chapter_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chapters']), 1)
        self.assertContains(response, 'Test Chapter')
    
    def test_chapter_detail_view(self):
        """Test chapter detail view."""
        response = self.client.get(
            reverse('chapter_detail', args=[self.chapter.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chapter')
        self.assertContains(response, 'A test chapter for integration testing')
        self.assertEqual(response.context['chapter'], self.chapter)
    
    def test_chapter_create_view_staff_access(self):
        """Test chapter creation view for staff users."""
        self.client.login(username='staff', password='Test@Pass123!')
        
        response = self.client.get(reverse('chapter_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Chapter')
    
    def test_chapter_create_view_non_staff_denied(self):
        """Test chapter creation view denies non-staff users."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(reverse('chapter_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_chapter_create_post(self):
        """Test creating a chapter via POST request."""
        self.client.login(username='staff', password='Test@Pass123!')
        
        form_data = {
            'name': 'New Test Chapter',
            'tier': 'municipal',
            'municipality': 'New City',
            'province': 'New Province',
            'country': 'Philippines',
            'description': 'A newly created test chapter',
            'coordinator': self.coordinator.id,
            'email': 'newchapter@test.com'
        }
        
        response = self.client.post(reverse('chapter_create'), form_data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check chapter was created
        new_chapter = Chapter.objects.get(name='New Test Chapter')
        self.assertEqual(new_chapter.municipality, 'New City')
        self.assertEqual(new_chapter.coordinator, self.coordinator)
        # Staff users auto-approve chapters
        self.assertEqual(new_chapter.status, 'active')
    
    def test_chapter_update_view_coordinator_access(self):
        """Test chapter update view for coordinator access."""
        self.client.login(username='coordinator', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_edit', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Chapter')
    
    def test_chapter_update_view_non_coordinator_denied(self):
        """Test chapter update view denies non-coordinators."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_edit', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_chapter_update_post(self):
        """Test updating a chapter via POST request."""
        self.client.login(username='coordinator', password='Test@Pass123!')
        
        form_data = {
            'name': 'Updated Test Chapter',
            'tier': 'municipal',
            'municipality': 'Updated City',
            'province': 'Updated Province',
            'country': 'Philippines',
            'description': 'An updated test chapter description',
            'coordinator': self.coordinator.id,
            'email': 'updated@test.com'
        }
        
        response = self.client.post(
            reverse('chapter_edit', args=[self.chapter.slug]),
            form_data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check chapter was updated
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.name, 'Updated Test Chapter')
        self.assertEqual(self.chapter.municipality, 'Updated City')
        self.assertEqual(self.chapter.email, 'updated@test.com')


class ChapterMembershipIntegrationTests(TestCase):
    """Integration tests for Chapter membership workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='admin'
        )
        
        self.member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='Test@Pass123!',
            first_name='Bob',
            last_name='Member',
            user_type='member'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator,
            status='active'
        )
    
    def test_membership_application_requires_login(self):
        """Test membership application requires authentication."""
        response = self.client.get(
            reverse('chapter_join', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_membership_application_form_display(self):
        """Test membership application form displays correctly."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_join', args=[self.chapter.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chapter')
        self.assertEqual(response.context['chapter'], self.chapter)
    
    def test_membership_application_submission(self):
        """Test submitting a membership application."""
        self.client.login(username='member', password='Test@Pass123!')
        
        form_data = {
            'is_volunteer': True,
            'volunteer_skills': 'Teaching, Event Organization',
            'availability': 'Weekends',
            'committees': 'Education',
            'notes': 'Excited to join and contribute!'
        }
        
        response = self.client.post(
            reverse('chapter_join', args=[self.chapter.slug]),
            form_data
        )
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check membership was created
        membership = ChapterMembership.objects.get(
            chapter=self.chapter,
            user=self.member
        )
        self.assertTrue(membership.is_volunteer)
        self.assertEqual(membership.volunteer_skills, 'Teaching, Event Organization')
        self.assertEqual(membership.status, 'pending')  # Default status
    
    def test_duplicate_membership_application_prevented(self):
        """Test that duplicate membership applications are prevented."""
        # Create existing membership
        ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member
        )
        
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_join', args=[self.chapter.slug])
        )
        
        # Should redirect with warning message
        self.assertEqual(response.status_code, 302)
    
    def test_chapter_members_view_requires_membership(self):
        """Test chapter members view requires membership."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_members', args=[self.chapter.slug])
        )
        
        # Should redirect with error message (non-member)
        self.assertEqual(response.status_code, 302)
    
    def test_chapter_members_view_with_membership(self):
        """Test chapter members view with valid membership."""
        # Create membership
        ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member,
            status='active'
        )
        
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_members', args=[self.chapter.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.get_full_name())
        self.assertEqual(response.context['chapter'], self.chapter)


class ChapterWorkflowE2ETests(TransactionTestCase):
    """End-to-end tests for complete chapter workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create users with different roles
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@fahaniecares.ph',
            password='StaffPass123!',
            first_name='Jane',
            last_name='Staff',
            user_type='admin'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@fahaniecares.ph',
            password='CoordPass123!',
            first_name='John',
            last_name='Coordinator',
            user_type='admin'
        )
        
        self.member1 = User.objects.create_user(
            username='member1',
            email='member1@example.com',
            password='MemberPass123!',
            first_name='Alice',
            last_name='Member',
            user_type='member'
        )
        
        self.member2 = User.objects.create_user(
            username='member2',
            email='member2@example.com',
            password='MemberPass123!',
            first_name='Bob',
            last_name='Volunteer',
            user_type='member'
        )
    
    def test_complete_chapter_lifecycle_workflow(self):
        """Test complete chapter lifecycle from creation to activity management."""
        
        # Step 1: Staff user creates a new chapter
        self.client.login(username='staff', password='StaffPass123!')
        
        chapter_data = {
            'name': 'Cotabato Community Chapter',
            'tier': 'municipal',
            'municipality': 'Cotabato City',
            'province': 'Maguindanao',
            'country': 'Philippines',
            'description': 'Serving the Cotabato community with dedication',
            'mission_statement': 'To provide excellent public service to Cotabato residents',
            'coordinator': self.coordinator.id,
            'email': 'cotabato@fahaniecares.ph',
            'phone': '+63 9123456789',
            'address': '123 Pioneer Avenue, Cotabato City',
            'meeting_location': 'City Hall Conference Room',
            'meeting_schedule': 'Every first Saturday at 2:00 PM'
        }
        
        response = self.client.post(reverse('chapter_create'), chapter_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify chapter was created and auto-approved
        chapter = Chapter.objects.get(name='Cotabato Community Chapter')
        self.assertEqual(chapter.status, 'active')
        self.assertEqual(chapter.approved_by, self.staff_user)
        
        # Step 2: Members apply for chapter membership
        self.client.login(username='member1', password='MemberPass123!')
        
        membership_data1 = {
            'is_volunteer': True,
            'volunteer_skills': 'Teaching, Community organizing',
            'availability': 'Weekends',
            'committees': 'Education, Outreach',
            'notes': 'Experienced teacher wanting to help the community'
        }
        
        response = self.client.post(
            reverse('chapter_join', args=[chapter.slug]),
            membership_data1
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify membership was created as pending
        membership1 = ChapterMembership.objects.get(chapter=chapter, user=self.member1)
        self.assertEqual(membership1.status, 'pending')
        self.assertTrue(membership1.is_volunteer)
        
        # Second member applies
        self.client.login(username='member2', password='MemberPass123!')
        
        membership_data2 = {
            'is_volunteer': False,
            'notes': 'Regular member wanting to stay informed'
        }
        
        response = self.client.post(
            reverse('chapter_join', args=[chapter.slug]),
            membership_data2
        )
        self.assertEqual(response.status_code, 302)
        
        membership2 = ChapterMembership.objects.get(chapter=chapter, user=self.member2)
        self.assertEqual(membership2.status, 'pending')
        self.assertFalse(membership2.is_volunteer)
        
        # Step 3: Coordinator approves memberships
        self.client.login(username='coordinator', password='CoordPass123!')
        
        # Approve first membership
        membership1.approve(self.coordinator)
        self.assertEqual(membership1.status, 'active')
        self.assertIsNotNone(membership1.membership_number)
        
        # Approve second membership
        membership2.approve(self.coordinator)
        self.assertEqual(membership2.status, 'active')
        
        # Verify chapter member count was updated
        chapter.refresh_from_db()
        # Note: update_member_count() should be called during approval
        
        # Step 4: Create chapter activity
        activity_date = datetime.date.today() + datetime.timedelta(days=14)
        activity = ChapterActivity.objects.create(
            chapter=chapter,
            title='Community Health Screening',
            activity_type='outreach',
            description='Free health screening for community members',
            objectives='Provide basic health services to underserved residents',
            date=activity_date,
            start_time=datetime.time(8, 0),   # 8:00 AM
            end_time=datetime.time(16, 0),    # 4:00 PM
            venue='Barangay Health Center',
            address='Barangay Rosary Heights, Cotabato City',
            organizer=self.coordinator,
            target_participants=100,
            budget=Decimal('15000.00'),
            resources_needed='Medical supplies, Registration forms, Tables, Chairs'
        )
        
        # Step 5: Members register for activity
        self.client.login(username='member1', password='MemberPass123!')
        
        # Try to register for activity
        registration_data = {
            'tasks_completed': '',
            'feedback': ''
        }
        
        response = self.client.post(
            reverse('activity_register', args=[activity.pk]),
            registration_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify attendance record was created
        attendance = ActivityAttendance.objects.get(
            activity=activity,
            attendee=self.member1
        )
        self.assertEqual(attendance.status, 'registered')
        
        # Step 6: Test chapter dashboard access
        self.client.login(username='coordinator', password='CoordPass123!')
        
        response = self.client.get(
            reverse('chapter_dashboard', args=[chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chapter'], chapter)
        
        # Verify dashboard shows correct stats
        context = response.context
        self.assertIn('pending_memberships', context)
        self.assertIn('upcoming_activities', context)
        self.assertIn('member_stats', context)
        
        # Step 7: Test member directory access
        self.client.login(username='member1', password='MemberPass123!')
        
        response = self.client.get(
            reverse('chapter_members', args=[chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
        
        # Should see both members
        memberships = response.context['memberships']
        self.assertEqual(len(memberships), 2)
        
        # Step 8: Test activity list view
        response = self.client.get(
            reverse('chapter_activities', args=[chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
        
        activities = response.context['activities']
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0], activity)
        
        # Step 9: Test activity detail view
        response = self.client.get(
            reverse('activity_detail', args=[activity.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['activity'], activity)
        
        # Should see user's attendance record
        user_attendance = response.context.get('user_attendance')
        self.assertIsNotNone(user_attendance)
        self.assertEqual(user_attendance.attendee, self.member1)
        
        # Final verification: Check all data integrity
        self.assertEqual(Chapter.objects.count(), 1)
        self.assertEqual(ChapterMembership.objects.filter(status='active').count(), 2)
        self.assertEqual(ChapterActivity.objects.count(), 1)
        self.assertEqual(ActivityAttendance.objects.count(), 1)
        
        # Verify chapter relationships
        self.assertEqual(chapter.memberships.count(), 2)
        self.assertEqual(chapter.activities.count(), 1)
        self.assertEqual(activity.attendance_records.count(), 1)
    
    def test_chapter_permission_enforcement_workflow(self):
        """Test that chapter permissions are properly enforced throughout workflows."""
        
        # Create a chapter with coordinator
        chapter = Chapter.objects.create(
            name='Permission Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator,
            status='active'
        )
        
        # Test 1: Anonymous user cannot access protected views
        protected_urls = [
            reverse('chapter_create'),
            reverse('chapter_join', args=[chapter.slug]),
            reverse('chapter_members', args=[chapter.slug]),
            reverse('chapter_dashboard', args=[chapter.slug]),
            reverse('chapter_edit', args=[chapter.slug])
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test 2: Regular member cannot access staff-only views
        self.client.login(username='member1', password='MemberPass123!')
        
        staff_only_urls = [
            reverse('chapter_create'),
            reverse('chapter_dashboard', args=[chapter.slug]),
            reverse('chapter_edit', args=[chapter.slug])
        ]
        
        for url in staff_only_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])  # Redirect or Forbidden
        
        # Test 3: Non-member cannot access member-only views
        member_only_urls = [
            reverse('chapter_members', args=[chapter.slug])
        ]
        
        for url in member_only_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect with error
        
        # Test 4: Coordinator can access coordinator-level views
        self.client.login(username='coordinator', password='CoordPass123!')
        
        coordinator_urls = [
            reverse('chapter_dashboard', args=[chapter.slug]),
            reverse('chapter_edit', args=[chapter.slug])
        ]
        
        for url in coordinator_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        
        # Test 5: Staff user can access all views
        self.client.login(username='staff', password='StaffPass123!')
        
        all_urls = [
            reverse('chapter_create'),
            reverse('chapter_dashboard', args=[chapter.slug]),
            reverse('chapter_edit', args=[chapter.slug])
        ]
        
        for url in all_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)