#!/bin/bash

# #FahanieCares Platform - SSL Certificate Monitoring Cron Setup
# Automated setup of SSL certificate monitoring with cron jobs

set -euo pipefail

# Configuration
SCRIPT_DIR="$(dirname "$0")"
SSL_MONITOR_SCRIPT="$SCRIPT_DIR/ssl_monitor.py"
LOG_DIR="/var/log/fahaniecares"
CRON_USER="${CRON_USER:-$(whoami)}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if script exists
check_ssl_monitor_script() {
    if [ ! -f "$SSL_MONITOR_SCRIPT" ]; then
        log "ERROR: SSL monitor script not found at $SSL_MONITOR_SCRIPT"
        return 1
    fi
    
    # Make script executable
    chmod +x "$SSL_MONITOR_SCRIPT"
    log "SSL monitor script found and made executable"
    return 0
}

# Create log directory
setup_log_directory() {
    if [ ! -d "$LOG_DIR" ]; then
        sudo mkdir -p "$LOG_DIR"
        sudo chown "$CRON_USER:$CRON_USER" "$LOG_DIR"
        log "Created log directory: $LOG_DIR"
    else
        log "Log directory already exists: $LOG_DIR"
    fi
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies for SSL monitoring..."
    
    # Check if pip3 is available
    if ! command -v pip3 >/dev/null 2>&1; then
        log "ERROR: pip3 not found. Please install Python 3 and pip3"
        return 1
    fi
    
    # Install required packages
    pip3 install requests urllib3 --user
    
    log "Python dependencies installed successfully"
    return 0
}

# Create cron jobs
setup_cron_jobs() {
    log "Setting up cron jobs for SSL certificate monitoring..."
    
    # Create temporary cron file
    local temp_cron="/tmp/fahaniecares_ssl_cron"
    
    # Get current crontab (if any)
    (crontab -l 2>/dev/null || true) > "$temp_cron"
    
    # Remove existing #FahanieCares SSL monitoring entries
    grep -v "#FahanieCares SSL Monitor" "$temp_cron" > "${temp_cron}.new" || true
    mv "${temp_cron}.new" "$temp_cron"
    
    # Add new cron entries
    cat >> "$temp_cron" << EOF

# #FahanieCares SSL Monitor - Daily certificate check
0 9 * * * /usr/bin/python3 "$SSL_MONITOR_SCRIPT" --threshold 30 --slack-webhook "$SLACK_WEBHOOK" --output "$LOG_DIR/ssl_check_daily.json" >> "$LOG_DIR/ssl_monitor.log" 2>&1

# #FahanieCares SSL Monitor - Weekly detailed report  
0 9 * * 1 /usr/bin/python3 "$SSL_MONITOR_SCRIPT" --threshold 60 --slack-webhook "$SLACK_WEBHOOK" --output "$LOG_DIR/ssl_check_weekly.json" >> "$LOG_DIR/ssl_monitor_weekly.log" 2>&1

# #FahanieCares SSL Monitor - Critical alert check (every 6 hours)
0 */6 * * * /usr/bin/python3 "$SSL_MONITOR_SCRIPT" --threshold 7 --slack-webhook "$SLACK_WEBHOOK" --output "$LOG_DIR/ssl_check_critical.json" >> "$LOG_DIR/ssl_monitor_critical.log" 2>&1

EOF

    # Install new crontab
    if crontab "$temp_cron"; then
        log "Cron jobs installed successfully"
        rm -f "$temp_cron"
        return 0
    else
        log "ERROR: Failed to install cron jobs"
        rm -f "$temp_cron"
        return 1
    fi
}

# Create systemd timer (alternative to cron)
setup_systemd_timer() {
    log "Setting up systemd timer for SSL certificate monitoring..."
    
    # Check if systemd is available
    if ! command -v systemctl >/dev/null 2>&1; then
        log "Systemd not available, skipping systemd timer setup"
        return 0
    fi
    
    # Create service file
    sudo tee /etc/systemd/system/fahaniecares-ssl-monitor.service > /dev/null << EOF
[Unit]
Description=#FahanieCares SSL Certificate Monitor
Wants=fahaniecares-ssl-monitor.timer

[Service]
Type=oneshot
User=$CRON_USER
ExecStart=/usr/bin/python3 $SSL_MONITOR_SCRIPT --threshold 30 --slack-webhook "$SLACK_WEBHOOK" --output $LOG_DIR/ssl_check_systemd.json
StandardOutput=append:$LOG_DIR/ssl_monitor_systemd.log
StandardError=append:$LOG_DIR/ssl_monitor_systemd.log

[Install]
WantedBy=multi-user.target
EOF

    # Create timer file
    sudo tee /etc/systemd/system/fahaniecares-ssl-monitor.timer > /dev/null << EOF
[Unit]
Description=Run #FahanieCares SSL Certificate Monitor daily
Requires=fahaniecares-ssl-monitor.service

[Timer]
OnCalendar=daily
RandomizedDelaySec=300
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Reload systemd and enable timer
    sudo systemctl daemon-reload
    sudo systemctl enable fahaniecares-ssl-monitor.timer
    sudo systemctl start fahaniecares-ssl-monitor.timer
    
    log "Systemd timer setup completed"
    return 0
}

