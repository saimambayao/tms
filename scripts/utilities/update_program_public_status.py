import os
import django
import sys
from django.conf import settings
from django.apps import apps

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Configure Django settings if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from apps.services.models import MinistryProgram

programs_to_update = ["dasdwq", "sample edit v2"]

print("Updating 'is_public' status for #FahanieCares programs:")
for title in programs_to_update:
    try:
        program = MinistryProgram.objects.get(title=title, program_source='fahaniecares')
        if not program.is_public:
            program.is_public = True
            program.save(update_fields=['is_public'])
            print(f"Successfully updated '{program.title}' (ID: {program.id}) to is_public=True.")
        else:
            print(f"Program '{program.title}' (ID: {program.id}) is already public.")
    except MinistryProgram.DoesNotExist:
        print(f"Program: '{title}' not found with program_source 'fahaniecares'.")
    except Exception as e:
        print(f"Error updating program '{title}': {e}")
