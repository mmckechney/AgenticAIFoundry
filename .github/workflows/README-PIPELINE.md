# App.py CI/CD Pipeline Setup Guide

## Overview
This GitHub Actions workflow automates the deployment of `app.py` (Streamlit application) to Azure App Service with built-in quality gates including evaluation and red team security testing.

## Pipeline Stages

### 1. **Quality Gates** (Testing Stage)
- Runs `eval()` function from `agenticai.py` to validate model performance
- Runs `redteam()` function to perform security testing
- Both tests must pass before deployment proceeds

### 2. **Build Stage**
- Creates deployment artifact with app.py and dependencies
- Generates Streamlit startup script
- Packages application for Azure App Service

### 3. **UAT Deployment**
- Deploys to UAT environment automatically on `develop` branch push
- Configures UAT-specific environment variables
- Performs health checks

### 4. **Production Deployment**
- Requires UAT deployment success
- Deploys to production on `main` branch push
- Configures production environment variables
- Performs health checks

## Trigger Conditions

### Automatic Triggers
- **Push to `main`**: Runs full pipeline → UAT → Production
- **Push to `develop`**: Runs pipeline → UAT only
- **Pull Request to `main`**: Runs quality gates only (no deployment)

### Manual Trigger
- Use `workflow_dispatch` to manually trigger deployment
- Select target environment (UAT or Production)

## Required GitHub Secrets

### General Secrets (for Testing)
```
PROJECT_ENDPOINT
MODEL_ENDPOINT
MODEL_API_KEY
MODEL_DEPLOYMENT_NAME
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_ENDPOINT_REDTEAM
AZURE_OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT
AZURE_API_VERSION
AZURE_SUBSCRIPTION_ID
AZURE_RESOURCE_GROUP
AZURE_PROJECT_NAME
AZURE_AI_PROJECT
APPLICATION_INSIGHTS_CONNECTION_STRING
```

### UAT Environment Secrets
```
AZURE_CREDENTIALS_UAT                    # Azure Service Principal JSON
PROJECT_ENDPOINT_UAT
MODEL_ENDPOINT_UAT
MODEL_API_KEY_UAT
MODEL_DEPLOYMENT_NAME_UAT
AZURE_OPENAI_ENDPOINT_UAT
AZURE_OPENAI_KEY_UAT
APPLICATION_INSIGHTS_CONNECTION_STRING_UAT
```

### Production Environment Secrets
```
AZURE_CREDENTIALS_PROD                   # Azure Service Principal JSON
PROJECT_ENDPOINT_PROD
MODEL_ENDPOINT_PROD
MODEL_API_KEY_PROD
MODEL_DEPLOYMENT_NAME_PROD
AZURE_OPENAI_ENDPOINT_PROD
AZURE_OPENAI_KEY_PROD
APPLICATION_INSIGHTS_CONNECTION_STRING_PROD
```

## Azure Service Principal Setup

### Create Service Principal for UAT
```bash
az ad sp create-for-rbac \
  --name "github-actions-uat" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{uat-resource-group} \
  --sdk-auth
```

### Create Service Principal for Production
```bash
az ad sp create-for-rbac \
  --name "github-actions-prod" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{prod-resource-group} \
  --sdk-auth
```

Store the JSON output in `AZURE_CREDENTIALS_UAT` and `AZURE_CREDENTIALS_PROD` secrets respectively.

## Azure App Service Setup

### Create UAT App Service
```bash
# Create resource group
az group create --name rg-agenticai-uat --location eastus

# Create App Service Plan (Linux)
az appservice plan create \
  --name asp-agenticai-uat \
  --resource-group rg-agenticai-uat \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --name agenticai-app-uat \
  --resource-group rg-agenticai-uat \
  --plan asp-agenticai-uat \
  --runtime "PYTHON:3.12"

# Configure for Streamlit
az webapp config set \
  --name agenticai-app-uat \
  --resource-group rg-agenticai-uat \
  --startup-file "bash startup.sh"
```

### Create Production App Service
```bash
# Create resource group
az group create --name rg-agenticai-prod --location eastus

# Create App Service Plan (Linux)
az appservice plan create \
  --name asp-agenticai-prod \
  --resource-group rg-agenticai-prod \
  --sku P1V2 \
  --is-linux

# Create Web App
az webapp create \
  --name agenticai-app-prod \
  --resource-group rg-agenticai-prod \
  --plan asp-agenticai-prod \
  --runtime "PYTHON:3.12"

# Configure for Streamlit
az webapp config set \
  --name agenticai-app-prod \
  --resource-group rg-agenticai-prod \
  --startup-file "bash startup.sh"
```

## GitHub Environments Setup

1. Go to **Settings** → **Environments** in your GitHub repository

