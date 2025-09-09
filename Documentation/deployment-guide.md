# CBR MCP Server - Deployment Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

This comprehensive deployment guide provides production-ready deployment strategies for the CBR MCP Server. It covers environment preparation, installation procedures, security hardening, scaling strategies, and maintenance procedures for various deployment scenarios including local production, containerized environments, and cloud deployments.

## Prerequisites and System Requirements

### Minimum System Requirements

**Hardware Requirements:**
- **CPU**: 2+ cores (4+ recommended for production)
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 10GB available space (50GB+ for production with logging)
- **Network**: Stable internet connection for model downloads

**Operating System Support:**
- Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- macOS 10.15+
- Windows 10+ (with WSL2 for production)
- Docker-compatible environments

**Software Dependencies:**
- Python 3.8+ (3.10+ recommended)
- pip package manager
- Git (for source deployment)
- systemd (for service management on Linux)
- nginx or Apache (optional, for reverse proxy)

### Recommended Production Specifications

**Production Server:**
- **CPU**: 4-8 cores with AVX2 support
- **Memory**: 16GB RAM (32GB+ for large case bases)
- **Storage**: SSD with 100GB+ available space
- **Network**: 1Gbps+ connection with low latency
- **Monitoring**: Dedicated monitoring/logging infrastructure

## Environment Preparation

### System Update and Package Installation

#### Ubuntu/Debian

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    curl \
    wget \
    sqlite3 \
    systemd \
    nginx \
    htop \
    iotop \
    nethogs

# Install optional monitoring tools
sudo apt install -y \
    prometheus-node-exporter \
    logrotate \
    fail2ban
```

#### CentOS/RHEL/Rocky Linux

```bash
# Update system packages
sudo dnf update -y

# Install EPEL repository
sudo dnf install -y epel-release

# Install system dependencies
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    gcc-c++ \
    git \
    curl \
    wget \
    sqlite \
    systemd \
    nginx \
    htop

# Install optional monitoring tools
sudo dnf install -y \
    node_exporter \
    logrotate
```

#### macOS

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 git curl wget sqlite3 nginx htop

# Install optional monitoring tools
brew install node_exporter
```

### User and Directory Setup

```bash
# Create dedicated service user (Linux)
sudo useradd -r -s /bin/false -d /opt/cbr cbr-server

# Create directory structure
sudo mkdir -p /opt/cbr/{app,data,logs,config,backups}
sudo mkdir -p /var/log/cbr
sudo mkdir -p /etc/cbr

# Set ownership and permissions
sudo chown -R cbr-server:cbr-server /opt/cbr
sudo chown -R cbr-server:cbr-server /var/log/cbr
sudo chown -R cbr-server:cbr-server /etc/cbr

# Set proper permissions
sudo chmod 755 /opt/cbr
sudo chmod 755 /opt/cbr/app
sudo chmod 750 /opt/cbr/data
sudo chmod 750 /opt/cbr/logs
sudo chmod 640 /opt/cbr/config
```

### Python Environment Setup

```bash
# Create Python virtual environment
sudo -u cbr-server python3 -m venv /opt/cbr/app/venv

# Activate virtual environment
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install --upgrade pip setuptools wheel

# Install production dependencies
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install \
    structlog \
    psutil \
    pyyaml \
    uvloop \
    aiofiles \
    prometheus-client
```

## Installation Methods

### Method 1: Source Installation (Recommended)

```bash
# Clone repository
cd /opt/cbr/app
sudo -u cbr-server git clone https://github.com/your-org/cbr_retrieval_mcp.git .

# Install package and dependencies
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install -e ".[dev]"

# Install production dependencies
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install -r requirements-prod.txt

# Verify installation
sudo -u cbr-server /opt/cbr/app/venv/bin/python -c "
from cbr_mcp_server import CBRMCPServer
print('CBR MCP Server installation verified')
"
```

### Method 2: Package Installation

```bash
# Install from PyPI (when available)
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install cbr-mcp-server

# Or install from wheel file
sudo -u cbr-server /opt/cbr/app/venv/bin/pip install cbr_mcp_server-1.0.0-py3-none-any.whl
```

### Method 3: Docker Installation

