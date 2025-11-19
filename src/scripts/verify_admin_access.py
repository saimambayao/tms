#!/usr/bin/env python3
"""
Admin Access Verification Script for #FahanieCares
Verifies that admin accounts can access the portal and bypass authentication.
"""

import requests
import os
import sys

def test_admin_login(base_url, username, password):
    """Test admin login and portal access."""
    print(f"\n=== Testing {username} Login ===")
    
    # Create session
    session = requests.Session()
    
    # Get login page to retrieve CSRF token
    login_url = f"{base_url}/admin/login/"
    response = session.get(login_url)
    
    if response.status_code != 200:
        print(f"❌ Cannot access login page: {response.status_code}")
        return False
    
    # Extract CSRF token
    csrf_token = None
    for line in response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    if not csrf_token:
        print("❌ Could not find CSRF token")
        return False
    
    # Prepare login data
    login_data = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token,
        'next': '/admin/'
    }
    
    # Attempt login
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code == 302:
        print(f"✅ {username} login successful!")
        
        # Test admin access
        admin_response = session.get(f"{base_url}/admin/")
        if admin_response.status_code == 200:
            print(f"✅ {username} can access admin portal!")
            return True
        else:
            print(f"❌ {username} cannot access admin portal: {admin_response.status_code}")
            return False
    else:
        print(f"❌ {username} login failed: {login_response.status_code}")
        if "Please enter a correct username and password" in login_response.text:
            print("   Authentication error still occurring")
        return False

def main():
    """Main verification function."""
    base_url = "http://localhost:3000"
    
    print("🔍 #FahanieCares Admin Access Verification")
    print("=" * 50)
    
    # Test both admin accounts
    admin_success = test_admin_login(base_url, "admin", "admin123")
    saidamen_success = test_admin_login(base_url, "saidamen.m", "saidamen123")
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    if admin_success and saidamen_success:
        print("✅ ALL ADMIN ACCOUNTS WORKING")
        print("🎉 Admin bypass authentication successful!")
        print("\n📋 ADMIN CREDENTIALS:")
        print("   Username: admin       | Password: admin123")
        print("   Username: saidamen.m  | Password: saidamen123")
        print("\n🌐 Access URL: http://localhost:3000/admin/")
    else:
        print("❌ SOME ADMIN ACCOUNTS FAILED")
        if not admin_success:
            print("   - admin account failed")
        if not saidamen_success:
            print("   - saidamen.m account failed")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server at http://localhost:3000")
        print("   Make sure the server is running with: python3 manage.py runserver 3000")
    except Exception as e:
        print(f"❌ Verification failed: {e}")