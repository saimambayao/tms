# SSL/TLS Configuration for #FahanieCares Production

This directory contains all SSL/TLS configuration files and scripts needed for secure HTTPS deployment of the #FahanieCares platform.

## Overview

The SSL configuration provides:
- ✅ **Let's Encrypt SSL Certificates** - Free, automated SSL certificates
- ✅ **Automatic Certificate Renewal** - No manual intervention required
- ✅ **Modern Security Standards** - TLS 1.2/1.3, strong ciphers, security headers
- ✅ **Government Compliance** - NIST cybersecurity guidelines
- ✅ **Performance Optimization** - OCSP stapling, session resumption
- ✅ **Monitoring & Verification** - Automated SSL health checks

## Files Structure

```
deployment/ssl/
├── README.md                 # This documentation
├── setup_ssl.sh             # Initial SSL certificate setup
├── verify_ssl.sh            # SSL verification and monitoring
├── ssl_security.conf        # Production security configuration  
├── docker-compose.ssl.yml   # Docker configuration with SSL
└── scripts/
    ├── renew_certificates.sh # Manual renewal script
    └── ssl_monitoring.sh     # Continuous monitoring
```

## Quick Start

### 1. Initial SSL Setup (Production)

```bash
# Navigate to SSL directory
cd deployment/ssl/

# Make scripts executable
chmod +x setup_ssl.sh verify_ssl.sh

# Run initial SSL setup (requires root/sudo)
sudo ./setup_ssl.sh

# Verify SSL configuration
./verify_ssl.sh
```

### 2. Docker Deployment with SSL

```bash
# Copy environment variables
cp .env.example .env.production
# Edit .env.production with your production values

# Deploy with SSL support
docker-compose -f docker-compose.yml -f ssl/docker-compose.ssl.yml up -d

# Verify SSL in Docker environment
docker exec fahaniecares_nginx_ssl nginx -t
```

### 3. Verify SSL is Working

```bash
# Check certificate validity
./verify_ssl.sh

# Test HTTPS access
curl -I https://fahaniecares.gov.ph

# Check SSL Labs rating (external)
# Visit: https://www.ssllabs.com/ssltest/
```

## Detailed Configuration Guide

### Environment Setup

1. **DNS Configuration**
   ```
   A    fahaniecares.gov.ph    → YOUR_SERVER_IP
   A    www.fahaniecares.gov.ph → YOUR_SERVER_IP
   ```

2. **Firewall Configuration**
   ```bash
   # Allow HTTP and HTTPS traffic
   sudo ufw allow 80
   sudo ufw allow 443
   
   # Enable firewall
   sudo ufw enable
   ```

3. **Domain Verification**
   ```bash
   # Verify DNS resolution
   nslookup fahaniecares.gov.ph
   nslookup www.fahaniecares.gov.ph
   ```

### SSL Certificate Setup

#### Staging Environment (Testing)
```bash
# Test with Let's Encrypt staging environment
STAGING=true sudo ./setup_ssl.sh
```

#### Production Environment
```bash
# Production SSL setup
sudo ./setup_ssl.sh
```

#### Manual Certificate Request
```bash
# Request certificate manually with certbot
sudo certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@fahaniecares.gov.ph \
  --agree-tos \
  --no-eff-email \
  -d fahaniecares.gov.ph \
  -d www.fahaniecares.gov.ph
```

### Security Configuration

The `ssl_security.conf` file contains production-ready security settings:

- **TLS 1.2/1.3 only** - Legacy protocols disabled
- **Modern cipher suites** - Strong encryption algorithms
- **Security headers** - HSTS, CSP, XSS protection
- **OCSP stapling** - Faster certificate validation
- **Performance optimization** - Session resumption, compression

Include in your nginx configuration:
```nginx
server {
    listen 443 ssl http2;
    server_name fahaniecares.gov.ph www.fahaniecares.gov.ph;
    
    # Include SSL security configuration
    include /etc/nginx/ssl/ssl_security.conf;
    
    # Your application configuration
    location / {
        proxy_pass http://web:8000;
        # ... other settings
    }
}
```

### Certificate Renewal

#### Automatic Renewal (Recommended)

The setup script configures automatic renewal via cron:
```bash
# Check cron configuration
sudo crontab -l | grep certbot

# Manual test of renewal
sudo certbot renew --dry-run
```

#### Manual Renewal
```bash
# Renew certificates manually
sudo certbot renew

# Reload nginx after renewal
sudo nginx -s reload
```

