#!/usr/bin/env python3
"""
SSL Certificate Monitoring Script for #FahanieCares

This script monitors SSL certificate expiration and sends alerts
when certificates are nearing expiration.
"""

import ssl
import socket
import datetime
import smtplib
import json
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Tuple
import logging
import requests

# Configuration
DOMAINS = [
    "fahaniecares.ph",
    "www.fahaniecares.ph",
    "cdn.fahaniecares.ph"
]

# Alert thresholds (in days)
CRITICAL_THRESHOLD = 7
WARNING_THRESHOLD = 30
INFO_THRESHOLD = 60

# Email configuration
EMAIL_CONFIG = {
    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
    "from_email": os.getenv("SSL_ALERT_FROM", "ssl-monitor@fahaniecares.ph"),
    "to_emails": os.getenv("SSL_ALERT_TO", "admin@fahaniecares.ph,devops@fahaniecares.ph").split(","),
    "use_tls": True
}

# Slack webhook (optional)
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ssl-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SSLCertificateMonitor:
    """Monitor SSL certificates for expiration."""
    
    def __init__(self):
        self.results = []
    
    def check_certificate(self, hostname: str, port: int = 443) -> Dict:
        """Check SSL certificate for a given hostname."""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to the server
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate info
                    cert = ssock.getpeercert()
                    
                    # Parse expiration date
                    not_after = datetime.datetime.strptime(
                        cert['notAfter'], 
                        '%b %d %H:%M:%S %Y %Z'
                    )
                    
                    # Calculate days until expiration
                    days_remaining = (not_after - datetime.datetime.now()).days
                    
                    # Get issuer
                    issuer = dict(x[0] for x in cert['issuer'])
                    
                    # Determine status
                    if days_remaining <= CRITICAL_THRESHOLD:
                        status = "CRITICAL"
                        severity = 3
                    elif days_remaining <= WARNING_THRESHOLD:
                        status = "WARNING"
                        severity = 2
                    elif days_remaining <= INFO_THRESHOLD:
                        status = "INFO"
                        severity = 1
                    else:
                        status = "OK"
                        severity = 0
                    
                    result = {
                        "hostname": hostname,
                        "status": status,
                        "severity": severity,
                        "days_remaining": days_remaining,
                        "expiration_date": not_after.strftime("%Y-%m-%d %H:%M:%S"),
                        "issuer": issuer.get('organizationName', 'Unknown'),
                        "common_name": dict(x[0] for x in cert['subject']).get('commonName', hostname),
                        "san": self._get_san(cert),
                        "error": None
                    }
                    
                    logger.info(f"Checked {hostname}: {status} ({days_remaining} days remaining)")
                    return result
                    
        except Exception as e:
            logger.error(f"Error checking {hostname}: {str(e)}")
            return {
                "hostname": hostname,
                "status": "ERROR",
                "severity": 4,
                "days_remaining": -1,
                "expiration_date": None,
                "issuer": None,
                "common_name": None,
                "san": [],
                "error": str(e)
            }
    
    def _get_san(self, cert: Dict) -> List[str]:
        """Extract Subject Alternative Names from certificate."""
        san_list = []
        for ext in cert.get('subjectAltName', []):
            if ext[0] == 'DNS':
                san_list.append(ext[1])
        return san_list
    
    def check_all_domains(self) -> List[Dict]:
        """Check all configured domains."""
        self.results = []
        for domain in DOMAINS:
            result = self.check_certificate(domain)
            self.results.append(result)
        return self.results
    
    def generate_report(self) -> str:
        """Generate a human-readable report."""
        report = ["SSL Certificate Status Report", "=" * 50, ""]
        
        # Sort by severity
        sorted_results = sorted(self.results, key=lambda x: x['severity'], reverse=True)
        
        for result in sorted_results:
            report.append(f"Domain: {result['hostname']}")
            report.append(f"Status: {result['status']}")
            
            if result['error']:
                report.append(f"Error: {result['error']}")
            else:
                report.append(f"Days until expiration: {result['days_remaining']}")
                report.append(f"Expiration date: {result['expiration_date']}")
                report.append(f"Issuer: {result['issuer']}")
                report.append(f"Common Name: {result['common_name']}")
                if result['san']:
                    report.append(f"SAN: {', '.join(result['san'])}")
            
            report.append("")
        
        return "\n".join(report)
    
    def generate_html_report(self) -> str:
        """Generate HTML report for email."""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #22c55e; color: white; }
                .critical { background-color: #ef4444; color: white; }
                .warning { background-color: #f97316; color: white; }
                .info { background-color: #3b82f6; color: white; }
                .ok { background-color: #10b981; color: white; }
                .error { background-color: #6b7280; color: white; }
            </style>
        </head>
        <body>
            <h2>SSL Certificate Status Report - #FahanieCares</h2>
            <p>Generated on: {timestamp}</p>
            <table>
                <tr>
                    <th>Domain</th>
                    <th>Status</th>
                    <th>Days Remaining</th>
                    <th>Expiration Date</th>
                    <th>Issuer</th>
                </tr>
        """.format(timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        for result in sorted(self.results, key=lambda x: x['severity'], reverse=True):
            status_class = result['status'].lower()
            html += f"""
                <tr>
                    <td>{result['hostname']}</td>
                    <td class="{status_class}">{result['status']}</td>
                    <td>{result['days_remaining'] if result['days_remaining'] >= 0 else 'N/A'}</td>
                    <td>{result['expiration_date'] or 'N/A'}</td>
                    <td>{result['issuer'] or 'N/A'}</td>
                </tr>
            """
        
        html += """
            </table>
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                This is an automated SSL certificate monitoring report from #FahanieCares infrastructure.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def send_email_alert(self, force: bool = False):
        """Send email alert if needed."""
        # Check if we need to send an alert
        max_severity = max(result['severity'] for result in self.results)
        
        if max_severity == 0 and not force:
            logger.info("All certificates are OK, no alert needed")
            return
        
        # Prepare email
        subject = f"SSL Certificate Alert - {self._get_severity_text(max_severity)}"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['to_emails'])
        
        # Add text and HTML parts
        text_part = MIMEText(self.generate_report(), 'plain')
        html_part = MIMEText(self.generate_html_report(), 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        try:
            with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
                if EMAIL_CONFIG['use_tls']:
                    server.starttls()
                if EMAIL_CONFIG['smtp_user'] and EMAIL_CONFIG['smtp_password']:
                    server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_password'])
                server.send_message(msg)
                logger.info(f"Email alert sent to {EMAIL_CONFIG['to_emails']}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
    
    def send_slack_alert(self):
        """Send Slack alert if webhook is configured."""
        if not SLACK_WEBHOOK:
            return
        
        # Prepare Slack message
        max_severity = max(result['severity'] for result in self.results)
        
        if max_severity == 0:
            return
        
        color = {
            1: "#3b82f6",  # INFO - blue
            2: "#f97316",  # WARNING - orange
            3: "#ef4444",  # CRITICAL - red
            4: "#6b7280"   # ERROR - gray
        }.get(max_severity, "#22c55e")
        
        attachments = []
        for result in sorted(self.results, key=lambda x: x['severity'], reverse=True):
            if result['severity'] > 0:
                attachment = {
                    "color": color,
                    "title": f"{result['hostname']} - {result['status']}",
                    "fields": [
                        {
                            "title": "Days Remaining",
                            "value": str(result['days_remaining']),
                            "short": True
                        },
                        {
                            "title": "Expiration Date",
                            "value": result['expiration_date'] or "N/A",
                            "short": True
                        }
                    ]
                }
                if result['error']:
                    attachment['fields'].append({
                        "title": "Error",
                        "value": result['error'],
                        "short": False
                    })
                attachments.append(attachment)
        
        payload = {
            "text": f"SSL Certificate Alert - {self._get_severity_text(max_severity)}",
            "attachments": attachments
        }
        
        try:
            response = requests.post(SLACK_WEBHOOK, json=payload)
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
    
    def _get_severity_text(self, severity: int) -> str:
        """Get human-readable severity text."""
        return {
            0: "OK",
            1: "INFO",
            2: "WARNING",
            3: "CRITICAL",
            4: "ERROR"
        }.get(severity, "UNKNOWN")
    
    def save_results(self, filename: str = "/var/log/ssl-status.json"):
        """Save results to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "results": self.results
                }, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")


def main():
    """Main function."""
    monitor = SSLCertificateMonitor()
    
    # Check all domains
    monitor.check_all_domains()
    
    # Generate and print report
    print(monitor.generate_report())
    
    # Save results
    monitor.save_results()
    
    # Send alerts
    force_email = '--force-email' in sys.argv
    monitor.send_email_alert(force=force_email)
    monitor.send_slack_alert()
    
    # Exit with appropriate code
    max_severity = max(result['severity'] for result in monitor.results)
    if max_severity >= 3:  # CRITICAL or ERROR
        sys.exit(2)
    elif max_severity >= 2:  # WARNING
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()