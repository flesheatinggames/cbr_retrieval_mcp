# CBR MCP Server - Monitoring and Alerting Setup Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

This comprehensive monitoring and alerting setup guide provides detailed instructions for implementing robust monitoring infrastructure for the CBR MCP Server. It covers system resource monitoring, performance metrics collection, health check automation, alerting configuration, and integration with external monitoring tools including Prometheus, Grafana, ELK Stack, and cloud monitoring services.

## Monitoring Architecture Overview

### Monitoring Components

The CBR MCP Server includes a multi-layered monitoring system:

1. **Built-in Health Dashboard**: Web-based real-time monitoring interface
2. **System Resource Monitor**: CPU, memory, disk, and network monitoring
3. **Application Metrics**: CBR-specific performance and usage metrics
4. **Database Health Monitoring**: ChromaDB integrity and performance tracking
5. **Request Tracing**: Detailed logging and correlation tracking
6. **External Integration**: APIs for third-party monitoring tools

### Monitoring Data Flow

```
CBR MCP Server → Built-in Metrics Collection → Health Dashboard
     ↓                      ↓                        ↓
Internal Logs → Log Aggregation → External Monitoring Tools
     ↓                      ↓                        ↓
Alert System ← Threshold Monitoring ← Performance Analysis
```

## Built-in Monitoring Configuration

### Enabling Comprehensive Monitoring

#### YAML Configuration

```yaml
# monitoring-config.yaml
monitoring:
  enabled: true
  interval: 30.0                    # Monitoring interval in seconds
  db_path: "/opt/cbr/data/monitoring.db"
  retention_hours: 168             # 7 days retention
  alert_cooldown: 300              # 5 minutes between alerts
  max_alerts_per_hour: 100         # Rate limiting for alerts
  
  # Resource monitoring thresholds
  thresholds:
    cpu:
      warning: 60.0                # CPU warning threshold %
      critical: 80.0               # CPU critical threshold %
      emergency: 95.0              # CPU emergency threshold %
    memory:
      warning: 70.0                # Memory warning threshold %
      critical: 85.0               # Memory critical threshold %
      emergency: 95.0              # Memory emergency threshold %
    disk:
      warning: 75.0                # Disk warning threshold %
      critical: 85.0               # Disk critical threshold %
      emergency: 95.0              # Disk emergency threshold %
    
  # Performance thresholds
  performance:
    query_latency:
      warning: 1.0                 # Query latency warning (seconds)
      critical: 3.0                # Query latency critical (seconds)
    error_rate:
      warning: 5.0                 # Error rate warning %
      critical: 15.0               # Error rate critical %
    cache_hit_rate:
      warning: 70.0                # Cache hit rate warning %
      critical: 50.0               # Cache hit rate critical %

# Health Dashboard Configuration
dashboard:
  host: "0.0.0.0"
  port: 8080
  debug: false
  websocket_enabled: true
  metrics_update_interval: 5       # Dashboard update interval
  security_headers: true
  max_websocket_connections: 100
  
# Enhanced Logging for Monitoring
logging:
  level: "INFO"
  format: "json"                   # JSON format for log aggregation
  performance_logging: true        # Enable performance metrics logging
  request_correlation: true        # Enable request correlation IDs
  output_file: "/var/log/cbr/server.log"
  max_file_size: 52428800         # 50MB
  backup_count: 10
  rotation_enabled: true
```

#### Environment Variables

```bash
# Core monitoring settings
export CBR_MONITORING_ENABLED=true
export CBR_MONITORING_INTERVAL=30
export CBR_MONITORING_DB_PATH="/opt/cbr/data/monitoring.db"
export CBR_MONITORING_RETENTION=168

# Dashboard settings
export CBR_DASHBOARD_HOST="0.0.0.0"
export CBR_DASHBOARD_PORT=8080
export CBR_WEBSOCKET_ENABLED=true
export CBR_METRICS_INTERVAL=5

# Alerting thresholds
export CBR_CPU_WARNING=60
export CBR_CPU_CRITICAL=80
export CBR_MEMORY_WARNING=70
export CBR_MEMORY_CRITICAL=85
export CBR_DISK_WARNING=75
export CBR_DISK_CRITICAL=85

# Performance monitoring
export CBR_PERFORMANCE_MONITORING=true
export CBR_LOG_PERFORMANCE=true
export CBR_REQUEST_CORRELATION=true
```

### Starting Monitoring Services

```bash
# Start CBR MCP Server with monitoring enabled
export CBR_CONFIG_FILE="/etc/cbr/monitoring-config.yaml"
systemctl start cbr-mcp-server

# Verify monitoring is active
curl http://localhost:8080/health
curl http://localhost:8080/api/metrics/system
curl http://localhost:8080/api/metrics/application

# Check dashboard accessibility
curl http://localhost:8080/
```

## System Resource Monitoring

### CPU Monitoring Setup

#### Custom CPU Monitoring Script

