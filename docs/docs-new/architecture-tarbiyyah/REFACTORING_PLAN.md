# Tarbiyyah Management System (TMS) - Subtle Transition Plan

**Document Version:** 1.6.2
**Date:** November 20, 2025
**Status:** Approved - Ready for Implementation

## Philosophy: Evolve, Don't Replace
Adapt existing models, forms, templates, and databases with minimal disruption. Focus on configuration, field additions, and contextual renaming rather than rebuilding from scratch.

---

## Phase 1: Branding & Configuration Layer (No Database Changes)

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-01-branding/`
- task_001.txt - Create Full Database Backup
- task_002.txt - Backup Media Files
- task_003.txt - Create Git Tag ✅ DONE
- task_005.txt - Document Rollback Plan
- task_007.txt - Create Branding Context Processor
- task_008.txt - Update PWA Manifest
- task_009.txt - Update Logos and Favicons
- task_010.txt - Implement Role-Based Navigation Structure
- task_012.txt - Update Announcements Template
- task_013.txt - Update Home Page Template
- task_014.txt - Update Page Titles
- task_015.txt - Verify Phase 1 Branding Complete

### 1.1 Update Display Text & Context
- Update `apps/core/models.py` → Announcement categories (keep model, change choices)
- Update templates: Replace "BM Parliament" with "Tarbiyyah Management System"
- Update `base.html`, navigation menus, page titles
- Modify PWA manifest for new branding
- Update static files: logos, favicons

### 1.2 Settings Context Variables
- Add context processor for system-wide terminology
- Configure `SYSTEM_NAME`, `SYSTEM_TYPE` in settings
- Keep all existing database tables

---

## Phase 2: User Roles - Extend, Don't Replace

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-02-roles/`
- task_016.txt - Add Role Choices to User Model
- task_017.txt - Create User Role Migration
- task_018.txt - Run Migration and Verify
- task_019.txt - Create Role Permission Mappings
- task_020.txt - Implement Role-Based Access Control
- task_021.txt - Update Templates for Role-Based Display
- task_022.txt - Create Role Selection Interface
- task_023.txt - Write Role-Based Tests
- task_024.txt - Create User Fixtures with Roles
- task_025.txt - Verify Phase 2 Roles Complete

### 2.1 Add New Role Choices (Keep Existing Role System)
**Adapt `apps/users/models.py` User.Role:**
- Keep existing role infrastructure
- **Add new choices** to existing enum:
  - `TARBIYYAH_ADMIN` (System administrator for entire Tarbiyyah Management System - below superuser, manages all madaris across BARMM)
  - `MADRASAH_ADMIN` (school-level administrator, rename from `coordinator`)
  - `MUDER` (مدير - madrasah director/principal)
  - `ASATIDZ` (أساتذة - teachers, plural of ustadz/ustadza)
  - `STUDENT`
  - `PARENT`
- Keep `superuser`, `admin`, `staff` roles
- **Role Hierarchy**: `superuser` > `TARBIYYAH_ADMIN` > `MADRASAH_ADMIN` > `MUDER` > `ASATIDZ`/`STUDENT`/`PARENT`
- **Rename existing role**: `coordinator` → `MADRASAH_ADMIN` (database migration needed)

### 2.2 Update RolePermission Mappings & Migration Strategy
- Add permission mappings for new roles
- Keep all existing middleware
- Update only the permission templates
- **Migration for role rename**: Update existing users with `role='coordinator'` to `role='madrasah_admin'`
- Update all role references in templates and UI to use new terminology

---

