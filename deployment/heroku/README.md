# Heroku Deployment

## 🏗️ Traditional Cloud Platform

Heroku is a mature platform with excellent documentation and ecosystem.

## Files Required

### 1. Procfile
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 2. runtime.txt
```
python-3.10.12
```

### 3. Heroku-specific requirements
Your existing `requirements.txt` works, but add if needed:
```
gunicorn==20.1.0
```

## 🚀 Deployment Steps

### 1. Install Heroku CLI

**macOS**:
```bash
brew tap heroku/brew && brew install heroku
```

**Windows**:
Download from: https://devcenter.heroku.com/articles/heroku-cli

**Linux**:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login and Create App

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-excel-ai-analyzer

# Or specify region
heroku create your-excel-ai-analyzer --region us
```

### 3. Configure Environment Variables

```bash
# Set OpenAI API key
heroku config:set OPENAI_API_KEY=your_openai_api_key

# Set secret key
heroku config:set SECRET_KEY=your_secret_key

# Set environment
heroku config:set ENVIRONMENT=production
```

### 4. Deploy

```bash
# Add files
git add .
git commit -m "Deploy to Heroku"

# Deploy to Heroku
git push heroku main
```

### 5. Open App

```bash
heroku open
```

## ⚙️ Configuration Files

### Procfile
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
```

### app.json (for Heroku Button)
```json
{
  "name": "Excel AI Analyzer",
  "description": "AI-powered Excel file analysis tool",
  "repository": "https://github.com/YOUR_USERNAME/excel_ai",
  "logo": "https://your-logo-url.com/logo.png",
  "keywords": ["python", "streamlit", "ai", "excel", "data-analysis"],
  "env": {
    "OPENAI_API_KEY": {
      "description": "Your OpenAI API key for AI features",
      "required": true
    },
    "SECRET_KEY": {
      "description": "Secret key for session management",
      "generator": "secret"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

## 💰 Pricing

### Free Tier (Deprecated):
Heroku discontinued free tier as of November 2022.

### Paid Plans:
- **Basic**: $7/month per dyno
- **Standard**: $25/month per dyno
- **Performance**: $250+/month per dyno

## 🔧 Heroku CLI Commands

```bash
# View logs
heroku logs --tail

# Run commands
heroku run python manage.py shell

# Scale dynos
heroku ps:scale web=1

# Restart app
heroku restart

# View app info
heroku info

# View config vars
heroku config
```

## 📊 Add-ons

### Database:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Redis:
```bash
heroku addons:create heroku-redis:hobby-dev
```

### Monitoring:
```bash
heroku addons:create newrelic:wayne
```

### File Storage:
```bash
heroku addons:create cloudinary:free
```

## 🐛 Troubleshooting

### Common Issues:

1. **App crashes on startup**:
   ```bash
   heroku logs --tail
   ```
   Check for missing dependencies or wrong Python version.

2. **Port binding error**:
   Ensure Procfile uses `$PORT` variable:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```

3. **Slug size too large**:
   ```bash
   heroku builds:info
   ```
   Optimize dependencies, use .slugignore file.

4. **Memory errors**:
   Upgrade to higher dyno type or optimize code.

### Debug Mode:
```bash
heroku config:set DEBUG=True
```

## 🔄 CI/CD with GitHub

### 1. Enable GitHub Integration:
1. Go to Heroku Dashboard
2. **Deploy** tab → **GitHub**
3. Connect repository
4. Enable **Automatic deploys**

### 2. Review Apps:
```bash
heroku review-apps:enable
```

## 🌐 Custom Domain

```bash
# Add custom domain
heroku domains:add www.your-domain.com

# SSL certificate (automatic)
heroku certs:auto:enable
```

Configure DNS:
```
CNAME: www.your-domain.com → your-app-name.herokuapp.com
```

## 📈 Performance Optimization

### 1. Use Gunicorn (alternative):
```bash
# Procfile
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### 2. Enable caching:
```python
import streamlit as st

@st.cache_data
def load_data():
    # Your data loading logic
    pass
```

### 3. Optimize dependencies:
- Use only required packages
- Consider lighter alternatives

## 🔒 Security

### Environment Variables:
```bash
heroku config:set SECURE_SSL_REDIRECT=True
heroku config:set STREAMLIT_SERVER_ENABLE_CORS=False
```

### HTTPS:
- Automatic SSL certificate
- Force HTTPS redirects