```bash
#!/bin/bash
# cpu_monitor.sh - Advanced CPU monitoring

THRESHOLD_WARNING=70
THRESHOLD_CRITICAL=85
ALERT_LOG="/var/log/cbr/cpu_alerts.log"
CBR_API_URL="http://localhost:8080/api/metrics/system"

monitor_cpu() {
    local cpu_usage=$(curl -s "$CBR_API_URL" | jq -r '.cpu.percent')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] CPU Usage: ${cpu_usage}%, Load Average: ${load_avg}" >> "$ALERT_LOG"
    
    if (( $(echo "$cpu_usage > $THRESHOLD_CRITICAL" | bc -l) )); then
        echo "[$timestamp] CRITICAL: CPU usage ${cpu_usage}% exceeds critical threshold" >> "$ALERT_LOG"
        # Send alert
        send_alert "CRITICAL" "CPU usage ${cpu_usage}% on $(hostname)"
    elif (( $(echo "$cpu_usage > $THRESHOLD_WARNING" | bc -l) )); then
        echo "[$timestamp] WARNING: CPU usage ${cpu_usage}% exceeds warning threshold" >> "$ALERT_LOG"
        send_alert "WARNING" "CPU usage ${cpu_usage}% on $(hostname)"
    fi
}

send_alert() {
    local severity="$1"
    local message="$2"
    
    # Email alert
    echo "$message" | mail -s "CBR Server Alert [$severity]" admin@company.com
    
    # Webhook alert (Slack, Discord, etc.)
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$message\"}" \
        "$WEBHOOK_URL"
    
    # Log to system log
    logger -t cbr-cpu-monitor "$severity: $message"
}

# Run monitoring
while true; do
    monitor_cpu
    sleep 60
done
```

#### systemd Service for CPU Monitoring

```ini
# /etc/systemd/system/cbr-cpu-monitor.service
[Unit]
Description=CBR MCP Server CPU Monitor
After=network.target cbr-mcp-server.service
Requires=cbr-mcp-server.service

[Service]
Type=simple
User=cbr-server
ExecStart=/opt/cbr/scripts/cpu_monitor.sh
Restart=always
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
```

### Memory Monitoring Setup

#### Memory Leak Detection Script

```python
#!/usr/bin/env python3
# memory_monitor.py - Advanced memory monitoring

import psutil
import requests
import json
import time
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

class MemoryMonitor:
    def __init__(self, config_file='/etc/cbr/memory-monitor.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        logging.basicConfig(
            filename=self.config['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.baseline_memory = None
        self.memory_history = []
        self.alert_sent = False
    
    def get_memory_metrics(self):
        """Get comprehensive memory metrics."""
        # System memory
        system_memory = psutil.virtual_memory()
        
        # CBR server process memory
        try:
            cbr_pid = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'cbr-mcp-server' in ' '.join(proc.info['cmdline'] or []):
                    cbr_pid = proc.info['pid']
                    break
            
            if cbr_pid:
                cbr_process = psutil.Process(cbr_pid)
                cbr_memory = cbr_process.memory_info()
                cbr_memory_percent = cbr_process.memory_percent()
            else:
                cbr_memory = None
                cbr_memory_percent = 0
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            cbr_memory = None
            cbr_memory_percent = 0
        
        # Application metrics from CBR API
        try:
            response = requests.get('http://localhost:8080/api/metrics/application')
            app_metrics = response.json()
            cache_memory = app_metrics.get('cache', {}).get('memory_usage', 0)
        except:
            cache_memory = 0
        
        return {
            'timestamp': datetime.now(),
            'system': {
                'total': system_memory.total,
                'used': system_memory.used,
                'available': system_memory.available,
                'percent': system_memory.percent
            },
            'cbr_process': {
                'rss': cbr_memory.rss if cbr_memory else 0,
                'vms': cbr_memory.vms if cbr_memory else 0,
                'percent': cbr_memory_percent
            },
            'cache_memory': cache_memory
        }
    
    def analyze_memory_trend(self):
        """Analyze memory usage trends for leak detection."""
        if len(self.memory_history) < 10:
            return None
        
        recent_memory = [m['system']['percent'] for m in self.memory_history[-10:]]
        early_memory = [m['system']['percent'] for m in self.memory_history[-20:-10]] if len(self.memory_history) >= 20 else recent_memory
        
        recent_avg = sum(recent_memory) / len(recent_memory)
        early_avg = sum(early_memory) / len(early_memory)
        
        growth_rate = (recent_avg - early_avg) / early_avg * 100 if early_avg > 0 else 0
        
        return {
            'growth_rate': growth_rate,
            'recent_avg': recent_avg,
            'early_avg': early_avg,
            'is_concerning': growth_rate > self.config['thresholds']['memory_growth_rate']
        }
    
    def send_memory_alert(self, metrics, trend_analysis):
        """Send memory usage alert."""
        subject = f"CBR Server Memory Alert - {metrics['system']['percent']:.1f}% usage"
        
        body = f"""
CBR MCP Server Memory Alert

Timestamp: {metrics['timestamp']}
Host: {psutil.uname().node}

System Memory:
- Usage: {metrics['system']['percent']:.1f}%
- Used: {metrics['system']['used'] / 1024**3:.2f} GB
- Available: {metrics['system']['available'] / 1024**3:.2f} GB
- Total: {metrics['system']['total'] / 1024**3:.2f} GB

CBR Process:
- Memory: {metrics['cbr_process']['percent']:.1f}%
- RSS: {metrics['cbr_process']['rss'] / 1024**2:.1f} MB
- VMS: {metrics['cbr_process']['vms'] / 1024**2:.1f} MB

Cache Memory: {metrics['cache_memory'] / 1024**2:.1f} MB

Trend Analysis:
- Growth Rate: {trend_analysis['growth_rate']:.2f}%
- Recent Average: {trend_analysis['recent_avg']:.1f}%
- Is Concerning: {trend_analysis['is_concerning']}

Dashboard: http://localhost:8080
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.config['smtp']['from']
        msg['To'] = ', '.join(self.config['smtp']['to'])
        
        try:
            with smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port']) as server:
                if self.config['smtp'].get('use_tls'):
                    server.starttls()
                if self.config['smtp'].get('username'):
                    server.login(self.config['smtp']['username'], self.config['smtp']['password'])
                server.send_message(msg)
            
            logging.info(f"Memory alert sent: {metrics['system']['percent']:.1f}% usage")
        except Exception as e:
            logging.error(f"Failed to send memory alert: {e}")
    
    def monitor(self):
        """Main monitoring loop."""
        logging.info("Memory monitoring started")
        
        while True:
            try:
                metrics = self.get_memory_metrics()
                self.memory_history.append(metrics)
                
                # Keep only recent history
                if len(self.memory_history) > 100:
                    self.memory_history = self.memory_history[-100:]
                
                # Check thresholds
                memory_percent = metrics['system']['percent']
                
                if memory_percent > self.config['thresholds']['critical']:
                    if not self.alert_sent:
                        trend_analysis = self.analyze_memory_trend()
                        if trend_analysis:
                            self.send_memory_alert(metrics, trend_analysis)
                        self.alert_sent = True
                elif memory_percent < self.config['thresholds']['warning']:
                    self.alert_sent = False
                
                # Log metrics
                logging.info(f"Memory: {memory_percent:.1f}%, CBR Process: {metrics['cbr_process']['percent']:.1f}%")
                
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                logging.error(f"Memory monitoring error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = MemoryMonitor()
    monitor.monitor()
```

