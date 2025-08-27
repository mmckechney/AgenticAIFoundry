# AgenticAI Foundry - stmfg1.py API Reference

## Table of Contents
1. [Overview](#overview)
2. [Core Functions](#core-functions)
3. [Agent Phase Functions](#agent-phase-functions)
4. [Utility Functions](#utility-functions)
5. [UI Functions](#ui-functions)
6. [Data Structures](#data-structures)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)

## Overview

This API reference documents all functions, classes, and data structures in the Adhesive Manufacturing Orchestrator (`stmfg1.py`). The system is built around three main phase functions that orchestrate specialized AI agents for comprehensive manufacturing guidance.

## Core Functions

### Agent Phase Functions

#### `connected_agent_phase1(query: str) -> tuple[str, dict, dict]`

Executes the Research & Development phase workflow with 5 specialized agents.

**Parameters:**
- `query` (str): User input describing R&D requirements or questions

**Returns:**
- `tuple`: (summary_text, agent_outputs, token_usage)
  - `summary_text` (str): Consolidated response from orchestrator agent
  - `agent_outputs` (dict): Individual responses from each connected agent
  - `token_usage` (dict): Token consumption metrics

**Agents Involved:**
- Ideation Agent (`ideationagent`)
- Raw Material Agent (`rawmaterialagent`) 
- Formulation Agent (`formulationagent`)
- Initial Lab Test Agent (`initiallabtestagent`)
- Concept Validation Agent (`conceptvalidationagent`)

**Example:**
```python
query = "Develop an eco-friendly adhesive for wooden furniture with low VOC emissions"
summary, agents, usage = connected_agent_phase1(query)

# Access individual agent responses
ideation_response = agents.get('ideationagent', 'No response')
material_response = agents.get('rawmaterialagent', 'No response')

# Check token usage
total_tokens = usage.get('total_tokens', 0)
```

**Workflow:**
1. Creates Azure AI Project client
2. Instantiates 5 specialized R&D agents
3. Creates orchestrator agent with connected tools
4. Executes multi-agent workflow
5. Parses and aggregates results
6. Cleans up all resources
7. Returns processed results

---

#### `connected_agent_phase2(query: str) -> tuple[str, dict, dict]`

Executes the Prototyping & Testing phase workflow with 5 specialized agents.

**Parameters:**
- `query` (str): User input describing prototyping requirements or questions

**Returns:**
- `tuple`: (summary_text, agent_outputs, token_usage)

**Agents Involved:**
- Prototype Creation Agent (`prototypecreationagent`)
- Performance Testing Agent (`performancetestingagent`)
- Customer Field Trial Agent (`customerfieldtrialagent`)
- Iteration & Refinement Agent (`refinementagent`)
- Quality Assurance Agent (`qualityassuranceagent`)

**Example:**
```python
query = "Create prototypes for eco-friendly wood adhesive with comprehensive testing"
summary, agents, usage = connected_agent_phase2(query)

# Access specific agent outputs
prototype_guidance = agents.get('prototypecreationagent', 'No guidance')
test_results = agents.get('performancetestingagent', 'No results')
```

---

#### `connected_agent_phase3(query: str) -> tuple[str, dict, dict]`

Executes the Production Scaling phase workflow with 6 specialized agents.

**Parameters:**
- `query` (str): User input describing production scaling requirements

**Returns:**
- `tuple`: (summary_text, agent_outputs, token_usage)

**Agents Involved:**
- Design Optimization Agent (`designoptimizationagent`)
- Pilot Production Agent (`pilotprodrampupagent`)
- Full-Scale Manufacturing Agent (`fullscalemfgagent`)
- Quality Control Production Agent (`qualitycontrolproductionagent`)
- Packaging Agent (`packingagent`)
- Commercialization Agent (`Commercializationagent`)

**Example:**
```python
query = "Scale eco-friendly wood adhesive to industrial production with quality control"
summary, agents, usage = connected_agent_phase3(query)

# Access production planning outputs
design_optimization = agents.get('designoptimizationagent', 'No optimization')
manufacturing_plan = agents.get('fullscalemfgagent', 'No plan')
```

## Utility Functions

#### `parse_agent_outputs(run_steps: list) -> dict`

Parses agent execution steps to extract individual agent responses.

**Parameters:**
- `run_steps` (list): List of execution steps from Azure AI agent run

**Returns:**
- `dict`: Mapping of agent names to their outputs

**Example:**
```python
run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
agent_outputs = parse_agent_outputs(run_steps)

# Access parsed outputs
for agent_name, output in agent_outputs.items():
    print(f"{agent_name}: {output[:100]}...")
```

**Implementation Details:**
```python
def parse_agent_outputs(run_steps):
    """Parse agent outputs from run steps to extract individual agent responses."""
    agent_outputs = {}
    
    for step in run_steps:
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])
        
        if tool_calls:
            for call in tool_calls:
                connected_agent = call.get("connected_agent", {})
                if connected_agent:
                    agent_name = connected_agent.get("name", "Unknown Agent")
                    agent_output = connected_agent.get("output", "No output available")
                    agent_outputs[agent_name] = agent_output
    
    return agent_outputs
```

---

#### `_html_escape(text: str) -> str`

Escapes HTML characters to prevent injection attacks in the UI.

**Parameters:**
- `text` (str): Input text that may contain HTML characters

**Returns:**
- `str`: Safely escaped text for display

**Example:**
```python
user_input = "<script>alert('test')</script>"
safe_text = _html_escape(user_input)
# Result: "&lt;script&gt;alert('test')&lt;/script&gt;"
```

**Implementation:**
```python
def _html_escape(text):
    """Escape HTML characters to prevent injection."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")
```

## UI Functions

#### `main_screen() -> None`

Renders the main Streamlit interface with tabbed navigation and chat functionality.

**Parameters:** None

**Returns:** None (renders UI)

**Features:**
- Three-tab interface for manufacturing phases
- Scrollable content panels with height management
- Real-time chat input and response display
- Session state management for conversation history
- Responsive design with professional styling

**Key Components:**
```python
def main_screen():
    # Configure page layout
    st.set_page_config(page_title="Adhesive Manufacturing Orchestrator", layout="wide")
    
    # Create tab structure
    tabs = st.tabs([
        "Phase 1: Research and Development (R&D)",
        "Phase 2: Prototyping and Testing", 
        "Phase 3: Scaling to Mass Production"
    ])
    
    # Render each phase with helper function
    with tabs[0]:
        render_phase("Phase 1: R&D", "p1", connected_agent_phase1)
    # ... additional tabs
```

#### `render_phase(phase_title: str, phase_key: str, run_fn: callable) -> None`

Helper function to render individual phase interfaces (defined within `main_screen`).

**Parameters:**
- `phase_title` (str): Display title for the phase
- `phase_key` (str): Session state key prefix (e.g., "p1", "p2", "p3")
- `run_fn` (callable): Phase execution function to call

**Features:**
- Two-column layout (summary + agent outputs)
- Scrollable content containers
- Chat input handling
- Session state updates
- Error handling and display

## Data Structures

### Agent Configuration Structure

```python
agent_config = {
    "name": str,                    # Agent identifier
    "instructions": str,            # Detailed agent instructions
    "connected_name": str,          # Connected tool name
    "description": str,             # Agent capability description
    "model": str,                   # Model deployment name
    "tools": list                   # Optional tools list
}
```

### Agent Response Structure

```python
agent_response = {
    "agent_name": {
        "output": str,              # Agent's response text
        "tool_calls": list,         # Tools called during execution
        "execution_time": float,    # Response time in seconds
        "token_usage": dict         # Token consumption metrics
    }
}
```

### Token Usage Structure

```python
token_usage = {
    "prompt_tokens": int,           # Tokens in input prompt
    "completion_tokens": int,       # Tokens in generated response
    "total_tokens": int            # Sum of prompt + completion tokens
}
```

### Session State Structure

```python
session_state = {
    "p1_history": list,            # Phase 1 conversation history
    "p2_history": list,            # Phase 2 conversation history
    "p3_history": list,            # Phase 3 conversation history
    "p1_agents": dict,             # Phase 1 agent outputs
    "p2_agents": dict,             # Phase 2 agent outputs
    "p3_agents": dict              # Phase 3 agent outputs
}
```

## Configuration

### Environment Variables

#### Required Variables
```python
required_env_vars = {
    "PROJECT_ENDPOINT": "Azure AI Project service endpoint",
    "MODEL_ENDPOINT": "Azure OpenAI service endpoint", 
    "MODEL_API_KEY": "Azure OpenAI API key",
    "MODEL_DEPLOYMENT_NAME": "Deployed model name (e.g., gpt-4o-mini)",
    "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED": "Telemetry recording flag"
}
```

#### Configuration Validation
```python
# Automatic validation on startup
missing_vars = []
for var in required_env_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {missing_vars}")
```

### Azure Client Configuration

#### Project Client Setup
```python
project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

#### OpenAI Client Setup  
```python
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-10-21",
)
```

#### Telemetry Configuration
```python
connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=connection_string)
tracer = trace.get_tracer(__name__)
```

## Error Handling

### Common Exception Types

#### `ConnectionError`
Raised when Azure services are unreachable.
```python
try:
    result = connected_agent_phase1(query)
except ConnectionError as e:
    st.error(f"Connection error: {e}")
    return None, {}, {}
```

#### `TimeoutError`
Raised when agent execution exceeds timeout limits.
```python
try:
    run = project_client.agents.runs.create_and_process(thread_id, agent_id)
except TimeoutError as e:
    st.error(f"Operation timed out: {e}")
    return None, {}, {}
```

#### `AuthenticationError`
Raised when Azure authentication fails.
```python
try:
    project_client = AIProjectClient(endpoint, credential)
except AuthenticationError as e:
    st.error(f"Authentication failed: {e}")
    return None, {}, {}
```

### Error Recovery Patterns

#### Graceful Degradation
```python
def robust_agent_execution(query, phase_function):
    """Execute phase function with comprehensive error handling"""
    try:
        return phase_function(query)
    except Exception as e:
        logger.error(f"Phase execution failed: {e}")
        return generate_fallback_response(query), {}, {}

def generate_fallback_response(query):
    """Provide helpful response when agents are unavailable"""
    return f"Unable to process query due to system issues. Please try again later."
```

#### Resource Cleanup
```python
def cleanup_resources(project_client, agents, orchestrator, thread):
    """Ensure all Azure resources are properly released"""
    try:
        # Delete orchestrator agent
        if orchestrator:
            project_client.agents.delete_agent(orchestrator.id)
        
        # Delete thread
        if thread:
            project_client.agents.threads.delete(thread.id)
            
        # Delete all connected agents
        for agent in agents:
            if agent:
                project_client.agents.delete_agent(agent.id)
                
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")
```

### Status Monitoring

#### Run Status Tracking
```python
def monitor_run_completion(run, project_client, thread_id, run_id, timeout=300):
    """Monitor agent run until completion with timeout"""
    start_time = time.time()
    
    while run.status in ["queued", "in_progress", "requires_action"]:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Run exceeded {timeout} second timeout")
            
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread_id, run_id=run_id)
        
    if run.status == "failed":
        raise RuntimeError(f"Run failed: {run.last_error}")
        
    return run
```

## Performance Considerations

### Token Usage Optimization
```python
def calculate_comprehensive_token_usage(run, run_steps=None):
    """Calculate token usage with fallback to run steps"""
    token_usage = {}
    
    # Primary: Get usage from run object
    if hasattr(run, 'usage') and run.usage:
        token_usage = {
            'prompt_tokens': getattr(run.usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(run.usage, 'completion_tokens', 0),
            'total_tokens': getattr(run.usage, 'total_tokens', 0)
        }
    else:
        # Fallback: Calculate from run steps
        total_prompt_tokens = 0
        total_completion_tokens = 0
        
        for step in run_steps or []:
            if hasattr(step, 'usage') and step.usage:
                total_prompt_tokens += getattr(step.usage, 'prompt_tokens', 0)
                total_completion_tokens += getattr(step.usage, 'completion_tokens', 0)
        
        token_usage = {
            'prompt_tokens': total_prompt_tokens,
            'completion_tokens': total_completion_tokens,
            'total_tokens': total_prompt_tokens + total_completion_tokens
        }
    
    return token_usage
```

### Memory Management
```python
def efficient_session_management():
    """Best practices for session state management"""
    # Initialize only required keys
    required_keys = ["p1_history", "p2_history", "p3_history", 
                     "p1_agents", "p2_agents", "p3_agents"]
    
    for key in required_keys:
        if key not in st.session_state:
            st.session_state[key] = [] if key.endswith("history") else {}
    
    # Limit history size to prevent memory issues
    max_history_size = 50
    for history_key in ["p1_history", "p2_history", "p3_history"]:
        if len(st.session_state[history_key]) > max_history_size:
            st.session_state[history_key] = st.session_state[history_key][-max_history_size:]
```

## Usage Examples

### Complete Workflow Example
```python
# Example: Complete adhesive development workflow
import streamlit as st

def complete_adhesive_workflow():
    """Example of using all three phases for complete product development"""
    
    # Phase 1: R&D
    rd_query = "Develop high-strength, eco-friendly adhesive for aerospace composites"
    rd_summary, rd_agents, rd_usage = connected_agent_phase1(rd_query)
    
    # Phase 2: Prototyping (using R&D results)
    proto_query = f"Create prototypes based on: {rd_summary[:200]}"
    proto_summary, proto_agents, proto_usage = connected_agent_phase2(proto_query)
    
    # Phase 3: Production (using prototyping results)  
    prod_query = f"Scale to production based on: {proto_summary[:200]}"
    prod_summary, prod_agents, prod_usage = connected_agent_phase3(prod_query)
    
    # Calculate total token usage
    total_tokens = (rd_usage.get('total_tokens', 0) + 
                   proto_usage.get('total_tokens', 0) + 
                   prod_usage.get('total_tokens', 0))
    
    return {
        'rd_results': (rd_summary, rd_agents),
        'proto_results': (proto_summary, proto_agents), 
        'prod_results': (prod_summary, prod_agents),
        'total_tokens': total_tokens
    }
```

This API reference provides comprehensive documentation for all functions and data structures in the Adhesive Manufacturing Orchestrator system, enabling developers to effectively integrate and extend the system's capabilities.