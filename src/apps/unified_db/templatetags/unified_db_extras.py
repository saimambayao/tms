from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_item_flexible(dictionary, key):
    """
    Get an item from a dictionary using a flexible key matching.
    This handles different column name variations and formats.
    Usage: {{ dictionary|get_item_flexible:key }}
    """
    if dictionary is None or not key:
        return None

    # Ensure dictionary is actually a dictionary
    if not hasattr(dictionary, 'keys') or not hasattr(dictionary, 'get'):
        return None

    # First try exact match
    if key in dictionary:
        return dictionary[key]

    # Try case-insensitive match
    key_lower = key.lower()
    for dict_key in dictionary.keys():
        if dict_key.lower() == key_lower:
            return dictionary[dict_key]

    # Try normalized key matching (remove spaces, underscores, etc.)
    normalized_key = normalize_column_name(key)
    for dict_key in dictionary.keys():
        if normalize_column_name(dict_key) == normalized_key:
            return dictionary[dict_key]

    # Try partial matching for common variations
    variations = generate_key_variations(key)
    for variation in variations:
        if variation in dictionary:
            return dictionary[variation]

    return None

@register.filter
def normalize_column_name(name):
    """
    Normalize column names by removing spaces, special characters, and standardizing format.
    Usage: {{ column_name|normalize_column_name }}
    """
    if not name:
        return ""

    # Convert to lowercase and remove extra spaces
    normalized = str(name).lower().strip()

    # Replace common separators with underscores
    normalized = re.sub(r'[\s\-/\.]+', '_', normalized)

    # Remove special characters except underscores
    normalized = re.sub(r'[^\w_]', '', normalized)

    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)

    # Remove leading/trailing underscores
    normalized = normalized.strip('_')

    return normalized

@register.filter
def generate_key_variations(key):
    """
    Generate common variations of a column name for flexible matching.
    Usage: {{ key|generate_key_variations }}
    """
    if not key:
        return []

    variations = set()
    key_lower = key.lower()
    key_title = key.title()

    # Add original variations
    variations.add(key)
    variations.add(key_lower)
    variations.add(key.upper())
    variations.add(key_title)

    # Add normalized version
    normalized = normalize_column_name(key)
    if normalized != key_lower:
        variations.add(normalized)

    # Common name variations
    name_variations = {
        'name': ['full_name', 'complete_name', 'display_name', 'person_name'],
        'first_name': ['fname', 'first', 'given_name'],
        'last_name': ['lname', 'surname', 'family_name'],
        'email': ['email_address', 'e_mail', 'mail'],
        'phone': ['phone_number', 'mobile', 'contact', 'telephone'],
        'address': ['home_address', 'residence', 'location'],
        'age': ['years_old', 'birth_year'],
        'gender': ['sex', 'male_female'],
        'status': ['state', 'condition', 'situation'],
        'date': ['created_date', 'timestamp', 'time'],
        'id': ['identifier', 'number', 'code'],
        'type': ['category', 'class', 'kind'],
        'amount': ['value', 'total', 'sum'],
        'description': ['desc', 'details', 'info', 'notes'],
        'organization': ['org', 'company', 'institution'],
        'position': ['role', 'title', 'job_title'],
        'department': ['dept', 'division', 'unit'],
        'salary': ['pay', 'wage', 'income', 'compensation'],
        'start_date': ['begin_date', 'from_date', 'commencement'],
        'end_date': ['finish_date', 'to_date', 'completion'],
    }

    # Add variations for common field names
    for base_name, variants in name_variations.items():
        if base_name in key_lower or any(variant in key_lower for variant in variants):
            variations.update(variants)
            variations.add(base_name)

    return list(variations)

@register.filter
def get_display_value(value, field_type=None):
    """
    Get a properly formatted display value for different field types.
    Usage: {{ value|get_display_value:field_type }}
    """
    if value is None:
        return "-"

    if field_type == 'date' and value:
        try:
            from datetime import datetime
            if isinstance(value, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                    try:
                        date_obj = datetime.strptime(value, fmt)
                        return date_obj.strftime('%B %d, %Y')
                    except ValueError:
                        continue
            return str(value)
        except:
            return str(value)

    if field_type == 'number' and value:
        try:
            return "{:,.2f}".format(float(value))
        except:
            return str(value)

    if field_type == 'boolean' and value:
        return "Yes" if value else "No"

    # Truncate long text values
    str_value = str(value)
    if len(str_value) > 50:
        return str_value[:47] + "..."

    return str_value

@register.filter
def get_column_display_name(column_name):
    """
    Get a human-readable display name for a column.
    Usage: {{ column_name|get_column_display_name }}
    """
    if not column_name:
        return ""

    # Handle common abbreviations and normalize
    display_names = {
        'fname': 'First Name',
        'lname': 'Last Name',
        'mname': 'Middle Name',
        'fullname': 'Full Name',
        'email': 'Email Address',
        'phone': 'Phone Number',
        'mobile': 'Mobile Number',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'zip': 'ZIP Code',
        'age': 'Age',
        'gender': 'Gender',
        'dob': 'Date of Birth',
        'status': 'Status',
        'type': 'Type',
        'category': 'Category',
        'amount': 'Amount',
        'salary': 'Salary',
        'position': 'Position',
        'department': 'Department',
        'org': 'Organization',
        'company': 'Company',
        'notes': 'Notes',
        'description': 'Description',
        'date': 'Date',
        'time': 'Time',
        'id': 'ID',
        'code': 'Code',
        'ref': 'Reference',
        'num': 'Number',
    }

    # Check if we have a direct mapping
    if column_name.lower() in display_names:
        return display_names[column_name.lower()]

    # Otherwise, format the column name nicely
    # Split on common separators
    parts = re.split(r'[\s_\-\.]+', column_name)

    # Title case each part and join with spaces
    formatted_parts = []
    for part in parts:
        if part:
            formatted_parts.append(part.title())

    return ' '.join(formatted_parts)