## Phase 3: Madaris Management - Full Transition from Chapters

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-03-madaris/`
- task_026.txt - Plan Madrasah Model Migration Strategy
- task_027.txt - Create Madrasah Model (rename from Chapter)
- task_028.txt - Add Education-Specific Fields
- task_029.txt - Create Madrasah Type Choices
- task_030.txt - Add Accreditation Fields
- task_031.txt - Add Location/Region Fields
- task_032.txt - Create Data Migration Script
- task_033.txt - Run Madrasah Migration
- task_034.txt - Update Foreign Key References
- task_035.txt - Verify Data Integrity
- task_036.txt - Update Madrasah Admin Interface
- task_037.txt - Create MadrasahEnrollment Model
- task_038.txt - Migrate Enrollment Data
- task_039.txt - Update Enrollment Admin
- task_040.txt - Create MadrasahActivity Model
- task_041.txt - Migrate Activity Data
- task_042.txt - Update Activity Admin
- task_043.txt - Update Madaris URLs and Views
- task_044.txt - Update Madaris Templates
- task_045.txt - Verify Phase 3 Complete

### 3.1 Rename App and Models
**Full transition: `apps/chapters/` → `apps/madaris/`**
- Rename app directory from `chapters` to `madaris`
- Rename `Chapter` model → `Madrasah`
- Rename `ChapterMembership` model → `MadrasahEnrollment`
- Rename `ChapterActivity` model → `MadrasahActivity`
- Update all imports, URLs, and references across the codebase
- Database migration: Rename tables `chapters_chapter` → `madaris_madrasah`, etc.

### 3.2 Madrasah Model Architecture
**Comprehensive Madrasah model with education-specific fields:**

```python
class Madrasah(models.Model):
    """Islamic School (Madrasah) Model"""

    # Basic Information
    name = CharField(max_length=255)  # e.g., "Madrasah Al-Furqan"
    name_arabic = CharField(max_length=255, blank=True)  # Arabic name
    school_code = CharField(max_length=50, unique=True)  # e.g., "MAD-LDS-001"

    # Madrasah Types (Multiple selection allowed)
    class MadrasahType(models.TextChoices):
        IBTIDAIYYAH = 'ibtidaiyyah', 'Ibtidaiyyah (Elementary)'
        IDADIYYAH = 'idadiyyah', "I'dadiyyah (Preparatory/Intermediate)"
        THANAWIYYAH = 'thanawiyyah', 'Thanawiyyah (Secondary)'
        KULLIYAH = 'kulliyah', 'Kulliyah (Tertiary/Higher Education)'
        INTEGRATED = 'integrated', 'Integrated (Multi-level)'
        TAHFIDZ = 'tahfidz', 'Tahfidz (Quran Memorization)'

    # JSONField for multiple madrasah types
    madrasah_types = JSONField(
        default=list,
        help_text="Select one or more education levels offered"
    )
    # e.g., ['ibtidaiyyah', 'thanawiyyah'] for a madrasah offering Elementary and Secondary

    # Location & Hierarchy (Keep existing structure)
    region = CharField(max_length=100, default='BARMM')
    province = CharField(max_length=100)  # e.g., 'Lanao del Sur'
    municipality = CharField(max_length=100)
    barangay = CharField(max_length=100)
    address = TextField()

    # Hierarchical Structure (for multi-school management)
    parent_madrasah = ForeignKey('self', null=True, blank=True,
                                  on_delete=SET_NULL,
                                  related_name='satellite_madaris')

    # Leadership
    muder = ForeignKey(User, on_delete=SET_NULL, null=True,
                       related_name='madrasah_as_muder',
                       limit_choices_to={'role': 'muder'})
    assistant_muder = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True,
                                  related_name='madrasah_as_assistant')
    registrar = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True,
                          related_name='madrasah_as_registrar')

    # Contact Information
    email = EmailField(blank=True)
    phone = CharField(max_length=20, blank=True)
    mobile = CharField(max_length=20)
    website = URLField(blank=True)

    # Accreditation & Recognition
    # NOTE: Accreditation is conducted by MBHTE (Ministry of Basic, Higher, and Technical Education)
    # The Tarbiyyah Committee coordinates the accreditation process and maintains status records
    class AccreditationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Accreditation'
        RECOGNIZED = 'recognized', 'Recognized by MBHTE'
        ACCREDITED = 'accredited', 'Fully Accredited'
        DEPED_RECOGNIZED = 'deped', 'DepEd Recognized'
        NOT_ACCREDITED = 'not_accredited', 'Not Yet Accredited'
        REJECTED = 'rejected', 'Accreditation Rejected'
    accreditation_status = CharField(max_length=20,
                                     choices=AccreditationStatus.choices,
                                     default='pending')
    accreditation_date = DateField(null=True, blank=True)  # Date accredited by MBHTE
    accreditation_number = CharField(max_length=100, blank=True)  # Accreditation cert number from MBHTE

    # Enrollment Capacity
    total_capacity = PositiveIntegerField(default=0)
    current_enrollment = PositiveIntegerField(default=0)

    # Facilities & Resources
    class FacilityLevel(models.TextChoices):
        POOR = 'poor', 'Poor (Inadequate facilities)'
        BASIC = 'basic', 'Basic (Limited facilities)'
        STANDARD = 'standard', 'Standard'
        GOOD = 'good', 'Good'
        EXCELLENT = 'excellent', 'Excellent'
    facility_level = CharField(max_length=20, choices=FacilityLevel.choices,
                               default='basic')
    has_library = BooleanField(default=False)
    has_computer_lab = BooleanField(default=False)
    has_masjid = BooleanField(default=True)  # Prayer hall/Mosque
    has_dormitory = BooleanField(default=False)

    # Curriculum Offered
    offers_arabic_language = BooleanField(default=True)
    offers_quran_studies = BooleanField(default=True)
    offers_hadith_studies = BooleanField(default=True)  # Ilm al-Hadith
    offers_islamic_studies = BooleanField(default=True)
    offers_general_education = BooleanField(default=False)
    curriculum_framework = ForeignKey('curriculum.CurriculumFramework',
                                      on_delete=SET_NULL, null=True, blank=True)

    # Operational Status
    class OperationalStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        UNDER_CONSTRUCTION = 'construction', 'Under Construction'
        TEMPORARILY_CLOSED = 'temp_closed', 'Temporarily Closed'
        CLOSED = 'closed', 'Permanently Closed'
    operational_status = CharField(max_length=20,
                                   choices=OperationalStatus.choices,
                                   default='active')

    # Founding & History
    founded_date = DateField(null=True, blank=True)
    founder_name = CharField(max_length=255, blank=True)

    # Social Media & Communication
    facebook_page = URLField(blank=True)

    # Metadata
    created_by = ForeignKey(User, on_delete=SET_NULL, null=True,
                           related_name='madaris_created')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'madaris_madrasah'
        verbose_name = 'Madrasah'
        verbose_name_plural = 'Madaris'
        ordering = ['province', 'municipality', 'name']

    def __str__(self):
        return f"{self.name} ({self.municipality}, {self.province})"