```bash
# Pull Docker image
docker pull cbr-mcp-server:latest

# Or build from source
git clone https://github.com/your-org/cbr_retrieval_mcp.git
cd cbr_retrieval_mcp
docker build -t cbr-mcp-server:latest .
```

## Configuration for Production

### Production Configuration File

Create `/etc/cbr/production.yaml`:

```yaml
# Production Configuration for CBR MCP Server
# /etc/cbr/production.yaml

# Core Configuration
database:
  path: "/opt/cbr/data/db"
  collection_name: "production_case_base"
  embedding_model: "nomic-ai/nomic-embed-text-v1.5"

# Query Configuration
query:
  max_results_default: 10
  similarity_threshold_default: 0.75

# Production Logging
logging:
  level: "INFO"
  format: "json"
  output_file: "/var/log/cbr/server.log"
  console_output: false
  max_file_size: 52428800  # 50MB
  backup_count: 20
  rotation_enabled: true
  cleanup_enabled: true
  disk_space_monitoring: true
  min_free_space_percent: 15.0
  handle_permissions: true

# System Resource Monitoring
monitoring:
  enabled: true
  interval: 60.0
  db_path: "/opt/cbr/data/monitoring.db"
  retention_hours: 720  # 30 days
  alert_cooldown: 300
  max_alerts_per_hour: 50
  
  thresholds:
    cpu:
      warning: 60.0
      critical: 75.0
      emergency: 90.0
    memory:
      warning: 70.0
      critical: 85.0
      emergency: 95.0
    disk:
      warning: 80.0
      critical: 90.0
      emergency: 95.0

# Health Dashboard
dashboard:
  host: "0.0.0.0"  # Bind to all interfaces
  port: 8080
  debug: false
  security_headers: true
  websocket_enabled: true
  max_websocket_connections: 100
  cors_origins:
    - "https://monitoring.yourcompany.com"
    - "https://admin.yourcompany.com"

# Production Features
production:
  require_auth: true
  api_keys:
    - "${CBR_API_KEY_1}"
    - "${CBR_API_KEY_2}"
  admin_keys:
    - "${CBR_ADMIN_KEY}"
  
  rate_limit_enabled: true
  rate_limit_requests: 500
  rate_limit_window: 3600
  
  cache_enabled: true
  cache_ttl: 1800
  performance_monitoring: true
  
  retry_enabled: true
  max_retries: 5
  circuit_breaker: true
  
  input_validation: "strict"
  sanitization: true
  max_query_length: 5000

# Health Checks
health:
  enabled: true
  timeout: 15
```

### Environment Variables for Production

Create `/etc/cbr/environment`:

```bash
# Production Environment Variables
# /etc/cbr/environment

# Core Configuration
CBR_CONFIG_FILE=/etc/cbr/production.yaml
CBR_DATABASE_PATH=/opt/cbr/data/db
CBR_LOG_FILE=/var/log/cbr/server.log

# Security (load from secure key management)
CBR_API_KEY_1=your-secure-api-key-1
CBR_API_KEY_2=your-secure-api-key-2
CBR_ADMIN_KEY=your-secure-admin-key

# Production Settings
CBR_LOG_LEVEL=INFO
CBR_REQUIRE_AUTH=true
CBR_RATE_LIMIT_ENABLED=true
CBR_CACHE_ENABLED=true
CBR_CIRCUIT_BREAKER=true

# Monitoring
CBR_DASHBOARD_HOST=0.0.0.0
CBR_DASHBOARD_PORT=8080
CBR_METRICS_ENABLED=true
CBR_PERFORMANCE_MONITORING=true

# Process Management
PYTHONUNBUFFERED=1
PYTHONIOENCODING=UTF-8
```

## Service Management

### systemd Service Configuration

Create `/etc/systemd/system/cbr-mcp-server.service`:

