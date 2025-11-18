from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Cooperative, CooperativeMembership, CooperativeOfficer
from apps.constituents.models import FahanieCaresMember

User = get_user_model()

class CooperativeRegistrationForm(forms.ModelForm):
    date_registered = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    registration_certificate = forms.FileField(required=False)
    articles_of_cooperation = forms.FileField(required=False)
    bylaws = forms.FileField(required=False)

    class Meta:
        model = Cooperative
        fields = [
            'name', 'registration_number', 'cooperative_type', 'status',
            'address', 'barangay', 'municipality', 'province',
            'contact_number', 'email', 'date_established', 'date_registered',
            'description', 'total_members', 'registration_certificate',
            'articles_of_cooperation', 'bylaws'
        ]
        widgets = {
            'date_established': forms.DateInput(attrs={'type': 'date'}),
        }

class CooperativeOfficerSelectionForm(forms.ModelForm):
    fahaniecares_member = forms.ModelChoiceField(
        queryset=FahanieCaresMember.objects.filter(status='approved'),
        widget=forms.Select(attrs={'class': 'select2'})
    )

    class Meta:
        model = CooperativeMembership
        fields = [
            'fahaniecares_member', 'position', 'date_joined', 'date_appointed',
            'term_start', 'term_end', 'is_active', 'is_founding_member',
            'membership_number', 'shares_owned', 'notes'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_appointed': forms.DateInput(attrs={'type': 'date'}),
            'term_start': forms.DateInput(attrs={'type': 'date'}),
            'term_end': forms.DateInput(attrs={'type': 'date'}),
        }

class CooperativeOfficerForm(forms.ModelForm):
    fahaniecares_member = forms.ModelChoiceField(
        queryset=FahanieCaresMember.objects.filter(status='approved'),
        widget=forms.Select(attrs={'class': 'select2'})
    )

    class Meta:
        model = CooperativeOfficer
        fields = [
            'fahaniecares_member', 'position', 'date_joined', 'date_appointed',
            'term_start', 'term_end', 'is_active'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_appointed': forms.DateInput(attrs={'type': 'date'}),
            'term_start': forms.DateInput(attrs={'type': 'date'}),
            'term_end': forms.DateInput(attrs={'type': 'date'}),
        }

class EnhancedOfficerRegistrationForm(forms.Form):
    """
    Combined form for registering a new FahanieCares member and making them a cooperative officer
    """
    
    # FahanieCares Member Information
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name (Optional)'})
    )
    contact_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+63 XXX XXX XXXX'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'})
    )
    sex = forms.ChoiceField(
        choices=FahanieCaresMember.SEX_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Current Address
    address_barangay = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barangay'})
    )
    address_municipality = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipality'})
    )
    address_province = forms.CharField(
        max_length=100,
        initial='Maguindanao del Sur',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Voter Registration Address
    voter_address_barangay = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Voter Barangay'})
    )
    voter_address_municipality = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Voter Municipality'})
    )
    voter_address_province = forms.CharField(
        max_length=100,
        initial='Maguindanao del Sur',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Sector and Education
    sector = forms.ChoiceField(
        choices=FahanieCaresMember.SECTOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    highest_education = forms.ChoiceField(
        choices=FahanieCaresMember.EDUCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    school_graduated = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Graduated (Optional)'})
    )
    eligibility = forms.ChoiceField(
        choices=FahanieCaresMember.ELIGIBILITY_CHOICES,
        initial='none',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Voter ID Photo
    voter_id_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    # Officer-Specific Information
    position = forms.ChoiceField(
        choices=CooperativeMembership.POSITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_joined = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_appointed = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    term_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    term_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check for existing member with same name
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        middle_name = cleaned_data.get('middle_name', '')
        
        if first_name and last_name:
            existing_member = FahanieCaresMember.objects.filter(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name
            ).first()
            
            if existing_member:
                raise ValidationError(
                    f"A FahanieCares member with the name '{first_name} {middle_name} {last_name}' already exists."
                )
        
        return cleaned_data
    
    def save(self, cooperative, user):
        """
        Create both FahanieCares member and cooperative officer in a single transaction
        """
        with transaction.atomic():
            # Create User account first
            username = f"{self.cleaned_data['first_name'].lower()}.{self.cleaned_data['last_name'].lower()}"
            # Ensure unique username
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user_account = User.objects.create_user(
                username=username,
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=User.objects.make_random_password()  # Generate random password
            )
            
            # Create FahanieCares member
            member = FahanieCaresMember.objects.create(
                user=user_account,
                last_name=self.cleaned_data['last_name'],
                first_name=self.cleaned_data['first_name'],
                middle_name=self.cleaned_data.get('middle_name', ''),
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
                voter_id_photo=self.cleaned_data.get('voter_id_photo'),
                status='approved',  # Auto-approve since it's staff-initiated
                approved_date=timezone.now().date(),
                approved_by=user
            )
            
            # Create cooperative officer
            officer = CooperativeOfficer.objects.create(
                cooperative=cooperative,
                fahaniecares_member=member,
                position=self.cleaned_data['position'],
                date_joined=self.cleaned_data['date_joined'],
                date_appointed=self.cleaned_data.get('date_appointed'),
                term_start=self.cleaned_data.get('term_start'),
                term_end=self.cleaned_data.get('term_end'),
                is_active=self.cleaned_data.get('is_active', True)
            )
            
            return officer, member

class BulkOfficerRegistrationForm(forms.Form):
    # This form will be more complex and will likely require a formset
    # For now, I'll define the basic fields for a single officer
    
    last_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    contact_number = forms.CharField(max_length=20)
    email = forms.EmailField()
    
    position = forms.ChoiceField(choices=CooperativeMembership.POSITION_CHOICES)
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    term_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    term_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
