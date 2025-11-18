#!/bin/bash
# SSL Certificate Setup Script for #FahanieCares Production
# Sets up Let's Encrypt SSL certificates for secure HTTPS deployment

set -e

# Configuration
DOMAIN="fahaniecares.gov.ph"
WWW_DOMAIN="www.fahaniecares.gov.ph"
EMAIL="admin@fahaniecares.gov.ph"
STAGING=${STAGING:-false}
CERTBOT_DIR="/etc/letsencrypt"
NGINX_SSL_DIR="/etc/nginx/ssl"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log "ERROR: This script must be run as root"
        exit 1
    fi
}

# Install certbot if not present
install_certbot() {
    log "Installing certbot..."
    
    if command -v certbot >/dev/null 2>&1; then
        log "Certbot already installed"
        return
    fi
    
    # Install certbot based on OS
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    elif [ -f /etc/redhat-release ]; then
        yum install -y certbot python3-certbot-nginx
    else
        log "ERROR: Unsupported operating system"
        exit 1
    fi
    
    log "Certbot installed successfully"
}

# Setup nginx for initial certificate request
setup_initial_nginx() {
    log "Setting up initial nginx configuration..."
    
    # Create temporary nginx config for certificate validation
    cat > /tmp/nginx_ssl_setup.conf << EOF
server {
    listen 80;
    server_name $DOMAIN $WWW_DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'SSL setup in progress...';
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Create webroot directory
    mkdir -p /var/www/certbot
    
    # Backup existing nginx config and use temporary one
    if [ -f /etc/nginx/nginx.conf ]; then
        cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi
    
    # Test and reload nginx
    nginx -t && nginx -s reload || nginx
}

# Request SSL certificate
request_certificate() {
    log "Requesting SSL certificate for $DOMAIN and $WWW_DOMAIN..."
    
    # Determine certbot staging flag
    STAGING_FLAG=""
    if [ "$STAGING" = "true" ]; then
        STAGING_FLAG="--staging"
        log "Using Let's Encrypt staging environment"
    fi
    
    # Request certificate
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        $STAGING_FLAG \
        -d $DOMAIN \
        -d $WWW_DOMAIN
    
    if [ $? -eq 0 ]; then
        log "SSL certificate obtained successfully"
    else
        log "ERROR: Failed to obtain SSL certificate"
        exit 1
    fi
}

# Setup SSL certificate links
setup_certificate_links() {
    log "Setting up SSL certificate links..."
    
    # Create nginx SSL directory
    mkdir -p $NGINX_SSL_DIR
    
    # Create symbolic links to Let's Encrypt certificates
    ln -sf $CERTBOT_DIR/live/$DOMAIN/fullchain.pem $NGINX_SSL_DIR/fullchain.pem
    ln -sf $CERTBOT_DIR/live/$DOMAIN/privkey.pem $NGINX_SSL_DIR/privkey.pem
    
    # Set proper permissions
    chmod 644 $NGINX_SSL_DIR/fullchain.pem
    chmod 600 $NGINX_SSL_DIR/privkey.pem
    
    log "SSL certificate links created"
}

# Setup automatic certificate renewal
setup_certificate_renewal() {
    log "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/renew_fahaniecares_ssl.sh << 'EOF'
#!/bin/bash
# Automatic SSL certificate renewal for #FahanieCares

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a /var/log/ssl_renewal.log
}

log "Starting SSL certificate renewal check..."

# Attempt renewal
if certbot renew --quiet --no-self-upgrade; then
    log "Certificate renewal check completed successfully"
    
    # Test nginx configuration
    if nginx -t; then
        # Reload nginx to use new certificates
        nginx -s reload
        log "Nginx reloaded with updated certificates"
    else
        log "ERROR: Nginx configuration test failed"
        exit 1
    fi
else
    log "ERROR: Certificate renewal failed"
    exit 1
fi

log "SSL renewal process completed"
EOF
    
    chmod +x /usr/local/bin/renew_fahaniecares_ssl.sh
    
    # Add cron job for automatic renewal (runs twice daily)
    (crontab -l 2>/dev/null; echo "0 0,12 * * * /usr/local/bin/renew_fahaniecares_ssl.sh") | crontab -
    
    log "Automatic renewal configured (runs twice daily)"
}

# Restore production nginx configuration
restore_nginx_config() {
    log "Restoring production nginx configuration..."
    
    # Copy production nginx config
    if [ -f /var/www/fahaniecares/deployment/nginx.conf ]; then
        cp /var/www/fahaniecares/deployment/nginx.conf /etc/nginx/nginx.conf
    elif [ -f ./nginx.conf ]; then
        cp ./nginx.conf /etc/nginx/nginx.conf
    else
        log "ERROR: Production nginx.conf not found"
        exit 1
    fi
    
    # Test and reload nginx
    if nginx -t; then
        nginx -s reload
        log "Production nginx configuration restored and loaded"
    else
        log "ERROR: Production nginx configuration test failed"
        exit 1
    fi
}

# Main execution
main() {
    log "Starting SSL setup for #FahanieCares..."
    
    check_root
    install_certbot
    setup_initial_nginx
    request_certificate
    setup_certificate_links
    setup_certificate_renewal
    restore_nginx_config
    
    log "SSL setup completed successfully!"
    log "HTTPS is now available at: https://$DOMAIN"
    log "Certificate will auto-renew via cron job"
    
    # Display certificate information
    log "Certificate information:"
    certbot certificates
}

# Run main function
main "$@"