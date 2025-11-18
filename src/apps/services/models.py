from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError # Import ValidationError
from apps.constituents.member_models import FahanieCaresMember # Import FahanieCaresMember

class MinistryProgram(models.Model):
    """
    Ministry Programs, Projects & Activities (PPAs) with full administrative control.
    Supports CRUD operations, audit trails, and role-based management.
    """
    
    MINISTRIES = (
        ('mssd', 'Ministry of Social Services and Development'),
        ('mafar', 'Ministry of Agriculture, Fisheries and Agrarian Reform'),
        ('mtit', 'Ministry of Trade, Industry and Tourism'),
        ('mhe', 'Ministry of Higher Education'),
        ('mbasiced', 'Ministry of Basic, Higher and Technical Education'),
        ('moh', 'Ministry of Health'),
        ('mpwh', 'Ministry of Public Works and Highways'),
        ('motc', 'Ministry of Transportation and Communications'),
        ('mei', 'Ministry of Environment and Interior'),
        ('mle', 'Ministry of Labor and Employment'),
        ('mp_office', 'Office of MP Atty. Sittie Fahanie S. Uy-Oyod'),
        ('other', 'Other Ministry/Office'),
    )
    
    PPA_TYPES = (
        ('program', 'Program'),
        ('project', 'Project'),
        ('activity', 'Activity'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('archived', 'Archived'),
    )
    
    FUNDING_SOURCES = (
        ('national', 'National Government'),
        ('regional', 'Regional Government (BARMM)'),
        ('local', 'Local Government Unit'),
        ('international', 'International Donor'),
        ('private', 'Private Sector'),
        ('mixed', 'Mixed Sources'),
        ('office_mooe', 'Office MOOE'),
        ('implementing_ministry', 'Implementing Ministry'),
    )
    
    PROGRAM_SOURCES = (
        ('fahaniecares', '#FahanieCares Program'),
        ('tdif', 'TDIF Project'),
        ('ministry', 'Ministry Program'),
    )
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, help_text="Unique ministry program code")
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    ministry = models.CharField(max_length=20, choices=MINISTRIES)
    program_source = models.CharField(
        max_length=20, 
        choices=PROGRAM_SOURCES, 
        default='ministry',
        help_text="Source/category of this program"
    )
    ppa_type = models.CharField(max_length=20, choices=PPA_TYPES)
    
    # Detailed Description
    description = models.TextField(help_text="Comprehensive program description")
    objectives = models.TextField(help_text="Program objectives and goals")
    expected_outcomes = models.TextField(help_text="Expected outcomes and impacts")
    key_performance_indicators = models.TextField(help_text="KPIs for monitoring and evaluation")
    
    # Target Groups
    target_beneficiaries = models.TextField(help_text="Description of target beneficiaries")
    geographic_coverage = models.TextField(help_text="Geographic areas covered")
    estimated_beneficiaries = models.PositiveIntegerField(default=0)
    
    # Implementation Details
    implementation_strategy = models.TextField(help_text="How the program will be implemented")
    implementing_units = models.TextField(help_text="Responsible implementing units/offices")
    partner_agencies = models.TextField(blank=True, help_text="Partner agencies and organizations")
    
    # Financial Information
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    allocated_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    utilized_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    funding_source = models.CharField(max_length=30, choices=FUNDING_SOURCES)
    funding_details = models.TextField(blank=True, help_text="Detailed funding information")
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    duration_months = models.PositiveIntegerField(null=True, blank=True, help_text="Program duration in months")
    
    # Status and Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    PRIORITY_LEVELS = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Administrative Control
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_ministry_programs'
    )
    ministry_liaison = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='liaised_programs',
        help_text="Ministry liaison officer responsible for this program"
    )
    program_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_programs'
    )
    
    # Access Control
    is_public = models.BooleanField(default=True, help_text="Whether program is visible to public")
    is_featured = models.BooleanField(default=False, help_text="Featured program on homepage")
    requires_approval = models.BooleanField(default=True, help_text="Changes require approval")
    
    # Documentation
    program_document = models.FileField(upload_to='ministry_programs/documents/', blank=True, null=True)
    implementation_guidelines = models.FileField(upload_to='ministry_programs/guidelines/', blank=True, null=True)
    monitoring_framework = models.FileField(upload_to='ministry_programs/monitoring/', blank=True, null=True)
    
    # Integration
    notion_database_id = models.CharField(max_length=36, blank=True, help_text="Notion database ID")
    external_system_id = models.CharField(max_length=100, blank=True, help_text="External system reference")
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='last_modified_programs'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_programs'
    )
    
    # Soft Delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_programs'
    )
    deletion_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at', 'ministry', 'title']
        indexes = [
            models.Index(fields=['ministry', 'status']),
            models.Index(fields=['status', 'is_deleted']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.ministry}-{self.title}")
        
        # Auto-generate code if not provided
        if not self.code:
            ministry_prefix = self.ministry.upper()
            year = self.start_date.year if self.start_date else timezone.now().year
            
            # Implement a retry mechanism for code generation to handle race conditions
            max_attempts = 5
            for attempt in range(max_attempts):
                count = MinistryProgram.objects.filter(
                    ministry=self.ministry,
                    start_date__year=year
                ).count() + 1 + attempt # Increment count for each attempt
                
                proposed_code = f"{ministry_prefix}-{year}-{count:03d}"
                
                # Check if the proposed code already exists
                if not MinistryProgram.objects.filter(code=proposed_code).exists():
                    self.code = proposed_code
                    break
                elif attempt == max_attempts - 1:
                    # If max attempts reached and code is still not unique, raise an error
                    raise ValueError("Could not generate a unique code after multiple attempts. Please try again.")
        
        # Automatic public visibility based on program status (is_deleted is managed by soft_delete/restore)
        if self.status in ['active', 'pending_approval']:
            self.is_public = True
        elif self.status in ['suspended', 'cancelled', 'archived']:
            self.is_public = False
        # If status is 'draft', is_public remains its default (True) or whatever it was set to.

        # Calculate duration_months if start_date and end_date are available and duration_months is not set
        if self.start_date and self.end_date and not self.duration_months:
            delta = self.end_date - self.start_date
            self.duration_months = round(delta.days / 30.44) # Average days in a month

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"[{self.get_ministry_display()}] {self.title}"
    
    def get_absolute_url(self):
        return reverse('fahaniecares_program_detail', args=[self.slug])

    def to_json(self):
        """
        Returns a JSON-serializable dictionary of the PPA's attributes,
        including display values for choices and formatted budget.
        """
        data = {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'slug': self.slug,
            'ministry': self.ministry,
            'ministry_display': self.get_ministry_display(),
            'program_source': self.program_source,
            'program_source_display': self.get_program_source_display(),
            'ppa_type': self.ppa_type,
            'ppa_type_display': self.get_ppa_type_display(),
            'description': self.description,
            'objectives': self.objectives,
            'expected_outcomes': self.expected_outcomes,
            'key_performance_indicators': self.key_performance_indicators,
            'target_beneficiaries': self.target_beneficiaries,
            'geographic_coverage': self.geographic_coverage,
            'estimated_beneficiaries': self.estimated_beneficiaries,
            'implementation_strategy': self.implementation_strategy,
            'implementing_units': self.implementing_units,
            'partner_agencies': self.partner_agencies,
            'total_budget': float(self.total_budget) if self.total_budget is not None else None,
            'allocated_budget': float(self.allocated_budget) if self.allocated_budget is not None else None,
            'utilized_budget': float(self.utilized_budget) if self.utilized_budget is not None else None,
            'funding_source': self.funding_source,
            'funding_source_display': self.get_funding_source_display(),
            'funding_details': self.funding_details,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_months': self.duration_months,
            'status': self.status,
            'status_display': self.get_status_display(),
            'priority_level': self.priority_level,
            'priority_display': self.get_priority_level_display(),
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'requires_approval': self.requires_approval,
            'notion_database_id': self.notion_database_id,
            'external_system_id': self.external_system_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deletion_reason': self.deletion_reason,
        }
        return data
    
    def soft_delete(self, user, reason=None):
        """Soft delete the program instead of hard delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        if reason:
            self.deletion_reason = reason
        
        # Also change status to 'cancelled' to avoid conflicts with save method's logic
        self.status = 'cancelled' 

        import logging
        logger = logging.getLogger(__name__)

        try:
            self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'deletion_reason', 'status'])
            self.refresh_from_db() # Force reload from DB to confirm state
            logger.info(f"PPA {self.id} ('{self.title}') successfully soft-deleted and status set to 'cancelled' by user {user.username}. Confirmed is_deleted after save: {self.is_deleted}")
        except Exception as e:
            logger.error(f"Error during soft_delete for PPA {self.id} ('{self.title}'): {e}")
            raise # Re-raise to propagate the error
    
    def restore(self, user):
        """Restore a soft-deleted program."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deletion_reason = ''
        self.last_modified_by = user
        self.save()
    
    def approve(self, user):
        """Approve the program."""
        self.status = 'active'
        self.approved_at = timezone.now()
        self.approved_by = user
        self.last_modified_by = user
        self.save()
    
    def can_edit(self, user):
        """Check if user can edit this program."""
        if user.is_superuser:
            return True
        if user == self.created_by or user == self.ministry_liaison or user == self.program_manager:
            return True
        if user.user_type in ['staff', 'mp'] and not self.requires_approval:
            return True
        return False
    
    def can_delete(self, user):
        """Check if user can delete this program."""
        if user.is_superuser:
            return True
        if user == self.created_by and self.status == 'draft':
            return True
        if user.user_type in ['staff', 'mp']:
            return True
        return False
    
    def get_budget_utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.allocated_budget > 0:
            return (self.utilized_budget / self.allocated_budget) * 100
        return 0
    
    def is_active(self):
        """Check if program is currently active."""
        return self.status == 'active' and not self.is_deleted
    
    @property
    def status_color(self):
        """Return CSS class for status badge color."""
        status_colors = {
            'draft': 'secondary',
            'pending_approval': 'warning',
            'active': 'success',
            'suspended': 'danger',
            'completed': 'info',
            'cancelled': 'dark',
            'archived': 'light',
        }
        return status_colors.get(self.status, 'secondary')


class MinistryProgramHistory(models.Model):
    """
    Track all changes made to ministry programs for audit purposes.
    """
    ACTION_TYPES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('restore', 'Restored'),
        ('approve', 'Approved'),
        ('suspend', 'Suspended'),
        ('complete', 'Completed'),
    )
    
    program = models.ForeignKey(
        MinistryProgram,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    changed_fields = models.JSONField(default=dict, help_text="Fields that were changed")
    old_values = models.JSONField(default=dict, help_text="Previous values")
    new_values = models.JSONField(default=dict, help_text="New values")
    
    # Change details
    reason = models.TextField(blank=True, help_text="Reason for the change")
    comments = models.TextField(blank=True)
    
    # User and timestamp
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='program_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # System info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['program', 'changed_at']),
            models.Index(fields=['action_type', 'changed_at']),
        ]
    
    def __str__(self):
        return f"{self.program.title} - {self.get_action_type_display()} by {self.changed_by.get_full_name()}"


