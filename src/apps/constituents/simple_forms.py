from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from apps.users.models import User
from .member_models import FahanieCaresMember


class SimpleMemberRegistrationForm(UserCreationForm):
    """
    Simplified registration form for when the main form has issues
    """
    # Basic Information Only
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    
    phone_regex = RegexValidator(
        regex=r'^(\+63|63|0)?9\d{9}$',
        message="Phone number must be entered in the format: '+639999999999', '639999999999', or '09999999999'."
    )
    contact_number = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    
    age = forms.IntegerField(min_value=1, max_value=120, required=True)
    sex = forms.ChoiceField(choices=FahanieCaresMember.SEX_CHOICES, required=True)
    
    # Basic address
    municipality = forms.CharField(max_length=100, required=True)
    
    # Sector
    sector = forms.ChoiceField(choices=FahanieCaresMember.SECTOR_CHOICES, required=True)
    
    # Terms
    terms = forms.BooleanField(required=True, label="I agree to the terms and conditions")
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        # Create user quickly
        user = super().save(commit=False)
        user.user_type = 'member'
        user.is_approved = False
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['contact_number']
        
        if commit:
            user.save()
            
            # Create simplified member record
            FahanieCaresMember.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                contact_number=self.cleaned_data['contact_number'],
                age=self.cleaned_data['age'],
                sex=self.cleaned_data['sex'],
                address_municipality=self.cleaned_data['municipality'],
                address_province='Maguindanao del Sur',  # Default
                voter_address_municipality=self.cleaned_data['municipality'],
                voter_address_province='Maguindanao del Sur',  # Default
                sector=self.cleaned_data['sector'],
                highest_education='high_school',  # Default
                eligibility='none',  # Default
                address_barangay='TBD',  # To be determined later
                voter_address_barangay='TBD',  # To be determined later
                middle_name='',
                school_graduated='',
                is_volunteer_teacher=False,
                volunteer_school='',
                volunteer_service_length='',
            )
        
        return user