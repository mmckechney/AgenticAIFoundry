#!/bin/bash

# Azure Web App startup script for AgenticAI Foundry
# This script configures and launches the Streamlit application in Azure Web App environment

echo "🤖 Starting AgenticAI Foundry on Azure Web App..."
echo "================================================"

# Check if running in Azure Web App (PORT environment variable is set by Azure)
if [ -n "$PORT" ]; then
    echo "🌐 Detected Azure Web App environment, using port: $PORT"
    STREAMLIT_PORT=$PORT
else
    echo "🏠 Local environment detected, using default port: 8501"
    STREAMLIT_PORT=8501
fi

# Install requirements if needed (safety check)
echo "📦 Ensuring dependencies are installed..."
pip install -r requirements.txt

# Launch Streamlit app with Azure Web App compatible settings
echo "🚀 Launching Streamlit application..."
echo "   Application will be available on port: $STREAMLIT_PORT"
echo ""

exec streamlit run streamlit_app.py \
    --server.port $STREAMLIT_PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false