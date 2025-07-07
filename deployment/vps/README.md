# VPS Deployment Guide

## 🖥️ Self-Hosted VPS Solution

Deploy your Excel AI Analyzer on any VPS provider for maximum control and cost efficiency.

## 🏆 Recommended VPS Providers

| Provider | Starting Price | Features |
|----------|----------------|----------|
| **Linode** | $5/month | Excellent docs, SSD storage |
| **DigitalOcean** | $5/month | Great community, one-click apps |
| **Vultr** | $5/month | High performance, global locations |
| **Hetzner** | €4/month | Best price/performance in EU |
| **Contabo** | €5/month | High RAM, good for AI workloads |

## 📋 Minimum Requirements

- **RAM**: 2GB (4GB recommended for AI features)
- **CPU**: 1 vCore (2+ recommended)
- **Storage**: 20GB SSD
- **Bandwidth**: 1TB/month
- **OS**: Ubuntu 20.04+ or Debian 11+

## 🚀 Quick Deploy Script

### One-Line Installation:
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/excel_ai/main/deployment/vps/install.sh | bash
```

### Manual Steps:

## 📖 Step-by-Step Deployment

### 1. Create VPS Instance

**Choose Configuration**:
- **OS**: Ubuntu 20.04 LTS
- **Size**: 
  - Basic: 1GB RAM, 1 vCPU ($5/month)
  - Recommended: 2GB RAM, 2 vCPU ($10/month)
  - AI Optimized: 4GB RAM, 2 vCPU ($20/month)

### 2. Initial Server Setup

```bash
# Connect via SSH
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser excel-ai
usermod -aG sudo excel-ai

# Setup SSH key authentication
mkdir -p /home/excel-ai/.ssh
cp ~/.ssh/authorized_keys /home/excel-ai/.ssh/
chown -R excel-ai:excel-ai /home/excel-ai/.ssh
chmod 700 /home/excel-ai/.ssh
chmod 600 /home/excel-ai/.ssh/authorized_keys

# Switch to new user
su - excel-ai
```

### 3. Install Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Install monitoring tools
sudo apt install htop iotop git curl wget unzip -y
```

### 4. Deploy Application

```bash
# Create app directory
sudo mkdir -p /opt/excel_ai
sudo chown $USER:$USER /opt/excel_ai
cd /opt/excel_ai

# Clone repository
git clone https://github.com/YOUR_USERNAME/excel_ai.git .

# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
PORT=8501
EOF

# Start application
docker-compose up -d
```

### 5. Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/excel-ai-analyzer << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # File upload size
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/excel-ai-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Setup SSL Certificate

```bash
# Install SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 7. Configure Firewall

```bash
# Setup UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Check status
sudo ufw status
```

## 🔧 Advanced Configuration

### Automatic Startup Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/excel-ai-analyzer.service << EOF
[Unit]
Description=Excel AI Analyzer
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/excel_ai
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=excel-ai

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable excel-ai-analyzer
sudo systemctl start excel-ai-analyzer
```

### Monitoring Setup

```bash
# Install monitoring stack
mkdir -p /opt/monitoring
cd /opt/monitoring

# Create monitoring docker-compose
cat > docker-compose.yml << EOF
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    restart: unless-stopped
EOF

# Start monitoring
docker-compose up -d
```

### Backup Script

```bash
# Create backup script
sudo tee /usr/local/bin/backup-excel-ai.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/excel_ai"

mkdir -p $BACKUP_DIR

# Backup application files and data
tar -czf $BACKUP_DIR/excel-ai-backup-$DATE.tar.gz \
    -C /opt \
    excel_ai \
    --exclude=excel_ai/node_modules \
    --exclude=excel_ai/.git

# Backup Docker volumes
docker run --rm \
    -v excel_ai_data:/data \
    -v $BACKUP_DIR:/backup \
    alpine \
    tar czf /backup/excel-ai-volumes-$DATE.tar.gz -C /data .

# Keep only last 7 backups
find $BACKUP_DIR -name "excel-ai-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/excel-ai-backup-$DATE.tar.gz"
EOF

sudo chmod +x /usr/local/bin/backup-excel-ai.sh

# Setup daily backup
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-excel-ai.sh") | crontab -
```

## 📊 Performance Optimization

### 1. Nginx Optimization

```bash
# Edit Nginx configuration
sudo nano /etc/nginx/nginx.conf
```

Add performance settings:
```nginx
http {
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Connection optimization
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 100m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
}
```

### 2. Docker Optimization

```bash
# Create optimized docker-compose override
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  excel-ai-analyzer:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
```

### 3. System Optimization

```bash
# Optimize system settings
sudo tee -a /etc/sysctl.conf << EOF
# Network optimization
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# File system optimization
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

sudo sysctl -p
```

## 🔒 Security Hardening

### SSH Security

```bash
# Configure SSH
sudo nano /etc/ssh/sshd_config
```

Add security settings:
```
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

```bash
sudo systemctl restart ssh
```

### Fail2Ban

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Configure Fail2Ban
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
logpath = /var/log/nginx/access.log
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📈 Monitoring & Maintenance

### Health Monitoring Script

```bash
# Create health check script
tee /opt/excel_ai/health-monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/excel-ai-health.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check application health
APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
if [ $APP_STATUS -eq 200 ]; then
    echo "[$DATE] ✅ Application healthy" >> $LOG_FILE
else
    echo "[$DATE] ❌ Application unhealthy (HTTP $APP_STATUS)" >> $LOG_FILE
    # Restart application
    cd /opt/excel_ai && docker-compose restart
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] ⚠️ Disk usage high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$DATE] ⚠️ Memory usage high: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /opt/excel_ai/health-monitor.sh

# Run every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/excel_ai/health-monitor.sh") | crontab -
```

## 🔄 Updates & Maintenance

### Update Script

```bash
# Create update script
sudo tee /usr/local/bin/update-excel-ai.sh << 'EOF'
#!/bin/bash
cd /opt/excel_ai

echo "🔄 Updating Excel AI Analyzer..."

# Backup current version
/usr/local/bin/backup-excel-ai.sh

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose pull
docker-compose up -d --build

echo "✅ Update completed!"
EOF

sudo chmod +x /usr/local/bin/update-excel-ai.sh
```

## 💰 Cost Optimization

### 1. Choose Right VPS Size
- Start with 2GB RAM for testing
- Scale up based on actual usage
- Monitor resource utilization

### 2. Use Reserved Instances
- Annual payments often 20-30% cheaper
- Good for production environments

### 3. Optimize Docker Images
- Use multi-stage builds
- Remove unnecessary packages
- Use slim base images

## 🐛 Troubleshooting

### Common Issues:

1. **Application won't start**:
   ```bash
   docker-compose logs -f
   ```

2. **Nginx errors**:
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. **SSL certificate issues**:
   ```bash
   sudo certbot certificates
   sudo certbot renew --force-renewal
   ```

4. **Performance issues**:
   ```bash
   htop
   docker stats
   ```

### Log Locations:
- Application: `/opt/excel_ai/logs/`
- Nginx: `/var/log/nginx/`
- System: `/var/log/syslog`

This VPS deployment gives you full control, excellent performance, and cost efficiency for hosting your Excel AI Analyzer!