#### Memory Monitor Configuration

```json
{
  "check_interval": 60,
  "log_file": "/var/log/cbr/memory_monitor.log",
  "thresholds": {
    "warning": 75.0,
    "critical": 85.0,
    "memory_growth_rate": 5.0
  },
  "smtp": {
    "server": "smtp.company.com",
    "port": 587,
    "use_tls": true,
    "from": "cbr-alerts@company.com",
    "to": ["admin@company.com", "ops@company.com"],
    "username": "cbr-alerts@company.com",
    "password": "secure-smtp-password"
  }
}
```

### Disk Space Monitoring

#### Automated Disk Cleanup Script

```bash
#!/bin/bash
# disk_monitor.sh - Disk space monitoring and cleanup

DISK_THRESHOLD_WARNING=80
DISK_THRESHOLD_CRITICAL=90
CBR_DATA_PATH="/opt/cbr/data"
CBR_LOGS_PATH="/var/log/cbr"
ALERT_LOG="/var/log/cbr/disk_alerts.log"

check_disk_usage() {
    local path="$1"
    local usage=$(df "$path" | awk 'NR==2{print $5}' | sed 's/%//')
    echo "$usage"
}

cleanup_old_files() {
    local path="$1"
    local days="$2"
    
    echo "[$timestamp] Cleaning up files older than $days days in $path" >> "$ALERT_LOG"
    
    # Backup old files before deletion
    find "$path" -name "*.log.*" -mtime +"$days" -exec gzip {} \; 2>/dev/null
    find "$path" -name "*.log.*.gz" -mtime +30 -delete 2>/dev/null
    
    # Clean temporary files
    find "$path" -name "*.tmp" -mtime +1 -delete 2>/dev/null
    find "$path" -name "core.*" -mtime +7 -delete 2>/dev/null
}

emergency_cleanup() {
    echo "[$timestamp] EMERGENCY: Starting aggressive cleanup" >> "$ALERT_LOG"
    
    # Clean old logs more aggressively
    cleanup_old_files "$CBR_LOGS_PATH" 3
    
    # Clear cache if CBR server supports it
    curl -X POST http://localhost:8080/api/cache/clear 2>/dev/null
    
    # Compress current logs
    find "$CBR_LOGS_PATH" -name "*.log" -size +100M -exec gzip {} \; 2>/dev/null
    
    # Docker cleanup if running in Docker
    if command -v docker &> /dev/null; then
        docker system prune -f 2>/dev/null
    fi
}

monitor_disk() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check main data directory
    local data_usage=$(check_disk_usage "$CBR_DATA_PATH")
    local logs_usage=$(check_disk_usage "$CBR_LOGS_PATH")
    local root_usage=$(check_disk_usage "/")
    
    echo "[$timestamp] Disk Usage - Data: ${data_usage}%, Logs: ${logs_usage}%, Root: ${root_usage}%" >> "$ALERT_LOG"
    
    # Check critical thresholds
    if [ "$root_usage" -gt "$DISK_THRESHOLD_CRITICAL" ] || [ "$data_usage" -gt "$DISK_THRESHOLD_CRITICAL" ]; then
        echo "[$timestamp] CRITICAL: Disk usage critical" >> "$ALERT_LOG"
        emergency_cleanup
        
        # Send critical alert
        echo "CRITICAL: Disk usage critical on $(hostname) - Root: ${root_usage}%, Data: ${data_usage}%" | \
            mail -s "CBR Disk Critical" admin@company.com
            
    elif [ "$root_usage" -gt "$DISK_THRESHOLD_WARNING" ] || [ "$data_usage" -gt "$DISK_THRESHOLD_WARNING" ]; then
        echo "[$timestamp] WARNING: Disk usage high" >> "$ALERT_LOG"
        cleanup_old_files "$CBR_LOGS_PATH" 7
        
        # Send warning alert
        echo "WARNING: Disk usage high on $(hostname) - Root: ${root_usage}%, Data: ${data_usage}%" | \
            mail -s "CBR Disk Warning" admin@company.com
    fi
}

# Main monitoring loop
while true; do
    monitor_disk
    sleep 300  # Check every 5 minutes
done
```

