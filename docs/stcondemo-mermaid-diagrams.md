# Agent Demo System - Mermaid Architecture Diagrams

This document contains comprehensive Mermaid diagrams for the Agent Demo system (`stcondemoui.py` and `stcondemo.py`), providing visual representations of the architecture, workflows, and interaction patterns.

## Table of Contents

1. [Complete System Architecture](#complete-system-architecture)
2. [Single Agent Mode Flow](#single-agent-mode-flow)
3. [Multi Agent Mode Flow](#multi-agent-mode-flow)
4. [UI Component Architecture](#ui-component-architecture)
5. [Tool Integration Patterns](#tool-integration-patterns)
6. [Sequence Diagrams](#sequence-diagrams)
7. [State Management Diagrams](#state-management-diagrams)
8. [Error Handling Flows](#error-handling-flows)

## Complete System Architecture

### High-Level System Overview

```mermaid
graph TB
    %% User Interface Layer
    User[User] --> StreamlitUI[Streamlit UI<br/>stcondemoui.py]
    StreamlitUI --> ChatInput[Chat Input Interface]
    StreamlitUI --> ModeSelector[Agent Mode Selector<br/>Single/Multi]
    StreamlitUI --> DisplayArea[Results Display Area]
    
    %% Backend Processing Layer
    ChatInput --> BackendCore[Backend Core<br/>stcondemo.py]
    BackendCore --> SingleAgent[single_agent&#40;&#41;<br/>Function]
    BackendCore --> MultiAgent[connected_agent&#40;&#41;<br/>Function]
    
    %% Mode Routing
    ModeSelector -->|Single Agent Mode| SingleAgent
    ModeSelector -->|Multi Agent Mode| MultiAgent
    
    %% Single Agent Architecture
    SingleAgent --> SingleAgentCore[Single Agent Core]
    SingleAgentCore --> FunctionTools[Function Tools<br/>Weather, Stock]
    SingleAgentCore --> MCPTools[MCP Tools<br/>Microsoft Learn]
    SingleAgentCore --> UnifiedExecution[Unified Execution Engine]
    
    %% Multi Agent Architecture  
    MultiAgent --> Orchestrator[Main Orchestrator Agent]
    Orchestrator --> BaseAgent[Base Agent<br/>basaeagent]
    Orchestrator --> StockAgentMA[Stock Agent<br/>Stockagent]
    Orchestrator --> RFPAgent[RFP Search Agent<br/>AISearchagent]
    Orchestrator --> SustainAgent[Sustainability Agent<br/>Sustainabilitypaperagent]
    Orchestrator --> MCPAgent[MCP Learn Agent<br/>Mcplearnagent]
    
    %% Azure AI Foundry Platform
    UnifiedExecution --> AzureFoundry[Azure AI Foundry Platform]
    Orchestrator --> AzureFoundry
    
    AzureFoundry --> AgentMgmt[Agent Management]
    AzureFoundry --> ThreadMgmt[Thread Management]
    AzureFoundry --> ToolEngine[Tool Execution Engine]
    AzureFoundry --> ModelServices[Model Services]
    
    %% External Integrations
    FunctionTools --> WeatherAPI[Weather API<br/>Open-Meteo]
    FunctionTools --> StockAPI[Stock API<br/>Yahoo Finance]
    StockAgentMA --> StockAPI
    
    MCPTools --> MSLearnMCP[Microsoft Learn<br/>MCP Server]
    MCPAgent --> MSLearnMCP
    
    RFPAgent --> AzureSearch[Azure AI Search<br/>RFP Documents]
    SustainAgent --> VectorStore[Vector Store<br/>Research Papers]
    
    %% Results Flow
    UnifiedExecution --> ResultsProcessor[Results Processor]
    Orchestrator --> ResultsAggregator[Results Aggregator]
    ResultsProcessor --> DisplayArea
    ResultsAggregator --> DisplayArea
    
    %% Session Management
    StreamlitUI --> SessionState[Session State Management]
    SessionState --> ChatHistory[Chat History]
    SessionState --> RunRecords[Run Records]
    SessionState --> ModePreference[Mode Preference]
    
    %% Styling
    classDef uiClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef singleClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef multiClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef azureClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef externalClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class User,StreamlitUI,ChatInput,ModeSelector,DisplayArea uiClass
    class SingleAgent,SingleAgentCore,FunctionTools,MCPTools,UnifiedExecution singleClass
    class MultiAgent,Orchestrator,BaseAgent,StockAgentMA,RFPAgent,SustainAgent,MCPAgent multiClass
    class AzureFoundry,AgentMgmt,ThreadMgmt,ToolEngine,ModelServices azureClass
    class WeatherAPI,StockAPI,MSLearnMCP,AzureSearch,VectorStore externalClass
```

## Single Agent Mode Flow

### Single Agent Architecture and Execution Flow

```mermaid
graph TD
    %% User Request Entry
    UserQuery[User Query] --> QueryAnalysis[Query Analysis Engine]
    
    %% Single Agent Core
    QueryAnalysis --> SingleAgentCore[Single Agent Core<br/>azure-ai-foundry]
    SingleAgentCore --> AgentInit[Agent Initialization]
    
    %% Tool Registration
    AgentInit --> ToolRegistration[Tool Registration Layer]
    ToolRegistration --> MCPTool[MCP Tool Registration<br/>Microsoft Learn]
    ToolRegistration --> FunctionTool[Function Tool Registration<br/>Weather, Stock]
    ToolRegistration --> ToolFlattening[Tool Definition Flattening]
    
    %% Agent Creation
    ToolFlattening --> AgentCreation[Azure AI Foundry<br/>Agent Creation]
    AgentCreation --> ThreadCreation[Thread Creation]
    ThreadCreation --> MessageSubmission[Message Submission]
    
    %% Execution Loop
    MessageSubmission --> ExecutionLoop[Execution Status Loop]
    ExecutionLoop --> StatusCheck{Run Status?}
    
    StatusCheck -->|Queued| WaitState[Wait State]
    StatusCheck -->|In Progress| ProcessingState[Processing State]
    StatusCheck -->|Requires Action| ActionRequired[Action Required]
    StatusCheck -->|Completed| ExecutionComplete[Execution Complete]
    StatusCheck -->|Failed| ErrorHandling[Error Handling]
    
    WaitState --> StatusCheck
    ProcessingState --> StatusCheck
    
    %% Action Handling
    ActionRequired --> ActionType{Action Type?}
    ActionType -->|MCP Approval| MCPApproval[MCP Tool Approval<br/>Auto-approve with headers]
    ActionType -->|Function Call| FunctionExecution[Function Tool Execution]
    
    %% MCP Tool Approval Flow
    MCPApproval --> ApprovalSubmission[Submit Tool Approvals]
    ApprovalSubmission --> StatusCheck
    
    %% Function Tool Execution Flow
    FunctionExecution --> FunctionRouter{Function Name?}
    FunctionRouter -->|get_weather| WeatherExecution[Weather API Call<br/>Open-Meteo]
    FunctionRouter -->|fetch_stock_data| StockExecution[Stock API Call<br/>Yahoo Finance]
    FunctionRouter -->|Unknown| UnknownFunction[Unknown Function Error]
    
    WeatherExecution --> FunctionResults[Function Results Collection]
    StockExecution --> FunctionResults
    UnknownFunction --> FunctionResults
    
    FunctionResults --> OutputSubmission[Submit Tool Outputs]
    OutputSubmission --> StatusCheck
    
    %% Completion Flow
    ExecutionComplete --> ResultExtraction[Result Extraction]
    ResultExtraction --> MessageRetrieval[Message Retrieval]
    MessageRetrieval --> StepAnalysis[Step Analysis]
    StepAnalysis --> TokenUsage[Token Usage Collection]
    TokenUsage --> Cleanup[Agent Cleanup]
    Cleanup --> ResponseFormatting[Response Formatting]
    
    %% Error Handling
    ErrorHandling --> ErrorAnalysis[Error Analysis]
    ErrorAnalysis --> ErrorResponse[Error Response Formation]
    ErrorResponse --> ResponseFormatting
    
    %% Final Response
    ResponseFormatting --> StructuredResponse[Structured Response<br/>summary, details, steps, tokens]
    StructuredResponse --> UIDisplay[UI Display Processing]
    
    %% Styling
    classDef queryClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef coreClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef toolClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef executionClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef resultClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class UserQuery,QueryAnalysis queryClass
    class SingleAgentCore,AgentInit,AgentCreation,ThreadCreation coreClass
    class ToolRegistration,MCPTool,FunctionTool,ToolFlattening toolClass
    class ExecutionLoop,StatusCheck,ActionRequired,FunctionExecution executionClass
    class ResultExtraction,ResponseFormatting,StructuredResponse resultClass
```

### Single Agent Tool Integration Detail

```mermaid
graph TB
    %% Tool Configuration
    ToolConfig[Tool Configuration] --> MCPConfig[MCP Tool Configuration]
    ToolConfig --> FunctionConfig[Function Tool Configuration]
    
    %% MCP Tool Details
    MCPConfig --> MCPServer[MCP Server<br/>learn.microsoft.com/api/mcp]
    MCPConfig --> MCPLabel[Server Label<br/>MicrosoftLearn]
    MCPConfig --> MCPTools[Available Tools<br/>Documentation queries]
    
    %% Function Tool Details
    FunctionConfig --> WeatherFunc[get_weather Function<br/>City parameter]
    FunctionConfig --> StockFunc[fetch_stock_data Function<br/>Company parameter]
    FunctionConfig --> FunctionSet[Function Set Creation]
    
    %% Tool Definition Processing
    MCPTools --> MCPDefinitions[MCP Tool Definitions]
    FunctionSet --> FunctionDefinitions[Function Tool Definitions]
    MCPDefinitions --> DefinitionFlattening[Definition List Flattening]
    FunctionDefinitions --> DefinitionFlattening
    
    %% Agent Registration
    DefinitionFlattening --> AgentTools[Agent Tool Registration]
    MCPServer --> MCPResources[MCP Tool Resources]
    MCPResources --> AgentResources[Agent Resource Assignment]
    
    %% Tool Execution Paths
    AgentTools --> ToolExecution[Tool Execution Engine]
    ToolExecution --> MCPExecution[MCP Tool Execution<br/>Auto-approval required]
    ToolExecution --> FunctionExecution[Function Tool Execution<br/>Direct local call]
    
    %% MCP Execution Flow
    MCPExecution --> MCPRequest[MCP Protocol Request]
    MCPRequest --> MSLearnAPI[Microsoft Learn API]
    MSLearnAPI --> MCPResponse[MCP Protocol Response]
    MCPResponse --> MCPFormatting[Response Formatting]
    
    %% Function Execution Flow
    FunctionExecution --> LocalValidation[Parameter Validation]
    LocalValidation --> APICall[External API Call]
    APICall --> APIResponse[API Response]
    APIResponse --> LocalFormatting[Response Formatting]
    
    %% Results Collection
    MCPFormatting --> ResultsCollection[Results Collection]
    LocalFormatting --> ResultsCollection
    ResultsCollection --> FinalResponse[Final Agent Response]
    
    %% Styling
    classDef configClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef mcpClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef functionClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef executionClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class ToolConfig,MCPConfig,FunctionConfig configClass
    class MCPServer,MCPLabel,MCPTools,MCPDefinitions,MCPExecution mcpClass
    class WeatherFunc,StockFunc,FunctionSet,FunctionDefinitions,FunctionExecution functionClass
    class ToolExecution,APICall,ResultsCollection,FinalResponse executionClass
```

## Multi Agent Mode Flow

### Multi Agent Orchestration Architecture

```mermaid
graph TB
    %% User Request Processing
    UserRequest[User Request] --> RequestAnalysis[Request Analysis]
    RequestAnalysis --> MultiAgentCore[Multi Agent Core<br/>connected_agent&#40;&#41;]
    
    %% Specialized Agent Creation Phase
    MultiAgentCore --> AgentCreationPhase[Agent Creation Phase]
    AgentCreationPhase --> CreateBaseAgent[Create Base Agent<br/>basaeagent]
    AgentCreationPhase --> CreateStockAgent[Create Stock Agent<br/>Stockagent]
    AgentCreationPhase --> CreateRFPAgent[Create RFP Agent<br/>AISearchagent]
    AgentCreationPhase --> CreateSustainAgent[Create Sustainability Agent<br/>Sustainabilitypaperagent]
    AgentCreationPhase --> CreateMCPAgent[Create MCP Agent<br/>Mcplearnagent]
    
    %% Agent Configuration Details
    CreateBaseAgent --> BaseConfig[Base Agent Configuration<br/>Generic responses]
    CreateStockAgent --> StockConfig[Stock Agent Configuration<br/>Function tools: fetch_stock_data]
    CreateRFPAgent --> RFPConfig[RFP Agent Configuration<br/>Azure AI Search tools]
    CreateSustainAgent --> SustainConfig[Sustainability Agent Configuration<br/>File search tools, Vector store]
    CreateMCPAgent --> MCPConfig[MCP Agent Configuration<br/>Microsoft Learn MCP]
    
    %% Connected Agent Tool Registration
    BaseConfig --> ConnectedToolReg[Connected Agent Tool Registration]
    StockConfig --> ConnectedToolReg
    RFPConfig --> ConnectedToolReg
    SustainConfig --> ConnectedToolReg
    MCPConfig --> ConnectedToolReg
    
    %% Main Orchestrator Creation
    ConnectedToolReg --> OrchestratorCreation[Main Orchestrator Creation]
    OrchestratorCreation --> OrchestratorConfig[Orchestrator Configuration<br/>Connected agent tools<br/>Delegation instructions]
    
    %% Execution Phase
    OrchestratorConfig --> ExecutionPhase[Execution Phase]
    ExecutionPhase --> ThreadCreation[Conversation Thread Creation]
    ThreadCreation --> MessageSubmission[User Message Submission]
    MessageSubmission --> OrchestratorExecution[Orchestrator Execution<br/>create_and_process]
    
    %% Orchestration Flow
    OrchestratorExecution --> TaskAnalysis[Task Analysis<br/>Determine required capabilities]
    TaskAnalysis --> AgentSelection[Agent Selection<br/>Match tasks to agents]
    
    %% Agent Delegation
    AgentSelection --> DelegateToStock{Stock Data Needed?}
    AgentSelection --> DelegateToRFP{RFP Search Needed?}
    AgentSelection --> DelegateToSustain{Sustainability Info Needed?}
    AgentSelection --> DelegateToMCP{Technical Docs Needed?}
    AgentSelection --> DelegateToBase{Generic Processing Needed?}
    
    DelegateToStock -->|Yes| StockExecution[Stock Agent Execution<br/>fetch_stock_data function]
    DelegateToRFP -->|Yes| RFPExecution[RFP Agent Execution<br/>Azure AI Search query]
    DelegateToSustain -->|Yes| SustainExecution[Sustainability Agent Execution<br/>Vector store search]
    DelegateToMCP -->|Yes| MCPExecution[MCP Agent Execution<br/>Microsoft Learn query]
    DelegateToBase -->|Yes| BaseExecution[Base Agent Execution<br/>Generic response]
    
    %% Results Aggregation
    StockExecution --> ResultsAggregation[Results Aggregation<br/>Orchestrator coordination]
    RFPExecution --> ResultsAggregation
    SustainExecution --> ResultsAggregation
    MCPExecution --> ResultsAggregation
    BaseExecution --> ResultsAggregation
    
    %% Response Synthesis
    ResultsAggregation --> ResponseSynthesis[Response Synthesis<br/>Combine all agent outputs]
    ResponseSynthesis --> FinalResponse[Final Comprehensive Response]
    
    %% Cleanup Phase
    FinalResponse --> CleanupPhase[Cleanup Phase]
    CleanupPhase --> DeleteAgents[Delete All Created Agents]
    CleanupPhase --> DeleteThreads[Delete Conversation Threads]
    CleanupPhase --> DeleteFiles[Delete Uploaded Files]
    CleanupPhase --> DeleteVectorStores[Delete Vector Stores]
    
    %% UI Response
    DeleteVectorStores --> UIResponse[UI Response Formatting]
    UIResponse --> DisplayResults[Display in Streamlit UI]
    
    %% Styling
    classDef requestClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef creationClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef agentClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef executionClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef cleanupClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class UserRequest,RequestAnalysis,MultiAgentCore requestClass
    class AgentCreationPhase,CreateBaseAgent,CreateStockAgent,CreateRFPAgent creationClass
    class BaseConfig,StockConfig,RFPConfig,SustainConfig,MCPConfig agentClass
    class ExecutionPhase,TaskAnalysis,AgentSelection,ResultsAggregation executionClass
    class CleanupPhase,DeleteAgents,DeleteThreads,UIResponse cleanupClass
```

### Multi Agent Communication Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Orch as Main Orchestrator
    participant Stock as Stock Agent
    participant RFP as RFP Agent
    participant MCP as MCP Agent
    participant Azure as Azure AI Foundry
    participant ExtAPI as External APIs
    
    %% Initial Setup
    User->>UI: Submit complex query
    UI->>Orch: connected_agent(query)
    Note over Orch: Create specialized agents
    
    Orch->>Azure: Create Stock Agent with function tools
    Azure-->>Orch: Stock Agent ID
    
    Orch->>Azure: Create RFP Agent with search tools
    Azure-->>Orch: RFP Agent ID
    
    Orch->>Azure: Create MCP Agent with Learn tools
    Azure-->>Orch: MCP Agent ID
    
    Orch->>Azure: Create main orchestrator with connected tools
    Azure-->>Orch: Orchestrator Agent ID
    
    %% Query Processing
    Orch->>Azure: Create conversation thread
    Azure-->>Orch: Thread ID
    
    Orch->>Azure: Submit user message
    Orch->>Azure: Start orchestrator execution
    
    Note over Azure: Orchestrator analyzes query and determines required agents
    
    %% Agent Delegation
    Azure->>Stock: Delegate stock data request
    Stock->>ExtAPI: fetch_stock_data("Company")
    ExtAPI-->>Stock: Stock data response
    Stock-->>Azure: Stock information
    
    Azure->>RFP: Delegate RFP search request
    RFP->>Azure: Query RFP document index
    Azure-->>RFP: Search results
    RFP-->>Azure: RFP document summaries
    
    Azure->>MCP: Delegate technical documentation request
    MCP->>ExtAPI: Microsoft Learn MCP query
    ExtAPI-->>MCP: Documentation response
    MCP-->>Azure: Technical guidance
    
    %% Response Assembly
    Azure->>Orch: Aggregate all agent responses
    Note over Orch: Synthesize comprehensive response
    Orch-->>UI: Final response with all information
    
    %% Cleanup
    Orch->>Azure: Delete all created agents
    Orch->>Azure: Delete threads and resources
    Azure-->>Orch: Cleanup confirmation
    
    UI->>User: Display comprehensive results
```

## UI Component Architecture

### Streamlit UI Component Structure

```mermaid
graph TB
    %% Main UI Entry
    StreamlitApp[Streamlit Application<br/>stcondemoui.py] --> UIConfig[UI Configuration<br/>st.set_page_config]
    UIConfig --> SessionInit[Session State Initialization]
    
    %% Session State Components
    SessionInit --> ChatHistoryState[Chat History State<br/>st.session_state.chat_history]
    SessionInit --> RunsState[Runs State<br/>st.session_state.runs]
    SessionInit --> ModeState[Mode State<br/>st.session_state.last_mode]
    
    %% Main Layout Structure
    SessionInit --> MainLayout[Main Layout Structure]
    MainLayout --> TitleHeader[Title Header<br/>Agent Chat Demo]
    MainLayout --> SidebarConfig[Sidebar Configuration]
    MainLayout --> MainColumns[Main Columns Layout<br/>55% / 45% split]
    
    %% Sidebar Components
    SidebarConfig --> ModeSelector[Agent Mode Selector<br/>Single/Multi Radio Buttons]
    SidebarConfig --> ClearButton[Clear Chat/Reset Button]
    SidebarConfig --> EnvInfo[Environment Information]
    
    %% Left Column Components
    MainColumns --> LeftColumn[Left Column Container]
    LeftColumn --> SummaryContainer[Summary Container<br/>Height: 200px]
    LeftColumn --> HistoryContainer[History Container<br/>Height: 300px]
    
    %% Right Column Components
    MainColumns --> RightColumn[Right Column Container]
    RightColumn --> ToolsContainer[Tools & Agent Outputs<br/>Height: 520px]
    
    %% Chat Input Component
    MainLayout --> ChatInputComponent[Chat Input Component<br/>st.chat_input]
    
    %% Event Handlers
    ModeSelector --> ModeChangeHandler[Mode Change Handler<br/>Update session state]
    ClearButton --> ClearHandler[Clear Handler<br/>Reset all session state]
    ChatInputComponent --> MessageHandler[Message Handler<br/>Process user input]
    
    %% Message Processing Flow
    MessageHandler --> InputValidation[Input Validation]
    InputValidation --> ModeRouting[Mode Routing]
    ModeRouting --> SingleAgentCall[Single Agent Function Call<br/>single_agent&#40;&#41;]
    ModeRouting --> MultiAgentCall[Multi Agent Function Call<br/>connected_agent&#40;&#41;]
    
    %% Response Processing
    SingleAgentCall --> ResponseProcessor[Response Processor]
    MultiAgentCall --> ResponseProcessor
    ResponseProcessor --> SessionUpdate[Session State Update<br/>Add to chat_history and runs]
    SessionUpdate --> UIRerun[UI Rerun<br/>st.rerun&#40;&#41;]
    
    %% Display Rendering
    UIRerun --> RenderSummary[Render Summary<br/>Latest run metadata]
    UIRerun --> RenderHistory[Render History<br/>Chat messages with timestamps]
    UIRerun --> RenderTools[Render Tools<br/>Tool outputs and logs]
    
    %% Summary Display Details
    SummaryContainer --> LatestMode[Latest Mode Display]
    SummaryContainer --> SummaryText[Summary Text Display<br/>Truncated to 1200 chars]
    SummaryContainer --> TokenUsage[Token Usage Display<br/>Prompt/Completion/Total]
    
    %% History Display Details
    HistoryContainer --> MessageLoop[Message Iteration Loop]
    MessageLoop --> MessageRole[Message Role<br/>User/Assistant]
    MessageLoop --> MessageContent[Message Content]
    MessageLoop --> MessageTimestamp[Message Timestamp]
    MessageLoop --> MessageSeparator[Message Separator]
    
    %% Tools Display Details
    ToolsContainer --> RunLogs[Run Logs Expander<br/>Execution details]
    ToolsContainer --> ToolOutputs[Tool Outputs Display]
    ToolOutputs --> ToolLoop[Tool Iteration Loop]
    ToolLoop --> ToolName[Tool Name]
    ToolLoop --> ToolExpander[Tool Expander<br/>Individual tool details]
    ToolExpander --> ToolArguments[Tool Arguments<br/>JSON formatted]
    ToolExpander --> ToolOutput[Tool Output<br/>Truncated to 4000 chars]
    
    %% Styling
    classDef uiMainClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef stateClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef layoutClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef handlerClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef displayClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class StreamlitApp,UIConfig,MainLayout,TitleHeader uiMainClass
    class SessionInit,ChatHistoryState,RunsState,ModeState stateClass
    class SidebarConfig,MainColumns,LeftColumn,RightColumn layoutClass
    class ModeChangeHandler,ClearHandler,MessageHandler,ResponseProcessor handlerClass
    class RenderSummary,RenderHistory,RenderTools,ToolOutputs displayClass
```

### UI State Management Flow

```mermaid
stateDiagram-v2
    [*] --> AppInitialization: User loads page
    AppInitialization --> SessionStateCheck: Check session state
    SessionStateCheck --> InitializeDefaults: No existing state
    SessionStateCheck --> LoadExistingState: Existing state found
    
    InitializeDefaults --> WaitingForInput: Ready for user interaction
    LoadExistingState --> WaitingForInput: Ready for user interaction
    
    WaitingForInput --> ModeSelection: User selects agent mode
    WaitingForInput --> QueryInput: User enters query
    WaitingForInput --> ClearAction: User clicks clear
    
    ModeSelection --> UpdateModeState: Update session_state.last_mode
    UpdateModeState --> WaitingForInput: UI rerendered
    
    ClearAction --> ClearAllState: Clear chat_history and runs
    ClearAllState --> RerunUI: st.rerun()
    RerunUI --> WaitingForInput: UI refreshed
    
    QueryInput --> ValidateInput: Input validation
    ValidateInput --> InvalidInput: Validation failed
    ValidateInput --> ProcessQuery: Valid input
    
    InvalidInput --> WaitingForInput: Show error message
    
    ProcessQuery --> AddUserMessage: Add to chat_history
    AddUserMessage --> RouteToAgent: Determine agent mode
    
    RouteToAgent --> SingleAgentExecution: Single agent mode
    RouteToAgent --> MultiAgentExecution: Multi agent mode
    
    SingleAgentExecution --> ProcessSingleResult: single_agent() returns
    MultiAgentExecution --> ProcessMultiResult: connected_agent() returns
    
    ProcessSingleResult --> CreateRunRecord: Create run record
    ProcessMultiResult --> CreateRunRecord: Create run record
    
    CreateRunRecord --> AddAssistantMessage: Add response to chat_history
    AddAssistantMessage --> AddRunToState: Add run to session_state.runs
    AddRunToState --> TriggerRerun: st.rerun()
    TriggerRerun --> RenderUpdatedUI: Display updated state
    RenderUpdatedUI --> WaitingForInput: Ready for next interaction
    
    WaitingForInput --> SessionTimeout: Timeout or close
    SessionTimeout --> [*]: Session ends
```

## Tool Integration Patterns

### Tool Integration Architecture

```mermaid
graph TB
    %% Tool Integration Entry Points
    ToolIntegration[Tool Integration Layer] --> SingleAgentTools[Single Agent Tool Integration]
    ToolIntegration --> MultiAgentTools[Multi Agent Tool Integration]
    
    %% Single Agent Tool Pattern
    SingleAgentTools --> ToolRegistration[Tool Registration Pattern]
    ToolRegistration --> MCPRegistration[MCP Tool Registration]
    ToolRegistration --> FunctionRegistration[Function Tool Registration]
    ToolRegistration --> DefinitionFlattening[Tool Definition Flattening]
    
    %% MCP Tool Registration Details
    MCPRegistration --> MCPToolConfig[MCP Tool Configuration]
    MCPToolConfig --> MCPServerURL[Server URL<br/>learn.microsoft.com/api/mcp]
    MCPToolConfig --> MCPServerLabel[Server Label<br/>MicrosoftLearn]
    MCPToolConfig --> MCPAllowedTools[Allowed Tools<br/>Empty = All]
    MCPToolConfig --> MCPHeaders[Authentication Headers]
    
    %% Function Tool Registration Details
    FunctionRegistration --> FunctionDict[Function Dictionary]
    FunctionDict --> WeatherFunction[get_weather Function<br/>API: Open-Meteo]
    FunctionDict --> StockFunction[fetch_stock_data Function<br/>API: Yahoo Finance]
    FunctionDict --> FunctionToolCreation[FunctionTool Creation<br/>Azure AI Foundry]
    
    %% Multi Agent Tool Pattern
    MultiAgentTools --> SpecializedAgentCreation[Specialized Agent Creation]
    SpecializedAgentCreation --> StockAgentCreation[Stock Agent Creation<br/>Function tools]
    SpecializedAgentCreation --> RFPAgentCreation[RFP Agent Creation<br/>Search tools]
    SpecializedAgentCreation --> SustainAgentCreation[Sustainability Agent Creation<br/>File search tools]
    SpecializedAgentCreation --> MCPAgentCreation[MCP Agent Creation<br/>MCP tools]
    
    %% Connected Agent Tool Pattern
    SpecializedAgentCreation --> ConnectedToolPattern[Connected Agent Tool Pattern]
    ConnectedToolPattern --> ConnectedToolCreation[ConnectedAgentTool Creation]
    ConnectedToolCreation --> AgentIDMapping[Agent ID Mapping]
    ConnectedToolCreation --> ToolNaming[Tool Naming Strategy]
    ConnectedToolCreation --> ToolDescription[Tool Description]
    
    %% Tool Execution Patterns
    DefinitionFlattening --> SingleAgentExecution[Single Agent Tool Execution]
    ConnectedToolCreation --> MultiAgentExecution[Multi Agent Tool Execution]
    
    %% Single Agent Execution Flow
    SingleAgentExecution --> RequiresActionCheck[Requires Action Check]
    RequiresActionCheck --> MCPApprovalFlow[MCP Approval Flow<br/>Auto-approve]
    RequiresActionCheck --> FunctionExecutionFlow[Function Execution Flow<br/>Direct call]
    
    %% Multi Agent Execution Flow  
    MultiAgentExecution --> AgentOrchestration[Agent Orchestration]
    AgentOrchestration --> AgentSelection[Agent Selection Logic]
    AgentSelection --> AgentDelegation[Agent Delegation]
    AgentDelegation --> InterAgentCommunication[Inter-Agent Communication]
    InterAgentCommunication --> ResultAggregation[Result Aggregation]
    
    %% Tool Results Processing
    MCPApprovalFlow --> ToolResultsProcessing[Tool Results Processing]
    FunctionExecutionFlow --> ToolResultsProcessing
    ResultAggregation --> ToolResultsProcessing
    
    ToolResultsProcessing --> ResponseFormatting[Response Formatting]
    ResponseFormatting --> ErrorHandling[Error Handling]
    ResponseFormatting --> SuccessResponse[Success Response]
    
    %% Styling
    classDef integrationClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef singleClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef multiClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef executionClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef resultClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class ToolIntegration,ToolRegistration,ConnectedToolPattern integrationClass
    class SingleAgentTools,MCPRegistration,FunctionRegistration,DefinitionFlattening singleClass
    class MultiAgentTools,SpecializedAgentCreation,ConnectedToolCreation multiClass
    class SingleAgentExecution,MultiAgentExecution,AgentOrchestration executionClass
    class ToolResultsProcessing,ResponseFormatting,SuccessResponse resultClass
```

### Function Tool Execution Pattern

```mermaid
graph TD
    %% Function Tool Execution Entry
    FunctionCall[Function Tool Call Required] --> FunctionRouter[Function Router]
    FunctionRouter --> FunctionValidation[Function Name Validation]
    
    %% Function Type Routing
    FunctionValidation --> FunctionTypeCheck{Function Type?}
    FunctionTypeCheck -->|get_weather| WeatherFlow[Weather Function Flow]
    FunctionTypeCheck -->|fetch_stock_data| StockFlow[Stock Function Flow]
    FunctionTypeCheck -->|Unknown| UnknownFlow[Unknown Function Flow]
    
    %% Weather Function Flow
    WeatherFlow --> WeatherArgValidation[Weather Arguments Validation]
    WeatherArgValidation --> CityParameterCheck{City Parameter Valid?}
    CityParameterCheck -->|No| WeatherError[City Required Error]
    CityParameterCheck -->|Yes| WeatherAPICall[Weather API Call<br/>Open-Meteo]
    
    WeatherAPICall --> WeatherAPIResponse{API Response?}
    WeatherAPIResponse -->|Success| WeatherFormatting[Weather Data Formatting<br/>Temperature & Wind]
    WeatherAPIResponse -->|Failure| WeatherAPIError[Weather API Error]
    
    %% Stock Function Flow
    StockFlow --> StockArgValidation[Stock Arguments Validation]
    StockArgValidation --> CompanyParameterCheck{Company Parameter Valid?}
    CompanyParameterCheck -->|No| StockError[Company Required Error]
    CompanyParameterCheck -->|Yes| StockAPIFlow[Stock API Flow]
    
    StockAPIFlow --> TickerLookup[Company to Ticker Lookup<br/>Yahoo Finance Search]
    TickerLookup --> TickerFound{Ticker Found?}
    TickerFound -->|No| TickerError[Company Not Found Error]
    TickerFound -->|Yes| StockDataFetch[Stock Data Fetch<br/>7-day historical data]
    
    StockDataFetch --> StockAPIResponse{API Response?}
    StockAPIResponse -->|Success| StockFormatting[Stock Data Formatting<br/>Price & trends]
    StockAPIResponse -->|Failure| StockAPIError[Stock API Error]
    
    %% Unknown Function Flow
    UnknownFlow --> UnknownError[Unknown Function Error]
    
    %% Results Collection
    WeatherFormatting --> ResultsCollection[Results Collection]
    WeatherError --> ResultsCollection
    WeatherAPIError --> ResultsCollection
    StockFormatting --> ResultsCollection
    StockError --> ResultsCollection
    TickerError --> ResultsCollection
    StockAPIError --> ResultsCollection
    UnknownError --> ResultsCollection
    
    %% Tool Output Submission
    ResultsCollection --> ToolOutputFormatting[Tool Output Formatting]
    ToolOutputFormatting --> ToolOutputSubmission[Tool Output Submission<br/>submit_tool_outputs]
    ToolOutputSubmission --> ExecutionContinuation[Execution Continuation]
    
    %% Styling
    classDef routingClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef weatherClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef stockClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef errorClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef resultClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class FunctionCall,FunctionRouter,FunctionValidation,FunctionTypeCheck routingClass
    class WeatherFlow,WeatherArgValidation,WeatherAPICall,WeatherFormatting weatherClass
    class StockFlow,StockArgValidation,StockAPIFlow,StockFormatting stockClass
    class WeatherError,StockError,UnknownError,TickerError,WeatherAPIError,StockAPIError errorClass
    class ResultsCollection,ToolOutputFormatting,ToolOutputSubmission resultClass
```

## Sequence Diagrams

### Single Agent Query Processing Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant SA as single_agent()
    participant Azure as Azure AI Foundry
    participant MCP as MCP Server
    participant API as External APIs
    
    %% Initial Request
    User->>UI: Enter query: "Weather in Paris and Microsoft stock"
    UI->>UI: Add to chat_history
    UI->>SA: single_agent(query)
    
    %% Tool Setup
    SA->>SA: Initialize MCP tool (Microsoft Learn)
    SA->>SA: Initialize function tools (weather, stock)
    SA->>SA: Flatten tool definitions
    
    %% Agent Creation
    SA->>Azure: Create agent with tools
    Azure-->>SA: Agent ID
    SA->>Azure: Create thread
    Azure-->>SA: Thread ID
    SA->>Azure: Submit user message
    
    %% Execution Loop
    SA->>Azure: Create run
    Azure-->>SA: Run ID (status: queued)
    
    loop Execution Monitoring
        SA->>Azure: Get run status
        Azure-->>SA: Status update
        
        alt Status: requires_action
            Azure-->>SA: Required action details
            
            alt MCP Tool Approval
                SA->>SA: Create tool approval
                SA->>Azure: Submit tool approvals
            else Function Tool Execution
                SA->>SA: Parse function call
                
                alt get_weather call
                    SA->>API: Open-Meteo API call
                    API-->>SA: Weather data
                else fetch_stock_data call
                    SA->>API: Yahoo Finance API call
                    API-->>SA: Stock data
                end
                
                SA->>Azure: Submit tool outputs
            end
        else Status: completed
            SA->>Azure: Get messages
            Azure-->>SA: Final response
            SA->>SA: Extract results and metadata
        end
    end
    
    %% Cleanup and Response
    SA->>Azure: Delete agent
    SA->>SA: Format structured response
    SA-->>UI: Return response object
    UI->>UI: Update session state
    UI->>UI: Display results
    UI-->>User: Show response in chat
```

### Multi Agent Orchestration Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant MA as connected_agent()
    participant Orch as Orchestrator
    participant SA as Stock Agent
    participant RA as RFP Agent
    participant Azure as Azure AI Foundry
    participant API as External APIs
    
    %% Initial Request
    User->>UI: Enter complex query
    UI->>MA: connected_agent(query)
    
    %% Agent Creation Phase
    MA->>Azure: Create base agent
    Azure-->>MA: Base agent ID
    
    MA->>Azure: Create stock agent with function tools
    Azure-->>MA: Stock agent ID
    
    MA->>Azure: Create RFP agent with search tools  
    Azure-->>MA: RFP agent ID
    
    MA->>Azure: Create sustainability agent with file tools
    Azure-->>MA: Sustainability agent ID
    
    MA->>Azure: Create MCP agent with Learn tools
    Azure-->>MA: MCP agent ID
    
    %% Orchestrator Setup
    MA->>MA: Create connected agent tools list
    MA->>Azure: Create orchestrator with connected tools
    Azure-->>MA: Orchestrator ID
    
    %% Execution Phase
    MA->>Azure: Create conversation thread
    Azure-->>MA: Thread ID
    MA->>Azure: Submit user message
    MA->>Azure: Start orchestrator execution
    
    %% Orchestration Flow
    Azure->>Orch: Analyze user request
    Orch->>Orch: Determine required agents
    
    %% Agent Delegation
    alt Stock information needed
        Orch->>SA: Delegate stock data request
        SA->>API: Yahoo Finance API
        API-->>SA: Stock data
        SA-->>Orch: Stock information
    end
    
    alt RFP documents needed
        Orch->>RA: Delegate document search
        RA->>Azure: Azure AI Search query
        Azure-->>RA: Search results
        RA-->>Orch: Document summaries
    end
    
    %% Response Assembly
    Orch->>Orch: Aggregate all agent responses
    Orch->>Azure: Generate comprehensive response
    Azure-->>MA: Final orchestrated response
    
    %% Cleanup Phase
    MA->>Azure: Delete all created agents
    MA->>Azure: Delete threads and resources
    Azure-->>MA: Cleanup confirmation
    
    %% Response to UI
    MA-->>UI: Return aggregated response
    UI->>UI: Update session state
    UI->>UI: Display comprehensive results
    UI-->>User: Show multi-agent response
```

## State Management Diagrams

### Session State Lifecycle

```mermaid
stateDiagram-v2
    [*] --> AppStart: User accesses application
    
    AppStart --> StateInitialization: Initialize session state
    StateInitialization --> DefaultsSet: Set default values
    
    DefaultsSet --> ChatHistoryEmpty: chat_history = []
    DefaultsSet --> RunsEmpty: runs = []
    DefaultsSet --> ModeDefault: last_mode = "Single Agent"
    
    ChatHistoryEmpty --> ReadyState: Application ready
    RunsEmpty --> ReadyState
    ModeDefault --> ReadyState
    
    ReadyState --> UserInteraction: Waiting for user input
    
    UserInteraction --> ModeChange: User changes agent mode
    UserInteraction --> QuerySubmission: User submits query
    UserInteraction --> ClearRequest: User clicks clear
    
    ModeChange --> ModeUpdate: Update last_mode
    ModeUpdate --> ReadyState: UI re-renders
    
    ClearRequest --> StateClear: Clear all session data
    StateClear --> DefaultsSet: Reset to defaults
    
    QuerySubmission --> ProcessingState: Execute agent function
    ProcessingState --> AgentExecution: Run single_agent() or connected_agent()
    
    AgentExecution --> ExecutionSuccess: Agent returns response
    AgentExecution --> ExecutionError: Agent encounters error
    
    ExecutionSuccess --> UpdateChatHistory: Add user & assistant messages
    ExecutionError --> UpdateChatHistory: Add error message
    
    UpdateChatHistory --> UpdateRunRecords: Add run metadata
    UpdateRunRecords --> UIRerender: Trigger st.rerun()
    UIRerender --> ReadyState: Display updated state
    
    ReadyState --> SessionEnd: User closes/timeout
    SessionEnd --> [*]: Session terminated
```

### Chat History State Management

```mermaid
graph TB
    %% Chat History Entry Points
    ChatHistoryMgmt[Chat History Management] --> AddUserMessage[Add User Message]
    ChatHistoryMgmt --> AddAssistantMessage[Add Assistant Message]
    ChatHistoryMgmt --> RenderHistory[Render History]
    ChatHistoryMgmt --> ClearHistory[Clear History]
    
    %% Add User Message Flow
    AddUserMessage --> UserValidation[User Input Validation]
    UserValidation --> CreateUserRecord[Create User Message Record]
    CreateUserRecord --> UserTimestamp[Add Timestamp]
    UserTimestamp --> AppendToHistory[Append to chat_history]
    
    %% Add Assistant Message Flow
    AddAssistantMessage --> AssistantResponse[Process Agent Response]
    AssistantResponse --> CreateAssistantRecord[Create Assistant Message Record]
    CreateAssistantRecord --> AssistantTimestamp[Add Timestamp]
    AssistantTimestamp --> AppendToHistory
    
    %% Message Record Structure
    AppendToHistory --> MessageStructure[Message Structure]
    MessageStructure --> RoleField[role: user/assistant]
    MessageStructure --> ContentField[content: message text]
    MessageStructure --> TimestampField[timestamp: HH:MM:SS]
    
    %% Render History Flow
    RenderHistory --> HistoryIteration[Iterate Through Messages]
    HistoryIteration --> MessageFormatting[Format Each Message]
    MessageFormatting --> RoleLabel[Display Role Label]
    MessageFormatting --> ContentDisplay[Display Content]
    MessageFormatting --> TimestampDisplay[Display Timestamp]
    MessageFormatting --> MessageSeparator[Add Separator]
    
    %% Clear History Flow
    ClearHistory --> HistoryReset[Reset chat_history to empty array]
    HistoryReset --> UIRefresh[Trigger UI Refresh]
    
    %% Memory Management
    AppendToHistory --> MemoryCheck[Check History Length]
    MemoryCheck --> HistoryLimitCheck{Length > MAX_HISTORY?}
    HistoryLimitCheck -->|Yes| TrimHistory[Trim Oldest Messages]
    HistoryLimitCheck -->|No| MemoryOptimized[Memory Optimized]
    TrimHistory --> MemoryOptimized
    
    %% State Persistence
    MemoryOptimized --> SessionPersistence[Session Persistence]
    SessionPersistence --> StateUpdated[Session State Updated]
    
    %% Styling
    classDef managementClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef messageClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef renderClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef memoryClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class ChatHistoryMgmt,AddUserMessage,AddAssistantMessage managementClass
    class CreateUserRecord,CreateAssistantRecord,MessageStructure messageClass
    class RenderHistory,HistoryIteration,MessageFormatting renderClass
    class MemoryCheck,HistoryLimitCheck,TrimHistory,MemoryOptimized memoryClass
```

## Error Handling Flows

### Comprehensive Error Handling Architecture

```mermaid
graph TB
    %% Error Entry Points
    ErrorSystem[Error Handling System] --> AgentErrors[Agent Execution Errors]
    ErrorSystem --> UIErrors[UI Interaction Errors]
    ErrorSystem --> ExternalErrors[External Service Errors]
    ErrorSystem --> ValidationErrors[Input Validation Errors]
    
    %% Agent Execution Error Flow
    AgentErrors --> AgentErrorType{Agent Error Type?}
    AgentErrorType -->|Authentication| AuthError[Authentication Error<br/>401/403 responses]
    AgentErrorType -->|Rate Limiting| RateError[Rate Limiting Error<br/>429 responses]
    AgentErrorType -->|Tool Execution| ToolError[Tool Execution Error<br/>Function failures]
    AgentErrorType -->|Model| ModelError[Model Error<br/>Model not found/unavailable]
    AgentErrorType -->|Timeout| TimeoutError[Timeout Error<br/>Long running operations]
    
    %% Authentication Error Handling
    AuthError --> AuthErrorHandler[Authentication Error Handler]
    AuthErrorHandler --> CheckCredentials[Check Azure Credentials]
    AuthErrorHandler --> AuthErrorResponse[Generate Auth Error Message]
    AuthErrorResponse --> AuthRecovery[Suggest Credential Fix]
    
    %% Rate Limiting Error Handling
    RateError --> RateErrorHandler[Rate Limiting Error Handler]
    RateErrorHandler --> BackoffStrategy[Implement Backoff Strategy]
    RateErrorHandler --> RateErrorResponse[Generate Rate Limit Message]
    RateErrorResponse --> RateRecovery[Suggest Retry Later]
    
    %% Tool Execution Error Handling
    ToolError --> ToolErrorHandler[Tool Error Handler]
    ToolErrorHandler --> ToolErrorType{Tool Error Type?}
    ToolErrorType -->|Function Error| FunctionErrorFlow[Function Error Flow]
    ToolErrorType -->|MCP Error| MCPErrorFlow[MCP Error Flow]
    ToolErrorType -->|External API Error| APIErrorFlow[External API Error Flow]
    
    %% Function Error Flow
    FunctionErrorFlow --> FunctionValidation[Function Parameter Validation]
    FunctionValidation --> FunctionErrorResponse[Generate Function Error Message]
    FunctionErrorResponse --> FunctionRecovery[Suggest Parameter Fix]
    
    %% MCP Error Flow
    MCPErrorFlow --> MCPConnectivityCheck[Check MCP Server Connectivity]
    MCPConnectivityCheck --> MCPErrorResponse[Generate MCP Error Message]
    MCPErrorResponse --> MCPRecovery[Suggest Network Check]
    
    %% External API Error Flow
    APIErrorFlow --> APIConnectivityCheck[Check External API Connectivity]
    APIConnectivityCheck --> APIErrorResponse[Generate API Error Message]
    APIErrorResponse --> APIRecovery[Suggest API Status Check]
    
    %% Model Error Handling
    ModelError --> ModelErrorHandler[Model Error Handler]
    ModelErrorHandler --> ModelValidation[Model Deployment Validation]
    ModelValidation --> ModelErrorResponse[Generate Model Error Message]
    ModelErrorResponse --> ModelRecovery[Suggest Model Check]
    
    %% Timeout Error Handling
    TimeoutError --> TimeoutErrorHandler[Timeout Error Handler]
    TimeoutErrorHandler --> TimeoutAnalysis[Analyze Timeout Cause]
    TimeoutAnalysis --> TimeoutErrorResponse[Generate Timeout Error Message]
    TimeoutErrorResponse --> TimeoutRecovery[Suggest Shorter Query]
    
    %% UI Error Handling
    UIErrors --> UIErrorType{UI Error Type?}
    UIErrorType -->|Input Validation| InputValidationError[Input Validation Error]
    UIErrorType -->|Session State| SessionStateError[Session State Error]
    UIErrorType -->|Display| DisplayError[Display Error]
    
    %% Input Validation Error Flow
    InputValidationError --> InputValidationHandler[Input Validation Handler]
    InputValidationHandler --> ValidationRules[Apply Validation Rules]
    ValidationRules --> ValidationErrorResponse[Generate Validation Error]
    ValidationErrorResponse --> ValidationRecovery[Suggest Input Fix]
    
    %% Session State Error Flow
    SessionStateError --> SessionErrorHandler[Session State Error Handler]
    SessionErrorHandler --> StateRecovery[Attempt State Recovery]
    StateRecovery --> StateErrorResponse[Generate State Error Message]
    StateErrorResponse --> StateReset[Suggest State Reset]
    
    %% External Service Error Flow
    ExternalErrors --> ExternalErrorType{External Service Type?}
    ExternalErrorType -->|Weather API| WeatherServiceError[Weather Service Error]
    ExternalErrorType -->|Stock API| StockServiceError[Stock Service Error]
    ExternalErrorType -->|Azure Service| AzureServiceError[Azure Service Error]
    
    %% Error Response Assembly
    AuthRecovery --> ErrorResponseAssembly[Error Response Assembly]
    RateRecovery --> ErrorResponseAssembly
    FunctionRecovery --> ErrorResponseAssembly
    MCPRecovery --> ErrorResponseAssembly
    APIRecovery --> ErrorResponseAssembly
    ModelRecovery --> ErrorResponseAssembly
    TimeoutRecovery --> ErrorResponseAssembly
    ValidationRecovery --> ErrorResponseAssembly
    StateReset --> ErrorResponseAssembly
    
    %% Final Error Response
    ErrorResponseAssembly --> ErrorFormatting[Error Message Formatting]
    ErrorFormatting --> ErrorLogging[Error Logging]
    ErrorLogging --> UserErrorDisplay[User Error Display]
    UserErrorDisplay --> ErrorRecoveryGuidance[Recovery Guidance]
    
    %% Styling
    classDef errorTypeClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef handlerClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef responseClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef recoveryClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    
    class AgentErrors,UIErrors,ExternalErrors,ValidationErrors errorTypeClass
    class AuthErrorHandler,RateErrorHandler,ToolErrorHandler,ModelErrorHandler handlerClass
    class AuthErrorResponse,RateErrorResponse,ModelErrorResponse,ValidationErrorResponse responseClass
    class AuthRecovery,RateRecovery,ModelRecovery,ValidationRecovery,ErrorRecoveryGuidance recoveryClass
```

### Error Recovery Strategies

```mermaid
graph TB
    %% Error Recovery Entry
    ErrorRecoverySystem[Error Recovery System] --> ErrorClassification[Error Classification]
    
    %% Error Classification
    ErrorClassification --> RecoverableErrors[Recoverable Errors]
    ErrorClassification --> NonRecoverableErrors[Non-Recoverable Errors]
    
    %% Recoverable Error Strategies
    RecoverableErrors --> RetryStrategy[Retry Strategy]
    RecoverableErrors --> FallbackStrategy[Fallback Strategy]
    RecoverableErrors --> DegradedStrategy[Degraded Service Strategy]
    
    %% Retry Strategy Implementation
    RetryStrategy --> ExponentialBackoff[Exponential Backoff]
    RetryStrategy --> MaxRetryLimit[Max Retry Limit Check]
    RetryStrategy --> RetryCondition[Retry Condition Evaluation]
    
    ExponentialBackoff --> BackoffDelay[Calculate Delay: 2^attempt]
    MaxRetryLimit --> RetryLimitCheck{Retry < Max Retries?}
    RetryLimitCheck -->|Yes| AttemptRetry[Attempt Operation Retry]
    RetryLimitCheck -->|No| RetryExhausted[Retry Limit Exhausted]
    
    AttemptRetry --> RetryResult{Retry Success?}
    RetryResult -->|Success| RetrySuccess[Retry Successful]
    RetryResult -->|Failure| RetryStrategy
    
    %% Fallback Strategy Implementation
    FallbackStrategy --> FallbackOptions[Evaluate Fallback Options]
    FallbackOptions --> AlternativeService[Alternative Service]
    FallbackOptions --> CachedResponse[Cached Response]
    FallbackOptions --> DefaultResponse[Default Response]
    
    AlternativeService --> AlternativeAttempt[Attempt Alternative]
    CachedResponse --> CacheCheck[Check Cache Validity]
    DefaultResponse --> DefaultGeneration[Generate Default Response]
    
    %% Degraded Service Strategy
    DegradedStrategy --> ReducedFunctionality[Reduced Functionality Mode]
    DegradedStrategy --> PartialResponse[Partial Response Mode]
    DegradedStrategy --> OfflineMode[Offline Mode]
    
    ReducedFunctionality --> DisableFeatures[Disable Non-Essential Features]
    PartialResponse --> PartialResults[Return Available Results]
    OfflineMode --> LocalProcessing[Local Processing Only]
    
    %% Non-Recoverable Error Handling
    NonRecoverableErrors --> UserNotification[User Notification]
    NonRecoverableErrors --> GracefulDegradation[Graceful Degradation]
    NonRecoverableErrors --> ErrorReporting[Error Reporting]
    
    UserNotification --> ClearErrorMessage[Clear Error Message]
    UserNotification --> ActionableGuidance[Actionable Guidance]
    UserNotification --> ContactInformation[Contact Information]
    
    GracefulDegradation --> SafeState[Return to Safe State]
    GracefulDegradation --> PreserveUserData[Preserve User Data]
    GracefulDegradation --> MinimalFunctionality[Minimal Functionality]
    
    %% Recovery Success Paths
    RetrySuccess --> RecoveryComplete[Recovery Complete]
    AlternativeAttempt --> RecoveryComplete
    CacheCheck --> RecoveryComplete
    DefaultGeneration --> RecoveryComplete
    DisableFeatures --> RecoveryComplete
    PartialResults --> RecoveryComplete
    LocalProcessing --> RecoveryComplete
    
    %% Recovery Failure Paths
    RetryExhausted --> FallbackStrategy
    FallbackStrategy --> DegradedStrategy
    DegradedStrategy --> NonRecoverableErrors
    
    %% Final States
    RecoveryComplete --> ContinueOperation[Continue Normal Operation]
    ClearErrorMessage --> UserRecoveryAction[User Recovery Action]
    SafeState --> ManualIntervention[Manual Intervention Required]
    
    %% Styling
    classDef recoveryClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef strategyClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef fallbackClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef errorClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class ErrorRecoverySystem,RecoverableErrors,RecoveryComplete recoveryClass
    class RetryStrategy,FallbackStrategy,DegradedStrategy strategyClass
    class AlternativeService,CachedResponse,DefaultResponse,PartialResponse fallbackClass
    class NonRecoverableErrors,RetryExhausted,ManualIntervention errorClass
```

---

*These Mermaid diagrams provide comprehensive visual documentation of the Agent Demo system architecture, covering all major components, flows, and interaction patterns. The diagrams are designed to be viewed in Mermaid-compatible environments and serve as interactive documentation for understanding the system's design and operation.*