```ini
[Unit]
Description=CBR MCP Server - Case-Based Reasoning MCP Service
Documentation=https://github.com/your-org/cbr_retrieval_mcp
After=network.target network-online.target
Wants=network-online.target
Requires=network.target

[Service]
Type=exec
User=cbr-server
Group=cbr-server
WorkingDirectory=/opt/cbr/app
ExecStart=/opt/cbr/app/venv/bin/python -m cbr_mcp_server
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
TimeoutStartSec=60
TimeoutStopSec=30

# Environment
Environment=PYTHONPATH=/opt/cbr/app
EnvironmentFile=/etc/cbr/environment

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/cbr/data /var/log/cbr /tmp
PrivateTmp=true
PrivateDevices=true
ProtectControlGroups=true
ProtectKernelModules=true
ProtectKernelTunables=true
RestrictRealtime=true
RestrictSUIDSGID=true
RemoveIPC=true

# Resource Limits
LimitNOFILE=65536
LimitNPROC=4096
MemoryMax=8G
CPUQuota=400%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cbr-mcp-server

[Install]
WantedBy=multi-user.target
```

### Service Management Commands

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service for startup
sudo systemctl enable cbr-mcp-server

# Start the service
sudo systemctl start cbr-mcp-server

# Check service status
sudo systemctl status cbr-mcp-server

# View service logs
sudo journalctl -u cbr-mcp-server -f

# Stop the service
sudo systemctl stop cbr-mcp-server

# Restart the service
sudo systemctl restart cbr-mcp-server

# Check service configuration
sudo systemctl show cbr-mcp-server

# Service health check
curl http://localhost:8080/health
```

## Docker Deployment

### Dockerfile for Production

Create `Dockerfile.production`:

```dockerfile
# Multi-stage build for production
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt requirements-prod.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install -r requirements-prod.txt

# Production stage
FROM python:3.10-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r cbr && useradd -r -g cbr cbr

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create application directories
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R cbr:cbr /app

# Copy application code
COPY --chown=cbr:cbr . /app/src
WORKDIR /app/src

# Install application
RUN pip install -e .

# Switch to non-root user
USER cbr

# Create volume mount points
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set environment variables
ENV CBR_DATABASE_PATH=/app/data/db \
    CBR_LOG_FILE=/app/logs/server.log \
    CBR_CONFIG_FILE=/app/config/production.yaml \
    PYTHONUNBUFFERED=1

# Run application
CMD ["python", "-m", "cbr_mcp_server"]
```

### Docker Compose for Production

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  cbr-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: cbr-mcp-server
    restart: unless-stopped
    
    # Environment variables
    environment:
      - CBR_LOG_LEVEL=INFO
      - CBR_REQUIRE_AUTH=true
      - CBR_RATE_LIMIT_ENABLED=true
      - CBR_DASHBOARD_HOST=0.0.0.0
      - CBR_DASHBOARD_PORT=8080
    
    # Environment file for secrets
    env_file:
      - .env.production
    
    # Port mapping
    ports:
      - "8080:8080"
    
    # Volume mounts
    volumes:
      - cbr_data:/app/data
      - cbr_logs:/app/logs
      - ./config/production.yaml:/app/config/production.yaml:ro
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
        labels: "service=cbr-mcp-server"
    
    # Security
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    
    # Networks
    networks:
      - cbr_network

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: cbr-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - cbr-mcp-server
    networks:
      - cbr_network

  # Optional: Prometheus monitoring
  prometheus:
    image: prom/prometheus
    container_name: cbr-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - cbr_network

volumes:
  cbr_data:
    driver: local
  cbr_logs:
    driver: local
  prometheus_data:
    driver: local

networks:
  cbr_network:
    driver: bridge
```

### Docker Environment File

Create `.env.production`:

```bash
# Production Environment for Docker
# .env.production

# Security Keys (use actual secure keys)
CBR_API_KEY_1=prod-api-key-secure-123
CBR_API_KEY_2=prod-api-key-secure-456
CBR_ADMIN_KEY=admin-key-secure-789

# Configuration
CBR_LOG_LEVEL=INFO
CBR_LOG_FORMAT=json
CBR_REQUIRE_AUTH=true
CBR_RATE_LIMIT_REQUESTS=500
CBR_CACHE_TTL=1800
CBR_PERFORMANCE_MONITORING=true
CBR_CIRCUIT_BREAKER=true

# Monitoring
CBR_METRICS_ENABLED=true
CBR_WEBSOCKET_ENABLED=true
CBR_SECURITY_HEADERS=true
```

### Docker Deployment Commands

```bash
# Build production image
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f cbr-mcp-server

# Scale service (if needed)
docker-compose -f docker-compose.production.yml up -d --scale cbr-mcp-server=3

# Update service
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Stop services
docker-compose -f docker-compose.production.yml down

# Clean up
docker-compose -f docker-compose.production.yml down -v
docker system prune -f
```