### Network Monitoring

#### Network Performance Monitoring Script

```bash
#!/bin/bash
# network_monitor.sh - Network performance monitoring

LOG_FILE="/var/log/cbr/network_monitor.log"
CBR_PORT=8080
CHECK_INTERVAL=60

monitor_network_performance() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Test CBR server connectivity
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:$CBR_PORT/health)
    local http_code=$(curl -o /dev/null -s -w "%{http_code}" http://localhost:$CBR_PORT/health)
    
    # Network interface statistics
    local interface=$(ip route | grep default | awk '{print $5}' | head -1)
    local rx_bytes=$(cat /sys/class/net/$interface/statistics/rx_bytes)
    local tx_bytes=$(cat /sys/class/net/$interface/statistics/tx_bytes)
    local rx_errors=$(cat /sys/class/net/$interface/statistics/rx_errors)
    local tx_errors=$(cat /sys/class/net/$interface/statistics/tx_errors)
    
    # Connection count
    local connections=$(netstat -an | grep :$CBR_PORT | wc -l)
    local established=$(netstat -an | grep :$CBR_PORT | grep ESTABLISHED | wc -l)
    
    echo "[$timestamp] HTTP: ${http_code}, Response: ${response_time}s, Connections: $established/$connections" >> "$LOG_FILE"
    echo "[$timestamp] Interface $interface - RX: $rx_bytes bytes, TX: $tx_bytes bytes, Errors: RX:$rx_errors TX:$tx_errors" >> "$LOG_FILE"
    
    # Alert on issues
    if [ "$http_code" != "200" ]; then
        echo "[$timestamp] ALERT: HTTP health check failed - Code: $http_code" >> "$LOG_FILE"
        echo "CBR Server health check failed on $(hostname) - HTTP $http_code" | \
            mail -s "CBR Network Alert" admin@company.com
    fi
    
    # Check response time threshold
    if (( $(echo "$response_time > 5.0" | bc -l) )); then
        echo "[$timestamp] ALERT: High response time - ${response_time}s" >> "$LOG_FILE"
        echo "CBR Server high response time on $(hostname) - ${response_time}s" | \
            mail -s "CBR Performance Alert" admin@company.com
    fi
}

# Network connectivity test
test_external_connectivity() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Test external dependencies
    if ! curl -s --max-time 10 https://huggingface.co > /dev/null; then
        echo "[$timestamp] WARNING: Cannot reach Hugging Face Hub" >> "$LOG_FILE"
    fi
    
    # Test DNS resolution
    if ! nslookup huggingface.co > /dev/null 2>&1; then
        echo "[$timestamp] WARNING: DNS resolution issues" >> "$LOG_FILE"
    fi
}

# Main monitoring
while true; do
    monitor_network_performance
    test_external_connectivity
    sleep $CHECK_INTERVAL
done
```

## Health Check Automation

### Comprehensive Health Check Script

