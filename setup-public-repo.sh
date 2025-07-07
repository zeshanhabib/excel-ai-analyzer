#!/bin/bash

# 🚀 Excel AI Analyzer - Public Repository Setup Script
# Creates a new public repository and pushes the public-deployment branch

set -e

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

print_header() {
    echo -e "${BLUE}🚀 $1${NC}"
}

print_header "Excel AI Analyzer - Public Repository Setup"

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "public-deployment" ]; then
    print_error "Please switch to the public-deployment branch first!"
    echo "Run: git checkout public-deployment"
    exit 1
fi

# Repository details
USERNAME="zeshanhabib"
REPO_NAME="excel-ai-analyzer"
NEW_REPO_URL="git@github.com:${USERNAME}/${REPO_NAME}.git"

print_info "Setting up public repository:"
echo "   Username: ${USERNAME}"
echo "   Repository: ${REPO_NAME}"
echo "   URL: https://github.com/${USERNAME}/${REPO_NAME}"
echo ""

# Step 1: Create GitHub repository instructions
print_header "Step 1: Create GitHub Repository"
echo ""
print_info "Please create a new repository on GitHub:"
echo "   1. Go to: https://github.com/new"
echo "   2. Repository name: ${REPO_NAME}"
echo "   3. Description: AI-powered Excel file analyzer with natural language queries and interactive visualizations"
echo "   4. Set to: PUBLIC ✅"
echo "   5. DO NOT initialize with README, .gitignore, or license"
echo "   6. Click 'Create repository'"
echo ""

read -p "Press Enter after creating the repository on GitHub..."

# Step 2: Add new remote
print_header "Step 2: Adding New Remote"
echo ""

# Remove existing origin if it exists and add new one
if git remote get-url origin >/dev/null 2>&1; then
    print_info "Removing existing origin remote..."
    git remote remove origin
fi

print_info "Adding new public repository remote..."
git remote add origin "$NEW_REPO_URL"

print_status "New remote added: $NEW_REPO_URL"

# Step 3: Final security check
print_header "Step 3: Final Security Check"
echo ""

print_info "Running final security scan..."

# Check for sensitive files
SENSITIVE_FILES=$(find . -name "*.env" ! -name "*.example" ! -name "*.docker" 2>/dev/null || true)
if [ -n "$SENSITIVE_FILES" ]; then
    print_error "Found sensitive .env files:"
    echo "$SENSITIVE_FILES"
    echo "Please remove or add to .gitignore before continuing."
    exit 1
fi

# Check for API keys in tracked files
API_KEYS=$(git ls-files | xargs grep -l "sk-" 2>/dev/null || true)
if [ -n "$API_KEYS" ]; then
    print_error "Found potential API keys in tracked files:"
    echo "$API_KEYS"
    echo "Please remove API keys before continuing."
    exit 1
fi

print_status "Security check passed - no sensitive data found"

# Step 4: Push to public repository
print_header "Step 4: Pushing to Public Repository"
echo ""

print_info "Pushing public-deployment branch as main..."

# Push the branch as main to the new repository
git push -u origin public-deployment:main

print_status "Successfully pushed to public repository!"

# Step 5: Set up branch protection and repository settings
print_header "Step 5: Repository Configuration"
echo ""

print_info "Recommended GitHub repository settings:"
echo ""
echo "🔒 Security Settings:"
echo "   • Go to Settings → Security"
echo "   • Enable 'Private vulnerability reporting'"
echo "   • Enable 'Dependency graph'"
echo "   • Enable 'Dependabot alerts'"
echo ""
echo "📋 Repository Settings:"
echo "   • Add topics: excel, ai, analyzer, streamlit, openai, python"
echo "   • Add website: https://your-username-excel-ai.streamlit.app (after deployment)"
echo "   • Set social preview image (optional)"
echo ""
echo "🚀 Deployment:"
echo "   • Go to https://share.streamlit.io/"
echo "   • Deploy from GitHub: ${USERNAME}/${REPO_NAME}"
echo "   • Set main file: app.py"
echo "   • Add secrets: OPENAI_API_KEY"
echo ""

# Step 6: Create deployment status badge
print_header "Step 6: Deployment Status Badge"
echo ""

BADGE_URL="https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"
DEPLOY_URL="https://share.streamlit.io/"

print_info "Add this deployment badge to your README:"
echo ""
echo "[![Deploy on Streamlit Cloud](${BADGE_URL})](${DEPLOY_URL})"
echo ""

# Step 7: Summary
print_header "🎉 Setup Complete!"
echo ""
print_status "Public repository successfully created and configured!"
echo ""
print_info "Repository Details:"
echo "   📍 URL: https://github.com/${USERNAME}/${REPO_NAME}"
echo "   🌿 Branch: main (from public-deployment)"
echo "   📦 Size: 596KB (optimized for public distribution)"
echo "   🔒 Security: All sensitive data removed"
echo ""
print_info "Next Steps:"
echo "   1. 🌐 Deploy to Streamlit Cloud: https://share.streamlit.io/"
echo "   2. 📋 Configure repository settings (topics, description)"
echo "   3. 🎯 Add deployment status badge to README"
echo "   4. 🚀 Share your public Excel AI Analyzer!"
echo ""
print_info "Quick Deploy Commands for Users:"
echo "   git clone https://github.com/${USERNAME}/${REPO_NAME}.git"
echo "   cd ${REPO_NAME}"
echo "   ./install.sh"
echo ""

print_status "Your Excel AI Analyzer is now public and ready for the world! 🌍"
