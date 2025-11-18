from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.cache import cache
from django.utils import timezone

class User(AbstractUser):
    """
    Enhanced custom user model for #FahanieCares application with comprehensive RBAC support.
    Extends Django's built-in AbstractUser to add custom fields and role-based access control.
    """
    USER_TYPES = (
        ('superuser', 'Superuser'),
        ('mp', 'Member of Parliament'),
        ('chief_of_staff', 'Chief of Staff'),
        ('staff', 'Parliamentary Office Staff'),
        ('admin', 'System Administrator'),
        ('coordinator', 'Coordinator'),
        ('info_officer', 'Information Officer'),
        ('chapter_member', 'Chapter Member'),
        ('registered_user', 'Registered User'),
        ('constituent', 'Constituent'),  # Legacy support
        ('member', 'Member'),  # Legacy support
    )
    
    # Role hierarchy for permission inheritance (1-10 scale, higher = more permissions)
    # Staff-based hierarchy: Staff is base level for parliamentary workers
    ROLE_HIERARCHY = {
        'superuser': 10,       # Ultimate access to everything
        'mp': 9,               # Strategic oversight and executive access
        'chief_of_staff': 8,   # Operational leadership and role management
        'admin': 7,            # Staff + Full portal management access
        'coordinator': 6,      # Staff + Service management access  
        'info_officer': 5,     # Staff + Communication management access
        'staff': 4,            # Base parliamentary staff (task/calendar + profile)
        'chapter_member': 3,   # Chapter activities and services
        'registered_user': 2,  # Basic profile and service access
        # Legacy mappings
        'constituent': 2,      # Map to registered_user level
        'member': 3,           # Map to chapter_member level
    }
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='registered_user')
    middle_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    chapter_id = models.CharField(max_length=50, blank=True)
    is_approved = models.BooleanField(default=False)
    
    # MFA Settings
    MFA_METHOD_CHOICES = (
        ('totp', 'Authenticator App (TOTP)'),
        ('sms', 'SMS/Text Message'),
    )
    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(max_length=10, choices=MFA_METHOD_CHOICES, default='totp', help_text="Preferred MFA method")
    mfa_secret = models.CharField(max_length=32, blank=True, help_text="TOTP secret for MFA")
    mfa_backup_codes = models.TextField(blank=True, help_text="Comma-separated backup codes")
    
    # SMS OTP Fields
    phone_verified = models.BooleanField(default=False, help_text="Is phone number verified for SMS OTP")
    sms_otp_secret = models.CharField(max_length=6, blank=True, help_text="Temporary SMS OTP")
    sms_otp_expires = models.DateTimeField(null=True, blank=True, help_text="SMS OTP expiration time")
    
    # Additional RBAC fields
    role_assigned_at = models.DateTimeField(null=True, blank=True)
    role_assigned_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_roles')
    last_permission_check = models.DateTimeField(null=True, blank=True)
    
    def get_role_hierarchy_level(self):
        """Get the numerical hierarchy level of the user's role."""
        return self.ROLE_HIERARCHY.get(self.user_type, 1)
    
    def has_role_permission(self, required_role):
        """Check if user has permission based on role hierarchy."""
        user_level = self.get_role_hierarchy_level()
        required_level = self.ROLE_HIERARCHY.get(required_role, 999)
        return user_level >= required_level
    
    def is_superuser_role(self):
        """Check if user is a Superuser."""
        return self.user_type == 'superuser'
    
    def is_mp(self):
        """Check if user is the Member of Parliament."""
        return self.user_type == 'mp'
    
    def is_chief_of_staff(self):
        """Check if user is Chief of Staff."""
        return self.user_type == 'chief_of_staff'
    
    def is_staff_role(self):
        """Check if user is Parliamentary Office Staff."""
        return self.user_type == 'staff'
    
    def is_admin(self):
        """Check if user is System Administrator."""
        return self.user_type == 'admin'
    
    def is_coordinator(self):
        """Check if user is a Coordinator."""
        return self.user_type == 'coordinator'
    
    def is_info_officer(self):
        """Check if user is an Information Officer."""
        return self.user_type == 'info_officer'
    
    def is_chapter_member_role(self):
        """Check if user is a Chapter Member."""
        return self.user_type in ['chapter_member', 'member']  # Include legacy member
    
    def is_registered_user_role(self):
        """Check if user is a Registered User."""
        return self.user_type in ['registered_user', 'constituent']  # Include legacy constituent
    
    # Legacy support methods (maintain backward compatibility)
    def is_staff_or_above(self):
        """Legacy: Check if user is staff or above (including coordinator)."""
        return self.has_role_permission('coordinator') # Changed from 'admin' to 'coordinator'
    
    def is_coordinator_or_above(self):
        """Legacy: Check if user is a coordinator, staff, or MP."""
        return self.has_role_permission('coordinator')
    
    def is_member_or_above(self):
        """Legacy: Check if user is a registered member or higher role."""
        return self.has_role_permission('chapter_member')
    
    def get_permissions_cache_key(self):
        """Generate cache key for user's permissions."""
        return f"user_permissions_{self.id}_{self.user_type}"
    
    def clear_permissions_cache(self):
        """Clear cached permissions for this user."""
        cache.delete(self.get_permissions_cache_key())
    
    def update_last_permission_check(self):
        """Update the timestamp of last permission check."""
        self.last_permission_check = timezone.now()
        self.save(update_fields=['last_permission_check'])
    
    def __str__(self):
        return self.username
    
    class Meta:
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['chapter_id']),
            models.Index(fields=['is_approved']),
        ]


