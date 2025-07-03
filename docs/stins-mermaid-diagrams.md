# Insurance Quote Assistant - Mermaid Architecture Diagrams

This document contains comprehensive Mermaid diagrams specifically for the Insurance Quote Assistant (`stins.py`) multi-agent orchestration system.

## Viewing the Diagrams

These mermaid diagrams can be viewed in several ways:

1. **GitHub**: The diagrams should render automatically when viewing this file on GitHub
2. **VS Code**: Install the "Mermaid Markdown Syntax Highlighting" extension
3. **Online Viewers**: Copy the mermaid code to [mermaid.live](https://mermaid.live) or [mermaid-js.github.io](https://mermaid-js.github.io/mermaid-live-editor)
4. **Local Tools**: Use mermaid CLI tools or browser extensions that support mermaid rendering

> **Note**: If the diagrams don't render properly in your environment, you can copy the mermaid code blocks to any online mermaid viewer for proper visualization.

## 1. Insurance Assistant Multi-Agent Architecture

```mermaid
graph TB
    %% User Interface Layer
    User[User Request] --> StreamlitUI[Streamlit Chat Interface<br/>insurance_chat_ui]
    StreamlitUI --> UserInput[User Input Processing]
    
    %% Main Orchestrator
    UserInput --> MainAgent[Main Orchestrator Agent<br/>InsuranceQuoteAssistant]
    
    %% Connected Agents
    MainAgent --> InsuranceAgent[Insurance Price Agent<br/>insurancepricebot]
    MainAgent --> DocumentAgent[Document Search Agent<br/>insdocagent]
    MainAgent --> EmailAgent[Email Agent<br/>sendemail]
    
    %% Agent Capabilities
    InsuranceAgent --> InfoCollection[Information Collection<br/>• First Name<br/>• Last Name<br/>• Date of Birth<br/>• Company Name<br/>• Age<br/>• Preexisting Conditions]
    InsuranceAgent --> QuoteGeneration[Quote Generation<br/>• Premium Calculation<br/>• Coverage Details<br/>• Risk Assessment]
    
    DocumentAgent --> VectorStore[Vector Store<br/>insurance_vector_store]
    VectorStore --> FileSearch[File Search Tool<br/>insurancetc.pdf]
    DocumentAgent --> TermsRetrieval[Terms & Conditions<br/>• Policy Details<br/>• Coverage Terms<br/>• Legal Requirements]
    
    EmailAgent --> EmailFormatting[Email Formatting<br/>• Quote Compilation<br/>• Terms Integration<br/>• Professional Layout]
    EmailAgent --> EmailDelivery[Email Delivery<br/>• SMTP Integration<br/>• Delivery Confirmation<br/>• Error Handling]
    
    %% Response Processing
    QuoteGeneration --> ResultAggregation[Result Aggregation]
    TermsRetrieval --> ResultAggregation
    EmailDelivery --> ResultAggregation
    
    ResultAggregation --> ResponseFormatting[Response Formatting<br/>QUOTE:<br/>quote details<br/>EMAIL OUTPUT:<br/>email confirmation]
    
    ResponseFormatting --> StreamlitUI
    StreamlitUI --> User
    
    %% Azure Services
    MainAgent --> AzureAI[Azure AI Foundry<br/>AIProjectClient]
    AzureAI --> AgentManagement[Agent Management<br/>• Creation<br/>• Lifecycle<br/>• Cleanup]
    AzureAI --> ThreadManagement[Thread Management<br/>• Conversation State<br/>• Message Processing]
    
    %% Styling
    classDef userClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef agentClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef dataClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class User,StreamlitUI userClass
    class MainAgent,InsuranceAgent,DocumentAgent,EmailAgent agentClass
    class AzureAI,AgentManagement,ThreadManagement serviceClass
    class VectorStore,FileSearch,InfoCollection dataClass
```

## 2. Agent Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant MA as Main Agent
    participant IA as Insurance Agent
    participant DA as Document Agent  
    participant EA as Email Agent
    participant VS as Vector Store
    participant ES as Email Service
    
    %% Initial Request
    U->>UI: "I need an insurance quote"
    UI->>MA: Process user request
    
    %% Information Collection Phase
    MA->>IA: Collect user information
    IA->>MA: Request: Name, DOB, Company, Age, Conditions
    MA->>UI: "Please provide required information"
    UI->>U: Display information request
    
    U->>UI: Provide personal details
    UI->>MA: Forward user information
    MA->>IA: Generate insurance quote
    
    %% Quote Generation
    IA->>IA: Process user data
    IA->>IA: Calculate premium & coverage
    IA->>MA: Return insurance quote
    
    %% Document Search Phase
    MA->>DA: Retrieve terms & conditions
    DA->>VS: Search insurance documents
    VS->>DA: Return relevant terms
    DA->>MA: Formatted terms & conditions
    
    %% Email Delivery Phase
    MA->>EA: Send complete quote package
    EA->>EA: Format email with quote + terms
    EA->>ES: Send email to user
    ES->>EA: Delivery confirmation
    EA->>MA: Email sent confirmation
    
    %% Response Assembly
    MA->>MA: Aggregate all results
    MA->>UI: Formatted response with quote & email confirmation
    UI->>U: Display complete response
    
    %% Cleanup
    Note over MA: Cleanup agents, threads, vector store
```

## 3. Connected Agent Tool Architecture

```mermaid
graph LR
    %% Main Agent
    MainAgent[Main Orchestrator<br/>InsuranceQuoteAssistant]
    
    %% Connected Agent Tools
    MainAgent --> InsuranceTool[ConnectedAgentTool<br/>Insurance Price Agent]
    MainAgent --> DocumentTool[ConnectedAgentTool<br/>Document Search Agent]
    MainAgent --> EmailTool[ConnectedAgentTool<br/>Email Agent]
    
    %% Tool Definitions
    InsuranceTool --> InsuranceImpl[Agent Implementation<br/>• ID: insurance_price_agent.id<br/>• Name: insurancepricebot<br/>• Description: Create insurance quote]
    
    DocumentTool --> DocumentImpl[Agent Implementation<br/>• ID: insdocagent.id<br/>• Name: insdocagent<br/>• Description: Summarize uploaded files]
    
    EmailTool --> EmailImpl[Agent Implementation<br/>• ID: asst_g3hRNabXnYHg3mzqBxvgDRG6<br/>• Name: sendemail<br/>• Description: Send quote via email]
    
    %% Tool Resources
    DocumentImpl --> FileSearchTool[FileSearchTool<br/>• Vector Store IDs<br/>• Document Processing<br/>• Semantic Search]
    
    FileSearchTool --> VectorResources[Vector Store Resources<br/>• File Upload: insurancetc.pdf<br/>• Vector Embeddings<br/>• Search Capabilities]
    
    %% Azure AI Foundry Integration
    InsuranceImpl --> AzureAgents[Azure AI Agents API]
    DocumentImpl --> AzureAgents
    EmailImpl --> AzureAgents
    
    AzureAgents --> ModelDeployment[Model Deployment<br/>MODEL_DEPLOYMENT_NAME]
    
    %% Styling
    classDef mainClass fill:#ff9999,stroke:#cc0000,stroke-width:3px
    classDef toolClass fill:#99ccff,stroke:#0066cc,stroke-width:2px
    classDef implClass fill:#99ff99,stroke:#009900,stroke-width:2px
    classDef azureClass fill:#ffcc99,stroke:#ff6600,stroke-width:2px
    
    class MainAgent mainClass
    class InsuranceTool,DocumentTool,EmailTool toolClass
    class InsuranceImpl,DocumentImpl,EmailImpl,FileSearchTool implClass
    class AzureAgents,ModelDeployment,VectorResources azureClass
```

## 4. Data Flow and State Management

```mermaid
stateDiagram-v2
    [*] --> UserInput: User starts conversation
    
    UserInput --> InfoValidation: Validate required fields
    InfoValidation --> InfoComplete: All fields provided
    InfoValidation --> InfoIncomplete: Missing fields
    
    InfoIncomplete --> UserInput: Request missing information
    
    InfoComplete --> QuoteGeneration: Generate insurance quote
    QuoteGeneration --> DocumentSearch: Search terms & conditions
    DocumentSearch --> EmailPrep: Prepare email content
    EmailPrep --> EmailSend: Send quote via email
    EmailSend --> ResponseFormat: Format final response
    ResponseFormat --> Cleanup: Clean up resources
    
    Cleanup --> [*]: Session complete
    
    %% Error States
    QuoteGeneration --> ErrorHandle: Quote generation failed
    DocumentSearch --> ErrorHandle: Document search failed
    EmailSend --> ErrorHandle: Email delivery failed
    
    ErrorHandle --> UserInput: Retry with error message
    
    %% Parallel Processing States
    state DocumentSearch {
        [*] --> FileUpload
        FileUpload --> VectorStore
        VectorStore --> SemanticSearch
        SemanticSearch --> ResultExtraction
        ResultExtraction --> [*]
    }
    
    state EmailPrep {
        [*] --> QuoteFormatting
        QuoteFormatting --> TermsIntegration
        TermsIntegration --> EmailTemplate
        EmailTemplate --> [*]
    }
```

## 5. Resource Lifecycle Management

```mermaid
graph TD
    %% Resource Creation
    RequestStart[Request Start] --> CreateProject[Create AI Project Client]
    CreateProject --> CreateInsuranceAgent[Create Insurance Price Agent]
    CreateInsuranceAgent --> CreateDocumentAgent[Create Document Search Agent]
    CreateDocumentAgent --> GetEmailAgent[Get Email Agent Reference]
    
    %% File and Vector Store Setup
    GetEmailAgent --> UploadFile[Upload Insurance Document<br/>./data/insurancetc.pdf]
    UploadFile --> CreateVectorStore[Create Vector Store<br/>insurance_vector_store]
    CreateVectorStore --> ConfigureFileSearch[Configure File Search Tool]
    
    %% Main Orchestrator Setup
    ConfigureFileSearch --> CreateMainAgent[Create Main Orchestrator<br/>InsuranceQuoteAssistant]
    CreateMainAgent --> CreateThread[Create Conversation Thread]
    CreateThread --> ProcessRequest[Process User Request]
    
    %% Processing
    ProcessRequest --> AgentExecution[Agent Execution Loop]
    AgentExecution --> StatusPolling{Check Run Status}
    StatusPolling -->|In Progress| StatusPolling
    StatusPolling -->|Complete| ExtractResults[Extract Results]
    StatusPolling -->|Failed| HandleError[Handle Error]
    
    %% Cleanup Phase
    ExtractResults --> CleanupStart[Start Cleanup]
    HandleError --> CleanupStart
    
    CleanupStart --> DeleteMainAgent[Delete Main Agent]
    DeleteMainAgent --> DeleteThread[Delete Thread]
    DeleteThread --> DeleteInsuranceAgent[Delete Insurance Agent]
    DeleteInsuranceAgent --> DeleteDocumentAgent[Delete Document Agent]
    DeleteDocumentAgent --> DeleteVectorStore[Delete Vector Store]
    DeleteVectorStore --> CleanupComplete[Cleanup Complete]
    
    %% Error Handling
    CreateProject -->|Failure| ErrorReturn[Return Error]
    CreateInsuranceAgent -->|Failure| ErrorReturn
    UploadFile -->|Failure| ErrorReturn
    CreateVectorStore -->|Failure| ErrorReturn
    
    %% Styling
    classDef createClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef processClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef cleanupClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef errorClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class CreateProject,CreateInsuranceAgent,CreateDocumentAgent,GetEmailAgent,CreateMainAgent createClass
    class ProcessRequest,AgentExecution,StatusPolling,ExtractResults processClass
    class CleanupStart,DeleteMainAgent,DeleteThread,DeleteInsuranceAgent,DeleteDocumentAgent,DeleteVectorStore cleanupClass
    class HandleError,ErrorReturn errorClass
```

## 6. Integration Architecture

```mermaid
graph TB
    %% External Integrations
    subgraph "External Services"
        EmailService[Email Service<br/>SMTP Integration]
        AzureOpenAI[Azure OpenAI<br/>Model Endpoints]
        AzureIdentity[Azure Identity<br/>DefaultAzureCredential]
    end
    
    %% Core Application
    subgraph "Insurance Assistant Application"
        StreamlitApp[Streamlit Application<br/>stins.py]
        ConnectedAgentFunc[connected_agent Function]
        UIFunction[insurance_chat_ui Function]
    end
    
    %% Azure AI Foundry Layer
    subgraph "Azure AI Foundry"
        ProjectClient[AI Project Client]
        AgentService[Agents Service]
        ThreadService[Threads Service]
        VectorService[Vector Stores Service]
        FileService[Files Service]
    end
    
    %% Agent Ecosystem
    subgraph "Connected Agents"
        MainOrchestrator[Main Orchestrator]
        InsuranceBot[Insurance Price Bot]
        DocumentBot[Document Search Bot]
        EmailBot[Email Bot]
    end
    
    %% Data Layer
    subgraph "Data Storage"
        VectorDB[Vector Database<br/>insurance_vector_store]
        FileStorage[File Storage<br/>insurancetc.pdf]
        ThreadState[Thread State]
        SessionState[Streamlit Session State]
    end
    
    %% Connections
    StreamlitApp --> UIFunction
    UIFunction --> ConnectedAgentFunc
    ConnectedAgentFunc --> ProjectClient
    
    ProjectClient --> AgentService
    ProjectClient --> ThreadService
    ProjectClient --> VectorService
    ProjectClient --> FileService
    
    AgentService --> MainOrchestrator
    AgentService --> InsuranceBot
    AgentService --> DocumentBot
    AgentService --> EmailBot
    
    FileService --> FileStorage
    VectorService --> VectorDB
    ThreadService --> ThreadState
    UIFunction --> SessionState
    
    %% External Service Connections
    ProjectClient --> AzureIdentity
    AgentService --> AzureOpenAI
    EmailBot --> EmailService
    
    %% Configuration
    ConnectedAgentFunc -.-> EnvConfig[Environment Configuration<br/>• PROJECT_ENDPOINT<br/>• MODEL_DEPLOYMENT_NAME<br/>• AZURE_OPENAI_ENDPOINT<br/>• AZURE_OPENAI_KEY]
    
    %% Styling
    classDef externalClass fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    classDef appClass fill:#4caf50,stroke:#2e7d32,stroke-width:2px
    classDef azureClass fill:#2196f3,stroke:#1565c0,stroke-width:2px
    classDef agentClass fill:#9c27b0,stroke:#6a1b9a,stroke-width:2px
    classDef dataClass fill:#ff9800,stroke:#e65100,stroke-width:2px
    
    class EmailService,AzureOpenAI,AzureIdentity externalClass
    class StreamlitApp,ConnectedAgentFunc,UIFunction appClass
    class ProjectClient,AgentService,ThreadService,VectorService,FileService azureClass
    class MainOrchestrator,InsuranceBot,DocumentBot,EmailBot agentClass
    class VectorDB,FileStorage,ThreadState,SessionState dataClass
```

## 7. Security and Authentication Flow

```mermaid
graph LR
    %% User Authentication
    User[User] --> StreamlitApp[Streamlit Application]
    
    %% Application Authentication
    StreamlitApp --> EnvValidation[Environment Variable Validation]
    EnvValidation --> AzureAuth[Azure Authentication]
    
    %% Azure Authentication Chain
    AzureAuth --> DefaultCredential[DefaultAzureCredential]
    DefaultCredential --> ServicePrincipal[Service Principal Authentication]
    DefaultCredential --> ManagedIdentity[Managed Identity Authentication]
    DefaultCredential --> AzureCLI[Azure CLI Authentication]
    
    %% Service Access
    ServicePrincipal --> ProjectAccess[AI Project Access]
    ManagedIdentity --> ProjectAccess
    AzureCLI --> ProjectAccess
    
    ProjectAccess --> AgentPermissions[Agent Management Permissions]
    ProjectAccess --> VectorPermissions[Vector Store Permissions]
    ProjectAccess --> FilePermissions[File Management Permissions]
    
    %% Data Security
    AgentPermissions --> SecureComm[Secure Agent Communication<br/>HTTPS/TLS]
    VectorPermissions --> EncryptedStorage[Encrypted Vector Storage]
    FilePermissions --> SecureFileUpload[Secure File Upload]
    
    %% External Service Security
    SecureComm --> EmailSecurity[Email Service Security<br/>• Authentication<br/>• Encryption<br/>• Audit Logging]
    
    %% Privacy Protection
    EncryptedStorage --> DataPrivacy[Data Privacy<br/>• PII Protection<br/>• Data Retention<br/>• GDPR Compliance]
    
    %% Audit and Monitoring
    DataPrivacy --> AuditLogging[Audit Logging<br/>• Access Logs<br/>• Operation Logs<br/>• Error Logs]
    EmailSecurity --> AuditLogging
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef authClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef securityClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef privacyClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class User,StreamlitApp userClass
    class EnvValidation,AzureAuth,DefaultCredential,ServicePrincipal,ManagedIdentity,AzureCLI authClass
    class ProjectAccess,AgentPermissions,VectorPermissions,FilePermissions,SecureComm,EmailSecurity securityClass
    class EncryptedStorage,SecureFileUpload,DataPrivacy,AuditLogging privacyClass
```

## Conclusion

These Mermaid diagrams provide comprehensive visual documentation of the Insurance Quote Assistant's multi-agent architecture. The diagrams illustrate:

1. **Multi-Agent Orchestration**: How connected agents work together
2. **Communication Patterns**: Message flow between components
3. **Tool Architecture**: Connected Agent Tool implementation
4. **State Management**: Application state transitions
5. **Resource Lifecycle**: Creation and cleanup processes
6. **Integration Architecture**: External service connections
7. **Security Flow**: Authentication and data protection

The visual representations help understand the complex interactions within the Azure AI Foundry Connected Agent ecosystem and provide a reference for system architecture, troubleshooting, and future enhancements.