```

### 3.3 MadrasahEnrollment Model Architecture
**Enrollment tracking for students and staff:**

```python
class MadrasahEnrollment(models.Model):
    """Tracks student enrollments and staff assignments to madaris"""

    # Core Relationships
    madrasah = ForeignKey(Madrasah, on_delete=CASCADE,
                          related_name='enrollments')
    user = ForeignKey(User, on_delete=CASCADE,
                      related_name='madrasah_enrollments')

    # Enrollment Type
    class EnrollmentType(models.TextChoices):
        STUDENT = 'student', 'Student Enrollment'
        ASATIDZ = 'asatidz', 'Teacher/Ustadz'
        STAFF = 'staff', 'Administrative Staff'
        VOLUNTEER = 'volunteer', 'Volunteer'
    enrollment_type = CharField(max_length=20, choices=EnrollmentType.choices)

    # Academic Information (for students)
    academic_year = ForeignKey('academics.AcademicYear', on_delete=CASCADE,
                               null=True, blank=True)
    grade_level = CharField(max_length=50, blank=True)  # e.g., "Grade 1", "Year 1"
    section = CharField(max_length=50, blank=True)
    student_number = CharField(max_length=50, blank=True, unique=True)

    # Assignment Information (for asatidz/staff)
    position = CharField(max_length=100, blank=True)  # e.g., "Arabic Teacher"
    subjects_taught = JSONField(default=list, blank=True)  # For asatidz
    department = CharField(max_length=100, blank=True)

    # Status
    class EnrollmentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        GRADUATED = 'graduated', 'Graduated'
        TRANSFERRED = 'transferred', 'Transferred Out'
        DROPPED = 'dropped', 'Dropped'
        SUSPENDED = 'suspended', 'Suspended'
        ON_LEAVE = 'on_leave', 'On Leave'
    status = CharField(max_length=20, choices=EnrollmentStatus.choices,
                      default='active')

    # Dates
    enrollment_date = DateField(default=date.today)
    end_date = DateField(null=True, blank=True)

    # Volunteer/Participation (keep from ChapterMembership)
    is_volunteer = BooleanField(default=False)
    volunteer_hours = DecimalField(max_digits=10, decimal_places=2,
                                   default=0.00)

    # Metadata
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'madaris_enrollment'
        verbose_name = 'Madrasah Enrollment'
        verbose_name_plural = 'Madrasah Enrollments'
        unique_together = [['madrasah', 'user', 'academic_year', 'enrollment_type']]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.madrasah.name} ({self.enrollment_type})"
```

### 3.4 MadrasahActivity Model
**Events and activities:**

```python
class MadrasahActivity(models.Model):
    """Madrasah events, activities, and programs"""

    madrasah = ForeignKey(Madrasah, on_delete=CASCADE,
                          related_name='activities')
    title = CharField(max_length=255)
    description = TextField()

    class ActivityType(models.TextChoices):
        ACADEMIC = 'academic', 'Academic Event'
        ISLAMIC = 'islamic', 'Islamic Event/Celebration'
        EXAM = 'exam', 'Examination'
        ORIENTATION = 'orientation', 'Orientation/Meeting'
        COMPETITION = 'competition', 'Competition'
        GRADUATION = 'graduation', 'Graduation Ceremony'
        FUNDRAISING = 'fundraising', 'Fundraising Event'
        COMMUNITY = 'community', 'Community Outreach'
        TRAINING = 'training', 'Teacher Training'
    activity_type = CharField(max_length=20, choices=ActivityType.choices)

    date = DateField()
    start_time = TimeField(null=True, blank=True)
    end_time = TimeField(null=True, blank=True)
    venue = CharField(max_length=255, blank=True)

    # Budget tracking (keep from ChapterActivity)
    budget = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_expense = DecimalField(max_digits=10, decimal_places=2, default=0.00)

    organizer = ForeignKey(User, on_delete=SET_NULL, null=True)

    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'madaris_activity'
        verbose_name = 'Madrasah Activity'
        verbose_name_plural = 'Madrasah Activities'
        ordering = ['-date']
```

### 3.5 Form Architecture for Madrasah Management

**A. MadrasahRegistrationForm (Create New Madrasah):**
```python
class MadrasahRegistrationForm(forms.ModelForm):
    """Comprehensive form for registering a new madrasah"""

    class Meta:
        model = Madrasah
        fields = [
            # Basic Info
            'name', 'name_arabic', 'school_code', 'madrasah_types',

            # Location
            'region', 'province', 'municipality', 'barangay', 'address',

            # Leadership
            'muder', 'assistant_muder', 'registrar',

            # Contact
            'email', 'phone', 'mobile', 'website', 'facebook_page',

            # Accreditation
            'accreditation_status', 'accreditation_date', 'accreditation_number',

            # Capacity
            'total_capacity',

            # Facilities
            'facility_level', 'has_library', 'has_computer_lab',
            'has_prayer_hall', 'has_dormitory',

            # Curriculum
            'offers_arabic_language', 'offers_quran_studies',
            'offers_islamic_studies', 'offers_general_education',

            # History
            'founded_date', 'founder_name',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Madrasah Al-Furqan'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-textarea'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-textarea'
            }),
            'madrasah_types': forms.CheckboxSelectMultiple(choices=Madrasah.MadrasahType.choices),
            'founded_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'accreditation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter leadership choices to appropriate roles
        self.fields['muder'].queryset = User.objects.filter(role='muder')

        # Make certain fields required
        self.fields['mobile'].required = True
        self.fields['province'].required = True
        self.fields['municipality'].required = True
        self.fields['madrasah_types'].required = True

    def clean(self):
        cleaned_data = super().clean()
        madrasah_types = cleaned_data.get('madrasah_types')

        if not madrasah_types:
            raise forms.ValidationError(
                "Please select at least one education level offered."
            )
        return cleaned_data
```

**B. MadrasahUpdateForm (Update Existing):**
```python
class MadrasahUpdateForm(MadrasahRegistrationForm):
    """Form for updating madrasah information"""

    class Meta(MadrasahRegistrationForm.Meta):
        # Include operational status for updates
        fields = MadrasahRegistrationForm.Meta.fields + [
            'operational_status', 'current_enrollment', 'parent_madrasah'
        ]
```

**C. MadrasahEnrollmentForm (Enroll Student/Staff):**
```python
class MadrasahEnrollmentForm(forms.ModelForm):
    """Form for enrolling students or assigning staff to madrasah"""

    class Meta:
        model = MadrasahEnrollment
        fields = [
            'madrasah', 'user', 'enrollment_type',
            'academic_year', 'grade_level', 'section', 'student_number',
            'position', 'subjects_taught', 'department',
            'enrollment_date', 'is_volunteer'
        ]

    def __init__(self, *args, **kwargs):
        enrollment_type = kwargs.pop('enrollment_type', None)
        super().__init__(*args, **kwargs)

        # Dynamic field display based on enrollment type
        if enrollment_type == 'student':
            # Show student-specific fields
            self.fields['academic_year'].required = True
            self.fields['grade_level'].required = True
            # Hide staff fields
            del self.fields['position']
            del self.fields['subjects_taught']
            del self.fields['department']

        elif enrollment_type in ['asatidz', 'staff']:
            # Show staff-specific fields
            self.fields['position'].required = True
            # Hide student fields
            del self.fields['academic_year']
            del self.fields['grade_level']
            del self.fields['section']
            del self.fields['student_number']
