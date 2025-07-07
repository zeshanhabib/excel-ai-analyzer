#!/bin/bash

# 📦 Excel AI Analyzer - Distribution Package Creator
# Creates a clean zip file for distribution excluding development files

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Creating Excel AI Analyzer Distribution Package...${NC}"

# Get the current date for versioning
DATE=$(date +%Y%m%d)
VERSION="v1.0.${DATE}"
PACKAGE_NAME="excel-ai-analyzer-${VERSION}"

echo -e "${BLUE}📋 Package Details:${NC}"
echo "   Name: ${PACKAGE_NAME}"
echo "   Date: $(date)"
echo "   Size: Calculating..."

# Create temporary directory for packaging
TEMP_DIR="/tmp/${PACKAGE_NAME}"
ZIP_FILE="${PACKAGE_NAME}.zip"

echo -e "\n${BLUE}🧹 Preparing clean distribution...${NC}"

# Remove existing zip and temp directory
rm -rf "${TEMP_DIR}" "${ZIP_FILE}" 2>/dev/null || true

# Create temp directory
mkdir -p "${TEMP_DIR}"

# Copy files using rsync to exclude unwanted items
rsync -av \
  --exclude='.git/' \
  --exclude='venv/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.log' \
  --exclude='.DS_Store' \
  --exclude='debug_reports/' \
  --exclude='.env' \
  --exclude='*.tmp' \
  --exclude='temp_*' \
  --exclude='node_modules/' \
  --exclude='.pytest_cache/' \
  --exclude='.coverage' \
  --exclude='htmlcov/' \
  --exclude='dist/' \
  --exclude='build/' \
  --exclude='*.egg-info/' \
  ./ "${TEMP_DIR}/"

echo -e "\n${BLUE}📋 Creating distribution documentation...${NC}"

# Create a distribution README
cat > "${TEMP_DIR}/DISTRIBUTION_README.md" << 'EOF'
# 📦 Excel AI Analyzer - Distribution Package

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Run Application
```bash
# Local development
streamlit run app.py

# Or use Docker
docker-compose up -d
```

## 📚 Documentation

- **README.md** - Complete setup and usage guide
- **QUICK_DEPLOY.md** - 5-minute deployment guide
- **deployment/** - Platform-specific deployment guides
- **PUBLIC_DEPLOYMENT_CHECKLIST.md** - Security checklist

## 🎯 Sample Data

Test the application with included sample data in `sample_data/`:
- Sales data (1,000 records)
- Employee data (500 records)
- Inventory data (300 records)
- Multi-sheet examples

## 🌐 Deployment Options

- **Streamlit Cloud** (Free)
- **Railway** ($5/month)
- **Heroku** ($7/month)
- **AWS/GCP/Azure**
- **VPS/Self-hosted**

See `deployment/` directory for detailed guides.

## 🔧 Requirements

- Python 3.8+
- OpenAI API key (for AI features)
- 2GB+ RAM recommended

## 📞 Support

- Documentation: See README.md
- Issues: Create GitHub issue
- Security: See PUBLIC_DEPLOYMENT_CHECKLIST.md

---

**Happy analyzing! 📊✨**
EOF

# Create installation script
cat > "${TEMP_DIR}/install.sh" << 'EOF'
#!/bin/bash

# 🚀 Excel AI Analyzer - Installation Script

echo "📦 Installing Excel AI Analyzer..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OpenAI API key"
fi

echo "✅ Installation complete!"
echo ""
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   streamlit run app.py"
echo ""
echo "🌐 Or use Docker:"
echo "   docker-compose up -d"
EOF

chmod +x "${TEMP_DIR}/install.sh"

# Create Windows batch file
cat > "${TEMP_DIR}/install.bat" << 'EOF'
@echo off
echo 📦 Installing Excel AI Analyzer...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment template
if not exist ".env" (
    echo ⚙️ Creating environment file...
    copy .env.example .env
    echo 📝 Please edit .env and add your OpenAI API key
)

echo ✅ Installation complete!
echo.
echo 🚀 To start the application:
echo    venv\Scripts\activate.bat
echo    streamlit run app.py
echo.
echo 🌐 Or use Docker:
echo    docker-compose up -d
pause
EOF

echo -e "\n${BLUE}📊 Package contents:${NC}"
find "${TEMP_DIR}" -type f | wc -l | xargs echo "   Files:"
du -sh "${TEMP_DIR}" | cut -f1 | xargs echo "   Size:"

echo -e "\n${BLUE}🗜️ Creating zip file...${NC}"

# Create zip file
cd "$(dirname "${TEMP_DIR}")"
zip -r "${ZIP_FILE}" "$(basename "${TEMP_DIR}")" > /dev/null

# Move zip to original directory
mv "${ZIP_FILE}" "${OLDPWD}/"

# Cleanup temp directory
rm -rf "${TEMP_DIR}"

# Final information
cd "${OLDPWD}"
ZIP_SIZE=$(du -sh "${ZIP_FILE}" | cut -f1)

echo -e "\n${GREEN}✅ Distribution package created successfully!${NC}"
echo -e "\n${BLUE}📦 Package Information:${NC}"
echo "   File: ${ZIP_FILE}"
echo "   Size: ${ZIP_SIZE}"
echo "   Location: $(pwd)/${ZIP_FILE}"

echo -e "\n${BLUE}📋 Contents:${NC}"
echo "   ✅ Source code (Python files)"
echo "   ✅ Sample data (Excel files)"
echo "   ✅ Docker configuration"
echo "   ✅ Deployment guides"
echo "   ✅ Installation scripts"
echo "   ✅ Documentation"
echo "   ❌ Virtual environment (excluded)"
echo "   ❌ Git history (excluded)"
echo "   ❌ Log files (excluded)"
echo "   ❌ Cache files (excluded)"

echo -e "\n${YELLOW}📤 Ready for distribution!${NC}"
echo "   Share: ${ZIP_FILE}"
echo "   Recipients can unzip and run ./install.sh (or install.bat on Windows)"

echo -e "\n${BLUE}🧪 Quick test:${NC}"
echo "   unzip ${ZIP_FILE}"
echo "   cd ${PACKAGE_NAME}"
echo "   ./install.sh"
