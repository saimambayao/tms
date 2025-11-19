#!/usr/bin/env python
"""
Diagnostic script to check media file configuration in production
Run this with: python manage.py shell < check_media_production.py
"""

import os
import sys
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

print("=" * 60)
print("MEDIA FILE CONFIGURATION CHECK")
print("=" * 60)

# Check basic settings
print("\n1. Basic Settings:")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')}")

# Check if using S3
using_s3 = hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID
print(f"   Using S3: {using_s3}")

if using_s3:
    print(f"   S3 Bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"   S3 Region: {getattr(settings, 'AWS_S3_REGION_NAME', 'Not set')}")

# Check media root directory
print("\n2. Media Directory Status:")
if settings.MEDIA_ROOT:
    if os.path.exists(settings.MEDIA_ROOT):
        print(f"   ✓ Media root exists: {settings.MEDIA_ROOT}")
        
        # Check permissions
        try:
            test_file = os.path.join(settings.MEDIA_ROOT, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("   ✓ Media root is writable")
        except Exception as e:
            print(f"   ✗ Media root is NOT writable: {e}")
            
        # Check subdirectories
        subdirs = [
            'announcements',
            'documents', 
            'constituents',
            'constituents/voter_id_photos',
            'voter_id_photos',
            'temp'
        ]
        
        print("\n3. Subdirectory Status:")
        for subdir in subdirs:
            path = os.path.join(settings.MEDIA_ROOT, subdir)
            if os.path.exists(path):
                print(f"   ✓ {subdir} exists")
                # Check if writable
                try:
                    test_file = os.path.join(path, '.test_write')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print(f"     └─ writable: YES")
                except:
                    print(f"     └─ writable: NO")
            else:
                print(f"   ✗ {subdir} does NOT exist")
    else:
        print(f"   ✗ Media root does NOT exist: {settings.MEDIA_ROOT}")

# Test file upload with Django storage
print("\n4. Testing Django Storage:")
try:
    # Try to save a test file
    test_content = ContentFile(b"Test content")
    test_path = default_storage.save('test_upload.txt', test_content)
    print(f"   ✓ File saved successfully: {test_path}")
    
    # Try to read it back
    if default_storage.exists(test_path):
        print("   ✓ File exists in storage")
        # Clean up
        default_storage.delete(test_path)
        print("   ✓ File deleted successfully")
    else:
        print("   ✗ File does not exist after save")
        
except Exception as e:
    print(f"   ✗ Storage test failed: {e}")
    import traceback
    traceback.print_exc()

# Check specific model upload paths
print("\n5. Model Upload Paths:")
from apps.constituents.models import FahanieCaresMember

# Get upload path for voter ID
upload_to = FahanieCaresMember._meta.get_field('voter_id_photo').upload_to
if callable(upload_to):
    print(f"   Voter ID upload_to: {upload_to.__name__} (function)")
else:
    print(f"   Voter ID upload_to: {upload_to}")

# Test creating a member instance path
print("\n6. Testing Member Instance:")
try:
    from apps.users.models import User
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='media_test_user',
        defaults={
            'email': 'mediatest@example.com',
            'first_name': 'Media',
            'last_name': 'Test'
        }
    )
    
    # Create a test member instance
    member = FahanieCaresMember(
        user=test_user,
        first_name='Test',
        last_name='User',
        email='test@example.com',
        contact_number='09123456789'
    )
    
    # Get the upload path that would be used
    if callable(upload_to):
        path = upload_to(member, 'test_photo.jpg')
        print(f"   Generated upload path: {path}")
    
    # Clean up
    if created:
        test_user.delete()
        
except Exception as e:
    print(f"   ✗ Model test failed: {e}")

print("\n" + "=" * 60)
print("END OF DIAGNOSTIC")
print("=" * 60)