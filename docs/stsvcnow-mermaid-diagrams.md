# ServiceNow AI Assistant - Mermaid Architecture Diagrams

This document contains comprehensive Mermaid diagrams illustrating the multi-agent orchestration architecture and technical components of the ServiceNow AI Assistant (stsvcnow.py).

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Multi-Agent Orchestration](#multi-agent-orchestration)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Integration Architecture](#integration-architecture)
5. [Component Interactions](#component-interactions)
6. [Process Workflows](#process-workflows)

## System Architecture

### High-Level System Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit Web Interface]
        VI[Voice Input Interface]
        CI[Chat Interface]
        AI[Audio Interface]
    end
    
    subgraph "Application Core"
        SIM[ServiceNowIncidentManager]
        AP[Audio Processor]
        TP[Text Processor]
        RM[Response Manager]
    end
    
    subgraph "AI Agent Orchestration Layer"
        AO[Agent Orchestrator]
        ASA[AI Search Agent]
        FSA[File Search Agent]
        EA[Email Agent]
        TTSA[TTS Agent]
    end
    
    subgraph "Azure AI Foundry Platform"
        AIP[AI Project Client]
        AM[Agent Management]
        TM[Thread Management]
        VS[Vector Store]
        CT[Connected Tools]
        FM[File Management]
    end
    
    subgraph "Azure AI Services"
        AOI[Azure OpenAI<br/>GPT-4 + Whisper + TTS]
        AIS[Azure AI Search<br/>Vector + Semantic]
        COG[Cognitive Services]
        ID[Azure Identity]
    end
    
    subgraph "Data Sources"
        SN[ServiceNow JSON Data]
        DOC[Document Files]
        VEC[Vector Embeddings]
    end
    
    %% User Interface Connections
    UI --> SIM
    VI --> AP
    CI --> TP
    AI --> TTSA
    
    %% Application Core Connections
    SIM --> AO
    AP --> AO
    TP --> AO
    RM --> UI
    
    %% Agent Orchestration
    AO --> ASA
    AO --> FSA
    AO --> EA
    AO --> TTSA
    
    %% Azure AI Foundry Integration
    ASA --> AIP
    FSA --> AIP
    EA --> AIP
    TTSA --> AIP
    
    AIP --> AM
    AIP --> TM
    AIP --> VS
    AIP --> CT
    AIP --> FM
    
    %% Azure Services Integration
    AM --> AOI
    CT --> AOI
    VS --> AOI
    ASA --> AIS
    
    %% Data Source Connections
    SIM --> SN
    FSA --> DOC
    VS --> VEC
    AIS --> VEC
    
    %% Response Flow
    ASA --> RM
    FSA --> RM
    EA --> RM
    TTSA --> RM
    
    style UI fill:#e1f5fe
    style AO fill:#fff3e0
    style AIP fill:#f3e5f5
    style AOI fill:#e8f5e8
```

### Component Architecture Detailed

```mermaid
graph LR
    subgraph "Frontend Layer"
        A[Streamlit UI Components]
        B[Material Design Styling]
        C[Audio Controls]
        D[Chat Interface]
    end
    
    subgraph "Business Logic Layer"
        E[ServiceNowIncidentManager]
        F[Audio Processing Pipeline]
        G[Response Generation Engine]
        H[Agent Coordination Hub]
    end
    
    subgraph "Agent Layer"
        I[AI Search Agent<br/>Vector + Semantic Search]
        J[File Search Agent<br/>Document Analysis]
        K[Email Agent<br/>Communication]
        L[TTS Agent<br/>Voice Synthesis]
    end
    
    subgraph "Infrastructure Layer"
        M[Azure AI Project Client]
        N[Vector Store Management]
        O[Thread Lifecycle]
        P[Resource Cleanup]
    end
    
    subgraph "External Services"
        Q[Azure OpenAI Models]
        R[Azure AI Search Index]
        S[ServiceNow Data Store]
        T[Email Services]
    end
    
    A --> E
    B --> D
    C --> F
    D --> G
    
    E --> H
    F --> H
    G --> H
    
    H --> I
    H --> J
    H --> K
    H --> L
    
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N
    M --> O
    M --> P
    
    I --> R
    J --> N
    K --> Q
    L --> Q
    E --> S
    K --> T
    
    style H fill:#ff9999,color:#000
    style M fill:#99ccff,color:#000
```

## Multi-Agent Orchestration

### Agent Orchestration Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant SIM as ServiceNowIncidentManager
    participant AO as Agent Orchestrator
    participant ASA as AI Search Agent
    participant FSA as File Search Agent
    participant EA as Email Agent
    participant AIP as Azure AI Project
    participant VS as Vector Store
    participant AIS as Azure AI Search
    participant AOI as Azure OpenAI
    
    Note over User,AOI: Multi-Agent Request Processing Flow
    
    User->>UI: Submit Query (Text/Voice)
    UI->>SIM: Process User Request
    
    SIM->>SIM: Search Local Incidents
    SIM->>AO: Coordinate Agent Response
    
    par AI Search Agent Execution
        AO->>ASA: Execute Search Query
        ASA->>AIP: Create Search Agent Instance
        AIP->>AIS: Configure AI Search Tool
        ASA->>AIP: Create Thread & Send Message
        AIP->>AIS: Execute Vector-Semantic Search
        AIS-->>AIP: Return Ranked Results
        AIP-->>ASA: Formatted Search Response
        ASA-->>AO: Search Results with Citations
    and File Search Agent Execution
        AO->>FSA: Analyze Documents
        FSA->>AIP: Upload Files to Vector Store
        AIP->>VS: Store Document Embeddings
        FSA->>AIP: Create File Search Agent
        AIP->>VS: Query Document Vectors
        VS-->>AIP: Relevant Document Chunks
        AIP-->>FSA: Document Analysis Results
        FSA-->>AO: File Content Analysis
    and Email Agent Execution (Conditional)
        alt Email Required
            AO->>EA: Process Email Request
            EA->>AIP: Create Email Agent
            EA->>AIP: Configure Connected Tool
            AIP->>AOI: Process Email via LLM
            AOI-->>AIP: Email Content Generated
            AIP-->>EA: Email Processing Status
            EA-->>AO: Email Confirmation
        end
    end
    
    AO->>AO: Aggregate Agent Responses
    AO->>SIM: Consolidated Results
    
    alt Voice Response Enabled
        SIM->>AIP: Generate TTS Response
        AIP->>AOI: Text-to-Speech Conversion
        AOI-->>AIP: Audio Response
        AIP-->>SIM: Voice Audio
    end
    
    SIM-->>UI: Final Response (Text + Audio)
    UI-->>User: Display Results & Play Audio
    
    Note over AO,AIP: Resource Cleanup
    AO->>AIP: Cleanup Agent Resources
    AIP->>AIP: Delete Agents, Threads, Vector Stores
```

### Agent State Management

```mermaid
stateDiagram-v2
    [*] --> AgentPool: System Start
    
    state AgentPool {
        [*] --> Available
        Available --> Creating: Request Received
        Creating --> Configured: Agent Instantiated
        Configured --> Active: Thread Created
        Active --> Processing: Execute Task
        Processing --> Responding: Generate Response
        Responding --> Completed: Task Finished
        Completed --> Cleanup: Release Resources
        Cleanup --> Available: Ready for Reuse
        
        Processing --> Error: Execution Failed
        Error --> Cleanup: Handle Error
        
        state Processing {
            [*] --> SearchExecution
            SearchExecution --> VectorQuery
            VectorQuery --> SemanticAnalysis
            SemanticAnalysis --> ResultFormatting
            ResultFormatting --> [*]
        }
    }
    
    AgentPool --> [*]: System Shutdown
    
    note right of Processing
        Concurrent agent execution
        with resource isolation
    end note
```

### Multi-Agent Communication Pattern

```mermaid
graph TD
    A[User Request] --> B[Request Router]
    
    B --> C{Request Analysis}
    
    C -->|Search Intent| D[AI Search Agent]
    C -->|File Analysis| E[File Search Agent]
    C -->|Email Intent| F[Email Agent]
    C -->|Audio Output| G[TTS Agent]
    
    D --> H[Azure AI Search Tool]
    E --> I[Vector Store Tool]
    F --> J[Connected Agent Tool]
    G --> K[OpenAI TTS Tool]
    
    H --> L[Search Results]
    I --> M[Document Analysis]
    J --> N[Email Status]
    K --> O[Audio Response]
    
    L --> P[Response Aggregator]
    M --> P
    N --> P
    O --> P
    
    P --> Q[Context Merger]
    Q --> R[Final Response]
    
    style B fill:#fff3e0
    style C fill:#e3f2fd
    style P fill:#f3e5f5
    style Q fill:#e8f5e8
```

## Data Flow Diagrams

### Request Processing Data Flow

```mermaid
flowchart TD
    A[User Input<br/>Text/Voice] --> B{Input Type}
    
    B -->|Text| C[Direct Text Processing]
    B -->|Voice| D[Whisper Transcription]
    
    C --> E[Query Preprocessing]
    D --> F[Transcribed Text]
    F --> E
    
    E --> G[Incident Search<br/>Local JSON Data]
    G --> H[Context Generation]
    
    H --> I{Agent Selection Logic}
    
    I -->|Search Query| J[AI Search Agent]
    I -->|File Analysis| K[File Search Agent]
    I -->|Email Request| L[Email Agent]
    
    subgraph "AI Search Flow"
        J --> M[Azure AI Search<br/>Vector + Semantic]
        M --> N[Search Results<br/>with Citations]
    end
    
    subgraph "File Search Flow"
        K --> O[Vector Store<br/>Document Embeddings]
        O --> P[Document Chunks<br/>with Relevance Scores]
    end
    
    subgraph "Email Flow"
        L --> Q[Connected Agent<br/>Email Processing]
        Q --> R[Email Status<br/>Confirmation]
    end
    
    N --> S[Response Aggregation]
    P --> S
    R --> S
    
    S --> T{Audio Enabled?}
    
    T -->|Yes| U[TTS Generation<br/>Voice Synthesis]
    T -->|No| V[Text Response Only]
    
    U --> W[Audio + Text Response]
    V --> X[Text Response]
    
    W --> Y[UI Display + Audio Player]
    X --> Z[UI Display Only]
    
    style I fill:#ff9999
    style S fill:#99ccff
    style T fill:#ffcc99
```

### Vector Store Data Flow

```mermaid
flowchart LR
    subgraph "Data Ingestion"
        A[ServiceNow JSON File]
        B[Document Files]
        C[Text Preprocessing]
    end
    
    subgraph "Vector Processing"
        D[Azure OpenAI Embeddings]
        E[Vector Store Creation]
        F[Index Optimization]
    end
    
    subgraph "Query Processing"
        G[User Query]
        H[Query Vectorization]
        I[Similarity Search]
    end
    
    subgraph "Result Processing"
        J[Ranked Results]
        K[Context Assembly]
        L[Response Generation]
    end
    
    A --> C
    B --> C
    C --> D
    
    D --> E
    E --> F
    
    G --> H
    H --> I
    F --> I
    
    I --> J
    J --> K
    K --> L
    
    style D fill:#e1f5fe
    style I fill:#f3e5f5
    style L fill:#e8f5e8
```

## Integration Architecture

### Azure AI Foundry Integration

```mermaid
graph TB
    subgraph "Application Layer"
        APP[stsvcnow.py]
        SIM[ServiceNowIncidentManager]
        AGENTS[Agent Functions]
    end
    
    subgraph "Azure AI Foundry Core"
        AIP[AI Project Client]
        
        subgraph "Agent Management"
            AM[Agent Factory]
            ALM[Agent Lifecycle]
            ACM[Agent Configuration]
        end
        
        subgraph "Thread Management"
            TF[Thread Factory]
            TLM[Thread Lifecycle]
            MM[Message Management]
        end
        
        subgraph "Tool Management"
            TM[Tool Registry]
            CTM[Connected Tools]
            STM[Search Tools]
            FTM[File Tools]
        end
        
        subgraph "Resource Management"
            VSM[Vector Store Manager]
            FM[File Manager]
            CM[Connection Manager]
        end
    end
    
    subgraph "Azure AI Services"
        subgraph "Azure OpenAI"
            GPT[GPT-4 Models]
            WHISPER[Whisper STT]
            TTS[Text-to-Speech]
            EMB[Embedding Models]
        end
        
        subgraph "Azure AI Search"
            SI[Search Index]
            VQ[Vector Queries]
            SQ[Semantic Queries]
        end
        
        subgraph "Azure Cognitive Services"
            SPEECH[Speech Services]
            VISION[Vision Services]
        end
    end
    
    subgraph "External Resources"
        JSON[ServiceNow JSON]
        FILES[Document Files]
        EMAIL[Email Services]
    end
    
    %% Application Connections
    APP --> AIP
    SIM --> AIP
    AGENTS --> AIP
    
    %% Foundry Internal Connections
    AIP --> AM
    AIP --> TF
    AIP --> TM
    AIP --> VSM
    
    AM --> ALM
    AM --> ACM
    TF --> TLM
    TF --> MM
    TM --> CTM
    TM --> STM
    TM --> FTM
    VSM --> FM
    VSM --> CM
    
    %% Service Connections
    ACM --> GPT
    MM --> GPT
    STM --> SI
    STM --> VQ
    STM --> SQ
    FTM --> EMB
    CTM --> TTS
    CTM --> WHISPER
    
    %% External Connections
    SIM --> JSON
    FM --> FILES
    CTM --> EMAIL
    
    style AIP fill:#ff9999
    style AM fill:#99ccff
    style TF fill:#99ccff
    style TM fill:#99ccff
    style VSM fill:#99ccff
```

### Service Dependency Architecture

```mermaid
graph LR
    subgraph "Core Dependencies"
        CD1[Azure OpenAI<br/>Required]
        CD2[Azure AI Project<br/>Required]
        CD3[Azure Identity<br/>Required]
        CD4[Python 3.8+<br/>Required]
        CD5[Streamlit<br/>Required]
    end
    
    subgraph "Optional Dependencies"
        OD1[Azure AI Search<br/>Enhanced Search]
        OD2[Azure Storage<br/>File Persistence]
        OD3[Azure Key Vault<br/>Security]
        OD4[Application Insights<br/>Monitoring]
    end
    
    subgraph "Data Dependencies"
        DD1[ServiceNow JSON<br/>Incident Data]
        DD2[Document Files<br/>Knowledge Base]
        DD3[Configuration Files<br/>Settings]
    end
    
    subgraph "Runtime Environment"
        RE1[Environment Variables]
        RE2[Authentication Tokens]
        RE3[Network Connectivity]
        RE4[File System Access]
    end
    
    APP[stsvcnow.py Application] --> CD1
    APP --> CD2
    APP --> CD3
    APP --> CD4
    APP --> CD5
    
    APP -.-> OD1
    APP -.-> OD2
    APP -.-> OD3
    APP -.-> OD4
    
    APP --> DD1
    APP --> DD2
    APP --> DD3
    
    APP --> RE1
    APP --> RE2
    APP --> RE3
    APP --> RE4
    
    style CD1 fill:#ff9999
    style CD2 fill:#ff9999
    style CD3 fill:#ff9999
    style CD4 fill:#ff9999
    style CD5 fill:#ff9999
    style OD1 fill:#99ccff
    style OD2 fill:#99ccff
    style OD3 fill:#99ccff
    style OD4 fill:#99ccff
```

## Component Interactions

### Agent Interaction Matrix

```mermaid
graph TB
    subgraph "Agent Interaction Patterns"
        subgraph "Primary Agents"
            ASA[AI Search Agent]
            FSA[File Search Agent]
            EA[Email Agent]
            TTSA[TTS Agent]
        end
        
        subgraph "Shared Resources"
            AIP[AI Project Client]
            VS[Vector Store]
            TH[Thread Pool]
            RM[Resource Manager]
        end
        
        subgraph "External Services"
            SEARCH[Azure AI Search]
            OPENAI[Azure OpenAI]
            STORAGE[Azure Storage]
        end
    end
    
    %% Agent to Resource Connections
    ASA <--> AIP
    FSA <--> AIP
    EA <--> AIP
    TTSA <--> AIP
    
    FSA <--> VS
    ASA <--> TH
    FSA <--> TH
    EA <--> TH
    TTSA <--> TH
    
    AIP <--> RM
    VS <--> RM
    TH <--> RM
    
    %% Service Connections
    ASA --> SEARCH
    FSA --> OPENAI
    EA --> OPENAI
    TTSA --> OPENAI
    VS --> STORAGE
    
    %% Inter-Agent Communication
    ASA -.-> FSA
    FSA -.-> EA
    EA -.-> TTSA
    
    style AIP fill:#ff9999
    style RM fill:#99ccff
```

### Component Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Initialization
    
    state Initialization {
        [*] --> LoadConfig
        LoadConfig --> InitializeServices
        InitializeServices --> CreateManagers
        CreateManagers --> SetupUI
        SetupUI --> [*]
    }
    
    Initialization --> Ready
    
    state Ready {
        [*] --> Idle
        Idle --> ProcessingRequest: User Request
        ProcessingRequest --> AgentExecution: Route to Agents
        
        state AgentExecution {
            [*] --> CreateAgent
            CreateAgent --> ConfigureTools
            ConfigureTools --> ExecuteTask
            ExecuteTask --> ProcessResponse
            ProcessResponse --> CleanupAgent
            CleanupAgent --> [*]
        }
        
        AgentExecution --> ResponseGeneration: Agent Complete
        ResponseGeneration --> Idle: Response Sent
    }
    
    Ready --> Shutdown: Application Exit
    
    state Shutdown {
        [*] --> CleanupResources
        CleanupResources --> CloseConnections
        CloseConnections --> SaveState
        SaveState --> [*]
    }
    
    Shutdown --> [*]
    
    note right of AgentExecution
        Multiple agents can execute
        concurrently with resource
        isolation and management
    end note
```

## Process Workflows

### End-to-End User Interaction Workflow

```mermaid
flowchart TD
    A[User Opens Application] --> B[Load ServiceNow Data]
    B --> C[Initialize Azure Services]
    C --> D[Display Main Interface]
    
    D --> E{User Action}
    
    E -->|Text Input| F[Process Text Query]
    E -->|Voice Input| G[Transcribe Audio]
    E -->|Upload File| H[Process Document]
    E -->|Settings Change| I[Update Configuration]
    
    F --> J[Search Incidents]
    G --> K[Convert to Text]
    K --> J
    H --> L[Vector Store Update]
    I --> D
    
    J --> M{Query Type Analysis}
    
    M -->|Search Query| N[Execute AI Search Agent]
    M -->|File Question| O[Execute File Search Agent]
    M -->|Email Request| P[Execute Email Agent]
    
    N --> Q[Get Search Results]
    O --> R[Analyze Documents]
    P --> S[Send Email]
    
    Q --> T[Combine Results]
    R --> T
    S --> T
    
    T --> U{Audio Enabled?}
    
    U -->|Yes| V[Generate Voice Response]
    U -->|No| W[Text Response Only]
    
    V --> X[Display Text + Play Audio]
    W --> Y[Display Text Only]
    
    X --> Z[Update Conversation History]
    Y --> Z
    
    Z --> AA[Ready for Next Query]
    AA --> E
    
    style M fill:#fff3e0
    style T fill:#e3f2fd
    style U fill:#f3e5f5
```

### Error Handling and Recovery Workflow

```mermaid
flowchart TD
    A[Process Started] --> B{Service Available?}
    
    B -->|Yes| C[Execute Normal Flow]
    B -->|No| D[Service Unavailable]
    
    C --> E{Execution Success?}
    
    E -->|Yes| F[Return Results]
    E -->|No| G[Handle Error]
    
    D --> H[Display Error Message]
    G --> I{Error Type}
    
    I -->|Network Error| J[Retry with Backoff]
    I -->|Auth Error| K[Refresh Credentials]
    I -->|Resource Error| L[Cleanup and Retry]
    I -->|Critical Error| M[Fallback Mode]
    
    J --> N{Retry Count < Max?}
    N -->|Yes| O[Wait and Retry]
    N -->|No| M
    
    K --> P[Re-authenticate]
    P --> O
    
    L --> Q[Release Resources]
    Q --> O
    
    O --> B
    
    M --> R[Limited Functionality]
    R --> S[Notify User]
    
    H --> S
    S --> T[Log Error Details]
    T --> U[Continue with Degraded Service]
    
    F --> V[Success]
    U --> V
    
    style G fill:#ffcdd2
    style M fill:#fff3e0
    style S fill:#e1f5fe
```

---

## Diagram Legend

### Node Types
- **Rectangle**: Standard components and services
- **Rounded Rectangle**: User interfaces and external systems
- **Diamond**: Decision points and conditional logic
- **Circle**: Start/end points in workflows
- **Hexagon**: Data stores and repositories

### Color Coding
- **Red (#ff9999)**: Critical core components
- **Blue (#99ccff)**: Azure services and infrastructure
- **Orange (#fff3e0)**: Processing and orchestration logic
- **Green (#e8f5e8)**: External services and outputs
- **Purple (#f3e5f5)**: Data flow and storage
- **Light Blue (#e1f5fe)**: User interface components

### Connection Types
- **Solid Arrow**: Direct communication/data flow
- **Dashed Arrow**: Conditional or optional interaction
- **Bidirectional Arrow**: Two-way communication
- **Thick Arrow**: Primary data/control flow

---

*These diagrams provide a comprehensive visual representation of the ServiceNow AI Assistant architecture and can be rendered using any Mermaid-compatible viewer or documentation platform.*