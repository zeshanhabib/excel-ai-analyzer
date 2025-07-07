# Railway Deployment

## 🚄 Modern Cloud Platform

Railway offers excellent Docker support and modern deployment experience.

## Prerequisites

- GitHub repository
- Railway account (free tier available)

## Deployment Methods

### Method 1: Direct from GitHub (Recommended)

1. **Visit**: https://railway.app/
2. **Sign up** with GitHub
3. **Click "Deploy from GitHub repo"**
4. **Select your repository**
5. **Railway auto-detects** Docker setup ✅

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway deploy
```

## 🐳 Configuration

Railway will automatically use your existing `Dockerfile` and `docker-compose.yml`.

### Environment Variables

In Railway dashboard:
1. Go to **Variables** tab
2. Add:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key
   PORT=8501
   ```

### Custom Domain

1. Go to **Settings** → **Domains**
2. **Add custom domain** or use Railway subdomain
3. **Automatic HTTPS** included ✅

## 📊 Railway Configuration File

Create `railway.toml` (optional):

```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "always"

[[services]]
name = "excel-ai-analyzer"
source = "."

[services.env]
PORT = "8501"
```

## 💰 Pricing

### Hobby Plan (Free):
- $5 credit/month
- Shared resources
- Community support

### Pro Plan ($20/month):
- $20 credit included
- Priority builds
- More resources
- Email support

## 🔄 Auto-Deployment

- **GitHub integration**: Auto-deploy on push to main
- **Branch deployments**: Deploy different branches
- **Rollback**: Easy rollback to previous versions

## 📈 Scaling

Railway automatically scales based on:
- CPU usage
- Memory usage
- Request volume

### Manual Scaling:
```bash
railway scale --replicas 3
```

## 🐛 Troubleshooting

### View Logs:
```bash
railway logs
```

### Common Issues:

1. **Build failures**:
   ```bash
   railway logs --build
   ```

2. **Port issues**:
   - Ensure `PORT` environment variable is set
   - Use `0.0.0.0:$PORT` in Streamlit config

3. **Memory limits**:
   - Optimize Docker image
   - Use multi-stage builds

## 🔧 Advanced Configuration

### Custom Dockerfile:
Railway uses your existing Dockerfile automatically.

### Database Integration:
```bash
railway add postgresql
railway add redis
```

### Monitoring:
- Built-in metrics dashboard
- Resource usage tracking
- Uptime monitoring

## 🚀 Deployment Commands

```bash
# Deploy current directory
railway deploy

# Deploy specific service
railway deploy --service excel-ai-analyzer

# Check deployment status
railway status

# View service info
railway info
```

## 🌐 Custom Domain Setup

1. **Railway Dashboard** → **Settings** → **Domains**
2. **Add domain**: `your-domain.com`
3. **Configure DNS**:
   ```
   CNAME: your-app-name.railway.app
   ```
4. **SSL Certificate**: Automatic via Let's Encrypt ✅

## 📊 Performance Tips

1. **Optimize Docker image**:
   - Use slim base images
   - Multi-stage builds
   - .dockerignore file

2. **Enable caching**:
   - Railway caches Docker layers
   - Use `@st.cache_data` in Streamlit

3. **Monitor resources**:
   - Check Railway dashboard
   - Set up alerts for high usage
