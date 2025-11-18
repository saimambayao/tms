from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from .models import Announcement
import tempfile
from PIL import Image
import io

User = get_user_model()


class DatabaseViewsAccessTestCase(TestCase):
    """Test access control for all database views."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@test.com',
            password='testpass123'
        )
        
        self.mp_user = User.objects.create_user(
            username='mp_user',
            email='mp@test.com',
            password='testpass123',
            user_type='mp'
        )
        
        self.chief_of_staff = User.objects.create_user(
            username='chief_of_staff',
            email='chief@test.com',
            password='testpass123',
            user_type='chief_of_staff'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123',
            user_type='coordinator'
        )
        
        self.info_officer = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='testpass123',
            user_type='information_officer'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com',
            password='testpass123',
            user_type='member'
        )
    
    def test_database_registrants_access(self):
        """Test access control for Database of Registrants."""
        url = reverse('database_registrants')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')
        
        # Test unauthorized user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test authorized user access
        authorized_users = [
            self.superuser, self.mp_user, self.chief_of_staff,
            self.admin_user, self.coordinator
        ]
        
        for user in authorized_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'constituents/database_registrants.html')
    
    def test_database_partners_access(self):
        """Test access control for Database of Partners."""
        url = reverse('database_partners')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')
        
        # Test unauthorized user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test authorized user access
        authorized_users = [
            self.superuser, self.mp_user, self.chief_of_staff,
            self.admin_user, self.coordinator
        ]
        
        for user in authorized_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/database_partners.html')
    
    def test_database_donors_access(self):
        """Test access control for Database of Donors."""
        url = reverse('database_donors')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')
        
        # Test unauthorized user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test authorized user access
        authorized_users = [
            self.superuser, self.mp_user, self.chief_of_staff,
            self.admin_user, self.coordinator
        ]
        
        for user in authorized_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/database_donors.html')
    
    def test_database_updates_access(self):
        """Test access control for Database of Updates."""
        url = reverse('database_updates')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')
        
        # Test unauthorized user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        
        # Test authorized user access (includes information officer)
        authorized_users = [
            self.superuser, self.mp_user, self.chief_of_staff,
            self.admin_user, self.coordinator, self.info_officer
        ]
        
        for user in authorized_users:
            self.client.login(username=user.username, password='testpass123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/database_updates.html')


class AnnouncementModelTestCase(TestCase):
    """Test the Announcement model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_announcement_creation(self):
        """Test creating an announcement."""
        announcement = Announcement.objects.create(
            title='Test Announcement',
            excerpt='This is a test excerpt',
            content='<p>This is test content</p>',
            category='news',
            status='draft',
            created_by=self.user
        )
        
        self.assertEqual(announcement.title, 'Test Announcement')
        self.assertEqual(announcement.slug, 'test-announcement')
        self.assertEqual(announcement.category, 'news')
        self.assertEqual(announcement.status, 'draft')
        self.assertIsNone(announcement.published_date)
        self.assertFalse(announcement.is_featured)
    
    def test_announcement_slug_generation(self):
        """Test automatic slug generation."""
        announcement = Announcement.objects.create(
            title='Test Announcement with Spaces',
            excerpt='Test excerpt',
            content='Test content',
            created_by=self.user
        )
        
        self.assertEqual(announcement.slug, 'test-announcement-with-spaces')
    
    def test_announcement_get_absolute_url(self):
        """Test the get_absolute_url method."""
        announcement = Announcement.objects.create(
            title='Test Announcement',
            excerpt='Test excerpt',
            content='Test content',
            created_by=self.user
        )
        
        self.assertEqual(
            announcement.get_absolute_url(),
            reverse('announcement_detail', kwargs={'slug': announcement.slug})
        )
    
    def test_announcement_category_color(self):
        """Test the get_category_color method."""
        announcement = Announcement.objects.create(
            title='Test',
            excerpt='Test',
            content='Test',
            created_by=self.user
        )
        
        # Test different categories
        category_colors = {
            'news': 'info',
            'event': 'warning',
            'parliament': 'success',
            'program': 'primary',
            'update': 'secondary',
        }
        
        for category, color in category_colors.items():
            announcement.category = category
            self.assertEqual(announcement.get_category_color(), color)


