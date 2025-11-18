from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import json


class GeneralDatabase(models.Model):
    """
    Main database container for organizing different types of data collections.
    Supports hierarchical structure with parent-child relationships for sub-databases.
    """

    DATABASE_TYPES = (
        ('attendance', 'Attendance Database'),
        ('events', 'Events Database'),
        ('training', 'Training Programs Database'),
        ('volunteers', 'Volunteer Activities Database'),
        ('beneficiaries', 'Beneficiaries Database'),
        ('custom', 'Custom Database'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    database_type = models.CharField(max_length=20, choices=DATABASE_TYPES, default='custom')
    parent_database = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_databases',
        help_text="Parent database for hierarchical structure"
    )

    # Configuration
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False, help_text="Allow public access to this database")
    allow_self_registration = models.BooleanField(default=False, help_text="Allow users to add themselves")

    # Access control
    allowed_roles = models.JSONField(
        default=list,
        help_text="List of user roles that can access this database. Empty list means all roles."
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='accessible_databases',
        help_text="Specific users with access to this database"
    )

    # Metadata
    slug = models.SlugField(unique=True, max_length=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_databases'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'General Database'
        verbose_name_plural = 'General Databases'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
            original_slug = self.slug
            queryset = GeneralDatabase.objects.all()
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            num = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent_database:
            return f"{self.parent_database.name} → {self.name}"
        return self.name

    def get_absolute_url(self):
        return f"/databases/{self.slug}/"

    def has_access(self, user):
        """Check if a user has access to this database"""
        if not self.is_active:
            return False

        # Superusers have access to everything
        if user.is_superuser:
            return True

        # Check specific user access
        if self.allowed_users.filter(pk=user.pk).exists():
            return True

        # Check role-based access
        if not self.allowed_roles:  # Empty list means all roles
            return True

        return user.user_type in self.allowed_roles

    def get_all_entries(self):
        """Get all entries in this database and sub-databases"""
        entries = self.entries.all()
        for sub_db in self.sub_databases.filter(is_active=True):
            entries = entries | sub_db.get_all_entries()
        return entries.distinct()

    @property
    def column_names(self):
        """Get all unique column names from entries in this database"""
        entries = self.entries.all()
        column_names = set()

        for entry in entries:
            column_names.update(entry.entry_data.keys())

        # Return sorted list for consistent display
        return sorted(list(column_names))

    @property
    def active_column_names(self):
        """Get column names that have actual data (non-empty values)"""
        entries = self.entries.all()
        column_names = set()

        for entry in entries:
            for key, value in entry.entry_data.items():
                # Only include columns that have non-empty values
                if value is not None and str(value).strip():
                    column_names.add(key)

        # Return sorted list for consistent display
        return sorted(list(column_names))

    def get_flexible_column_names(self):
        """Get column names with flexible matching for different formats"""
        entries = self.entries.all()
        all_columns = set()

        for entry in entries:
            all_columns.update(entry.entry_data.keys())

        # Group similar column names together
        normalized_groups = {}
        for col in all_columns:
            normalized = self._normalize_column_name(col)
            if normalized not in normalized_groups:
                normalized_groups[normalized] = []
            normalized_groups[normalized].append(col)

        # Return the most common variant for each normalized name
        result = []
        for normalized, variants in normalized_groups.items():
            # Choose the most readable variant (prefer title case, then original)
            best_variant = max(variants, key=lambda x: (
                1 if x.istitle() else 0,  # Prefer title case
                len(x),  # Prefer longer names
                x  # Then alphabetical
            ))
            result.append(best_variant)

        return sorted(result)

    def _normalize_column_name(self, name):
        """Normalize column names for comparison"""
        import re
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

    def find_column_matches(self, target_column):
        """Find all columns that might match a target column name"""
        entries = self.entries.all()
        all_columns = set()

        for entry in entries:
            all_columns.update(entry.entry_data.keys())

        target_normalized = self._normalize_column_name(target_column)
        matches = []

        for col in all_columns:
            col_normalized = self._normalize_column_name(col)

            # Exact match
            if col == target_column:
                return [col]

            # Normalized match
            if col_normalized == target_normalized:
                matches.append(col)

            # Partial match (for common variations)
            if (target_normalized in col_normalized or
                col_normalized in target_normalized):
                matches.append(col)

        return matches if matches else [target_column]


class DatabaseField(models.Model):
    """
    Custom field definitions for databases.
    Supports various field types with validation rules.
    """

    FIELD_TYPES = (
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('select', 'Select Dropdown'),
        ('multiselect', 'Multiple Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Buttons'),
        ('file', 'File Upload'),
        ('image', 'Image Upload'),
        ('url', 'URL'),
        ('hidden', 'Hidden Field'),
    )

    VALIDATION_TYPES = (
        ('none', 'No Validation'),
        ('required', 'Required Field'),
        ('email', 'Valid Email'),
        ('phone', 'Valid Phone Number'),
        ('numeric', 'Numeric Only'),
        ('min_length', 'Minimum Length'),
        ('max_length', 'Maximum Length'),
        ('min_value', 'Minimum Value'),
        ('max_value', 'Maximum Value'),
        ('regex', 'Regular Expression'),
    )

    database = models.ForeignKey(
        GeneralDatabase,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=255, help_text="Display label for the field")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=True, help_text="Include in search results")
    is_filterable = models.BooleanField(default=False, help_text="Show as filter option")

    # Field configuration
    default_value = models.CharField(max_length=500, blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    help_text = models.TextField(blank=True)

    # Select field options (for select, multiselect, radio)
    options = models.JSONField(
        default=list,
        help_text="List of options for select fields. Format: [{'value': 'opt1', 'label': 'Option 1'}]"
    )

    # Validation rules
    validation_type = models.CharField(max_length=20, choices=VALIDATION_TYPES, default='none')
    validation_rules = models.JSONField(
        default=dict,
        help_text="Validation parameters (min_length, max_length, regex pattern, etc.)"
    )

    # Display order
    order = models.PositiveIntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['database', 'name']
        verbose_name = 'Database Field'
        verbose_name_plural = 'Database Fields'

    def __str__(self):
        return f"{self.database.name}: {self.label}"

    def validate_value(self, value):
        """Validate a field value based on field configuration"""
        if self.is_required and not value:
            raise ValidationError(f"{self.label} is required.")

        if not value:  # Allow empty values for non-required fields
            return True

        # Type-specific validation
        if self.field_type == 'email' and value:
            import re
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value)):
                raise ValidationError(f"{self.label} must be a valid email address.")

        elif self.field_type == 'number' and value:
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"{self.label} must be a valid number.")

        elif self.field_type == 'phone' and value:
            import re
            # Basic phone validation - adjust regex as needed
            if not re.match(r'^[\+]?[0-9\s\-\(\)]+$', str(value)):
                raise ValidationError(f"{self.label} must be a valid phone number.")

        elif self.field_type == 'url' and value:
            import re
            if not re.match(r'^https?://', str(value)):
                raise ValidationError(f"{self.label} must be a valid URL starting with http:// or https://")

        # Custom validation rules
        if self.validation_type == 'min_length' and 'min_length' in self.validation_rules:
            if len(str(value)) < self.validation_rules['min_length']:
                raise ValidationError(f"{self.label} must be at least {self.validation_rules['min_length']} characters long.")

        elif self.validation_type == 'max_length' and 'max_length' in self.validation_rules:
            if len(str(value)) > self.validation_rules['max_length']:
                raise ValidationError(f"{self.label} cannot be longer than {self.validation_rules['max_length']} characters.")

        elif self.validation_type == 'min_value' and 'min_value' in self.validation_rules:
            try:
                if float(value) < float(self.validation_rules['min_value']):
                    raise ValidationError(f"{self.label} must be at least {self.validation_rules['min_value']}.")
            except (ValueError, TypeError):
                raise ValidationError(f"{self.label} must be a valid number.")

        elif self.validation_type == 'max_value' and 'max_value' in self.validation_rules:
            try:
                if float(value) > float(self.validation_rules['max_value']):
                    raise ValidationError(f"{self.label} cannot be greater than {self.validation_rules['max_value']}.")
            except (ValueError, TypeError):
                raise ValidationError(f"{self.label} must be a valid number.")

        elif self.validation_type == 'regex' and 'pattern' in self.validation_rules:
            import re
            if not re.match(self.validation_rules['pattern'], str(value)):
                raise ValidationError(f"{self.label} format is invalid.")

        return True


