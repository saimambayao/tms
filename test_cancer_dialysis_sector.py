#!/usr/bin/env python
"""
Simple test script to verify the Cancer/Dialysis Patients sector choices
"""
import os
import sys
import django

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from apps.constituents.member_models import FahanieCaresMember

def test_cancer_dialysis_sector():
    """Test if the Cancer/Dialysis Patients sector is properly configured"""
    print("Testing Cancer/Dialysis Patients sector implementation...")

    # Test 1: Check if cancer_dialysis sector is in SECTOR_CHOICES
    sector_choices = dict(FahanieCaresMember.SECTOR_CHOICES)
    if 'cancer_dialysis' in sector_choices:
        print("✓ Cancer/Dialysis Patients sector found in SECTOR_CHOICES")
        print(f"  Display name: {sector_choices['cancer_dialysis']}")
    else:
        print("✗ Cancer/Dialysis Patients sector NOT found in SECTOR_CHOICES")
        return False

    # Test 2: Check if model has the required fields
    required_fields = ['cancer_patient', 'dialysis_patient']
    model_fields = [field.name for field in FahanieCaresMember._meta.get_fields()]

    for field in required_fields:
        if field in model_fields:
            print(f"✓ Model field '{field}' found")
        else:
            print(f"✗ Model field '{field}' NOT found")
            return False

    print("\n✓ All tests passed! Cancer/Dialysis Patients sector is properly implemented.")
    return True

if __name__ == '__main__':
    test_cancer_dialysis_sector()
