# AgenticAI Foundry - stmfg1.py Mermaid Architecture Diagrams

## Table of Contents
1. [System Overview Diagrams](#system-overview-diagrams)
2. [Agent Architecture Diagrams](#agent-architecture-diagrams)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Sequence Diagrams](#sequence-diagrams)
5. [Process Flow Diagrams](#process-flow-diagrams)
6. [Technical Architecture Diagrams](#technical-architecture-diagrams)
7. [Integration Diagrams](#integration-diagrams)

## System Overview Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Streamlit Web Interface]
        subgraph "Phase Tabs"
            P1[Phase 1: R&D]
            P2[Phase 2: Prototyping]
            P3[Phase 3: Production]
        end
    end
    
    subgraph "Business Logic Layer"
        subgraph "Agent Orchestration"
            AO1[Phase 1 Orchestrator]
            AO2[Phase 2 Orchestrator]
            AO3[Phase 3 Orchestrator]
        end
        
        subgraph "Connected Agents"
            subgraph "Phase 1 Agents"
                A1[Ideation Agent]
                A2[Raw Material Agent]
                A3[Formulation Agent]
                A4[Lab Test Agent]
                A5[Validation Agent]
            end
            
            subgraph "Phase 2 Agents"
                A6[Prototype Agent]
                A7[Testing Agent]
                A8[Trial Agent]
                A9[Refinement Agent]
                A10[QA Agent]
            end
            
            subgraph "Phase 3 Agents"
                A11[Design Optimization]
                A12[Pilot Production]
                A13[Manufacturing]
                A14[Quality Control]
                A15[Packaging]
                A16[Commercialization]
            end
        end
    end
    
    subgraph "Service Layer"
        subgraph "Azure AI Services"
            AIP[AI Project Client]
            AGM[Agent Manager]
            THM[Thread Manager]
            MSG[Message Manager]
        end
        
        subgraph "Monitoring"
            TEL[Telemetry Service]
            APP[Application Insights]
        end
    end
    
    subgraph "Infrastructure Layer"
        subgraph "Azure Cloud"
            AUTH[Azure Identity]
            AI[Azure OpenAI]
            MON[Monitoring Services]
        end
    end
    
    UI --> AO1
    UI --> AO2
    UI --> AO3
    
    P1 --> AO1
    P2 --> AO2
    P3 --> AO3
    
    AO1 --> A1
    AO1 --> A2
    AO1 --> A3
    AO1 --> A4
    AO1 --> A5
    
    AO2 --> A6
    AO2 --> A7
    AO2 --> A8
    AO2 --> A9
    AO2 --> A10
    
    AO3 --> A11
    AO3 --> A12
    AO3 --> A13
    AO3 --> A14
    AO3 --> A15
    AO3 --> A16
    
    AO1 --> AIP
    AO2 --> AIP
    AO3 --> AIP
    
    AIP --> AGM
    AIP --> THM
    AIP --> MSG
    
    AGM --> AUTH
    AGM --> AI
    
    TEL --> APP
    TEL --> MON
```

### Component Relationship Model

```mermaid
graph LR
    subgraph "User Interface"
        ST[Streamlit App]
        SS[Session State]
        CH[Chat Interface]
    end
    
    subgraph "Application Logic"
        PM[Phase Manager]
        AE[Agent Executor]
        RP[Result Parser]
        UM[Usage Monitor]
    end
    
    subgraph "Azure Integration"
        PC[Project Client]
        AC[Agent Client]
        TC[Thread Client]
        MC[Message Client]
    end
    
    subgraph "External Services"
        AOI[Azure OpenAI]
        AI[Application Insights]
        ID[Identity Service]
    end
    
    ST --> PM
    ST --> SS
    CH --> PM
    
    PM --> AE
    AE --> RP
    AE --> UM
    
    AE --> PC
    PC --> AC
    PC --> TC
    PC --> MC
    
    AC --> AOI
    AC --> ID
    UM --> AI
```

## Agent Architecture Diagrams

### Phase 1: Research & Development Agent Network

```mermaid
graph TD
    subgraph "Phase 1: R&D Agent Network"
        PO1[Phase 1 Orchestrator<br/>PresalesAgent]
        
        subgraph "Connected Agents"
            IA[Ideation Agent<br/>Creative Catalyst]
            RMA[Raw Material Agent<br/>Materials Specialist]
            FA[Formulation Agent<br/>Chemical Engineer]
            LTA[Lab Test Agent<br/>QA Specialist]
            CVA[Concept Validation Agent<br/>Integration Expert]
        end
        
        subgraph "Agent Capabilities"
            IA --> IAC[Market Analysis<br/>Trend Identification<br/>Concept Generation]
            RMA --> RMAC[Material Selection<br/>Cost Analysis<br/>Compliance Check]
            FA --> FAC[Recipe Development<br/>Property Prediction<br/>Iteration Planning]
            LTA --> LTAC[Test Planning<br/>Result Simulation<br/>Failure Analysis]
            CVA --> CVAC[Feedback Synthesis<br/>SWOT Analysis<br/>Concept Refinement]
        end
    end
    
    PO1 --> IA
    PO1 --> RMA
    PO1 --> FA
    PO1 --> LTA
    PO1 --> CVA
    
    IA -.-> RMA
    RMA -.-> FA
    FA -.-> LTA
    LTA -.-> CVA
    CVA -.-> PO1
```

### Phase 2: Prototyping & Testing Agent Network

```mermaid
graph TD
    subgraph "Phase 2: Prototyping Agent Network"
        PO2[Phase 2 Orchestrator<br/>PresalesAgent]
        
        subgraph "Connected Agents"
            PCA[Prototype Creation<br/>Process Specialist]
            PTA[Performance Testing<br/>Testing Expert]
            CFTA[Customer Field Trial<br/>Customer Specialist]
            IRA[Iteration Refinement<br/>Optimization Expert]
            QAA[Quality Assurance<br/>QC Specialist]
        end
        
        subgraph "Agent Outputs"
            PCA --> PCAO[Prototyping Process<br/>Batch Preparation<br/>Challenge Mitigation]
            PTA --> PTAO[Test Plans<br/>Simulated Results<br/>Performance Analysis]
            CFTA --> CFTAO[Trial Plans<br/>Customer Feedback<br/>Adjustments]
            IRA --> IRAO[Result Analysis<br/>Refinement Proposals<br/>Compliance Check]
            QAA --> QAAO[QC Plans<br/>QC Results<br/>Approval Status]
        end
    end
    
    PO2 --> PCA
    PO2 --> PTA
    PO2 --> CFTA
    PO2 --> IRA
    PO2 --> QAA
    
    PCA -.-> PTA
    PTA -.-> CFTA
    CFTA -.-> IRA
    IRA -.-> QAA
    QAA -.-> PO2
```

### Phase 3: Production Scaling Agent Network

```mermaid
graph TD
    subgraph "Phase 3: Production Agent Network"
        PO3[Phase 3 Orchestrator<br/>PresalesAgent]
        
        subgraph "Connected Agents"
            DOA[Design Optimization<br/>Process Engineer]
            PPRA[Pilot Production<br/>Ramp-up Specialist]
            FSMA[Full-Scale Manufacturing<br/>Production Engineer]
            QCPA[Quality Control Production<br/>QA Expert]
            PA[Packaging Agent<br/>Logistics Specialist]
            CA[Commercialization<br/>Market Specialist]
        end
        
        subgraph "Production Flow"
            DOA --> PPRA
            PPRA --> FSMA
            FSMA --> QCPA
            QCPA --> PA
            PA --> CA
        end
    end
    
    PO3 --> DOA
    PO3 --> PPRA
    PO3 --> FSMA
    PO3 --> QCPA
    PO3 --> PA
    PO3 --> CA
```

## Data Flow Diagrams

### User Query Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant StreamlitUI as Streamlit UI
    participant SessionState as Session State
    participant PhaseOrchestrator as Phase Orchestrator
    participant ConnectedAgents as Connected Agents
    participant AzureAI as Azure AI Services
    participant Database as Results Database
    
    User->>StreamlitUI: Submit Query
    StreamlitUI->>SessionState: Validate State
    SessionState-->>StreamlitUI: State Valid
    
    StreamlitUI->>PhaseOrchestrator: Execute Phase Function
    PhaseOrchestrator->>AzureAI: Create Project Client
    AzureAI-->>PhaseOrchestrator: Client Instance
    
    PhaseOrchestrator->>ConnectedAgents: Create Specialized Agents
    ConnectedAgents-->>PhaseOrchestrator: Agent Instances
    
    PhaseOrchestrator->>AzureAI: Create Main Agent with Tools
    AzureAI-->>PhaseOrchestrator: Main Agent Created
    
    PhaseOrchestrator->>AzureAI: Create Thread & Message
    AzureAI-->>PhaseOrchestrator: Thread & Message IDs
    
    PhaseOrchestrator->>AzureAI: Execute Agent Run
    AzureAI->>ConnectedAgents: Tool Calls to Specialists
    
    loop Agent Execution
        ConnectedAgents->>ConnectedAgents: Process Specialized Task
        ConnectedAgents-->>AzureAI: Return Results
    end
    
    AzureAI-->>PhaseOrchestrator: Aggregated Results
    PhaseOrchestrator->>Database: Parse & Store Results
    PhaseOrchestrator->>AzureAI: Cleanup Agents & Threads
    
    PhaseOrchestrator-->>StreamlitUI: Return Summary & Agent Outputs
    StreamlitUI->>SessionState: Update History
    StreamlitUI-->>User: Display Results
```

### Agent Communication Flow

```mermaid
flowchart TD
    subgraph "Agent Execution Pipeline"
        START([User Query Input])
        INIT[Initialize Project Client]
        CREATE[Create Connected Agents]
        ORCHESTRATE[Create Main Orchestrator]
        THREAD[Create Thread & Message]
        EXECUTE[Execute Agent Run]
        MONITOR[Monitor Run Status]
        PARSE[Parse Agent Outputs]
        TRACK[Track Token Usage]
        CLEANUP[Cleanup Resources]
        RETURN([Return Results])
    end
    
    subgraph "Status Monitoring"
        QUEUED[Queued]
        PROGRESS[In Progress]
        ACTION[Requires Action]
        COMPLETE[Completed]
        FAILED[Failed]
    end
    
    START --> INIT
    INIT --> CREATE
    CREATE --> ORCHESTRATE
    ORCHESTRATE --> THREAD
    THREAD --> EXECUTE
    EXECUTE --> MONITOR
    
    MONITOR --> QUEUED
    MONITOR --> PROGRESS
    MONITOR --> ACTION
    MONITOR --> COMPLETE
    MONITOR --> FAILED
    
    QUEUED --> MONITOR
    PROGRESS --> MONITOR
    ACTION --> MONITOR
    COMPLETE --> PARSE
    FAILED --> CLEANUP
    
    PARSE --> TRACK
    TRACK --> CLEANUP
    CLEANUP --> RETURN
```

## Sequence Diagrams

### Complete Manufacturing Process Flow

```mermaid
sequenceDiagram
    participant Customer
    participant UI as Streamlit Interface
    participant P1 as Phase 1: R&D
    participant P2 as Phase 2: Prototyping
    participant P3 as Phase 3: Production
    participant Azure as Azure AI Services
    
    Note over Customer,Azure: Phase 1: Research & Development
    Customer->>UI: Submit R&D Requirements
    UI->>P1: Process R&D Query
    P1->>Azure: Create R&D Agent Network
    Azure-->>P1: 5 Specialized Agents Ready
    
    P1->>Azure: Execute Ideation → Materials → Formulation → Testing → Validation
    Azure-->>P1: Validated Concept with Specifications
    P1-->>UI: R&D Summary & Agent Outputs
    UI-->>Customer: Display R&D Results
    
    Note over Customer,Azure: Phase 2: Prototyping & Testing
    Customer->>UI: Submit Prototyping Requirements
    UI->>P2: Process Prototyping Query
    P2->>Azure: Create Prototyping Agent Network
    Azure-->>P2: 5 Specialized Agents Ready
    
    P2->>Azure: Execute Creation → Testing → Trials → Refinement → QA
    Azure-->>P2: Quality-Assured Prototype
    P2-->>UI: Prototyping Summary & Agent Outputs
    UI-->>Customer: Display Prototyping Results
    
    Note over Customer,Azure: Phase 3: Production Scaling
    Customer->>UI: Submit Production Requirements
    UI->>P3: Process Production Query
    P3->>Azure: Create Production Agent Network
    Azure-->>P3: 6 Specialized Agents Ready
    
    P3->>Azure: Execute Optimization → Pilot → Manufacturing → QC → Packaging → Commercialization
    Azure-->>P3: Market-Ready Product
    P3-->>UI: Production Summary & Agent Outputs
    UI-->>Customer: Display Production Results
```

### Agent Lifecycle Management

```mermaid
sequenceDiagram
    participant Orchestrator
    participant ProjectClient as Azure Project Client
    participant SpecializedAgent as Specialized Agent
    participant Thread
    participant Message
    participant Run
    
    Note over Orchestrator,Run: Agent Creation Phase
    Orchestrator->>ProjectClient: create_agent(config)
    ProjectClient-->>Orchestrator: agent_instance
    Orchestrator->>Orchestrator: create_connected_tool(agent)
    
    Note over Orchestrator,Run: Execution Phase
    Orchestrator->>ProjectClient: create_thread()
    ProjectClient-->>Thread: thread_instance
    Orchestrator->>Thread: create_message(query)
    Thread-->>Message: message_instance
    
    Orchestrator->>ProjectClient: create_run(thread, agent)
    ProjectClient-->>Run: run_instance
    
    loop Status Monitoring
        Orchestrator->>Run: get_status()
        Run-->>Orchestrator: status_update
    end
    
    Run->>SpecializedAgent: tool_call(parameters)
    SpecializedAgent-->>Run: agent_response
    
    Note over Orchestrator,Run: Results Processing
    Orchestrator->>Run: get_run_steps()
    Run-->>Orchestrator: execution_steps
    Orchestrator->>Orchestrator: parse_agent_outputs(steps)
    
    Note over Orchestrator,Run: Cleanup Phase
    Orchestrator->>ProjectClient: delete_agent(agent_id)
    Orchestrator->>ProjectClient: delete_thread(thread_id)
    ProjectClient-->>Orchestrator: cleanup_complete
```

## Process Flow Diagrams

### End-to-End Manufacturing Process

```mermaid
flowchart TD
    subgraph "Phase 1: Research & Development"
        START([Market Requirements])
        IDEATION[Ideation Agent<br/>Generate Concepts]
        MATERIALS[Raw Material Agent<br/>Select Materials]
        FORMULATION[Formulation Agent<br/>Develop Recipes]
        LABTEST[Lab Test Agent<br/>Validate Properties]
        VALIDATION[Concept Validation<br/>Final Approval]
        R1([R&D Complete])
    end
    
    subgraph "Phase 2: Prototyping & Testing"
        R1P2([Approved Concept])
        PROTOTYPE[Prototype Creation<br/>Create Samples]
        PERFORMANCE[Performance Testing<br/>Validate Performance]
        CUSTOMER[Customer Trials<br/>Field Testing]
        REFINE[Iteration & Refinement<br/>Optimize Formula]
        QA[Quality Assurance<br/>Final QC Check]
        R2([Prototype Approved])
    end
    
    subgraph "Phase 3: Production Scaling"
        R2P3([Approved Prototype])
        DESIGN[Design Optimization<br/>Scale for Production]
        PILOT[Pilot Production<br/>Test Manufacturing]
        MANUFACTURING[Full Manufacturing<br/>Mass Production]
        QC[Quality Control<br/>Production QC]
        PACKAGING[Packaging<br/>Distribution Ready]
        COMMERCIAL[Commercialization<br/>Market Launch]
        R3([Product Launched])
    end
    
    START --> IDEATION
    IDEATION --> MATERIALS
    MATERIALS --> FORMULATION
    FORMULATION --> LABTEST
    LABTEST --> VALIDATION
    VALIDATION --> R1
    
    R1 --> R1P2
    R1P2 --> PROTOTYPE
    PROTOTYPE --> PERFORMANCE
    PERFORMANCE --> CUSTOMER
    CUSTOMER --> REFINE
    REFINE --> QA
    QA --> R2
    
    R2 --> R2P3
    R2P3 --> DESIGN
    DESIGN --> PILOT
    PILOT --> MANUFACTURING
    MANUFACTURING --> QC
    QC --> PACKAGING
    PACKAGING --> COMMERCIAL
    COMMERCIAL --> R3
    
    style START fill:#e1f5fe
    style R1 fill:#c8e6c9
    style R2 fill:#c8e6c9
    style R3 fill:#4caf50,color:#fff
```

### Agent Decision Flow

```mermaid
flowchart TD
    subgraph "Agent Decision Framework"
        INPUT([User Query])
        CLASSIFY{Classify Query Type}
        
        R_QUERY[R&D Query]
        P_QUERY[Prototyping Query]
        M_QUERY[Manufacturing Query]
        
        R_AGENTS[Activate R&D Agents]
        P_AGENTS[Activate Prototyping Agents]
        M_AGENTS[Activate Manufacturing Agents]
        
        PROCESS[Process through Agent Network]
        
        VALIDATE{Validate Results}
        REFINE[Refine Output]
        
        OUTPUT([Structured Response])
    end
    
    INPUT --> CLASSIFY
    
    CLASSIFY -->|Innovation/Materials| R_QUERY
    CLASSIFY -->|Testing/Quality| P_QUERY
    CLASSIFY -->|Scale/Production| M_QUERY
    
    R_QUERY --> R_AGENTS
    P_QUERY --> P_AGENTS
    M_QUERY --> M_AGENTS
    
    R_AGENTS --> PROCESS
    P_AGENTS --> PROCESS
    M_AGENTS --> PROCESS
    
    PROCESS --> VALIDATE
    VALIDATE -->|Pass| OUTPUT
    VALIDATE -->|Needs Refinement| REFINE
    REFINE --> PROCESS
```

## Technical Architecture Diagrams

### System Component Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        subgraph "Streamlit Application"
            UI[User Interface]
            TAB[Tab Navigation]
            CHAT[Chat Interface]
            STATE[Session State Manager]
        end
    end
    
    subgraph "Business Logic Layer"
        subgraph "Phase Controllers"
            PC1[Phase 1 Controller]
            PC2[Phase 2 Controller] 
            PC3[Phase 3 Controller]
        end
        
        subgraph "Agent Management"
            AM[Agent Manager]
            AT[Agent Tools]
            AC[Agent Communication]
        end
        
        subgraph "Data Processing"
            RP[Result Parser]
            UM[Usage Monitor]
            ES[Error Handler]
        end
    end
    
    subgraph "Integration Layer"
        subgraph "Azure AI Integration"
            APC[AI Project Client]
            AGT[Agent Gateway]
            THG[Thread Gateway]
            MSG[Message Gateway]
        end
        
        subgraph "Monitoring Integration"
            TEL[Telemetry Client]
            LOG[Logging Service]
            MET[Metrics Collector]
        end
    end
    
    subgraph "External Services"
        subgraph "Azure Services"
            AOI[Azure OpenAI]
            AID[Azure Identity]
            AIN[Application Insights]
        end
    end
    
    UI --> PC1
    UI --> PC2
    UI --> PC3
    TAB --> STATE
    CHAT --> AM
    
    PC1 --> AM
    PC2 --> AM
    PC3 --> AM
    
    AM --> APC
    AT --> AGT
    AC --> THG
    
    RP --> UM
    UM --> TEL
    ES --> LOG
    
    APC --> AOI
    AGT --> AID
    THG --> AOI
    MSG --> AOI
    
    TEL --> AIN
    LOG --> AIN
    MET --> AIN
```

### Data Architecture

```mermaid
graph LR
    subgraph "Data Input"
        UQ[User Queries]
        CF[Configuration Files]
        ENV[Environment Variables]
    end
    
    subgraph "Data Processing"
        subgraph "Session Data"
            SS[Session State]
            AH[Agent History]
            TU[Token Usage]
        end
        
        subgraph "Runtime Data"
            AI[Agent Instructions]
            AR[Agent Responses]
            ER[Execution Results]
        end
    end
    
    subgraph "Data Storage"
        subgraph "Temporary Storage"
            MEM[Memory Cache]
            TEMP[Temporary Files]
        end
        
        subgraph "Persistent Storage"
            LOG[Log Files]
            TEL[Telemetry Data]
        end
    end
    
    subgraph "Data Output"
        UR[User Responses]
        REP[Reports]
        MET[Metrics]
    end
    
    UQ --> SS
    CF --> AI
    ENV --> AI
    
    SS --> AR
    AI --> AR
    AR --> ER
    
    ER --> MEM
    AR --> TEMP
    TU --> TEL
    
    ER --> UR
    MET --> REP
    TEL --> MET
```

## Integration Diagrams

### Azure Services Integration

```mermaid
graph TD
    subgraph "Application Layer"
        APP[stmfg1.py Application]
    end
    
    subgraph "Azure AI Platform"
        subgraph "Core AI Services"
            AIP[AI Project Service]
            AOI[Azure OpenAI Service]
            COG[Cognitive Services]
        end
        
        subgraph "Management Services"
            AID[Azure Identity]
            ARM[Azure Resource Manager]
            KEY[Key Vault]
        end
        
        subgraph "Monitoring Services"
            AIN[Application Insights]
            MON[Azure Monitor]
            LOG[Log Analytics]
        end
    end
    
    subgraph "Authentication Flow"
        DEF[DefaultAzureCredential]
        MSI[Managed Identity]
        CLI[Azure CLI]
        VS[Visual Studio]
    end
    
    APP --> AIP
    APP --> AOI
    APP --> AID
    APP --> AIN
    
    AIP --> ARM
    AOI --> KEY
    
    AID --> DEF
    DEF --> MSI
    DEF --> CLI
    DEF --> VS
    
    AIN --> MON
    MON --> LOG
```

### External System Integration Pattern

```mermaid
graph LR
    subgraph "stmfg1.py Core"
        CORE[Application Core]
        AIF[Agent Interface]
        EXT[Extension Points]
    end
    
    subgraph "Integration Layer"
        API[API Gateway]
        AUTH[Auth Middleware]
        VAL[Validation Layer]
        MAP[Data Mapper]
    end
    
    subgraph "External Systems (Future)"
        ERP[ERP Systems]
        LAB[Lab Equipment]
        CRM[CRM Systems]
        SUP[Supplier APIs]
        REG[Regulatory DBs]
    end
    
    CORE --> AIF
    AIF --> EXT
    EXT --> API
    
    API --> AUTH
    AUTH --> VAL
    VAL --> MAP
    
    MAP --> ERP
    MAP --> LAB
    MAP --> CRM
    MAP --> SUP
    MAP --> REG
```

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Developer Machine]
        VSCODE[VS Code + Extensions]
        DOCKER[Docker Desktop]
    end
    
    subgraph "Cloud Infrastructure"
        subgraph "Container Platform"
            ACI[Azure Container Instances]
            AKS[Azure Kubernetes Service]
            ACR[Azure Container Registry]
        end
        
        subgraph "App Services"
            WEB[Azure Web Apps]
            FUNC[Azure Functions]
            LOGIC[Logic Apps]
        end
        
        subgraph "AI Services"
            PROJ[AI Project]
            OPENAI[Azure OpenAI]
            SEARCH[AI Search]
        end
    end
    
    subgraph "CI/CD Pipeline"
        REPO[Git Repository]
        BUILD[Build Pipeline]
        TEST[Test Pipeline]
        DEPLOY[Deployment Pipeline]
    end
    
    DEV --> DOCKER
    DOCKER --> ACR
    
    REPO --> BUILD
    BUILD --> TEST
    TEST --> DEPLOY
    
    DEPLOY --> ACI
    DEPLOY --> AKS
    DEPLOY --> WEB
    
    ACI --> PROJ
    AKS --> OPENAI
    WEB --> SEARCH
```

## Monitoring and Observability

### Telemetry Flow Diagram

```mermaid
sequenceDiagram
    participant App as stmfg1.py
    participant Tel as Telemetry Service
    participant AI as Application Insights
    participant Mon as Azure Monitor
    participant Alert as Alert Manager
    
    Note over App,Alert: Application Startup
    App->>Tel: Initialize Telemetry
    Tel->>AI: Connect to App Insights
    AI-->>Tel: Connection Established
    
    Note over App,Alert: Agent Execution
    App->>Tel: Log Agent Start
    Tel->>AI: Send Custom Event
    App->>Tel: Track Token Usage
    Tel->>AI: Send Custom Metric
    App->>Tel: Log Agent Completion
    Tel->>AI: Send Custom Event
    
    Note over App,Alert: Error Handling
    App->>Tel: Log Error Event
    Tel->>AI: Send Exception
    AI->>Mon: Trigger Alert Rule
    Mon->>Alert: Send Notification
    
    Note over App,Alert: Performance Monitoring
    App->>Tel: Track Response Time
    Tel->>AI: Send Performance Counter
    AI->>Mon: Update Dashboard
```

This comprehensive collection of Mermaid diagrams provides complete visualization of the stmfg1.py system architecture, from high-level overview through detailed technical implementation, covering all aspects of the adhesive manufacturing orchestrator's design and operation.