2. Create **testing** environment (no protection rules needed)

3. Create **UAT** environment:
   - Add reviewers if needed
   - Set deployment branch pattern: `develop`

4. Create **Production** environment:
   - ✅ Required reviewers (recommended)
   - ✅ Wait timer (e.g., 5 minutes)
   - Set deployment branch pattern: `main`

## Workflow Variables

Update these in the workflow file if your app names differ:

```yaml
env:
  PYTHON_VERSION: '3.12'
  AZURE_WEBAPP_NAME_UAT: 'agenticai-app-uat'      # Change to your UAT app name
  AZURE_WEBAPP_NAME_PROD: 'agenticai-app-prod'    # Change to your PROD app name
```

## Testing the Pipeline

### Test Quality Gates Only
```bash
# Create a feature branch
git checkout -b feature/test-pipeline

# Make a change to app.py
echo "# Test change" >> app.py

# Push to trigger PR workflow
git add .
git commit -m "Test: Quality gates"
git push origin feature/test-pipeline

# Create PR to main (will run eval & redteam only)
```

### Test UAT Deployment
```bash
# Push to develop branch
git checkout develop
git merge feature/test-pipeline
git push origin develop

# This will:
# 1. Run quality gates
# 2. Build application
# 3. Deploy to UAT
```

### Test Production Deployment
```bash
# Merge to main
git checkout main
git merge develop
git push origin main

# This will:
# 1. Run quality gates
# 2. Build application
# 3. Deploy to UAT
# 4. Deploy to Production (with approval if configured)
```

### Manual Deployment
1. Go to **Actions** tab in GitHub
2. Select "App.py CI/CD Pipeline with Eval & Red Team"
3. Click "Run workflow"
4. Select branch and environment
5. Click "Run workflow"

## Monitoring

### View Logs
- GitHub Actions: Repository → Actions → Select workflow run
- Azure Portal: App Service → Deployment Center → Logs
- Application Insights: Monitor app performance and errors

### Health Check Endpoints
- **UAT**: `https://agenticai-app-uat.azurewebsites.net`
- **Production**: `https://agenticai-app-prod.azurewebsites.net`

## Troubleshooting

### Quality Gates Failing

**Eval() fails:**
```bash
# Check evaluation configuration
# Ensure all AZURE_OPENAI_* secrets are set correctly
# Verify model deployment is accessible
```

**Redteam() fails:**
```bash
# Check AZURE_OPENAI_ENDPOINT_REDTEAM is set
# Verify AZURE_AI_PROJECT endpoint is correct
# Ensure sufficient permissions for red team testing
```

### Deployment Failures

**Authentication errors:**
```bash
# Verify service principal has correct permissions
# Re-create service principal if expired
# Check AZURE_CREDENTIALS_* secrets are valid JSON
```

**App won't start:**
```bash
# Check startup.sh is executable
# Verify Python version matches (3.12)
# Check requirements.txt is complete
# Review App Service logs in Azure Portal
```

**Missing environment variables:**
```bash
# Verify all *_UAT and *_PROD secrets are set
# Check app-settings-json in workflow file
# Manually verify in Azure Portal → Configuration
```

## File Structure

```
AgenticAIFoundry/
├── .github/
│   └── workflows/
│       └── app-cicd-pipeline.yml      # Main CI/CD workflow
├── app.py                              # Streamlit application
├── agenticai.py                        # Contains eval() and redteam()
├── utils.py                            # Utility functions
├── user_logic_apps.py                  # Logic apps integration
├── requirements.txt                    # Python dependencies
├── data/                               # Application data
├── img/                                # Images/assets
└── startup.sh                          # Generated during build
```

## Best Practices

1. **Never commit secrets** to the repository
2. **Use separate Azure resources** for UAT and Production
3. **Enable Application Insights** for monitoring
4. **Set up alerts** for deployment failures
5. **Review deployment approvals** for production
6. **Keep dependencies updated** in requirements.txt
7. **Test in UAT** before production deployment
8. **Monitor token usage** and costs in Azure Portal

## Cost Optimization

- Use **B2 tier** for UAT (can scale down when not in use)
- Use **P1V2 or higher** for Production (better performance)
- Enable **auto-scaling** based on metrics
- Set up **budget alerts** in Azure

## Security Recommendations

1. Enable **Managed Identity** for Azure resources
2. Use **Azure Key Vault** for sensitive configuration
3. Enable **HTTPS only** in App Service
4. Configure **IP restrictions** if needed
5. Enable **authentication** for production apps
6. Regularly review **red team results**
7. Keep **Python and dependencies updated**

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review Azure App Service logs
3. Check Application Insights for runtime errors
4. Review this documentation

---

**Last Updated**: November 2025
**Pipeline Version**: 1.0
