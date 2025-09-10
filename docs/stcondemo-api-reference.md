# Agent Demo System - API Reference

## Overview

This document provides comprehensive API reference for the Agent Demo system (`stcondemoui.py` and `stcondemo.py`), including function signatures, parameters, return values, and usage examples.

## Table of Contents

1. [Core Functions](#core-functions)
2. [UI Functions](#ui-functions)
3. [Tool Functions](#tool-functions)
4. [Utility Functions](#utility-functions)
5. [Class Definitions](#class-definitions)
6. [Configuration Constants](#configuration-constants)
7. [Error Handling](#error-handling)

## Core Functions

### `single_agent(query: str) -> dict`

Executes a single agent with integrated tool access (Function tools + MCP tools).

#### Parameters
- **`query`** (`str`): User query string to process

#### Returns
- **`dict`**: Structured response containing:
  ```python
  {
      "summary": str,           # Main response text
      "details": str,           # Execution logs
      "messages": list,         # Message history
      "steps": list,            # Tool execution steps
      "token_usage": dict,      # Token consumption details
      "status": str,            # Execution status
      "query": str              # Original query
  }
  ```

#### Usage Example
```python
response = single_agent("What's the weather in Paris?")
print(response["summary"])  # Weather information
print(response["token_usage"])  # {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225}
```

#### Supported Query Types
- **Weather**: `"What's the weather in [city]?"`
- **Stock**: `"What is [company]'s stock price?"`
- **Documentation**: `"How do I [technical question]?"`
- **General**: Any question requiring single-agent processing

#### Error Handling
- Returns error details in `status` field
- Logs detailed error information in `details` field
- Gracefully handles tool execution failures

---

### `connected_agent(query: str) -> dict`

Executes multi-agent orchestration with specialized connected agents.

#### Parameters
- **`query`** (`str`): User query string to process

#### Returns
- **`dict`**: Structured response containing:
  ```python
  {
      "summary": str,           # Aggregated response from all agents
      "token_usage": dict,      # Token consumption across all agents
      "status": str             # Overall execution status
  }
  ```

#### Usage Example
```python
response = connected_agent("Get Microsoft stock price and find RFP documents")
print(response["summary"])  # Combined stock and RFP information
```

#### Specialized Agents Created
1. **Base Agent**: Generic processing
2. **Stock Agent**: Financial data with `fetch_stock_data`
3. **RFP Search Agent**: Document search with Azure AI Search
4. **Sustainability Agent**: Research papers with file search
5. **MCP Learn Agent**: Microsoft documentation

#### Agent Coordination
- **Orchestrator**: Main agent coordinates all specialized agents
- **Connected Tools**: Agents exposed as tools to orchestrator
- **Result Aggregation**: Combines outputs from multiple agents
- **Resource Cleanup**: Automatic cleanup of all created agents

---

## Tool Functions

### `get_weather(city: str) -> str`

Retrieves current weather information for specified city.

#### Parameters
- **`city`** (`str`): City name (e.g., "Paris", "New York")

#### Returns
- **`str`**: Weather information string

#### Implementation Details
```python
def get_weather(city: str) -> str:
    """Get current weather for a city using Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 0,
        "longitude": 0,
        "current_weather": True
    }
    # Note: Simplified implementation - real version needs geocoding
```

#### Usage Example
```python
weather = get_weather("Tokyo")
# Returns: "Current temperature: 25°C, Wind speed: 10 km/h"
```

#### Error Handling
- **Invalid city**: Returns error message requesting valid city name
- **API failure**: Returns formatted error with status code
- **Network issues**: Returns connection error message

---

### `fetch_stock_data(company_name: str) -> str`

Retrieves stock price data for specified company.

#### Parameters
- **`company_name`** (`str`): Company name (e.g., "Microsoft", "Apple")

#### Returns
- **`str`**: Stock data string with 7-day historical information

#### Implementation Details
```python
def fetch_stock_data(company_name: str) -> str:
    """Fetches stock data using Yahoo Finance API."""
    # Step 1: Get ticker symbol
    ticker = get_ticker(company_name)
    
    # Step 2: Fetch 7-day data
    data = yf.download(ticker, period='7d')
    
    return data.to_string()
```

#### Helper Function: `get_ticker(company_name: str) -> str`
```python
def get_ticker(company_name: str) -> str:
    """Searches for stock ticker based on company name."""
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
    # Returns ticker symbol or None
```

#### Usage Example
```python
stock_data = fetch_stock_data("Apple")
# Returns: Formatted stock data with prices, volumes, etc.
```

#### Error Handling
- **Company not found**: Returns "Could not find ticker for company" message
- **No data available**: Returns "No data found for ticker" message
- **API failure**: Returns formatted error message

---

## UI Functions

### `run_single_agent(user_text: str) -> dict`

UI wrapper for single agent execution with session state management.

#### Parameters
- **`user_text`** (`str`): User input from chat interface

#### Returns
- **`dict`**: Run record for session state

#### Implementation
```python
def run_single_agent(user_text: str) -> dict:
    result = single_agent(user_text)
    
    # Extract tool events from steps
    tool_events = []
    for step in result.get("steps", []):
        for tc in step.get("tool_calls", []):
            tool_events.append({
                "name": tc.get("name"),
                "arguments": tc.get("arguments"),
                "output": tc.get("output"),
                "step_id": step.get("id"),
                "status": step.get("status"),
            })
    
    # Create run record
    run_record = {
        "mode": "Single Agent",
        "summary": result.get("summary"),
        "details": result.get("details"),
        "tools": tool_events,
        "raw": result,
        "token_usage": result.get("token_usage"),
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    
    st.session_state.runs.append(run_record)
    return run_record
```

---

### `run_multi_agent(user_text: str) -> dict`

UI wrapper for multi-agent execution with stdout parsing.

#### Parameters
- **`user_text`** (`str`): User input from chat interface

#### Returns
- **`dict`**: Run record for session state

#### Implementation
```python
def run_multi_agent(user_text: str) -> dict:
    buffer = io.StringIO()
    
    # Capture stdout from connected_agent execution
    with contextlib.redirect_stdout(buffer):
        result_obj = connected_agent(user_text)
    
    stdout_lines = buffer.getvalue().splitlines()
    tool_events = _parse_connected_stdout(stdout_lines)
    
    # Create run record
    run_record = {
        "mode": "Multi Agent",
        "summary": result_obj.get("summary") or "(no response)",
        "details": "\n".join(stdout_lines[-400:]),  # Keep tail
        "tools": tool_events,
        "raw": {"stdout": stdout_lines, "summary": result_obj.get("summary")},
        "token_usage": result_obj.get("token_usage"),
        "status": result_obj.get("status"),
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    
    st.session_state.runs.append(run_record)
    return run_record
```

---

### `_parse_connected_stdout(stdout_lines: list) -> list`

Parses stdout output from multi-agent execution to extract tool information.

#### Parameters
- **`stdout_lines`** (`list[str]`): List of stdout lines from agent execution

#### Returns
- **`list[dict]`**: List of tool event dictionaries

#### Implementation
```python
def _parse_connected_stdout(stdout_lines: list) -> list:
    """Parse stdout from connected_agent() to extract tool/agent outputs."""
    results = []
    current = {}
    
    for line in stdout_lines:
        line = line.strip()
        
        if line.startswith("Tool call:"):
            # Commit previous and start new
            if current:
                results.append(current)
            
            # Parse tool call line
            try:
                parts = line.split(",")
                name_part = parts[0].split(":", 1)[1].strip()
                current = {
                    "type": "tool_call",
                    "agent_name": name_part,
                    "raw": line
                }
            except Exception:
                current = {
                    "type": "tool_call",
                    "agent_name": "unknown",
                    "raw": line
                }
                
        elif "Connected Input(Name of Agent):" in line:
            agent_name = line.split(":", 1)[1].strip()
            current.setdefault("agent_name", agent_name)
            current.setdefault("raw", "")
            current["raw"] += "\n" + line
            
        elif line.startswith("Connected Output:"):
            output = line.split(":", 1)[1].strip()
            current["output"] = output
            current.setdefault("raw", "")
            current["raw"] += "\n" + line
    
    if current:
        results.append(current)
    
    return results
```

#### Output Format
```python
[
    {
        "type": "tool_call",
        "agent_name": "Stockagent",
        "output": "Stock price information...",
        "raw": "Full stdout capture..."
    },
    # ... more tool events
]
```

---

### `_render_chat_history(container)`

Renders chat history in specified Streamlit container.

#### Parameters
- **`container`**: Streamlit container object

#### Implementation
```python
def _render_chat_history(container):
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"]
        timestamp = msg.get("timestamp")
        
        # Format role label with timestamp
        label = f"**{role.capitalize()}**" + (f" · {timestamp}" if timestamp else "")
        
        # Render message components
        container.markdown(label)
        container.markdown(content)
        container.markdown("---")
```

---

### `_truncate(txt: str, limit: int = 1200) -> str`

Truncates text to specified character limit.

#### Parameters
- **`txt`** (`str`): Text to truncate
- **`limit`** (`int`, optional): Character limit (default: 1200)

#### Returns
- **`str`**: Truncated text with "..." suffix if truncated

#### Implementation
```python
def _truncate(txt: str, limit: int = 1200) -> str:
    if txt is None:
        return ""
    t = str(txt)
    return t if len(t) <= limit else t[:limit - 3] + "..."
```

---

## Utility Functions

### Session State Initialization

#### `initialize_session_state()`

Initializes Streamlit session state with default values.

```python
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "runs" not in st.session_state:
        st.session_state.runs = []
        
    if "last_mode" not in st.session_state:
        st.session_state.last_mode = "Single Agent"
```

### Message Management

#### `add_message(role: str, content: str, timestamp: str = None)`

Adds message to chat history.

```python
def add_message(role: str, content: str, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })
```

### Tool Definition Management

#### `_ensure_list(v) -> list`

Ensures value is in list format for tool definition flattening.

```python
def _ensure_list(v):
    """Ensures consistent list format for tool definitions"""
    return v if isinstance(v, list) else [v]
```

## Configuration Constants

### Environment Variables

```python
# Azure AI Foundry Configuration
PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_ENDPOINT = os.environ["MODEL_ENDPOINT"]
MODEL_API_KEY = os.environ["MODEL_API_KEY"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]

# MCP Configuration
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
MCP_SERVER_LABEL = os.environ.get("MCP_SERVER_LABEL", "MicrosoftLearn")

# Azure Resources
AZURE_SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
AZURE_RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
```

### Application Constants

```python
# UI Configuration
MAX_CHAT_HISTORY = 100          # Maximum chat messages to retain
MAX_RUN_RECORDS = 50            # Maximum run records to retain
TRUNCATE_LIMIT = 1200           # Default text truncation limit
TOOLS_OUTPUT_LIMIT = 4000       # Tool output display limit

# Agent Configuration
MAX_ITERATIONS = 50             # Maximum agent execution iterations
AGENT_TEMPERATURE = 0.0         # Agent response temperature
MAX_TOKENS = 4000               # Maximum response tokens
```

### Tool Configuration

```python
# Weather Tool
WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast"

# Stock Tool  
STOCK_SEARCH_API = "https://query1.finance.yahoo.com/v1/finance/search"
STOCK_PERIOD = "7d"             # Historical data period

# MCP Tool
MCP_ALLOWED_TOOLS = []          # Empty = all tools allowed
MCP_TIMEOUT = 30                # MCP request timeout (seconds)
```

## Error Handling

### Exception Types

#### `ToolExecutionError`
```python
class ToolExecutionError(Exception):
    """Raised when tool execution fails"""
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        self.message = message
        super().__init__(f"Tool '{tool_name}' failed: {message}")
```

#### `ValidationError`
```python
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass
```

#### `AgentExecutionError`
```python
class AgentExecutionError(Exception):
    """Raised when agent execution fails"""
    def __init__(self, agent_type: str, message: str, details: dict = None):
        self.agent_type = agent_type
        self.message = message
        self.details = details or {}
        super().__init__(f"Agent '{agent_type}' failed: {message}")
```

### Error Response Format

```python
{
    "error": True,
    "error_type": str,              # Error category
    "error_message": str,           # Human-readable message
    "error_details": dict,          # Technical details
    "recovery_suggestion": str,     # Suggested resolution
    "timestamp": str               # Error timestamp
}
```

### Error Handling Patterns

#### Function Tool Error Handling
```python
try:
    result = function_call(args)
    return {"success": True, "result": result}
except Exception as e:
    return {
        "success": False,
        "error": str(e),
        "error_type": type(e).__name__,
        "recovery_suggestion": "Check parameters and try again"
    }
```

#### Agent Execution Error Handling
```python
try:
    response = agent_execution()
    return response
except AgentExecutionError as e:
    return {
        "summary": f"Error: {e.message}",
        "status": "failed",
        "error_details": e.details,
        "recovery_suggestion": "Check configuration and retry"
    }
```

## Type Definitions

### Message Type
```python
from typing import TypedDict

class Message(TypedDict):
    role: str              # "user" or "assistant"
    content: str           # Message content
    timestamp: str         # HH:MM:SS format
```

### Run Record Type
```python
class RunRecord(TypedDict):
    mode: str              # "Single Agent" or "Multi Agent"
    summary: str           # Response summary
    details: str           # Execution details
    tools: list           # Tool execution events
    raw: dict             # Raw response data
    token_usage: dict     # Token consumption
    status: str           # Execution status
    timestamp: str        # ISO timestamp
```

### Tool Event Type
```python
class ToolEvent(TypedDict):
    name: str             # Tool/function name
    arguments: str        # Tool arguments (JSON string)
    output: str           # Tool output
    step_id: str          # Execution step ID
    status: str           # Tool execution status
```

## Usage Patterns

### Basic Single Agent Usage
```python
# Simple query
response = single_agent("What's the weather in London?")
if response["status"] == "completed":
    print(response["summary"])
else:
    print(f"Error: {response.get('details', 'Unknown error')}")
```

### Basic Multi Agent Usage
```python
# Complex query
response = connected_agent("Get stock data and RFP documents")
if response.get("status") == "completed":
    print(response["summary"])
else:
    print("Multi-agent execution failed")
```

### UI Integration Pattern
```python
# In Streamlit app
if user_input:
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.utcnow().strftime("%H:%M:%S")
    })
    
    # Execute based on mode
    if mode == "Single Agent":
        run_record = run_single_agent(user_input)
    else:
        run_record = run_multi_agent(user_input)
    
    # Add assistant response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": run_record.get("summary", "No response"),
        "timestamp": datetime.utcnow().strftime("%H:%M:%S")
    })
    
    st.rerun()
```

---

*This API reference provides comprehensive documentation for all functions, classes, and patterns used in the Agent Demo system. Use this reference for implementation details and integration guidance.*