## Security Hardening

### Network Security

```bash
# Configure firewall (UFW on Ubuntu)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow CBR dashboard (restrict source IPs)
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Allow HTTP/HTTPS if using reverse proxy
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check firewall status
sudo ufw status verbose
```

### SSL/TLS Configuration

#### Nginx Reverse Proxy with SSL

Create `/etc/nginx/sites-available/cbr-mcp`:

```nginx
server {
    listen 443 ssl http2;
    server_name cbr.yourcompany.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/cbr.yourcompany.com.crt;
    ssl_certificate_key /etc/ssl/private/cbr.yourcompany.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' ws: wss:; object-src 'none'; frame-src 'none';" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=cbr_api:10m rate=10r/s;
    limit_req zone=cbr_api burst=20 nodelay;

    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket Support
    location /ws/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint (internal only)
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        allow 127.0.0.1;
        allow 192.168.1.0/24;
        deny all;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name cbr.yourcompany.com;
    return 301 https://$server_name$request_uri;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/cbr-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Authentication and Authorization

#### API Key Management

```bash
# Generate secure API keys
openssl rand -base64 32  # For API keys
openssl rand -base64 32  # For admin keys

# Store in environment or secret management system
export CBR_API_KEY_1="$(openssl rand -base64 32)"
export CBR_API_KEY_2="$(openssl rand -base64 32)"
export CBR_ADMIN_KEY="$(openssl rand -base64 32)"

# For production, use secret management
# AWS Secrets Manager, HashiCorp Vault, etc.
```

#### Fail2Ban Configuration

Create `/etc/fail2ban/jail.d/cbr-mcp.conf`:

```ini
[cbr-mcp]
enabled = true
port = 8080,80,443
filter = cbr-mcp
logpath = /var/log/cbr/server.log
maxretry = 5
bantime = 3600
findtime = 600
ignoreip = 127.0.0.1/8 192.168.1.0/24
```

Create `/etc/fail2ban/filter.d/cbr-mcp.conf`:

```ini
[Definition]
failregex = ^.*Authentication failed.*from <HOST>
            ^.*Rate limit exceeded.*from <HOST>
            ^.*Invalid request.*from <HOST>
ignoreregex =
```

```bash
# Enable fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status cbr-mcp
```

### File System Security

```bash
# Set proper file permissions
sudo chmod 640 /etc/cbr/production.yaml
sudo chmod 600 /etc/cbr/environment
sudo chmod 750 /opt/cbr/data
sudo chmod 755 /opt/cbr/app

# SELinux configuration (if enabled)
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 8080

# AppArmor profile (Ubuntu/Debian)
sudo aa-genprof cbr-mcp-server
```

## Database Setup and Migration

### Initial Database Setup

```bash
# Create database directory
sudo -u cbr-server mkdir -p /opt/cbr/data/db

# Initialize ChromaDB
sudo -u cbr-server python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/opt/cbr/data/db')
print('ChromaDB initialized successfully')
"

# Set up monitoring database
sudo -u cbr-server python3 -c "
from cbr_mcp_server import ResourceMonitor, MonitoringConfig
config = MonitoringConfig(db_path='/opt/cbr/data/monitoring.db')
monitor = ResourceMonitor(config)
print('Monitoring database initialized')
"
```

### Database Migration Procedures

```bash
# Backup existing database
sudo -u cbr-server cp -r /opt/cbr/data/db /opt/cbr/backups/db_$(date +%Y%m%d_%H%M%S)

# Migration script
sudo -u cbr-server python3 -c "
from cbr_mcp_server import DatabaseMigrationManager, CBRServerConfig
config = CBRServerConfig.from_environment()
migration_manager = DatabaseMigrationManager(config)

# Run migrations
migration_manager.migrate_to_latest_version()
print('Database migration completed successfully')
"

# Verify migration
sudo -u cbr-server python3 -c "
from cbr_mcp_server import DatabaseIntegrityValidator, CBRServerConfig
config = CBRServerConfig.from_environment()
validator = DatabaseIntegrityValidator(config)
result = validator.run_full_integrity_check()
print(f'Post-migration integrity: {result.overall_status}')
"
```

### Backup and Restore Procedures

```bash
#!/bin/bash
# backup_cbr.sh - Database backup script

