from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Staff(models.Model):
    """
    Staff profile information that maps to Notion Staff Profiles database.
    """
    
    EMPLOYMENT_STATUS_CHOICES = (
        ('coterminous', 'Coterminous'),
        ('contractual', 'Contractual'),
        ('consultant', 'Consultant'),
        ('intern', 'Intern'),
        ('volunteer', 'Volunteer'),
    )
    
    DIVISION_CHOICES = (
        ('legislative_affairs', 'Legislative Affairs'),
        ('administrative_affairs', 'Administrative Affairs'),
        ('communications', 'Communications'),
        ('mp_office', "MP Uy-Oyod's Office"),
        ('it_unit', 'IT Unit'),
    )
    
    OFFICE_CHOICES = (
        ('main_office', 'Main Office'),
        ('satellite_office', 'Satellite Office'),
    )
    
    # Basic Information
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        null=True,
        blank=True,
        help_text="Associated user account (optional for external staff)"
    )
    full_name = models.CharField(max_length=255, help_text="Full name as it appears in Notion")
    position = models.CharField(max_length=255, blank=True, help_text="Position/Designation")
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    
    # Organizational Information
    division = models.CharField(max_length=30, choices=DIVISION_CHOICES, blank=True)
    office = models.CharField(max_length=20, choices=OFFICE_CHOICES, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True)
    date_hired = models.DateField(null=True, blank=True, help_text="Date Hired/Engaged")
    
    # Role and Responsibilities
    duties_responsibilities = models.TextField(blank=True)
    staff_workflow = models.TextField(blank=True, help_text="Daily workflow and tasks")
    
    # Profile and Status
    is_active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['full_name']
    
    
    def __str__(self):
        return f"{self.full_name} - {self.position or 'Staff'}"
    
    def get_absolute_url(self):
        return reverse('staff:staff_detail', args=[self.pk])
    
    @property
    def display_name(self):
        """Return the display name for the staff member."""
        if self.user:
            return self.user.get_full_name() or self.full_name
        return self.full_name
    
    @property
    def has_user_account(self):
        """Check if staff member has an associated user account."""
        return self.user is not None


class StaffSupervisor(models.Model):
    """
    Supervisor relationship between staff members.
    """
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='supervisors'
    )
    supervisor = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='supervised_staff'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['staff', 'supervisor']
        verbose_name = "Staff Supervisor Relationship"
        verbose_name_plural = "Staff Supervisor Relationships"
    
    def __str__(self):
        return f"{self.supervisor.full_name} supervises {self.staff.full_name}"


