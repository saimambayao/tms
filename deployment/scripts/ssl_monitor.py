#!/usr/bin/env python3

"""
#FahanieCares Platform - SSL Certificate Monitoring
Automated SSL certificate monitoring with expiry alerts
"""

import ssl
import socket
import datetime
import json
import sys
import argparse
import requests
from urllib.parse import urlparse


class SSLCertificateMonitor:
    """Monitor SSL certificates and send alerts for expiring certificates."""
    
    def __init__(self, slack_webhook=None, email_config=None):
        self.slack_webhook = slack_webhook
        self.email_config = email_config
        self.results = {}
    
    def check_certificate(self, hostname, port=443, timeout=10):
        """Check SSL certificate for a given hostname."""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to the server
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate information
                    cert_info = self.parse_certificate(cert, hostname)
                    self.results[hostname] = cert_info
                    
                    return cert_info
                    
        except socket.gaierror as e:
            error_info = {
                'hostname': hostname,
                'status': 'error',
                'error': f'DNS resolution failed: {e}',
                'checked_at': datetime.datetime.now().isoformat()
            }
            self.results[hostname] = error_info
            return error_info
            
        except socket.timeout as e:
            error_info = {
                'hostname': hostname,
                'status': 'error',
                'error': f'Connection timeout: {e}',
                'checked_at': datetime.datetime.now().isoformat()
            }
            self.results[hostname] = error_info
            return error_info
            
        except ssl.SSLError as e:
            error_info = {
                'hostname': hostname,
                'status': 'error',
                'error': f'SSL error: {e}',
                'checked_at': datetime.datetime.now().isoformat()
            }
            self.results[hostname] = error_info
            return error_info
            
        except Exception as e:
            error_info = {
                'hostname': hostname,
                'status': 'error',
                'error': f'Unexpected error: {e}',
                'checked_at': datetime.datetime.now().isoformat()
            }
            self.results[hostname] = error_info
            return error_info
    
    def parse_certificate(self, cert, hostname):
        """Parse certificate information."""
        try:
            # Extract expiry date
            not_after = cert['notAfter']
            expiry_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
            
            # Extract issue date
            not_before = cert['notBefore']
            issue_date = datetime.datetime.strptime(not_before, '%b %d %H:%M:%S %Y %Z')
            
            # Calculate days until expiry
            now = datetime.datetime.now()
            days_until_expiry = (expiry_date - now).days
            
            # Extract subject information
            subject = dict(x[0] for x in cert['subject'])
            
            # Extract issuer information
            issuer = dict(x[0] for x in cert['issuer'])
            
            # Extract Subject Alternative Names (SAN)
            san_list = []
            if 'subjectAltName' in cert:
                san_list = [san[1] for san in cert['subjectAltName'] if san[0] == 'DNS']
            
            # Determine certificate status
            if days_until_expiry < 0:
                status = 'expired'
            elif days_until_expiry <= 7:
                status = 'critical'
            elif days_until_expiry <= 30:
                status = 'warning'
            else:
                status = 'valid'
            
            cert_info = {
                'hostname': hostname,
                'status': status,
                'common_name': subject.get('commonName', 'Unknown'),
                'organization': subject.get('organizationName', 'Unknown'),
                'issuer': issuer.get('commonName', 'Unknown'),
                'issue_date': issue_date.isoformat(),
                'expiry_date': expiry_date.isoformat(),
                'days_until_expiry': days_until_expiry,
                'subject_alt_names': san_list,
                'serial_number': cert.get('serialNumber', 'Unknown'),
                'version': cert.get('version', 'Unknown'),
                'checked_at': datetime.datetime.now().isoformat()
            }
            
            return cert_info
            
        except Exception as e:
            return {
                'hostname': hostname,
                'status': 'error',
                'error': f'Certificate parsing failed: {e}',
                'checked_at': datetime.datetime.now().isoformat()
            }
    
    def check_multiple_hosts(self, hostnames):
        """Check certificates for multiple hostnames."""
        results = {}
        
        for hostname in hostnames:
            print(f"Checking certificate for {hostname}...")
            result = self.check_certificate(hostname)
            results[hostname] = result
            
            # Print status
            if result['status'] == 'error':
                print(f"  ❌ Error: {result['error']}")
            else:
                days = result.get('days_until_expiry', 0)
                status_emoji = {
                    'expired': '🔴',
                    'critical': '🟠', 
                    'warning': '🟡',
                    'valid': '🟢'
                }.get(result['status'], '❓')
                
                print(f"  {status_emoji} {result['status'].upper()}: expires in {days} days")
        
        return results
    
    def send_slack_notification(self, message, status='INFO'):
        """Send notification to Slack."""
        if not self.slack_webhook:
            return False
        
        emoji_map = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🚨',
            'ERROR': '❌',
            'SUCCESS': '✅'
        }
        
        emoji = emoji_map.get(status, 'ℹ️')
        
        payload = {
            'text': f"{emoji} #FahanieCares SSL Monitor: {message}",
            'username': 'SSL Monitor',
            'icon_emoji': ':lock:'
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False
    
    def generate_alert_message(self, cert_info):
        """Generate alert message for certificate status."""
        hostname = cert_info['hostname']
        status = cert_info['status']
        
        if status == 'error':
            return f"SSL check failed for {hostname}: {cert_info.get('error', 'Unknown error')}"
        
        days = cert_info.get('days_until_expiry', 0)
        expiry_date = cert_info.get('expiry_date', 'Unknown')
        
        if status == 'expired':
            return f"Certificate for {hostname} has EXPIRED! Expired on {expiry_date}"
        elif status == 'critical':
            return f"Certificate for {hostname} expires in {days} days! Expiry: {expiry_date}"
        elif status == 'warning':
            return f"Certificate for {hostname} expires in {days} days. Expiry: {expiry_date}"
        else:
            return f"Certificate for {hostname} is valid ({days} days remaining)"
    
    def check_and_alert(self, hostnames, alert_threshold_days=30):
        """Check certificates and send alerts if needed."""
        results = self.check_multiple_hosts(hostnames)
        
        alerts_sent = []
        
        for hostname, cert_info in results.items():
            status = cert_info['status']
            
            # Determine if alert should be sent
            should_alert = False
            alert_level = 'INFO'
            
            if status == 'error':
                should_alert = True
                alert_level = 'ERROR'
            elif status == 'expired':
                should_alert = True
                alert_level = 'CRITICAL'
            elif status == 'critical':
                should_alert = True
                alert_level = 'CRITICAL'
            elif status == 'warning':
                should_alert = True
                alert_level = 'WARNING'
            elif status == 'valid':
                days = cert_info.get('days_until_expiry', 0)
                if days <= alert_threshold_days:
                    should_alert = True
                    alert_level = 'WARNING'
            
            if should_alert:
                message = self.generate_alert_message(cert_info)
                
                # Send Slack notification
                if self.send_slack_notification(message, alert_level):
                    alerts_sent.append({
                        'hostname': hostname,
                        'level': alert_level,
                        'message': message,
                        'sent_at': datetime.datetime.now().isoformat()
                    })
        
        return {
            'certificates': results,
            'alerts_sent': alerts_sent,
            'summary': self.generate_summary(results)
        }
    
    def generate_summary(self, results):
        """Generate summary of certificate check results."""
        total = len(results)
        
        status_counts = {
            'valid': 0,
            'warning': 0,
            'critical': 0,
            'expired': 0,
            'error': 0
        }
        
        for cert_info in results.values():
            status = cert_info['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_certificates': total,
            'status_breakdown': status_counts,
            'checked_at': datetime.datetime.now().isoformat()
        }
    
    def save_results(self, filepath, results):
        """Save results to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save results: {e}")
            return False


def get_fahaniecares_domains():
    """Get list of domains to monitor for #FahanieCares."""
    return [
        'fahaniecares.ph',
        'www.fahaniecares.ph',
        # Add additional domains as needed
        # 'api.fahaniecares.ph',
        # 'admin.fahaniecares.ph',
    ]


def main():
    """Main function for SSL certificate monitoring."""
    parser = argparse.ArgumentParser(description='Monitor SSL certificates for #FahanieCares')
    parser.add_argument('--domains', nargs='+', help='Domains to check')
    parser.add_argument('--slack-webhook', help='Slack webhook URL for notifications')
    parser.add_argument('--threshold', type=int, default=30, help='Alert threshold in days')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--check-only', action='store_true', help='Check only, no alerts')
    
    args = parser.parse_args()
    
    # Use provided domains or default #FahanieCares domains
    domains = args.domains if args.domains else get_fahaniecares_domains()
    
    print("🔒 #FahanieCares SSL Certificate Monitor")
    print(f"📋 Checking {len(domains)} domain(s): {', '.join(domains)}")
    print(f"⏰ Alert threshold: {args.threshold} days")
    print("-" * 60)
    
    # Initialize monitor
    monitor = SSLCertificateMonitor(slack_webhook=args.slack_webhook)
    
    try:
        if args.check_only:
            # Check only mode
            results = monitor.check_multiple_hosts(domains)
            summary = monitor.generate_summary(results)
            
            final_results = {
                'certificates': results,
                'summary': summary,
                'mode': 'check_only'
            }
        else:
            # Check and alert mode
            final_results = monitor.check_and_alert(domains, args.threshold)
        
        # Print summary
        summary = final_results['summary']
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total certificates checked: {summary['total_certificates']}")
        
        for status, count in summary['status_breakdown'].items():
            if count > 0:
                emoji = {
                    'valid': '🟢',
                    'warning': '🟡', 
                    'critical': '🟠',
                    'expired': '🔴',
                    'error': '❌'
                }.get(status, '❓')
                print(f"{emoji} {status.upper()}: {count}")
        
        if 'alerts_sent' in final_results:
            alerts_count = len(final_results['alerts_sent'])
            if alerts_count > 0:
                print(f"📨 Alerts sent: {alerts_count}")
            else:
                print("📨 No alerts sent")
        
        # Save results if output file specified
        if args.output:
            if monitor.save_results(args.output, final_results):
                print(f"💾 Results saved to: {args.output}")
        
        # Determine exit code based on certificate status
        if summary['status_breakdown'].get('expired', 0) > 0:
            print("\n🚨 CRITICAL: One or more certificates have expired!")
            return 2
        elif summary['status_breakdown'].get('critical', 0) > 0:
            print("\n⚠️  WARNING: One or more certificates expire within 7 days!")
            return 1
        elif summary['status_breakdown'].get('error', 0) > 0:
            print("\n❌ ERROR: One or more certificate checks failed!")
            return 1
        else:
            print("\n✅ All certificates are healthy!")
            return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Certificate monitoring interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Certificate monitoring failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())