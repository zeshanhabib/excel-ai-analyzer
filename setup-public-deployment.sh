#!/bin/bash

# 🚀 Excel AI Analyzer - Public Deployment Setup Script
# This script prepares your local project for public deployment

set -e

echo "🚀 Setting up Excel AI Analyzer for Public Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "This script must be run from the Excel AI Analyzer root directory!"
    exit 1
fi

print_info "Preparing public deployment branch..."

# 1. Create and switch to public deployment branch
echo ""
echo "📁 Creating public-deployment branch..."
git checkout -b public-deployment 2>/dev/null || git checkout public-deployment

# 2. Remove sensitive files from git history if they exist
echo ""
echo "🔒 Ensuring sensitive files are not tracked..."

# Remove any accidentally tracked sensitive files
git rm --cached .env 2>/dev/null || true
git rm --cached *.log 2>/dev/null || true
git rm --cached users.key 2>/dev/null || true
git rm --cached users.enc 2>/dev/null || true
git rm --cached debug_reports/*.json 2>/dev/null || true

# 3. Clean up temporary and sensitive files
echo ""
echo "🧹 Cleaning up temporary files..."

# Remove log files
rm -f *.log
rm -f logs/*.log 2>/dev/null || true

# Remove debug reports
rm -rf debug_reports/*.json 2>/dev/null || true

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove OS files
find . -name ".DS_Store" -delete 2>/dev/null || true

# 4. Verify .env.example exists and is properly configured
if [ ! -f ".env.example" ]; then
    print_warning ".env.example not found. Creating one..."
    cat > .env.example << EOF
# Environment variables for Excel AI Analyzer
# Copy this file to .env and fill in your actual values

# Required: OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: OpenAI Model Selection
OPENAI_MODEL=gpt-4o-mini

# Optional: Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS=

# Flask/Streamlit Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False

# Deployment Settings
ENVIRONMENT=development
PORT=8501
EOF
fi

# 5. Create or update public README
echo ""
echo "📖 Creating public deployment documentation..."

# Check if we need to create a public README section
if ! grep -q "Public Deployment" README.md; then
    cat >> README.md << 'EOF'

## 🌐 Public Deployment

This project is ready for public deployment on various cloud platforms.

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/excel_ai.git
   cd excel_ai
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**:
   ```bash
   streamlit run app.py
   ```

### Deployment Options

See the `deployment/` directory for platform-specific guides:

- **Streamlit Cloud** (Free): `deployment/streamlit-cloud/README.md`
- **Railway**: `deployment/railway/README.md`
- **Heroku**: `deployment/heroku/README.md`
- **AWS**: `deployment/aws/README.md`
- **VPS**: `deployment/vps/README.md`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `OPENAI_MODEL` | OpenAI model to use | No (default: gpt-4o-mini) |
| `GOOGLE_SHEETS_CREDENTIALS` | Google Sheets API credentials | No |

EOF
fi

# 6. Commit changes
echo ""
echo "💾 Committing public deployment setup..."
git add .
git commit -m "🚀 Prepare for public deployment

- Enhanced .gitignore for security
- Updated .env.example with comprehensive options
- Cleaned up sensitive files and logs
- Added public deployment documentation

Ready for public repository deployment!" 2>/dev/null || true

# 7. Show status
echo ""
echo "🎉 Public deployment setup complete!"
echo ""
print_status "Branch 'public-deployment' is ready for public repository"
print_info "Next steps:"
echo "  1. Push to GitHub: git push origin public-deployment"
echo "  2. Create public repository on GitHub"
echo "  3. Deploy using guides in deployment/ directory"
echo ""
print_warning "Remember to:"
echo "  - Set OPENAI_API_KEY in your deployment platform"
echo "  - Review all files before making repository public"
echo "  - Test deployment on your chosen platform"
echo ""

# 8. Show deployment options
echo "🚀 Available Deployment Platforms:"
echo ""
echo "  🌟 Streamlit Cloud (Free):  https://share.streamlit.io/"
echo "  🚂 Railway ($5/month):     https://railway.app/"
echo "  🔴 Heroku ($7/month):      https://heroku.com/"
echo "  🌊 DigitalOcean:           https://www.digitalocean.com/"
echo "  ☁️  AWS/GCP/Azure:         Enterprise options available"
echo ""
echo "See deployment/ directory for detailed guides!"
