from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin interface for managing announcements/latest updates
    """
    list_display = ['title', 'category_badge', 'status_badge', 'is_featured', 'published_date', 'created_by']
    list_filter = ['category', 'status', 'is_featured', 'published_date', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    list_editable = ['is_featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'image')
        }),
        ('Publishing', {
            'fields': ('category', 'status', 'is_featured', 'published_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def category_badge(self, obj):
        """Display category with colored badge"""
        colors = {
            'news': '#3b82f6',
            'event': '#f97316', 
            'parliament': '#10b981',
            'program': '#22c55e',
            'update': '#6b7280',
        }
        color = colors.get(obj.category, '#22c55e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'draft': '#6b7280',
            'published': '#10b981',
            'archived': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Automatically set created_by when creating new announcements"""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