```python
#!/usr/bin/env python3
# health_checker.py - Comprehensive health monitoring

import requests
import json
import time
import logging
import subprocess
import psutil
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class HealthChecker:
    def __init__(self, config_file='/etc/cbr/health-check.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        logging.basicConfig(
            filename=self.config['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.base_url = f"http://localhost:{self.config['cbr_port']}"
        self.last_alert_time = {}
    
    def check_service_status(self):
        """Check if CBR service is running."""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'cbr-mcp-server'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False
    
    def check_port_listening(self):
        """Check if CBR port is listening."""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == self.config['cbr_port'] and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def check_health_endpoint(self):
        """Check CBR health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                return {
                    'status': True,
                    'data': health_data,
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': False,
                    'error': f"HTTP {response.status_code}",
                    'response_time': response.elapsed.total_seconds()
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'error': str(e),
                'response_time': None
            }
    
    def check_api_functionality(self):
        """Test CBR API functionality."""
        tests = []
        
        # Test system metrics
        try:
            response = requests.get(f"{self.base_url}/api/metrics/system", timeout=10)
            tests.append({
                'name': 'system_metrics',
                'status': response.status_code == 200,
                'response_time': response.elapsed.total_seconds()
            })
        except Exception as e:
            tests.append({
                'name': 'system_metrics',
                'status': False,
                'error': str(e)
            })
        
        # Test application metrics
        try:
            response = requests.get(f"{self.base_url}/api/metrics/application", timeout=10)
            tests.append({
                'name': 'application_metrics',
                'status': response.status_code == 200,
                'response_time': response.elapsed.total_seconds()
            })
        except Exception as e:
            tests.append({
                'name': 'application_metrics',
                'status': False,
                'error': str(e)
            })
        
        # Test WebSocket endpoint
        try:
            response = requests.get(f"{self.base_url}/ws/metrics", timeout=5)
            # WebSocket upgrade expected to fail with HTTP client, but endpoint should exist
            tests.append({
                'name': 'websocket_endpoint',
                'status': response.status_code in [400, 426],  # Bad Request or Upgrade Required
                'response_time': response.elapsed.total_seconds()
            })
        except Exception as e:
            tests.append({
                'name': 'websocket_endpoint',
                'status': False,
                'error': str(e)
            })
        
        return tests
    
    def check_database_health(self):
        """Check database connectivity and integrity."""
        try:
            # This would need to be implemented in the CBR server API
            response = requests.get(f"{self.base_url}/api/database/health", timeout=15)
            if response.status_code == 200:
                db_health = response.json()
                return {
                    'status': True,
                    'data': db_health
                }
            else:
                return {
                    'status': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def check_resource_usage(self):
        """Check system resource usage."""
        try:
            response = requests.get(f"{self.base_url}/api/metrics/system", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                
                alerts = []
                if metrics['cpu']['percent'] > self.config['thresholds']['cpu_critical']:
                    alerts.append(f"CPU usage critical: {metrics['cpu']['percent']:.1f}%")
                if metrics['memory']['percent'] > self.config['thresholds']['memory_critical']:
                    alerts.append(f"Memory usage critical: {metrics['memory']['percent']:.1f}%")
                if metrics['disk']['percent'] > self.config['thresholds']['disk_critical']:
                    alerts.append(f"Disk usage critical: {metrics['disk']['percent']:.1f}%")
                
                return {
                    'status': True,
                    'metrics': metrics,
                    'alerts': alerts
                }
            else:
                return {
                    'status': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def send_alert(self, subject, body, severity='INFO'):
        """Send alert email."""
        alert_key = f"{severity}_{subject}"
        current_time = datetime.now()
        
        # Check alert cooldown
        if alert_key in self.last_alert_time:
            time_diff = current_time - self.last_alert_time[alert_key]
            if time_diff.total_seconds() < self.config['alert_cooldown']:
                return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp']['from']
            msg['To'] = ', '.join(self.config['smtp']['to'])
            msg['Subject'] = f"[{severity}] CBR Health Check - {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port']) as server:
                if self.config['smtp'].get('use_tls'):
                    server.starttls()
                if self.config['smtp'].get('username'):
                    server.login(self.config['smtp']['username'], self.config['smtp']['password'])
                server.send_message(msg)
            
            self.last_alert_time[alert_key] = current_time
            logging.info(f"Alert sent: {subject}")
            
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
    
    def run_health_check(self):
        """Run comprehensive health check."""
        timestamp = datetime.now()
        results = {
            'timestamp': timestamp.isoformat(),
            'checks': {}
        }
        
        # Service status check
        results['checks']['service'] = {
            'running': self.check_service_status(),
            'port_listening': self.check_port_listening()
        }
        
        # Health endpoint check
        results['checks']['health'] = self.check_health_endpoint()
        
        # API functionality tests
        results['checks']['api_tests'] = self.check_api_functionality()
        
        # Database health
        results['checks']['database'] = self.check_database_health()
        
        # Resource usage
        results['checks']['resources'] = self.check_resource_usage()
        
        # Overall status
        overall_healthy = all([
            results['checks']['service']['running'],
            results['checks']['service']['port_listening'],
            results['checks']['health']['status'],
            all(test['status'] for test in results['checks']['api_tests']),
            results['checks']['database']['status'],
            results['checks']['resources']['status']
        ])
        
        results['overall_status'] = 'HEALTHY' if overall_healthy else 'UNHEALTHY'
        
        # Log results
        logging.info(f"Health check completed: {results['overall_status']}")
        
        # Send alerts if needed
        if not overall_healthy:
            self.process_health_alerts(results)
        
        return results
    
    def process_health_alerts(self, results):
        """Process and send health alerts."""
        alerts = []
        
        if not results['checks']['service']['running']:
            alerts.append("CBR service is not running")
        
        if not results['checks']['service']['port_listening']:
            alerts.append("CBR port is not listening")
        
        if not results['checks']['health']['status']:
            alerts.append(f"Health endpoint failed: {results['checks']['health'].get('error', 'Unknown')}")
        
        for test in results['checks']['api_tests']:
            if not test['status']:
                alerts.append(f"API test '{test['name']}' failed: {test.get('error', 'Unknown')}")
        
        if not results['checks']['database']['status']:
            alerts.append(f"Database health check failed: {results['checks']['database'].get('error', 'Unknown')}")
        
        if results['checks']['resources']['status'] and results['checks']['resources'].get('alerts'):
            alerts.extend(results['checks']['resources']['alerts'])
        
        if alerts:
            alert_body = f"""
CBR MCP Server Health Check Failed

Timestamp: {results['timestamp']}
Host: {psutil.uname().node}

Issues detected:
"""
            for alert in alerts:
                alert_body += f"- {alert}\n"
            
            alert_body += f"""
Dashboard: {self.base_url}

Full health check results:
{json.dumps(results, indent=2)}
"""
            
            self.send_alert("Health Check Failed", alert_body, "CRITICAL")
    
    def monitor(self):
        """Main monitoring loop."""
        logging.info("Health monitoring started")
        
        while True:
            try:
                results = self.run_health_check()
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                logging.error(f"Health check error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    checker = HealthChecker()
    checker.monitor()
```

