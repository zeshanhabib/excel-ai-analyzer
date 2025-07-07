#!/bin/bash

# AWS EC2 Setup Script for Excel AI Analyzer
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/excel_ai/main/deployment/aws/setup.sh | bash

set -e

echo "🚀 Setting up Excel AI Analyzer on AWS EC2..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y

# Install Certbot for SSL
echo "🔒 Installing Certbot..."
sudo apt install certbot python3-certbot-nginx -y

# Install Git
echo "📝 Installing Git..."
sudo apt install git -y

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/excel_ai
sudo chown $USER:$USER /opt/excel_ai
cd /opt/excel_ai

# Clone repository (user needs to provide their repo URL)
echo "📥 Ready to clone repository..."
echo "Please run the following commands:"
echo ""
echo "cd /opt/excel_ai"
echo "git clone https://github.com/YOUR_USERNAME/excel_ai.git ."
echo ""
echo "# Set environment variables"
echo "nano .env"
echo "# Add: OPENAI_API_KEY=your_key_here"
echo "# Add: SECRET_KEY=your_secret_key_here"
echo "# Add: ENVIRONMENT=production"
echo ""
echo "# Start the application"
echo "docker-compose up -d"
echo ""

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 8501
sudo ufw --force enable

# Create Nginx configuration template
echo "📄 Creating Nginx configuration template..."
sudo tee /etc/nginx/sites-available/excel-ai-analyzer > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

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
        
        # Increase timeout for large file uploads
        proxy_connect_timeout       300;
        proxy_send_timeout          300;
        proxy_read_timeout          300;
        send_timeout                300;
        client_max_body_size        100M;
    }
}
EOF

# Create systemd service for auto-start
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/excel-ai-analyzer.service > /dev/null <<EOF
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

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable excel-ai-analyzer

# Create log rotation
echo "📊 Setting up log rotation..."
sudo tee /etc/logrotate.d/excel-ai-analyzer > /dev/null <<EOF
/opt/excel_ai/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Install monitoring tools
echo "📈 Installing monitoring tools..."
sudo apt install htop iotop nethogs -y

# Create backup script
echo "💾 Creating backup script..."
sudo tee /usr/local/bin/backup-excel-ai.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/opt/backups/excel-ai"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Backup application files
tar -czf \$BACKUP_DIR/excel-ai-\$DATE.tar.gz -C /opt/excel_ai .

# Keep only last 7 backups
find \$BACKUP_DIR -name "excel-ai-*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$BACKUP_DIR/excel-ai-\$DATE.tar.gz"
EOF

sudo chmod +x /usr/local/bin/backup-excel-ai.sh

# Setup daily backup cron job
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-excel-ai.sh") | crontab -

# Create health check script
echo "🏥 Creating health check script..."
tee /opt/excel_ai/health-check.sh > /dev/null <<EOF
#!/bin/bash
response=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
if [ \$response -eq 200 ]; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application is unhealthy (HTTP \$response)"
    # Restart application
    cd /opt/excel_ai
    docker-compose restart
    exit 1
fi
EOF

chmod +x /opt/excel_ai/health-check.sh

# Setup health check cron job (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/excel_ai/health-check.sh >> /var/log/excel-ai-health.log 2>&1") | crontab -

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository:"
echo "   cd /opt/excel_ai && git clone https://github.com/YOUR_USERNAME/excel_ai.git ."
echo ""
echo "2. Create environment file:"
echo "   nano .env"
echo "   # Add your environment variables"
echo ""
echo "3. Start the application:"
echo "   docker-compose up -d"
echo ""
echo "4. Configure Nginx (replace your-domain.com):"
echo "   sudo nano /etc/nginx/sites-available/excel-ai-analyzer"
echo "   sudo ln -s /etc/nginx/sites-available/excel-ai-analyzer /etc/nginx/sites-enabled/"
echo "   sudo nginx -t && sudo systemctl restart nginx"
echo ""
echo "5. Setup SSL certificate:"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Restart app: docker-compose restart"
echo "   Health check: ./health-check.sh"
echo "   Backup: /usr/local/bin/backup-excel-ai.sh"
echo ""
echo "🌐 Your app will be available at:"
echo "   http://$(curl -s ifconfig.me):8501 (direct)"
echo "   http://your-domain.com (via Nginx)"
echo ""
