# Azure Function Agent Integration - Quick Reference Guide

## 🚀 Quick Start

### Prerequisites
- Azure AI Foundry project
- Azure Storage account with queue service
- Azure Functions (for actual function execution)
- Python 3.8+ environment

### Installation
```bash
pip install azure-ai-projects azure-ai-agents azure-identity python-dotenv
```

### Environment Setup
```bash
# .env file
PROJECT_ENDPOINT_ENT=https://your-project.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=your-model-deployment
STORAGE_SERVICE_ENDPOINT=https://account.queue.core.windows.net
```

## 📋 Function Reference

### Basic Function Agent
```python
from stazfunctest import azurefunc_test

# Simple usage
response = azurefunc_test("Your question here")
print(response)
```

### Connected Agent Orchestration  
```python
from stazfunctest import connected_azure_function_agent

# Advanced orchestration
response = connected_azure_function_agent("What would foo say?")
print(response)
```

## 🔧 Configuration Patterns

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_ENDPOINT_ENT` | AI Foundry endpoint | `https://project.cognitiveservices.azure.com/` |
| `MODEL_DEPLOYMENT_NAME` | Model deployment | `gpt-4` |
| `STORAGE_SERVICE_ENDPOINT` | Storage queue endpoint | `https://storage.queue.core.windows.net` |

### Function Tool Configuration
```python
AzureFunctionTool(
    name="function_name",
    description="Function purpose",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Input query"}
        }
    },
    input_queue=AzureFunctionStorageQueue(
        queue_name="function-input",
        storage_service_endpoint=endpoint
    ),
    output_queue=AzureFunctionStorageQueue(
        queue_name="function-output", 
        storage_service_endpoint=endpoint
    )
)
```

## 🏗️ Architecture Patterns

### Basic Pattern
```
User → Agent → Function Tool → Azure Function → Response
```

### Connected Agent Pattern
```
User → Orchestrator Agent → Function Agent → Azure Function → Response
```

### Queue-Based Flow
```
Query → Input Queue → Function → Output Queue → Response
```

## 💡 Common Use Cases

### 1. Weather Service Integration
```python
# Query weather through Azure Function
response = azurefunc_test("What's the weather in Seattle?")
```

### 2. Data Processing Pipeline
```python
# Process data through connected agents
response = connected_azure_function_agent("Process this dataset: [data]")
```

### 3. External API Integration
```python
# Integrate with external services via functions
response = azurefunc_test("Get stock price for MSFT")
```

## ⚠️ Error Handling

### Common Errors

#### Missing Environment Variables
```python
# Error: Missing STORAGE_SERVICE_ENDPOINT
# Solution: Set environment variable
os.environ["STORAGE_SERVICE_ENDPOINT"] = "https://storage.queue.core.windows.net"
```

#### Invalid Storage Endpoint
```python
# Error: STORAGE_SERVICE_ENDPOINT looks invalid
# Solution: Use correct format
STORAGE_SERVICE_ENDPOINT=https://account.queue.core.windows.net
```

#### Agent Run Failures
```python
# Check run status
if run.status == "failed":
    print(f"Run failed: {run.last_error}")
```

### Error Handling Best Practices
```python
try:
    response = azurefunc_test(query)
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## 🔍 Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Agent Status
```python
print(f"Agent ID: {agent.id}")
print(f"Thread ID: {thread.id}")
print(f"Run Status: {run.status}")
```

### Check Message Content
```python
for msg in messages:
    print(f"Role: {msg.role}")
    print(f"Content: {msg.content}")
```

## 📊 Performance Tips

### Resource Management
```python
# Always clean up resources
try:
    # Your code here
finally:
    project_client.agents.delete_agent(agent.id)
    project_client.agents.threads.delete(thread.id)
```

### Efficient Message Processing
```python
# Extract text efficiently
text = _extract_text_from_message(message)
if text:
    return text
```

### Connection Reuse
```python
# Reuse client connections
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)
```

## 🎯 Best Practices

### 1. Configuration Management
- Use environment variables for sensitive data
- Validate configuration at startup
- Provide clear error messages

### 2. Error Handling
- Implement comprehensive error handling
- Log errors with context
- Clean up resources in finally blocks

### 3. Resource Management
- Delete agents and threads when done
- Monitor resource usage
- Implement proper lifecycle management

### 4. Security
- Use Azure Identity for authentication
- Validate input parameters
- Secure storage endpoints

### 5. Testing
- Test with various query types
- Validate error scenarios
- Monitor performance metrics

## 📚 Integration Examples

### With Streamlit
```python
import streamlit as st
from stazfunctest import azurefunc_test

st.title("Azure Function Agent")
query = st.text_input("Enter your question:")
if st.button("Ask"):
    response = azurefunc_test(query)
    st.write(response)
```

### With FastAPI
```python
from fastapi import FastAPI
from stazfunctest import connected_azure_function_agent

app = FastAPI()

@app.post("/query")
async def process_query(query: str):
    response = connected_azure_function_agent(query)
    return {"response": response}
```

### Batch Processing
```python
queries = ["Query 1", "Query 2", "Query 3"]
responses = []

for query in queries:
    try:
        response = azurefunc_test(query)
        responses.append({"query": query, "response": response})
    except Exception as e:
        responses.append({"query": query, "error": str(e)})
```

## 📋 Troubleshooting Checklist

### ✅ Environment Setup
- [ ] Azure AI Foundry project configured
- [ ] Storage account with queue service enabled
- [ ] Environment variables set correctly
- [ ] Azure credentials configured

### ✅ Code Configuration
- [ ] Import statements correct
- [ ] Function tool properly configured
- [ ] Queue names match Azure setup
- [ ] Agent instructions are clear

### ✅ Runtime Checks
- [ ] Agent creation successful
- [ ] Thread creation successful
- [ ] Run execution completes
- [ ] Response extraction works
- [ ] Resources cleaned up properly

## 🔗 Related Documentation

- [Technical Architecture](stazfunctest-technical-architecture.md)
- [Mermaid Diagrams](stazfunctest-mermaid-diagrams.md)
- [API Reference](stazfunctest-api-reference.md)

---

*This quick reference provides essential information for using the Azure Function Agent Integration module. For detailed technical information, refer to the complete documentation.*