BACKUP_DIR="/opt/cbr/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="/opt/cbr/data/db"
MONITORING_DB="/opt/cbr/data/monitoring.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup databases
echo "Creating backup: cbr_backup_$TIMESTAMP"
tar -czf "$BACKUP_DIR/cbr_backup_$TIMESTAMP.tar.gz" \
    -C /opt/cbr/data \
    db/ \
    monitoring.db \
    --exclude="*.tmp" \
    --exclude="*.lock"

# Backup configuration
tar -czf "$BACKUP_DIR/cbr_config_$TIMESTAMP.tar.gz" \
    /etc/cbr/ \
    /opt/cbr/config/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "cbr_backup_*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "cbr_config_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/cbr_backup_$TIMESTAMP.tar.gz"
```

```bash
#!/bin/bash
# restore_cbr.sh - Database restore script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/opt/cbr/data_restore_$(date +%Y%m%d_%H%M%S)"

# Stop service
sudo systemctl stop cbr-mcp-server

# Create restore directory
mkdir -p "$RESTORE_DIR"

# Extract backup
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Backup current data
mv /opt/cbr/data /opt/cbr/data_backup_$(date +%Y%m%d_%H%M%S)

# Restore data
mv "$RESTORE_DIR" /opt/cbr/data

# Set permissions
sudo chown -R cbr-server:cbr-server /opt/cbr/data

# Start service
sudo systemctl start cbr-mcp-server

echo "Restore completed from: $BACKUP_FILE"
```

## Scaling and Performance Considerations

### Horizontal Scaling with Load Balancer

#### HAProxy Configuration

Create `/etc/haproxy/haproxy.cfg`:

```
global
    daemon
    maxconn 4096
    log stdout local0

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    log global

frontend cbr_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/cbr.pem
    redirect scheme https if !{ ssl_fc }
    default_backend cbr_servers

backend cbr_servers
    balance roundrobin
    option httpchk GET /health HTTP/1.1\r\nHost:\ localhost
    http-check expect status 200
    
    server cbr1 192.168.1.10:8080 check inter 30s rise 2 fall 3
    server cbr2 192.168.1.11:8080 check inter 30s rise 2 fall 3
    server cbr3 192.168.1.12:8080 check inter 30s rise 2 fall 3

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
```

### Kubernetes Deployment

#### Kubernetes Manifests

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cbr-mcp
```

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cbr-config
  namespace: cbr-mcp
data:
  production.yaml: |
    database:
      path: "/app/data/db"
      collection_name: "production_case_base"
    
    logging:
      level: "INFO"
      format: "json"
      console_output: true
    
    dashboard:
      host: "0.0.0.0"
      port: 8080
    
    production:
      require_auth: true
      rate_limit_enabled: true
      cache_enabled: true
      circuit_breaker: true
```

Create `k8s/secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cbr-secrets
  namespace: cbr-mcp
type: Opaque
data:
  api-key-1: <base64-encoded-api-key-1>
  api-key-2: <base64-encoded-api-key-2>
  admin-key: <base64-encoded-admin-key>
```

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cbr-mcp-server
  namespace: cbr-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cbr-mcp-server
  template:
    metadata:
      labels:
        app: cbr-mcp-server
    spec:
      containers:
      - name: cbr-mcp-server
        image: cbr-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: CBR_CONFIG_FILE
          value: "/app/config/production.yaml"
        - name: CBR_API_KEY_1
          valueFrom:
            secretKeyRef:
              name: cbr-secrets
              key: api-key-1
        - name: CBR_API_KEY_2
          valueFrom:
            secretKeyRef:
              name: cbr-secrets
              key: api-key-2
        - name: CBR_ADMIN_KEY
          valueFrom:
            secretKeyRef:
              name: cbr-secrets
              key: admin-key
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "8Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: cbr-config
      - name: data
        persistentVolumeClaim:
          claimName: cbr-data-pvc
```

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cbr-mcp-service
  namespace: cbr-mcp
spec:
  selector:
    app: cbr-mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n cbr-mcp
kubectl get svc -n cbr-mcp

# View logs
kubectl logs -f deployment/cbr-mcp-server -n cbr-mcp

