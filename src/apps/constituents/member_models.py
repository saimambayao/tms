from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import safe_voter_id_upload
import secrets
import string

class BMParliamentMember(models.Model):
    """
    Comprehensive member profile for #BM Parliament registration
    """
    
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    EDUCATION_CHOICES = (
        ('elementary', 'Elementary level'),
        ('high_school', 'High School level'),
        ('vocational', 'Vocational/Technical level'),
        ('some_college', 'College level'),
        ('bachelors', "Bachelor's Degree"),
        ('masters', "Master's Degree"),
        ('doctorate', 'Doctorate Degree/PhD'),
        ('other', 'Other')
    )
    
    SECTOR_CHOICES = (
        ('student', 'College Students in need of Educational Assistance'),
        ('delivery_riders', 'Delivery Riders'),
        ('dressmaker_weaver', 'Dressmaker/Weaver'),
        ('farmer', 'Farmers'),
        ('fisherman', 'Fishermen'),
        ('women_mothers', 'Learning Women/Mothers (Ummahat)'),
        ('madaris_students', 'Madaris Students'),
        ('mujahidin', 'Mujahidin/Mujahidat'),
        ('special_needs', 'Parents/Guardians of Children with Special Needs'),
        ('pwd_student', 'Person with Disability (PWD)'),
        ('volunteer_teacher', 'Public School Volunteer Teachers (English/Arabic)'),
        ('small_time_vendor', 'Small-time Vendors'),
        ('solo_parent', 'Solo Parents'),
        ('volunteer_health', 'Volunteer Health Workers'),
        ('cancer_dialysis', 'Hospital Patients'),
    )
    
    ELIGIBILITY_CHOICES = (
        ('none', 'None'),
        ('prc_passer', 'PRC Passer'),
        ('csc_passer', 'CSC Passer'),
        ('both', 'Both PRC and CSC Passer')
    )
    
    # Link to User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bm_parliament_member'
    )
    
    # Application Information
    date_of_application = models.DateField(auto_now_add=True)
    
    # Personal Information
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    age = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    sex = models.CharField(max_length=20, choices=SEX_CHOICES)
    member_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Current Address
    address_barangay = models.CharField(max_length=100)
    address_municipality = models.CharField(max_length=100)
    address_province = models.CharField(max_length=100, default='Maguindanao del Sur')
    
    # Voter Registration Address
    voter_address_barangay = models.CharField(max_length=100)
    voter_address_municipality = models.CharField(max_length=100)
    voter_address_province = models.CharField(max_length=100, default='Maguindanao del Sur')
    
    # Sector Information
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    
    # Education Information
    highest_education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    school_graduated = models.CharField(max_length=255, blank=True)
    eligibility = models.CharField(max_length=20, choices=ELIGIBILITY_CHOICES, default='none')

    # College Student Specific Information (only required for student sector)
    college_school = models.CharField(max_length=255, blank=True, help_text="Name of college/university currently attending")
    year_level = models.CharField(max_length=20, blank=True, choices=[
        ('1st_year', '1st Year'),
        ('2nd_year', '2nd Year'),
        ('3rd_year', '3rd Year'),
        ('4th_year', '4th Year'),
        ('5th_year', '5th Year'),
        ('graduate', 'Graduate Student'),
    ], help_text="Current year level in college")

    # PWD Specific Information (only required for pwd_student sector)
    pwd_disability_type = models.CharField(max_length=20, blank=True, choices=[
        ('physical', 'Physical Disability'),
        ('mental', 'Mental/Intellectual Disability'),
    ], help_text="Type of disability")

    # LGBTQ Community Specific Information (only required for lgbtq_community sector)
    lgbtq_identity = models.CharField(max_length=30, blank=True, choices=[
        ('gay', 'Gay'),
        ('lesbian', 'Lesbian'),
        ('bisexual', 'Bisexual'),
        ('transgender', 'Transgender'),
        ('queer', 'Queer'),
        ('questioning', 'Questioning'),
        ('intersex', 'Intersex'),
        ('asexual', 'Asexual'),
        ('pansexual', 'Pansexual'),
        ('non_binary', 'Non-Binary'),
        ('genderfluid', 'Genderfluid'),
        ('two_spirit', 'Two-Spirit'),
        ('other', 'Other'),
    ], help_text="LGBTQ+ identity")

    # Cancer/Dialysis Patient Specific Information (only required for cancer_dialysis sector)
    cancer_patient = models.BooleanField(default=False, help_text="Is a cancer patient")
    dialysis_patient = models.BooleanField(default=False, help_text="Is a dialysis patient")


    # Verification Photo
    voter_id_photo = models.ImageField(
        upload_to=safe_voter_id_upload, 
        null=True, 
        blank=True,
        help_text="Upload a clear photo of your Voter's Certificate or ID for verification."
    )

    # Status and Approval
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('incomplete', 'Incomplete'),
        ('non_compliant', 'Non Compliant'),
        ('archived', 'Archived'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    approved_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_members'
    )
    denied_date = models.DateField(null=True, blank=True)
    denied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='denied_members'
    )
    denial_reason = models.TextField(blank=True)
    
    # Integration fields
    assigned_chapter = models.ForeignKey(
        'chapters.Chapter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_members',
        help_text="Chapter assigned to this approved member"
    )
    chapter_assigned_date = models.DateField(null=True, blank=True)
    chapter_assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_chapter_members'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'constituents'
        ordering = ['-date_of_application']
        verbose_name = '#BM Parliament Member'
        verbose_name_plural = '#BM Parliament Members'
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name}"
    
    def get_full_name(self):
        """Return the full name in proper format"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """Return complete current address"""
        return f"{self.address_barangay}, {self.address_municipality}, {self.address_province}"
    
    def get_voter_address(self):
        """Return complete voter registration address"""
        return f"{self.voter_address_barangay}, {self.voter_address_municipality}, {self.voter_address_province}"

    @property
    def is_approved(self):
        """Check if the member's registration is approved."""
        return self.status == 'approved'
    
    def get_sector_display_category(self):
        """Return the main category of the sector"""
        vulnerable_sectors = [
            'pwd_student', 'solo_parent', 'volunteer_teacher', 
            'volunteer_health', 'special_needs'
        ]
        youth_sectors = ['student']
        
        if self.sector in vulnerable_sectors:
            return "Vulnerable Sectors"
        elif self.sector in youth_sectors:
            return "Youth"
        elif self.sector == 'women_mothers':
            return "Women/Mothers and Children"
        return "Other"

    SECTOR_ID_PREFIXES = {
        'pwd_student': 'PWD',
        'solo_parent': 'SP',
        'volunteer_health': 'VHW',
        'volunteer_teacher': 'VT',
        'special_needs': 'SN',
        'women_mothers': 'WM',
        'farmer': 'F',
        'fisherman': 'FM',
        'small_time_vendor': 'STV',
        'dressmaker_weaver': 'DW',
        'student': 'S',
        'mujahidin': 'MJ',
        'madaris_students': 'MS',
    }

    def _generate_member_id(self, is_temporary=False):
        if is_temporary:
            # Generate a temporary ID: PREG + 8 random alphanumeric characters
            alphabet = string.ascii_uppercase + string.digits
            random_suffix = ''.join(secrets.choice(alphabet) for i in range(8))
            return f"PREG{random_suffix}"
        else:
            prefix = self.SECTOR_ID_PREFIXES.get(self.sector, 'GEN') # Default to GEN if sector not found
            
            # Find the highest existing sequential number for the given prefix
            # We need to ensure the suffix is numeric to avoid issues with temporary IDs
            last_member = BMParliamentMember.objects.filter(
                member_id__startswith=prefix
            ).exclude(
                member_id__regex=r'^PREG[A-Z0-9]{8}$' # Exclude temporary IDs
            ).order_by('-member_id').first()

            next_number = 1
            if last_member and last_member.member_id:
                try:
                    last_number_str = last_member.member_id[len(prefix):]
                    last_number = int(last_number_str)
                    next_number = last_number + 1
                except ValueError:
                    # If suffix is not a valid number, start from 1
                    next_number = 1
            
            # Ensure uniqueness by incrementing until a unique ID is found
            while True:
                new_member_id = f"{prefix}{next_number:04d}"
                if not BMParliamentMember.objects.filter(member_id=new_member_id).exists():
                    return new_member_id
                next_number += 1

    def _generate_status_id(self, status_prefix):
        """Generate ID for incomplete (INC) and non-compliant (NOC) statuses"""
        # Find the highest existing sequential number for the given status prefix
        last_member = BMParliamentMember.objects.filter(
            member_id__startswith=status_prefix
        ).order_by('-member_id').first()

        next_number = 1
        if last_member and last_member.member_id:
            try:
                last_number_str = last_member.member_id[len(status_prefix):]
                last_number = int(last_number_str)
                next_number = last_number + 1
            except ValueError:
                # If suffix is not a valid number, start from 1
                next_number = 1

        # Ensure uniqueness by incrementing until a unique ID is found
        while True:
            new_member_id = f"{status_prefix}{next_number:04d}"
            if not BMParliamentMember.objects.filter(member_id=new_member_id).exists():
                return new_member_id
            next_number += 1

    def save(self, *args, **kwargs):
        # Check if the instance is new
        is_new = self._state.adding

        # Check for existing member with the same full name
        if is_new:
            existing_member = BMParliamentMember.objects.filter(
                first_name=self.first_name,
                last_name=self.last_name,
                middle_name=self.middle_name
            ).exclude(pk=self.pk).first()

            if existing_member:
                from django.core.exceptions import ValidationError
                raise ValidationError("A member with this full name already exists.")

        # Handle member ID generation based on status
        if is_new and self.status == 'pending' and not self.member_id:
            # Assign temporary ID for new, pending registrants
            self.member_id = self._generate_member_id(is_temporary=True)
        elif self.status == 'approved':
            if not self.member_id or (self.member_id and self.member_id.startswith('PREG')):
                # Assign permanent ID when approved and no ID exists or if it's a temporary ID
                self.member_id = self._generate_member_id()
        elif self.status == 'incomplete' and not self.member_id:
            # Assign INC ID for incomplete registrants
            self.member_id = self._generate_status_id('INC')
        elif self.status == 'non_compliant' and not self.member_id:
            # Assign NOC ID for non-compliant registrants
            self.member_id = self._generate_status_id('NOC')

        super().save(*args, **kwargs)
