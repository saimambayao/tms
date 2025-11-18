#!/bin/bash
# SSL Certificate Verification Script for #FahanieCares
# Checks SSL certificate status, expiry, and security configuration

set -e

# Configuration
DOMAIN="fahaniecares.gov.ph"
WWW_DOMAIN="www.fahaniecares.gov.ph"
LOG_FILE="/var/log/ssl_verification.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check certificate validity
check_certificate_validity() {
    log "${BLUE}Checking SSL certificate validity...${NC}"
    
    for domain in "$DOMAIN" "$WWW_DOMAIN"; do
        log "Checking certificate for: $domain"
        
        # Get certificate information
        cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            log "${GREEN}✓ Certificate found for $domain${NC}"
            
            # Extract expiry date
            expiry_date=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
            log "  Expires: $expiry_date"
            
            # Check if certificate expires within 30 days
            expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s 2>/dev/null)
            current_epoch=$(date +%s)
            days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
            
            if [ $days_until_expiry -lt 30 ]; then
                log "${YELLOW}⚠ Certificate expires in $days_until_expiry days - renewal needed${NC}"
            elif [ $days_until_expiry -lt 7 ]; then
                log "${RED}⚠ URGENT: Certificate expires in $days_until_expiry days!${NC}"
            else
                log "${GREEN}✓ Certificate valid for $days_until_expiry days${NC}"
            fi
        else
            log "${RED}✗ Failed to retrieve certificate for $domain${NC}"
        fi
    done
}

# Check SSL security configuration
check_ssl_security() {
    log "${BLUE}Checking SSL security configuration...${NC}"
    
    # Check SSL Labs rating (if available)
    if command_exists curl; then
        log "Checking SSL Labs rating..."
        
        # Note: This is a simplified check. In production, you might want to use SSL Labs API
        # for a comprehensive security assessment
        
        # Check HTTPS redirect
        http_response=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" || echo "000")
        if [ "$http_response" = "301" ] || [ "$http_response" = "302" ]; then
            log "${GREEN}✓ HTTP to HTTPS redirect working${NC}"
        else
            log "${RED}✗ HTTP to HTTPS redirect not working (response: $http_response)${NC}"
        fi
        
        # Check HSTS header
        hsts_header=$(curl -s -I "https://$DOMAIN" | grep -i "strict-transport-security" || echo "")
        if [ -n "$hsts_header" ]; then
            log "${GREEN}✓ HSTS header present: $hsts_header${NC}"
        else
            log "${RED}✗ HSTS header missing${NC}"
        fi
        
        # Check security headers
        log "Checking security headers..."
        
        headers=$(curl -s -I "https://$DOMAIN")
        
        # X-Content-Type-Options
        if echo "$headers" | grep -qi "x-content-type-options"; then
            log "${GREEN}✓ X-Content-Type-Options header present${NC}"
        else
            log "${YELLOW}⚠ X-Content-Type-Options header missing${NC}"
        fi
        
        # X-Frame-Options
        if echo "$headers" | grep -qi "x-frame-options"; then
            log "${GREEN}✓ X-Frame-Options header present${NC}"
        else
            log "${YELLOW}⚠ X-Frame-Options header missing${NC}"
        fi
        
        # CSP header
        if echo "$headers" | grep -qi "content-security-policy"; then
            log "${GREEN}✓ Content-Security-Policy header present${NC}"
        else
            log "${YELLOW}⚠ Content-Security-Policy header missing${NC}"
        fi
    fi
}

# Check SSL certificate files
check_certificate_files() {
    log "${BLUE}Checking SSL certificate files...${NC}"
    
    # Check if running in Docker or host system
    if [ -f /.dockerenv ]; then
        # Running in Docker
        CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
    else
        # Running on host system
        CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
    fi
    
    # Check certificate files
    if [ -f "$CERT_PATH/fullchain.pem" ]; then
        log "${GREEN}✓ Certificate file exists: $CERT_PATH/fullchain.pem${NC}"
        
        # Check certificate validity
        cert_validity=$(openssl x509 -in "$CERT_PATH/fullchain.pem" -noout -dates 2>/dev/null || echo "")
        if [ -n "$cert_validity" ]; then
            log "${GREEN}✓ Certificate file is valid${NC}"
            log "  $cert_validity"
        else
            log "${RED}✗ Certificate file is invalid or corrupted${NC}"
        fi
    else
        log "${RED}✗ Certificate file not found: $CERT_PATH/fullchain.pem${NC}"
    fi
    
    if [ -f "$CERT_PATH/privkey.pem" ]; then
        log "${GREEN}✓ Private key file exists: $CERT_PATH/privkey.pem${NC}"
        
        # Check private key permissions
        key_perms=$(stat -c "%a" "$CERT_PATH/privkey.pem" 2>/dev/null || stat -f "%A" "$CERT_PATH/privkey.pem" 2>/dev/null || echo "unknown")
        if [ "$key_perms" = "600" ] || [ "$key_perms" = "400" ]; then
            log "${GREEN}✓ Private key has secure permissions: $key_perms${NC}"
        else
            log "${YELLOW}⚠ Private key permissions should be 600 or 400 (current: $key_perms)${NC}"
        fi
    else
        log "${RED}✗ Private key file not found: $CERT_PATH/privkey.pem${NC}"
    fi
}

