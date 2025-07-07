# AWS EC2 Deployment

## ☁️ Enterprise-Grade Hosting

Deploy your Excel AI Analyzer on AWS EC2 for scalable, production-ready hosting.

## 🚀 Quick Deploy

### Option 1: Using Docker (Recommended)

1. **Launch EC2 Instance**:
   - **AMI**: Ubuntu 20.04 LTS
   - **Instance Type**: t3.medium (minimum for AI workloads)
   - **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8501 (Streamlit)

2. **Connect and Setup**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Run Setup Script**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/excel_ai/main/deployment/aws/setup.sh | bash
   ```

### Option 2: Manual Setup

Follow the detailed steps below.

## 📋 Manual Deployment Steps

### 1. Launch EC2 Instance

**Instance Configuration**:
- **AMI**: Ubuntu 20.04 LTS
- **Instance Type**: 
  - `t3.medium` (minimum) - 2 vCPU, 4GB RAM
  - `t3.large` (recommended) - 2 vCPU, 8GB RAM
  - `c5.xlarge` (production) - 4 vCPU, 8GB RAM

**Security Group Rules**:
```
SSH (22)     - Your IP
HTTP (80)    - 0.0.0.0/0
HTTPS (443)  - 0.0.0.0/0
Custom (8501) - 0.0.0.0/0
```

### 2. Connect to Instance

```bash
# Connect via SSH
ssh -i your-key-pair.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

### 3. Install Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 4. Deploy Application

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/excel_ai.git
cd excel_ai

# Set environment variables
echo "OPENAI_API_KEY=your_openai_api_key" > .env
echo "SECRET_KEY=your_secret_key" >> .env
echo "ENVIRONMENT=production" >> .env

# Start application
docker-compose up -d
```

### 5. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/excel-ai-analyzer
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/excel-ai-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Setup SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔧 Advanced Configuration

### Auto Scaling Group

Create `user-data.sh` for auto-scaling:
```bash
#!/bin/bash
apt update
apt install docker.io docker-compose -y
usermod -aG docker ubuntu

# Clone and start app
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/excel_ai.git
cd excel_ai
echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env
docker-compose up -d
```

### Load Balancer

Use AWS Application Load Balancer:
1. **Create ALB** with target group
2. **Configure health check**: `/health` endpoint
3. **Add SSL certificate** via ACM

### RDS Database

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update connection string
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/dbname
```

## 💰 Cost Estimation

### Monthly Costs:
- **t3.medium**: ~$30/month
- **t3.large**: ~$60/month
- **Load Balancer**: ~$20/month
- **RDS (db.t3.micro)**: ~$15/month
- **SSL Certificate**: Free (Let's Encrypt)

## 📊 Monitoring & Logging

### CloudWatch Setup

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

### Application Logs

```bash
# View application logs
docker-compose logs -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 Security Best Practices

### 1. Security Groups
- Restrict SSH access to your IP only
- Use HTTPS for all web traffic

### 2. IAM Roles
Create IAM role with minimal permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket/*"
        }
    ]
}
```

### 3. Environment Variables
```bash
# Store in AWS Systems Manager Parameter Store
aws ssm put-parameter --name "/excel-ai/openai-key" --value "your-key" --type "SecureString"
```

## 🔄 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.EC2_SSH_KEY }}
        script: |
          cd excel_ai
          git pull origin main
          docker-compose down
          docker-compose up -d --build
```

## 🐛 Troubleshooting

### Common Issues:

1. **Permission denied**:
   ```bash
   sudo chmod 400 your-key.pem
   ```

2. **Docker not starting**:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Nginx configuration error**:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **SSL certificate issues**:
   ```bash
   sudo certbot renew --dry-run
   ```

## 📈 Performance Optimization

### 1. Instance Optimization
- Use SSD storage (gp3)
- Enable detailed monitoring
- Configure auto-scaling based on CPU/memory

### 2. Application Optimization
- Use Redis for caching
- Optimize Docker images
- Enable gzip compression in Nginx

### 3. Database Optimization
- Use RDS for production
- Enable read replicas
- Configure proper backup strategy