class DatabaseEntry(models.Model):
    """
    Individual records within a database.
    Stores flexible data based on the database's field configuration.
    """

    database = models.ForeignKey(
        GeneralDatabase,
        on_delete=models.CASCADE,
        related_name='entries'
    )

    # Person identification (can link to existing users or store as guest)
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='database_entries',
        help_text="Link to existing user account"
    )

    # Guest information (for non-registered users)
    guest_first_name = models.CharField(max_length=100, blank=True)
    guest_last_name = models.CharField(max_length=100, blank=True)
    guest_middle_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)

    # Entry data (flexible JSON storage)
    entry_data = models.JSONField(
        default=dict,
        help_text="Flexible storage for all field values"
    )

    # Status and workflow
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_entries'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Search optimization
    search_text = models.TextField(blank=True, help_text="Concatenated searchable text")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Database Entry'
        verbose_name_plural = 'Database Entries'
        indexes = [
            models.Index(fields=['database', 'status']),
            models.Index(fields=['linked_user']),
            models.Index(fields=['guest_email']),
            models.Index(fields=['guest_first_name', 'guest_last_name']),
        ]

    def __str__(self):
        if self.linked_user:
            return f"{self.database.name}: {self.linked_user.get_full_name()}"
        else:
            name = f"{self.guest_first_name} {self.guest_last_name}".strip()
            return f"{self.database.name}: {name or 'Guest User'}"

    def get_full_name(self):
        """Get the full name of the person (user or guest)"""
        if self.linked_user:
            full_name = self.linked_user.get_full_name()
            return full_name if full_name.strip() else "User"
        else:
            parts = [self.guest_first_name, self.guest_middle_name, self.guest_last_name]
            full_name = ' '.join([p for p in parts if p]).strip()

            # If no name parts, try to get name from entry_data
            if not full_name:
                for key, value in self.entry_data.items():
                    key_lower = key.lower()
                    if any(keyword in key_lower for keyword in ['first', 'fname', 'first_name']) and value:
                        first_name = str(value).strip()
                    elif any(keyword in key_lower for keyword in ['last', 'lname', 'last_name', 'surname']) and value:
                        last_name = str(value).strip()
                    elif any(keyword in key_lower for keyword in ['name', 'full_name']) and value:
                        return str(value).strip()

                # If we found names in entry_data, use them
                if 'first_name' in locals() and 'last_name' in locals():
                    full_name = f"{first_name} {last_name}".strip()
                elif 'first_name' in locals():
                    full_name = first_name
                elif 'last_name' in locals():
                    full_name = last_name

            return full_name if full_name else "Guest User"

    def get_contact_info(self):
        """Get contact information"""
        if self.linked_user:
            return {
                'email': self.linked_user.email,
                'phone': getattr(self.linked_user, 'phone_number', ''),
            }
        else:
            return {
                'email': self.guest_email,
                'phone': self.guest_phone,
            }

    def save(self, *args, **kwargs):
        # Update search text for optimization
        search_parts = []

        # Add user/guest name to search
        if self.linked_user:
            search_parts.append(self.linked_user.get_full_name())
            search_parts.append(self.linked_user.email)
            if hasattr(self.linked_user, 'phone_number'):
                search_parts.append(self.linked_user.phone_number)
        else:
            search_parts.extend([
                self.guest_first_name,
                self.guest_last_name,
                self.guest_middle_name,
                self.guest_email,
                self.guest_phone,
            ])

        # Add entry data values to search (including names from imported data)
        for key, value in self.entry_data.items():
            if value:
                search_parts.append(str(key).lower())  # Include field names
                search_parts.append(str(value))        # Include field values

        self.search_text = ' '.join(search_parts).lower()

        super().save(*args, **kwargs)

    def get_field_value(self, field_name):
        """Get a specific field value"""
        return self.entry_data.get(field_name)

    def set_field_value(self, field_name, value):
        """Set a specific field value"""
        self.entry_data[field_name] = value
        self.save(update_fields=['entry_data', 'updated_at'])