class ServiceProgram(models.Model):
    """
    Direct service programs offered by #FahanieCares.
    """
    PROGRAM_STATUS = (
        ('active', 'Active'),
        ('planning', 'Planning'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    )
    
    PROGRAM_TYPES = (
        ('educational', 'Educational Support'),
        ('health', 'Healthcare Services'),
        ('livelihood', 'Livelihood Assistance'),
        ('emergency', 'Emergency Relief'),
        ('infrastructure', 'Community Infrastructure'),
        ('social', 'Social Services'),
        ('youth', 'Youth Development'),
        ('elderly', 'Senior Citizen Support'),
        ('pwd', 'PWD Assistance'),
        ('volunteer_teachers', 'Volunteer Teachers'),
        ('other', 'Other Services'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField()
    objectives = models.TextField()
    
    # Eligibility
    eligibility_criteria = models.TextField()
    required_documents = models.TextField()
    target_beneficiaries = models.CharField(max_length=200)
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    application_start = models.DateField(null=True, blank=True)
    application_end = models.DateField(null=True, blank=True)
    
    # Resources
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    funding_source = models.CharField(max_length=200, blank=True)
    max_beneficiaries = models.PositiveIntegerField(default=0)
    
    # Implementation
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS, default='planning')
    implementing_chapters = models.ManyToManyField(
        'chapters.Chapter',
        related_name='programs',
        blank=True
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coordinated_programs'
    )
    
    # Partnerships
    partner_agencies = models.TextField(blank=True)
    partner_organizations = models.TextField(blank=True)
    
    # Documentation
    program_guidelines = models.FileField(upload_to='program_guidelines/', blank=True, null=True)
    application_form = models.FileField(upload_to='program_forms/', blank=True, null=True)
    
    # Tracking
    beneficiary_count = models.PositiveIntegerField(default=0)
    budget_utilized = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_programs'
    )
    
    class Meta:
        ordering = ['-start_date', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('service_program_detail', args=[self.slug])
    
    def is_accepting_applications(self):
        """Check if program is currently accepting applications."""
        if not self.application_start or not self.application_end:
            return self.status == 'active'
        
        today = timezone.now().date()
        return (self.application_start <= today <= self.application_end and 
                self.status == 'active')
    
    def update_beneficiary_count(self):
        """Update the beneficiary count based on approved applications."""
        self.beneficiary_count = self.applications.filter(
            status='approved'
        ).count()
        self.save(update_fields=['beneficiary_count'])


class ServiceApplication(models.Model):
    """
    Represents an application submitted by a constituent for a ServiceProgram.
    """
    APPLICATION_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('completed', 'Completed'),
    )

    # Program fields - one of these should be set
    service_program = models.ForeignKey(
        ServiceProgram,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,
        help_text="The service program applied for (if applicable)"
    )
    ministry_program = models.ForeignKey(
        MinistryProgram,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,
        help_text="The ministry program applied for (if applicable)"
    )

    constituent = models.ForeignKey(
        FahanieCaresMember, # Change to FahanieCaresMember
        on_delete=models.CASCADE,
        related_name='service_applications'
    )
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    remarks = models.TextField(blank=True, help_text="Internal remarks about the application")

    # New fields for assessment and assistance
    PRIORITY_LEVELS = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    assessment_notes = models.TextField(blank=True, help_text="Notes from the application assessment")
    
    home_visit_required = models.BooleanField(default=False)
    home_visit_completed = models.BooleanField(default=False)
    home_visit_report = models.TextField(blank=True, help_text="Report from home visit, if conducted")

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications_reviewed'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications_approved'
    )

    assistance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    assistance_description = models.TextField(blank=True, help_text="Description of assistance provided")
    disbursement_date = models.DateField(null=True, blank=True)
    disbursement_method = models.CharField(max_length=50, blank=True)

    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)

    # Fields for beneficiary details (if different from applicant)
    beneficiary_is_self = models.BooleanField(default=True, help_text="Is the beneficiary the same as the applicant?")
    beneficiary_name = models.CharField(max_length=255, blank=True, help_text="Full name of the beneficiary if different from applicant")
    beneficiary_relationship = models.CharField(max_length=100, blank=True, help_text="Relationship of beneficiary to applicant")
    beneficiary_contact = models.CharField(max_length=20, blank=True, help_text="Contact number of the beneficiary")
    
    household_size = models.PositiveIntegerField(default=1)
    household_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reason_for_application = models.TextField(blank=True)
    supporting_details = models.TextField(blank=True)

    class Meta:
        ordering = ['-application_date']
        # Removed unique_together as it's complex with two nullable FKs.
        # Uniqueness will need to be handled in clean() or custom validation.

    def clean(self):
        # Ensure only one of service_program or ministry_program is set
        if self.service_program and self.ministry_program:
            raise ValidationError('An application cannot be for both a Service Program and a Ministry Program.')
        if not self.service_program and not self.ministry_program:
            raise ValidationError('An application must be for either a Service Program or a Ministry Program.')

    def __str__(self):
        if self.service_program:
            return f"Application for {self.service_program.name} by {self.constituent.full_name}"
        elif self.ministry_program:
            return f"Application for {self.ministry_program.title} by {self.constituent.full_name}"
        return f"Application by {self.constituent.full_name}"

    @property
    def program(self):
        """Returns the associated program, whether service or ministry."""
        return self.service_program or self.ministry_program

    @property
    def status_color(self):
        """Return CSS class for status badge color based on application status."""
        status_colors = {
            'pending': 'yellow',
            'approved': 'green',
            'rejected': 'red',
            'withdrawn': 'gray',
            'completed': 'blue',
        }
        return status_colors.get(self.status, 'gray')

    def approve(self, user, amount=None, description=None):
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = user
        self.assistance_amount = amount
        self.assistance_description = description
        self.save()
        if self.service_program:
            self.service_program.update_beneficiary_count()
        # No equivalent update for MinistryProgram currently, if needed, add here.

    def reject(self, user, reason=""):
        self.status = 'rejected'
        self.remarks = reason
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.save()

    def withdraw(self):
        self.status = 'withdrawn'
        self.save()


