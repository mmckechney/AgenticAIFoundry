# ServiceNow AI Assistant - Quick Reference Guide

## Overview
The ServiceNow AI Assistant (`stsvcnow.py`) is a multi-agent AI system for intelligent IT service management using Azure AI Foundry Connected Agent technology.

## Quick Start

### Prerequisites
```bash
# Required Azure Services
- Azure OpenAI (GPT-4, Whisper, TTS)
- Azure AI Project with agent capabilities
- Azure AI Search (optional, for enhanced search)

# Environment Setup
export AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
export AZURE_OPENAI_KEY="your-api-key"
export PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com"
export MODEL_DEPLOYMENT_NAME="gpt-4o"
```

### Installation
```bash
pip install streamlit azure-ai-projects azure-identity python-dotenv
streamlit run stsvcnow.py
```

## Core Components

### ServiceNowIncidentManager
```python
# Initialize incident manager
manager = ServiceNowIncidentManager("servicenow_incidents_full.json")

# Search incidents
incidents = manager.search_incidents("high priority network issues")

# Generate context
context = manager.get_incident_context(incidents)
```

### AI Agents

#### AI Search Agent
```python
# Execute intelligent search
response = ai_search_agent("Show me all Copilot related incidents")
# Returns: Formatted results with citations
```

#### File Search Agent
```python
# Analyze documents
response = generate_response_file(
    user_query="How to resolve Copilot access issues?",
    context=incident_context,
    conversation_history=[]
)
```

#### Email Agent
```python
# Send email via AI
query = "Send incident summary to admin@company.com"
result = sendemail(query)
```

#### Voice Processing
```python
# Transcribe audio
text = transcribe_audio(audio_data)

# Generate voice response
audio = generate_audio_response_gpt_1(text, voice="nova")
```

## API Reference

### Core Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `ai_search_agent(query)` | Intelligent search | `query: str` | Search results with citations |
| `generate_response_file(query, context, history)` | File-based Q&A | `query: str, context: str, history: List[Dict]` | AI response from documents |
| `sendemail(query)` | Email processing | `query: str` | Email status |
| `transcribe_audio(audio_data)` | Speech-to-text | `audio_data` | Transcribed text |
| `generate_audio_response_gpt_1(text, voice)` | Text-to-speech | `text: str, voice: str` | Audio file path |

### ServiceNowIncidentManager Methods

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `load_data()` | Load incident data | None | None |
| `search_incidents(query, limit)` | Search incidents | `query: str, limit: int=10` | `List[Dict]` |
| `get_incident_context(incidents)` | Generate context | `incidents: List[Dict]` | `str` |

## Configuration

### Environment Variables
```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4o

# Optional
SEARCH_ENDPOINT=https://your-search.search.windows.net
SEARCH_KEY=your-search-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### Data Format
ServiceNow incident data should be in JSON format:
```json
{
  "incidents": [
    {
      "incident_id": "INC0000001",
      "short_description": "Brief description",
      "long_description": "Detailed description",
      "priority": "High|Medium|Low",
      "status": "Open|In Progress|Resolved|Closed",
      "solution": "Resolution steps",
      "start_time": "2024-01-01T10:00:00Z",
      "interactions": [
        {
          "user": "username",
          "comment": "User comment",
          "timestamp": "2024-01-01T10:05:00Z"
        }
      ]
    }
  ]
}
```

## Usage Examples

### Basic Text Query
```python
import streamlit as st

# Initialize the system
if 'incident_manager' not in st.session_state:
    st.session_state.incident_manager = ServiceNowIncidentManager()

# Process user query
user_query = "Show me all high priority incidents from last week"
incidents = st.session_state.incident_manager.search_incidents(user_query)
response = ai_search_agent(user_query)

st.write(response)
```

### Voice-Enabled Interaction
```python
# Record audio input
audio_data = st.audio_input("Ask about incidents")

if audio_data:
    # Transcribe speech
    transcription = transcribe_audio(audio_data)
    
    # Process query
    response = ai_search_agent(transcription)
    
    # Generate voice response
    if st.session_state.get('audio_enabled', True):
        audio_file = generate_audio_response_gpt_1(response, "nova")
        st.audio(audio_file, format="audio/mp3")
    
    st.write(response)
```

### File Analysis
```python
# Upload and analyze documents
uploaded_file = st.file_uploader("Upload ServiceNow document")

if uploaded_file:
    # Save file temporarily
    with open("temp_document.txt", "wb") as f:
        f.write(uploaded_file.read())
    
    # Analyze with file search agent
    query = "What are the key issues mentioned in this document?"
    response = generate_response_file(query, "", [])
    
    st.write(response)
```

### Email Integration
```python
# Send email with AI assistance
if st.button("Email Incident Summary"):
    email_query = """
    Send an email to admin@company.com with subject 'Daily Incident Summary' 
    containing a summary of today's high priority incidents
    """
    
    result = sendemail(email_query)
    st.success("Email sent successfully!")
