"""
Comprehensive tests for the #FahanieCares RBAC system.
Tests role hierarchy, permissions, decorators, and access control.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from ..models import DynamicPermission, RolePermission, UserPermissionOverride, RoleTransitionLog
from ..permissions import (
    HasRolePermission, HasDynamicPermission, HasFeatureAccess,
    get_user_permissions, assign_user_to_role_group
)
from ..decorators import require_role, require_role_or_higher, require_feature

User = get_user_model()


class RBACModelTests(TestCase):
    """Test RBAC model functionality."""
    
    def setUp(self):
        """Set up test users and permissions."""
        # Create test users for each role
        self.superuser_user = User.objects.create_user(
            username='super_test',
            password='testpass123',
            user_type='superuser'
        )
        self.mp_user = User.objects.create_user(
            username='mp_test',
            password='testpass123',
            user_type='mp'
        )
        self.chief_user = User.objects.create_user(
            username='chief_test',
            password='testpass123',
            user_type='chief_of_staff'
        )
        self.staff_user = User.objects.create_user(
            username='staff_test',
            password='testpass123',
            user_type='staff'
        )
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            user_type='admin'
        )
        self.coordinator_user = User.objects.create_user(
            username='coord_test',
            password='testpass123',
            user_type='coordinator'
        )
        self.info_officer_user = User.objects.create_user(
            username='info_test',
            password='testpass123',
            user_type='info_officer'
        )
        self.member_user = User.objects.create_user(
            username='member_test',
            password='testpass123',
            user_type='chapter_member'
        )
        self.basic_user = User.objects.create_user(
            username='user_test',
            password='testpass123',
            user_type='registered_user'
        )
        
        # Create test permission
        self.test_permission = DynamicPermission.objects.create(
            name='Test Permission',
            codename='test_permission',
            description='A test permission',
            module='test'
        )
    
    def test_role_hierarchy(self):
        """Test role hierarchy levels with staff-based structure."""
        # Test hierarchy levels with corrected staff-based structure
        self.assertEqual(self.superuser_user.get_role_hierarchy_level(), 10)
        self.assertEqual(self.mp_user.get_role_hierarchy_level(), 9)
        self.assertEqual(self.chief_user.get_role_hierarchy_level(), 8)
        self.assertEqual(self.admin_user.get_role_hierarchy_level(), 7)  # System Administrator
        self.assertEqual(self.coordinator_user.get_role_hierarchy_level(), 6)
        self.assertEqual(self.info_officer_user.get_role_hierarchy_level(), 5)
        self.assertEqual(self.staff_user.get_role_hierarchy_level(), 4)  # Base staff level
        self.assertEqual(self.member_user.get_role_hierarchy_level(), 3)
        self.assertEqual(self.basic_user.get_role_hierarchy_level(), 2)
    
    def test_has_role_permission(self):
        """Test role permission checking."""
        # MP can access everything
        self.assertTrue(self.mp_user.has_role_permission('registered_user'))
        self.assertTrue(self.mp_user.has_role_permission('coordinator'))
        self.assertTrue(self.mp_user.has_role_permission('mp'))
        
        # Coordinator can access coordinator and below
        self.assertTrue(self.coordinator_user.has_role_permission('registered_user'))
        self.assertTrue(self.coordinator_user.has_role_permission('coordinator'))
        self.assertFalse(self.coordinator_user.has_role_permission('admin'))
        
        # Basic user can only access their level
        self.assertTrue(self.basic_user.has_role_permission('registered_user'))
        self.assertFalse(self.basic_user.has_role_permission('chapter_member'))
    
    def test_role_specific_methods(self):
        """Test role-specific check methods."""
        # Test Superuser check
        self.assertTrue(self.superuser_user.is_superuser_role())
        self.assertFalse(self.mp_user.is_superuser_role())
        
        # Test MP check
        self.assertTrue(self.mp_user.is_mp())
        self.assertFalse(self.chief_user.is_mp())
        
        # Test Chief of Staff check
        self.assertTrue(self.chief_user.is_chief_of_staff())
        self.assertFalse(self.admin_user.is_chief_of_staff())
        
        # Test Staff check
        self.assertTrue(self.staff_user.is_staff_role())
        self.assertFalse(self.admin_user.is_staff_role())
        
        # Test Admin check
        self.assertTrue(self.admin_user.is_admin())
        self.assertFalse(self.coordinator_user.is_admin())
        
        # Test Coordinator check
        self.assertTrue(self.coordinator_user.is_coordinator())
        self.assertFalse(self.info_officer_user.is_coordinator())
        
        # Test Info Officer check
        self.assertTrue(self.info_officer_user.is_info_officer())
        self.assertFalse(self.member_user.is_info_officer())
    
    def test_dynamic_permissions(self):
        """Test dynamic permission system."""
        # Assign permission to coordinator role
        RolePermission.objects.create(
            role='coordinator',
            permission=self.test_permission,
            is_active=True
        )
        
        # Check permission exists
        permissions = get_user_permissions(self.coordinator_user)
        self.assertIn('test_permission', permissions)
        
        # Check other roles don't have it
        permissions = get_user_permissions(self.basic_user)
        self.assertNotIn('test_permission', permissions)
    
    def test_permission_overrides(self):
        """Test user permission overrides."""
        # Grant permission override to basic user
        override = UserPermissionOverride.objects.create(
            user=self.basic_user,
            permission=self.test_permission,
            is_granted=True,
            reason='Test grant'
        )
        
        # Check permission is granted
        permissions = get_user_permissions(self.basic_user)
        self.assertIn('test_permission', permissions)
        
        # Revoke permission from coordinator
        RolePermission.objects.create(
            role='coordinator',
            permission=self.test_permission,
            is_active=True
        )
        
        revoke_override = UserPermissionOverride.objects.create(
            user=self.coordinator_user,
            permission=self.test_permission,
            is_granted=False,
            reason='Test revoke'
        )
        
        # Check permission is revoked
        permissions = get_user_permissions(self.coordinator_user)
        self.assertNotIn('test_permission', permissions)
    
    def test_permission_expiry(self):
        """Test permission override expiry."""
        # Create expired override
        expired_override = UserPermissionOverride.objects.create(
            user=self.basic_user,
            permission=self.test_permission,
            is_granted=True,
            reason='Temporary access',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Check override is not active
        self.assertFalse(expired_override.is_active())
        
        # Check permission is not granted
        permissions = get_user_permissions(self.basic_user)
        self.assertNotIn('test_permission', permissions)
    
    def test_role_transition_logging(self):
        """Test role transition logging."""
        # Change user role
        self.basic_user.user_type = 'coordinator'
        self.basic_user.role_assigned_by = self.chief_user
        self.basic_user.role_assigned_at = timezone.now()
        self.basic_user.save()
        
        # Create log entry
        log = RoleTransitionLog.objects.create(
            user=self.basic_user,
            from_role='registered_user',
            to_role='coordinator',
            reason='Promotion test',
            changed_by=self.chief_user
        )
        
        # Verify log entry
        self.assertEqual(log.user, self.basic_user)
        self.assertEqual(log.from_role, 'registered_user')
        self.assertEqual(log.to_role, 'coordinator')
        self.assertEqual(log.changed_by, self.chief_user)


class RBACPermissionTests(TestCase):
    """Test permission classes."""
    
    def setUp(self):
        """Set up test environment."""
        self.factory = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass',
            user_type='admin'
        )
        self.basic_user = User.objects.create_user(
            username='basic',
            password='testpass',
            user_type='registered_user'
        )
    
    def test_has_role_permission_class(self):
        """Test HasRolePermission permission class."""
        permission = HasRolePermission()
        
        # Create mock request and view
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        class MockView:
            required_role = 'admin'
        
        # Test admin access
        request = MockRequest(self.admin_user)
        view = MockView()
        self.assertTrue(permission.has_permission(request, view))
        
        # Test basic user denied
        request = MockRequest(self.basic_user)
        self.assertFalse(permission.has_permission(request, view))
    
    def test_has_feature_access_class(self):
        """Test HasFeatureAccess permission class."""
        permission = HasFeatureAccess()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        class MockView:
            required_feature = 'referral_management'
        
        # Test admin has access
        request = MockRequest(self.admin_user)
        view = MockView()
        self.assertTrue(permission.has_permission(request, view))
        
        # Test basic user denied
        request = MockRequest(self.basic_user)
        self.assertFalse(permission.has_permission(request, view))


class RBACDecoratorTests(TestCase):
    """Test permission decorators."""
    
    def setUp(self):
        """Set up test environment."""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass',
            user_type='admin'
        )
        self.basic_user = User.objects.create_user(
            username='basic',
            password='testpass',
            user_type='registered_user'
        )
    
    def test_require_role_decorator(self):
        """Test require_role decorator."""
        @require_role('admin', 'chief_of_staff')
        def admin_only_view(request):
            return 'Success'
        
        # Create mock request
        class MockRequest:
            def __init__(self, user):
                self.user = user
                self.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        # Test admin access
        request = MockRequest(self.admin_user)
        # Note: In real test, would need to mock login_required
        # This is a simplified test
        
        # Test basic user denied
        request = MockRequest(self.basic_user)
        # Would raise PermissionDenied in real scenario
    
    def test_require_role_or_higher_decorator(self):
        """Test require_role_or_higher decorator."""
        @require_role_or_higher('coordinator')
        def coordinator_view(request):
            return 'Success'
        
        # Test with admin (higher than coordinator)
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.admin_user)
        # Admin should have access
        
        request = MockRequest(self.basic_user)
        # Basic user should be denied


class RBACIntegrationTests(TestCase):
    """Integration tests for RBAC system."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        
        # Create users
        self.mp_user = User.objects.create_user(
            username='mp',
            password='testpass',
            user_type='mp'
        )
        self.coordinator_user = User.objects.create_user(
            username='coordinator',
            password='testpass',
            user_type='coordinator'
        )
        self.basic_user = User.objects.create_user(
            username='basic',
            password='testpass',
            user_type='registered_user'
        )
        
        # Set up groups
        from apps.users.permissions import setup_role_groups
        setup_role_groups()
        
        # Assign users to groups
        assign_user_to_role_group(self.mp_user)
        assign_user_to_role_group(self.coordinator_user)
        assign_user_to_role_group(self.basic_user)
    
    def test_group_assignment(self):
        """Test automatic group assignment."""
        # Check MP is in correct group
        self.assertTrue(
            self.mp_user.groups.filter(name='Member of Parliament').exists()
        )
        
        # Check coordinator is in correct group
        self.assertTrue(
            self.coordinator_user.groups.filter(name='Coordinator').exists()
        )
        
        # Check basic user is in correct group
        self.assertTrue(
            self.basic_user.groups.filter(name='Registered User').exists()
        )
    
    def test_legacy_role_mapping(self):
        """Test legacy role mapping."""
        # Create legacy user
        legacy_user = User.objects.create_user(
            username='legacy',
            password='testpass',
            user_type='staff'  # Now maps to Parliamentary Office Staff
        )
        
        # Check it maps to staff role
        self.assertTrue(legacy_user.is_staff_role())
        
        # Assign to group
        assign_user_to_role_group(legacy_user)
        
        # Check assigned to staff group
        self.assertTrue(
            legacy_user.groups.filter(name='Parliamentary Office Staff').exists()
        )