# Scale deployment
kubectl scale deployment cbr-mcp-server --replicas=5 -n cbr-mcp
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Maintenance Script

```bash
#!/bin/bash
# daily_maintenance.sh

LOG_FILE="/var/log/cbr/maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting daily maintenance" >> "$LOG_FILE"

# Check service health
if curl -sf http://localhost:8080/health > /dev/null; then
    echo "[$DATE] Health check: PASSED" >> "$LOG_FILE"
else
    echo "[$DATE] Health check: FAILED" >> "$LOG_FILE"
    # Send alert
    echo "CBR MCP Server health check failed" | mail -s "CBR Alert" admin@company.com
fi

# Check disk usage
DISK_USAGE=$(df /opt/cbr/data | awk 'NR==2{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$DATE] Disk usage warning: ${DISK_USAGE}%" >> "$LOG_FILE"
    # Cleanup old logs if needed
    find /var/log/cbr -name "*.log.*" -mtime +7 -delete
fi

# Database integrity check
python3 -c "
from cbr_mcp_server import DatabaseIntegrityValidator, CBRServerConfig
config = CBRServerConfig.from_environment()
validator = DatabaseIntegrityValidator(config)
result = validator.run_full_integrity_check()
print(f'[$DATE] Database integrity: {result.overall_status}')
" >> "$LOG_FILE"

# Backup database
/opt/cbr/scripts/backup_cbr.sh >> "$LOG_FILE" 2>&1

echo "[$DATE] Daily maintenance completed" >> "$LOG_FILE"
```

#### Weekly Maintenance Script

```bash
#!/bin/bash
# weekly_maintenance.sh

# Performance optimization
systemctl restart cbr-mcp-server

# Log rotation (if not using logrotate)
find /var/log/cbr -name "*.log" -size +100M -exec gzip {} \;

# Update system packages (optional, schedule carefully)
# apt update && apt upgrade -y

# Database optimization
python3 -c "
from cbr_mcp_server import DatabaseOptimizer, CBRServerConfig
config = CBRServerConfig.from_environment()
optimizer = DatabaseOptimizer(config)
optimizer.optimize_indices()
optimizer.cleanup_old_metrics()
print('Database optimization completed')
"

# Security updates check
apt list --upgradable | grep -i security
```

### Monitoring and Alerting Setup

#### Log Monitoring with rsyslog

Create `/etc/rsyslog.d/cbr-mcp.conf`:

```
# CBR MCP Server log monitoring
if $programname == 'cbr-mcp-server' then {
    if $msg contains 'ERROR' then {
        @@log-server.company.com:514
        stop
    }
    if $msg contains 'CRITICAL' then {
        @@alert-server.company.com:514
        stop
    }
    /var/log/cbr/cbr-filtered.log
    stop
}
```

#### Prometheus Monitoring

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cbr-mcp-server'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana Dashboard

Create dashboard JSON for CBR MCP Server monitoring including:
- System resource metrics (CPU, Memory, Disk)
- Application metrics (Request rates, Error rates, Cache performance)
- Database metrics (Query latency, Connection status)
- Custom CBR metrics (Retrieval performance, Similarity scores)

### Troubleshooting Production Issues

#### Emergency Procedures

```bash
# Emergency restart with logging
sudo systemctl stop cbr-mcp-server
sudo -u cbr-server cp /var/log/cbr/server.log /opt/cbr/backups/emergency_$(date +%Y%m%d_%H%M%S).log
sudo systemctl start cbr-mcp-server

# Emergency database repair
sudo systemctl stop cbr-mcp-server
sudo -u cbr-server python3 -c "
from cbr_mcp_server import DatabaseRepairer, CBRServerConfig
config = CBRServerConfig.from_environment()
repairer = DatabaseRepairer(config)
success = repairer.emergency_repair()
print(f'Emergency repair: {success}')
"
sudo systemctl start cbr-mcp-server

# Resource emergency procedures
# If high memory usage
systemctl restart cbr-mcp-server
# If high CPU usage
renice -10 $(pgrep -f cbr-mcp-server)
# If disk full
find /var/log -name "*.log.*" -mtime +1 -delete
```

This comprehensive deployment guide provides everything needed to successfully deploy, secure, and maintain the CBR MCP Server in production environments.