class DatabaseUpdatesViewTestCase(TestCase):
    """Test the Database Updates list view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='testpass123',
            user_type='information_officer'
        )
        
        # Create test announcements
        for i in range(25):
            Announcement.objects.create(
                title=f'Announcement {i}',
                excerpt=f'Excerpt {i}',
                content=f'Content {i}',
                category=['news', 'event', 'parliament', 'program', 'update'][i % 5],
                status=['draft', 'published', 'archived'][i % 3],
                is_featured=i % 4 == 0,
                created_by=self.user,
                published_date=timezone.now() - timedelta(days=i) if i % 3 == 1 else None
            )
    
    def test_list_view_pagination(self):
        """Test pagination in the list view."""
        self.client.login(username='info_officer', password='testpass123')
        response = self.client.get(reverse('database_updates'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['announcements']), 20)  # Default pagination
        self.assertTrue(response.context['is_paginated'])
    
    def test_list_view_filtering(self):
        """Test filtering functionality."""
        self.client.login(username='info_officer', password='testpass123')
        
        # Test category filter
        response = self.client.get(reverse('database_updates'), {'category': 'news'})
        for announcement in response.context['announcements']:
            self.assertEqual(announcement.category, 'news')
        
        # Test status filter
        response = self.client.get(reverse('database_updates'), {'status': 'published'})
        for announcement in response.context['announcements']:
            self.assertEqual(announcement.status, 'published')
        
        # Test featured filter
        response = self.client.get(reverse('database_updates'), {'is_featured': 'yes'})
        for announcement in response.context['announcements']:
            self.assertTrue(announcement.is_featured)
    
    def test_list_view_search(self):
        """Test search functionality."""
        self.client.login(username='info_officer', password='testpass123')
        
        # Create a specific announcement to search for
        Announcement.objects.create(
            title='Special Announcement',
            excerpt='Special excerpt for testing',
            content='Special content for testing',
            created_by=self.user
        )
        
        response = self.client.get(reverse('database_updates'), {'search': 'Special'})
        
        self.assertTrue(any('Special' in ann.title for ann in response.context['announcements']))
    
    def test_list_view_statistics(self):
        """Test statistics display."""
        self.client.login(username='info_officer', password='testpass123')
        response = self.client.get(reverse('database_updates'))
        
        context = response.context
        self.assertIn('total_announcements', context)
        self.assertIn('published_count', context)
        self.assertIn('draft_count', context)
        self.assertIn('featured_count', context)
        self.assertIn('this_month_count', context)


class AnnouncementCRUDTestCase(TestCase):
    """Test Create, Read, Update, Delete operations for announcements."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='testpass123',
            user_type='information_officer'
        )
        self.client.login(username='info_officer', password='testpass123')
    
    def test_create_announcement(self):
        """Test creating a new announcement."""
        url = reverse('database_announcement_create')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/database_announcement_form.html')
        
        # Test POST request
        data = {
            'title': 'New Test Announcement',
            'category': 'news',
            'status': 'draft',
            'excerpt': 'This is a test excerpt',
            'content': '<p>This is test content</p>',
            'is_featured': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Check if announcement was created
        announcement = Announcement.objects.get(title='New Test Announcement')
        self.assertEqual(announcement.created_by, self.user)
        self.assertEqual(announcement.status, 'draft')
    
    def test_create_announcement_with_image(self):
        """Test creating an announcement with an image."""
        url = reverse('database_announcement_create')
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        uploaded_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )
        
        data = {
            'title': 'Announcement with Image',
            'category': 'news',
            'status': 'published',
            'excerpt': 'Test excerpt',
            'content': '<p>Test content</p>',
            'is_featured': True,
            'image': uploaded_image
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        announcement = Announcement.objects.get(title='Announcement with Image')
        self.assertTrue(announcement.image)
        self.assertIsNotNone(announcement.published_date)
    
    def test_update_announcement(self):
        """Test updating an existing announcement."""
        # Create an announcement
        announcement = Announcement.objects.create(
            title='Original Title',
            excerpt='Original excerpt',
            content='Original content',
            status='draft',
            created_by=self.user
        )
        
        url = reverse('database_announcement_edit', kwargs={'pk': announcement.pk})
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Original Title')
        
        # Test POST request
        data = {
            'title': 'Updated Title',
            'category': 'event',
            'status': 'published',
            'excerpt': 'Updated excerpt',
            'content': '<p>Updated content</p>',
            'is_featured': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Check if announcement was updated
        announcement.refresh_from_db()
        self.assertEqual(announcement.title, 'Updated Title')
        self.assertEqual(announcement.status, 'published')
        self.assertIsNotNone(announcement.published_date)
        self.assertTrue(announcement.is_featured)
    
    def test_delete_announcement(self):
        """Test deleting an announcement."""
        announcement = Announcement.objects.create(
            title='To Delete',
            excerpt='Test',
            content='Test',
            created_by=self.user
        )
        
        url = reverse('database_announcement_delete', kwargs={'pk': announcement.pk})
        
        # Test POST request (DELETE)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        # Check if announcement was deleted
        with self.assertRaises(Announcement.DoesNotExist):
            Announcement.objects.get(pk=announcement.pk)
    
    def test_save_and_continue_editing(self):
        """Test the save and continue editing functionality."""
        url = reverse('database_announcement_create')
        
        data = {
            'title': 'Save and Continue Test',
            'category': 'news',
            'status': 'draft',
            'excerpt': 'Test excerpt',
            'content': '<p>Test content</p>',
            'is_featured': False,
            'save_and_continue': 'true'
        }
        
        response = self.client.post(url, data)
        
        # Should redirect to edit page
        announcement = Announcement.objects.get(title='Save and Continue Test')
        expected_url = reverse('database_announcement_edit', kwargs={'pk': announcement.pk})
        self.assertRedirects(response, expected_url)


class PublicAnnouncementViewTestCase(TestCase):
    """Test the public announcement views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123'
        )
        
        # Create published announcements
        self.published_announcements = []
        for i in range(5):
            ann = Announcement.objects.create(
                title=f'Published Announcement {i}',
                slug=f'published-announcement-{i}',
                excerpt=f'Published excerpt {i}',
                content=f'<p>Published content {i}</p>',
                category='news',
                status='published',
                published_date=timezone.now() - timedelta(days=i),
                is_featured=i == 0,
                created_by=self.user
            )
            self.published_announcements.append(ann)
        
        # Create draft announcement (should not appear in public views)
        self.draft_announcement = Announcement.objects.create(
            title='Draft Announcement',
            excerpt='Draft excerpt',
            content='Draft content',
            status='draft',
            created_by=self.user
        )
    
    def test_public_announcement_list(self):
        """Test the public announcement list view."""
        response = self.client.get(reverse('announcements'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/announcements.html')
        
        # Check that only published announcements appear
        announcements = response.context['announcements']
        for ann in announcements:
            self.assertEqual(ann.status, 'published')
        
        # Check that draft announcement doesn't appear
        self.assertNotIn(self.draft_announcement, announcements)
    
    def test_public_announcement_detail(self):
        """Test the public announcement detail view."""
        announcement = self.published_announcements[0]
        
        response = self.client.get(
            reverse('announcement_detail', kwargs={'slug': announcement.slug})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/announcement_detail.html')
        self.assertContains(response, announcement.title)
        self.assertContains(response, announcement.content)
    
    def test_homepage_featured_announcements(self):
        """Test that featured announcements appear on homepage."""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        
        # Check if featured announcements are in context
        if 'featured_announcements' in response.context:
            featured = response.context['featured_announcements']
            for ann in featured:
                self.assertTrue(ann.is_featured)
                self.assertEqual(ann.status, 'published')