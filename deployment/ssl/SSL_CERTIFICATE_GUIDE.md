# SSL Certificate Management Guide for #FahanieCares

## Overview

This guide provides comprehensive instructions for managing SSL certificates for the #FahanieCares platform. We support both Let's Encrypt (free, automated) and commercial SSL certificates.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial SSL Setup](#initial-ssl-setup)
3. [Let's Encrypt Setup](#lets-encrypt-setup)
4. [Commercial SSL Setup](#commercial-ssl-setup)
5. [Certificate Renewal](#certificate-renewal)
6. [Monitoring and Alerts](#monitoring-and-alerts)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

## Prerequisites

- Root access to the server
- Domain names properly configured in DNS
- Nginx installed and configured
- Python 3.8+ for monitoring scripts
- Email service configured for alerts

## Initial SSL Setup

### 1. Run the SSL Setup Script

```bash
cd /path/to/src/deployment
sudo ./ssl-setup.sh
```

The script will:
- Install required dependencies (certbot, openssl)
- Create SSL directories
- Generate Diffie-Hellman parameters
- Configure Nginx for SSL
- Set up auto-renewal (for Let's Encrypt)

### 2. Choose Certificate Type

When prompted, select:
- **Option 1**: Let's Encrypt (recommended for production)
- **Option 2**: Manual certificate installation

## Let's Encrypt Setup

### Automatic Setup

The SSL setup script handles Let's Encrypt automatically:

```bash
sudo ./ssl-setup.sh
# Select option 1 when prompted
```

### Manual Let's Encrypt Commands

If you need to manually manage Let's Encrypt certificates:

```bash
# Obtain new certificate
sudo certbot certonly --nginx -d fahaniecares.ph -d www.fahaniecares.ph -d cdn.fahaniecares.ph

# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# List certificates
sudo certbot certificates
```

### Let's Encrypt File Locations

- Certificate: `/etc/letsencrypt/live/fahaniecares.ph/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/fahaniecares.ph/privkey.pem`
- Chain: `/etc/letsencrypt/live/fahaniecares.ph/chain.pem`

## Commercial SSL Setup

### 1. Purchase SSL Certificate

Recommended providers:
- DigiCert
- GlobalSign
- Sectigo (formerly Comodo)
- GeoTrust

### 2. Generate CSR (Certificate Signing Request)

```bash
# Create private key
openssl genrsa -out /etc/ssl/fahaniecares/private/fahaniecares.key 4096

# Generate CSR
openssl req -new -key /etc/ssl/fahaniecares/private/fahaniecares.key \
  -out /etc/ssl/fahaniecares/fahaniecares.csr \
  -subj "/C=PH/ST=NCR/L=Manila/O=FahanieCares/CN=fahaniecares.ph"

# Add Subject Alternative Names
cat > /etc/ssl/fahaniecares/san.cnf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = fahaniecares.ph
DNS.2 = www.fahaniecares.ph
DNS.3 = cdn.fahaniecares.ph
EOF

# Generate CSR with SAN
openssl req -new -key /etc/ssl/fahaniecares/private/fahaniecares.key \
  -out /etc/ssl/fahaniecares/fahaniecares.csr \
  -config /etc/ssl/fahaniecares/san.cnf
```

### 3. Install Commercial Certificate

```bash
# Place certificate files
sudo cp your-certificate.crt /etc/ssl/fahaniecares/certs/fahaniecares.crt
sudo cp your-ca-bundle.crt /etc/ssl/fahaniecares/certs/fahaniecares-ca.crt
sudo cp your-private-key.key /etc/ssl/fahaniecares/private/fahaniecares.key

# Set permissions
sudo chmod 644 /etc/ssl/fahaniecares/certs/*.crt
sudo chmod 600 /etc/ssl/fahaniecares/private/*.key

# Update Nginx configuration
sudo nano /etc/nginx/snippets/ssl-fahaniecares.conf
# Comment out Let's Encrypt lines and uncomment manual certificate lines
```

## Certificate Renewal

### Let's Encrypt Auto-Renewal

Auto-renewal is configured by default via cron:

```bash
# Check auto-renewal status
sudo systemctl status certbot.timer

# View renewal configuration
sudo cat /etc/cron.daily/certbot-renew

# Test renewal
sudo certbot renew --dry-run
```

### Commercial Certificate Renewal

1. **60 days before expiration**: Generate new CSR
2. **45 days before expiration**: Purchase renewal
3. **30 days before expiration**: Install new certificate
4. **7 days before expiration**: Final verification

### Manual Renewal Process

```bash
# Backup current certificate
sudo cp -r /etc/ssl/fahaniecares /etc/ssl/fahaniecares.backup.$(date +%Y%m%d)

# Install new certificate
sudo cp new-certificate.crt /etc/ssl/fahaniecares/certs/fahaniecares.crt

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx

# Verify installation
echo | openssl s_client -servername fahaniecares.ph -connect fahaniecares.ph:443 2>/dev/null | openssl x509 -noout -dates
```

## Monitoring and Alerts

### 1. Enable SSL Monitoring

```bash
# Make monitoring script executable
chmod +x /path/to/src/deployment/ssl-monitor.py

# Add to crontab (daily check at 9 AM)
sudo crontab -e
0 9 * * * /usr/bin/python3 /path/to/src/deployment/ssl-monitor.py
```

### 2. Configure Email Alerts

Set environment variables for email alerts:

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SSL_ALERT_FROM="ssl-monitor@fahaniecares.ph"
export SSL_ALERT_TO="admin@fahaniecares.ph,devops@fahaniecares.ph"
```

### 3. Configure Slack Alerts (Optional)

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 4. Monitor Certificate Status

```bash
# Check current status
python3 /path/to/src/deployment/ssl-monitor.py

# Force email report
python3 /path/to/src/deployment/ssl-monitor.py --force-email

# View JSON status
cat /var/log/ssl-status.json
```

## Troubleshooting

### Common Issues

#### 1. Certificate Not Trusted

```bash
# Check certificate chain
openssl s_client -connect fahaniecares.ph:443 -showcerts

# Verify certificate
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt /path/to/certificate.crt
```

#### 2. Mixed Content Warnings

```bash
# Check for HTTP resources
grep -r "http://" /path/to/templates/
grep -r "http://" /path/to/static/

# Update to HTTPS or protocol-relative URLs
```

#### 3. SSL Handshake Failures

```bash
# Test SSL/TLS versions
openssl s_client -connect fahaniecares.ph:443 -tls1_2
openssl s_client -connect fahaniecares.ph:443 -tls1_3

# Check cipher suites
nmap --script ssl-enum-ciphers -p 443 fahaniecares.ph
```

#### 4. Certificate Renewal Failures

```bash
# Check Let's Encrypt logs
sudo journalctl -u certbot

# Verify DNS
dig fahaniecares.ph
dig www.fahaniecares.ph

# Test ACME challenge
sudo certbot certonly --nginx -d fahaniecares.ph --dry-run
```

### SSL Testing Tools

1. **SSL Labs**: https://www.ssllabs.com/ssltest/analyze.html?d=fahaniecares.ph
2. **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
3. **Security Headers**: https://securityheaders.com/?q=fahaniecares.ph

## Security Best Practices

### 1. Strong Configuration

```nginx
# Use modern SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256...;
ssl_prefer_server_ciphers off;
```

### 2. Security Headers

```nginx
# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Other security headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### 3. OCSP Stapling

```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
```

### 4. Certificate Pinning (Advanced)

For mobile apps or critical APIs:

```nginx
add_header Public-Key-Pins 'pin-sha256="base64+primary=="; pin-sha256="base64+backup=="; max-age=5184000; includeSubDomains' always;
```

### 5. Regular Audits

- Weekly: Check certificate expiration
- Monthly: Review SSL configuration
- Quarterly: Full security audit
- Yearly: Update SSL/TLS standards

## Emergency Procedures

### Certificate Expired

1. **Immediate Action**:
   ```bash
   # For Let's Encrypt
   sudo certbot renew --force-renewal
   sudo systemctl reload nginx
   
   # For commercial
   # Install backup certificate or generate self-signed temporarily
   ```

2. **Generate Emergency Self-Signed Certificate**:
   ```bash
   openssl req -x509 -nodes -days 30 -newkey rsa:4096 \
     -keyout /etc/ssl/emergency.key \
     -out /etc/ssl/emergency.crt \
     -subj "/CN=fahaniecares.ph"
   ```

3. **Notify Team**:
   - Send emergency alert
   - Update status page
   - Prepare incident report

### Compromised Private Key

1. **Revoke Certificate**:
   - Contact CA immediately
   - Submit revocation request

2. **Generate New Keys**:
   ```bash
   # Generate new private key
   openssl genrsa -out /etc/ssl/fahaniecares/private/fahaniecares-new.key 4096
   
   # Generate new CSR
   openssl req -new -key /etc/ssl/fahaniecares/private/fahaniecares-new.key \
     -out /etc/ssl/fahaniecares/fahaniecares-new.csr
   ```

3. **Install New Certificate**:
   - Obtain new certificate
   - Update all servers
   - Monitor for issues

## Maintenance Schedule

| Task | Frequency | Responsible | Notes |
|------|-----------|-------------|-------|
| Check expiration | Daily | Automated | Via ssl-monitor.py |
| Review alerts | Weekly | DevOps | Check email/Slack |
| Test renewal | Monthly | DevOps | Dry run |
| Update configuration | Quarterly | Security Team | Review best practices |
| Full audit | Yearly | External | Professional assessment |

## Contact Information

- **Security Team**: security@fahaniecares.ph
- **DevOps Team**: devops@fahaniecares.ph
- **Emergency**: +63-XXX-XXX-XXXX

---

Last Updated: January 2025
Maintained by: #FahanieCares Development Team