"""
Enhanced custom permission classes for #FahanieCares role-based access control.
Integrates with dynamic permissions and comprehensive role hierarchy.
"""

from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.permissions import BasePermission
from guardian.shortcuts import get_objects_for_user
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


def cache_permission_check(timeout=300):
    """
    Decorator to cache permission check results.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, view, obj=None):
            # Create cache key based on user, view, and object
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            view_name = view.__class__.__name__
            obj_id = obj.id if obj and hasattr(obj, 'id') else 'none'
            
            cache_key = f"perm_{user_id}_{view_name}_{obj_id}_{func.__name__}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Calculate permission based on function signature
            if func.__name__ == 'has_permission':
                result = func(self, request, view)
            else:  # has_object_permission
                result = func(self, request, view, obj)
            
            # Cache the result
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    @cache_permission_check()
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
        
        # Write permissions only to owner
        return obj.owner == request.user if hasattr(obj, 'owner') else False


class HasRolePermission(BasePermission):
    """
    Enhanced permission class that checks if user has required role for the action.
    Integrates with the User model's role hierarchy.
    """
    
    @cache_permission_check()
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get required role from view
        required_role = getattr(view, 'required_role', None)
        if not required_role:
            return True
        
        # Use the User model's role permission check
        has_permission = request.user.has_role_permission(required_role)
        
        # Update last permission check timestamp
        request.user.update_last_permission_check()
        
        # Log permission check for auditing
        logger.info(
            f"Permission check: User {request.user.username} ({request.user.user_type}) "
            f"accessing {view.__class__.__name__} requiring {required_role}: {has_permission}"
        )
        
        return has_permission
    
    @cache_permission_check()
    def has_object_permission(self, request, view, obj):
        # First check general permission
        if not self.has_permission(request, view):
            return False
        
        # Check object-specific permissions if needed
        object_role = getattr(view, 'object_required_role', None)
        if object_role:
            return request.user.has_role_permission(object_role)
        
        return True


class HasDynamicPermission(BasePermission):
    """
    Permission class that checks dynamic permissions from the database.
    """
    
    @cache_permission_check()
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get required permission codename from view
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True
        
        # Import here to avoid circular imports
        from .models import DynamicPermission, RolePermission, UserPermissionOverride
        
        # Check if permission exists and is active
        try:
            permission = DynamicPermission.objects.get(
                codename=required_permission,
                is_active=True
            )
        except DynamicPermission.DoesNotExist:
            logger.warning(f"Dynamic permission {required_permission} not found")
            return False
        
        # Check user permission overrides first
        override = UserPermissionOverride.objects.filter(
            user=request.user,
            permission=permission
        ).first()
        
        if override and override.is_active():
            logger.info(
                f"Permission override: User {request.user.username} "
                f"{override.is_granted and 'granted' or 'revoked'} {permission.codename}"
            )
            return override.is_granted
        
        # Check role-based permission
        has_role_permission = RolePermission.objects.filter(
            role=request.user.user_type,
            permission=permission,
            is_active=True
        ).exists()
        
        logger.info(
            f"Dynamic permission check: User {request.user.username} ({request.user.user_type}) "
            f"for {permission.codename}: {has_role_permission}"
        )
        
        return has_role_permission


class HasFeatureAccess(BasePermission):
    """
    Enhanced permission class that checks if user has access to specific features.
    Updated to include all new roles in the RBAC system.
    """
    
    FEATURE_PERMISSIONS = {
        # Base Staff Features (All parliamentary staff get these)
        'task_management': ['staff', 'info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'calendar_management': ['staff', 'info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'schedule_coordination': ['staff', 'info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'office_workflow': ['staff', 'info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        
        # Communication Features (Info Officer + above)
        'announcement_management': ['info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'content_management': ['info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'notification_broadcast': ['info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        
        # Service Management Features (Coordinator + above)
        'referral_management': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'program_administration': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'chapter_management': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'constituent_management': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'fahaniecares_programs': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'tdif_projects': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'ministry_programs': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        
        # System Administration Features (Admin + above)
        'system_administration': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        'user_management': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        'security_settings': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        'integration_management': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        'workflow_management': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        'audit_logs': ['admin', 'chief_of_staff', 'mp', 'superuser'],
        
        # Strategic Features (Chief of Staff + above)
        'role_management': ['chief_of_staff', 'mp', 'superuser'],
        'document_approval': ['chief_of_staff', 'mp', 'superuser'],
        
        # Analytics and reporting (based on role level)
        'analytics_view': ['info_officer', 'coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'operational_reports': ['coordinator', 'admin', 'chief_of_staff', 'mp', 'superuser'],
        'executive_reports': ['admin', 'chief_of_staff', 'mp', 'superuser'],
    }
    
    @cache_permission_check()
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get required feature from view
        required_feature = getattr(view, 'required_feature', None)
        if not required_feature:
            return True
        
        allowed_roles = self.FEATURE_PERMISSIONS.get(required_feature, [])
        return request.user.user_type in allowed_roles
    
    @cache_permission_check()
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ChapterPermission(BasePermission):
    """
    Permission class for chapter-based access control.
    """
    
    @cache_permission_check()
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff and MP have access to all chapters
        if request.user.is_staff_or_above():
            return True
        
        # Chapter members can only access their own chapter
        return bool(request.user.chapter_id)
    
    @cache_permission_check()
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Staff and MP have access to all chapters
        if request.user.is_staff_or_above():
            return True
        
        # Check if object belongs to user's chapter
        if hasattr(obj, 'chapter_id'):
            return obj.chapter_id == request.user.chapter_id
        elif hasattr(obj, 'chapter'):
            return str(obj.chapter.id) == request.user.chapter_id
        
        return False


class RoleBasedMixin:
    """
    Mixin for views to easily implement role-based permissions.
    """
    
    def get_required_role(self):
        """Override this method to set required role dynamically."""
        return getattr(self, 'required_role', None)
    
    def get_required_feature(self):
        """Override this method to set required feature dynamically."""
        return getattr(self, 'required_feature', None)
    
    def check_permissions(self, request):
        """Check all permission requirements."""
        # Check role permission
        required_role = self.get_required_role()
        if required_role:
            permission = HasRolePermission()
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request,
                    message=f"Role '{required_role}' or higher required."
                )
        
        # Check feature permission
        required_feature = self.get_required_feature()
        if required_feature:
            permission = HasFeatureAccess()
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request,
                    message=f"Access to '{required_feature}' feature required."
                )


def setup_role_groups():
    """
    Enhanced setup for Django Groups with comprehensive RBAC role hierarchy.
    Creates groups for all roles with appropriate permissions.
    """
    
    # Define roles and their permissions based on the new RBAC structure
    role_permissions = {
        'Registered User': [
            # Basic profile and service access
            'view_user',  # Own profile only
            'change_user',  # Own profile only
            'view_program',
            'view_service',
            'add_referral',  # Apply for services
            'view_referral',  # Own referrals only
            'view_announcement',
        ],
        
        'Chapter Member': [
            # All Registered User permissions plus:
            'view_user',
            'change_user',
            'view_program',
            'view_service',
            'add_referral',
            'view_referral',
            'view_announcement',
            # Chapter-specific permissions
            'view_chapter',
            'view_constituent',  # Limited to own chapter
            'add_constituent',  # Can refer others
            'view_chapter_activity',
            'participate_chapter_activity',
        ],
        
        'Information Officer': [
            # All Parliamentary Office Staff permissions
            'view_user',
            'change_user',
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
            'view_calendar',
            'view_tasks',
            # PLUS Communications management
            'view_announcement',
            'add_announcement',
            'change_announcement',
            'delete_announcement',
            'view_content',
            'add_content',
            'change_content',
            'delete_content',
            'send_notification',
            'manage_newsletter',
            'view_media_resource',
            'add_media_resource',
            'change_media_resource',
        ],
        
        'Coordinator': [
            # All Parliamentary Office Staff permissions (base staff permissions)
            'view_user',
            'change_user',
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
            'view_calendar',
            'view_tasks',
            # PLUS Service coordination and management
            'add_user',  # Register constituents
            'view_program',
            'add_program',
            'change_program',
            'view_service',
            'add_service',
            'change_service',
            'add_referral',
            'view_referral',
            'change_referral',
            'view_announcement',
            'view_chapter',
            'change_chapter',
            'view_constituent',
            'add_constituent',
            'change_constituent',
            'delete_constituent',
            # Service coordination
            'manage_fahaniecares_program',
            'manage_tdif_project',
            'manage_ministry_program',
            'view_operational_report',
            'export_data',
            'view_chapter_activity',
            'manage_chapter_activity',
        ],
        
        'System Administrator': [
            # All Parliamentary Office Staff permissions (base staff permissions)
            'view_user',
            'change_user',
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
            'view_calendar',
            'view_tasks',
            # PLUS Full technical and portal management control
            'add_user',
            'delete_user',
            'view_program',
            'add_program',
            'change_program',
            'delete_program',
            'view_service',
            'add_service',
            'change_service',
            'delete_service',
            'view_referral',
            'add_referral',
            'change_referral',
            'delete_referral',
            'view_chapter',
            'add_chapter',
            'change_chapter',
            'delete_chapter',
            'view_constituent',
            'add_constituent',
            'change_constituent',
            'delete_constituent',
            # System administration
            'view_system_config',
            'change_system_config',
            'view_integration',
            'change_integration',
            'view_audit_log',
            'manage_security',
            'manage_backup',
            'manage_fahaniecares_program',
            'manage_tdif_project',
            'manage_ministry_program',
            'view_operational_report',
            'export_data',
            # Content and communication management
            'view_announcement',
            'add_announcement',
            'change_announcement',
            'delete_announcement',
            'view_content',
            'add_content',
            'change_content',
            'delete_content',
            'send_notification',
        ],
        
        'Parliamentary Office Staff': [
            # Base staff permissions - minimal access
            'view_user',        # Own profile only
            'change_user',      # Own profile only
            # Task and calendar management (future functionality)
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
            'view_calendar',
            'view_tasks',
        ],
        
        'Chief of Staff': [
            # All Staff permissions plus strategic functions
            'view_user',
            'add_user',
            'change_user',
            'delete_user',
            'assign_role',  # Role management
            'view_executive_report',
            'manage_workflow',
            'approve_critical_action',
            'view_all_data',
            'export_all_data',
            'manage_staff',
            'strategic_planning',
            # All staff permissions
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
        ],
        
        'Member of Parliament': [
            # Strategic oversight only
            'view_executive_dashboard',
            'view_executive_report',
            'view_analytics',
            'view_all_data',  # Read-only access to all
            'strategic_oversight',
            'view_audit_log',
            # Calendar viewing for awareness
            'view_calendar',
            'view_tasks',
        ],
        
        'Superuser': [
            # Ultimate system control - all permissions
            'view_user',
            'add_user',
            'change_user',
            'delete_user',
            'assign_role',
            'view_program',
            'add_program',
            'change_program',
            'delete_program',
            'view_service',
            'add_service',
            'change_service',
            'delete_service',
            'view_referral',
            'add_referral',
            'change_referral',
            'delete_referral',
            'view_chapter',
            'add_chapter',
            'change_chapter',
            'delete_chapter',
            'view_constituent',
            'add_constituent',
            'change_constituent',
            'delete_constituent',
            'view_announcement',
            'add_announcement',
            'change_announcement',
            'delete_announcement',
            # System administration
            'view_system_config',
            'change_system_config',
            'view_integration',
            'change_integration',
            'view_audit_log',
            'manage_security',
            'manage_backup',
            # Strategic oversight
            'view_executive_dashboard',
            'view_executive_report',
            'view_analytics',
            'view_all_data',
            'strategic_oversight',
            'manage_workflow',
            'approve_critical_action',
            'export_all_data',
            'manage_staff',
            'strategic_planning',
            # Task and calendar management
            'manage_tasks',
            'manage_calendar',
            'coordinate_schedule',
            'manage_office_workflow',
            'manage_meetings',
            'coordinate_events',
            'manage_appointments',
            'view_calendar',
            'view_tasks',
            # Content management
            'view_content',
            'add_content',
            'change_content',
            'delete_content',
            'send_notification',
            'manage_newsletter',
            'view_media_resource',
            'add_media_resource',
            'change_media_resource',
        ],
    }
    
    # Create groups and assign permissions
    for role_name, permission_names in role_permissions.items():
        group, created = Group.objects.get_or_create(name=role_name)
        
        if created or not group.permissions.exists():
            # Clear existing permissions
            group.permissions.clear()
            
            # Add permissions
            for perm_name in permission_names:
                try:
                    permission = Permission.objects.get(codename=perm_name)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission '{perm_name}' not found for group '{role_name}'")
        
        print(f"{'Created' if created else 'Updated'} group: {role_name}")


def assign_user_to_role_group(user):
    """
    Enhanced function to assign user to appropriate group based on user_type.
    Handles both new and legacy user types.
    """
    # Map user types to group names
    type_to_group = {
        # New RBAC roles
        'superuser': 'Superuser',
        'mp': 'Member of Parliament',
        'chief_of_staff': 'Chief of Staff',
        'staff': 'Parliamentary Office Staff',
        'admin': 'System Administrator',
        'coordinator': 'Coordinator',
        'info_officer': 'Information Officer',
        'chapter_member': 'Chapter Member',
        'registered_user': 'Registered User',
        # Legacy mappings
        'member': 'Chapter Member',  # Map old member to chapter_member
        'constituent': 'Registered User',  # Map old constituent to registered_user
    }
    
    # Get all role group names
    all_role_groups = [
        'Superuser',
        'Member of Parliament',
        'Chief of Staff', 
        'Parliamentary Office Staff',
        'System Administrator',
        'Coordinator',
        'Information Officer',
        'Chapter Member',
        'Registered User',
        # Legacy groups to clean up
        'Member',
        'Chapter Coordinator',
        'Referral Staff',
        'Program Admin',
        'Superadmin',
    ]
    
    # Remove user from all role groups first
    role_groups = Group.objects.filter(name__in=all_role_groups)
    user.groups.remove(*role_groups)
    
    # Add user to appropriate group
    group_name = type_to_group.get(user.user_type)
    if group_name:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            logger.info(f"User {user.username} assigned to group {group_name}")
            
            # Log role transition
            from .models import RoleTransitionLog
            RoleTransitionLog.objects.create(
                user=user,
                to_role=user.user_type,
                reason="Automatic group assignment based on user type",
                changed_by=None  # System action
            )
        except Group.DoesNotExist:
            logger.error(f"Group '{group_name}' not found for user {user.username}")


def get_user_permissions(user):
    """
    Get all permissions for a user, including role-based and overrides.
    Returns a set of permission codenames.
    """
    if not user.is_authenticated:
        return set()
    
    # Check cache first
    cache_key = user.get_permissions_cache_key()
    cached_permissions = cache.get(cache_key)
    if cached_permissions is not None:
        return cached_permissions
    
    permissions = set()
    
    # Import here to avoid circular imports
    from .models import DynamicPermission, RolePermission, UserPermissionOverride
    
    # Get role-based permissions
    role_permissions = RolePermission.objects.filter(
        role=user.user_type,
        is_active=True,
        permission__is_active=True
    ).values_list('permission__codename', flat=True)
    permissions.update(role_permissions)
    
    # Apply user permission overrides
    overrides = UserPermissionOverride.objects.filter(
        user=user
    ).select_related('permission')
    
    for override in overrides:
        if override.is_active():
            if override.is_granted:
                permissions.add(override.permission.codename)
            else:
                permissions.discard(override.permission.codename)
    
    # Add Django's built-in permissions from groups
    group_permissions = user.get_group_permissions()
    permissions.update(perm.split('.')[-1] for perm in group_permissions)
    
    # Cache the permissions
    cache.set(cache_key, permissions, 300)  # 5 minutes
    
    return permissions


def clear_permission_cache(user_id=None):
    """
    Clear permission cache for a specific user or all users.
    """
    if user_id:
        # Clear cache for specific user
        cache_pattern = f"perm_{user_id}_*"
    else:
        # Clear all permission cache
        cache_pattern = "perm_*"
    
    # Note: This is a simplified approach
    # In production, you might want to use Redis SCAN for better performance
    cache.clear(using='permissions')