```

**D. MadrasahActivityForm:**
```python
class MadrasahActivityForm(forms.ModelForm):
    """Form for creating madrasah activities/events"""

    class Meta:
        model = MadrasahActivity
        fields = [
            'madrasah', 'title', 'description', 'activity_type',
            'date', 'start_time', 'end_time', 'venue',
            'budget', 'organizer'
        ]

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
```

**E. MadrasahSearchForm:**
```python
class MadrasahSearchForm(forms.Form):
    """Advanced search form for madaris"""

    name = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={
                              'placeholder': 'Search by name...'
                          }))
    province = forms.ChoiceField(required=False)
    municipality = forms.ChoiceField(required=False)
    madrasah_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Madrasah.MadrasahType.choices)
    )
    accreditation_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Madrasah.AccreditationStatus.choices)
    )
    operational_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Madrasah.OperationalStatus.choices)
    )
```

### 3.6 Migration Strategy
**Step-by-step data migration:**

1. **Create new madaris app**: `python manage.py startapp madaris`
2. **Create models**: Add Madrasah, MadrasahEnrollment, MadrasahActivity models
3. **Generate initial migrations**: `python manage.py makemigrations madaris`
4. **Data migration script**: Copy data from Chapter → Madrasah
   ```python
   def migrate_chapters_to_madaris(apps, schema_editor):
       Chapter = apps.get_model('chapters', 'Chapter')
       Madrasah = apps.get_model('madaris', 'Madrasah')

       for chapter in Chapter.objects.all():
           Madrasah.objects.create(
               name=chapter.name,
               school_code=chapter.id,  # Generate proper code
               province=chapter.province,
               municipality=chapter.municipality,
               # ... map other fields
           )
   ```
5. **Update references**: Update all ForeignKey references across apps
6. **Remove old app**: After verification, remove `apps/chapters/`

### 3.7 URLs & Views Structure
```python
# apps/madaris/urls.py
urlpatterns = [
    path('', MadrasahListView.as_view(), name='madrasah-list'),
    path('register/', MadrasahCreateView.as_view(), name='madrasah-register'),
    path('<int:pk>/', MadrasahDetailView.as_view(), name='madrasah-detail'),
    path('<int:pk>/update/', MadrasahUpdateView.as_view(), name='madrasah-update'),
    path('<int:pk>/enroll/', EnrollmentCreateView.as_view(), name='madrasah-enroll'),
    path('<int:pk>/activities/', MadrasahActivityListView.as_view(), name='madrasah-activities'),
]
```

---

## Phase 4: Asatidz (Teachers) - Extend Student Profile System

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-04-teachers/`
- task_046.txt - Create Asatidz (Teachers) App
- task_047.txt - Create Teacher Model and Fields
- task_048.txt - Create Teacher Assignment Model
- task_049.txt - Create Teacher Admin Interface
- task_050.txt - Verify Phase 4 Complete

### 4.1 Create Asatidz Profile (Extend Existing)
**Add `apps/teachers/models.py`** with minimal new model:
*(Note: Keep app name as 'teachers' in code for Django conventions, but refer to as 'Asatidz' in UI)*
```python
class TeacherProfile(models.Model):
    user = OneToOneField(User)  # Links to existing user
    employee_id = CharField()
    specializations = JSONField()  # Quran, Fiqh, Arabic, etc.
    certifications = JSONField()
    hire_date = DateField()
    # Reuse User model for: name, contact, demographics
```

### 4.2 Reuse MadrasahEnrollment for Teacher Assignments
- Use `MadrasahEnrollment` model (renamed from ChapterMembership)
- Filter by `role='asatidz'` and `membership_type='staff'`
- Add `subjects_taught` JSONField to MadrasahEnrollment
- No new assignment tables needed - reuse existing structure

---

## Phase 5: Curriculum - New Lightweight App

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-05-curriculum/`
- Tasks to be created (~10 tasks)
- See phase-05-curriculum/README.md for planned tasks

### 5.1 Create Minimal `apps/curriculum/`
**Only essential models:**
```python
class Subject(models.Model):
    code, name, category, credit_hours
    # Simple, lightweight

class CurriculumFramework(models.Model):
    name, education_level, subjects (M2M to Subject)
    # Tracks what subjects per grade

class LessonPlan(models.Model):
    teacher (FK to User), subject (FK), content (TextField)
    # Optional teacher resource
```

### 5.2 No Complex Competency System (Yet)
- Start simple: Subjects and basic curriculum
- Add competencies later if needed
- Keep it practical and usable

---

## Phase 6: Student Model - Rename and Expand (Best Reuse Opportunity!)

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-06-student/`
- Tasks to be created (~12 tasks)
- See phase-06-student/README.md for planned tasks
- ⚠️ HIGH RISK - Major data migration required

### 6.1 Rename BMParliamentMember to Student
**Rename `BMParliamentMember` → `Student`** - it already has:
- ✅ Personal information (name, birth_date, gender, address)
- ✅ Family details (parents, guardians, household)
- ✅ **Madaris education fields already exist!**
- ✅ Educational background
- ✅ Special sectors tracking
- ✅ Status workflow

**Add minimal fields:**
- `student_number` (CharField)
- `enrollment_status` (CharField choices)
- Keep everything else as-is

