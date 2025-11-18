from django import forms
from .member_models import FahanieCaresMember
from apps.users.models import User
from django.forms import formset_factory
from django.core.exceptions import ValidationError

# Define choices for provinces and municipalities
PROVINCE_CHOICES = [
    ('', 'Select Province'),
    ('Maguindanao del Sur', 'Maguindanao del Sur'),
    ('Maguindanao del Norte', 'Maguindanao del Norte'),
    ('Cotabato City', 'Cotabato City'),
    ('Special Geographic Areas', 'Special Geographic Areas'),
]

MUNICIPALITY_CHOICES_MAP = {
    'Maguindanao del Sur': [
        ('Ampatuan', 'Ampatuan'), ('Buluan', 'Buluan'), ('Datu Abdullah Sangki', 'Datu Abdullah Sangki'),
        ('Datu Anggal Midtimbang', 'Datu Anggal Midtimbang'), ('Datu Hoffer Ampatuan', 'Datu Hoffer Ampatuan'),
        ('Datu Montawal', 'Datu Montawal'), ('Datu Paglas', 'Datu Paglas'), ('Datu Piang', 'Datu Piang'),
        ('Datu Salibo', 'Datu Salibo'), ('Datu Saudi Ampatuan', 'Datu Saudi Ampatuan'), ('Datu Unsay', 'Datu Unsay'),
        ('General Salipada K. Pendatun', 'General Salipada K. Pendatun'), ('Guindulungan', 'Guindulungan'),
        ('Mamasapano', 'Mamasapano'), ('Mangudadatu', 'Mangudadatu'), ('Pagalungan', 'Pagalungan'),
        ('Paglat', 'Paglat'), ('Pandag', 'Pandag'), ('Rajah Buayan', 'Rajah Buayan'),
        ('Shariff Aguak', 'Shariff Aguak'), ('Shariff Saydona Mustapha', 'Shariff Saydona Mustapha'),
        ('South Upi', 'South Upi'), ('Sultan sa Barongis', 'Sultan sa Barongis'), ('Talayan', 'Talayan')
    ],
    'Maguindanao del Norte': [
        ('Barira', 'Barira'), ('Buldon', 'Buldon'), ('Datu Blah Sinsuat', 'Datu Blah Sinsuat'),
        ('Datu Odin Sinsuat', 'Datu Odin Sinsuat'), ('Kabuntalan', 'Kabuntalan'), ('Matanog', 'Matanog'),
        ('Northern Kabuntalan', 'Northern Kabuntalan'), ('Parang', 'Parang'), ('North Upi', 'North Upi'),
        ('Sultan Kudarat', 'Sultan Kudarat'), ('Sultan Mastura', 'Sultan Mastura'), ('Talitay', 'Talitay')
    ],
    'Cotabato City': [
        ('Cotabato City', 'Cotabato City')
    ],
    'Special Geographic Areas': [
        ('Pahamuddin', 'Pahamuddin'), ('Kadayangan', 'Kadayangan'), ('Nabalawag', 'Nabalawag'),
        ('Old Kaabakan', 'Old Kaabakan'), ('Kapalawan', 'Kapalawan'), ('Malidegao', 'Malidegao'),
        ('Tugunan', 'Tugunan'), ('Ligawasan', 'Ligawasan')
    ]
}


