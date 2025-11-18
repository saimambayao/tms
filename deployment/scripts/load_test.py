#!/usr/bin/env python3

"""
#FahanieCares Platform - Load Testing Script
Comprehensive load testing for production scenarios using locust
"""

import os
import sys
import time
import random
import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class FahanieCaresUser(HttpUser):
    """
    Simulates realistic user behavior on the #FahanieCares platform.
    """
    
    wait_time = between(2, 8)  # Realistic wait time between requests
    
    def on_start(self):
        """Initialize user session."""
        self.test_user_data = {
            'first_name': f'Test{random.randint(1000, 9999)}',
            'last_name': f'User{random.randint(1000, 9999)}',
            'email': f'test{random.randint(1000, 9999)}@example.com',
            'phone_number': f'+6391{random.randint(10000000, 99999999)}'
        }
        
        # Get CSRF token for forms
        self.csrf_token = None
        self.get_csrf_token()
    
    def get_csrf_token(self):
        """Get CSRF token from a page with forms."""
        try:
            response = self.client.get('/contact/')
            if 'csrfmiddlewaretoken' in response.text:
                # Extract CSRF token from response
                import re
                match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']*)["\']', response.text)
                if match:
                    self.csrf_token = match.group(1)
        except Exception as e:
            print(f"Failed to get CSRF token: {e}")
    
    @task(30)
    def view_homepage(self):
        """Most common user action - viewing the homepage."""
        self.client.get('/', name="Homepage")
    
    @task(20)
    def view_services(self):
        """View services and programs."""
        endpoints = [
            '/programs/',
            '/ministries-ppas/',
            '/accessible-ministry-programs/',
            '/services/'
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, name="Services Page")
    
    @task(15)
    def view_chapters(self):
        """View chapters information."""
        self.client.get('/about-chapters/', name="Chapters Page")
        
        # Sometimes also view chapter list
        if random.random() < 0.3:
            self.client.get('/chapters/', name="Chapter List")
    
    @task(10)
    def view_about_contact(self):
        """View about and contact pages."""
        pages = ['/about/', '/contact/']
        page = random.choice(pages)
        self.client.get(page, name="About/Contact Page")
    
    @task(8)
    def view_updates(self):
        """View announcements and updates."""
        self.client.get('/updates/', name="Updates Page")
    
    @task(5)
    def health_checks(self):
        """Health check endpoints (monitoring systems)."""
        endpoints = ['/health/', '/ready/', '/metrics/']
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, name="Health Check")
    
    @task(3)
    def member_registration_flow(self):
        """Simulate member registration process."""
        # View registration page
        response = self.client.get('/member-registration/', name="Registration Form")
        
        if response.status_code == 200 and self.csrf_token:
            # Submit registration (with test data)
            form_data = {
                'csrfmiddlewaretoken': self.csrf_token,
                'first_name': self.test_user_data['first_name'],
                'last_name': self.test_user_data['last_name'],
                'email': self.test_user_data['email'],
                'phone_number': self.test_user_data['phone_number'],
                'current_province': 'Maguindanao del Sur',
                'current_municipality': 'Cotabato City',
                'voter_province': 'Maguindanao del Sur',
                'voter_municipality': 'Cotabato City',
                'sector': 'professional',
                'education_level': 'college',
                'terms_accepted': 'on'
            }
            
            self.client.post(
                '/member-registration/', 
                data=form_data,
                name="Submit Registration"
            )
    
    @task(2)
    def contact_form_submission(self):
        """Simulate contact form submission."""
        if self.csrf_token:
            form_data = {
                'csrfmiddlewaretoken': self.csrf_token,
                'first_name': self.test_user_data['first_name'],
                'last_name': self.test_user_data['last_name'],
                'email': self.test_user_data['email'],
                'phone_number': self.test_user_data['phone_number'],
                'subject': 'Load Test Message',
                'message': 'This is a test message from load testing.'
            }
            
            self.client.post(
                '/contact/', 
                data=form_data,
                name="Contact Form"
            )
    
    @task(2)
    def service_referral_flow(self):
        """Simulate service referral browsing."""
        # Browse services
        self.client.get('/referrals/services/', name="Browse Services")
        
        # View service details (simulate clicking on a service)
        if random.random() < 0.5:
            # Simulate viewing a specific service
            service_urls = [
                '/referrals/services/health-assistance/',
                '/referrals/services/education-support/',
                '/referrals/services/agricultural-programs/'
            ]
            service_url = random.choice(service_urls)
            self.client.get(service_url, name="Service Details", catch_response=True)
    
    @task(1)
    def admin_simulation(self):
        """Simulate admin/staff user behavior (login attempts)."""
        # Simulate login page access
        self.client.get('/accounts/login/', name="Login Page")
        
        # Note: We don't actually log in to avoid affecting real admin accounts


