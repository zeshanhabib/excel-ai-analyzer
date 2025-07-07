#!/bin/bash

# VPS Installation Script for Excel AI Analyzer
# Works on Ubuntu 20.04+, Debian 11+, CentOS 8+
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/excel_ai/main/deployment/vps/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Please don't run this script as root. Create a regular user account first."
fi

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        error "Cannot detect operating system"
    fi
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log "Docker already installed"
        return
    fi

    # Install Docker using official script
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    log "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    log "Installing Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log "Docker Compose already installed"
        return
    fi

    # Install latest Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for easier access
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log "Docker Compose installed successfully"
}

# Install Nginx
install_nginx() {
    log "Installing Nginx..."
    
    if command -v nginx &> /dev/null; then
        log "Nginx already installed"
        return
    fi

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update
        sudo apt install nginx -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install nginx -y
    fi
    
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    log "Nginx installed successfully"
}

# Install Certbot
install_certbot() {
    log "Installing Certbot for SSL certificates..."
    
    if command -v certbot &> /dev/null; then
        log "Certbot already installed"
        return
    fi

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt install certbot python3-certbot-nginx -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install certbot python3-certbot-nginx -y
    fi
    
    log "Certbot installed successfully"
}

# Install essential tools
install_tools() {
    log "Installing essential tools..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update
        sudo apt install -y git curl wget unzip htop iotop nethogs ufw fail2ban
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install -y git curl wget unzip htop iotop nethogs firewalld fail2ban
    fi
    
    log "Essential tools installed successfully"
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory..."
    
    APP_DIR="/opt/excel_ai"
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    
    log "Application directory created at $APP_DIR"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo ufw allow OpenSSH
        sudo ufw allow 'Nginx Full'
        sudo ufw allow 8501
        sudo ufw --force enable
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --permanent --add-port=8501/tcp
        sudo firewall-cmd --reload
    fi
    
    log "Firewall configured successfully"
}

# Create Nginx configuration
create_nginx_config() {
    log "Creating Nginx configuration..."
    
    sudo tee /etc/nginx/sites-available/excel-ai-analyzer > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # File upload size
    client_max_body_size 100M;
    client_body_timeout 300s;

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

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
}
EOF

    # Enable site (Ubuntu/Debian)
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo ln -sf /etc/nginx/sites-available/excel-ai-analyzer /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
    fi
    
    # Test and restart Nginx
    sudo nginx -t && sudo systemctl restart nginx
    
    log "Nginx configuration created successfully"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    sudo tee /etc/systemd/system/excel-ai-analyzer.service > /dev/null <<EOF
[Unit]
Description=Excel AI Analyzer
Requires=docker.service
After=docker.service network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/excel_ai
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
TimeoutStartSec=300
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable excel-ai-analyzer
    
    log "Systemd service created successfully"
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    sudo tee /usr/local/bin/backup-excel-ai.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/excel-ai"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/excel_ai"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/excel-ai-app-$DATE.tar.gz \
    -C /opt \
    excel_ai \
    --exclude=excel_ai/.git \
    --exclude=excel_ai/logs \
    --exclude=excel_ai/temp

# Backup Docker volumes if they exist
if docker volume ls -q | grep -q excel_ai; then
    docker run --rm \
        -v excel_ai_data:/data \
        -v $BACKUP_DIR:/backup \
        alpine:latest \
        tar czf /backup/excel-ai-volumes-$DATE.tar.gz -C /data .
fi

# Keep only last 7 backups
find $BACKUP_DIR -name "excel-ai-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/excel-ai-app-$DATE.tar.gz"
logger "Excel AI Analyzer backup completed"
EOF

    sudo chmod +x /usr/local/bin/backup-excel-ai.sh
    
    # Setup daily backup cron job
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-excel-ai.sh") | crontab -
    
    log "Backup script created and scheduled"
}

# Create health monitor script
create_health_monitor() {
    log "Creating health monitoring script..."
    
    tee /opt/excel_ai/health-monitor.sh > /dev/null <<'EOF'
#!/bin/bash
LOG_FILE="/var/log/excel-ai-health.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log with timestamp
log_msg() {
    echo "[$DATE] $1" >> $LOG_FILE
}

# Check application health
APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 || echo "000")
if [ "$APP_STATUS" = "200" ]; then
    log_msg "✅ Application healthy"
else
    log_msg "❌ Application unhealthy (HTTP $APP_STATUS)"
    # Try to restart application
    cd /opt/excel_ai && docker-compose restart && log_msg "🔄 Application restarted"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    log_msg "⚠️ Disk usage critical: ${DISK_USAGE}%"