#### Health Check Configuration

```json
{
  "cbr_port": 8080,
  "check_interval": 300,
  "alert_cooldown": 1800,
  "log_file": "/var/log/cbr/health_check.log",
  "thresholds": {
    "cpu_critical": 85.0,
    "memory_critical": 90.0,
    "disk_critical": 90.0,
    "response_time_warning": 2.0,
    "response_time_critical": 5.0
  },
  "smtp": {
    "server": "smtp.company.com",
    "port": 587,
    "use_tls": true,
    "from": "cbr-health@company.com",
    "to": ["admin@company.com", "oncall@company.com"],
    "username": "cbr-health@company.com",
    "password": "secure-smtp-password"
  }
}
```

## External Monitoring Tool Integration

### Prometheus Integration

#### Prometheus Metrics Exporter

```python
#!/usr/bin/env python3
# prometheus_exporter.py - Prometheus metrics exporter for CBR

import time
import requests
import logging
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Info
import json

# Define Prometheus metrics
cbr_up = Gauge('cbr_up', 'CBR server availability')
cbr_cpu_usage = Gauge('cbr_cpu_usage_percent', 'CPU usage percentage')
cbr_memory_usage = Gauge('cbr_memory_usage_percent', 'Memory usage percentage')
cbr_disk_usage = Gauge('cbr_disk_usage_percent', 'Disk usage percentage')

cbr_requests_total = Counter('cbr_requests_total', 'Total requests processed')
cbr_requests_errors = Counter('cbr_requests_errors_total', 'Total request errors')
cbr_cache_hits = Counter('cbr_cache_hits_total', 'Total cache hits')
cbr_cache_misses = Counter('cbr_cache_misses_total', 'Total cache misses')

cbr_query_latency = Histogram('cbr_query_latency_seconds', 'Query latency distribution')
cbr_database_latency = Histogram('cbr_database_latency_seconds', 'Database query latency')

cbr_info = Info('cbr_server_info', 'CBR server information')

class CBRPrometheusExporter:
    def __init__(self, cbr_url="http://localhost:8080", scrape_interval=30):
        self.cbr_url = cbr_url
        self.scrape_interval = scrape_interval
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def collect_metrics(self):
        """Collect metrics from CBR server."""
        try:
            # Health check
            health_response = requests.get(f"{self.cbr_url}/health", timeout=10)
            cbr_up.set(1 if health_response.status_code == 200 else 0)
            
            if health_response.status_code != 200:
                return
            
            # System metrics
            system_response = requests.get(f"{self.cbr_url}/api/metrics/system", timeout=10)
            if system_response.status_code == 200:
                system_data = system_response.json()
                cbr_cpu_usage.set(system_data['cpu']['percent'])
                cbr_memory_usage.set(system_data['memory']['percent'])
                cbr_disk_usage.set(system_data['disk']['percent'])
            
            # Application metrics
            app_response = requests.get(f"{self.cbr_url}/api/metrics/application", timeout=10)
            if app_response.status_code == 200:
                app_data = app_response.json()
                
                # Set counters to current values (Prometheus will calculate rates)
                cbr_requests_total._value._value = app_data['requests']['total']
                cbr_requests_errors._value._value = app_data['requests']['error']
                cbr_cache_hits._value._value = app_data['cache']['hits']
                cbr_cache_misses._value._value = app_data['cache']['misses']
            
            # Query statistics
            query_response = requests.get(f"{self.cbr_url}/api/stats/queries", timeout=10)
            if query_response.status_code == 200:
                query_data = query_response.json()
                
                # Update latency histogram with current average
                # (In production, individual request timings would be better)
                avg_latency = query_data['performance']['avg_response_time']
                cbr_query_latency.observe(avg_latency)
            
            # Server info (static information)
            cbr_info.info({
                'version': '1.0.0',
                'host': requests.get(f"{self.cbr_url}/health").json().get('host', 'unknown')
            })
            
            self.logger.info("Metrics collected successfully")
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            cbr_up.set(0)
    
    def run(self):
        """Start the Prometheus exporter."""
        # Start Prometheus metrics server
        start_http_server(8000)
        self.logger.info("Prometheus exporter started on port 8000")
        
        while True:
            self.collect_metrics()
            time.sleep(self.scrape_interval)

if __name__ == "__main__":
    exporter = CBRPrometheusExporter()
    exporter.run()
```

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

