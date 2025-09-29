# AgenticAI Access Management - Quick Reference Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [MCP Server Management](#mcp-server-management)
3. [Agent Management](#agent-management)
4. [User Access Control](#user-access-control)
5. [Configuration Management](#configuration-management)
6. [Security Operations](#security-operations)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

## Getting Started

### Prerequisites

```bash
# Required Python packages
pip install -r requirements.txt

# Environment variables (required)
export PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project"
export MODEL_ENDPOINT="https://your-model.services.ai.azure.com"
export MODEL_API_KEY="your-api-key"
export MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
export APPLICATION_INSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key"
```

### Quick Start

```bash
# Start MCP Server Dashboard
streamlit run stmcplist.py

# Start Agent Dashboard
streamlit run stagentlist.py

# Access via browser
# http://localhost:8501
```

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `mcplist.json` | MCP servers and user access | Root directory |
| `agentlist.json` | Agents and user access | Root directory |
| `.env` | Environment variables | Root directory |

## MCP Server Management

### Dashboard Access

1. **User Dashboard**: View accessible MCP servers
2. **Admin Dashboard**: Manage servers and user access

### Server Configuration

#### Basic Server Properties

```json
{
  "id": 1,
  "name": "Production MCP Server",
  "certified": true,
  "expiration_date": "2025-12-31",
  "company_name": "TechCorp",
  "business_unit": "Engineering",
  "cost_center": "CC001",
  "purpose": "Production"
}
```

#### Authentication Setup

```json
{
  "auth": {
    "username": "mcp_user",
    "api_key": "secure_api_key_here"
  }
}
```

#### Server Instructions

```json
{
  "instructions": "Use VPN for access. Monitor logs daily.",
  "prompt": "You are a helpful assistant for data analysis."
}
```

### Common Server Operations

#### Add New Server

1. Go to Admin Dashboard
2. Select "Add New Server" (if available) or edit existing
3. Fill required fields:
   - Name (required)
   - Authentication credentials
   - Expiration date
   - Business unit and purpose
4. Save changes

#### Update Server Access

1. Select server in Admin Dashboard
2. Use "Users with Access" multiselect
3. Add/remove users as needed
4. Click "Save Changes"

#### Server Status Check

```python
# Check server expiration
from datetime import datetime
current_date = datetime.utcnow().date()
is_expired = server['expiration_date'] < current_date.strftime('%Y-%m-%d')
```

### Server Filtering

| Filter Type | Options |
|------------|---------|
| Certification | Yes, No |
| Purpose | Development, Testing, Production, Analytics |
| Business Unit | Engineering, Finance, HR, etc. |

## Agent Management

### Dashboard Access

1. **User Dashboard**: View accessible agents with filtering
2. **Admin Dashboard**: Complete agent lifecycle management

### Agent Configuration

#### Basic Agent Properties

```json
{
  "id": 1,
  "name": "Customer Support Agent",
  "business_unit": "Support",
  "purpose": "Customer Support",
  "owner": "TechCorp",
  "certified": true,
  "expiration_date": "2025-06-30"
}
```

#### Agent Instructions and Prompts

```json
{
  "instructions": "Handle customer queries efficiently and escalate complex issues.",
  "prompt": "You are a helpful customer support agent. Be polite and professional."
}
```

#### Agent Parameters

```json
{
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 150,
    "model": "gpt-4",
    "top_p": 0.9,
    "custom_setting": "value"
  }
}
```

#### Authentication Methods

##### API Key Authentication
```json
{
  "auth": {
    "method": "api_key",
    "credentials": {
      "api_key": "agent_api_123456"
    }
  }
}
```

##### OAuth2 Authentication
```json
{
  "auth": {
    "method": "oauth2",
    "credentials": {
      "token": "oauth_token_654321"
    }
  }
}
```

##### Basic Authentication
```json
{
  "auth": {
    "method": "basic_auth",
    "credentials": {
      "username": "agent_user",
      "password": "secure_password"
    }
  }
}
```

##### JWT Authentication
```json
{
  "auth": {
    "method": "jwt",
    "credentials": {
      "token": "jwt_token_789012"
    }
  }
}
```

### Agent Operations

#### Create/Update Agent

1. Navigate to Admin Dashboard
2. Select agent or create new
3. Configure metadata:
   - Name, business unit, owner
   - Purpose and certification status
   - Expiration date
4. Set up authentication method
5. Configure parameters (JSON format)
6. Assign user access
7. Save changes

#### Parameter Management

```python
# Valid parameter example
{
  "temperature": 0.7,        # 0.0 to 2.0
  "max_tokens": 150,         # Positive integer
  "model": "gpt-4",          # Model identifier
  "top_p": 0.9,              # 0.0 to 1.0
  "frequency_penalty": 0.0,  # -2.0 to 2.0
  "presence_penalty": 0.0    # -2.0 to 2.0
}
```

#### User Access Management

1. In Admin Dashboard, select agent
2. Use "Users with Access" multiselect
3. View access matrix in expanded section
4. Save changes to apply immediately

### Agent Filtering

| Filter | Options |
|--------|---------|
| Purpose | Customer Support, Code Review, Data Analysis, etc. |
| Certification | All, Yes, No |
| Business Unit | Support, Engineering, Finance, HR, etc. |
| Owner | TechCorp, DataFlow, SecureSys, etc. |

## User Access Control

### User Management

#### User Data Structure

```json
{
  "id": 1,
  "username": "john_doe",
  "password": "hashed_password",
  "access_servers": [1, 5, 10],    // MCP server IDs
  "access_agents": [2, 7, 12, 15]  // Agent IDs
}
```

### Access Control Operations

#### Grant Server Access

```python
# Add server ID to user's access_servers list
user['access_servers'].append(server_id)
```

#### Revoke Server Access

```python
# Remove server ID from user's access_servers list
user['access_servers'] = [sid for sid in user['access_servers'] if sid != server_id]
```

#### Grant Agent Access

```python
# Add agent ID to user's access_agents list
user['access_agents'].append(str(agent_id))  # Ensure string type
```

#### Revoke Agent Access

```python
# Remove agent ID from user's access_agents list
user['access_agents'] = [aid for aid in user['access_agents'] if aid != str(agent_id)]
```

### Access Validation

#### Check Server Access

```python
def has_server_access(user, server_id):
    return server_id in user.get('access_servers', [])
```

#### Check Agent Access

```python
def has_agent_access(user, agent_id):
    agent_id_str = str(agent_id)
    return agent_id_str in [str(aid) for aid in user.get('access_agents', [])]
```

## Configuration Management

### Environment Configuration

#### Required Variables

```bash
# Azure AI Services
PROJECT_ENDPOINT="https://account.services.ai.azure.com/api/projects/project"
MODEL_ENDPOINT="https://account.services.ai.azure.com"
MODEL_API_KEY="your-api-key"
MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

# MCP Configuration
MCP_SERVER_URL="https://learn.microsoft.com/api/mcp"
MCP_SERVER_LABEL="MicrosoftLearn"

# Monitoring
APPLICATION_INSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key"

# OpenAI (if different from MODEL_)
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
AZURE_OPENAI_KEY="your-openai-key"
```

### Data Configuration

#### MCP List Structure

```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "password": "hashed_password",
      "access_servers": [1, 2, 3]
    }
  ],
  "mcp_servers": [
    {
      "id": 1,
      "name": "Production Server",
      "auth": {
        "username": "user",
        "api_key": "key"
      },
      "certified": true,
      "expiration_date": "2025-12-31"
    }
  ]
}
```

#### Agent List Structure

```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "password": "hashed_password",
      "access_agents": ["1", "2", "3"]
    }
  ],
  "agents": [
    {
      "id": 1,
      "name": "Support Agent",
      "business_unit": "Support",
      "purpose": "Customer Support",
      "auth": {
        "method": "api_key",
        "credentials": {
          "api_key": "agent_key"
        }
      },
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 150
      }
    }
  ]
}
```

### Configuration Validation

#### JSON Schema Validation

```python
def validate_config_file(file_path, schema):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate against schema
        jsonschema.validate(data, schema)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except jsonschema.ValidationError as e:
        return False, f"Schema validation failed: {e}"
```

#### Environment Validation

```python
def validate_environment():
    required_vars = [
        'PROJECT_ENDPOINT',
        'MODEL_API_KEY',
        'MODEL_DEPLOYMENT_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ConfigurationError(f"Missing environment variables: {missing_vars}")
```

## Security Operations

### Authentication Management

#### Session Security

```python
# Session timeout configuration
SESSION_TIMEOUT = 3600  # 1 hour

# Session validation
def is_session_valid(session):
    return (time.time() - session.get('created_at', 0)) < SESSION_TIMEOUT
```

#### Credential Management

```python
# Secure credential storage
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Access Logging

#### Security Events

```python
def log_security_event(event_type, user_id, details):
    security_log.info({
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.utcnow(),
        'details': details
    })

# Usage examples
log_security_event('login_attempt', user_id, {'success': True, 'ip': request.remote_addr})
log_security_event('access_denied', user_id, {'resource': 'server_5', 'reason': 'expired'})
log_security_event('admin_action', admin_id, {'action': 'grant_access', 'target': 'user_10'})
```

### Audit Trail

#### Access Audit

```python
def audit_access_change(admin_id, user_id, resource_type, resource_id, action):
    audit_log.info({
        'event': 'access_change',
        'admin_id': admin_id,
        'user_id': user_id,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'action': action,  # 'grant' or 'revoke'
        'timestamp': datetime.utcnow()
    })
```

## Troubleshooting

### Common Issues

#### 1. Configuration File Errors

**Problem**: JSON parsing errors

**Solutions**:
```bash
# Validate JSON syntax
python -m json.tool mcplist.json
python -m json.tool agentlist.json

# Check file permissions
chmod 644 mcplist.json agentlist.json
```

#### 2. Authentication Failures

**Problem**: Azure authentication errors

**Solutions**:
```bash
# Check Azure CLI login
az login

# Verify environment variables
echo $PROJECT_ENDPOINT
echo $MODEL_API_KEY

# Test Azure connection
az account show
```

#### 3. Cache Issues

**Problem**: Stale data in interface

**Solutions**:
```python
# Clear Streamlit cache
import streamlit as st
st.cache_data.clear()

# Restart application
# Ctrl+C and restart streamlit
```

#### 4. Permission Errors

**Problem**: User cannot access resources

**Check**:
- User ID exists in users list
- Resource ID exists in user's access list
- Resource is not expired
- Resource is certified (if required)

### Debug Mode

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"User access servers: {user.get('access_servers', [])}")
print(f"Available servers: {[s['id'] for s in servers]}")
```

#### Streamlit Debug

```python
# Show debug information in UI
with st.expander("Debug Information"):
    st.write("Session State:", st.session_state)
    st.write("User Data:", selected_user)
    st.write("Available Resources:", accessible_resources)
```

### Performance Issues

#### Memory Usage

```python
# Monitor memory usage
import psutil
process = psutil.Process()
memory_usage = process.memory_info().rss / 1024 / 1024  # MB
st.write(f"Memory usage: {memory_usage:.2f} MB")
```

#### Query Performance

```python
# Time operations
import time

start_time = time.time()
result = expensive_operation()
duration = time.time() - start_time
st.write(f"Operation took {duration:.2f} seconds")
```

## API Reference

### Core Functions

#### Data Management

```python
# Load data from JSON files
@st.cache_data
def load_data():
    """Load users and servers/agents from JSON files"""
    pass

# Save data to JSON files
def save_data(users, resources, file_path):
    """Save updated data back to JSON file"""
    pass

# Get resource by ID
def get_resource_by_id(resources, resource_id):
    """Find resource by ID (type-safe)"""
    pass
```

#### Access Control

```python
# Update user access for resource
def update_user_access_for_resource(resource_id, usernames, users, resource_type):
    """Update user access lists for resource"""
    pass

# Check user access
def check_user_access(user, resource_id, resource_type):
    """Check if user has access to resource"""
    pass

# Get user accessible resources
def get_user_accessible_resources(user, resources, resource_type):
    """Get all resources accessible to user"""
    pass
```

#### Validation

```python
# Validate JSON configuration
def validate_json_config(data, schema):
    """Validate JSON data against schema"""
    pass

# Validate agent parameters
def validate_agent_parameters(parameters):
    """Validate agent parameter configuration"""
    pass

# Validate authentication config
def validate_auth_config(auth_config):
    """Validate authentication configuration"""
    pass
```

### UI Components

```python
# Render filter interface
def render_filter_interface(resources):
    """Render dynamic filter controls"""
    pass

# Render resource list
def render_resource_list(resources, filters):
    """Render filtered resource list"""
    pass

# Render admin form
def render_admin_form(resource, users):
    """Render resource editing form"""
    pass
```

### Utility Functions

```python
# Format date for display
def format_date(date_string):
    """Format date string for UI display"""
    pass

# Check expiration status
def is_expired(expiration_date):
    """Check if resource is expired"""
    pass

# Generate secure random string
def generate_secure_token(length=32):
    """Generate secure random token"""
    pass
```

---

## Quick Commands Cheat Sheet

### Application Management

```bash
# Start MCP Dashboard
streamlit run stmcplist.py --server.port 8501

# Start Agent Dashboard  
streamlit run stagentlist.py --server.port 8502

# Run both simultaneously
streamlit run stmcplist.py --server.port 8501 &
streamlit run stagentlist.py --server.port 8502 &
```

### Configuration

```bash
# Validate JSON configuration
python -c "import json; json.load(open('mcplist.json'))"
python -c "import json; json.load(open('agentlist.json'))"

# Backup configuration
cp mcplist.json mcplist.json.backup
cp agentlist.json agentlist.json.backup

# Restore configuration
cp mcplist.json.backup mcplist.json
cp agentlist.json.backup agentlist.json
```

### Monitoring

```bash
# Check application logs
tail -f logs/agenticai.log

# Monitor system resources
htop
iostat 1

# Check network connections
netstat -tlnp | grep :8501
netstat -tlnp | grep :8502
```

This quick reference guide provides essential information for day-to-day operations and troubleshooting of the AgenticAI Access Management system.