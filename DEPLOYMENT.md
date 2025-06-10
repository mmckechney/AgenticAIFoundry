# Azure Web App Deployment Guide

This guide explains how to deploy the AgenticAI Foundry application to Azure Web App using the provided GitHub Actions workflow.

## Prerequisites

1. **Azure Subscription**: Active Azure subscription with permissions to create and manage Web Apps
2. **Azure Web App**: Python 3.12 web app created in Azure
3. **GitHub Repository**: This repository with appropriate secrets configured

## Setup Instructions

### 1. Create Azure Web App

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Create a new Web App with the following settings:
   - **Runtime stack**: Python 3.12
   - **Operating System**: Linux
   - **Region**: Choose your preferred region
   - **App Service Plan**: Choose appropriate size based on your needs

### 2. Configure GitHub Secrets

Add the following secret to your GitHub repository:

- `AZUREAPPSERVICE_PUBLISHPROFILE`: 
  1. In Azure Portal, go to your Web App
  2. Click "Get publish profile" and download the file
  3. Copy the entire contents of the downloaded file
  4. Add it as a GitHub secret with the name `AZUREAPPSERVICE_PUBLISHPROFILE`

### 3. Update Workflow Configuration

Edit `.github/workflows/azure-webapp-deploy.yml` and update:

```yaml
env:
  AZURE_WEBAPP_NAME: your-webapp-name    # Replace with your actual Web App name
```

### 4. Configure Environment Variables in Azure

In your Azure Web App, go to Configuration > Application settings and add the required environment variables:

**Required:**
- `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME`: AI model deployment name (e.g., gpt-4o-mini)
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_KEY`: Azure OpenAI API key

**Optional (for full functionality):**
- `AZURE_SEARCH_ENDPOINT`: For AI search functionality
- `AZURE_SEARCH_KEY`: Search service authentication
- `GOOGLE_EMAIL`: For email functionality
- `GOOGLE_APP_PASSWORD`: Gmail app password

See `.env.example` for the complete list of environment variables.

## Deployment Process

### Automatic Deployment

The workflow automatically triggers on:
- Push to the `main` branch
- Manual trigger via GitHub Actions UI

### Manual Deployment

To manually trigger deployment:
1. Go to GitHub Actions tab in your repository
2. Select "Deploy to Azure Web App" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Application Configuration

The application will automatically:
- Detect the Azure Web App environment
- Use the PORT environment variable set by Azure
- Configure Streamlit for cloud deployment
- Fall back to demo mode if Azure AI dependencies are not properly configured

## Monitoring and Troubleshooting

### Viewing Logs

1. In Azure Portal, go to your Web App
2. Navigate to "Log stream" to view real-time logs
3. Check "App Service logs" for detailed application logs

### Common Issues

1. **Startup Issues**: Check that all required environment variables are set
2. **Dependency Issues**: Verify Python version and requirements.txt
3. **Port Issues**: The application automatically detects Azure's PORT variable
4. **Demo Mode**: App runs in demo mode if Azure AI services are not properly configured

### Health Check

The application includes automatic fallback to demo mode, so it will start even if some Azure AI dependencies are missing.

## Security Considerations

- Store sensitive credentials in Azure Web App configuration, not in code
- Use Azure Managed Identity when possible
- Regularly update dependencies
- Monitor for security vulnerabilities

## Cost Optimization

- Choose appropriate App Service Plan size
- Consider scaling rules based on usage
- Monitor resource consumption in Azure Portal