class ApplicationAttachment(models.Model):
    """
    Attachments related to a service application.
    """
    application = models.ForeignKey(
        ServiceApplication,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='application_attachments/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Attachment for {self.application} - {self.file.name}"


class ServiceDisbursement(models.Model):
    """
    Records financial disbursements made for a service application.
    """
    DISBURSEMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('voucher', 'Voucher'),
        ('in_kind', 'In-Kind'),
    )
    DISBURSEMENT_STATUS = (
        ('pending', 'Pending'),
        ('disbursed', 'Disbursed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )

    application = models.ForeignKey(
        ServiceApplication,
        on_delete=models.CASCADE,
        related_name='disbursements'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=DISBURSEMENT_METHODS)
    status = models.CharField(max_length=20, choices=DISBURSEMENT_STATUS, default='pending')
    scheduled_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction or reference number")
    notes = models.TextField(blank=True)

    disbursed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disbursements_made'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date', '-created_at']

    def __str__(self):
        return f"Disbursement of {self.amount} for {self.application}"


class ServiceImpact(models.Model):
    """
    Records the impact and outcomes of service programs.
    This comment is added to trigger a file change for deployment purposes.
    """
    program = models.ForeignKey(
        ServiceProgram,
        on_delete=models.CASCADE,
        related_name='impact_reports'
    )
    report_date = models.DateField(auto_now_add=True)
    period_start = models.DateField()
    period_end = models.DateField()
    total_beneficiaries = models.PositiveIntegerField(default=0)
    qualitative_impact = models.TextField(blank=True, help_text="Narrative description of impact")
    quantitative_data = models.JSONField(default=dict, blank=True, null=True, help_text="JSON field for structured data (e.g., {'jobs_created': 10, 'literacy_rate_increase': 0.15})")
    challenges = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impact_reports_submitted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']
        unique_together = ('program', 'period_start', 'period_end')

    def __str__(self):
        return f"Impact Report for {self.program.name} ({self.period_start} to {self.period_end})"