class HighVolumeUser(FahanieCaresUser):
    """Simulates high-volume usage patterns (e.g., during announcements)."""
    
    wait_time = between(1, 3)  # Faster interaction
    
    @task(50)
    def rapid_homepage_views(self):
        """Rapid homepage refreshes during high-traffic events."""
        self.client.get('/', name="High-Volume Homepage")
    
    @task(30)
    def announcement_checking(self):
        """Frequent announcement page checking."""
        self.client.get('/updates/', name="High-Volume Updates")
    
    @task(20)
    def service_browsing(self):
        """Intensive service browsing."""
        self.client.get('/programs/', name="High-Volume Programs")


class MobileUser(FahanieCaresUser):
    """Simulates mobile user behavior patterns."""
    
    wait_time = between(3, 10)  # Mobile users often have longer think time
    
    def on_start(self):
        super().on_start()
        # Add mobile user agent
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        })
    
    @task(40)
    def mobile_homepage(self):
        """Mobile homepage access."""
        self.client.get('/', name="Mobile Homepage")
    
    @task(25)
    def mobile_services(self):
        """Mobile service access."""
        self.client.get('/mobile/', name="Mobile Services")
    
    @task(20)
    def mobile_chapters(self):
        """Mobile chapter browsing."""
        self.client.get('/about-chapters/', name="Mobile Chapters")
    
    @task(10)
    def mobile_contact(self):
        """Mobile contact form."""
        self.client.get('/contact/', name="Mobile Contact")
    
    @task(5)
    def offline_sync(self):
        """Mobile offline sync simulation."""
        self.client.get('/api/mobile/sync/', name="Mobile Sync")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts."""
    print("=" * 60)
    print("🚀 Starting #FahanieCares Load Test")
    print(f"Target URL: {environment.host}")
    print(f"Test Duration: {getattr(environment.parsed_options, 'run_time', 'Not specified')}")
    print(f"Users: {getattr(environment.parsed_options, 'num_users', 'Not specified')}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops."""
    print("=" * 60)
    print("🏁 #FahanieCares Load Test Completed")
    print("=" * 60)


def run_load_test():
    """Run load test with predefined scenarios."""
    import subprocess
    import argparse
    
    parser = argparse.ArgumentParser(description='Run #FahanieCares load tests')
    parser.add_argument('--host', default='http://localhost:3000', help='Target host')
    parser.add_argument('--users', type=int, default=50, help='Number of concurrent users')
    parser.add_argument('--spawn-rate', type=int, default=5, help='Users spawned per second')
    parser.add_argument('--time', default='5m', help='Test duration')
    parser.add_argument('--scenario', choices=['normal', 'high-volume', 'mobile', 'mixed'], 
                       default='mixed', help='Test scenario')
    
    args = parser.parse_args()
    
    # Build locust command
    cmd = [
        'locust',
        '--host', args.host,
        '--users', str(args.users),
        '--spawn-rate', str(args.spawn_rate),
        '--run-time', args.time,
        '--headless'
    ]
    
    # Add user class based on scenario
    if args.scenario == 'normal':
        cmd.extend(['--locustfile', __file__, 'FahanieCaresUser'])
    elif args.scenario == 'high-volume':
        cmd.extend(['--locustfile', __file__, 'HighVolumeUser'])
    elif args.scenario == 'mobile':
        cmd.extend(['--locustfile', __file__, 'MobileUser'])
    else:  # mixed
        cmd.extend(['--locustfile', __file__])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Load test failed: {e}")
        return e.returncode
    except FileNotFoundError:
        print("Error: locust not found. Install with: pip install locust")
        print("Then run: python load_test.py --help")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(run_load_test())
    else:
        print("Usage examples:")
        print("  python load_test.py --users 100 --time 10m")
        print("  python load_test.py --scenario high-volume --users 200")
        print("  python load_test.py --host https://fahaniecares.ph --users 50")
        print("\nTo run with locust web UI:")
        print("  locust --host http://localhost:3000")