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

program_titles = ["dasdwq", "sasa", "sample edit v2"]

print("Checking status for #FahanieCares programs:")
for title in program_titles:
    try:
        program = MinistryProgram.objects.get(title=title, program_source='fahaniecares')
        print(f"Program: '{program.title}' (ID: {program.id})")
        print(f"  is_public: {program.is_public}")
        print(f"  is_deleted: {program.is_deleted}")
        print(f"  status: {program.status}")
    except MinistryProgram.DoesNotExist:
        print(f"Program: '{title}' not found with program_source 'fahaniecares'.")
    except Exception as e:
        print(f"Error checking program '{title}': {e}")
