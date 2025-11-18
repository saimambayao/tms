from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import User, DynamicPermission, RolePermission, UserPermissionOverride, RoleTransitionLog
from .permissions import assign_user_to_role_group
import datetime


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Enhanced custom admin for User model with RBAC support.
    """
    list_display = (
        'username', 'email', 'get_full_name', 'user_type_badge', 
        'is_approved', 'chapter_info', 'mfa_status', 'last_login_info'
    )
    list_filter = ('user_type', 'is_approved', 'is_staff', 'is_active', 'mfa_enabled', 'chapter_id')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'municipality', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'role_assigned_at', 'role_assigned_by', 'last_permission_check')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'address', 'municipality')
        }),
        ('Role & Access Control', {
            'fields': ('user_type', 'is_approved', 'chapter_id', 'role_assigned_at', 'role_assigned_by'),
            'classes': ('wide',)
        }),
        ('Security', {
            'fields': ('mfa_enabled', 'mfa_secret', 'mfa_backup_codes', 'last_permission_check'),
            'classes': ('collapse',)
        }),
        ('System Integration', {
            'fields': ('notion_id',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'phone_number', 'address', 'municipality')
        }),
        ('Role & Access Control', {
            'fields': ('user_type', 'is_approved', 'chapter_id')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    actions = ['approve_users', 'assign_to_role_groups', 'enable_mfa', 'disable_mfa']
    
    def get_full_name(self, obj):
        """Display full name with middle name."""
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return ' '.join(part for part in parts if part)
    get_full_name.short_description = 'Full Name'
    
    def user_type_badge(self, obj):
        """Display user type as a colored badge."""
        colors = {
            'mp': '#2563eb',  # Blue
            'chief_of_staff': '#7c3aed',  # Purple
            'admin': '#dc2626',  # Red
            'coordinator': '#16a34a',  # Green
            'info_officer': '#ea580c',  # Orange
            'chapter_member': '#0891b2',  # Cyan
            'registered_user': '#64748b',  # Gray
            # Legacy
            'staff': '#dc2626',
            'member': '#0891b2',
            'constituent': '#64748b',
        }
        color = colors.get(obj.user_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'Role'
    
    def chapter_info(self, obj):
        """Display chapter information."""
        if obj.chapter_id:
            return format_html('<span title="Chapter ID: {}">{}</span>', obj.chapter_id, obj.chapter_id[:8])
        return '-'
    chapter_info.short_description = 'Chapter'
    
    def mfa_status(self, obj):
        """Display MFA status."""
        if obj.mfa_enabled:
            return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: gray;">✗ Disabled</span>')
    mfa_status.short_description = 'MFA'
    
    def last_login_info(self, obj):
        """Display last login information."""
        if obj.last_login:
            delta = datetime.datetime.now(obj.last_login.tzinfo) - obj.last_login
            if delta.days == 0:
                return format_html('<span style="color: green;">Today</span>')
            elif delta.days == 1:
                return format_html('<span style="color: green;">Yesterday</span>')
            elif delta.days < 7:
                return format_html('<span style="color: orange;">{} days ago</span>', delta.days)
            else:
                return format_html('<span style="color: red;">{} days ago</span>', delta.days)
        return '-'
    last_login_info.short_description = 'Last Login'
    
    def approve_users(self, request, queryset):
        """Bulk approve users."""
        count = queryset.filter(is_approved=False).update(is_approved=True)
        self.message_user(request, f'{count} users approved successfully.', messages.SUCCESS)
    approve_users.short_description = 'Approve selected users'
    
    def assign_to_role_groups(self, request, queryset):
        """Assign users to their appropriate role groups."""
        for user in queryset:
            assign_user_to_role_group(user)
        self.message_user(
            request, 
            f'{queryset.count()} users assigned to role groups.', 
            messages.SUCCESS
        )
    assign_to_role_groups.short_description = 'Assign to role groups'
    
    def enable_mfa(self, request, queryset):
        """Enable MFA requirement for selected users."""
        count = queryset.update(mfa_enabled=True)
        self.message_user(request, f'MFA enabled for {count} users.', messages.SUCCESS)
    enable_mfa.short_description = 'Enable MFA'
    
    def disable_mfa(self, request, queryset):
        """Disable MFA for selected users."""
        count = queryset.update(mfa_enabled=False, mfa_secret='')
        self.message_user(request, f'MFA disabled for {count} users.', messages.SUCCESS)
    disable_mfa.short_description = 'Disable MFA'
    
    def save_model(self, request, obj, form, change):
        """Override save to handle role assignments."""
        if change and 'user_type' in form.changed_data:
            obj.role_assigned_at = datetime.datetime.now()
            obj.role_assigned_by = request.user
            # Log role transition
            RoleTransitionLog.objects.create(
                user=obj,
                from_role=form.initial.get('user_type'),
                to_role=obj.user_type,
                reason=f"Changed via admin by {request.user.username}",
                changed_by=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
        super().save_model(request, obj, form, change)
        # Assign to role group
        assign_user_to_role_group(obj)


@admin.register(DynamicPermission)
class DynamicPermissionAdmin(admin.ModelAdmin):
    """Admin for managing dynamic permissions."""
    list_display = ('name', 'codename', 'module', 'is_active', 'roles_count')
    list_filter = ('module', 'is_active', 'created_at')
    search_fields = ('name', 'codename', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'codename', 'module', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def roles_count(self, obj):
        """Display count of roles with this permission."""
        count = obj.rolepermission_set.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:users_rolepermission_changelist') + f'?permission__id__exact={obj.id}'
            return format_html('<a href="{}">{} roles</a>', url, count)
        return '0 roles'
    roles_count.short_description = 'Assigned To'


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin for managing role-permission mappings."""
    list_display = ('role_badge', 'permission', 'is_active', 'can_delegate', 'created_at')
    list_filter = ('role', 'is_active', 'can_delegate', 'permission__module')
    search_fields = ('permission__name', 'permission__codename')
    readonly_fields = ('created_at', 'created_by')
    autocomplete_fields = ['permission']
    
    fieldsets = (
        (None, {
            'fields': ('role', 'permission')
        }),
        ('Settings', {
            'fields': ('is_active', 'can_delegate')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def role_badge(self, obj):
        """Display role as a colored badge."""
        colors = {
            'mp': '#2563eb',
            'chief_of_staff': '#7c3aed',
            'admin': '#dc2626',
            'coordinator': '#16a34a',
            'info_officer': '#ea580c',
            'chapter_member': '#0891b2',
            'registered_user': '#64748b',
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def save_model(self, request, obj, form, change):
        """Set created_by on save."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    """Admin for managing user permission overrides."""
    list_display = ('user', 'permission', 'is_granted_badge', 'is_active_status', 'expires_at', 'created_by')
    list_filter = ('is_granted', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'permission__name', 'reason')
    readonly_fields = ('created_at', 'created_by')
    autocomplete_fields = ['user', 'permission']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'permission', 'is_granted')
        }),
        ('Details', {
            'fields': ('reason', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def is_granted_badge(self, obj):
        """Display grant/revoke status as badge."""
        if obj.is_granted:
            return format_html(
                '<span style="background-color: #16a34a; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ GRANTED</span>'
            )
        return format_html(
            '<span style="background-color: #dc2626; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">✗ REVOKED</span>'
        )
    is_granted_badge.short_description = 'Status'
    
    def is_active_status(self, obj):
        """Display if override is currently active."""
        if obj.is_active():
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')
    is_active_status.short_description = 'Active'
    
    def save_model(self, request, obj, form, change):
        """Set created_by on save."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RoleTransitionLog)
class RoleTransitionLogAdmin(admin.ModelAdmin):
    """Admin for viewing role transition logs."""
    list_display = ('user', 'transition_info', 'changed_by', 'changed_at', 'ip_address')
    list_filter = ('from_role', 'to_role', 'changed_at')
    search_fields = ('user__username', 'user__email', 'reason', 'changed_by__username')
    readonly_fields = ('user', 'from_role', 'to_role', 'reason', 'changed_by', 'changed_at', 'ip_address')
    date_hierarchy = 'changed_at'
    
    def transition_info(self, obj):
        """Display role transition information."""
        if obj.from_role:
            return format_html(
                '{} → {}',
                obj.get_from_role_display() or 'None',
                obj.get_to_role_display()
            )
        return format_html('→ {}', obj.get_to_role_display())
    transition_info.short_description = 'Role Change'
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete logs."""
        return request.user.is_superuser