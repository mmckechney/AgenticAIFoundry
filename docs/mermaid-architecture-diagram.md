# AgenticAIFoundry - Mermaid Architecture Diagram

This document contains a comprehensive mermaid diagram showing the complete architecture of the AgenticAIFoundry platform, including all connected agents, evaluation frameworks, red team testing, and external integrations.

## Complete System Architecture

```mermaid
graph TB
    %% Main Controller
    User[User Request] --> Main[Main Controller<br/>agenticai.py]
    
    %% Core Agent Ecosystem
    Main --> AgentManager[Agent Manager]
    AgentManager --> CodeAgent[Code Interpreter Agent<br/>code_interpreter()]
    AgentManager --> SearchAgent[AI Search Agent<br/>ai_search_agent()]
    AgentManager --> ConnectedAgent[Connected Agent<br/>connected_agent()]
    AgentManager --> ReasoningAgent[Reasoning Agent<br/>process_message_reasoning()]
    AgentManager --> WeatherAgent[Weather Agent<br/>fetch_weather()]
    
    %% Evaluation Framework
    Main --> EvalFramework[Evaluation Framework<br/>eval()]
    EvalFramework --> QualityEval[Quality Evaluators]
    EvalFramework --> SafetyEval[Safety Evaluators]
    EvalFramework --> AgenticEval[Agentic Evaluators<br/>agent_eval()]
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
    Main --> RedTeam[Red Team Framework<br/>redteam()]
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
    ConnectedAgent --> EmailAgent[Email Agent<br/>send_email()]
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

## Component Dependencies

```mermaid
graph LR
    %% Core Dependencies
    Python[Python 3.12+] --> AgenticAI[agenticai.py]
    DotEnv[python-dotenv] --> AgenticAI
    
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
    
    %% Data Files
    AgenticAI --> JSONLData[JSONL Data Files]
    AgenticAI --> JSONResults[JSON Result Files]
    AgenticAI --> LogFiles[Log Files]
    
    %% Styling
    classDef coreClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef azureClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef dataClass fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    
    class Python,DotEnv,OpenAIClient,Pandas,JSON,OpenTelemetry coreClass
    class AzureIdentity,AzureAIProjects,AzureAIEvaluation,AzureAIAgents,AzureMonitorOTel azureClass
    class GmailSMTP,StockAPIs,EmailSMTP externalClass
    class JSONLData,JSONResults,LogFiles,Environment dataClass
```

---

*This mermaid diagram provides a comprehensive visual representation of the AgenticAIFoundry architecture, showing all connected agents, evaluation frameworks, security testing components, and their relationships. The diagram is designed to complement the Architecture Blueprint document and provide an interactive visual guide to the system.*