# Check certificate renewal setup
check_renewal_setup() {
    log "${BLUE}Checking certificate renewal setup...${NC}"
    
    # Check if certbot is installed
    if command_exists certbot; then
        log "${GREEN}✓ Certbot is installed${NC}"
        
        # Check certbot certificates
        log "Certbot certificates:"
        certbot certificates 2>/dev/null | tee -a "$LOG_FILE" || log "${YELLOW}⚠ Could not list certbot certificates${NC}"
        
        # Check renewal configuration
        if [ -f "/etc/letsencrypt/renewal/$DOMAIN.conf" ]; then
            log "${GREEN}✓ Renewal configuration exists${NC}"
        else
            log "${YELLOW}⚠ Renewal configuration not found${NC}"
        fi
    else
        log "${RED}✗ Certbot not installed${NC}"
    fi
    
    # Check cron job for renewal
    if crontab -l 2>/dev/null | grep -q "certbot\|renew.*ssl"; then
        log "${GREEN}✓ SSL renewal cron job found${NC}"
        log "Cron jobs related to SSL:"
        crontab -l 2>/dev/null | grep -E "certbot|renew.*ssl" | tee -a "$LOG_FILE"
    else
        log "${YELLOW}⚠ SSL renewal cron job not found${NC}"
    fi
}

# Performance test
test_ssl_performance() {
    log "${BLUE}Testing SSL connection performance...${NC}"
    
    if command_exists curl; then
        for domain in "$DOMAIN" "$WWW_DOMAIN"; do
            log "Testing performance for: $domain"
            
            # Measure connection time
            connection_time=$(curl -o /dev/null -s -w "%{time_connect}\n" "https://$domain" 2>/dev/null || echo "failed")
            
            if [ "$connection_time" != "failed" ]; then
                log "${GREEN}✓ SSL connection time: ${connection_time}s${NC}"
                
                # Check if connection time is reasonable (< 2 seconds)
                if [ "$(echo "$connection_time < 2.0" | bc -l 2>/dev/null || echo "1")" = "1" ]; then
                    log "${GREEN}✓ Connection time is acceptable${NC}"
                else
                    log "${YELLOW}⚠ Connection time is slow (>${connection_time}s)${NC}"
                fi
            else
                log "${RED}✗ Failed to connect to $domain${NC}"
            fi
        done
    fi
}

# Generate SSL report
generate_report() {
    log "${BLUE}Generating SSL verification report...${NC}"
    
    {
        echo "================================"
        echo "#FahanieCares SSL Status Report"
        echo "Generated: $(date)"
        echo "================================"
        echo ""
        echo "Domain: $DOMAIN"
        echo "WWW Domain: $WWW_DOMAIN"
        echo ""
        echo "Log file: $LOG_FILE"
        echo ""
        echo "Summary:"
        echo "- Certificate validity: Check log for details"
        echo "- Security headers: Check log for details"
        echo "- File integrity: Check log for details"
        echo "- Renewal setup: Check log for details"
        echo "- Performance: Check log for details"
        echo ""
        echo "For detailed results, see: $LOG_FILE"
        echo ""
    } > "/tmp/ssl_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log "${GREEN}SSL verification report generated${NC}"
}

# Main execution
main() {
    log "${BLUE}Starting SSL verification for #FahanieCares...${NC}"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    check_certificate_validity
    echo ""
    check_ssl_security  
    echo ""
    check_certificate_files
    echo ""
    check_renewal_setup
    echo ""
    test_ssl_performance
    echo ""
    generate_report
    
    log "${GREEN}SSL verification completed!${NC}"
    log "Review the full log at: $LOG_FILE"
}

# Show usage if help requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "SSL Certificate Verification Script for #FahanieCares"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo ""
    echo "This script checks:"
    echo "  - SSL certificate validity and expiry"
    echo "  - SSL security configuration"
    echo "  - Certificate file integrity" 
    echo "  - Renewal setup and cron jobs"
    echo "  - SSL connection performance"
    echo ""
    echo "Log file: $LOG_FILE"
    exit 0
fi

# Run main function
main "$@"