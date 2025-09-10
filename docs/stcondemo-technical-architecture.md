# Agent Demo System - Technical Architecture

## Overview

This document provides an in-depth technical analysis of the Agent Demo system (`stcondemoui.py` and `stcondemo.py`), focusing on the architectural decisions, implementation patterns, and technical integration details that enable both Single Agent and Multi (Connected) Agent modes.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Single Agent Technical Design](#single-agent-technical-design)
3. [Multi Agent Technical Design](#multi-agent-technical-design)
4. [Azure AI Foundry Integration](#azure-ai-foundry-integration)
5. [Tool System Architecture](#tool-system-architecture)
6. [Data Flow Patterns](#data-flow-patterns)
7. [Session Management](#session-management)
8. [Error Handling Architecture](#error-handling-architecture)
9. [Performance Considerations](#performance-considerations)
10. [Security Architecture](#security-architecture)

## System Architecture

### Layered Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                   (stcondemoui.py)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Streamlit UI  │  │  State Management│  │   Layout    │ │
│  │   Components    │  │                  │  │  Management │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ Function Calls
┌─────────────────────▼───────────────────────────────────────┐
│                   Business Logic Layer                     │
│                    (stcondemo.py)                          │
│  ┌─────────────────┐              ┌─────────────────┐      │
│  │ single_agent()  │              │connected_agent()│      │
│  │                 │              │                 │      │
│  │ • Unified Agent │              │ • Agent         │      │
│  │   Processing    │              │   Orchestration │      │
│  │ • Tool          │              │ • Multi-Agent   │      │
│  │   Integration   │              │   Coordination  │      │
│  └─────────────────┘              └─────────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │ Azure SDK Calls
┌─────────────────────▼───────────────────────────────────────┐
│                   Integration Layer                        │
│                  (Azure AI Foundry)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Agent SDK       │  │ Project Client  │  │ Tool Engine │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API Calls
┌─────────────────────▼───────────────────────────────────────┐
│                   External Services Layer                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Azure OpenAI    │  │ External APIs   │  │ MCP Protocol│ │
│  │ Services        │  │                 │  │ Services    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Patterns

#### **Request Flow Architecture**

```
User Input → UI Validation → Mode Router → Execution Engine → Tool Dispatcher → Service Integration → Response Assembly → UI Rendering
```

#### **State Management Architecture**

```
Session State ↔ Chat History ↔ Run Records ↔ Tool Outputs ↔ Execution Metadata
```

## Single Agent Technical Design

### Agent Creation and Configuration

```python
def single_agent(query: str) -> dict:
    """
    Technical Implementation of Single Agent Mode
    
    Architecture Pattern: Unified Agent with Multiple Tool Integration
    """
    
    # Tool Configuration Layer
    mcp_tool = McpTool(
        server_label="MicrosoftLearn",
        server_url="https://learn.microsoft.com/api/mcp",
        allowed_tools=[],  # Empty = all tools available
    )
    
    # Function Tool Registration
    user_functions = {get_weather, fetch_stock_data}
    functions = FunctionTool(functions=user_functions)
    
    # Tool Definition Flattening Pattern
    tool_definitions = (
        _ensure_list(mcp_tool.definitions) +
        _ensure_list(functions.definitions)
    )
    
    # Agent Instantiation with Azure AI Foundry
    agent = agents_client.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="rest-mcp-agent",
        instructions=AGENT_INSTRUCTIONS,
        tools=tool_definitions,
        tool_resources=mcp_tool.resources,
    )
```

### Tool Integration Architecture

#### **Tool Definition Flattening**

The system implements a sophisticated tool definition flattening pattern to handle multiple tool types:

```python
def _ensure_list(v):
    """Ensures consistent list format for tool definitions"""
    return v if isinstance(v, list) else [v]

# Flattening pattern prevents nested array issues
tool_definitions = (
    _ensure_list(mcp_tool.definitions) +      # MCP tool definitions
    _ensure_list(functions.definitions)       # Function tool definitions
)
```

#### **Tool Execution Engine**

```python
# Tool Execution Flow
while run.status in ["queued", "in_progress", "requires_action"]:
    if run.status == "requires_action":
        # Handle MCP Tool Approvals
        if isinstance(required_action, SubmitToolApprovalAction):
            handle_mcp_approvals(required_action)
        
        # Handle Function Tool Executions  
        else:
            handle_function_executions(required_action)
```

### Execution State Machine

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   QUEUED    │────▶│IN_PROGRESS  │────▶│REQUIRES_    │
│             │     │             │     │ACTION       │
└─────────────┘     └─────────────┘     └─────────┬───┘
                                                  │
                    ┌─────────────┐               │
                    │ COMPLETED   │◀──────────────┘
                    │             │
                    └─────────────┘
                           │
                    ┌─────────▼───┐
                    │   CLEANUP   │
                    │             │
                    └─────────────┘
```

### Tool Resolution Pattern

```python
def resolve_tool_execution(tool_call):
    """
    Dynamic tool resolution based on function name
    
    Supports:
    - Weather queries via get_weather()
    - Stock data via fetch_stock_data() 
    - MCP protocol tools (handled by Azure AI Foundry)
    """
    func_name = extract_function_name(tool_call)
    args_dict = parse_arguments(tool_call.arguments)
    
    if func_name == "get_weather":
        return execute_weather_tool(args_dict)
    elif func_name == "fetch_stock_data":
        return execute_stock_tool(args_dict)
    else:
        # MCP and other tools handled by platform
        return platform_execution(tool_call)
```

## Multi Agent Technical Design

### Agent Orchestration Architecture

```python
def connected_agent(query: str) -> dict:
    """
    Technical Implementation of Multi Agent Mode
    
    Architecture Pattern: Orchestrated Specialized Agents
    """
    
    # Phase 1: Specialized Agent Creation
    base_agent = create_base_agent()
    stock_agent = create_stock_agent()  
    rfp_agent = create_rfp_search_agent()
    sustainability_agent = create_sustainability_agent()
    mcp_agent = create_mcp_agent()
    
    # Phase 2: Connected Agent Tool Registration
    connected_tools = [
        ConnectedAgentTool(id=base_agent.id, name="basaeagent", 
                          description="Generic information processing"),
        ConnectedAgentTool(id=stock_agent.id, name="Stockagent",
                          description="Stock price and financial data"),
        ConnectedAgentTool(id=rfp_agent.id, name="AISearchagent", 
                          description="Construction RFP document search"),
        # ... additional connected tools
    ]
    
    # Phase 3: Main Orchestrator Creation
    orchestrator = create_orchestrator_agent(connected_tools)
    
    # Phase 4: Execution and Coordination
    return execute_coordinated_workflow(orchestrator, query)
```

### Specialized Agent Factory Pattern

#### **Stock Price Agent**

```python
def create_stock_agent():
    """
    Creates specialized stock price agent with function tools
    """
    user_functions = {fetch_stock_data}
    functions = FunctionTool(functions=user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    
    return project_client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="Stockagent",
        instructions="Specialized agent for stock data fetching",
        toolset=toolset,
    )
```

#### **RFP Search Agent**

```python
def create_rfp_search_agent():
    """
    Creates specialized RFP document search agent
    """
    ai_search = AzureAISearchTool(
        index_connection_id="vecdb",
        index_name="constructionrfpdocs1", 
        query_type=AzureAISearchQueryType.SIMPLE,
        top_k=5,
    )
    
    return project_client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="AISearchagent",
        instructions="Construction RFP document specialist",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
```

#### **Sustainability Research Agent**

```python
def create_sustainability_agent():
    """
    Creates agent with file search capabilities for research papers
    """
    # File upload and vector store creation
    file = project_client.agents.files.upload_and_poll(
        file_path="./papers/ssrn-4072178.pdf", 
        purpose=FilePurpose.AGENTS
    )
    
    vector_store = project_client.agents.vector_stores.create_and_poll(
        file_ids=[file.id], 
        name="suspaperstore"
    )
    
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])
    
    return project_client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="Sustainabilitypaperagent", 
        instructions="Sustainability research and analysis specialist",
        tools=file_search.definitions,
        tool_resources=file_search.resources,
    )
```

### Orchestration Communication Pattern

```python
def execute_coordinated_workflow(orchestrator, query):
    """
    Executes multi-agent workflow with proper coordination
    """
    # Create conversation thread
    thread = project_client.agents.threads.create()
    
    # Submit user message
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=query,
    )
    
    # Execute with orchestration
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id, 
        agent_id=orchestrator.id
    )
    
    # Monitor execution with state transitions
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = project_client.agents.runs.get(
            thread_id=thread.id, 
            run_id=run.id
        )
        
        # Handle inter-agent communication
        if run.status == "requires_action":
            handle_agent_coordination(run.required_action)
    
    return extract_orchestrated_results(thread, run)
```

### Inter-Agent Communication Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Query    │───▶│  Orchestrator   │───▶│  Query Analysis │
│                 │    │     Agent       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼────┐  ┌───────▼────┐  ┌───────▼────┐
        │Stock Agent │  │ RFP Agent  │  │ MCP Agent  │
        │            │  │            │  │            │
        └───────┬────┘  └───────┬────┘  └───────┬────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                        ┌───────▼────┐
                        │ Result     │
                        │Aggregation │
                        └────────────┘
```

## Azure AI Foundry Integration

### Project Client Architecture

```python
class AzureFoundryIntegration:
    """
    Encapsulates Azure AI Foundry platform integration
    """
    
    def __init__(self):
        self.project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        
        self.agents_client = self.project_client.agents
    
    def create_agent_with_tools(self, config):
        """
        Standardized agent creation with tool integration
        """
        return self.agents_client.create_agent(
            model=config.model,
            name=config.name,
            instructions=config.instructions,
            tools=config.tool_definitions,
            tool_resources=config.tool_resources,
        )
    
    def execute_with_monitoring(self, agent_id, thread_id):
        """
        Execute agent run with comprehensive monitoring
        """
        run = self.agents_client.runs.create(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        return self.monitor_execution(run, thread_id)
```

### Resource Lifecycle Management

```python
class ResourceManager:
    """
    Manages Azure AI Foundry resource lifecycle
    """
    
    def __init__(self):
        self.created_agents = []
        self.created_threads = []
        self.created_files = []
        self.created_vector_stores = []
    
    def track_agent(self, agent):
        self.created_agents.append(agent.id)
        return agent
    
    def cleanup_all_resources(self):
        """
        Comprehensive resource cleanup to prevent resource leaks
        """
        # Delete agents
        for agent_id in self.created_agents:
            try:
                self.project_client.agents.delete_agent(agent_id)
            except Exception as e:
                log_cleanup_error("agent", agent_id, e)
        
        # Delete threads  
        for thread_id in self.created_threads:
            try:
                self.project_client.agents.threads.delete(thread_id)
            except Exception as e:
                log_cleanup_error("thread", thread_id, e)
        
        # Cleanup vector stores and files
        self._cleanup_vector_resources()
```

### Thread and Message Management

```python
def manage_conversation_flow(agents_client, agent_id, user_query):
    """
    Manages conversation thread lifecycle and message flow
    """
    # Thread creation
    thread = agents_client.threads.create()
    
    # Message submission
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_query
    )
    
    # Run execution with monitoring
    run = agents_client.runs.create(
        thread_id=thread.id,
        agent_id=agent_id
    )
    
    # Status monitoring loop
    return monitor_run_execution(agents_client, thread.id, run.id)
```

## Tool System Architecture

### Tool Type Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    Tool System                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                Base Tool                        │   │
│  │                                                 │   │
│  │  • Tool Definition                              │   │
│  │  • Resource Management                         │   │
│  │  • Execution Interface                         │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                   │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │              Tool Implementations              │   │
│  │                                                 │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │   │
│  │ │ Function    │ │ Connected   │ │    MCP      │ │   │
│  │ │ Tools       │ │ Agent Tools │ │   Tools     │ │   │
│  │ │             │ │             │ │             │ │   │
│  │ │ • Python    │ │ • Agent     │ │ • Protocol  │ │   │
│  │ │   Functions │ │   Delegation│ │   Based     │ │   │
│  │ │ • Local     │ │ • Inter-    │ │ • External  │ │   │
│  │ │   Execution │ │   Agent     │ │   Services  │ │   │
│  │ │             │ │   Comm.     │ │             │ │   │
│  │ └─────────────┘ └─────────────┘ └─────────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Function Tool Implementation

```python
class FunctionToolManager:
    """
    Manages function tool registration and execution
    """
    
    def __init__(self, functions_dict):
        self.functions = functions_dict
        self.tool_definitions = self._create_definitions()
    
    def _create_definitions(self):
        """
        Creates Azure AI Foundry compatible tool definitions
        """
        return FunctionTool(functions=self.functions).definitions
    
    def execute_function_call(self, function_name, arguments):
        """
        Executes function call with error handling and validation
        """
        if function_name not in self.functions:
            raise ToolExecutionError(f"Unknown function: {function_name}")
        
        try:
            # Validate arguments
            validated_args = self._validate_arguments(function_name, arguments)
            
            # Execute function
            result = self.functions[function_name](**validated_args)
            
            # Format result
            return self._format_result(result)
            
        except Exception as e:
            return self._handle_execution_error(function_name, e)
```

### MCP Tool Integration

```python
class MCPToolManager:
    """
    Manages MCP (Model Context Protocol) tool integration
    """
    
    def __init__(self, server_url, server_label):
        self.mcp_tool = McpTool(
            server_label=server_label,
            server_url=server_url,
            allowed_tools=[],  # Allow all tools
        )
    
    def get_tool_definitions(self):
        """
        Returns MCP tool definitions for agent registration
        """
        return self.mcp_tool.definitions
    
    def get_tool_resources(self):
        """
        Returns MCP tool resources for agent configuration
        """
        return self.mcp_tool.resources
    
    def handle_approval_action(self, required_action):
        """
        Handles MCP tool approval workflow
        """
        tool_calls = required_action.submit_tool_approval.tool_calls or []
        approvals = []
        
        for tool_call in tool_calls:
            if isinstance(tool_call, RequiredMcpToolCall):
                approvals.append(ToolApproval(
                    tool_call_id=tool_call.id,
                    approve=True,
                    headers=self.mcp_tool.headers
                ))
        
        return approvals
```

### Connected Agent Tool Pattern

```python
class ConnectedAgentToolManager:
    """
    Manages connected agent tool registration and coordination
    """
    
    def __init__(self):
        self.connected_tools = []
        self.agent_registry = {}
    
    def register_connected_agent(self, agent, name, description):
        """
        Registers an agent as a connected tool
        """
        connected_tool = ConnectedAgentTool(
            id=agent.id,
            name=name, 
            description=description
        )
        
        self.connected_tools.append(connected_tool)
        self.agent_registry[name] = agent
        
        return connected_tool
    
    def get_tool_definitions(self):
        """
        Returns connected agent tool definitions for orchestrator
        """
        return [tool.definitions[0] for tool in self.connected_tools]
```

## Data Flow Patterns

### Single Agent Data Flow

```
User Query
    │
    ▼
Query Analysis
    │
    ▼
Tool Selection ────┐
    │              │
    ▼              ▼
Execute Tools  Wait for Results
    │              │
    ▼              ▼
Collect Results ◀──┘
    │
    ▼
Response Assembly
    │
    ▼
UI Display
```

### Multi Agent Data Flow

```
User Query
    │
    ▼
Orchestrator Analysis
    │
    ▼
Agent Selection ────┐
    │               │
    ▼               ▼
Delegate Tasks  Monitor Progress
    │               │
    ├── Stock Agent ──┤
    ├── RFP Agent ────┤  
    ├── MCP Agent ────┤
    │               │
    ▼               ▼
Collect Results ◀───┘
    │
    ▼
Result Aggregation
    │
    ▼
Response Synthesis
    │
    ▼
UI Display
```

### Tool Execution Data Flow

```python
def tool_execution_pipeline(tool_call):
    """
    Standardized tool execution pipeline
    """
    # Phase 1: Validation
    validated_call = validate_tool_call(tool_call)
    
    # Phase 2: Preparation  
    execution_context = prepare_execution_context(validated_call)
    
    # Phase 3: Execution
    raw_result = execute_tool_with_monitoring(execution_context)
    
    # Phase 4: Post-processing
    processed_result = post_process_result(raw_result)
    
    # Phase 5: Formatting
    formatted_result = format_for_agent(processed_result)
    
    return formatted_result
```

## Session Management

### Streamlit Session State Architecture

```python
class SessionStateManager:
    """
    Manages Streamlit session state for Agent Demo UI
    """
    
    @staticmethod
    def initialize_session_state():
        """
        Initializes session state variables with default values
        """
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        if "runs" not in st.session_state:
            st.session_state.runs = []
            
        if "last_mode" not in st.session_state:
            st.session_state.last_mode = "Single Agent"
    
    @staticmethod
    def add_message(role, content, timestamp=None):
        """
        Adds message to chat history with timestamp
        """
        if timestamp is None:
            timestamp = datetime.utcnow().strftime("%H:%M:%S")
            
        st.session_state.chat_history.append({
            "role": role,
            "content": content, 
            "timestamp": timestamp
        })
    
    @staticmethod
    def add_run_record(mode, summary, details, tools, raw_data):
        """
        Adds execution run record with metadata
        """
        run_record = {
            "mode": mode,
            "summary": summary,
            "details": details,
            "tools": tools,
            "raw": raw_data,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
        
        st.session_state.runs.append(run_record)
        return run_record
```

### Chat History Management

```python
def render_chat_history(container):
    """
    Renders chat history with proper formatting and timestamps
    """
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp")
        
        # Format role and timestamp
        label = f"**{role.capitalize()}**"
        if timestamp:
            label += f" · {timestamp}"
            
        # Render message
        container.markdown(label)
        container.markdown(content)
        container.markdown("---")
```

### Run Record Management

```python
def track_execution_run(mode, result):
    """
    Tracks agent execution run with comprehensive metadata
    """
    run_record = {
        "mode": mode,
        "summary": result.get("summary"),
        "details": result.get("details"),
        "tools": extract_tool_events(result),
        "raw": result,
        "token_usage": result.get("token_usage"),
        "status": result.get("status"),
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z"
    }
    
    st.session_state.runs.append(run_record)
    return run_record
```

## Error Handling Architecture

### Error Classification System

```python
class AgentErrorHandler:
    """
    Comprehensive error handling for agent operations
    """
    
    ERROR_CATEGORIES = {
        "AUTHENTICATION": ["401", "403", "invalid_credential"],
        "RATE_LIMITING": ["429", "rate_limit_exceeded"],
        "SERVICE_UNAVAILABLE": ["503", "502", "500"],
        "VALIDATION": ["400", "invalid_input", "missing_parameter"],
        "TOOL_EXECUTION": ["tool_error", "function_error"],
    }
    
    def handle_error(self, error, context):
        """
        Routes error to appropriate handler based on error type
        """
        error_category = self.classify_error(error)
        
        if error_category == "AUTHENTICATION":
            return self.handle_auth_error(error, context)
        elif error_category == "RATE_LIMITING":
            return self.handle_rate_limit_error(error, context)
        elif error_category == "TOOL_EXECUTION":
            return self.handle_tool_error(error, context)
        else:
            return self.handle_generic_error(error, context)
    
    def handle_auth_error(self, error, context):
        """
        Handles authentication and authorization errors
        """
        return {
            "error_type": "authentication",
            "message": "Authentication failed. Check credentials.",
            "resolution": "Verify environment variables and Azure permissions",
            "context": context
        }
```

### Retry and Resilience Patterns

```python
class RetryManager:
    """
    Implements retry logic for transient failures
    """
    
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """
        Executes operation with exponential backoff retry
        """
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except RetryableException as e:
                if attempt == self.max_retries:
                    raise e
                    
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
                
        raise MaxRetriesExceeded()
```

## Performance Considerations

### Resource Optimization

#### **Agent Lifecycle Management**

```python
class PerformantAgentManager:
    """
    Optimized agent management for performance
    """
    
    def __init__(self):
        self.agent_pool = {}
        self.cleanup_queue = []
    
    def get_or_create_agent(self, config):
        """
        Implements agent pooling for performance
        """
        agent_key = self.generate_agent_key(config)
        
        if agent_key in self.agent_pool:
            return self.agent_pool[agent_key]
        
        agent = self.create_new_agent(config)
        self.agent_pool[agent_key] = agent
        
        # Schedule cleanup
        self.schedule_cleanup(agent, config.ttl)
        
        return agent
```

#### **Memory Management**

```python
def optimize_memory_usage():
    """
    Implements memory optimization strategies
    """
    # Limit chat history size
    if len(st.session_state.chat_history) > MAX_CHAT_HISTORY:
        st.session_state.chat_history = st.session_state.chat_history[-MAX_CHAT_HISTORY:]
    
    # Limit run records
    if len(st.session_state.runs) > MAX_RUN_RECORDS:
        st.session_state.runs = st.session_state.runs[-MAX_RUN_RECORDS:]
    
    # Clear large raw data from old runs
    for run in st.session_state.runs[:-KEEP_DETAILED_RUNS:]:
        if "raw" in run:
            run["raw"] = {"truncated": True}
```

### API Call Optimization

```python
class APIOptimizer:
    """
    Optimizes API calls for performance and cost
    """
    
    def __init__(self):
        self.call_cache = {}
        self.rate_limiter = RateLimiter()
    
    def optimized_api_call(self, endpoint, params):
        """
        Implements caching and rate limiting for API calls
        """
        # Check cache
        cache_key = self.generate_cache_key(endpoint, params)
        if cache_key in self.call_cache:
            return self.call_cache[cache_key]
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Execute call
        result = self.execute_api_call(endpoint, params)
        
        # Cache result (if cacheable)
        if self.is_cacheable(endpoint, params):
            self.call_cache[cache_key] = result
        
        return result
```

## Security Architecture

### Credential Management

```python
class SecurityManager:
    """
    Manages security aspects of agent operations
    """
    
    def __init__(self):
        self.credential_provider = DefaultAzureCredential()
        self.secret_manager = AzureKeyVaultManager()
    
    def get_secure_credentials(self):
        """
        Retrieves credentials using Azure security best practices
        """
        return {
            "azure_credential": self.credential_provider,
            "api_keys": self.secret_manager.get_api_keys(),
            "connection_strings": self.secret_manager.get_connection_strings()
        }
    
    def sanitize_logs(self, log_data):
        """
        Removes sensitive information from logs
        """
        sensitive_patterns = [
            r'api[_-]?key["\s:=]+["\w\-]+',
            r'password["\s:=]+["\w\-]+',
            r'secret["\s:=]+["\w\-]+'
        ]
        
        sanitized = log_data
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        
        return sanitized
```

### Input Validation

```python
def validate_user_input(user_input):
    """
    Validates and sanitizes user input for security
    """
    # Length validation
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValidationError("Input too long")
    
    # Content filtering
    if contains_malicious_patterns(user_input):
        raise SecurityError("Potentially malicious input detected")
    
    # Sanitization
    sanitized_input = sanitize_input(user_input)
    
    return sanitized_input
```

### Audit Logging

```python
class AuditLogger:
    """
    Implements comprehensive audit logging
    """
    
    def log_agent_execution(self, mode, query, result, user_context):
        """
        Logs agent execution for audit purposes
        """
        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": mode,
            "query_hash": hashlib.sha256(query.encode()).hexdigest(),
            "result_status": result.get("status"),
            "token_usage": result.get("token_usage"),
            "user_context": user_context,
            "tools_used": extract_tools_used(result)
        }
        
        self.write_audit_log(audit_record)
```

---

*This technical architecture document provides comprehensive technical details for implementing, maintaining, and extending the Agent Demo system. It serves as a reference for developers and architects working with the codebase.*