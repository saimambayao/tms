from django import forms
from .models import Chapter, ChapterMembership, ChapterActivity

class ChapterForm(forms.ModelForm):
    """Form for creating and updating chapters."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only include provincial and municipal chapters in parent chapter choices
        self.fields['parent_chapter'].queryset = Chapter.objects.filter(tier__in=['provincial', 'municipal'])
    
    class Meta:
        model = Chapter
        fields = [
            'name', 'tier', 'municipality', 'province', 'country',
            'description', 'mission_statement', 'established_date',
            'coordinator', 'email', 'phone', 'address',
            'meeting_location', 'meeting_schedule',
            'facebook_page', 'twitter_handle', 'instagram_handle',
            'parent_chapter'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., #FahanieCares Cotabato Chapter',
                'required': True
            }),
            'tier': forms.Select(attrs={'required': True}),
            'municipality': forms.TextInput(attrs={
                'placeholder': 'Municipality or City name',
                'required': True
            }),
            'province': forms.TextInput(attrs={
                'placeholder': 'Province name',
                'required': True
            }),
            'country': forms.TextInput(attrs={
                'value': 'Philippines',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Brief description of the chapter\'s focus and community',
                'required': True
            }),
            'mission_statement': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'The chapter\'s specific mission and goals'
            }),
            'established_date': forms.DateInput(attrs={'type': 'date'}),
            'coordinator': forms.Select(),
            'email': forms.EmailInput(attrs={
                'placeholder': 'chapter@fahaniecares.ph'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+63 XXX XXX XXXX'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Complete address including street, barangay, and landmarks'
            }),
            'meeting_location': forms.TextInput(attrs={
                'placeholder': 'e.g., City Hall Conference Room'
            }),
            'meeting_schedule': forms.TextInput(attrs={
                'placeholder': 'e.g., Every first Saturday of the month at 2:00 PM'
            }),
            'facebook_page': forms.URLInput(attrs={
                'placeholder': 'https://facebook.com/your-page'
            }),
            'twitter_handle': forms.TextInput(attrs={
                'placeholder': 'username (without @)'
            }),
            'instagram_handle': forms.TextInput(attrs={
                'placeholder': 'username (without @)'
            }),
            'parent_chapter': forms.Select(),
        }

class MembershipForm(forms.ModelForm):
    """Form for managing memberships."""
    
    class Meta:
        model = ChapterMembership
        fields = [
            'user', 'role', 'status', 'is_volunteer',
            'volunteer_skills', 'availability', 'committees',
            'notes'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'volunteer_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'availability': forms.TextInput(attrs={'class': 'form-control'}),
            'committees': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MembershipApplicationForm(forms.ModelForm):
    """Form for membership applications."""
    
    class Meta:
        model = ChapterMembership
        fields = [
            'is_volunteer', 'volunteer_skills', 'availability',
            'committees', 'notes'
        ]
        widgets = {
            'volunteer_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please describe any skills you can offer as a volunteer'
            }),
            'availability': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Weekends, Evenings, Flexible'
            }),
            'committees': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Events, Outreach, Fundraising'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional information you\'d like to share'
            }),
        }

class ActivityForm(forms.ModelForm):
    """Form for creating and updating activities."""
    
    class Meta:
        model = ChapterActivity
        fields = [
            'title', 'activity_type', 'description', 'objectives',
            'date', 'start_time', 'end_time', 'venue', 'address',
            'online_link', 'target_participants', 'budget',
            'resources_needed'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'online_link': forms.URLInput(attrs={'class': 'form-control'}),
            'target_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'resources_needed': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }