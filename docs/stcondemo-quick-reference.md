# Agent Demo System - Quick Reference Guide

## Overview

Quick reference for the Agent Demo system (`stcondemoui.py` and `stcondemo.py`) - a comparison platform for Single vs Multi-Agent architectures using Azure AI Foundry.

## 🚀 Quick Start

### Prerequisites
- Azure AI Foundry project configured
- Required environment variables set
- Python 3.12+ with dependencies installed

### Launch Application
```bash
streamlit run stcondemoui.py
```

### Basic Usage
1. **Select Mode**: Choose "Single Agent" or "Multi Agent" in sidebar
2. **Enter Query**: Type question in chat input
3. **View Results**: See response in chat area with tool details

## 🔧 Environment Variables

### Required Configuration
```bash
# Azure AI Foundry
PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
MODEL_ENDPOINT=https://<account>.services.ai.azure.com
MODEL_API_KEY=<api_key>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# MCP Configuration
MCP_SERVER_URL=https://learn.microsoft.com/api/mcp
MCP_SERVER_LABEL=MicrosoftLearn

# Azure Resources
AZURE_SUBSCRIPTION_ID=<subscription_id>
AZURE_RESOURCE_GROUP=<resource_group>
```

### Optional Configuration
```bash
# OpenTelemetry Tracing
APPLICATION_INSIGHTS_CONNECTION_STRING=<connection_string>

# Azure OpenAI (for compatibility)
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_KEY=<key>
```

## 📊 Agent Modes Comparison

| Feature | Single Agent | Multi Agent |
|---------|-------------|-------------|
| **Architecture** | Unified agent with multiple tools | Orchestrated specialized agents |
| **Tool Integration** | Direct tool access | Connected agent tools |
| **Execution** | Single execution context | Multi-agent coordination |
| **Use Cases** | Simple to moderate queries | Complex multi-domain queries |
| **Resource Usage** | Lower overhead | Higher resource usage |
| **Response Time** | Faster for simple queries | Better for complex workflows |

## 🛠️ Available Tools & Capabilities

### Single Agent Mode Tools

#### **Function Tools**
- **`get_weather(city)`**: Current weather data via Open-Meteo API
- **`fetch_stock_data(company)`**: Stock prices via Yahoo Finance API

#### **MCP Tools**
- **Microsoft Learn**: Azure documentation and technical guidance
- **Server**: `https://learn.microsoft.com/api/mcp`
- **Usage**: Technical how-to queries, SDK references

### Multi Agent Mode Agents

#### **Stock Agent** (`Stockagent`)
- **Purpose**: Financial data retrieval
- **Tools**: `fetch_stock_data` function
- **Use Cases**: Stock prices, market data

#### **RFP Search Agent** (`AISearchagent`)
- **Purpose**: Construction/proposal document search
- **Tools**: Azure AI Search integration
- **Index**: `constructionrfpdocs1`
- **Use Cases**: Construction management, RFP documents

#### **Sustainability Agent** (`Sustainabilitypaperagent`)
- **Purpose**: Sustainability research analysis
- **Tools**: File search with vector store
- **Resources**: Research papers (PDF documents)
- **Use Cases**: Environmental impact, sustainability frameworks

#### **MCP Learn Agent** (`Mcplearnagent`)
- **Purpose**: Microsoft technical documentation
- **Tools**: Microsoft Learn MCP protocol
- **Use Cases**: Azure documentation, technical guides

#### **Base Agent** (`basaeagent`)
- **Purpose**: Generic information processing
- **Tools**: Basic response generation
- **Use Cases**: General queries, fallback responses

## 💬 Query Examples

### Weather Queries
```
"What's the weather in Tokyo?"
"Current weather conditions in Paris"
"Show me the weather for New York City"
```

### Stock Queries
```
"What is Microsoft's stock price?"
"Get me Apple stock data"
"Show Tesla stock information"
```

### Technical Documentation
```
"How do I create an Azure AI agent?"
"Azure OpenAI best practices"
"REST API documentation for Azure AI Foundry"
```

### Construction/RFP Queries (Multi-Agent)
```
"Show me construction management experience"
"Find RFP documents for building projects"
"Construction proposal templates"
```

### Sustainability Queries (Multi-Agent)
```
"Summarize sustainability frameworks"
"Environmental impact assessment methods"
"Green building practices"
```

### Complex Multi-Domain Queries (Multi-Agent)
```
"Get Microsoft stock price and email results"
"Research sustainability practices and find related RFP documents"
"Analyze market data and provide technical documentation"
```

## 🎯 UI Components Reference

### Sidebar Controls
- **Agent Mode Selector**: Radio buttons for Single/Multi agent selection
- **Clear Chat/Reset**: Clears all session data
- **Environment Info**: Shows required configuration

### Main Display Areas

#### **Left Column (55%)**
- **Summary Container**: Latest run metadata and token usage
- **Chat History**: Conversation with timestamps

#### **Right Column (45%)**
- **Tools & Agent Outputs**: Detailed tool execution logs
- **Run Logs**: Expandable execution details

### Chat Input
- **Text Input**: Bottom-fixed input field
- **Supports**: Weather, stock, documentation, RFP, sustainability queries

## 🔍 Session State Management

### Key Session Variables
```python
st.session_state.chat_history  # List of chat messages
st.session_state.runs          # List of execution records  
st.session_state.last_mode     # User's preferred agent mode
```

### Message Structure
```python
{
    "role": "user" | "assistant",
    "content": "message text",
    "timestamp": "HH:MM:SS"
}
```

### Run Record Structure
```python
{
    "mode": "Single Agent" | "Multi Agent",
    "summary": "agent response summary",
    "details": "execution logs",
    "tools": [...],  # tool execution details
    "token_usage": {...},  # API token consumption
    "timestamp": "ISO timestamp"
}
```