rule_files:
  - "cbr_alerts.yml"

scrape_configs:
  - job_name: 'cbr-mcp-server'
    static_configs:
      - targets: ['localhost:8000']  # Prometheus exporter
    scrape_interval: 30s
    metrics_path: '/metrics'
    
  - job_name: 'cbr-dashboard'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 60s
    metrics_path: '/metrics'  # If CBR server exposes Prometheus metrics directly

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Prometheus Alert Rules

```yaml
# cbr_alerts.yml
groups:
  - name: cbr-alerts
    rules:
      - alert: CBRServerDown
        expr: cbr_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "CBR MCP Server is down"
          description: "CBR MCP Server has been down for more than 1 minute"
      
      - alert: CBRHighCPUUsage
        expr: cbr_cpu_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CBR server high CPU usage"
          description: "CBR server CPU usage is {{ $value }}% for more than 5 minutes"
      
      - alert: CBRHighMemoryUsage
        expr: cbr_memory_usage_percent > 90
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CBR server high memory usage"
          description: "CBR server memory usage is {{ $value }}% for more than 2 minutes"
      
      - alert: CBRHighErrorRate
        expr: rate(cbr_requests_errors_total[5m]) / rate(cbr_requests_total[5m]) > 0.10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "CBR server high error rate"
          description: "CBR server error rate is {{ $value | humanizePercentage }} for more than 2 minutes"
      
      - alert: CBRSlowQueries
        expr: cbr_query_latency_seconds > 3.0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "CBR server slow queries"
          description: "CBR server query latency is {{ $value }}s for more than 1 minute"
      
      - alert: CBRLowCacheHitRate
        expr: rate(cbr_cache_hits_total[10m]) / (rate(cbr_cache_hits_total[10m]) + rate(cbr_cache_misses_total[10m])) < 0.70
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CBR server low cache hit rate"
          description: "CBR server cache hit rate is {{ $value | humanizePercentage }} for more than 5 minutes"
```

### Grafana Dashboard Configuration

#### Grafana Dashboard JSON

```json
{
  "dashboard": {
    "id": null,
    "title": "CBR MCP Server Monitoring",
    "tags": ["cbr", "mcp", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Server Status",
        "type": "stat",
        "targets": [
          {
            "expr": "cbr_up",
            "legendFormat": "Server Status"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {
                "options": {
                  "0": {"text": "DOWN", "color": "red"},
                  "1": {"text": "UP", "color": "green"}
                },
                "type": "value"
              }
            ]
          }
        }
      },
      {
        "id": 2,
        "title": "System Resources",
        "type": "timeseries",
        "targets": [
          {
            "expr": "cbr_cpu_usage_percent",
            "legendFormat": "CPU %"
          },
          {
            "expr": "cbr_memory_usage_percent",
            "legendFormat": "Memory %"
          },
          {
            "expr": "cbr_disk_usage_percent",
            "legendFormat": "Disk %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "max": 100,
            "unit": "percent"
          }
        }
      },
      {
        "id": 3,
        "title": "Request Rate",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(cbr_requests_total[5m])",
            "legendFormat": "Requests/sec"
          },
          {
            "expr": "rate(cbr_requests_errors_total[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "Query Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "cbr_query_latency_seconds",
            "legendFormat": "Query Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s"
          }
        }
      },
      {
        "id": 5,
        "title": "Cache Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(cbr_cache_hits_total[5m])",
            "legendFormat": "Cache Hits/sec"
          },
          {
            "expr": "rate(cbr_cache_misses_total[5m])",
            "legendFormat": "Cache Misses/sec"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### ELK Stack Integration

#### Filebeat Configuration

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/cbr/*.log
  fields:
    service: cbr-mcp-server
    environment: production
  fields_under_root: true
  multiline.pattern: '^\d{4}-\d{2}-\d{2}'
  multiline.negate: true
  multiline.match: after

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "cbr-logs-%{+yyyy.MM.dd}"

setup.ilm.enabled: false
setup.template.name: "cbr-logs"
setup.template.pattern: "cbr-logs-*"

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
```

#### Logstash Configuration