class PersonLink(models.Model):
    """
    Links database entries that belong to the same person across different databases.
    Enables unified person view and prevents duplicate entries.
    """

    LINK_TYPES = (
        ('fahanie_cares_member', 'FahanieCares Member'),
        ('constituent', 'Constituent Profile'),
        ('database_entry', 'Database Entry'),
        ('external', 'External System'),
    )

    # Core person identification
    primary_name = models.CharField(max_length=255, help_text="Primary name for this person")
    normalized_name = models.CharField(max_length=255, help_text="Normalized name for matching")

    # Linked records
    fahanie_cares_member = models.ForeignKey(
        'constituents.FahanieCaresMember',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='person_links'
    )
    constituent = models.ForeignKey(
        'constituents.Constituent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='person_links'
    )
    database_entries = models.ManyToManyField(
        DatabaseEntry,
        blank=True,
        related_name='person_links'
    )

    # External system links
    external_id = models.CharField(max_length=100, blank=True, help_text="ID in external system")
    external_system = models.CharField(max_length=100, blank=True, help_text="Name of external system")

    # Matching confidence and metadata
    confidence_score = models.FloatField(default=1.0, help_text="Confidence in person matching (0-1)")
    is_verified = models.BooleanField(default=False, help_text="Manually verified match")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_person_links'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-confidence_score', '-created_at']
        verbose_name = 'Person Link'
        verbose_name_plural = 'Person Links'
        indexes = [
            models.Index(fields=['normalized_name']),
            models.Index(fields=['primary_name']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"Person Link: {self.primary_name}"

    def get_all_entries(self):
        """Get all database entries linked to this person"""
        entries = set()

        if self.fahanie_cares_member:
            entries.add(('fahanie_cares_member', self.fahanie_cares_member))

        if self.constituent:
            entries.add(('constituent', self.constituent))

        for entry in self.database_entries.all():
            entries.add(('database_entry', entry))

        return entries

    def add_database_entry(self, entry):
        """Add a database entry to this person link"""
        self.database_entries.add(entry)
        self.save()

    def calculate_confidence_score(self):
        """Calculate confidence score based on name matching and other factors"""
        # This would implement fuzzy matching logic
        # For now, return a default high confidence
        return 0.9


# Import here to avoid circular imports
from django.apps import apps
try:
    from apps.constituents.models import FahanieCaresMember
    from apps.constituents.models import Constituent
except ImportError:
    # Models might not be available during migration
    pass