class FahanieCaresMemberRegistrationForm(forms.ModelForm):
    address_province = forms.ChoiceField(choices=PROVINCE_CHOICES, required=True)
    address_municipality = forms.ChoiceField(choices=[('', 'Select Municipality')], required=True)
    voter_address_province = forms.ChoiceField(choices=PROVINCE_CHOICES, required=True)
    voter_address_municipality = forms.ChoiceField(choices=[('', 'Select Municipality')], required=True)

    class Meta:
        model = FahanieCaresMember
        fields = [
            'last_name', 'first_name', 'middle_name', 'contact_number', 'email',
            'age', 'sex', 'address_barangay', 'address_municipality', 'address_province',
            'voter_address_barangay', 'voter_address_municipality', 'voter_address_province',
            'sector', 'highest_education', 'school_graduated', 'eligibility',
            'cancer_patient', 'dialysis_patient',
            'voter_id_photo', 'status' # Add status field
        ]
        widgets = {
            'sex': forms.Select(choices=FahanieCaresMember.SEX_CHOICES),
            'highest_education': forms.Select(choices=FahanieCaresMember.EDUCATION_CHOICES),
            'sector': forms.Select(choices=FahanieCaresMember.SECTOR_CHOICES),
            'eligibility': forms.Select(choices=FahanieCaresMember.ELIGIBILITY_CHOICES),
            'status': forms.Select(choices=FahanieCaresMember.STATUS_CHOICES), # Add widget for status
            # Explicitly define Select widgets for address fields
            'address_province': forms.Select(),
            'address_municipality': forms.Select(),
            'voter_address_province': forms.Select(),
            'voter_address_municipality': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial value for status field
        if not self.instance.pk: # Only for new forms, not when editing existing ones
            self.fields['status'].initial = 'pending'

        # Get the initial data for province, either from instance or submitted data
        initial_address_province = None
        initial_voter_address_province = None

        if self.instance.pk: # Editing an existing instance
            initial_address_province = self.instance.address_province
            initial_voter_address_province = self.instance.voter_address_province
        elif self.data: # Form is being submitted (has POST data)
            # The `self.prefix` attribute of a form in a formset will give the prefix.
            prefix = self.prefix if self.prefix else ''
            
            if f'{prefix}-address_province' in self.data:
                initial_address_province = self.data.get(f'{prefix}-address_province')
            if f'{prefix}-voter_address_province' in self.data:
                initial_voter_address_province = self.data.get(f'{prefix}-voter_address_province')

        # Set choices for municipality fields based on the determined province
        if initial_address_province:
            self.fields['address_municipality'].choices = [('', 'Select Municipality')] + MUNICIPALITY_CHOICES_MAP.get(initial_address_province, [])
        else:
            self.fields['address_municipality'].choices = [('', 'Select Municipality')] # Keep empty if no province selected/submitted

        if initial_voter_address_province:
            self.fields['voter_address_municipality'].choices = [('', 'Select Municipality')] + MUNICIPALITY_CHOICES_MAP.get(initial_voter_address_province, [])
        else:
            self.fields['voter_address_municipality'].choices = [('', 'Select Municipality')] # Keep empty if no province selected/submitted

        for field_name, field in self.fields.items():
            # Apply default class for most inputs
            field.widget.attrs['class'] = 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-500 focus:ring-opacity-50'
            
            # Override for specific widget types
            if field.widget.input_type == 'checkbox':
                field.widget.attrs['class'] = 'form-checkbox h-5 w-5 text-green-600'
            elif field.widget.input_type == 'radio':
                field.widget.attrs['class'] = 'form-radio h-4 w-4 text-green-600'
            elif isinstance(field.widget, forms.Select):
                # Use the classes from database_registrants.html for select fields
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        middle_name = cleaned_data.get('middle_name', '')

        if first_name and last_name:
            if FahanieCaresMember.objects.filter(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name
            ).exists():
                self.add_error(None, "A member with this full name already exists.")
        return cleaned_data

FahanieCaresMemberFormSet = formset_factory(
    FahanieCaresMemberRegistrationForm,
    extra=1,
    can_delete=True
)


class ExcelUploadForm(forms.Form):
    """
    Form for uploading Excel file containing names to check against database.
    """
    excel_file = forms.FileField(
        label="Upload Excel File",
        help_text="Upload an Excel file (.xlsx or .xls) containing a column with names to check against the database.",
        widget=forms.FileInput(attrs={
            'accept': '.xlsx,.xls',
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')

        if not excel_file:
            raise ValidationError("Please select an Excel file to upload.")

        # Check file extension
        if not excel_file.name.lower().endswith(('.xlsx', '.xls')):
            raise ValidationError("Please upload a valid Excel file (.xlsx or .xls).")

        # Check file size (limit to 10MB)
        if excel_file.size > 10 * 1024 * 1024:
            raise ValidationError("File size must be less than 10MB.")

        # Try to read the Excel file to validate it
        try:
            from io import BytesIO

            # Import pandas locally to avoid module-level import issues
            import pandas as pd

            # Read the file into a pandas DataFrame
            file_content = BytesIO(excel_file.read())
            df = pd.read_excel(file_content, engine='openpyxl' if excel_file.name.lower().endswith('.xlsx') else 'xlrd')

            # Check if DataFrame is empty
            if df.empty:
                raise ValidationError("The Excel file appears to be empty.")

            # Check if there's at least one column
            if len(df.columns) == 0:
                raise ValidationError("The Excel file must contain at least one column with names.")

            # Store the DataFrame for later use
            self.cleaned_data['dataframe'] = df

        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {str(e)}. Please ensure the file is a valid Excel format.")

        return excel_file