```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [service] == "cbr-mcp-server" {
    # Parse JSON logs
    if [message] =~ /^{.*}$/ {
      json {
        source => "message"
      }
    }
    
    # Parse timestamp
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    # Extract performance metrics
    if [performance] {
      mutate {
        add_field => { 
          "performance_operation" => "%{[performance][operation]}"
          "performance_duration" => "%{[performance][duration]}"
        }
      }
    }
    
    # Classify log levels
    if [level] == "ERROR" or [level] == "CRITICAL" {
      mutate {
        add_tag => [ "error" ]
      }
    }
    
    if [level] == "WARNING" {
      mutate {
        add_tag => [ "warning" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "cbr-logs-%{+YYYY.MM.dd}"
  }
  
  # Send errors to alerts
  if "error" in [tags] {
    http {
      url => "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
      http_method => "post"
      format => "json"
      content_type => "application/json"
      mapping => {
        "text" => "CBR Error: %{message}"
        "channel" => "#alerts"
        "username" => "CBR Monitor"
      }
    }
  }
}
```

### Cloud Monitoring Integration

#### AWS CloudWatch Integration

```python
#!/usr/bin/env python3
# cloudwatch_metrics.py - AWS CloudWatch metrics publisher

import boto3
import requests
import time
import logging
from datetime import datetime

class CloudWatchPublisher:
    def __init__(self, region='us-east-1'):
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.cbr_url = "http://localhost:8080"
        self.namespace = 'CBR/MCPServer'
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def publish_metrics(self):
        """Publish CBR metrics to CloudWatch."""
        try:
            # Get metrics from CBR server
            system_response = requests.get(f"{self.cbr_url}/api/metrics/system", timeout=10)
            app_response = requests.get(f"{self.cbr_url}/api/metrics/application", timeout=10)
            
            if system_response.status_code != 200 or app_response.status_code != 200:
                return
            
            system_data = system_response.json()
            app_data = app_response.json()
            
            # Prepare metrics data
            metric_data = [
                {
                    'MetricName': 'CPUUtilization',
                    'Value': system_data['cpu']['percent'],
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'MemoryUtilization', 
                    'Value': system_data['memory']['percent'],
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'DiskUtilization',
                    'Value': system_data['disk']['percent'], 
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'RequestCount',
                    'Value': app_data['requests']['total'],
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'ErrorCount',
                    'Value': app_data['requests']['error'],
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'CacheHitRate',
                    'Value': app_data['cache']['hit_rate'] * 100,
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'DatabaseLatency',
                    'Value': app_data['database']['avg_latency'] * 1000,  # Convert to ms
                    'Unit': 'Milliseconds'
                }
            ]
            
            # Add dimensions
            for metric in metric_data:
                metric['Dimensions'] = [
                    {
                        'Name': 'InstanceId',
                        'Value': boto3.Session().region_name + '-cbr-server'
                    },
                    {
                        'Name': 'Service',
                        'Value': 'CBRMCPServer'
                    }
                ]
            
            # Publish to CloudWatch
            response = self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=metric_data
            )
            
            self.logger.info(f"Published {len(metric_data)} metrics to CloudWatch")
            
        except Exception as e:
            self.logger.error(f"Error publishing to CloudWatch: {e}")
    
    def run(self):
        """Main loop."""
        while True:
            self.publish_metrics()
            time.sleep(60)  # Publish every minute

if __name__ == "__main__":
    publisher = CloudWatchPublisher()
    publisher.run()
```

#### AWS CloudWatch Alarms

```python
#!/usr/bin/env python3
# create_cloudwatch_alarms.py - Create CloudWatch alarms for CBR

import boto3

def create_cbr_alarms():
    cloudwatch = boto3.client('cloudwatch')
    
    alarms = [
        {
            'AlarmName': 'CBR-High-CPU-Usage',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 2,
            'MetricName': 'CPUUtilization',
            'Namespace': 'CBR/MCPServer',
            'Period': 300,
            'Statistic': 'Average',
            'Threshold': 80.0,
            'ActionsEnabled': True,
            'AlarmActions': [
                'arn:aws:sns:us-east-1:123456789012:cbr-alerts'
            ],
            'AlarmDescription': 'CBR server high CPU usage',
        },
        {
            'AlarmName': 'CBR-High-Memory-Usage',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 2,
            'MetricName': 'MemoryUtilization',
            'Namespace': 'CBR/MCPServer',
            'Period': 300,
            'Statistic': 'Average',
            'Threshold': 85.0,
            'ActionsEnabled': True,
            'AlarmActions': [
                'arn:aws:sns:us-east-1:123456789012:cbr-alerts'
            ],
            'AlarmDescription': 'CBR server high memory usage',
        },
        {
            'AlarmName': 'CBR-High-Error-Rate',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 1,
            'MetricName': 'ErrorCount',
            'Namespace': 'CBR/MCPServer',
            'Period': 300,
            'Statistic': 'Sum',
            'Threshold': 10.0,
            'ActionsEnabled': True,
            'AlarmActions': [
                'arn:aws:sns:us-east-1:123456789012:cbr-critical'
            ],
            'AlarmDescription': 'CBR server high error rate',
        }
    ]
    
    for alarm in alarms:
        response = cloudwatch.put_metric_alarm(**alarm)
        print(f"Created alarm: {alarm['AlarmName']}")

if __name__ == "__main__":
    create_cbr_alarms()
```

This comprehensive monitoring and alerting setup guide provides everything needed to implement robust monitoring infrastructure for the CBR MCP Server, including built-in monitoring, system resource monitoring, health checks, and integration with external monitoring platforms.