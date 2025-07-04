#!/bin/bash

# Excel AI Analyzer Startup Script
echo "🚀 Starting Excel AI Analyzer..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, pandas, plotly, openai" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "📦 Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Check if sample data exists
if [ ! -d "sample_data" ]; then
    echo "📊 Creating sample data..."
    python create_sample_data.py
fi

# Set environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | xargs)
    echo "✅ Environment variables loaded from .env"
fi

echo "🌐 Starting Streamlit application..."
echo "📋 The application will open in your browser at: http://localhost:8501"
echo "🔧 Use Ctrl+C to stop the application"
echo ""

# Start Streamlit
streamlit run app.py --server.port 8501 --server.address localhost
