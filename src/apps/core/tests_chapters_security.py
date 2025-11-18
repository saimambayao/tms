"""
Security tests for chapters access control separation.
Tests public vs staff-only access to ensure proper role-based restrictions.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.chapters.models import Chapter

User = get_user_model()


class ChaptersAccessControlTest(TestCase):
    """Test access control separation between public and staff chapter views."""
    
    def setUp(self):
        """Set up test users with different roles and test data."""
        self.client = Client()
        
        # Create test users with different roles
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.mp_user = User.objects.create_user(
            username='mp_user',
            email='mp@test.com',
            password='testpass123',
            user_type='mp',
            first_name='MP',
            last_name='User'
        )
        
        self.coordinator_user = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123',
            user_type='coordinator',
            first_name='Coordinator',
            last_name='User'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123',
            user_type='public',
            first_name='Regular',
            last_name='User'
        )
        
        # Create test chapter
        self.test_chapter = Chapter.objects.create(
            name='Test Chapter',
            tier='provincial',
            municipality='Test City',
            province='Test Province',
            country='Philippines',
            description='Test chapter for security testing',
            status='active'
        )
    
    def test_public_chapters_list_accessible_to_all(self):
        """Test that public chapters list is accessible to everyone."""
        # Test anonymous user
        response = self.client.get(reverse('chapter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chapters/chapter_list.html')
        
        # Test regular user
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('chapter_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test admin user
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('chapter_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_database_chapters_requires_login(self):
        """Test that database chapters view requires login."""
        # Test anonymous user gets redirected to login
        response = self.client.get(reverse('chapters_overview'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_database_chapters_requires_proper_role(self):
        """Test that database chapters view requires proper role."""
        # Test regular user gets redirected to home
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('chapters_overview'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Verify error message is set
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('You do not have permission' in str(m) for m in messages))
    
    def test_database_chapters_accessible_to_authorized_roles(self):
        """Test that database chapters view is accessible to authorized roles."""
        authorized_users = [
            ('admin', 'testpass123'),  # Superuser
            ('mp_user', 'testpass123'),  # MP
            ('coordinator', 'testpass123'),  # Coordinator
        ]
        
        for username, password in authorized_users:
            self.client.login(username=username, password=password)
            response = self.client.get(reverse('chapters_overview'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/database_chapters.html')
            self.client.logout()
    
    def test_assign_chapter_ajax_requires_authorization(self):
        """Test that chapter assignment AJAX endpoint requires proper authorization."""
        # Test anonymous user
        response = self.client.post(reverse('assign_chapter'), {
            'registrant_id': '1',
            'chapter_id': '1'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user
        self.client.login(username='regular', password='testpass123')
        response = self.client.post(reverse('assign_chapter'), {
            'registrant_id': '1',
            'chapter_id': '1'
        })
        self.assertEqual(response.status_code, 403)  # Permission denied
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Permission denied')
        
        # Test authorized user (coordinator)
        self.client.login(username='coordinator', password='testpass123')
        response = self.client.post(reverse('assign_chapter'), {
            'registrant_id': '1',
            'chapter_id': '1'
        })
        # Will fail with 404 because test data doesn't exist, but not 403
        self.assertNotEqual(response.status_code, 403)
    
    def test_chapter_detail_public_access(self):
        """Test that chapter detail view is publicly accessible."""
        # Test anonymous user
        response = self.client.get(reverse('chapter_detail', kwargs={'slug': self.test_chapter.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chapters/chapter_detail.html')
        
        # Test logged-in user
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('chapter_detail', kwargs={'slug': self.test_chapter.slug}))
        self.assertEqual(response.status_code, 200)
    
    def test_security_headers_on_database_view(self):
        """Test that database view has proper security headers."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('chapters_overview'))
        
        # Verify CSRF token is in context for forms
        self.assertIn('csrf_token', response.context)
        
        # Verify user role is displayed (check for the actual content)
        self.assertContains(response, 'Chapters Database Management')


class ChapterURLSeparationTest(TestCase):
    """Test URL pattern separation between public and staff views."""
    
    def test_distinct_url_patterns(self):
        """Test that public and staff URLs are distinct and non-conflicting."""
        # Public URLs
        public_url = reverse('chapter_list')
        self.assertEqual(public_url, '/chapters/')
        
        # Staff database URL
        staff_url = reverse('chapters_overview')
        self.assertEqual(staff_url, '/chapters-overview/')
        
        # Ensure they are different
        self.assertNotEqual(public_url, staff_url)
    
    def test_url_namespace_separation(self):
        """Test that URLs are properly namespaced to avoid conflicts."""
        # Chapter app URLs should be under /chapters/
        self.assertTrue(reverse('chapter_list').startswith('/chapters/'))
        self.assertTrue(reverse('chapter_create').startswith('/chapters/'))
        
        # Core app database URL should be separate
        self.assertTrue(reverse('chapters_overview').startswith('/chapters-overview/'))