#!/usr/bin/env python
"""
Test script to verify pandas import works in Django context
"""
import os
import sys
import django

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Setup Django
django.setup()

print("Testing pandas import in Django context...")
try:
    import pandas as pd
    print(f"✅ pandas imported successfully: version {pd.__version__}")

    # Test basic functionality
    df = pd.DataFrame({'test': [1, 2, 3]})
    print(f"✅ pandas DataFrame created: {len(df)} rows")

    # Test openpyxl import
    import openpyxl
    print(f"✅ openpyxl imported successfully: version {openpyxl.__version__}")

    print("\n🎉 All Excel processing libraries are working correctly!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure pandas and openpyxl are installed in the virtual environment")
    sys.exit(1)

print("\nTesting Django form import...")
try:
    from apps.constituents.forms import ExcelUploadForm
    print("✅ ExcelUploadForm imported successfully")

    # Test form instantiation
    form = ExcelUploadForm()
    print("✅ ExcelUploadForm instantiated successfully")

except ImportError as e:
    print(f"❌ Django form import error: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! The Excel name check feature should work correctly.")
