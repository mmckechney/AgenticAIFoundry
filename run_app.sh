#!/bin/bash

# AgenticAI Foundry Streamlit App Launcher
# This script launches the Streamlit web application

echo "🤖 Starting AgenticAI Foundry Web Application..."
echo "================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Please create one from .env.example"
    echo "   Copy .env.example to .env and fill in your configuration values."
    echo ""
fi

# Check if virtual environment should be activated
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Launch Streamlit app
echo "🚀 Launching web application..."
echo "   Open your browser to: http://localhost:8501"
echo "   Press Ctrl+C to stop the application"
echo ""

streamlit run app.py --server.port 8501 --server.address 0.0.0.0