## ⚡ Performance Tips

### Single Agent Mode
- **Best For**: Weather, stock, documentation queries
- **Advantages**: Lower latency, simpler architecture
- **Optimize**: Use specific function calls, clear parameter names

### Multi Agent Mode  
- **Best For**: Complex multi-domain queries
- **Advantages**: Specialized expertise, comprehensive responses
- **Optimize**: Structured queries, specific domain requests

### General Optimization
- **Query Length**: Keep queries focused and specific
- **Resource Cleanup**: Application automatically cleans up agents
- **Memory Management**: Session state limited to prevent memory issues

## 🚨 Troubleshooting

### Common Issues

#### **Authentication Errors**
```
Error: 401 Unauthorized
Solution: Check Azure credentials and environment variables
```

#### **Model Not Found**
```
Error: Model deployment not found
Solution: Verify MODEL_DEPLOYMENT_NAME matches actual deployment
```

#### **Tool Execution Failures**
```
Error: Function tool execution failed
Solution: Check network connectivity and API availability
```

#### **MCP Connection Issues**
```
Error: MCP server not responding
Solution: Verify MCP_SERVER_URL accessibility
```

### Debug Information

#### **Enable Debug Mode**
- Check "Run Logs" expander for detailed execution traces
- Monitor token usage in summary container
- Review tool outputs in right column

#### **Common Error Patterns**
- **Rate Limiting**: 429 errors - wait and retry
- **Network Issues**: Check internet connectivity
- **Configuration**: Verify all environment variables

## 📝 Configuration Examples

### Development Environment
```bash
# .env file for development
PROJECT_ENDPOINT=https://myproject.services.ai.azure.com/api/projects/myproject
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
MCP_SERVER_URL=https://learn.microsoft.com/api/mcp
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012
AZURE_RESOURCE_GROUP=my-resource-group
```

### Production Environment
```bash
# Use Azure Key Vault for secrets
# Use Managed Identity for authentication
# Monitor with Application Insights
APPLICATION_INSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## 🔧 Advanced Configuration

### Model Selection
```python
# Supported models
MODEL_DEPLOYMENT_NAME = "gpt-4o-mini"     # Fast, cost-effective
MODEL_DEPLOYMENT_NAME = "gpt-4o"          # Higher quality
MODEL_DEPLOYMENT_NAME = "o1-preview"      # Advanced reasoning
```

### Temperature Settings
```python
# In agent creation
temperature = 0.0  # Deterministic responses (default)
temperature = 0.7  # More creative responses
```

### MCP Tool Configuration
```python
# Custom MCP server
MCP_SERVER_URL = "https://custom-mcp-server.com/api"
MCP_SERVER_LABEL = "CustomMCP"

# Restricted tools
allowed_tools = ["tool1", "tool2"]  # Empty = all tools
```

## 📊 Monitoring & Analytics

### Token Usage Monitoring
- **Display**: Summary container shows token consumption
- **Fields**: Prompt tokens, completion tokens, total tokens
- **Tracking**: Per-run and cumulative usage

### Performance Metrics
- **Response Time**: Monitored per agent execution
- **Success Rate**: Track successful vs failed executions
- **Tool Usage**: Monitor which tools are used most frequently

### Error Tracking
- **Error Logs**: Detailed error information in run logs
- **Error Categories**: Authentication, rate limiting, tool execution
- **Recovery**: Automatic retry for transient errors

## 🔄 Workflow Patterns

### Single Agent Workflow
```
User Query → Tool Selection → Parallel Execution → Response Assembly
```

### Multi Agent Workflow
```
User Query → Agent Analysis → Task Delegation → Result Aggregation → Response Synthesis
```

### Error Handling Workflow
```
Error Detection → Error Classification → Recovery Strategy → User Notification
```

## 📚 API Reference Quick Links

### Core Functions
- **`single_agent(query: str) -> dict`**: Execute single agent mode
- **`connected_agent(query: str) -> dict`**: Execute multi agent mode

### Helper Functions
- **`get_weather(city: str) -> str`**: Weather data retrieval
- **`fetch_stock_data(company: str) -> str`**: Stock data retrieval

### UI Functions
- **`_render_chat_history(container)`**: Render chat messages
- **`_parse_connected_stdout(lines)`**: Parse multi-agent output
- **`_truncate(text, limit)`**: Text truncation utility

## 🎨 Customization Options

### UI Customization
```python
# Page configuration
st.set_page_config(
    page_title="Custom Agent Demo",
    layout="wide"
)

# Column ratios
col_left, col_right = st.columns([0.6, 0.4])  # Adjust ratios
```

### Agent Instructions
```python
# Custom agent instructions
instructions = """
You are a specialized agent for [domain].
- Focus on [specific tasks]
- Use [preferred tools]
- Format responses as [format]
"""
```

### Tool Configuration
```python
# Add custom function tools
custom_functions = {custom_function1, custom_function2}
functions = FunctionTool(functions=custom_functions)
```

## 📋 Checklists

### Pre-Launch Checklist
- [ ] Azure AI Foundry project configured
- [ ] All environment variables set
- [ ] Model deployments verified
- [ ] Network connectivity tested
- [ ] Dependencies installed

### Debug Checklist
- [ ] Check environment variables
- [ ] Verify Azure credentials
- [ ] Test model deployment access
- [ ] Check MCP server connectivity
- [ ] Review error logs

### Performance Checklist
- [ ] Monitor token usage
- [ ] Track response times
- [ ] Review error rates
- [ ] Optimize query patterns
- [ ] Clean up resources

---

*This quick reference provides essential information for daily use of the Agent Demo system. For detailed technical information, see the complete documentation files.*