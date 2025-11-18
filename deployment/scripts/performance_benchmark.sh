#!/bin/bash

# #FahanieCares Platform - Performance Benchmarking Script
# Comprehensive performance testing and benchmarking

set -euo pipefail

# Configuration
TARGET_HOST="${TARGET_HOST:-http://localhost:3000}"
RESULTS_DIR="${RESULTS_DIR:-/tmp/fahaniecares_performance}"
TEST_DURATION="${TEST_DURATION:-300}"  # 5 minutes default
CONCURRENT_USERS="${CONCURRENT_USERS:-50}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RESULTS_DIR/benchmark.log"
}

# Send notification function
send_notification() {
    local message="$1"
    local status="$2"
    
    log "$message"
    
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"⚡ #FahanieCares Performance Test $status: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking performance testing dependencies..."
    
    local missing_deps=()
    
    # Check for curl
    if ! command -v curl >/dev/null 2>&1; then
        missing_deps+=("curl")
    fi
    
    # Check for ab (Apache Bench)
    if ! command -v ab >/dev/null 2>&1; then
        log "Installing Apache Bench (ab)..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y apache2-utils
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y httpd-tools
        elif command -v brew >/dev/null 2>&1; then
            brew install httpd
        else
            missing_deps+=("ab (Apache Bench)")
        fi
    fi
    
    # Check for Python and locust
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    elif ! python3 -c "import locust" 2>/dev/null; then
        log "Installing locust for load testing..."
        pip3 install locust requests 2>/dev/null || missing_deps+=("locust")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "ERROR: Missing dependencies: ${missing_deps[*]}"
        log "Please install missing dependencies and try again"
        return 1
    fi
    
    log "All dependencies available"
    return 0
}

# Basic connectivity test
test_connectivity() {
    log "Testing basic connectivity to $TARGET_HOST"
    
    if curl -f -s -I "$TARGET_HOST" >/dev/null; then
        log "✓ Target host is reachable"
        return 0
    else
        log "✗ Target host is not reachable"
        return 1
    fi
}

# Apache Bench tests
run_apache_bench_tests() {
    log "Running Apache Bench (ab) tests..."
    
    local endpoints=(
        "/"
        "/about-chapters/"
        "/programs/"
        "/contact/"
        "/health/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="$TARGET_HOST$endpoint"
        local output_file="$RESULTS_DIR/ab_${endpoint//\//_}.txt"
        
        log "Testing endpoint: $endpoint"
        
        # Run ab test: 1000 requests, 10 concurrent
        if ab -n 1000 -c 10 -k -H "Accept-Encoding: gzip,deflate" "$url" > "$output_file" 2>&1; then
            # Extract key metrics
            local requests_per_sec=$(grep "Requests per second" "$output_file" | awk '{print $4}')
            local time_per_request=$(grep "Time per request.*mean" "$output_file" | head -1 | awk '{print $4}')
            local failed_requests=$(grep "Failed requests" "$output_file" | awk '{print $3}')
            
            log "  ✓ $endpoint - RPS: $requests_per_sec, Time: ${time_per_request}ms, Failures: $failed_requests"
        else
            log "  ✗ $endpoint - Test failed"
        fi
    done
}

# Response time analysis
analyze_response_times() {
    log "Analyzing response times for critical endpoints..."
    
    local endpoints=(
        "/"
        "/about-chapters/"
        "/programs/"
        "/health/"
        "/ready/"
    )
    
    local total_time=0
    local test_count=0
    
    for endpoint in "${endpoints[@]}"; do
        local url="$TARGET_HOST$endpoint"
        
        log "Measuring response time for: $endpoint"
        
        # Measure response time with curl
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url" 2>/dev/null || echo "0")
        local response_time_ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "0")
        
        log "  Response time: ${response_time_ms}ms"
        
        # Accumulate for average
        total_time=$(echo "$total_time + $response_time" | bc 2>/dev/null || echo "$total_time")
        ((test_count++))
        
        # Record in results file
        echo "$endpoint,$response_time_ms" >> "$RESULTS_DIR/response_times.csv"
    done
    
    # Calculate average response time
    if [ "$test_count" -gt 0 ]; then
        local avg_time=$(echo "scale=3; $total_time / $test_count" | bc 2>/dev/null || echo "0")
        local avg_time_ms=$(echo "$avg_time * 1000" | bc 2>/dev/null || echo "0")
        log "Average response time: ${avg_time_ms}ms"
        
        echo "AVERAGE,$avg_time_ms" >> "$RESULTS_DIR/response_times.csv"
    fi
}