class DynamicPermission(models.Model):
    """
    Dynamic permissions that can be created and managed at runtime.
    Supplements Django's built-in permission system.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Human-readable permission name")
    codename = models.CharField(max_length=100, unique=True, help_text="Programmatic permission identifier")
    description = models.TextField(help_text="Detailed description of what this permission allows")
    module = models.CharField(max_length=50, help_text="Module this permission belongs to")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['module', 'name']
        indexes = [
            models.Index(fields=['codename']),
            models.Index(fields=['module']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.module}.{self.codename}"


class RolePermission(models.Model):
    """
    Maps roles to their permissions, enabling role-based access control.
    """
    role = models.CharField(max_length=20, choices=User.USER_TYPES)
    permission = models.ForeignKey(DynamicPermission, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    can_delegate = models.BooleanField(default=False, help_text="Can this role delegate this permission to others?")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission__module', 'permission__name']
        indexes = [
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.permission}"


class UserPermissionOverride(models.Model):
    """
    Allows granting or revoking specific permissions for individual users,
    overriding their role-based permissions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_overrides')
    permission = models.ForeignKey(DynamicPermission, on_delete=models.CASCADE)
    is_granted = models.BooleanField(default=True, help_text="True to grant, False to revoke")
    reason = models.TextField(help_text="Reason for this override")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this override expires")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permission_overrides_created')
    
    class Meta:
        unique_together = ['user', 'permission']
        indexes = [
            models.Index(fields=['user', 'is_granted']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_active(self):
        """Check if this override is currently active."""
        if not self.expires_at:
            return True
        return timezone.now() < self.expires_at
    
    def __str__(self):
        action = "grants" if self.is_granted else "revokes"
        return f"Override {action} {self.permission} for {self.user}"


class RoleTransitionLog(models.Model):
    """
    Audit log for tracking role changes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_transitions')
    from_role = models.CharField(max_length=20, choices=User.USER_TYPES, null=True, blank=True)
    to_role = models.CharField(max_length=20, choices=User.USER_TYPES)
    reason = models.TextField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_changes_made')
    changed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['user', '-changed_at']),
            models.Index(fields=['changed_by', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.user} role changed from {self.from_role} to {self.to_role}"
