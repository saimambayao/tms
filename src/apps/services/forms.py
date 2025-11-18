from django import forms
from apps.services.models import MinistryProgram

class MinistryProgramForm(forms.ModelForm):
    class Meta:
        model = MinistryProgram
        fields = [
            'title', 'ministry', 'program_source', 'ppa_type', 'status',
            'priority_level', 'total_budget', 'start_date', 'end_date',
            'geographic_coverage', 'target_beneficiaries', 'description',
            'objectives', 'expected_outcomes', 'key_performance_indicators',
            'implementation_strategy', 'implementing_units', 'funding_source',
            'is_featured' # Removed slug, is_public, and is_deleted from fields
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'objectives': forms.Textarea(attrs={'rows': 2}),
            'expected_outcomes': forms.Textarea(attrs={'rows': 2}),
            'key_performance_indicators': forms.Textarea(attrs={'rows': 2}),
            'implementation_strategy': forms.Textarea(attrs={'rows': 3}),
            'implementing_units': forms.Textarea(attrs={'rows': 2}),
            'duration_months': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap/Tailwind CSS classes to fields for consistent styling
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.DateInput, forms.Textarea, forms.Select)):
                field.widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'h-4 w-4 text-primary-600 border-gray-300 rounded'})

    def clean_total_budget(self):
        total_budget = self.cleaned_data.get('total_budget')
        if total_budget is not None and total_budget < 0:
            raise forms.ValidationError("Total budget cannot be negative.")
        return total_budget

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "End date cannot be before start date.")
        return cleaned_data

# Placeholder forms for apps.services.views.py imports
class ServiceApplicationForm(forms.Form):
    # Add placeholder fields as needed to satisfy imports
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

class ServiceAssessmentForm(forms.Form):
    assessment_notes = forms.CharField(widget=forms.Textarea)

class ServiceDisbursementForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class ApplicationForm(forms.Form):
    program_of_interest = forms.ChoiceField(
        choices=[], # Choices will be set in __init__
        label="Program of Interest",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent'})
    )
    message = forms.CharField(
        label="Reason for Application",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent'}),
        help_text="Please provide a brief explanation of why you are applying for this program."
    )
    requirements = forms.FileField(
        label="Supporting Documents (Optional)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent'}),
        help_text="Upload any relevant documents (e.g., ID, proof of income, certificates). Max 5 files."
    )

    def __init__(self, *args, **kwargs):
        programs = kwargs.pop('programs', None)
        super().__init__(*args, **kwargs)
        if programs:
            # Format programs for ChoiceField: [(value, label), ...]
            # value will be 'service_ID' or 'ministry_ID'
            self.fields['program_of_interest'].choices = [
                (p['id'], p['name'] if 'name' in p else p['title']) for p in programs
            ]
            # Add a default empty choice
            self.fields['program_of_interest'].choices.insert(0, ('', '--- Select a Program ---'))

class ProgramSearchForm(forms.Form):
    # Placeholder for program search fields
    search_query = forms.CharField(max_length=255, required=False)
    ministry = forms.CharField(max_length=50, required=False)

class ImportProgramsForm(forms.Form):
    # Placeholder for program import fields
    csv_file = forms.FileField()