class StaffTeam(models.Model):
    """
    Team structure for organizing staff members.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    team_lead = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    members = models.ManyToManyField(
        Staff,
        related_name='teams',
        blank=True
    )
    division = models.CharField(max_length=30, choices=Staff.DIVISION_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('staff:team_detail', args=[self.pk])


class StaffAttendance(models.Model):
    """
    Track staff attendance and work hours.
    """
    ATTENDANCE_STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('sick_leave', 'Sick Leave'),
        ('vacation_leave', 'Vacation Leave'),
        ('official_business', 'Official Business'),
        ('holiday', 'Holiday'),
    )
    
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES)
    notes = models.TextField(blank=True)
    
    # Approved by supervisor
    approved_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance'
    )
    is_approved = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.date} ({self.status})"
    
    @property
    def hours_worked(self):
        """Calculate hours worked for the day."""
        if self.time_in and self.time_out:
            from datetime import datetime, timedelta
            time_in = datetime.combine(self.date, self.time_in)
            time_out = datetime.combine(self.date, self.time_out)
            if time_out < time_in:  # Next day
                time_out += timedelta(days=1)
            return (time_out - time_in).total_seconds() / 3600
        return 0


class StaffPerformance(models.Model):
    """
    Performance evaluation records for staff members.
    """
    EVALUATION_PERIOD_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    )
    
    PERFORMANCE_RATING_CHOICES = (
        (5, 'Outstanding'),
        (4, 'Very Good'),
        (3, 'Good'),
        (2, 'Needs Improvement'),
        (1, 'Poor'),
    )
    
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='performance_records'
    )
    evaluation_period = models.CharField(max_length=20, choices=EVALUATION_PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Performance Metrics
    overall_rating = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES)
    quality_of_work = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES, null=True, blank=True)
    punctuality = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES, null=True, blank=True)
    teamwork = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES, null=True, blank=True)
    communication = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES, null=True, blank=True)
    initiative = models.PositiveSmallIntegerField(choices=PERFORMANCE_RATING_CHOICES, null=True, blank=True)
    
    # Comments and Goals
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals_next_period = models.TextField(blank=True)
    evaluator_comments = models.TextField(blank=True)
    
    # Evaluator Information
    evaluated_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_evaluations'
    )
    evaluation_date = models.DateField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'evaluation_period', 'period_start', 'period_end']
        ordering = ['-evaluation_date']
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.evaluation_period} ({self.period_start} to {self.period_end})"


class TaskCategory(models.Model):
    """
    Categories for organizing staff tasks.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code for category")
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Task Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Task management for staff members - individual tasks with priorities, deadlines, and tracking.
    """
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Task title or summary")
    description = models.TextField(blank=True, help_text="Detailed task description")
    
    # Assignment and Organization
    assigned_to = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text="Staff member assigned to this task"
    )
    assigned_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        help_text="Staff member who assigned this task"
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Task Properties
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Dates and Timing
    due_date = models.DateTimeField(null=True, blank=True, help_text="Task deadline")
    start_date = models.DateTimeField(null=True, blank=True, help_text="When task should start")
    completed_date = models.DateTimeField(null=True, blank=True, help_text="When task was completed")
    
    # Progress and Effort
    estimated_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Estimated hours to complete"
    )
    actual_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Actual hours spent on task"
    )
    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        help_text="Progress percentage (0-100)"
    )
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Additional notes or updates")
    attachments = models.FileField(
        upload_to='task_attachments/',
        null=True,
        blank=True,
        help_text="Task-related files"
    )
    
    # Dependencies
    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_tasks',
        help_text="Tasks that must be completed before this one"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.assigned_to.full_name} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """Calculate days until due date."""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def can_start(self):
        """Check if all dependencies are completed."""
        return not self.depends_on.exclude(status='completed').exists()
    
    def mark_completed(self):
        """Mark task as completed and set completion date."""
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.progress_percentage = 100
        self.save()


class TaskComment(models.Model):
    """
    Comments and updates on tasks for collaboration and tracking.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    comment = models.TextField(help_text="Comment or update text")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.task.title}"


class TaskTimeLog(models.Model):
    """
    Time tracking for tasks - log time spent working on specific tasks.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    
    # Time Information
    start_time = models.DateTimeField(help_text="When work started")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When work ended")
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Duration in hours (calculated automatically)"
    )
    
    # Work Description
    description = models.TextField(blank=True, help_text="What was worked on during this time")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.task.title} ({self.duration_hours}h)"
    
    def save(self, *args, **kwargs):
        """Calculate duration when end_time is set."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_hours = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)


class StaffWorkflowTemplate(models.Model):
    """
    Template for recurring tasks based on staff workflows from CSV data.
    """
    name = models.CharField(max_length=255, help_text="Template name")
    description = models.TextField(blank=True)
    division = models.CharField(max_length=30, choices=Staff.DIVISION_CHOICES, blank=True)
    position = models.CharField(max_length=255, blank=True, help_text="Specific position this applies to")
    
    # Template Settings
    is_active = models.BooleanField(default=True)
    auto_assign = models.BooleanField(default=False, help_text="Automatically assign to matching staff")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WorkflowTask(models.Model):
    """
    Individual task within a workflow template.
    """
    workflow = models.ForeignKey(
        StaffWorkflowTemplate,
        on_delete=models.CASCADE,
        related_name='workflow_tasks'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Task.PRIORITY_CHOICES, default='medium')
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Sequence and dependencies
    order = models.PositiveSmallIntegerField(default=0, help_text="Order within workflow")
    depends_on_previous = models.BooleanField(default=False, help_text="Must wait for previous task")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['workflow', 'order']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.title}"