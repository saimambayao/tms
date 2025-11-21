from django import forms
from apps.staff.models import Staff
import logging

logger = logging.getLogger(__name__)


class StaffForm(forms.ModelForm):
    """Form for creating and editing staff members in the database."""
    
    class Meta:
        model = Staff
        fields = [
            'full_name', 'position', 'email', 'phone_number', 'address',
            'division', 'office', 'employment_status', 'date_hired',
            'duties_responsibilities', 'staff_workflow', 'bio', 'is_active'
        ]
        # Note: notion_id is excluded as it's for Notion integration only
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Enter full name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Enter position/designation'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3,
                'placeholder': 'Enter address'
            }),
            'division': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'office': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'date_hired': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'type': 'date'
            }),
            'duties_responsibilities': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 4,
                'placeholder': 'Enter duties and responsibilities'
            }),
            'staff_workflow': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 4,
                'placeholder': 'Enter daily workflow and tasks'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3,
                'placeholder': 'Enter bio/additional information'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:ring-primary-500'
            })
        }
        labels = {
            'full_name': 'Full Name *',
            'position': 'Position/Designation',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'division': 'Division',
            'office': 'Office',
            'employment_status': 'Employment Status',
            'date_hired': 'Date Hired',
            'duties_responsibilities': 'Duties & Responsibilities',
            'staff_workflow': 'Staff Workflow',
            'bio': 'Bio/Additional Information',
            'is_active': 'Active Status'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choice for select fields
        self.fields['division'].choices = [('', 'Select Division')] + list(Staff.DIVISION_CHOICES)
        self.fields['office'].choices = [('', 'Select Office')] + list(Staff.OFFICE_CHOICES)
        self.fields['employment_status'].choices = [('', 'Select Employment Status')] + list(Staff.EMPLOYMENT_STATUS_CHOICES)
