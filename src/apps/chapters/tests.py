from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Chapter, ChapterMembership, ChapterActivity
from .forms import MembershipApplicationForm

User = get_user_model()


class ChapterModelTest(TestCase):
    """Test Chapter model functionality."""
    
    def setUp(self):
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='coordinator'
        )
    
    def test_chapter_creation(self):
        """Test creating a chapter."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            province='Test Province',
            tier='municipal',
            coordinator=self.coordinator,
            status='active'
        )
        
        self.assertEqual(chapter.name, 'Test Chapter')
        self.assertEqual(chapter.slug, 'test-chapter')
        self.assertEqual(chapter.municipality, 'Test City')
        self.assertEqual(chapter.tier, 'municipal')
        self.assertEqual(chapter.status, 'active')
        self.assertEqual(chapter.coordinator, self.coordinator)
    
    def test_chapter_slug_generation(self):
        """Test automatic slug generation."""
        chapter = Chapter.objects.create(
            name='My Special Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        self.assertEqual(chapter.slug, 'my-special-chapter')
    
    def test_chapter_str_representation(self):
        """Test chapter string representation."""
        chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.coordinator
        )
        
        self.assertEqual(str(chapter), 'Test Chapter (Municipal/City Chapter)')
    
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


class ChapterMembershipModelTest(TestCase):
    """Test ChapterMembership model functionality."""
    
    def setUp(self):
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='coordinator'
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
    
    def test_membership_creation(self):
        """Test creating a membership."""
        membership = ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member,
            is_volunteer=True,
            volunteer_skills='Teaching',
            availability='Weekends'
        )
        
        self.assertEqual(membership.chapter, self.chapter)
        self.assertEqual(membership.user, self.member)
        self.assertTrue(membership.is_volunteer)
        self.assertEqual(membership.volunteer_skills, 'Teaching')
        self.assertEqual(membership.status, 'pending')  # default status
    
    def test_membership_unique_constraint(self):
        """Test that a user can only have one membership per chapter."""
        # Create first membership
        ChapterMembership.objects.create(
            chapter=self.chapter,
            user=self.member
        )
        
        # Try to create duplicate - should fail
        with self.assertRaises(Exception):  # Could be IntegrityError
            ChapterMembership.objects.create(
                chapter=self.chapter,
                user=self.member
            )


class ChapterViewsTest(TestCase):
    """Test Chapter views."""
    
    def setUp(self):
        self.client = Client()
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coord@test.com',
            password='Test@Pass123!',
            user_type='coordinator'
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
    
    def test_chapter_list_view(self):
        """Test chapter list view."""
        response = self.client.get(reverse('chapter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chapter')
    
    def test_chapter_detail_view(self):
        """Test chapter detail view."""
        response = self.client.get(
            reverse('chapter_detail', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chapter')
    
    def test_membership_application_requires_login(self):
        """Test that membership application requires login."""
        response = self.client.get(
            reverse('chapter_join', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_membership_application_authenticated(self):
        """Test membership application for authenticated user."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.get(
            reverse('chapter_join', args=[self.chapter.slug])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_membership_application_post(self):
        """Test submitting membership application."""
        self.client.login(username='member', password='Test@Pass123!')
        
        response = self.client.post(
            reverse('chapter_join', args=[self.chapter.slug]),
            {
                'is_volunteer': True,
                'volunteer_skills': 'Teaching',
                'availability': 'Weekends',
                'notes': 'Excited to join!'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check membership was created
        membership = ChapterMembership.objects.get(
            chapter=self.chapter,
            user=self.member
        )
        self.assertTrue(membership.is_volunteer)
        self.assertEqual(membership.volunteer_skills, 'Teaching')


class MembershipApplicationFormTest(TestCase):
    """Test MembershipApplicationForm."""
    
    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'is_volunteer': True,
            'volunteer_skills': 'Teaching, organizing events',
            'availability': 'Weekends',
            'notes': 'Excited to contribute!'
        }
        
        form = MembershipApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_without_volunteer_skills(self):
        """Test form without volunteer skills when volunteering."""
        form_data = {
            'is_volunteer': True,
            'availability': 'Weekends'
        }
        
        form = MembershipApplicationForm(data=form_data)
        # Form should still be valid - volunteer_skills is not required