### 6.2 Rename Model: BMParliamentMember → Student
- Create Django migration: `rename_model('constituents', 'BMParliamentMember', 'Student')`
- All references in code: `Student` (instead of BMParliamentMember)
- Database table: Rename `constituents_bmparlimentmember` → `constituents_student`
- Update all imports, forms, templates, and admin registrations
- Keep all existing fields and functionality intact

### 6.3 Student Model - Profile for Enrolled Students Only
- **REMOVE** `Constituent` model entirely
- `Student` (BMParliamentMember renamed): Profile for **students enrolled in madaris only**
  - Fields: enrollment, academic records, family details, birth_date, gender, address, etc.
- `Teacher`/`Asatidz` (separate model): Profile for **teaching staff** (created in Phase 4)
- `Parent` (separate model): Profile for **guardians/parents** (created in Phase 9)
- `User` (Django auth): Base account for admins and staff (no profile extension needed)
- Role differentiation: `User.role` field determines access and permissions, NOT the profile model
- Migration: Migrate all Constituent data to appropriate Student/Teacher/Parent records based on role
- Update references in related models (Chapter → Madrasah, ChapterMembership → StudentEnrollment, etc.)

---

## Phase 7: Academic Records - Lightweight Addition

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-07-academic/`
- Tasks to be created (~10 tasks)
- See phase-07-academic/README.md for planned tasks

### 7.1 Create Minimal `apps/academics/`
**Only core models:**
```python
class AcademicYear(models.Model):
    year, start_date, end_date, status

class Class(models.Model):
    madrasah (FK to Madrasah model)
    teacher (FK to User with role='asatidz')
    subject (FK to Subject)
    grade_level, section, schedule (JSONField)

class Attendance(models.Model):
    student (FK to User), class (FK), date, status

class Grade(models.Model):
    student (FK to User), class (FK), period, score
```

### 7.2 No Over-Engineering
- Simple grading (not complex rubrics initially)
- Basic attendance tracking
- Can expand later

---

## Phase 8: Programs - Adapt MinistryProgram (Minimal Changes)

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-08-programs/`
- Tasks to be created (~10 tasks)
- See phase-08-programs/README.md for planned tasks

### 8.1 Keep `apps/services/` Structure
**Adapt `MinistryProgram`:**
- Add `program_category` choices: add 'scholarship', 'teacher_training', 'curriculum'
- Keep all existing fields: ministry, budget, timeline
- Use for educational programs, scholarships, training

**Adapt `ServiceApplication`:**
- Use for student scholarship applications
- Use for teacher training enrollments
- Keep existing workflow

### 8.2 Reuse ServiceProgram
- Keep for direct services
- Adapt for educational assistance programs
- No new models needed

---

## Phase 9: Parent Portal - Extend User System

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-09-parent/`
- Tasks to be created (~10 tasks)
- See phase-09-parent/README.md for planned tasks

### 9.1 Minimal Parent Integration
**Add to `apps/users/models.py`:**
```python
class ParentStudent(models.Model):
    parent (FK to User with role='parent')
    student (FK to User with role='student')
    relationship (CharField)
```

### 9.2 Reuse Student Model Family Fields
- Student model already has parent/guardian information fields
- Create User accounts for parents (role='parent')
- Link parents to students via ParentStudent junction table
- No need for separate Parent profile model

---

## Phase 10: Adapt Existing Features (Minimal Changes)

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-10-adapt/`
- Tasks to be created (~8 tasks)
- See phase-10-adapt/README.md for planned tasks

### 10.1 Keep As-Is
- ✅ `apps/documents/` - perfect for certificates, transcripts
- ✅ `apps/notifications/` - use for school communications
- ✅ `apps/dashboards/` - adapt queries for academic metrics
- ✅ `apps/analytics/` - adapt for enrollment/attendance stats

### 10.2 Soft-Remove Parliamentary Features
- Keep `apps/referrals/` but hide in UI (might be useful later)
- Keep `apps/parliamentary/` but deactivate in settings
- Don't delete code - just don't expose in navigation

---

## Phase 11: Forms - Adapt Existing

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-11-forms/`
- Tasks to be created (~6 tasks)
- See phase-11-forms/README.md for planned tasks

### 11.1 Reuse Forms with Field Updates
- `StudentForm` (renamed from BMParliamentMemberForm) → add student-specific fields, relabel
- `MadrasahForm` (renamed from ChapterForm) → add madrasah-specific fields, relabel
- Keep all existing form infrastructure
- Update `forms.py` minimally

### 11.2 Keep Crispy Forms + Tailwind
- All existing form layouts work
- Just update field labels and help text
- Add new fields where needed

---

## Phase 12: Templates - Contextual Display

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-12-templates/`
- Tasks to be created (~5 tasks)
- See phase-12-templates/README.md for planned tasks

### 12.1 Template Variable Context
Create `apps/core/context_processors.py`:
```python
def system_context(request):
    return {
        'SYSTEM_NAME': 'Tarbiyyah Management System',
        'MEMBER_LABEL': 'Student',
        'CHAPTER_LABEL': 'School',
        'ACTIVITY_LABEL': 'Event',
        # etc.
    }
```

### 12.2 Update Templates with Variables
- Replace hardcoded "Chapter" with `{{ MADRASAH_LABEL }}`
- Replace "Member" with `{{ STUDENT_LABEL }}`
- Add context variables in settings: `MADRASAH_LABEL = "Madrasah"`, `STUDENT_LABEL = "Student"`
- Minimal template changes - mostly substitution

### 12.3 Reuse Atomic Components
- Keep all atoms, molecules, organisms
- Just update text content
- No structural changes

---