# Memory and CPU usage simulation
run_resource_monitoring() {
    log "Starting resource monitoring during load test..."
    
    local monitor_file="$RESULTS_DIR/resource_usage.log"
    
    # Start monitoring in background
    (
        while true; do
            local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            local cpu_usage="N/A"
            local memory_usage="N/A"
            
            # Get system resource usage (if available)
            if command -v top >/dev/null 2>&1; then
                cpu_usage=$(top -l 1 -s 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' 2>/dev/null || echo "N/A")
            fi
            
            if command -v free >/dev/null 2>&1; then
                memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}' 2>/dev/null || echo "N/A")
            elif command -v vm_stat >/dev/null 2>&1; then
                # macOS memory calculation
                memory_usage=$(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//' 2>/dev/null || echo "N/A")
            fi
            
            echo "$timestamp,CPU:${cpu_usage}%,Memory:${memory_usage}%" >> "$monitor_file"
            sleep 5
        done
    ) &
    
    local monitor_pid=$!
    echo "$monitor_pid" > "$RESULTS_DIR/monitor.pid"
    
    log "Resource monitoring started (PID: $monitor_pid)"
}

# Stop resource monitoring
stop_resource_monitoring() {
    if [ -f "$RESULTS_DIR/monitor.pid" ]; then
        local monitor_pid=$(cat "$RESULTS_DIR/monitor.pid")
        if kill "$monitor_pid" 2>/dev/null; then
            log "Resource monitoring stopped"
        fi
        rm -f "$RESULTS_DIR/monitor.pid"
    fi
}

# Run locust load test
run_locust_load_test() {
    log "Running Locust load test..."
    
    local script_dir="$(dirname "$0")"
    local load_test_script="$script_dir/load_test.py"
    
    if [ ! -f "$load_test_script" ]; then
        log "WARNING: load_test.py not found, skipping advanced load test"
        return 0
    fi
    
    # Run mixed scenario load test
    python3 "$load_test_script" \
        --host "$TARGET_HOST" \
        --users "$CONCURRENT_USERS" \
        --spawn-rate 5 \
        --time "${TEST_DURATION}s" \
        --scenario mixed > "$RESULTS_DIR/locust_output.txt" 2>&1 || true
    
    log "Locust load test completed"
}

# Database performance test
test_database_performance() {
    log "Testing database performance endpoints..."
    
    local db_endpoints=(
        "/health/detailed/"
        "/metrics/"
    )
    
    for endpoint in "${db_endpoints[@]}"; do
        local url="$TARGET_HOST$endpoint"
        
        log "Testing database endpoint: $endpoint"
        
        # Test with multiple concurrent requests
        for i in {1..5}; do
            curl -s -o /dev/null -w "Request $i: %{time_total}s\n" "$url" >> "$RESULTS_DIR/db_performance.log" 2>&1 &
        done
        
        # Wait for all background requests to complete
        wait
    done
}

# Generate performance report
generate_performance_report() {
    log "Generating performance report..."
    
    local report_file="$RESULTS_DIR/performance_report.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create JSON report
    cat > "$report_file" << EOF
{
    "test_info": {
        "timestamp": "$timestamp",
        "target_host": "$TARGET_HOST",
        "test_duration": "$TEST_DURATION",
        "concurrent_users": "$CONCURRENT_USERS"
    },
    "summary": {
        "total_tests_run": 0,
        "avg_response_time_ms": 0,
        "max_response_time_ms": 0,
        "min_response_time_ms": 0,
        "error_rate": 0
    },
    "test_files": {
        "apache_bench": "ab_*.txt",
        "response_times": "response_times.csv",
        "resource_usage": "resource_usage.log",
        "locust_output": "locust_output.txt",
        "database_performance": "db_performance.log"
    }
}
EOF

    # Calculate summary statistics if response times file exists
    if [ -f "$RESULTS_DIR/response_times.csv" ]; then
        local avg_response=$(tail -1 "$RESULTS_DIR/response_times.csv" | cut -d',' -f2 | sed 's/AVERAGE,//')
        
        # Update summary in JSON (simplified)
        log "Average response time: ${avg_response}ms"
    fi
    
    log "Performance report generated: $report_file"
}

# Health check validation
validate_health_endpoints() {
    log "Validating health check endpoints..."
    
    local health_endpoints=(
        "/health/"
        "/ready/"
        "/metrics/"
    )
    
    local failed_count=0
    
    for endpoint in "${health_endpoints[@]}"; do
        local url="$TARGET_HOST$endpoint"
        
        if curl -f -s "$url" >/dev/null; then
            log "✓ $endpoint - OK"
        else
            log "✗ $endpoint - FAILED"
            ((failed_count++))
        fi
    done
    
    if [ "$failed_count" -eq 0 ]; then
        log "All health endpoints are responding correctly"
        return 0
    else
        log "WARNING: $failed_count health endpoints failed"
        return 1
    fi
}

# Main benchmark function
main() {
    log "=== Starting #FahanieCares Performance Benchmark ==="
    
    # Check dependencies
    if ! check_dependencies; then
        send_notification "Performance test failed - missing dependencies" "FAILED"
        exit 1
    fi
    
    # Test connectivity
    if ! test_connectivity; then
        send_notification "Performance test failed - target unreachable" "FAILED"
        exit 1
    fi
    
    # Start resource monitoring
    run_resource_monitoring
    
    # Run tests
    log "Running performance tests..."
    
    validate_health_endpoints
    analyze_response_times
    run_apache_bench_tests
    test_database_performance
    run_locust_load_test
    
    # Stop monitoring
    stop_resource_monitoring
    
    # Generate report
    generate_performance_report
    
    # Final summary
    local total_time=$SECONDS
    log "=== Performance Benchmark Completed ==="
    log "Total test time: ${total_time}s"
    log "Results saved to: $RESULTS_DIR"
    
    send_notification "Performance benchmark completed successfully in ${total_time}s" "SUCCESS"
}

# Handle script termination
trap 'stop_resource_monitoring; log "Performance test interrupted"; exit 1' INT TERM

# Run main function
main "$@"