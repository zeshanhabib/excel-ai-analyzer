#!/bin/bash

# Excel AI Analyzer - Quick Deployment Guide
# ==========================================

echo "🚀 Excel AI Analyzer - Quick Deployment"
echo "========================================"

# Check if running in correct directory
if [[ ! -f "app.py" ]]; then
    echo "❌ Error: Run this script from the excel_ai project directory"
    exit 1
fi

echo "📋 Deployment Options:"
echo "1. Local Development (Recommended for testing)"
echo "2. Docker Deployment (Recommended for production)"
echo "3. Show current status"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🔧 Starting Local Development Deployment..."
        
        # Check if virtual environment exists
        if [[ ! -d ".venv" ]]; then
            echo "📦 Creating virtual environment..."
            python -m venv .venv
        fi
        
        # Activate virtual environment
        echo "🔌 Activating virtual environment..."
        source .venv/bin/activate
        
        # Install dependencies
        echo "📥 Installing dependencies..."
        pip install -r requirements.txt
        
        # Create environment file if it doesn't exist
        if [[ ! -f ".env" ]]; then
            echo "⚙️ Creating environment file..."
            cp .env.example .env
            echo "📝 Please edit .env file to add your OpenAI API key"
        fi
        
        # Generate sample data
        echo "📊 Generating sample data..."
        python create_sample_data.py
        
        # Run tests
        echo "🧪 Running tests..."
        python test_app.py
        
        if [[ $? -eq 0 ]]; then
            echo "✅ All tests passed!"
            echo "🌐 Starting application..."
            echo ""
            echo "🎯 Application will be available at: http://localhost:8501"
            echo "🛑 Press Ctrl+C to stop the application"
            echo ""
            streamlit run app.py
        else
            echo "❌ Tests failed. Please check the output above."
            exit 1
        fi
        ;;
        
    2)
        echo "🐳 Starting Docker Deployment..."
        
        # Check if Docker is running
        if ! docker info &>/dev/null; then
            echo "❌ Docker is not running. Please start Docker first."
            exit 1
        fi
        
        # Create environment file if it doesn't exist
        if [[ ! -f ".env" ]]; then
            echo "⚙️ Creating environment file..."
            cp .env.docker .env
            echo "📝 Please edit .env file to add your API keys"
            echo "⚠️  At minimum, set your OPENAI_API_KEY"
            exit 1
        fi
        
        # Start with Docker
        echo "🔨 Building and starting Docker services..."
        ./docker-start.sh
        ;;
        
    3)
        echo "📊 Current Status Check..."
        
        # Check if Streamlit is running
        if pgrep -f "streamlit" &>/dev/null; then
            echo "🟢 Streamlit is currently running"
            echo "🌐 Application URL: http://localhost:8501"
        else
            echo "🔴 Streamlit is not running"
        fi
        
        # Check if Docker containers are running
        if docker ps | grep -q "excel-ai"; then
            echo "🟢 Docker containers are running"
            docker ps | grep excel-ai
        else
            echo "🔴 No Docker containers running"
        fi
        
        # Check environment setup
        if [[ -f ".env" ]]; then
            echo "🟢 Environment file exists"
            if grep -q "your_openai_api_key_here" .env; then
                echo "⚠️  OpenAI API key not configured"
            else
                echo "🟢 OpenAI API key configured"
            fi
        else
            echo "🔴 Environment file missing"
        fi
        
        # Check sample data
        if [[ -d "sample_data" && $(ls sample_data/*.xlsx 2>/dev/null | wc -l) -gt 0 ]]; then
            echo "🟢 Sample data available ($(ls sample_data/*.xlsx | wc -l) files)"
        else
            echo "🔴 Sample data missing"
        fi
        ;;
        
    *)
        echo "❌ Invalid option. Please choose 1, 2, or 3."
        exit 1
        ;;
esac