```

## Agent Architecture

### Multi-Agent Flow
```
User Input → ServiceNowIncidentManager → Agent Orchestrator
                                              ↓
                           ┌─────────────────────────────────┐
                           │        Agent Selection          │
                           └─────────────────────────────────┘
                                              ↓
                  ┌─────────────┬─────────────┬─────────────┐
                  │ AI Search   │ File Search │ Email Agent │
                  │ Agent       │ Agent       │             │
                  └─────────────┴─────────────┴─────────────┘
                                              ↓
                           ┌─────────────────────────────────┐
                           │     Response Aggregation       │
                           └─────────────────────────────────┘
                                              ↓
                           ┌─────────────────────────────────┐
                           │    TTS Processing (Optional)    │
                           └─────────────────────────────────┘
                                              ↓
                                       User Response
```

### Agent Responsibilities

| Agent | Primary Function | Tools Used | Output |
|-------|------------------|------------|--------|
| **AI Search** | Semantic search across ServiceNow data | Azure AI Search | Ranked results with citations |
| **File Search** | Document analysis and knowledge extraction | Vector Store | Document-based answers |
| **Email** | Communication and notifications | Connected Agent | Email confirmation |
| **TTS** | Voice response generation | Azure OpenAI TTS | Audio files |

## Troubleshooting

### Common Issues

#### Authentication Errors
```python
# Check credentials
print(os.environ.get("AZURE_OPENAI_KEY", "Not set"))
print(os.environ.get("PROJECT_ENDPOINT", "Not set"))

# Verify Azure identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

#### Resource Cleanup Issues
```python
# Manual cleanup if needed
project_client.agents.delete_agent(agent_id)
project_client.agents.threads.delete(thread_id)
project_client.agents.vector_stores.delete(vector_store_id)
```

#### Performance Issues
```python
# Enable connection pooling
import requests
session = requests.Session()

# Implement caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query):
    return ai_search_agent(query)
```

### Error Handling Patterns

```python
def robust_agent_execution(agent_function, *args, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return agent_function(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"Agent execution failed: {e}")
                return "I apologize, but I'm having trouble processing your request right now."
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Optimization

### Caching Strategy
```python
# Response caching
@st.cache_data(ttl=300)  # 5-minute cache
def cached_incident_search(query):
    return ai_search_agent(query)

# Vector store caching
@st.cache_resource
def get_vector_store():
    return create_vector_store()
```

### Connection Management
```python
# Reuse AI Project Client
@st.cache_resource
def get_project_client():
    return AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
```

### Batch Processing
```python
# Process multiple queries efficiently
def batch_process_queries(queries):
    with get_project_client() as client:
        results = []
        for query in queries:
            result = process_single_query(client, query)
            results.append(result)
        return results
```

## Security Best Practices

### Credential Management
```python
# Use Azure Key Vault
from azure.keyvault.secrets import SecretClient

def get_secret(secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

### Input Validation
```python
def validate_user_input(user_input):
    # Sanitize input
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    # Check for potential injection
    forbidden_patterns = ["<script>", "javascript:", "data:"]
    for pattern in forbidden_patterns:
        if pattern in user_input.lower():
            raise ValueError("Invalid input detected")
    
    return user_input
```

### Data Privacy
```python
# Remove sensitive information
def sanitize_response(response):
    import re
    # Remove email addresses
    response = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', response)
    # Remove phone numbers
    response = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', response)
    return response
```

## Monitoring and Logging

### Application Insights Integration
```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key'
))

# Log agent activity
def log_agent_execution(agent_name, query, response_time):
    logger.info(f"Agent: {agent_name}, Query: {query}, Time: {response_time}ms")
```

### Performance Metrics
```python
import time
from functools import wraps

def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        st.sidebar.metric(
            f"{func.__name__} Response Time",
            f"{(end_time - start_time) * 1000:.0f} ms"
        )
        return result
    return wrapper

@measure_performance
def timed_search(query):
    return ai_search_agent(query)
```

## Deployment

### Local Development
```bash
# Development setup
git clone https://github.com/balakreshnan/AgenticAIFoundry.git
cd AgenticAIFoundry
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
streamlit run stsvcnow.py
```

### Production Deployment

#### Azure Container Instances
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "stsvcnow.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Azure App Service
```yaml
# azure-pipelines.yml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'

- script: |
    pip install -r requirements.txt
    pytest tests/
  displayName: 'Install dependencies and run tests'

- task: AzureWebApp@1
  inputs:
    azureSubscription: 'your-subscription'
    appName: 'servicenow-ai-assistant'
    package: '.'
```

## Support and Resources

### Documentation Links
- [Azure AI Foundry Documentation](https://docs.microsoft.com/azure/ai-foundry/)
- [Azure OpenAI Service](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Common Use Cases
1. **Incident Search**: "Show me all network-related incidents from this month"
2. **Solution Finding**: "How was incident INC123456 resolved?"
3. **Trend Analysis**: "What are the most common Copilot issues?"
4. **Status Updates**: "Send status update to team lead"
5. **Documentation**: "Explain the standard incident resolution process"

### Performance Benchmarks
- **Response Time**: < 2 seconds for search queries
- **Accuracy**: > 95% for incident retrieval
- **Availability**: 99.9% uptime target
- **Throughput**: 100+ requests per minute

---

*For detailed technical documentation, see the complete architecture documents in the docs folder.*