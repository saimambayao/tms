from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import JSONField
from simple_history.models import HistoricalRecords
from django.core.validators import RegexValidator
from django.contrib.postgres.search import SearchVectorField

User = get_user_model()

class Agency(models.Model):
    """
    Government agencies for service referrals.
    """
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=20, blank=True)
    ministry = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    contact_info = models.TextField(blank=True, null=True, help_text='Additional contact information') # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        verbose_name_plural = "Agencies"
        ordering = ['name']
    
    def __str__(self):
        if self.abbreviation:
            return f"{self.abbreviation} - {self.name}"
        return self.name

class ServiceCategory(models.Model):
    """
    Categories for government services.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    slug = models.SlugField(unique=True, max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True) # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Government services that can be referred to.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='services')
    eligibility_criteria = models.TextField(blank=True, null=True, help_text='Structured eligibility criteria')
    required_documents = JSONField(blank=True, default=list, help_text='List of required documents')
    application_process = models.TextField(blank=True)
    processing_time = models.CharField(max_length=100, blank=True)
    fees = models.CharField(max_length=100, blank=True)
    contact_info = models.TextField(blank=True, null=True)
    website_link = models.URLField(blank=True)
    form_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show this service on the homepage")
    slug = models.SlugField(unique=True, max_length=255)
    search_vector = SearchVectorField(blank=True, null=True) # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('service_detail', args=[self.slug])

class Referral(models.Model):
    """
    Service referrals for constituents.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('processing', 'Processing'),
        ('referred', 'Referred to Agency'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    reference_number = models.CharField(max_length=20, unique=True, validators=[RegexValidator(regex='^REF-\\d{8}-\\d{4}$', message='Reference number must be in format REF-YYYYMMDD-NNNN')])
    constituent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='referrals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    description = models.TextField(help_text="Describe the specific need or request")
    supporting_documents = JSONField(blank=True, default=list, help_text="List of supporting documents provided")
    metadata = JSONField(blank=True, default=dict, help_text='Additional metadata for the referral') # New field
    staff_notes = models.TextField(blank=True)
    agency_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_referrals')
    agency_contact = models.CharField(max_length=255, blank=True)
    agency_reference = models.CharField(max_length=100, blank=True, help_text="Reference number at the agency")
    submitted_at = models.DateTimeField(null=True, blank=True)
    referred_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    search_vector = SearchVectorField(blank=True, null=True) # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Referral {self.reference_number} - {self.constituent.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate a unique reference number
            year = timezone.now().year
            month = timezone.now().month
            day = timezone.now().day
            count = Referral.objects.filter(
                created_at__year=year,
                created_at__month=month,
                created_at__day=day
            ).count() + 1
            self.reference_number = f"REF-{year}{month:02d}{day:02d}-{count:04d}"
        
        # Update timestamps for status changes
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        elif self.status == 'referred' and not self.referred_at:
            self.referred_at = timezone.now()
        elif self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            
        super().save(*args, **kwargs)

class ReferralUpdate(models.Model):
    """
    Updates/statuses for referrals.
    """
    UPDATE_TYPE_CHOICES = (
        ('status_change', 'Status Change'),
        ('comment', 'Comment'),
        ('document_added', 'Document Added'),
        ('assignment', 'Assignment Change'),
        ('follow_up', 'Follow-up'),
    )
    
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=20, choices=Referral.STATUS_CHOICES)
    notes = models.TextField()
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES, default='status_change', db_index=True) # New field
    metadata = JSONField(blank=True, default=dict) # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # New field
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.referral.reference_number} - {self.status}"

class ReferralDocument(models.Model):
    """
    Documents attached to referrals.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('id_document', 'ID Document'),
        ('proof_of_income', 'Proof of Income'),
        ('medical_certificate', 'Medical Certificate'),
        ('barangay_certificate', 'Barangay Certificate'),
        ('application_form', 'Application Form'),
        ('supporting_document', 'Supporting Document'),
        ('other', 'Other'),
    )

    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='referral_documents/')
    file_size = models.PositiveIntegerField(default=0) # New field
    file_type = models.CharField(max_length=50, blank=True) # New field
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='supporting_document', db_index=True) # New field
    is_verified = models.BooleanField(default=False, db_index=True) # New field
    verified_at = models.DateTimeField(blank=True, null=True) # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # New field
    is_deleted = models.BooleanField(default=False, db_index=True) # New field
    deleted_at = models.DateTimeField(blank=True, null=True) # New field
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_%(class)ss') # New field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_%(class)ss') # New field
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_%(class)ss') # New field
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents') # New field

    history = HistoricalRecords() # New field
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Document for {self.referral.reference_number} - {self.name}"
