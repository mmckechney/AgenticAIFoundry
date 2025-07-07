# AgenticAIFoundry - Mermaid Architecture Diagram

This document contains comprehensive mermaid diagrams showing the complete architecture of the AgenticAIFoundry platform, including all connected agents, evaluation frameworks, red team testing, and external integrations.

## Viewing the Diagrams

These mermaid diagrams can be viewed in several ways:

1. **GitHub**: The diagrams should render automatically when viewing this file on GitHub
2. **VS Code**: Install the "Mermaid Markdown Syntax Highlighting" extension
3. **Online Viewers**: Copy the mermaid code to [mermaid.live](https://mermaid.live) or [mermaid-js.github.io](https://mermaid-js.github.io/mermaid-live-editor)
4. **Local Tools**: Use mermaid CLI tools or browser extensions that support mermaid rendering

> **Note**: If the diagrams don't render properly in your environment, you can copy the mermaid code blocks to any online mermaid viewer for proper visualization.

## Complete System Architecture

```mermaid
graph TB
    %% Main Controller
    User[User Request] --> Main[Main Controller<br/>agenticai.py]
    User --> MCPInterface[MCP Voice Interface<br/>bbmcp.py]
    User --> VisionInterface[Vision Analysis Interface<br/>stdrawing.py]
    
    %% Core Agent Ecosystem
    Main --> AgentManager[Agent Manager]
    AgentManager --> CodeAgent[Code Interpreter Agent<br/>code_interpreter]
    AgentManager --> SearchAgent[AI Search Agent<br/>ai_search_agent]
    AgentManager --> ConnectedAgent[Connected Agent<br/>connected_agent]
    AgentManager --> ReasoningAgent[Reasoning Agent<br/>process_message_reasoning]
    AgentManager --> WeatherAgent[Weather Agent<br/>fetch_weather]
    AgentManager --> MultiAgentTeam[Multi-Agent Team<br/>sample_agents_multi_agent_team]
    
    %% MCP Integration Layer
    MCPInterface --> MCPManager[MCP Protocol Manager]
    MCPManager --> MSFTLearnMCP[Microsoft Learn MCP<br/>msft_generate_chat_response]
    MCPManager --> GitHubMCP[GitHub Copilot MCP<br/>bbgithub_generate_chat_response]
    MCPManager --> HuggingFaceMCP[HuggingFace MCP<br/>hf_generate_chat_response]
    
    %% Vision Analysis Layer
    VisionInterface --> VisionManager[Vision Analysis Manager]
    VisionManager --> AzureVision[Azure GPT-4.1 Vision<br/>analyze_with_azure]
    VisionManager --> O3Vision[O3 Vision Model<br/>analyze_with_o3]
    VisionManager --> ImageProcessor[Image Processing<br/>image_to_base64]
    
    %% Voice Interface Components
    MCPInterface --> VoiceInput[Audio Input<br/>save_audio_file]
    MCPInterface --> Transcription[Speech-to-Text<br/>transcribe_audio]
    MCPInterface --> TextToSpeech[Text-to-Speech<br/>generate_audio_response_gpt]
    MCPInterface --> ChatHistory[Chat History Management]
    
    %% Evaluation Framework
    Main --> EvalFramework[Evaluation Framework<br/>eval]
    EvalFramework --> QualityEval[Quality Evaluators]
    EvalFramework --> SafetyEval[Safety Evaluators]
    EvalFramework --> AgenticEval[Agentic Evaluators<br/>agent_eval]
    EvalFramework --> AdvancedEval[Advanced Metrics]
    
    %% Quality Evaluators Details
    QualityEval --> Relevance[Relevance Evaluator]
    QualityEval --> Coherence[Coherence Evaluator]
    QualityEval --> Groundedness[Groundedness Evaluator]
    QualityEval --> Fluency[Fluency Evaluator]
    QualityEval --> Similarity[Similarity Evaluator]
    
    %% Safety Evaluators Details
    SafetyEval --> ContentSafety[Content Safety Evaluator]
    SafetyEval --> Violence[Violence Evaluator]
    SafetyEval --> HateUnfairness[Hate/Unfairness Evaluator]
    SafetyEval --> Sexual[Sexual Content Evaluator]
    SafetyEval --> SelfHarm[Self-Harm Evaluator]
    SafetyEval --> IndirectAttack[Indirect Attack Evaluator]
    SafetyEval --> ProtectedMaterial[Protected Material Evaluator]
    
    %% Agentic Evaluators Details
    AgenticEval --> IntentResolution[Intent Resolution Evaluator]
    AgenticEval --> TaskAdherence[Task Adherence Evaluator]
    AgenticEval --> ToolCallAccuracy[Tool Call Accuracy Evaluator]
    
    %% Advanced Metrics Details
    AdvancedEval --> BLEU[BLEU Score Evaluator]
    AdvancedEval --> GLEU[GLEU Score Evaluator]
    AdvancedEval --> ROUGE[ROUGE Score Evaluator]
    AdvancedEval --> METEOR[METEOR Score Evaluator]
    AdvancedEval --> F1Score[F1 Score Evaluator]
    AdvancedEval --> Retrieval[Retrieval Evaluator]
    AdvancedEval --> GroundnessPro[Groundedness Pro Evaluator]
    
    %% Red Team Security Testing
    Main --> RedTeam[Red Team Framework<br/>redteam]
    RedTeam --> RiskCategories[Risk Categories]
    RedTeam --> AttackStrategies[Attack Strategies]
    RedTeam --> TargetSystems[Target Systems]
    
    %% Risk Categories Details
    RiskCategories --> ViolenceRisk[Violence]
    RiskCategories --> HateRisk[Hate/Unfairness]
    RiskCategories --> SexualRisk[Sexual Content]
    RiskCategories --> SelfHarmRisk[Self-Harm]
    
    %% Attack Strategies Details
    AttackStrategies --> EasyAttack[Easy Complexity]
    AttackStrategies --> ModerateAttack[Moderate Complexity]
    AttackStrategies --> CharManip[Character Manipulation]
    AttackStrategies --> Encoding[Encoding Attacks<br/>ROT13, Base64, Binary]
    AttackStrategies --> UnicodeAttack[Unicode Confusables]
    AttackStrategies --> FlipAttack[Flip Strategy]
    
    %% Target Systems Details
    TargetSystems --> SimpleCallback[Simple Callback Target]
    TargetSystems --> AdvancedCallback[Advanced Callback Target]
    TargetSystems --> ModelConfig[Azure OpenAI Model Config]
    
    %% Connected Agent Sub-components
    ConnectedAgent --> StockAgent[Stock Price Agent]
    ConnectedAgent --> EmailAgent[Email Agent<br/>send_email]
    ConnectedAgent --> RFPAgent[RFP Search Agent]
    ConnectedAgent --> MainOrchestrator[Main Orchestrator Agent]
    
    %% Azure AI Foundry Platform
    AgentManager --> AzureFoundry[Azure AI Foundry Platform]
    EvalFramework --> AzureFoundry
    RedTeam --> AzureFoundry
    
    AzureFoundry --> AgentMgmt[Agent Management]
    AzureFoundry --> ThreadMgmt[Thread Management]
    AzureFoundry --> MessageProc[Message Processing]
    AzureFoundry --> ToolExecution[Tool Execution Engine]
    
    %% Azure Services
    AzureFoundry --> AzureOpenAI[Azure OpenAI Services]
    AzureFoundry --> AzureSearch[Azure AI Search]
    AzureFoundry --> AzureIdentity[Azure Identity]
    AzureFoundry --> AzureCognitive[Azure Cognitive Services]
    
    %% Azure OpenAI Models
    AzureOpenAI --> GPT4Models[GPT-4 Models]
    AzureOpenAI --> O1Models[O1 Series Models<br/>Reasoning]
    AzureOpenAI --> O4Models[O4 Mini Models]
    
    %% Azure AI Search Components
    AzureSearch --> SearchIndex[Construction RFP Docs Index]
    AzureSearch --> VectorDB[Vector Database Connection]
    AzureSearch --> SimpleQuery[Simple Query Type]
    
    %% External Services Integration
    ConnectedAgent --> ExternalServices[External Services]
    ExternalServices --> GmailSMTP[Gmail SMTP<br/>Email Service]
    ExternalServices --> StockAPIs[Stock Price APIs]
    ExternalServices --> CustomAPIs[Custom APIs]
    ExternalServices --> FileSystem[File System<br/>Data Storage]
    
    %% MCP External Services
    MCPManager --> MCPServices[MCP Protocol Services]
    MCPServices --> MSFTLearnAPI[Microsoft Learn API<br/>learn.microsoft.com/api/mcp]
    MCPServices --> GitHubCopilotAPI[GitHub Copilot API<br/>api.githubcopilot.com/mcp/]
    MCPServices --> HuggingFaceAPI[HuggingFace API<br/>hf.co/mcp]
    
    %% Voice Processing Services
    MCPInterface --> VoiceServices[Voice Processing Services]
    VoiceServices --> WhisperAPI[Azure OpenAI Whisper<br/>Speech-to-Text]
    VoiceServices --> TTSAPI[Azure OpenAI TTS<br/>Text-to-Speech]
    
    %% Tool Systems
    CodeAgent --> CodeTool[Code Interpreter Tool]
    SearchAgent --> SearchTool[Azure AI Search Tool]
    ConnectedAgent --> ConnectedTools[Connected Agent Tools]
    WeatherAgent --> FunctionTool[Function Tool]
    
    %% Tool Details
    CodeTool --> PythonExec[Python Execution Engine]
    CodeTool --> DataAnalysis[Data Analysis<br/>Pandas, NumPy, Matplotlib]
    CodeTool --> Visualization[Visualization Tools]
    
    SearchTool --> QueryProcessor[Query Processor]
    SearchTool --> ResultRanker[Result Ranker]
    SearchTool --> TopKRetrieval[Top-K Retrieval]
    
    ConnectedTools --> StockTool[Stock Price Tool]
    ConnectedTools --> EmailTool[Email Tool]
    ConnectedTools --> SearchConnTool[Search Connected Tool]
    
    %% Monitoring and Telemetry
    Main --> Monitoring[Monitoring & Telemetry]
    Monitoring --> OpenTelemetry[OpenTelemetry Integration]
    Monitoring --> AzureMonitor[Azure Monitor]
    Monitoring --> Tracing[Request Tracing]
    Monitoring --> Performance[Performance Monitoring]
    
    %% Data Flow and Storage
    EvalFramework --> DataStorage[Data Storage]
    RedTeam --> DataStorage
    DataStorage --> JSONLFiles[JSONL Input Files]
    DataStorage --> JSONResults[JSON Result Files]
    DataStorage --> LogFiles[Log Files]
    DataStorage --> ConfigFiles[Configuration Files<br/>.env]
    
    %% Results and Outputs
    EvalFramework --> EvalResults[Evaluation Results]
    RedTeam --> SecurityResults[Security Scan Results]
    AgentManager --> AgentResponses[Agent Responses]
    
    EvalResults --> MetricsReport[Metrics Report]
    EvalResults --> StudioURL[AI Foundry Studio URL]
    SecurityResults --> VulnAssessment[Vulnerability Assessment]
    SecurityResults --> RiskScoring[Risk Scoring]
    SecurityResults --> ComplianceReport[Compliance Report]
    
    %% Styling
    classDef agentClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef evalClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef securityClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef azureClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef dataClass fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    
    class CodeAgent,SearchAgent,ConnectedAgent,ReasoningAgent,WeatherAgent,AgentManager agentClass
    class EvalFramework,QualityEval,SafetyEval,AgenticEval,AdvancedEval evalClass
    class RedTeam,RiskCategories,AttackStrategies,SecurityResults securityClass
    class AzureFoundry,AzureOpenAI,AzureSearch,AzureIdentity azureClass
    class ExternalServices,GmailSMTP,StockAPIs externalClass
    class DataStorage,JSONLFiles,JSONResults dataClass
    class MCPInterface,MCPManager,MSFTLearnMCP,GitHubMCP,HuggingFaceMCP mcpClass
    class VoiceInput,Transcription,TextToSpeech,ChatHistory voiceClass
    class VisionInterface,VisionManager,AzureVision,O3Vision,ImageProcessor visionClass
```

## Multi-Agent Team Coordination Architecture

```mermaid
graph TB
    %% User Request Entry
    UserReq[User Request] --> TeamEntry[AgentTeam Entry Point]
    
    %% AgentTeam Framework
    TeamEntry --> AgentTeam[AgentTeam Controller<br/>agent_team.py]
    AgentTeam --> TeamLeader[Team Leader Agent<br/>Auto-generated]
    
    %% Team Assembly Process
    AgentTeam --> TeamAssembly[Team Assembly Process]
    TeamAssembly --> CreateMembers[Create Team Members]
    TeamAssembly --> ConfigureTools[Configure Agent Tools]
    TeamAssembly --> SetupDelegation[Setup Delegation Rules]
    
    %% Specialized Agents
    CreateMembers --> TimeWeatherAgent[TimeWeatherAgent<br/>Time & Weather]
    CreateMembers --> EmailAgent[SendEmailAgent<br/>Email Services]
    CreateMembers --> TempAgent[TemperatureAgent<br/>Unit Conversion]
    
    %% Tool Integration
    TimeWeatherAgent --> TimeTool[fetch_current_datetime]
    TimeWeatherAgent --> WeatherTool[fetch_weather]
    EmailAgent --> EmailTool[send_email_using_recipient_name]
    TempAgent --> TempTool[convert_temperature]
    
    %% Task Delegation Flow
    TeamLeader --> TaskAnalysis[Analyze Request]
    TaskAnalysis --> CreateTask[Create Task]
    CreateTask --> SelectAgent[Select Best Agent]
    SelectAgent --> ExecuteTask[Execute Task]
    
    %% Task Queue Management
    CreateTask --> TaskQueue[Task Queue]
    TaskQueue --> TaskProcessor[Task Processor]
    TaskProcessor --> AgentAssignment[Agent Assignment]
    
    %% Inter-Agent Communication
    AgentAssignment --> TimeWeatherAgent
    AgentAssignment --> EmailAgent
    AgentAssignment --> TempAgent
    
    %% Result Flow
    TimeWeatherAgent --> Results[Task Results]
    EmailAgent --> Results
    TempAgent --> Results
    Results --> TeamLeader
    TeamLeader --> CompletionCheck[Check Completion]
    CompletionCheck --> MoreTasks{More Tasks Needed?}
    MoreTasks -->|Yes| CreateTask
    MoreTasks -->|No| FinalResponse[Final Response]
    
    %% Tracing and Monitoring
    AgentTeam --> TracingConfig[AgentTraceConfigurator]
    TracingConfig --> AzureMonitor[Azure Monitor]
    TracingConfig --> ConsoleTrace[Console Tracing]
    TracingConfig --> AgentTrace[Agent Instrumentation]
    
    %% Cleanup
    FinalResponse --> Cleanup[Team Dismantlement]
    Cleanup --> DeleteAgents[Delete All Agents]
    
    %% Styling
    classDef teamClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef agentClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef toolClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef flowClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class AgentTeam,TeamLeader,TeamAssembly teamClass
    class TimeWeatherAgent,EmailAgent,TempAgent agentClass
    class TimeTool,WeatherTool,EmailTool,TempTool toolClass
    class TaskAnalysis,CreateTask,ExecuteTask,Results flowClass
```

## Multi-Agent Team Task Delegation Flow

```mermaid
sequenceDiagram
    participant User
    participant TL as Team Leader
    participant TWA as TimeWeatherAgent
    participant EA as EmailAgent
    participant TA as TemperatureAgent
    participant TQ as Task Queue
    participant Trace as OpenTelemetry
    
    User->>TL: Complex Request
    Note over TL: "Get current time and weather for NYC,<br/>convert temperature to Fahrenheit,<br/>email summary to user"
    
    Trace->>Trace: Start Request Span
    TL->>TL: Analyze Request
    TL->>TQ: Create Task 1: Get Time & Weather
    TQ->>TWA: Assign Task 1
    
    Trace->>Trace: Start Task Span
    TWA->>TWA: fetch_current_datetime()
    TWA->>TWA: fetch_weather("New York")
    TWA->>TL: Task 1 Results
    Trace->>Trace: Complete Task Span
    
    TL->>TQ: Create Task 2: Convert Temperature
    TQ->>TA: Assign Task 2
    
    Trace->>Trace: Start Task Span
    TA->>TA: convert_temperature(25.0)
    TA->>TL: Task 2 Results
    Trace->>Trace: Complete Task Span
    
    TL->>TQ: Create Task 3: Send Email Summary
    TQ->>EA: Assign Task 3
    
    Trace->>Trace: Start Task Span
    EA->>EA: send_email_using_recipient_name()
    EA->>TL: Task 3 Results
    Trace->>Trace: Complete Task Span
    
    TL->>TL: Check Task Completeness
    TL->>User: Final Comprehensive Response
    Trace->>Trace: Complete Request Span
    
    Note over TL,TA: All interactions traced with<br/>OpenTelemetry spans and events
```

## Insurance Quote Assistant Multi-Agent Architecture

```mermaid
graph TB
    %% User Interface
    User[User] --> StreamlitUI[Streamlit Interface<br/>stins.py]
    StreamlitUI --> ChatInput[Chat Input Processing]
    
    %% Main Orchestrator
    ChatInput --> MainAgent[Main Orchestrator<br/>InsuranceQuoteAssistant]
    
    %% Connected Agents
    MainAgent --> InsuranceAgent[Insurance Price Agent<br/>insurancepricebot]
    MainAgent --> DocumentAgent[Document Search Agent<br/>insdocagent]  
    MainAgent --> EmailAgent[Email Agent<br/>sendemail]
    
    %% Agent Capabilities
    InsuranceAgent --> InfoValidation[Information Validation<br/>• First Name<br/>• Last Name<br/>• Date of Birth<br/>• Company Name<br/>• Age<br/>• Preexisting Conditions]
    InsuranceAgent --> QuoteCalc[Quote Calculation<br/>• Premium Calculation<br/>• Coverage Analysis<br/>• Risk Assessment]
    
    DocumentAgent --> VectorStore[Vector Store<br/>insurance_vector_store]
    VectorStore --> FileSearch[File Search Tool<br/>insurancetc.pdf]
    DocumentAgent --> TermsExtraction[Terms Extraction<br/>• Policy Terms<br/>• Conditions<br/>• Legal Requirements]
    
    EmailAgent --> EmailFormat[Email Formatting<br/>• Quote Integration<br/>• Terms Attachment<br/>• Professional Layout]
    EmailAgent --> DeliveryService[Email Delivery<br/>• SMTP Integration<br/>• Confirmation<br/>• Error Handling]
    
    %% Response Assembly
    QuoteCalc --> ResponseAssembly[Response Assembly]
    TermsExtraction --> ResponseAssembly
    DeliveryService --> ResponseAssembly
    
    ResponseAssembly --> FinalFormat[Final Response<br/>QUOTE<br/>quote details<br/>[EMAIL OUTPUT]<br/>confirmation]
    FinalFormat --> StreamlitUI
    
    %% Azure AI Foundry Integration
    MainAgent --> AzureFoundry[Azure AI Foundry<br/>AIProjectClient]
    AzureFoundry --> AgentManagement[Agent Management<br/>• Lifecycle<br/>• Threading<br/>• Cleanup]
    AzureFoundry --> ConnectedTools[Connected Agent Tools<br/>• Tool Definitions<br/>• Communication<br/>• Orchestration]
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef agentClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef toolClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef azureClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class User,StreamlitUI,ChatInput userClass
    class MainAgent,InsuranceAgent,DocumentAgent,EmailAgent agentClass
    class InfoValidation,QuoteCalc,TermsExtraction,EmailFormat toolClass
    class AzureFoundry,AgentManagement,ConnectedTools azureClass
```

## Insurance Assistant Sequential Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant MA as Main Agent
    participant IA as Insurance Agent
    participant DA as Document Agent
    participant EA as Email Agent
    participant VS as Vector Store
    participant AF as Azure Foundry
    
    %% Initial Request
    U->>UI: "I need an insurance quote"
    UI->>MA: Process request through connected_agent()
    MA->>AF: Create conversation thread
    
    %% Information Collection Phase
    MA->>IA: Invoke insurance pricing tool
    IA->>IA: Validate required information
    IA->>MA: Request missing user details
    MA->>UI: "Please provide: Name, DOB, Company, Age, Conditions"
    UI->>U: Display information request
    
    U->>UI: Provide complete information
    UI->>MA: Forward user data
    MA->>IA: Generate insurance quote with user data
    IA->>IA: Calculate premium & coverage
    IA->>MA: Return formatted insurance quote
    
    %% Document Search Phase
    MA->>DA: Invoke document search tool
    DA->>VS: Semantic search for terms & conditions
    VS->>DA: Return relevant policy documents
    DA->>DA: Extract and format terms
    DA->>MA: Return terms & conditions summary
    
    %% Email Delivery Phase
    MA->>EA: Invoke email delivery tool
    EA->>EA: Format complete quote package
    EA->>EA: Send email to user
    EA->>MA: Return delivery confirmation
    
    %% Response Assembly
    MA->>MA: Assemble final response
    Note over MA: Format: [QUOTE]\nquote details\n[EMAIL OUTPUT]\nconfirmation
    MA->>UI: Return structured response
    UI->>U: Display complete insurance quote & confirmation
    
    %% Cleanup
    MA->>AF: Delete agents and resources
    AF->>AF: Clean up threads, vector store, agents
```

## Insurance Assistant Resource Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initialize: User starts session
    Initialize --> CreateProject: Setup AIProjectClient
    CreateProject --> CreateAgents: Create specialized agents
    
    CreateAgents --> SetupInsuranceAgent: Create Insurance Price Agent
    SetupInsuranceAgent --> SetupDocumentAgent: Create Document Agent
    SetupDocumentAgent --> SetupEmailAgent: Get Email Agent Reference
    SetupEmailAgent --> CreateVectorStore: Upload & process documents
    
    CreateVectorStore --> CreateMainAgent: Setup orchestrator with tools
    CreateMainAgent --> ProcessRequest: Ready to handle requests
    
    ProcessRequest --> ValidateInfo: Check user information
    ValidateInfo --> IncompleteInfo: Missing required fields
    ValidateInfo --> CompleteInfo: All fields provided
    
    IncompleteInfo --> ProcessRequest: Request missing information
    
    CompleteInfo --> GenerateQuote: Create insurance quote
    GenerateQuote --> SearchDocuments: Find terms & conditions
    SearchDocuments --> SendEmail: Deliver quote package
    SendEmail --> AssembleResponse: Format final response
    AssembleResponse --> Cleanup: Clean up resources
    
    Cleanup --> DeleteAgents: Remove created agents
    DeleteAgents --> DeleteVectorStore: Remove document storage
    DeleteVectorStore --> DeleteThreads: Clean up conversations
    DeleteThreads --> [*]: Session complete
    
    %% Error Handling
    CreateProject --> ErrorState: Azure connection failed
    CreateAgents --> ErrorState: Agent creation failed
    GenerateQuote --> ErrorState: Quote generation failed
    SearchDocuments --> ErrorState: Document search failed
    SendEmail --> ErrorState: Email delivery failed
    
    ErrorState --> Cleanup: Clean up partial resources
```
```

## Agent Interaction Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main as Main Controller
    participant AM as Agent Manager
    participant CA as Connected Agent
    participant SA as Stock Agent
    participant EA as Email Agent
    participant RA as RFP Agent
    participant Azure as Azure AI Foundry
    participant Ext as External Services
    
    User->>Main: User Request
    Main->>AM: Route to Agent Manager
    AM->>CA: Create Connected Agent
    
    CA->>SA: Create Stock Price Agent
    SA->>Azure: Register with Azure AI Foundry
    Azure-->>SA: Agent ID
    
    CA->>RA: Create RFP Search Agent
    RA->>Azure: Register with Search Tools
    Azure-->>RA: Agent ID with Search Resources
    
    CA->>EA: Create Email Agent
    EA->>Azure: Register with Function Tools
    Azure-->>EA: Agent ID
    
    CA->>Azure: Create Main Orchestrator
    Azure-->>CA: Orchestrator Agent ID
    
    User->>CA: Query (e.g., "Get Microsoft stock price and email results")
    CA->>Azure: Process Request
    Azure->>SA: Get Stock Price
    SA->>Ext: External Stock API Call
    Ext-->>SA: Stock Data
    SA-->>Azure: Stock Results
    
    Azure->>EA: Send Email
    EA->>Ext: Gmail SMTP
    Ext-->>EA: Email Sent Confirmation
    EA-->>Azure: Email Status
    
    Azure-->>CA: Combined Results
    CA-->>User: Final Response
    
    Note over Azure: All interactions are traced<br/>with OpenTelemetry
```

## Evaluation Pipeline Flow

```mermaid
flowchart TD
    Start[Start Evaluation] --> LoadData[Load JSONL Data]
    LoadData --> InitEval[Initialize Evaluators]
    
    InitEval --> QualityPath[Quality Metrics Path]
    InitEval --> SafetyPath[Safety Metrics Path]
    InitEval --> AgenticPath[Agentic Metrics Path]
    InitEval --> AdvancedPath[Advanced Metrics Path]
    
    %% Quality Metrics Flow
    QualityPath --> QualityEvals{Quality Evaluators}
    QualityEvals --> Relevance[Relevance Score]
    QualityEvals --> Coherence[Coherence Score]
    QualityEvals --> Groundedness[Groundedness Score]
    QualityEvals --> Fluency[Fluency Score]
    
    %% Safety Metrics Flow
    SafetyPath --> SafetyEvals{Safety Evaluators}
    SafetyEvals --> ContentSafety[Content Safety Score]
    SafetyEvals --> Violence[Violence Detection]
    SafetyEvals --> HateUnfairness[Hate/Unfairness Score]
    SafetyEvals --> IndirectAttack[Indirect Attack Score]
    
    %% Agentic Metrics Flow
    AgenticPath --> AgenticEvals{Agentic Evaluators}
    AgenticEvals --> IntentResolution[Intent Resolution Score]
    AgenticEvals --> TaskAdherence[Task Adherence Score]
    AgenticEvals --> ToolCallAccuracy[Tool Call Accuracy]
    
    %% Advanced Metrics Flow
    AdvancedPath --> AdvancedEvals{Advanced Evaluators}
    AdvancedEvals --> BLEU[BLEU Score]
    AdvancedEvals --> F1Score[F1 Score]
    AdvancedEvals --> ROUGE[ROUGE Score]
    
    %% Convergence
    Relevance --> Aggregate[Aggregate Results]
    Coherence --> Aggregate
    Groundedness --> Aggregate
    Fluency --> Aggregate
    ContentSafety --> Aggregate
    Violence --> Aggregate
    HateUnfairness --> Aggregate
    IndirectAttack --> Aggregate
    IntentResolution --> Aggregate
    TaskAdherence --> Aggregate
    ToolCallAccuracy --> Aggregate
    BLEU --> Aggregate
    F1Score --> Aggregate
    ROUGE --> Aggregate
    
    Aggregate --> GenerateReport[Generate Report]
    GenerateReport --> SaveResults[Save JSON Results]
    SaveResults --> StudioURL[Generate Studio URL]
    StudioURL --> End[End Evaluation]
    
    %% Styling
    classDef qualityClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef safetyClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef agenticClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef advancedClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class QualityPath,QualityEvals,Relevance,Coherence,Groundedness,Fluency qualityClass
    class SafetyPath,SafetyEvals,ContentSafety,Violence,HateUnfairness,IndirectAttack safetyClass
    class AgenticPath,AgenticEvals,IntentResolution,TaskAdherence,ToolCallAccuracy agenticClass
    class AdvancedPath,AdvancedEvals,BLEU,F1Score,ROUGE advancedClass
```

## Red Team Security Testing Flow

```mermaid
flowchart TB
    StartScan[Start Red Team Scan] --> InitRedTeam[Initialize Red Team Agent]
    InitRedTeam --> ConfigRisk[Configure Risk Categories]
    
    ConfigRisk --> ViolenceRisk[Violence Risk]
    ConfigRisk --> HateRisk[Hate/Unfairness Risk]
    ConfigRisk --> SexualRisk[Sexual Content Risk]
    ConfigRisk --> SelfHarmRisk[Self-Harm Risk]
    
    ViolenceRisk --> SelectStrategies[Select Attack Strategies]
    HateRisk --> SelectStrategies
    SexualRisk --> SelectStrategies
    SelfHarmRisk --> SelectStrategies
    
    SelectStrategies --> EasyAttacks[Easy Complexity Attacks]
    SelectStrategies --> ModerateAttacks[Moderate Complexity Attacks]
    SelectStrategies --> CharacterAttacks[Character Manipulation]
    SelectStrategies --> EncodingAttacks[Encoding Attacks]
    SelectStrategies --> FlipAttacks[Flip Strategy Attacks]
    
    %% Attack Execution Paths
    EasyAttacks --> ExecuteAttack1[Execute Attack Set 1]
    ModerateAttacks --> ExecuteAttack2[Execute Attack Set 2]
    CharacterAttacks --> ExecuteAttack3[Execute Attack Set 3]
    EncodingAttacks --> ExecuteAttack4[Execute Attack Set 4]
    FlipAttacks --> ExecuteAttack5[Execute Attack Set 5]
    
    %% Target Types
    ExecuteAttack1 --> SimpleTarget[Simple Callback Target]
    ExecuteAttack2 --> AdvancedTarget[Advanced Callback Target]
    ExecuteAttack3 --> ModelTarget[Azure OpenAI Model Target]
    ExecuteAttack4 --> SimpleTarget
    ExecuteAttack5 --> ModelTarget
    
    %% Results Processing
    SimpleTarget --> CollectResults[Collect Scan Results]
    AdvancedTarget --> CollectResults
    ModelTarget --> CollectResults
    
    CollectResults --> AnalyzeVuln[Analyze Vulnerabilities]
    AnalyzeVuln --> RiskScoring[Calculate Risk Scores]
    RiskScoring --> GenerateReport[Generate Security Report]
    
    GenerateReport --> SaveScanResults[Save Scan Results JSON]
    SaveScanResults --> ComplianceCheck[Compliance Assessment]
    ComplianceCheck --> Recommendations[Generate Recommendations]
    Recommendations --> EndScan[End Red Team Scan]
    
    %% Styling
    classDef riskClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef attackClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef targetClass fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef resultClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class ViolenceRisk,HateRisk,SexualRisk,SelfHarmRisk riskClass
    class EasyAttacks,ModerateAttacks,CharacterAttacks,EncodingAttacks,FlipAttacks attackClass
    class SimpleTarget,AdvancedTarget,ModelTarget targetClass
    class CollectResults,AnalyzeVuln,RiskScoring,GenerateReport resultClass
```

## MCP Voice Interface Flow

```mermaid
flowchart TD
    %% User Interaction
    UserVoice[User Voice Input] --> AudioCapture[Audio Capture<br/>st.audio_input]
    AudioCapture --> SaveAudio[Save Audio File<br/>save_audio_file]
    
    %% Transcription Process
    SaveAudio --> Transcription[Speech-to-Text<br/>transcribe_audio]
    Transcription --> WhisperAPI[Azure OpenAI Whisper]
    WhisperAPI --> TextOutput[Transcribed Text]
    
    %% MCP Server Selection
    TextOutput --> ServerSelection[MCP Server Selection]
    ServerSelection --> MSFTOption[Microsoft Learn]
    ServerSelection --> GitHubOption[GitHub Copilot]
    ServerSelection --> HFOption[HuggingFace]
    
    %% MCP Processing
    MSFTOption --> MSFTResponse[msft_generate_chat_response]
    GitHubOption --> GitHubResponse[bbgithub_generate_chat_response]
    HFOption --> HFResponse[hf_generate_chat_response]
    
    %% MCP Server Communication
    MSFTResponse --> MSFTServer[Microsoft Learn MCP<br/>learn.microsoft.com/api/mcp]
    GitHubResponse --> GitHubServer[GitHub Copilot MCP<br/>api.githubcopilot.com/mcp/]
    HFResponse --> HFServer[HuggingFace MCP<br/>hf.co/mcp]
    
    %% Response Processing
    MSFTServer --> ResponseText[Generated Response Text]
    GitHubServer --> ResponseText
    HFServer --> ResponseText
    
    %% Text-to-Speech
    ResponseText --> TTS[Text-to-Speech<br/>generate_audio_response_gpt]
    TTS --> TTSService[Azure OpenAI TTS<br/>gpt-4o-mini-tts]
    TTSService --> AudioResponse[Audio Response]
    
    %% User Output
    AudioResponse --> AudioPlayback[Audio Playback<br/>Streamlit Audio Player]
    ResponseText --> TextDisplay[Text Display<br/>Streamlit Markdown]
    
    %% Session Management
    TextOutput --> SessionHistory[Chat History<br/>st.session_state.messages]
    ResponseText --> SessionHistory
    AudioResponse --> SessionHistory
    
    %% Cleanup
    AudioPlayback --> Cleanup[Cleanup Temp Files<br/>os.remove]
    
    %% Styling
    classDef userClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef voiceClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef mcpClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef azureClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef processClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class UserVoice,AudioCapture,SaveAudio userClass
    class Transcription,WhisperAPI,TTS,TTSService,AudioResponse,AudioPlayback voiceClass
    class ServerSelection,MSFTResponse,GitHubResponse,HFResponse,MSFTServer,GitHubServer,HFServer mcpClass
    class MSFTOption,GitHubOption,HFOption,ResponseText,TextDisplay azureClass
    class SessionHistory,Cleanup,TextOutput processClass
```

## Component Dependencies

```mermaid
graph LR
    %% Core Dependencies
    Python[Python 3.12+] --> AgenticAI[agenticai.py]
    Python --> BBMCP[bbmcp.py]
    DotEnv[python-dotenv] --> AgenticAI
    DotEnv --> BBMCP
    
    %% MCP Application Dependencies
    Streamlit[streamlit] --> BBMCP
    OpenAIClient --> BBMCP
    Requests[requests] --> BBMCP
    GTTS[gtts] --> BBMCP
    TempFile[tempfile] --> BBMCP
    Base64[base64] --> BBMCP
    
    %% Azure Dependencies
    AzureIdentity[azure-identity] --> AgenticAI
    AzureAIProjects[azure-ai-projects] --> AgenticAI
    AzureAIEvaluation[azure-ai-evaluation] --> AgenticAI
    AzureAIAgents[azure-ai-agents] --> AgenticAI
    AzureMonitorOTel[azure-monitor-opentelemetry] --> AgenticAI
    
    %% OpenAI Dependencies
    OpenAIClient[openai] --> AgenticAI
    
    %% Data Processing
    Pandas[pandas] --> AgenticAI
    JSON[json] --> AgenticAI
    
    %% Monitoring
    OpenTelemetry[opentelemetry] --> AgenticAI
    
    %% Utilities
    Utils[utils.py] --> AgenticAI
    Utils --> EmailSMTP[Email SMTP Integration]
    
    %% Configuration
    Environment[.env Configuration] --> AgenticAI
    Requirements[requirements.txt] --> Python
    
    %% Azure Services (External)
    AgenticAI --> AzureOpenAIService[Azure OpenAI Service]
    AgenticAI --> AzureAISearchService[Azure AI Search Service]
    AgenticAI --> AzureFoundryService[Azure AI Foundry Service]
    AgenticAI --> AzureIdentityService[Azure Identity Service]
    
    %% External Services
    AgenticAI --> GmailSMTP[Gmail SMTP]
    AgenticAI --> StockAPIs[Stock Price APIs]
    
    %% MCP External Services
    BBMCP --> MCPServices[MCP Protocol Services]
    MCPServices --> MSFTLearnMCP[Microsoft Learn MCP]
    MCPServices --> GitHubCopilotMCP[GitHub Copilot MCP]
    MCPServices --> HuggingFaceMCP[HuggingFace MCP]
    
    %% Voice Processing Services
    BBMCP --> VoiceServices[Voice Processing]
    VoiceServices --> AzureWhisper[Azure OpenAI Whisper]
    VoiceServices --> AzureTTS[Azure OpenAI TTS]
    
    %% Data Files
    AgenticAI --> JSONLData[JSONL Data Files]
    AgenticAI --> JSONResults[JSON Result Files]
    AgenticAI --> LogFiles[Log Files]
    
    %% Styling
    classDef coreClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef azureClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef dataClass fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    classDef mcpClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class Python,DotEnv,OpenAIClient,Pandas,JSON,OpenTelemetry,Streamlit,Requests,GTTS,TempFile,Base64 coreClass
    class AzureIdentity,AzureAIProjects,AzureAIEvaluation,AzureAIAgents,AzureMonitorOTel azureClass
    class GmailSMTP,StockAPIs,EmailSMTP externalClass
    class JSONLData,JSONResults,LogFiles,Environment dataClass
    class BBMCP,MCPServices,MSFTLearnMCP,GitHubCopilotMCP,HuggingFaceMCP,VoiceServices,AzureWhisper,AzureTTS mcpClass
```

---

*This mermaid diagram provides a comprehensive visual representation of the AgenticAIFoundry architecture, showing all connected agents, evaluation frameworks, security testing components, MCP protocol integration, voice interface capabilities, and their relationships. The diagram is designed to complement the Architecture Blueprint document and provide an interactive visual guide to the system.*
