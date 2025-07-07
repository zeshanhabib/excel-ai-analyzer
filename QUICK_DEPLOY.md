# 🚀 Quick Deploy Guide

## Deploy Excel AI Analyzer in 5 Minutes

### Option 1: Streamlit Cloud (FREE) 🌟

**Perfect for demos and testing**

1. **Fork/Clone this repository**
2. **Go to**: https://share.streamlit.io/
3. **Sign in** with GitHub
4. **Deploy**: Select your repo, set main file to `app.py`
5. **Add Secret**: In dashboard, add `OPENAI_API_KEY = "your-key"`
6. **Done!** Your app is live at `https://your-app.streamlit.app`

### Option 2: Railway ($5/month) 🚂

**Best for production apps**

1. **Go to**: https://railway.app/
2. **Sign up** with GitHub
3. **Deploy from GitHub repo**: Select your repository
4. **Railway auto-detects** Docker configuration
5. **Add Environment Variable**: `OPENAI_API_KEY`
6. **Deploy!** Live at `https://your-app.railway.app`

### Option 3: One-Click Docker 🐳

**For any VPS or cloud server**

```bash
# Clone and deploy in one command
git clone https://github.com/YOUR_USERNAME/excel_ai.git
cd excel_ai
echo "OPENAI_API_KEY=your-key-here" > .env
docker-compose up -d
```

Your app will be running on `http://localhost:8501`

## Environment Setup

### Required Environment Variables

```bash
# Copy example and edit
cp .env.example .env

# Add your OpenAI API Key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Get OpenAI API Key

1. Visit: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and use in your deployment

## Platform-Specific Guides

| Platform | Cost | Difficulty | Guide |
|----------|------|------------|-------|
| Streamlit Cloud | Free | ⭐ | [Guide](deployment/streamlit-cloud/README.md) |
| Railway | $5/mo | ⭐⭐ | [Guide](deployment/railway/README.md) |
| Heroku | $7/mo | ⭐⭐ | [Guide](deployment/heroku/README.md) |
| DigitalOcean | $5/mo | ⭐⭐⭐ | [Guide](deployment/README.md) |
| AWS/GCP | $10+/mo | ⭐⭐⭐⭐ | [Guide](deployment/aws/README.md) |
| VPS | $5/mo | ⭐⭐⭐⭐⭐ | [Guide](deployment/vps/README.md) |

## Features Ready for Production

✅ **Excel File Analysis** - Upload and analyze any Excel file  
✅ **AI-Powered Insights** - Get intelligent data analysis  
✅ **Interactive Visualizations** - Beautiful charts and graphs  
✅ **Google Sheets Integration** - Connect to Google Sheets  
✅ **Docker Ready** - Containerized for easy deployment  
✅ **Multi-Platform** - Deploy anywhere  
✅ **Security Hardened** - Production-ready security  

## Need Help?

- 📖 **Full Documentation**: See `deployment/README.md`
- 🔒 **Security Checklist**: See `PUBLIC_DEPLOYMENT_CHECKLIST.md`
- 🐛 **Issues**: Create GitHub issue
- 💬 **Discussions**: Use GitHub discussions

---

**Ready to deploy?** Choose your platform above and follow the guide!
