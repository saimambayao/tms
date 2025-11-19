#!/usr/bin/env python3
"""
Test script to verify registration flow works locally
Run this after starting Docker: python test_registration_flow.py
"""

import requests
import time
from io import BytesIO
from PIL import Image
import os

# Configuration
BASE_URL = "http://localhost:3000"
REGISTER_URL = f"{BASE_URL}/accounts/register/"

# Test user data
test_user = {
    "username": f"testuser_{int(time.time())}",
    "password1": "TestPass123",
    "password2": "TestPass123",
    "email": f"test_{int(time.time())}@example.com",
    "first_name": "Test",
    "last_name": "User",
    "middle_name": "Middle",
    "contact_number": "09123456789",
    "age": "25",
    "sex": "male",
    "address_barangay": "Test Barangay",
    "address_municipality": "Ampatuan",
    "address_province": "Maguindanao del Sur",
    "voter_address_barangay": "Test Barangay",
    "voter_address_municipality": "Ampatuan", 
    "voter_address_province": "Maguindanao del Sur",
    "sector": "student_assistance",  # Using full value from SECTOR_CHOICES
    "highest_education": "bachelors",  # Using full value from EDUCATION_CHOICES
    "school_graduated": "Test University",
    "eligibility": "none",
    "is_volunteer_teacher": "",
    "volunteer_school": "",
    "volunteer_service_length": "",
    "terms": "on"
}

def create_test_image():
    """Create a simple test image for voter ID"""
    img = Image.new('RGB', (200, 100), color='lightblue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_registration():
    print("Testing #FahanieCares Member Registration Flow")
    print("=" * 50)
    
    # Create a session to handle cookies
    session = requests.Session()
    
    # Step 1: Get the registration page to get CSRF token
    print("\n1. Fetching registration page...")
    try:
        response = session.get(REGISTER_URL)
        if response.status_code == 200:
            print("✓ Registration page loaded successfully")
            
            # Extract CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if csrf_token:
                print(f"✓ CSRF token found: {csrf_token[:20]}...")
            else:
                print("✗ CSRF token not found")
                return
        else:
            print(f"✗ Failed to load registration page: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Error loading registration page: {e}")
        return
    
    # Step 2: Submit registration form
    print("\n2. Submitting registration form...")
    
    # Add CSRF token to form data
    test_user['csrfmiddlewaretoken'] = csrf_token
    
    # Create test image for voter ID
    test_image = create_test_image()
    
    # Prepare files
    files = {
        'voter_id_photo': ('test_voter_id.jpg', test_image, 'image/jpeg')
    }
    
    try:
        response = session.post(REGISTER_URL, data=test_user, files=files)
        
        print(f"Response status: {response.status_code}")
        
        print(f"Response URL: {response.url}")
        
        # Always save response for debugging
        with open('registration_response.html', 'w') as f:
            f.write(response.text)
        print("Response saved to registration_response.html for debugging")
        
        if response.status_code == 200 or response.status_code == 302:
            # Check if we were redirected to success page
            if "registration_success" in response.url or "success" in response.text.lower():
                print("✓ Registration successful!")
            else:
                # Check for form errors
                if "errorlist" in response.text or "field-validation-error" in response.text:
                    print("✗ Form validation errors:")
                    # Extract error messages
                    import re
                    errors = re.findall(r'class="errorlist.*?>(.*?)</ul>', response.text, re.DOTALL)
                    for error in errors:
                        print(f"  - {error.strip()}")
                else:
                    print("✗ Registration failed - no success redirect")
                    # Check if there's a success message in the page
                    if "has been submitted successfully" in response.text:
                        print("  But found success message in response!")
        else:
            print(f"✗ Registration failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error submitting registration: {e}")
        
    # Step 3: Check database (if we have admin access)
    print("\n3. Checking if user was created...")
    try:
        # Try to login with the new credentials
        login_data = {
            'username': test_user['username'],
            'password': test_user['password1'],
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/accounts/login/", data=login_data)
        
        if login_response.status_code == 200 and "logout" in login_response.text.lower():
            print("✓ User can login - registration successful!")
        else:
            print("✗ Cannot login with new user credentials")
            
    except Exception as e:
        print(f"✗ Error checking login: {e}")

if __name__ == "__main__":
    # Check if local server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✓ Local server is running at {BASE_URL}")
    except:
        print(f"✗ Local server is not running at {BASE_URL}")
        print("Please start the Docker containers first: docker-compose up -d")
        exit(1)
    
    test_registration()