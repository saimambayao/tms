"""
Template tags for permission checking in #FahanieCares.
"""

from django import template
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from guardian.shortcuts import get_perms
import hashlib

register = template.Library()


@register.simple_tag
def has_permission(user, permission, obj=None):
    """
    Check if user has a specific permission on an object.
    
    Usage: {% has_permission user 'change_referral' referral_obj %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Create cache key
    obj_id = obj.id if obj and hasattr(obj, 'id') else 'none'
    cache_key = f"template_perm_{user.id}_{permission}_{obj_id}"
    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
    
    # Try cache first
    result = cache.get(cache_key)
    if result is not None:
        return result
    
    # Check permission
    if obj:
        # Object-level permission
        result = user.has_perm(permission, obj)
    else:
        # Model-level permission
        result = user.has_perm(permission)
    
    # Cache result
    cache.set(cache_key, result, 300)
    return result


@register.simple_tag
def has_role(user, role):
    """
    Check if user has a specific role.
    
    Usage: {% has_role user 'staff' %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    return getattr(user, 'user_type', None) == role


@register.simple_tag
def has_role_or_higher(user, role):
    """
    Check if user has a specific role or higher.
    
    Usage: {% has_role_or_higher user 'coordinator' %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Use the User model's method for consistency
    return user.has_role_permission(role) if hasattr(user, 'has_role_permission') else False


@register.simple_tag
def has_feature_access(user, feature):
    """
    Check if user has access to a specific feature.
    
    Usage: {% has_feature_access user 'referral_management' %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    from ..permissions import HasFeatureAccess
    
    permission = HasFeatureAccess()
    allowed_roles = permission.FEATURE_PERMISSIONS.get(feature, [])
    user_role = getattr(user, 'user_type', '')
    
    return user_role in allowed_roles


@register.simple_tag
def can_manage_chapter(user, chapter=None):
    """
    Check if user can manage a specific chapter.
    
    Usage: {% can_manage_chapter user chapter_obj %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Staff and MP can manage all chapters
    if hasattr(user, 'is_staff_or_above') and user.is_staff_or_above():
        return True
    
    # Coordinators can manage their own chapter
    if getattr(user, 'user_type', '') == 'coordinator':
        if chapter:
            return str(chapter.id) == getattr(user, 'chapter_id', '')
        return bool(getattr(user, 'chapter_id', ''))
    
    return False


@register.simple_tag
def can_view_referral(user, referral):
    """
    Check if user can view a specific referral.
    
    Usage: {% can_view_referral user referral_obj %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Staff and MP can view all referrals
    if hasattr(user, 'is_staff_or_above') and user.is_staff_or_above():
        return True
    
    # Users can view their own referrals
    if hasattr(referral, 'owner') and referral.owner == user:
        return True
    
    # Chapter coordinators can view referrals from their chapter
    if (getattr(user, 'user_type', '') == 'coordinator' and 
        hasattr(referral, 'chapter_id') and 
        referral.chapter_id == getattr(user, 'chapter_id', '')):
        return True
    
    return False


@register.simple_tag
def can_edit_referral(user, referral):
    """
    Check if user can edit a specific referral.
    
    Usage: {% can_edit_referral user referral_obj %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Staff and MP can edit all referrals
    if hasattr(user, 'is_staff_or_above') and user.is_staff_or_above():
        return True
    
    # Users can edit their own pending referrals
    if (hasattr(referral, 'owner') and referral.owner == user and 
        getattr(referral, 'status', '') in ['pending', 'submitted']):
        return True
    
    return False


@register.filter
def user_role_display(user):
    """
    Get a human-readable display of the user's role.
    
    Usage: {{ user|user_role_display }}
    """
    if isinstance(user, AnonymousUser):
        return 'Guest'
    
    role_map = {
        # New RBAC roles
        'mp': 'Member of Parliament',
        'chief_of_staff': 'Chief of Staff',
        'admin': 'System Administrator',
        'coordinator': 'Coordinator',
        'info_officer': 'Information Officer',
        'chapter_member': 'Chapter Member',
        'registered_user': 'Registered User',
        # Legacy roles
        'constituent': 'Constituent',
        'member': 'Member',
        'staff': 'Parliamentary Staff',
    }
    
    return role_map.get(getattr(user, 'user_type', ''), 'Unknown')


@register.inclusion_tag('components/navigation/role_menu.html', takes_context=True)
def role_navigation_menu(context):
    """
    Render role-based navigation menu.
    
    Usage: {% role_navigation_menu %}
    """
    request = context['request']
    user = request.user
    
    if isinstance(user, AnonymousUser):
        return {'nav_items': []}
    
    # Get navigation items from middleware
    nav_items = getattr(request, 'navigation_items', [])
    
    return {
        'nav_items': nav_items,
        'user': user,
        'user_role': getattr(user, 'user_type', ''),
        'request': request,
    }


@register.inclusion_tag('components/permissions/feature_check.html')
def feature_access_check(user, feature, show_message=True):
    """
    Check feature access and optionally show a message.
    
    Usage: {% feature_access_check user 'referral_management' %}
    """
    has_access = has_feature_access(user, feature)
    
    return {
        'has_access': has_access,
        'feature': feature,
        'user': user,
        'show_message': show_message,
    }


@register.simple_tag(takes_context=True)
def available_features(context):
    """
    Get list of features available to the current user.
    
    Usage: {% available_features as features %}
    """
    request = context['request']
    return getattr(request, 'available_features', [])


@register.simple_tag
def user_permissions(user):
    """
    Get list of permissions for the user.
    
    Usage: {% user_permissions user as permissions %}
    """
    if isinstance(user, AnonymousUser):
        return []
    
    # Get from cache
    cache_key = f"user_perms_{user.id}"
    permissions = cache.get(cache_key)
    
    if permissions is None:
        permissions = []
        
        # Get permissions from groups
        for group in user.groups.all():
            permissions.extend([
                perm.codename for perm in group.permissions.all()
            ])
        
        # Get direct permissions
        permissions.extend([
            perm.codename for perm in user.user_permissions.all()
        ])
        
        permissions = list(set(permissions))
        cache.set(cache_key, permissions, 300)
    
    return permissions


@register.simple_tag
def chapter_members_count(chapter):
    """
    Get count of members in a chapter.
    
    Usage: {% chapter_members_count chapter_obj %}
    """
    if not chapter:
        return 0
    
    cache_key = f"chapter_members_{chapter.id}"
    count = cache.get(cache_key)
    
    if count is None:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = User.objects.filter(chapter_id=str(chapter.id)).count()
        cache.set(cache_key, count, 600)  # Cache for 10 minutes
    
    return count


@register.simple_tag
def pending_referrals_count(user):
    """
    Get count of pending referrals for a user or chapter.
    
    Usage: {% pending_referrals_count user %}
    """
    if isinstance(user, AnonymousUser):
        return 0
    
    cache_key = f"pending_referrals_{user.id}"
    count = cache.get(cache_key)
    
    if count is None:
        from ...referrals.models import Referral
        
        if hasattr(user, 'is_staff_or_above') and user.is_staff_or_above():
            # Staff can see all pending referrals
            count = Referral.objects.filter(status='pending').count()
        elif getattr(user, 'user_type', '') == 'coordinator':
            # Coordinators see pending referrals from their chapter
            count = Referral.objects.filter(
                status='pending',
                chapter_id=getattr(user, 'chapter_id', '')
            ).count()
        else:
            # Regular users see their own pending referrals
            count = Referral.objects.filter(
                status='pending',
                owner=user
            ).count()
        
        cache.set(cache_key, count, 300)  # Cache for 5 minutes
    
    return count


@register.simple_tag
def has_dynamic_permission(user, permission_codename):
    """
    Check if user has a specific dynamic permission.
    
    Usage: {% has_dynamic_permission user 'manage_workflows' %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    from ..permissions import get_user_permissions
    
    permissions = get_user_permissions(user)
    return permission_codename in permissions


@register.simple_tag
def get_role_badge_color(user_type):
    """
    Get the color for a role badge.
    
    Usage: {% get_role_badge_color 'admin' %}
    """
    colors = {
        'mp': 'bg-blue-600',
        'chief_of_staff': 'bg-purple-600',
        'admin': 'bg-red-600',
        'coordinator': 'bg-green-600',
        'info_officer': 'bg-orange-600',
        'chapter_member': 'bg-cyan-600',
        'registered_user': 'bg-gray-600',
        # Legacy
        'staff': 'bg-red-600',
        'member': 'bg-cyan-600',
        'constituent': 'bg-gray-600',
    }
    return colors.get(user_type, 'bg-gray-400')


@register.simple_tag
def get_user_role_icon(user_type):
    """
    Get the Font Awesome icon for a user role.
    
    Usage: {% get_user_role_icon 'admin' %}
    """
    icons = {
        'mp': 'fas fa-crown',
        'chief_of_staff': 'fas fa-user-tie',
        'admin': 'fas fa-user-shield',
        'coordinator': 'fas fa-users-cog',
        'info_officer': 'fas fa-bullhorn',
        'chapter_member': 'fas fa-user-check',
        'registered_user': 'fas fa-user',
        # Legacy
        'staff': 'fas fa-user-shield',
        'member': 'fas fa-user-check',
        'constituent': 'fas fa-user',
    }
    return icons.get(user_type, 'fas fa-user')


@register.inclusion_tag('components/users/role_badge.html')
def role_badge(user, show_icon=True, size='md'):
    """
    Display a user's role as a styled badge.
    
    Usage: {% role_badge user show_icon=True size='lg' %}
    """
    if isinstance(user, AnonymousUser):
        return {
            'role_display': 'Guest',
            'role_color': 'bg-gray-400',
            'role_icon': 'fas fa-user-slash',
            'show_icon': show_icon,
            'size': size,
        }
    
    user_type = getattr(user, 'user_type', '')
    
    return {
        'role_display': user_role_display(user),
        'role_color': get_role_badge_color(user_type),
        'role_icon': get_user_role_icon(user_type),
        'show_icon': show_icon,
        'size': size,
    }


@register.simple_tag
def can_assign_role(user, target_role):
    """
    Check if user can assign a specific role to others.
    
    Usage: {% can_assign_role user 'coordinator' %}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    # Only Chief of Staff can assign roles
    return user.user_type == 'chief_of_staff'


@register.simple_tag
def get_available_actions(user, context_type, obj=None):
    """
    Get available actions for a user in a specific context.
    
    Usage: {% get_available_actions user 'referral' referral_obj as actions %}
    """
    if isinstance(user, AnonymousUser):
        return []
    
    actions = []
    
    if context_type == 'referral':
        if has_feature_access(user, 'referral_management'):
            actions.extend(['view', 'edit', 'update_status', 'add_comment'])
            if user.user_type in ['admin', 'chief_of_staff']:
                actions.extend(['delete', 'reassign'])
        elif obj and hasattr(obj, 'owner') and obj.owner == user:
            actions.extend(['view', 'add_comment'])
            if getattr(obj, 'status', '') in ['pending', 'submitted']:
                actions.append('edit')
    
    elif context_type == 'user_management':
        if user.user_type in ['admin', 'chief_of_staff']:
            actions.extend(['view_all', 'create', 'edit', 'activate', 'deactivate'])
            if user.user_type == 'chief_of_staff':
                actions.extend(['assign_role', 'delete'])
    
    elif context_type == 'announcement':
        if user.user_type in ['info_officer', 'admin', 'chief_of_staff']:
            actions.extend(['create', 'edit', 'publish', 'unpublish', 'delete'])
        else:
            actions.append('view')
    
    return actions