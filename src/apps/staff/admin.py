from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Staff, StaffSupervisor, StaffTeam, StaffAttendance, StaffPerformance,
    TaskCategory, Task, TaskComment, TaskTimeLog, StaffWorkflowTemplate, WorkflowTask
)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'position', 'division', 'employment_status', 
        'office', 'is_active', 'has_user_account_display', 'date_hired'
    ]
    list_filter = [
        'division', 'employment_status', 'office', 'is_active', 'date_hired'
    ]
    search_fields = ['full_name', 'position', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'full_name', 'position', 'profile_image', 'bio')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Organizational Information', {
            'fields': ('division', 'office', 'employment_status', 'date_hired')
        }),
        ('Role and Responsibilities', {
            'fields': ('duties_responsibilities', 'staff_workflow')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_user_account_display(self, obj):
        if obj.has_user_account:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_user_account_display.short_description = 'Has User Account'
    has_user_account_display.allow_tags = True


@admin.register(StaffSupervisor)
class StaffSupervisorAdmin(admin.ModelAdmin):
    list_display = ['staff', 'supervisor', 'created_at']
    list_filter = ['supervisor__division', 'created_at']
    search_fields = ['staff__full_name', 'supervisor__full_name']
    autocomplete_fields = ['staff', 'supervisor']


@admin.register(StaffTeam)
class StaffTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_lead', 'division', 'member_count', 'is_active']
    list_filter = ['division', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'description', 'team_lead', 'division')
        }),
        ('Members', {
            'fields': ('members',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'date', 'status', 'time_in', 'time_out', 
        'hours_worked_display', 'is_approved'
    ]
    list_filter = [
        'status', 'is_approved', 'date', 'staff__division'
    ]
    search_fields = ['staff__full_name', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'hours_worked_display']
    fieldsets = (
        ('Attendance Information', {
            'fields': ('staff', 'date', 'status')
        }),
        ('Time Tracking', {
            'fields': ('time_in', 'time_out', 'hours_worked_display')
        }),
        ('Notes and Approval', {
            'fields': ('notes', 'approved_by', 'is_approved')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def hours_worked_display(self, obj):
        hours = obj.hours_worked
        if hours > 0:
            return f"{hours:.2f} hours"
        return "Not calculated"
    hours_worked_display.short_description = 'Hours Worked'


@admin.register(StaffPerformance)
class StaffPerformanceAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'evaluation_period', 'period_start', 'period_end',
        'overall_rating_display', 'evaluated_by', 'evaluation_date'
    ]
    list_filter = [
        'evaluation_period', 'overall_rating', 'evaluation_date',
        'staff__division'
    ]
    search_fields = ['staff__full_name', 'evaluator_comments', 'strengths']
    date_hierarchy = 'evaluation_date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Evaluation Information', {
            'fields': ('staff', 'evaluation_period', 'period_start', 'period_end', 'evaluation_date', 'evaluated_by')
        }),
        ('Performance Ratings', {
            'fields': ('overall_rating', 'quality_of_work', 'punctuality', 'teamwork', 'communication', 'initiative')
        }),
        ('Comments and Goals', {
            'fields': ('strengths', 'areas_for_improvement', 'goals_next_period', 'evaluator_comments')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def overall_rating_display(self, obj):
        rating_colors = {
            5: 'green',
            4: 'lightgreen', 
            3: 'orange',
            2: 'red',
            1: 'darkred'
        }
        color = rating_colors.get(obj.overall_rating, 'black')
        rating_text = dict(obj.PERFORMANCE_RATING_CHOICES).get(obj.overall_rating, 'Unknown')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color, rating_text, obj.overall_rating
        )
    overall_rating_display.short_description = 'Overall Rating'
    overall_rating_display.allow_tags = True


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'task_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'
    color_display.allow_tags = True
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'assigned_to', 'priority_display', 'status_display', 
        'due_date', 'progress_percentage', 'is_overdue_display', 'created_at'
    ]
    list_filter = [
        'priority', 'status', 'category', 'assigned_to__division', 
        'due_date', 'created_at'
    ]
    search_fields = ['title', 'description', 'assigned_to__full_name', 'assigned_by__full_name']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue_display', 'days_until_due']
    autocomplete_fields = ['assigned_to', 'assigned_by', 'category']
    filter_horizontal = ['depends_on']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_by')
        }),
        ('Properties', {
            'fields': ('priority', 'status', 'progress_percentage')
        }),
        ('Timing', {
            'fields': ('start_date', 'due_date', 'completed_date', 'estimated_hours', 'actual_hours')
        }),
        ('Dependencies', {
            'fields': ('depends_on',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'attachments')
        }),
        ('Status Information', {
            'fields': ('is_overdue_display', 'days_until_due'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def priority_display(self, obj):
        priority_colors = {
            'low': '#6B7280',
            'medium': '#F59E0B', 
            'high': '#EF4444',
            'urgent': '#DC2626'
        }
        color = priority_colors.get(obj.priority, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    priority_display.allow_tags = True
    
    def status_display(self, obj):
        status_colors = {
            'pending': '#6B7280',
            'in_progress': '#3B82F6',
            'on_hold': '#F59E0B',
            'completed': '#10B981',
            'cancelled': '#EF4444'
        }
        color = status_colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.allow_tags = True
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">⚠ OVERDUE</span>')
        elif obj.days_until_due is not None and obj.days_until_due <= 3:
            return format_html('<span style="color: orange; font-weight: bold;">⏰ DUE SOON</span>')
        return format_html('<span style="color: green;">✓ On Track</span>')
    is_overdue_display.short_description = 'Due Status'
    is_overdue_display.allow_tags = True


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'comment_preview', 'created_at']
    list_filter = ['author__division', 'created_at']
    search_fields = ['task__title', 'author__full_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment Preview'


@admin.register(TaskTimeLog)
class TaskTimeLogAdmin(admin.ModelAdmin):
    list_display = [
        'task', 'staff', 'start_time', 'end_time', 
        'duration_hours', 'description_preview'
    ]
    list_filter = ['staff__division', 'start_time']
    search_fields = ['task__title', 'staff__full_name', 'description']
    readonly_fields = ['created_at', 'duration_hours']
    date_hierarchy = 'start_time'
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return 'No description'
    description_preview.short_description = 'Description'


@admin.register(StaffWorkflowTemplate)
class StaffWorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'division', 'position', 'task_count', 'auto_assign', 'is_active']
    list_filter = ['division', 'auto_assign', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'position']
    readonly_fields = ['created_at', 'updated_at']
    
    def task_count(self, obj):
        return obj.workflow_tasks.count()
    task_count.short_description = 'Tasks in Template'


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'title', 'order', 'priority', 'estimated_hours', 'depends_on_previous']
    list_filter = ['workflow', 'priority', 'depends_on_previous']
    search_fields = ['workflow__name', 'title', 'description']
    readonly_fields = ['created_at']
    ordering = ['workflow', 'order']