from django.contrib import admin
from .models import GeneralDatabase, DatabaseEntry, DatabaseField, PersonLink


@admin.register(GeneralDatabase)
class GeneralDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'database_type', 'is_active', 'created_at', 'entry_count']
    list_filter = ['database_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    filter_horizontal = ['allowed_users']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'database_type', 'slug')
        }),
        ('Hierarchy', {
            'fields': ('parent_database',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'is_public', 'allow_self_registration')
        }),
        ('Access Control', {
            'fields': ('allowed_roles', 'allowed_users'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def entry_count(self, obj):
        return obj.entries.count()
    entry_count.short_description = 'Entries'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            entry_count=models.Count('entries')
        )


@admin.register(DatabaseField)
class DatabaseFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'name', 'field_type', 'database', 'is_required', 'order']
    list_filter = ['field_type', 'is_required', 'is_searchable', 'is_filterable']
    search_fields = ['name', 'label', 'database__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('database', 'name', 'label', 'field_type')
        }),
        ('Configuration', {
            'fields': ('is_required', 'is_searchable', 'is_filterable', 'order')
        }),
        ('Field Settings', {
            'fields': ('default_value', 'placeholder', 'help_text'),
            'classes': ('collapse',)
        }),
        ('Options (for select fields)', {
            'fields': ('options',),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('validation_type', 'validation_rules'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DatabaseEntry)
class DatabaseEntryAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'database', 'status', 'created_at', 'created_by']
    list_filter = ['status', 'database', 'created_at']
    search_fields = ['guest_first_name', 'guest_last_name', 'guest_email', 'guest_phone', 'search_text']
    readonly_fields = ['created_at', 'updated_at', 'search_text']
    fieldsets = (
        ('Basic Information', {
            'fields': ('database', 'status', 'linked_user')
        }),
        ('Guest Information', {
            'fields': ('guest_first_name', 'guest_middle_name', 'guest_last_name', 'guest_email', 'guest_phone')
        }),
        ('Entry Data', {
            'fields': ('entry_data',),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'search_text'),
            'classes': ('collapse',)
        }),
    )
    raw_id_fields = ['linked_user', 'approved_by', 'created_by']
    list_per_page = 50

    def get_full_name(self, obj):
        if obj.linked_user:
            return obj.linked_user.get_full_name()
        elif obj.guest_first_name or obj.guest_last_name:
            return obj.get_full_name()
        else:
            # Try to get name from entry_data
            for key, value in obj.entry_data.items():
                if key.lower() in ['first_name', 'firstname', 'first', 'name'] and value:
                    first_name = str(value).strip()
                    last_name = ''
                    for k2, v2 in obj.entry_data.items():
                        if k2.lower() in ['last_name', 'lastname', 'last', 'surname'] and v2:
                            last_name = str(v2).strip()
                            break
                    return f"{first_name} {last_name}".strip() if last_name else first_name
                elif key.lower() in ['last_name', 'lastname', 'last', 'surname'] and value and not obj.guest_first_name:
                    return str(value).strip()
            return "Guest User"
    get_full_name.short_description = 'Name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('database', 'linked_user', 'created_by')


@admin.register(PersonLink)
class PersonLinkAdmin(admin.ModelAdmin):
    list_display = ['primary_name', 'confidence_score', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['primary_name', 'normalized_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('primary_name', 'normalized_name', 'confidence_score')
        }),
        ('Linked Records', {
            'fields': ('fahanie_cares_member', 'constituent', 'database_entries')
        }),
        ('External Links', {
            'fields': ('external_id', 'external_system'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ['database_entries']
    raw_id_fields = ['fahanie_cares_member', 'constituent', 'verified_by']


# Import here to avoid circular imports
from django.db import models
