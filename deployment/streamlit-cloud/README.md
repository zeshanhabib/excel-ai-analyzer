# Streamlit Cloud Deployment

## 🌟 Free & Easy Deployment

Streamlit Cloud is the easiest way to deploy your Excel AI Analyzer for free.

## Prerequisites

1. **GitHub Repository** (public for free tier)
2. **requirements.txt** ✅ (already have)
3. **app.py** ✅ (already have)

## Step-by-Step Deployment

### 1. Prepare Repository

Ensure your repository has these files:
- `app.py` (main Streamlit app)
- `requirements.txt` (dependencies)
- All supporting Python files

### 2. Push to GitHub

```bash
# If not already done
git init
git add .
git commit -m "Initial commit for Streamlit Cloud"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/excel_ai.git
git push -u origin main
```

### 3. Deploy on Streamlit Cloud

1. **Visit**: https://share.streamlit.io/
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Select your repository**: `excel_ai`
5. **Main file path**: `app.py`
6. **Click "Deploy!"**

### 4. Configure Secrets

In Streamlit Cloud dashboard:
1. Go to **App settings** → **Secrets**
2. Add your environment variables:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
SECRET_KEY = "your_secret_key_here"
```

## 🎯 App URL

Your app will be available at:
```
https://share.streamlit.io/YOUR_USERNAME/excel_ai/main/app.py
```

## 🔄 Automatic Updates

- **Auto-deploy**: Every push to main branch triggers redeployment
- **Manual redeploy**: Use the "Reboot app" button in dashboard

## 📋 Limitations

- ⚠️ **Public repos only** (for free tier)
- ⚠️ **Resource limits**: 1GB RAM, shared CPU
- ⚠️ **No custom domain** (free tier)
- ⚠️ **Sleep after inactivity**

## 🚀 Upgrade Options

**Streamlit Cloud Teams** ($20/month):
- Private repositories
- More resources
- Custom domains
- Priority support

## 🐛 Troubleshooting

### Common Issues:

1. **App won't start**:
   - Check `requirements.txt` format
   - Ensure all imports are included

2. **Memory errors**:
   - Optimize file processing
   - Use `@st.cache_data` for large operations

3. **API key issues**:
   - Verify secrets are properly set
   - Check for typos in secret names

### Logs:
View real-time logs in the Streamlit Cloud dashboard under "Manage app" → "Logs"

## 📊 Monitoring

- **Usage stats**: Available in Streamlit Cloud dashboard
- **Error tracking**: Check logs for exceptions
- **Performance**: Monitor load times and memory usage