## Phase 13: Database Strategy - Additive Only

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-13-database/`
- Tasks to be created (~8 tasks)
- See phase-13-database/README.md for planned tasks

### 13.1 Zero Destructive Migrations
- **Never drop columns** - mark as deprecated instead
- **Rename models/tables for clarity** - Django's RenameModel preserves all data (zero data loss)
- **Never DROP tables** - only rename or add new ones
- Only ADD fields after renaming
- Keep all existing data - 100% data preservation

### 13.2 Migration Approach

**Step 1: Rename Models (Database Tables)**
```python
class Migration:
    operations = [
        # Rename database tables
        migrations.RenameModel(
            old_name='Chapter',
            new_name='Madrasah',
        ),  # Table: chapters_chapter → chapters_madrasah

        migrations.RenameModel(
            old_name='ChapterMembership',
            new_name='MadrasahEnrollment',
        ),  # Table: chapters_chaptermembership → chapters_madrasahenrollment

        migrations.RenameModel(
            old_name='BMParliamentMember',
            new_name='Student',
        ),  # Table: constituents_bmparlimentmember → constituents_student

        migrations.RenameModel(
            old_name='ChapterActivity',
            new_name='MadrasahActivity',
        ),  # Table: chapters_chapteractivity → chapters_madrasahactivity
    ]
```

**Step 2: Add New Fields**
```python
class Migration:
    operations = [
        AddField('Madrasah', 'school_code'),
        AddField('Madrasah', 'madrasah_types'),  # JSONField
        AddField('Student', 'student_number'),
        AddField('Student', 'enrollment_status'),
        # All old fields remain intact
    ]
