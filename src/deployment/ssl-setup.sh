#!/bin/bash

# SSL Certificate Setup Script for #FahanieCares
# This script handles SSL certificate installation and renewal
# Supports both Let's Encrypt (Certbot) and manual certificate installation

set -e

# Configuration
DOMAIN="fahaniecares.ph"
WWW_DOMAIN="www.fahaniecares.ph"
CDN_DOMAIN="cdn.fahaniecares.ph"
EMAIL="ssl@fahaniecares.ph"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
SSL_DIR="/etc/ssl/fahaniecares"
LE_DIR="/etc/letsencrypt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}#FahanieCares SSL Certificate Setup${NC}"
echo "======================================"

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root${NC}"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    apt-get update
    apt-get install -y certbot python3-certbot-nginx openssl
}

# Function to create SSL directories
create_ssl_directories() {
    echo -e "${YELLOW}Creating SSL directories...${NC}"
    mkdir -p $SSL_DIR
    mkdir -p $SSL_DIR/certs
    mkdir -p $SSL_DIR/private
    mkdir -p $SSL_DIR/dhparam
    chmod 700 $SSL_DIR/private
}

# Function to generate Diffie-Hellman parameters
generate_dhparam() {
    if [ ! -f "$SSL_DIR/dhparam/dhparam4096.pem" ]; then
        echo -e "${YELLOW}Generating Diffie-Hellman parameters (this may take a while)...${NC}"
        openssl dhparam -out $SSL_DIR/dhparam/dhparam4096.pem 4096
    else
        echo -e "${GREEN}Diffie-Hellman parameters already exist${NC}"
    fi
}

# Function to obtain Let's Encrypt certificate
obtain_letsencrypt_cert() {
    echo -e "${YELLOW}Obtaining Let's Encrypt certificate...${NC}"
    
    # Test if we can obtain a certificate (dry run)
    certbot certonly --nginx \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        --domains $DOMAIN,$WWW_DOMAIN,$CDN_DOMAIN \
        --dry-run
    
    if [ $? -eq 0 ]; then
        # Actually obtain the certificate
        certbot certonly --nginx \
            --non-interactive \
            --agree-tos \
            --email $EMAIL \
            --domains $DOMAIN,$WWW_DOMAIN,$CDN_DOMAIN
        
        echo -e "${GREEN}Let's Encrypt certificate obtained successfully${NC}"
        return 0
    else
        echo -e "${RED}Failed to obtain Let's Encrypt certificate${NC}"
        return 1
    fi
}

