"""
Enhanced permission decorators for #FahanieCares RBAC system.
Provides convenient decorators for view-level access control.
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)


def require_role(*allowed_roles):
    """
    Decorator that checks if user has one of the required roles.
    Can be used with function-based views.
    
    Usage:
        @require_role('admin', 'chief_of_staff')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.user_type in allowed_roles:
                logger.info(
                    f"Access granted: User {request.user.username} ({request.user.user_type}) "
                    f"accessing {view_func.__name__}"
                )
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Access denied: User {request.user.username} ({request.user.user_type}) "
                f"attempted to access {view_func.__name__} requiring roles {allowed_roles}"
            )
            
            # Log the attempt
            from .models import RoleTransitionLog
            RoleTransitionLog.objects.create(
                user=request.user,
                from_role=request.user.user_type,
                to_role=request.user.user_type,
                reason=f"Access denied to {view_func.__name__} - requires roles: {', '.join(allowed_roles)}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.error(
                request,
                f"Access denied. This action requires one of the following roles: {', '.join(allowed_roles)}"
            )
            raise PermissionDenied
        
        return wrapped_view
    return decorator


def require_role_or_higher(minimum_role):
    """
    Decorator that checks if user has the minimum required role or higher.
    Uses the role hierarchy for permission checking.
    
    Usage:
        @require_role_or_higher('coordinator')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.has_role_permission(minimum_role):
                logger.info(
                    f"Access granted: User {request.user.username} ({request.user.user_type}) "
                    f"accessing {view_func.__name__} with minimum role {minimum_role}"
                )
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Access denied: User {request.user.username} ({request.user.user_type}) "
                f"attempted to access {view_func.__name__} requiring minimum role {minimum_role}"
            )
            
            messages.error(
                request,
                f"Access denied. This action requires {minimum_role} role or higher."
            )
            raise PermissionDenied
        
        return wrapped_view
    return decorator


def require_feature(feature_name):
    """
    Decorator that checks if user has access to a specific feature.
    
    Usage:
        @require_feature('referral_management')
        def manage_referrals(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            from .permissions import HasFeatureAccess
            
            # Create a mock view to check permissions
            class MockView:
                required_feature = feature_name
            
            permission = HasFeatureAccess()
            if permission.has_permission(request, MockView()):
                logger.info(
                    f"Feature access granted: User {request.user.username} "
                    f"accessing {feature_name}"
                )
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Feature access denied: User {request.user.username} "
                f"attempted to access {feature_name}"
            )
            
            messages.error(
                request,
                f"Access denied. You don't have access to the {feature_name} feature."
            )
            raise PermissionDenied
        
        return wrapped_view
    return decorator


def require_dynamic_permission(permission_codename):
    """
    Decorator that checks for dynamic permissions from the database.
    
    Usage:
        @require_dynamic_permission('approve_high_value_referral')
        def approve_referral(request, referral_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            from .permissions import get_user_permissions
            
            user_permissions = get_user_permissions(request.user)
            if permission_codename in user_permissions:
                logger.info(
                    f"Dynamic permission granted: User {request.user.username} "
                    f"has permission {permission_codename}"
                )
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Dynamic permission denied: User {request.user.username} "
                f"lacks permission {permission_codename}"
            )
            
            messages.error(
                request,
                f"Access denied. You don't have the required permission: {permission_codename}"
            )
            raise PermissionDenied
        
        return wrapped_view
    return decorator


def require_own_object_or_role(owner_field='user', allowed_roles=None):
    """
    Decorator that allows access if user owns the object or has specified roles.
    
    Usage:
        @require_own_object_or_role(owner_field='created_by', allowed_roles=['admin', 'coordinator'])
        def edit_referral(request, referral_id):
            referral = get_object_or_404(Referral, id=referral_id)
            ...
    """
    if allowed_roles is None:
        allowed_roles = ['admin', 'chief_of_staff']
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # First check if user has an allowed role
            if request.user.user_type in allowed_roles:
                logger.info(
                    f"Object access granted via role: User {request.user.username} "
                    f"has role {request.user.user_type}"
                )
                return view_func(request, *args, **kwargs)
            
            # If not, the view must handle ownership check
            # This is a partial check - the view needs to verify ownership
            logger.info(
                f"Object access check: User {request.user.username} "
                f"must verify ownership in view {view_func.__name__}"
            )
            
            # Add a flag to request to indicate ownership check is needed
            request.check_object_ownership = True
            request.owner_field = owner_field
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def require_chapter_access():
    """
    Decorator that checks if user has access to chapter-related functionality.
    
    Usage:
        @require_chapter_access()
        def chapter_view(request, chapter_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Staff and above have access to all chapters
            if request.user.is_staff_or_above():
                return view_func(request, *args, **kwargs)
            
            # Chapter members can only access their own chapter
            if request.user.chapter_id:
                # Add chapter_id to request for validation in view
                request.user_chapter_id = request.user.chapter_id
                return view_func(request, *args, **kwargs)
            
            messages.error(
                request,
                "Access denied. You must be a chapter member to access this feature."
            )
            raise PermissionDenied
        
        return wrapped_view
    return decorator


# Method decorators for class-based views
method_require_role = method_decorator(require_role)
method_require_role_or_higher = method_decorator(require_role_or_higher)
method_require_feature = method_decorator(require_feature)
method_require_dynamic_permission = method_decorator(require_dynamic_permission)
method_require_chapter_access = method_decorator(require_chapter_access)


class RoleRequiredMixin:
    """
    Mixin for class-based views to require specific roles.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            required_roles = ['admin', 'chief_of_staff']
            ...
    """
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        if not self.required_roles:
            raise ValueError("required_roles must be set")
        
        if request.user.user_type not in self.required_roles:
            logger.warning(
                f"Access denied: User {request.user.username} ({request.user.user_type}) "
                f"attempted to access {self.__class__.__name__} requiring roles {self.required_roles}"
            )
            messages.error(
                request,
                f"Access denied. This action requires one of the following roles: {', '.join(self.required_roles)}"
            )
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)


class RoleOrHigherRequiredMixin:
    """
    Mixin for class-based views to require minimum role level.
    
    Usage:
        class MyView(RoleOrHigherRequiredMixin, View):
            minimum_role = 'coordinator'
            ...
    """
    minimum_role = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        if not self.minimum_role:
            raise ValueError("minimum_role must be set")
        
        if not request.user.has_role_permission(self.minimum_role):
            logger.warning(
                f"Access denied: User {request.user.username} ({request.user.user_type}) "
                f"attempted to access {self.__class__.__name__} requiring minimum role {self.minimum_role}"
            )
            messages.error(
                request,
                f"Access denied. This action requires {self.minimum_role} role or higher."
            )
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)


class FeatureRequiredMixin:
    """
    Mixin for class-based views to require feature access.
    
    Usage:
        class ReferralManagementView(FeatureRequiredMixin, View):
            required_feature = 'referral_management'
            ...
    """
    required_feature = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        if not self.required_feature:
            raise ValueError("required_feature must be set")
        
        from .permissions import HasFeatureAccess
        
        permission = HasFeatureAccess()
        if not permission.has_permission(request, self):
            logger.warning(
                f"Feature access denied: User {request.user.username} "
                f"attempted to access {self.required_feature}"
            )
            messages.error(
                request,
                f"Access denied. You don't have access to the {self.required_feature} feature."
            )
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)