# Test SSL monitoring
test_ssl_monitoring() {
    log "Testing SSL certificate monitoring..."
    
    # Run a test check
    if python3 "$SSL_MONITOR_SCRIPT" --check-only --domains fahaniecares.ph; then
        log "✓ SSL monitoring test passed"
        return 0
    else
        log "✗ SSL monitoring test failed"
        return 1
    fi
}

# Show status
show_status() {
    log "=== SSL Certificate Monitoring Status ==="
    
    # Check cron jobs
    log "Cron jobs:"
    crontab -l 2>/dev/null | grep -A 5 -B 1 "#FahanieCares SSL Monitor" || log "  No cron jobs found"
    
    # Check systemd timers
    if command -v systemctl >/dev/null 2>&1; then
        log "Systemd timers:"
        systemctl list-timers fahaniecares-ssl-monitor.timer 2>/dev/null || log "  No systemd timers found"
    fi
    
    # Check recent logs
    if [ -d "$LOG_DIR" ]; then
        log "Recent log files:"
        ls -la "$LOG_DIR"/ssl_* 2>/dev/null || log "  No log files found"
    fi
}

# Remove SSL monitoring setup
remove_setup() {
    log "Removing SSL certificate monitoring setup..."
    
    # Remove cron jobs
    local temp_cron="/tmp/fahaniecares_ssl_cron_remove"
    (crontab -l 2>/dev/null || true) | grep -v "#FahanieCares SSL Monitor" > "$temp_cron" || true
    crontab "$temp_cron" 2>/dev/null || true
    rm -f "$temp_cron"
    
    # Remove systemd timer
    if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl stop fahaniecares-ssl-monitor.timer 2>/dev/null || true
        sudo systemctl disable fahaniecares-ssl-monitor.timer 2>/dev/null || true
        sudo rm -f /etc/systemd/system/fahaniecares-ssl-monitor.* 2>/dev/null || true
        sudo systemctl daemon-reload 2>/dev/null || true
    fi
    
    log "SSL monitoring setup removed"
}

# Main function
main() {
    local action="${1:-setup}"
    
    case "$action" in
        "setup")
            log "=== Setting up #FahanieCares SSL Certificate Monitoring ==="
            
            if ! check_ssl_monitor_script; then
                exit 1
            fi
            
            setup_log_directory
            install_dependencies
            
            # Setup both cron and systemd (systemd as backup)
            setup_cron_jobs
            setup_systemd_timer
            
            # Test the setup
            test_ssl_monitoring
            
            log "=== SSL Certificate Monitoring Setup Complete ==="
            log "Daily monitoring will run at 9:00 AM"
            log "Critical checks will run every 6 hours"
            log "Weekly reports will run on Mondays at 9:00 AM"
            
            if [ -n "$SLACK_WEBHOOK" ]; then
                log "Slack notifications are configured"
            else
                log "WARNING: No Slack webhook configured. Set SLACK_WEBHOOK environment variable for notifications"
            fi
            ;;
            
        "test")
            log "=== Testing SSL Certificate Monitoring ==="
            test_ssl_monitoring
            ;;
            
        "status")
            show_status
            ;;
            
        "remove")
            remove_setup
            ;;
            
        *)
            echo "Usage: $0 {setup|test|status|remove}"
            echo ""
            echo "Commands:"
            echo "  setup   - Install and configure SSL certificate monitoring"
            echo "  test    - Test SSL monitoring functionality"
            echo "  status  - Show current monitoring status"
            echo "  remove  - Remove SSL monitoring setup"
            echo ""
            echo "Environment variables:"
            echo "  SLACK_WEBHOOK - Slack webhook URL for notifications"
            echo "  CRON_USER     - User to run cron jobs (default: current user)"
            echo ""
            echo "Examples:"
            echo "  SLACK_WEBHOOK='https://hooks.slack.com/...' $0 setup"
            echo "  $0 test"
            echo "  $0 status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"