```

### 13.3 Data Adaptation
- Existing chapters can be marked as `chapter_type='school'`
- Existing members can be marked as `student` role
- No data loss - only additions

---

## Pre-Implementation Checklist & Recommendations

### ⚠️ CRITICAL: Before Implementation

1. **Backup Everything**
   - Full database dump (PostgreSQL/MySQL backup)
   - Complete media files backup (user uploads, images, documents)
   - Git repository snapshot/tag (create release tag: `v1.0-pre-tarbiyyah`)
   - Environment configuration files (.env, settings)
   - Store backups in multiple locations (local + cloud storage)

2. **Test Migrations on Staging**
   - Set up staging environment identical to production
   - Run all RenameModel operations on staging database
   - Verify table renames: `constituents_bmparlimentmember` → `constituents_student`
   - Test data integrity: confirm all records preserved
   - Check foreign key relationships still work
   - Verify admin interface loads correctly with new model names

3. **Document Rollback Plan**
   - Prepare reverse migrations (Student → BMParliamentMember, etc.)
   - Document steps to restore from backup
   - Identify rollback decision points (when to abort implementation)
   - Test rollback procedure on staging environment
   - Keep database dump readily accessible during migration

4. **Stakeholder Sign-off**
   - Present plan to MBASICED/Tarbiyyah leadership
   - Confirm Islamic education terminology is culturally appropriate
   - Verify education levels align with BARMM standards
   - Get approval for role names (TARBIYYAH_ADMIN, MUDER, ASATIDZ)
   - Confirm madrasah types match actual school offerings
   - Obtain written approval before proceeding

### 📋 During Implementation Best Practices

1. **Follow Week-by-Week Plan Strictly**
   - Complete Phases 1-2 (Branding, Roles) before touching models
   - Never skip phases - each builds on previous work
   - Week 1 → Week 2 → Week 3 progression only
   - Do NOT implement Phase 5 before Phase 3 is stable

2. **Test After Each Phase**
   - Run full test suite after completing each phase
   - Manual testing of affected features
   - Verify admin interface functionality
   - Check user-facing pages render correctly
   - **Do not proceed to next phase until current phase is fully stable**

3. **Keep Old Parliamentary Features Hidden (Not Deleted)**
   - Follow Phase 10.2 approach: soft-remove, don't delete code
   - Hide `apps/referrals/` and `apps/parliamentary/` from UI navigation
   - Keep code in repository (commented out in urls.py)
   - Deactivate in settings: `INSTALLED_APPS` comments
   - Benefits: Easy rollback if needed, code preserved for reference

4. **Continuous Monitoring**
   - Monitor error logs after each deployment
   - Check database query performance (watch for N+1 queries)
   - Track user feedback on terminology changes
   - Monitor server resource usage (CPU, memory, disk)

5. **Communication**
   - Notify all users before major changes
   - Provide training for new terminology (Madrasah, Student, etc.)
   - Update user documentation and help guides
   - Set up support channel for questions during transition

---

## Implementation Steps (Practical Order)

### Week 1: Foundation
1. Update branding (templates, static files)
2. Add context processor for terminology
3. Add new role choices to User model
4. Create migrations for new roles

### Week 2: Core Adaptations
5. Rename Chapter → Madrasah, add madrasah-specific fields
6. Rename ChapterMembership → MadrasahEnrollment, add enrollment-specific fields
7. Rename BMParliamentMember → Student, add student-specific fields
8. Update forms to StudentForm and MadrasahForm with new fields

### Week 3: New Apps (Minimal)
9. Create `apps/teachers/` with TeacherProfile model
10. Create `apps/curriculum/` with Subject, CurriculumFramework
11. Create `apps/academics/` with Class, Grade, Attendance
12. Create migrations for new models

### Week 4: UI Adaptation
13. Update navigation menus
14. Update dashboard queries for academic context
15. Adapt forms and templates with new labels
16. Create role-specific dashboards (reuse dashboard app)

### Week 5: Parent Portal & Programs
17. Add ParentStudent model
18. Adapt MinistryProgram for educational programs
19. Update program application forms
20. Test parent portal access

### Week 6: Testing & Polish
21. Test all user roles and permissions
22. Test data entry workflows
23. Test reporting and analytics
24. Documentation updates

---

## What This Approach Achieves

✅ **Minimal code disruption** - Most models stay intact
✅ **Zero data loss** - All existing data preserved
✅ **Gradual transition** - Can run hybrid system during transition
✅ **Reuse proven code** - 85%+ of codebase unchanged
✅ **Fast implementation** - 4-6 weeks instead of 8-12
✅ **Low risk** - Additive changes only
✅ **Flexible** - Can keep chapter functionality if needed

---

## Key Reuse Summary

| Component | Strategy |
|-----------|----------|
| User model | ✅ Add new roles (TARBIYYAH_ADMIN, MADRASAH_ADMIN, MUDER, ASATIDZ, STUDENT, PARENT) |
| Chapter | ✅ **RENAME** to Madrasah, add madrasah-specific fields |
| ChapterMembership | ✅ **RENAME** to MadrasahEnrollment, add enrollment fields |
| BMParliamentMember | ✅ **RENAME** to Student, add student-specific fields |
| ChapterActivity | ✅ **RENAME** to MadrasahActivity, adapt for school events |
| Constituent | ❌ **REMOVE** entirely - replaced by Student/Teacher/Parent models |
| MinistryProgram | ✅ Adapt categories for educational programs |
| Documents | ✅ Use as-is for certificates, transcripts |
| Notifications | ✅ Use as-is for school communications |
| Dashboards | ✅ Adapt queries, reuse framework |
| Forms | ✅ **RENAME** to StudentForm, MadrasahForm; update fields |
| Templates | ✅ Update text with {{ MADRASAH_LABEL }}, {{ STUDENT_LABEL }} |

---

## New Components (Only What's Essential)

- `TeacherProfile` - Extends User for teacher-specific data
- `Subject`, `CurriculumFramework`, `LessonPlan` - Basic curriculum
- `AcademicYear`, `Class`, `Grade`, `Attendance` - Core academics
- `ParentStudent` - Simple parent-student link

**Total new models: ~10 (vs 30+ in full rebuild)**

---

## Geographic Scope: Hierarchical Structure

The system supports the following hierarchy:
- **Region Level**: BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)
- **Provincial Level**: Maguindanao del Norte, Maguindanao del Sur, Lanao del Sur, Basilan, Sulu, Tawi-Tawi
- **Municipal/City Level**: Municipalities and cities within provinces
- **School Level**: Individual madaris schools

This hierarchy is already supported by the existing Chapter model's parent-child relationship structure.

---

## Focus Areas (Per User Requirements)

1. **Teacher/Asatidz Management** - Phase 4
2. **Curriculum Management** - Phase 5
3. **Hierarchical Structure** - Supported by existing Chapter model
4. **New Role System** - Phase 2 with education-specific roles

---

## Notes

- This plan was created based on analysis of the existing BM Parliament codebase
- The approach prioritizes reuse and adaptation over rebuilding
- All database changes are additive (no data loss)
- The system can operate in a hybrid mode during transition

---

## Future Enhancement: Frontend Modernization (Separate Branch)

**Note:** This phase should be implemented **AFTER** completing all backend refactoring (Phases 1-13) in a **separate branch** to avoid mixing concerns.

### Phase 14: Next.js Frontend Migration (Optional Future Enhancement)

**Implementation Tasks:** `/docs/docs-new/tasks-refactor/phase-14-frontend/` **[DEFERRED]**
- task_015a.txt - Next.js 16 Frontend Implementation with React 19.2
- task_015b.txt - REST API Enhancement for Next.js Integration
- **Status:** Deferred to separate branch after Phases 1-13 complete

**Strategy:** Complete backend refactoring first, then modernize frontend separately

**Current Approach (Phases 1-13):**
- ✅ Complete all backend refactoring with Django templates
- ✅ Get fully functional TMS working with traditional Django views
- ✅ System is production-ready with Django templates
- ✅ All business logic in Django backend

**Future Frontend Migration (Phase 14 - Separate Branch):**
Once backend is stable and complete, optionally migrate to modern frontend:

### 14.1 Next.js Integration Strategy
**Approach:** Gradual API-first architecture while preserving Django backend
- Introduce **Next.js 16 with React 19.2** as frontend layer
- Keep Django as robust API backend (Django REST Framework)
- Maintain all existing business logic in Django
- TypeScript for type safety and better developer experience

### 14.2 API Development
**Enhance Django REST Framework:**
- Extend existing DRF endpoints for all models
- Add API endpoints for:
  - Madrasah CRUD operations
  - Student management
  - Teacher (Asatidz) management
  - Academic records
  - Parent portal data
- Keep API versioning (`/api/v1/`)
- JWT authentication for API access

### 14.3 Next.js Setup
**Create Next.js application in separate branch:**
- Initialize Next.js 16 with React 19.2 and TypeScript
- Configure Tailwind CSS (maintain design consistency)
- Set up API client for Django backend
- Implement server-side rendering (SSR) for SEO
- Leverage React 19.2 features (Actions, Suspense improvements)
- Progressive Web App (PWA) configuration
- Environment-based API endpoint configuration

### 14.4 Implementation Strategy
**Minimal disruption approach:**
- Create `frontend-migration` branch from stable main
- Deploy Next.js frontend separately
- Point to existing Django API
- Gradual page-by-page migration
- Django admin interface remains for superuser operations
- Both frontends can coexist during transition
- Merge to main only when Next.js frontend is feature-complete

### 14.5 Why Separate This Phase?

**Benefits of completing backend first:**
- ✅ **Focus:** Team focuses on one major change at a time (backend refactoring)
- ✅ **Risk Reduction:** Avoid mixing two complex migrations (data model + frontend)
- ✅ **Stability:** Get working system with Django templates first
- ✅ **Flexibility:** Frontend migration becomes optional/future enhancement
- ✅ **Branch Isolation:** Frontend work doesn't block backend deployment
- ✅ **Testing:** Easier to test backend changes without frontend complexity
- ✅ **Deployment:** Can deploy functional system before frontend modernization

**Implementation Timeline:**
- **Now:** Phases 1-13 (Backend refactoring with Django templates)
- **Later:** Phase 14 (Frontend migration in separate `frontend-migration` branch)

**Decision Point:**
After completing Phases 1-13, the Tarbiyyah Committee can decide:
- Option A: Keep Django templates (fully functional, no additional cost)
- Option B: Proceed with Next.js migration (modern UI, additional development time)

---

## Implementation Priority

**Immediate (Current Sprint):**
1. Phase 1: Branding & Configuration
2. Phase 2: User Roles
3. Phase 3: Madaris Management
4. Phases 4-13: Complete backend refactoring

**Future (Separate Branch, Optional):**
- Phase 14: Next.js Frontend Migration

This approach ensures a **working, production-ready system** with Django templates first, with frontend modernization as an optional future enhancement.

---

## Implementation Resources

### Task Files Organization

Detailed implementation tasks for this plan are located in:
**`/docs/docs-new/tasks-refactor/`**

Tasks are organized into **14 phase subdirectories** for easy navigation:

```
tasks-refactor/
├── phase-01-branding/      # 14 tasks - Branding & Configuration (No DB changes)
├── phase-02-roles/          # 10 tasks - User Roles & Permissions
├── phase-03-madaris/        # 20 tasks - Full Chapter → Madrasah transition
├── phase-04-teachers/       # 5 tasks - Asatidz (Teachers) app
├── phase-05-curriculum/     # Tasks to be created - Curriculum Management
├── phase-06-student/        # Tasks to be created - Student Model transition
├── phase-07-academic/       # Tasks to be created - Academic Records
├── phase-08-programs/       # Tasks to be created - Programs Adaptation
├── phase-09-parent/         # Tasks to be created - Parent Portal
├── phase-10-adapt/          # Tasks to be created - Adaptation & Integration
├── phase-11-forms/          # Tasks to be created - Forms Cleanup
├── phase-12-templates/      # Tasks to be created - Templates Cleanup
├── phase-13-database/       # Tasks to be created - Database Final Cleanup
└── phase-14-frontend/       # 2 tasks - Next.js Frontend (DEFERRED)
```

### Quick Start Guides

- **START_HERE.md** - Quick start guide for parallel task execution
- **CLAUDE_CODE_PARALLEL_EXECUTION.md** - Guide for using Claude Code agents
- **README.md** - Task organization overview and progress tracking

### Phase Documentation

Each phase directory contains:
- **README.md** - Phase overview, task list, dependencies, risk assessment
- **task_XXX.txt** - Detailed step-by-step implementation tasks

### Current Status (November 20, 2025)

- ✅ **Ready for Implementation:** Phases 1-4 (49 tasks created)
- 📋 **To Be Created:** Phases 5-13 (~79 tasks planned)
- ⏸️ **Deferred:** Phase 14 (2 tasks - Next.js Frontend)

### Related Documentation

- **UI_NAVIGATION_PLAN.md** - Multitenant navigation architecture (5 role-based navbars)
- **TMS_DEVELOPMENT_PROPOSAL.md** - Cost proposal and timeline
- **CLAUDE.md** (`/docs/CLAUDE.md`) - Instructions for Claude Code agents

---

## Changelog

**Version History:**

- **v1.6.2** (November 20, 2025): Added task file references to all 14 phases; Each phase now lists specific implementation tasks with file paths; Links to phase subdirectories in `/docs/docs-new/tasks-refactor/`; Added task counts and status indicators
- **v1.6.1** (November 20, 2025): Added "Implementation Resources" section documenting the new task organization into 14 phase subdirectories; Added references to quick start guides and phase-specific README files; Updated current status showing 49 tasks ready for implementation
- **v1.6.0** (November 20, 2025): **Major architectural change** - Moved Next.js frontend migration from Phase 1.5 to Phase 14 (Future Enhancement); Backend refactoring (Phases 1-13) will be completed first with Django templates; Next.js migration becomes optional future enhancement in separate branch
- **v1.5.1**: Added comprehensive Pre-Implementation Checklist & Recommendations section with backup procedures, staging testing requirements, rollback planning, stakeholder sign-off, and implementation best practices
- **v1.5.0**: **Major architectural clarification** - Student model approach changed to direct rename (not adapter/wrapper); Constituent model removed entirely and replaced by Student/Teacher/Parent models with role-based differentiation; Updated all form names (StudentForm, MadrasahForm); Updated template variables (MADRASAH_LABEL, STUDENT_LABEL); Clarified TARBIYYAH_ADMIN as system admin below superuser; Updated implementation steps and summary table for consistency
- **v1.4.8**: Added "Permanently Closed" to OperationalStatus choices
- **v1.4.7**: Added `offers_hadith_studies` (Ilm al-Hadith) to curriculum offerings
- **v1.4.6**: Renamed `has_prayer_hall` to `has_masjid` for Islamic school context
- **v1.4.5**: Added "Poor" to FacilityLevel choices
- **v1.4.4**: Added "Rejected" to AccreditationStatus choices
- **v1.4.3**: Changed madrasah_type to madrasah_types (JSONField, multi-select) to support madaris offering multiple education levels
- **v1.4.2**: Revised madrasah types: Ibtidaiyyah, I'dadiyyah, Thanawiyyah, Kulliyah, Integrated, Tahfidz
- **v1.4.1**: Added KULLIYYAH (Tertiary/Higher Education) to madrasah types
- **v1.4**: **Phase 3 - Full transition to Madaris**: Complete refactoring from chapters to madaris with comprehensive model architecture and forms
- **v1.3**: Changed role names to Islamic education terminology: `SCHOOL_PRINCIPAL` → `MUDER`, `TEACHER` → `ASATIDZ`
- **v1.2**: Renamed `coordinator` role to `MADRASAH_ADMIN`
- **v1.1**: Changed `MBASICED_OFFICER` to `TARBIYYAH_ADMIN`
- **v1.0**: Initial plan

---

**Note:** Parliamentary features are soft-hidden, not deleted