elif [ $DISK_USAGE -gt 75 ]; then
    log_msg "⚠️ Disk usage high: ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    log_msg "⚠️ Memory usage critical: ${MEM_USAGE}%"
fi

# Check Docker service
if ! systemctl is-active --quiet docker; then
    log_msg "❌ Docker service not running"
    sudo systemctl start docker
fi

# Rotate log file if it gets too large (>10MB)
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt 10485760 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    touch "$LOG_FILE"
    log_msg "📋 Log file rotated"
fi
EOF

    chmod +x /opt/excel_ai/health-monitor.sh
    
    # Setup health monitoring cron job (every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/excel_ai/health-monitor.sh") | crontab -
    
    log "Health monitoring script created and scheduled"
}

# Create update script
create_update_script() {
    log "Creating update script..."
    
    sudo tee /usr/local/bin/update-excel-ai.sh > /dev/null <<'EOF'
#!/bin/bash
set -e

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

cd /opt/excel_ai

log "🔄 Updating Excel AI Analyzer..."

# Create backup before update
log "📦 Creating backup..."
/usr/local/bin/backup-excel-ai.sh

# Pull latest changes
log "⬇️ Pulling latest code..."
git pull origin main

# Stop application
log "⏹️ Stopping application..."
docker-compose down

# Pull latest images
log "🐳 Pulling latest Docker images..."
docker-compose pull

# Start application
log "▶️ Starting application..."
docker-compose up -d --build

# Wait for application to start
log "⏳ Waiting for application to start..."
sleep 30

# Check health
if curl -s http://localhost:8501 > /dev/null; then
    log "✅ Update completed successfully!"
else
    log "❌ Application may not be running properly. Check logs:"
    docker-compose logs --tail=50
fi
EOF

    sudo chmod +x /usr/local/bin/update-excel-ai.sh
    
    log "Update script created"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    echo "🚀 Excel AI Analyzer VPS Installation Script"
    echo "=============================================="
    echo -e "${NC}"
    
    # Detect OS
    detect_os
    log "Detected OS: $OS $VER"
    
    # Update system first
    log "Updating system packages..."
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update && sudo apt upgrade -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum update -y
    fi
    
    # Install components
    install_tools
    install_docker
    install_docker_compose
    install_nginx
    install_certbot
    
    # Setup application
    setup_app_directory
    configure_firewall
    create_nginx_config
    create_systemd_service
    create_backup_script
    create_health_monitor
    create_update_script
    
    # Create example environment file
    cat > /opt/excel_ai/.env.example <<EOF
# Copy this file to .env and fill in your values
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
PORT=8501
DEBUG=false
EOF
    
    echo -e "${GREEN}"
    echo "✅ Installation completed successfully!"
    echo "======================================"
    echo -e "${NC}"
    
    echo "📋 Next steps:"
    echo ""
    echo "1. 📥 Clone your repository:"
    echo "   cd /opt/excel_ai"
    echo "   git clone https://github.com/YOUR_USERNAME/excel_ai.git ."
    echo ""
    echo "2. ⚙️ Configure environment:"
    echo "   cp .env.example .env"
    echo "   nano .env  # Add your API keys"
    echo ""
    echo "3. 🚀 Start the application:"
    echo "   docker-compose up -d"
    echo ""
    echo "4. 🌐 Configure domain (optional):"
    echo "   sudo nano /etc/nginx/sites-available/excel-ai-analyzer"
    echo "   # Replace 'server_name _;' with your domain"
    echo "   sudo systemctl reload nginx"
    echo ""
    echo "5. 🔒 Setup SSL certificate:"
    echo "   sudo certbot --nginx -d your-domain.com"
    echo ""
    echo "🔧 Useful commands:"
    echo "   Status:    systemctl status excel-ai-analyzer"
    echo "   Logs:      docker-compose -f /opt/excel_ai/docker-compose.yml logs -f"
    echo "   Update:    sudo /usr/local/bin/update-excel-ai.sh"
    echo "   Backup:    sudo /usr/local/bin/backup-excel-ai.sh"
    echo "   Health:    /opt/excel_ai/health-monitor.sh"
    echo ""
    echo "🌐 Your app will be available at:"
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "YOUR_SERVER_IP")
    echo "   http://$SERVER_IP (after starting the app)"
    echo "   http://your-domain.com (after domain configuration)"
    echo ""
    echo "📊 Monitoring:"
    echo "   Health logs: tail -f /var/log/excel-ai-health.log"
    echo "   System resources: htop"
    echo ""
    warn "Remember to logout and login again for Docker group changes to take effect!"
}

# Run main function
main "$@"
