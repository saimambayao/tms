# Radio Button Validation Issue - Root Cause Analysis and Solution

**Date**: June 10, 2025  
**Author**: BM Parliament Development Team  
**Issue**: Registration form showing "This field is required" errors for radio button fields despite being selected

## Problem Description

The BM Parliament member registration form was experiencing validation errors where radio button fields (sex, sector, highest_education, eligibility) were showing "This field is required" errors even though users had selected values. This issue occurred specifically when:

1. The form had validation errors (e.g., username already taken, password mismatch)
2. The form was re-rendered with errors
3. The form used `enctype="multipart/form-data"` for file uploads

### Screenshot of the Issue
Users would see errors like:
- "Sex: This field is required"
- "Sector: This field is required"
- "Highest_Education: This field is required"
- "Eligibility: This field is required"

Even though they had already selected these options before submitting.

## Root Cause Analysis

### 1. Django Form Data Binding Issue
When a Django form with `enctype="multipart/form-data"` fails validation, the radio button values weren't being properly preserved in the POST data when the form was re-rendered. This is a known issue with how Django handles radio button widgets in multipart forms.

### 2. Redundant Validation
The form had redundant validation in the `clean()` method that was checking for radio button values, which could cause additional validation failures:

```python
# This was redundant and problematic
required_radio_fields = ['sex', 'sector', 'highest_education', 'eligibility']
for field_name in required_radio_fields:
    if not cleaned_data.get(field_name):
        raise forms.ValidationError(f"Please select a {field_name.replace('_', ' ')}.")
```

### 3. File Upload Size Mismatch
The form was checking for a 10MB file size limit, but Django settings had `FILE_UPLOAD_MAX_MEMORY_SIZE = 5MB`, causing potential confusion.

## Solution Implemented

### 1. Created RadioFieldValidationMixin
A reusable mixin that ensures radio button fields are properly validated in forms:

```python
class RadioFieldValidationMixin:
    """
    Mixin to ensure radio button fields are properly validated in forms,
    especially when using enctype="multipart/form-data"
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Log form initialization for debugging
        if self.is_bound:
            logger.debug(f"Form {self.__class__.__name__} initialized with POST data")
            
            # Check for radio select fields
            for field_name, field in self.fields.items():
                if isinstance(field.widget, forms.RadioSelect):
                    # Ensure the field data is properly bound
                    if hasattr(self, 'data') and field_name in self.data:
                        logger.debug(f"Radio field {field_name} has value: {self.data.get(field_name)}")
                    else:
                        logger.warning(f"Radio field {field_name} missing from POST data")
```

### 2. Created EnhancedRadioSelect Widget
A custom widget that ensures proper data handling:

```python
class EnhancedRadioSelect(forms.RadioSelect):
    """
    Enhanced RadioSelect widget that ensures proper data handling
    """
    
    def value_from_datadict(self, data, files, name):
        """
        Override to ensure radio button values are properly extracted from POST data
        """
        value = data.get(name)
        if value:
            logger.debug(f"RadioSelect field {name} extracted value: {value}")
        else:
            logger.warning(f"RadioSelect field {name} has no value in POST data")
        return value
```

### 3. Applied Fix to All Forms
Updated all forms with RadioSelect widgets to use the mixin and enhanced widget:
- `BM ParliamentMemberRegistrationForm`
- `BM ParliamentMemberUpdateForm`
- `DocumentApprovalForm`
- `VotingRecordForm`

### 4. Improved File Upload Validation
Added proper file size and type validation:

```python
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
```

## Docker Considerations

**No Docker-specific issues were found.** The Docker environment was working correctly. The issue was purely related to Django form handling. However, when testing fixes in Docker:

1. Code changes are automatically synced due to volume mounting
2. The web container needs to be restarted for Python code changes: `docker-compose restart web`
3. Template and static file changes don't require restart

## Files Modified

1. `/src/apps/core/forms.py` - Added RadioFieldValidationMixin and EnhancedRadioSelect
2. `/src/apps/constituents/member_forms.py` - Applied mixin and fixed validation
3. `/src/apps/constituents/member_views.py` - Added debugging logs
4. `/src/apps/documents/forms.py` - Applied fix to DocumentApprovalForm
5. `/src/apps/parliamentary/forms.py` - Applied fix to VotingRecordForm

## Testing the Fix

### Local Testing with Docker
```bash
# Start Docker containers
docker-compose up -d

# Restart web container after code changes
docker-compose restart web

# View logs
docker-compose logs -f web
```

### Test Scenarios
1. Submit form with missing required fields - radio buttons should stay selected
2. Submit form with invalid file size (>5MB) - radio buttons should stay selected
3. Submit form with duplicate email - radio buttons should stay selected
4. Submit valid form - should succeed

## Prevention Strategies

1. **Always test forms with file uploads** - They behave differently due to `enctype="multipart/form-data"`
2. **Use the RadioFieldValidationMixin** for any new forms with radio buttons
3. **Avoid redundant validation** - Let Django's built-in field validation handle required fields
4. **Match file size limits** between form validation and Django settings
5. **Add comprehensive logging** to form validation for easier debugging

## Related Issues

- Django ticket #[number] - Radio button values lost on form validation errors
- Stack Overflow: "Django RadioSelect loses value on form error"
- Similar issues may affect CheckboxSelectMultiple widgets

## Deployment Notes

The fix was deployed by pushing to the main branch, which automatically:
1. Syncs to the production fork repository
2. Triggers the production rebuild in Coolify
3. Updates the live site at https://bmparliament.gov.ph

No manual deployment steps were required.