### Monitoring and Verification

#### Daily SSL Checks
```bash
# Run verification script
./verify_ssl.sh

# Check certificate expiry
sudo certbot certificates
```

#### SSL Labs Rating
- Visit [SSL Labs](https://www.ssllabs.com/ssltest/)
- Enter: `fahaniecares.gov.ph`
- Target: **A+ rating**

#### Security Headers Check
```bash
# Check security headers
curl -I https://fahaniecares.gov.ph | grep -E "(Strict-Transport|X-Content|X-Frame|Content-Security)"
```

## Docker Integration

### SSL-Enabled Docker Compose

The `docker-compose.ssl.yml` extends the main configuration with:

1. **Certbot Service** - Automatic certificate management
2. **SSL Renewal Service** - Continuous certificate renewal
3. **Enhanced Nginx** - SSL-aware reverse proxy
4. **Security Environment** - SSL-specific Django settings

### Docker SSL Commands

```bash
# View certificate status in Docker
docker-compose exec certbot certbot certificates

# Renew certificates in Docker
docker-compose exec ssl_renewer certbot renew

# Check nginx SSL config
docker-compose exec nginx nginx -t

# View nginx SSL logs
docker-compose logs nginx | grep SSL
```

## Security Best Practices

### 1. Certificate Security
- ✅ Private keys have 600 permissions
- ✅ Certificates stored in secure directories
- ✅ No hardcoded certificates in code
- ✅ Regular certificate monitoring

### 2. Configuration Security
- ✅ Only TLS 1.2/1.3 enabled
- ✅ Strong cipher suites only
- ✅ HSTS with preload enabled
- ✅ Security headers configured

### 3. Operational Security
- ✅ Automated certificate renewal
- ✅ Certificate expiry monitoring
- ✅ SSL configuration verification
- ✅ Performance monitoring

## Troubleshooting

### Common Issues

#### 1. Certificate Request Failed
```bash
# Check DNS resolution
nslookup fahaniecares.gov.ph

# Verify domain points to server
dig fahaniecares.gov.ph

# Check firewall allows port 80
sudo ufw status | grep 80
```

#### 2. Nginx SSL Errors
```bash
# Check nginx configuration
sudo nginx -t

# Check certificate files exist
ls -la /etc/letsencrypt/live/fahaniecares.gov.ph/

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/fahaniecares.gov.ph/fullchain.pem -noout -dates
```

#### 3. Renewal Issues
```bash
# Test renewal
sudo certbot renew --dry-run

# Check renewal configuration
sudo cat /etc/letsencrypt/renewal/fahaniecares.gov.ph.conf

# Check cron job
sudo crontab -l | grep certbot
```

#### 4. Docker SSL Issues
```bash
# Check container logs
docker-compose logs nginx
docker-compose logs certbot

# Verify volume mounts
docker-compose exec nginx ls -la /etc/letsencrypt/live/

# Test certificate in container
docker-compose exec nginx openssl x509 -in /etc/letsencrypt/live/fahaniecares.gov.ph/fullchain.pem -noout -dates
```

### Emergency Procedures

#### Certificate Expired
```bash
# Force certificate renewal
sudo certbot renew --force-renewal

# Restart nginx
sudo systemctl restart nginx

# Or in Docker
docker-compose restart nginx
```

#### SSL Configuration Issues
```bash
# Restore backup configuration
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf

# Test and reload
sudo nginx -t && sudo nginx -s reload
```

## Maintenance Schedule

### Daily (Automated)
- ✅ Certificate expiry checks
- ✅ SSL connection tests
- ✅ Security header verification

### Weekly
- ✅ SSL Labs rating check
- ✅ Configuration review
- ✅ Log analysis

### Monthly
- ✅ Security configuration updates
- ✅ Certificate renewal testing
- ✅ Performance optimization review

## Support and Documentation

### Official Documentation
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [NIST Cybersecurity Guidelines](https://www.nist.gov/cybersecurity)

### Internal Resources
- Main deployment guide: `../production_deployment_guide.md`
- Nginx configuration: `../nginx.conf`
- Docker configuration: `../docker-compose.yml`

### Emergency Contacts
- **System Administrator**: admin@fahaniecares.gov.ph
- **Security Team**: security@fahaniecares.gov.ph
- **MP Office**: mp@fahaniecares.gov.ph

---

**Last Updated**: June 7, 2024  
**Version**: 1.0  
**Prepared by**: #FahanieCares Development Team