# Function to setup manual SSL certificate
setup_manual_cert() {
    echo -e "${YELLOW}Setting up manual SSL certificate...${NC}"
    
    # Check if certificate files exist
    if [ ! -f "$SSL_DIR/certs/fahaniecares.crt" ] || [ ! -f "$SSL_DIR/private/fahaniecares.key" ]; then
        echo -e "${RED}Certificate files not found in $SSL_DIR${NC}"
        echo "Please place your certificate files:"
        echo "  - Certificate: $SSL_DIR/certs/fahaniecares.crt"
        echo "  - Private Key: $SSL_DIR/private/fahaniecares.key"
        echo "  - CA Bundle (optional): $SSL_DIR/certs/fahaniecares-ca.crt"
        exit 1
    fi
    
    # Set proper permissions
    chmod 644 $SSL_DIR/certs/*.crt
    chmod 600 $SSL_DIR/private/*.key
    
    echo -e "${GREEN}Manual SSL certificate configured${NC}"
}

# Function to configure Nginx SSL
configure_nginx_ssl() {
    echo -e "${YELLOW}Configuring Nginx SSL...${NC}"
    
    # Create SSL configuration snippet
    cat > /etc/nginx/snippets/ssl-fahaniecares.conf <<EOF
# SSL Certificate Configuration
ssl_certificate $LE_DIR/live/$DOMAIN/fullchain.pem;
ssl_certificate_key $LE_DIR/live/$DOMAIN/privkey.pem;

# For manual certificates, use:
# ssl_certificate $SSL_DIR/certs/fahaniecares.crt;
# ssl_certificate_key $SSL_DIR/private/fahaniecares.key;
# ssl_trusted_certificate $SSL_DIR/certs/fahaniecares-ca.crt;

# SSL session caching
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# Diffie-Hellman parameter
ssl_dhparam $SSL_DIR/dhparam/dhparam4096.pem;

# Modern SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'" always;
EOF
    
    echo -e "${GREEN}Nginx SSL configuration created${NC}"
}

# Function to update Nginx site configuration
update_nginx_site() {
    echo -e "${YELLOW}Updating Nginx site configuration...${NC}"
    
    # Backup existing configuration
    cp $NGINX_SITES_AVAILABLE/fahaniecares $NGINX_SITES_AVAILABLE/fahaniecares.backup
    
    # Update the configuration to include SSL
    cat > $NGINX_SITES_AVAILABLE/fahaniecares-ssl <<'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name fahaniecares.ph www.fahaniecares.ph cdn.fahaniecares.ph;
    
    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name fahaniecares.ph www.fahaniecares.ph;
    
    # Include SSL configuration
    include /etc/nginx/snippets/ssl-fahaniecares.conf;
    
    # Root directory
    root /var/www/fahaniecares;
    
    # Django application
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias /var/www/fahaniecares/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/fahaniecares/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Security.txt
    location /.well-known/security.txt {
        alias /var/www/fahaniecares/security.txt;
    }
    
    # Favicon
    location /favicon.ico {
        alias /var/www/fahaniecares/static/images/favicon.ico;
        expires 30d;
        access_log off;
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# CDN subdomain
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name cdn.fahaniecares.ph;
    
    # Include SSL configuration
    include /etc/nginx/snippets/ssl-fahaniecares.conf;
    
    # Root directory for static assets
    root /var/www/fahaniecares;
    
    # Static files only
    location /static/ {
        alias /var/www/fahaniecares/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }
    
    # Media files
    location /media/ {
        alias /var/www/fahaniecares/media/;
        expires 30d;
        add_header Cache-Control "public";
        add_header Access-Control-Allow-Origin "*";
    }
    
    # Deny all other requests
    location / {
        return 404;
    }
}
EOF
    
    # Enable the new configuration
    ln -sf $NGINX_SITES_AVAILABLE/fahaniecares-ssl $NGINX_SITES_ENABLED/
    
    echo -e "${GREEN}Nginx site configuration updated${NC}"
}

# Function to test Nginx configuration
test_nginx_config() {
    echo -e "${YELLOW}Testing Nginx configuration...${NC}"
    nginx -t
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Nginx configuration is valid${NC}"
        return 0
    else
        echo -e "${RED}Nginx configuration is invalid${NC}"
        return 1
    fi
}

# Function to reload Nginx
reload_nginx() {
    echo -e "${YELLOW}Reloading Nginx...${NC}"
    systemctl reload nginx
    echo -e "${GREEN}Nginx reloaded${NC}"
}

# Function to setup auto-renewal
setup_auto_renewal() {
    echo -e "${YELLOW}Setting up auto-renewal...${NC}"
    
    # Create renewal script
    cat > /etc/cron.daily/certbot-renew <<'EOF'
#!/bin/bash
# Renew Let's Encrypt certificates
certbot renew --quiet --non-interactive --post-hook "systemctl reload nginx"

# Check certificate expiry and send notification
OPENSSL_OUTPUT=$(echo | openssl s_client -servername fahaniecares.ph -connect fahaniecares.ph:443 2>/dev/null | openssl x509 -noout -dates)
EXPIRY_DATE=$(echo "$OPENSSL_OUTPUT" | grep "notAfter" | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "SSL certificate expires in $DAYS_LEFT days" | mail -s "SSL Certificate Expiry Warning" ssl@fahaniecares.ph
fi
EOF
    
    chmod +x /etc/cron.daily/certbot-renew
    
    echo -e "${GREEN}Auto-renewal configured${NC}"
}

# Function to verify SSL installation
verify_ssl() {
    echo -e "${YELLOW}Verifying SSL installation...${NC}"
    
    # Check certificate
    echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -text | grep -E "Subject:|Issuer:|Not After"
    
    # Check SSL Labs grade (optional)
    echo -e "\n${YELLOW}You can check your SSL configuration at:${NC}"
    echo "https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
}

# Main execution
main() {
    check_root
    install_dependencies
    create_ssl_directories
    generate_dhparam
    
    echo -e "\n${YELLOW}Select SSL certificate option:${NC}"
    echo "1) Let's Encrypt (recommended for production)"
    echo "2) Manual certificate installation"
    read -p "Enter your choice (1 or 2): " choice
    
    case $choice in
        1)
            obtain_letsencrypt_cert
            if [ $? -eq 0 ]; then
                setup_auto_renewal
            fi
            ;;
        2)
            setup_manual_cert
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
    
    configure_nginx_ssl
    update_nginx_site
    
    if test_nginx_config; then
        reload_nginx
        verify_ssl
        echo -e "\n${GREEN}SSL setup completed successfully!${NC}"
    else
        echo -e "\n${RED}SSL setup failed. Please check the configuration.${NC}"
        exit 1
    fi
}

# Run main function
main