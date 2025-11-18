from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from apps.users.models import User
from .member_models import FahanieCaresMember
from .utils import MUNICIPALITY_CHOICES_DATA # Import the centralized data

class FahanieCaresMemberRegistrationForm(UserCreationForm):
    """
    Comprehensive registration form for #FahanieCares members
    """
    # Personal Information
    last_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    first_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name'})
    )
    
    phone_regex = RegexValidator(
        regex=r'^(\+63|63|0)?9\d{9}$',
        message="Phone number must be entered in the format: '+639999999999', '639999999999', or '09999999999'. Philippine mobile numbers only."
    )
    contact_number = forms.CharField(
        validators=[phone_regex], 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Contact Number'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    
    age = forms.IntegerField(
        min_value=1, 
        max_value=120,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Age'})
    )
    
    sex = forms.ChoiceField(
        choices=FahanieCaresMember.SEX_CHOICES,
        required=True,
        initial='male',
        widget=forms.RadioSelect()
    )
    
    # Province choices for Maguindanao region
    PROVINCE_CHOICES = [
        ('', '-- Select Province --'),
        ('Maguindanao del Sur', 'Maguindanao del Sur'),
        ('Maguindanao del Norte', 'Maguindanao del Norte'),
        ('Cotabato City', 'Cotabato City'),
        ('Special Geographic Areas', 'Special Geographic Areas'),
    ]
    
    # Current Address
    address_barangay = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barangay'})
    )
    address_municipality = forms.ChoiceField(
        choices=[('', '-- Select Municipality --')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'current'})
    )
    address_province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        initial='Maguindanao del Sur',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'current'})
    )
    
    # Voter Registration Address
    voter_address_barangay = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Voter Registration Barangay'})
    )
    voter_address_municipality = forms.ChoiceField(
        choices=[('', '-- Select Municipality --')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'voter'})
    )
    voter_address_province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        initial='Maguindanao del Sur',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'voter'})
    )
    
    # Sector Information
    sector = forms.ChoiceField(
        choices=FahanieCaresMember.SECTOR_CHOICES,
        required=True,
        initial='pwd_student', # The key remains the same, only the display value changed in models
        widget=forms.RadioSelect()
    )
    
    # Education Information
    highest_education = forms.ChoiceField(
        choices=FahanieCaresMember.EDUCATION_CHOICES,
        required=True,
        initial='elementary',
        widget=forms.RadioSelect()
    )
    school_graduated = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Graduated From'})
    )
    eligibility = forms.ChoiceField(
        choices=FahanieCaresMember.ELIGIBILITY_CHOICES,
        required=True,
        initial='none', # The key remains the same, only the display value changed in models
        widget=forms.RadioSelect()
    )

    # College Student Specific Information
    college_school = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of College/University'})
    )
    year_level = forms.ChoiceField(
        choices=[('', '-- Select Year Level --')] + list(FahanieCaresMember._meta.get_field('year_level').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # PWD Specific Information
    pwd_disability_type = forms.ChoiceField(
        choices=[
            ('', '-- Select Disability Type --'),
            ('physical', 'Physical Disability'),
            ('mental', 'Mental/Intellectual Disability'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # LGBTQ Community Specific Information
    lgbtq_identity = forms.ChoiceField(
        choices=[
            ('', '-- Select LGBTQ+ Identity --'),
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
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    
    # Verification Photo
    voter_id_photo = forms.ImageField(
        required=True,
        label="Voter's Certificate Photo",
        help_text="Upload a clear photo of your most recent Voter's Certificate (latest 6 months only) for verification.",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    # Terms and Conditions
    # Terms and Conditions
    terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions and data privacy policy"
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Initialize municipality choices with all possible municipalities for validation
        # This allows form validation to pass while JavaScript handles the UI filtering
        all_municipalities = []
        for province_muns in MUNICIPALITY_CHOICES_DATA.values():
            all_municipalities.extend(province_muns)
        
        municipality_choices = [('', '-- Select Municipality --')] + [(m, m) for m in sorted(list(set(all_municipalities)))]
        self.fields['address_municipality'].choices = municipality_choices
        self.fields['voter_address_municipality'].choices = municipality_choices
        
        # Update all widget classes to use Tailwind CSS
        tailwind_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder-gray-500'
        checkbox_classes = 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        radio_classes = 'form-radio h-4 w-4 text-primary-600 transition duration-150 ease-in-out' # Added for radio buttons
        
        # Update form widget classes
        for field_name, field in self.fields.items():
            if field_name == 'terms':
                field.widget.attrs['class'] = checkbox_classes
            elif field_name in ['sex', 'sector', 'highest_education', 'eligibility']:
                # Apply radio_classes to the RadioSelect widget's individual inputs
                # Django's RadioSelect renders a list of radio inputs, so we apply to the widget itself
                field.widget.attrs['class'] = radio_classes
            elif field_name == 'voter_id_photo':
                # Apply proper styling for file input
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent'
                field.widget.attrs['accept'] = 'image/*' 
            elif field_name in ['address_province', 'voter_address_province', 'address_municipality', 'voter_address_municipality']:
                # Select/dropdown widgets
                field.widget.attrs['class'] = tailwind_classes
                # Keep data attributes for JavaScript handling
                if 'data-address-type' in field.widget.attrs:
                    data_type = field.widget.attrs['data-address-type']
                    field.widget.attrs['data-address-type'] = data_type
            else:
                field.widget.attrs['class'] = tailwind_classes
        
        # Add specific placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username (will be used for login)'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        
        # Add password help text
        self.fields['password1'].help_text = (
            'Password must be at least 8 characters long and be alphanumeric '
            '(contain both letters and numbers).'
        )
        
        # Debug: Log form binding state
        logger.info(f"Form initialized - Bound: {self.is_bound}, POST data present: {'data' in kwargs}")
        if self.is_bound and hasattr(self, 'data'):
            logger.info(f"Form data keys: {list(self.data.keys())}")
            logger.info(f"Radio field values in form data - sex: {self.data.get('sex')}, sector: {self.data.get('sector')}")
    
    
    def clean_voter_id_photo(self):
        """Validate voter ID photo upload"""
        photo = self.cleaned_data.get('voter_id_photo')
        
        if photo:
            # Check file size (5MB limit)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size too large. Please upload a file smaller than 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(photo, 'content_type') and photo.content_type not in allowed_types:
                raise forms.ValidationError("Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.")
            
            # Additional check on file extension
            import os
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise forms.ValidationError("Invalid file extension. Allowed extensions: .jpg, .jpeg, .png, .gif, .webp")
        
        return photo
    
    def clean(self):
        import logging
        logger = logging.getLogger(__name__)
        
        cleaned_data = super().clean()
        
        # Debug: Log received radio button values
        logger.info(f"Form data received - Sex: {cleaned_data.get('sex')}, Sector: {cleaned_data.get('sector')}, Education: {cleaned_data.get('highest_education')}, Eligibility: {cleaned_data.get('eligibility')}")
        
        email = cleaned_data.get('email')
        
        # Don't do redundant validation - Django already validates required fields
        # Just log if fields are missing for debugging
        required_radio_fields = ['sex', 'sector', 'highest_education', 'eligibility']
        for field_name in required_radio_fields:
            if not cleaned_data.get(field_name):
                logger.warning(f"Radio field {field_name} is missing from cleaned data")
        
        # Check for duplicate email (optimized query)
        if email:
            from apps.users.models import User
            if User.objects.filter(email=email).only('id').exists():
                self.add_error('email', "An account with this email address already exists. Please use a different email or try logging in.")
        
        # Check for duplicate username
        username = cleaned_data.get('username')
        if username:
            from apps.users.models import User
            if User.objects.filter(username=username).only('id').exists():
                self.add_error('username', "This username is already taken. Please choose a different username.")

        # Check for duplicate names (first_name, last_name)
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if first_name and last_name:
            if FahanieCaresMember.objects.filter(first_name=first_name, last_name=last_name).exists():
                self.add_error('first_name', "A member with this first name and last name already exists.")
                self.add_error('last_name', "A member with this first name and last name already exists.")
        
        return cleaned_data
    
    def save(self, commit=True):
        import logging
        from django.db import transaction
        logger = logging.getLogger(__name__)
        
        if not commit:
            return super().save(commit=False)
        
        # Use database transaction for atomicity
        try:
            with transaction.atomic():
                # Save User instance
                user = super().save(commit=False)
                user.user_type = 'member'
                # New registrations are not approved by default
                user.is_approved = False
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.middle_name = self.cleaned_data['middle_name']
                user.email = self.cleaned_data['email']
                user.phone_number = self.cleaned_data['contact_number']
                user.save()
                
                logger.info(f"User created successfully: {user.username}")
                
                # Create FahanieCaresMember instance
                member = FahanieCaresMember(
                    user=user,
                    last_name=self.cleaned_data['last_name'],
                    first_name=self.cleaned_data['first_name'],
                    middle_name=self.cleaned_data['middle_name'],
                    contact_number=self.cleaned_data['contact_number'],
                    email=self.cleaned_data['email'],
                    age=self.cleaned_data['age'],
                    sex=self.cleaned_data['sex'],
                    address_barangay=self.cleaned_data['address_barangay'],
                    address_municipality=self.cleaned_data['address_municipality'],
                    address_province=self.cleaned_data['address_province'],
                    voter_address_barangay=self.cleaned_data['voter_address_barangay'],
                    voter_address_municipality=self.cleaned_data['voter_address_municipality'],
                    voter_address_province=self.cleaned_data['voter_address_province'],
                    sector=self.cleaned_data['sector'],
                    highest_education=self.cleaned_data['highest_education'],
                    school_graduated=self.cleaned_data.get('school_graduated', ''),
                    eligibility=self.cleaned_data['eligibility'],
                    college_school=self.cleaned_data.get('college_school', ''),
                    year_level=self.cleaned_data.get('year_level', ''),
                    pwd_disability_type=self.cleaned_data.get('pwd_disability_type', ''),
                    lgbtq_identity=self.cleaned_data.get('lgbtq_identity', ''),
                    voter_id_photo=self.cleaned_data.get('voter_id_photo', None),
                    status='pending'  # Explicitly set status to 'pending' for new registrations
                )
                member.save()
                
                logger.info(f"FahanieCaresMember created successfully: {member.id}")
                
                # Log successful completion
                logger.info(f"Registration completed successfully for user: {user.username}")
                
            return user
            
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(f"Error saving member registration for user {getattr(user, 'username', 'unknown')}: {str(e)}", exc_info=True)
            
            # Provide a user-friendly error message
            error_message = "An error occurred while processing your registration. "
            
            # Check for common error types
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                error_message += "This email or username is already registered. Please use different credentials or try logging in."
            elif "permission" in str(e).lower():
                error_message += "There was a temporary issue with file uploads. Your registration data has been saved, but you may need to upload your ID photo later."
            else:
                error_message += "Please check your information and try again. If the problem persists, please contact support."
            
            raise forms.ValidationError(error_message)


class FahanieCaresMemberUpdateForm(forms.ModelForm):
    """
    Form for updating member information
    """
    # Personal Information
    last_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    first_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name'})
    )
    
    phone_regex = RegexValidator(
        regex=r'^(\+63|63|0)?9\d{9}$',
        message="Phone number must be entered in the format: '+639999999999', '639999999999', or '09999999999'. Philippine mobile numbers only."
    )
    contact_number = forms.CharField(
        validators=[phone_regex], 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Contact Number'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    
    age = forms.IntegerField(
        min_value=1, 
        max_value=120,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Age'})
    )
    
    sex = forms.ChoiceField(
        choices=FahanieCaresMember.SEX_CHOICES,
        required=True,
        initial='male',
        widget=forms.RadioSelect()
    )
    
    # Province choices for Maguindanao region
    PROVINCE_CHOICES = [
        ('', '-- Select Province --'),
        ('Maguindanao del Sur', 'Maguindanao del Sur'),
        ('Maguindanao del Norte', 'Maguindanao del Norte'),
        ('Cotabato City', 'Cotabato City'),
        ('Special Geographic Areas', 'Special Geographic Areas'),
    ]
    
    # Current Address
    address_barangay = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barangay'})
    )
    address_municipality = forms.ChoiceField(
        choices=[('', '-- Select Municipality --')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'current'})
    )
    address_province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        initial='Maguindanao del Sur',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'current'})
    )
    
    # Voter Registration Address
    voter_address_barangay = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Voter Registration Barangay'})
    )
    voter_address_municipality = forms.ChoiceField(
        choices=[('', '-- Select Municipality --')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'voter'})
    )
    voter_address_province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        initial='Maguindanao del Sur',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'data-address-type': 'voter'})
    )
    
    # Sector Information
    sector = forms.ChoiceField(
        choices=FahanieCaresMember.SECTOR_CHOICES,
        required=True,
        initial='pwd_student', # The key remains the same, only the display value changed in models
        widget=forms.RadioSelect()
    )
    
    # Education Information
    highest_education = forms.ChoiceField(
        choices=FahanieCaresMember.EDUCATION_CHOICES,
        required=True,
        initial='elementary',
        widget=forms.RadioSelect()
    )
    school_graduated = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Graduated From'})
    )
    eligibility = forms.ChoiceField(
        choices=FahanieCaresMember.ELIGIBILITY_CHOICES,
        required=True,
        initial='none', # The key remains the same, only the display value changed in models
        widget=forms.RadioSelect()
    )
    
    
    # Verification Photo
    voter_id_photo = forms.ImageField(
        required=False,
        label="Voter's Certificate or ID Photo",
        help_text="Upload a clear photo of your most recent Voter's Certificate or ID for verification.",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=FahanieCaresMember.STATUS_CHOICES,
        required=False, # Make it not required for user updates
        widget=forms.HiddenInput() # Hide it from the user, as it's managed by the system
    )

    class Meta:
        model = FahanieCaresMember
        exclude = ['user', 'date_of_application', 'is_approved', 'approved_by', 'is_volunteer_teacher', 'volunteer_school', 'volunteer_service_length', 'approved_date', 'denied_date', 'denied_by', 'denial_reason', 'assigned_chapter', 'chapter_assigned_date', 'chapter_assigned_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize municipality choices with all possible municipalities for validation
        # This allows form validation to pass while JavaScript handles the UI filtering
        all_municipalities = []
        for province_muns in MUNICIPALITY_CHOICES_DATA.values():
            all_municipalities.extend(province_muns)
        
        municipality_choices = [('', '-- Select Municipality --')] + [(m, m) for m in sorted(list(set(all_municipalities)))]
        self.fields['address_municipality'].choices = municipality_choices
        self.fields['voter_address_municipality'].choices = municipality_choices

        # Apply Tailwind CSS classes to all widgets
        tailwind_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder-gray-500'
        checkbox_classes = 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        radio_classes = 'form-radio h-4 w-4 text-primary-600 transition duration-150 ease-in-out'
        
        # Apply Tailwind CSS classes to specific widgets
        self.fields['voter_id_photo'].widget.attrs['class'] = tailwind_classes
        self.fields['voter_id_photo'].widget.attrs['accept'] = 'image/*'
        
        for field_name in ['sex', 'sector', 'highest_education', 'eligibility']:
            self.fields[field_name].widget.attrs['class'] = radio_classes
            
        for field_name in ['address_province', 'voter_address_province', 'address_municipality', 'voter_address_municipality']:
            self.fields[field_name].widget.attrs['class'] = tailwind_classes
            if 'data-address-type' in self.fields[field_name].widget.attrs:
                data_type = self.fields[field_name].widget.attrs['data-address-type']
                self.fields[field_name].widget.attrs['data-address-type'] = data_type
        
        # Apply to other text/number/email fields
        for field_name in ['last_name', 'first_name', 'middle_name', 'contact_number', 'email', 'age', 'address_barangay', 'voter_address_barangay', 'school_graduated']:
            self.fields[field_name].widget.attrs['class'] = tailwind_classes

        # Set initial values for fields if instance exists
        if self.instance and self.instance.pk:
            # Set province values
            self.fields['address_province'].initial = self.instance.address_province
            self.fields['voter_address_province'].initial = self.instance.voter_address_province
            
            # Set initial values for explicitly defined RadioSelect fields
            self.fields['sex'].initial = self.instance.sex
            self.fields['sector'].initial = self.instance.sector
            self.fields['highest_education'].initial = self.instance.highest_education
            self.fields['eligibility'].initial = self.instance.eligibility
            
            # Set initial value for status field
            self.fields['status'].initial = self.instance.status

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
