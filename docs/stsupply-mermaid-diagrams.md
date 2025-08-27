# Healthcare Supply Chain Orchestrator - Mermaid Diagrams

## Table of Contents
1. [System Architecture Diagrams](#system-architecture-diagrams)
2. [Agent Interaction Diagrams](#agent-interaction-diagrams)
3. [Process Flow Diagrams](#process-flow-diagrams)
4. [Sequence Diagrams](#sequence-diagrams)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Deployment Diagrams](#deployment-diagrams)
7. [Integration Diagrams](#integration-diagrams)

## System Architecture Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit UI]
        API[REST API]
        Dashboard[Analytics Dashboard]
    end
    
    subgraph "Orchestration Layer"
        MainAgent[Main Orchestrator Agent]
        MessageQueue[Message Queue]
        StateManager[State Management]
    end
    
    subgraph "SCOR Agents Layer"
        PlanAgent[Plan Agent<br/>Demand & Supply Planning]
        SourceAgent[Source Agent<br/>Procurement & Suppliers]
        MakeAgent[Make Agent<br/>Manufacturing & Production]
        DeliverAgent[Deliver Agent<br/>Distribution & Logistics]
        ReturnAgent[Return Agent<br/>Reverse Logistics]
    end
    
    subgraph "AI Services Layer"
        AzureAI[Azure AI Foundry]
        OpenAI[Azure OpenAI]
        CognitiveServices[Cognitive Services]
    end
    
    subgraph "Data Layer"
        DataLake[(Azure Data Lake)]
        Database[(Azure SQL DB)]
        Cache[(Redis Cache)]
        DocumentDB[(Cosmos DB)]
    end
    
    subgraph "Integration Layer"
        ERP[ERP Systems]
        WMS[WMS Systems]
        Regulatory[Regulatory APIs]
        ThirdParty[Third-party Services]
    end
    
    subgraph "Infrastructure Layer"
        Kubernetes[AKS Cluster]
        Storage[Azure Storage]
        KeyVault[Azure Key Vault]
        ServiceBus[Azure Service Bus]
    end
    
    subgraph "Monitoring Layer"
        AppInsights[Application Insights]
        LogAnalytics[Log Analytics]
        Prometheus[Prometheus]
        Grafana[Grafana]
    end
    
    %% Connections
    UI --> MainAgent
    API --> MainAgent
    Dashboard --> MainAgent
    
    MainAgent --> MessageQueue
    MainAgent --> StateManager
    MessageQueue --> PlanAgent
    MessageQueue --> SourceAgent
    MessageQueue --> MakeAgent
    MessageQueue --> DeliverAgent
    MessageQueue --> ReturnAgent
    
    PlanAgent --> AzureAI
    SourceAgent --> AzureAI
    MakeAgent --> AzureAI
    DeliverAgent --> AzureAI
    ReturnAgent --> AzureAI
    
    AzureAI --> OpenAI
    AzureAI --> CognitiveServices
    
    MainAgent --> DataLake
    MainAgent --> Database
    MainAgent --> Cache
    MainAgent --> DocumentDB
    
    MainAgent --> ERP
    MainAgent --> WMS
    MainAgent --> Regulatory
    MainAgent --> ThirdParty
    
    MainAgent --> ServiceBus
    StateManager --> KeyVault
    
    MainAgent --> AppInsights
    Infrastructure --> LogAnalytics
    Infrastructure --> Prometheus
    Prometheus --> Grafana
    
    %% Styling
    classDef uiLayer fill:#e1f5fe
    classDef orchestrationLayer fill:#f3e5f5
    classDef agentLayer fill:#e8f5e8
    classDef aiLayer fill:#fff3e0
    classDef dataLayer fill:#fce4ec
    classDef integrationLayer fill:#f1f8e9
    classDef infraLayer fill:#e3f2fd
    classDef monitoringLayer fill:#fff8e1
    
    class UI,API,Dashboard uiLayer
    class MainAgent,MessageQueue,StateManager orchestrationLayer
    class PlanAgent,SourceAgent,MakeAgent,DeliverAgent,ReturnAgent agentLayer
    class AzureAI,OpenAI,CognitiveServices aiLayer
    class DataLake,Database,Cache,DocumentDB dataLayer
    class ERP,WMS,Regulatory,ThirdParty integrationLayer
    class Kubernetes,Storage,KeyVault,ServiceBus infraLayer
    class AppInsights,LogAnalytics,Prometheus,Grafana monitoringLayer
```

### SCOR Agent Architecture

```mermaid
graph LR
    subgraph "Plan Stage"
        P1[Demand Forecasting]
        P2[Supply Planning]
        P3[Resource Allocation]
        P4[Risk Assessment]
        P1 --> P2 --> P3 --> P4
    end
    
    subgraph "Source Stage"
        S1[Supplier Identification]
        S2[Contract Negotiation]
        S3[Procurement Planning]
        S4[Supplier Audits]
        S1 --> S2 --> S3 --> S4
    end
    
    subgraph "Make Stage"
        M1[Production Planning]
        M2[Quality Control]
        M3[Manufacturing Execution]
        M4[Batch Management]
        M1 --> M2 --> M3 --> M4
    end
    
    subgraph "Deliver Stage"
        D1[Distribution Planning]
        D2[Logistics Coordination]
        D3[Last-mile Delivery]
        D4[Performance Tracking]
        D1 --> D2 --> D3 --> D4
    end
    
    subgraph "Return Stage"
        R1[Reverse Logistics]
        R2[Product Recalls]
        R3[Sustainability Management]
        R4[Post-market Surveillance]
        R1 --> R2 --> R3 --> R4
    end
    
    %% Cross-stage connections
    P4 --> S1
    S4 --> M1
    M4 --> D1
    D4 --> R1
    R4 --> P1
    
    %% Feedback loops
    M2 --> S2
    D2 --> M2
    R2 --> D2
    R3 --> S1
```

## Agent Interaction Diagrams

### Multi-Agent Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Orch as Main Orchestrator
    participant Plan as Plan Agent
    participant Source as Source Agent
    participant Make as Make Agent
    participant Deliver as Deliver Agent
    participant Return as Return Agent
    participant AI as Azure AI Services
    
    User->>UI: Submit supply chain query
    UI->>Orch: Process query request
    
    Note over Orch: Query Analysis & Agent Selection
    
    par Parallel Agent Execution
        Orch->>Plan: Analyze demand & planning
        Orch->>Source: Evaluate sourcing options
        Orch->>Make: Assess manufacturing needs
        Orch->>Deliver: Plan distribution strategy
        Orch->>Return: Consider return scenarios
    end
    
    Plan->>AI: Request demand forecast
    AI-->>Plan: Forecast data & analytics
    Plan-->>Orch: Planning recommendations
    
    Source->>AI: Analyze supplier options
    AI-->>Source: Supplier insights
    Source-->>Orch: Sourcing strategy
    
    Make->>AI: Production optimization
    AI-->>Make: Manufacturing insights
    Make-->>Orch: Production plan
    
    Deliver->>AI: Logistics optimization
    AI-->>Deliver: Distribution insights
    Deliver-->>Orch: Delivery strategy
    
    Return->>AI: Analyze return patterns
    AI-->>Return: Return insights
    Return-->>Orch: Return recommendations
    
    Note over Orch: Synthesize Agent Responses
    
    Orch->>UI: Comprehensive analysis
    UI->>User: Display results with agent outputs
```

### Agent Collaboration Patterns

```mermaid
graph TD
    subgraph "Collaborative Intelligence"
        A[Query Input] --> B{Analysis Required?}
        B -->|Simple| C[Single Agent]
        B -->|Complex| D[Multi-Agent Orchestration]
        
        D --> E[Plan Agent Analysis]
        E --> F{Sourcing Impact?}
        F -->|Yes| G[Source Agent Input]
        F -->|No| H[Continue to Make]
        
        G --> I{Manufacturing Impact?}
        H --> I
        I -->|Yes| J[Make Agent Input]
        I -->|No| K[Continue to Deliver]
        
        J --> L{Distribution Impact?}
        K --> L
        L -->|Yes| M[Deliver Agent Input]
        L -->|No| N[Continue to Return]
        
        M --> O{Return Considerations?}
        N --> O
        O -->|Yes| P[Return Agent Input]
        O -->|No| Q[Synthesis Phase]
        
        P --> Q
        C --> Q
        Q --> R[Integrated Response]
        
        subgraph "Cross-Agent Learning"
            S[Shared Context]
            T[Pattern Recognition]
            U[Continuous Improvement]
            S --> T --> U --> S
        end
        
        R --> S
    end
    
    %% Styling
    classDef decisionNode fill:#ffe0b2
    classDef agentNode fill:#c8e6c9
    classDef processNode fill:#e1bee7
    classDef learningNode fill:#ffcdd2
    
    class B,F,I,L,O decisionNode
    class E,G,J,M,P agentNode
    class Q,R processNode
    class S,T,U learningNode
```

## Process Flow Diagrams

### End-to-End Supply Chain Process

```mermaid
flowchart TD
    Start([User Query Input]) --> Analysis{Query Analysis}
    
    Analysis --> Pharmaceutical[Pharmaceutical Process]
    Analysis --> Biotech[Biotech Process]
    Analysis --> MedDevice[Medical Device Process]
    Analysis --> ClinicalTrial[Clinical Trial Process]
    
    subgraph "Pharmaceutical Supply Chain"
        Pharmaceutical --> P1[Demand Forecasting<br/>Plan Agent]
        P1 --> P2[API Sourcing<br/>Source Agent]
        P2 --> P3[Drug Manufacturing<br/>Make Agent]
        P3 --> P4[Distribution Network<br/>Deliver Agent]
        P4 --> P5[Recall Management<br/>Return Agent]
    end
    
    subgraph "Biotech Supply Chain"
        Biotech --> B1[Patient Demand Analysis<br/>Plan Agent]
        B1 --> B2[Specialized Materials<br/>Source Agent]
        B2 --> B3[Personalized Production<br/>Make Agent]
        B3 --> B4[Cold Chain Delivery<br/>Deliver Agent]
        B4 --> B5[Outcome Tracking<br/>Return Agent]
    end
    
    subgraph "Medical Device Supply Chain"
        MedDevice --> M1[Market Forecast<br/>Plan Agent]
        M1 --> M2[Component Sourcing<br/>Source Agent]
        M2 --> M3[Device Assembly<br/>Make Agent]
        M3 --> M4[Global Distribution<br/>Deliver Agent]
        M4 --> M5[Service & Returns<br/>Return Agent]
    end
    
    subgraph "Clinical Trial Supply Chain"
        ClinicalTrial --> C1[Enrollment Planning<br/>Plan Agent]
        C1 --> C2[Investigational Drugs<br/>Source Agent]
        C2 --> C3[Trial Kit Preparation<br/>Make Agent]
        C3 --> C4[Site Distribution<br/>Deliver Agent]
        C4 --> C5[Unused Drug Returns<br/>Return Agent]
    end
    
    P5 --> Integration{Integration & Synthesis}
    B5 --> Integration
    M5 --> Integration
    C5 --> Integration
    
    Integration --> Compliance{Regulatory Compliance Check}
    Compliance -->|Pass| Output[Comprehensive Recommendations]
    Compliance -->|Fail| Revision[Compliance Revision]
    Revision --> Integration
    
    Output --> Monitoring[Continuous Monitoring]
    Monitoring --> Feedback[Performance Feedback]
    Feedback --> Start
    
    %% Styling
    classDef startEnd fill:#4caf50,color:#fff
    classDef decision fill:#ff9800,color:#fff
    classDef process fill:#2196f3,color:#fff
    classDef agent fill:#9c27b0,color:#fff
    
    class Start,Output startEnd
    class Analysis,Integration,Compliance decision
    class Monitoring,Feedback,Revision process
    class P1,P2,P3,P4,P5,B1,B2,B3,B4,B5,M1,M2,M3,M4,M5,C1,C2,C3,C4,C5 agent
```

### Regulatory Compliance Flow

```mermaid
flowchart LR
    subgraph "Regulatory Intelligence"
        R1[Regulation Monitoring] --> R2[Impact Analysis]
        R2 --> R3[Compliance Mapping]
        R3 --> R4[Risk Assessment]
    end
    
    subgraph "FDA Compliance"
        F1[GMP Requirements]
        F2[Clinical Guidelines]
        F3[Manufacturing Standards]
        F4[Distribution Controls]
        F1 --> F2 --> F3 --> F4
    end
    
    subgraph "EMA Compliance"
        E1[European Guidelines]
        E2[Quality Standards]
        E3[Safety Monitoring]
        E4[Post-market Surveillance]
        E1 --> E2 --> E3 --> E4
    end
    
    subgraph "Other Regulatory Bodies"
        O1[ICH Guidelines]
        O2[Local Regulations]
        O3[Industry Standards]
        O4[Quality Certifications]
        O1 --> O2 --> O3 --> O4
    end
    
    R4 --> F1
    R4 --> E1
    R4 --> O1
    
    F4 --> Audit[Automated Compliance Audit]
    E4 --> Audit
    O4 --> Audit
    
    Audit --> Report[Compliance Report]
    Report --> Action{Action Required?}
    Action -->|Yes| Remediation[Remediation Plan]
    Action -->|No| Monitor[Continuous Monitoring]
    
    Remediation --> Implementation[Implementation]
    Implementation --> Verification[Verification]
    Verification --> Monitor
    Monitor --> R1
```

## Sequence Diagrams

### Complex Multi-Stage Query Processing

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant UI as Streamlit UI
    participant Cache as Redis Cache
    participant Orch as Orchestrator
    participant Queue as Message Queue
    participant Plan as Plan Agent
    participant Source as Source Agent
    participant Make as Make Agent
    participant Deliver as Deliver Agent
    participant Return as Return Agent
    participant AI as Azure AI
    participant DB as Database
    participant Monitor as Monitoring
    
    User->>UI: Complex supply chain optimization query
    UI->>Cache: Check for cached results
    Cache-->>UI: Cache miss
    
    UI->>Orch: Submit query for processing
    Orch->>Monitor: Log query initiation
    Orch->>Queue: Enqueue agent tasks
    
    par Parallel Agent Processing
        Queue->>Plan: Process demand planning task
        Queue->>Source: Process sourcing task
        Queue->>Make: Process manufacturing task
        Queue->>Deliver: Process distribution task
        Queue->>Return: Process returns task
    end
    
    Plan->>AI: Request demand forecasting
    AI-->>Plan: Forecast results
    Plan->>DB: Store planning data
    Plan-->>Queue: Planning complete
    
    Source->>AI: Request supplier analysis
    AI-->>Source: Supplier recommendations
    Source->>DB: Store sourcing data
    Source-->>Queue: Sourcing complete
    
    Make->>AI: Request production optimization
    AI-->>Make: Manufacturing insights
    Make->>DB: Store production data
    Make-->>Queue: Manufacturing complete
    
    Deliver->>AI: Request logistics optimization
    AI-->>Deliver: Distribution strategy
    Deliver->>DB: Store delivery data
    Deliver-->>Queue: Delivery complete
    
    Return->>AI: Request returns analysis
    AI-->>Return: Return recommendations
    Return->>DB: Store return data
    Return-->>Queue: Returns complete
    
    Queue-->>Orch: All agents complete
    Orch->>DB: Retrieve all agent data
    DB-->>Orch: Consolidated data
    
    Orch->>AI: Synthesize agent outputs
    AI-->>Orch: Integrated analysis
    
    Orch->>Cache: Store results
    Orch->>Monitor: Log completion metrics
    Orch-->>UI: Comprehensive response
    UI-->>User: Display integrated analysis
```

### Real-Time Supply Chain Monitoring

```mermaid
sequenceDiagram
    participant Monitor as Monitoring System
    participant Alert as Alert Manager
    participant Agents as SCOR Agents
    participant External as External Systems
    participant User as User Interface
    participant Actions as Automated Actions
    
    loop Continuous Monitoring
        Monitor->>External: Poll system health
        External-->>Monitor: Health status
        
        Monitor->>Agents: Check agent performance
        Agents-->>Monitor: Performance metrics
        
        alt Critical Issue Detected
            Monitor->>Alert: Trigger critical alert
            Alert->>User: Send immediate notification
            Alert->>Actions: Initiate automated response
            Actions->>Agents: Execute contingency plans
            Agents->>External: Implement changes
            
        else Warning Level Issue
            Monitor->>Alert: Log warning
            Alert->>User: Dashboard notification
            
        else Normal Operation
            Monitor->>User: Update dashboard metrics
        end
        
        Note over Monitor,Actions: 30-second monitoring cycle
    end
```

### Supply Chain Disruption Response

```mermaid
sequenceDiagram
    participant Event as Disruption Event
    participant Monitor as Monitoring
    participant Risk as Risk Engine
    participant Plan as Plan Agent
    participant Source as Source Agent
    participant Orch as Orchestrator
    participant Notify as Notification
    participant User as Stakeholders
    
    Event->>Monitor: Supply disruption detected
    Monitor->>Risk: Assess impact severity
    Risk->>Risk: Calculate risk score
    
    alt High Risk (Score > 8)
        Risk->>Notify: Trigger emergency protocol
        Notify->>User: Emergency notification
        Risk->>Plan: Initiate crisis planning
        Plan->>Source: Find alternative suppliers
        Source->>Plan: Supplier alternatives
        Plan->>Orch: Emergency response plan
        Orch->>User: Crisis management dashboard
        
    else Medium Risk (Score 5-8)
        Risk->>Plan: Assess planning impact
        Plan->>Source: Evaluate sourcing options
        Source->>Plan: Sourcing recommendations
        Plan->>Orch: Mitigation strategies
        Orch->>User: Advisory recommendations
        
    else Low Risk (Score < 5)
        Risk->>Monitor: Continue monitoring
        Monitor->>User: Status update
    end
    
    loop Recovery Monitoring
        Monitor->>Risk: Check recovery status
        Risk->>Orch: Update response plans
        Orch->>User: Progress updates
    end
```

## Data Flow Diagrams

### Healthcare Data Pipeline

```mermaid
flowchart TD
    subgraph "Data Sources"
        ERP[(ERP Systems)]
        WMS[(WMS Systems)]
        Regulatory[(Regulatory APIs)]
        Market[(Market Data)]
        IoT[(IoT Sensors)]
        Clinical[(Clinical Systems)]
    end
    
    subgraph "Data Ingestion"
        Collectors[Data Collectors]
        Validation[Data Validation]
        Enrichment[Data Enrichment]
        Transformation[ETL Pipeline]
    end
    
    subgraph "Data Storage"
        RawData[(Raw Data Lake)]
        ProcessedData[(Processed Data)]
        Metadata[(Metadata Store)]
        Cache[(Performance Cache)]
    end
    
    subgraph "Data Processing"
        AI[AI Processing]
        Analytics[Analytics Engine]
        ML[ML Pipeline]
        Insights[Insight Generation]
    end
    
    subgraph "Data Consumption"
        Agents[SCOR Agents]
        Dashboards[Dashboards]
        APIs[External APIs]
        Reports[Automated Reports]
    end
    
    %% Connections
    ERP --> Collectors
    WMS --> Collectors
    Regulatory --> Collectors
    Market --> Collectors
    IoT --> Collectors
    Clinical --> Collectors
    
    Collectors --> Validation
    Validation --> Enrichment
    Enrichment --> Transformation
    
    Transformation --> RawData
    Transformation --> ProcessedData
    Transformation --> Metadata
    ProcessedData --> Cache
    
    ProcessedData --> AI
    ProcessedData --> Analytics
    ProcessedData --> ML
    AI --> Insights
    Analytics --> Insights
    ML --> Insights
    
    Insights --> Agents
    Insights --> Dashboards
    Insights --> APIs
    Insights --> Reports
    
    %% Feedback loops
    Agents --> ML
    Reports --> Validation
```

### Real-Time Analytics Flow

```mermaid
graph LR
    subgraph "Stream Processing"
        S1[Event Stream] --> S2[Real-time Processing]
        S2 --> S3[Pattern Detection]
        S3 --> S4[Anomaly Detection]
    end
    
    subgraph "Batch Processing"
        B1[Batch Data] --> B2[Historical Analysis]
        B2 --> B3[Trend Analysis]
        B3 --> B4[Predictive Models]
    end
    
    subgraph "Hybrid Analytics"
        H1[Lambda Architecture]
        H2[Feature Engineering]
        H3[Model Serving]
        H4[Decision Engine]
        
        S4 --> H1
        B4 --> H1
        H1 --> H2 --> H3 --> H4
    end
    
    subgraph "Action Layer"
        A1[Automated Actions]
        A2[Alert Generation]
        A3[Recommendation Engine]
        A4[Feedback Loop]
        
        H4 --> A1
        H4 --> A2
        H4 --> A3
        A3 --> A4
        A4 --> S1
    end
```

## Deployment Diagrams

### Multi-Region Deployment Architecture

```mermaid
graph TB
    subgraph "Global Load Balancer"
        GLB[Azure Front Door]
    end
    
    subgraph "Region 1: East US"
        subgraph "AKS Cluster East"
            E1[Orchestrator Pods]
            E2[Agent Pods]
            E3[API Gateway]
        end
        subgraph "Data Services East"
            ED1[(Primary Database)]
            ED2[(Data Lake)]
            ED3[(Redis Cache)]
        end
        subgraph "AI Services East"
            EA1[Azure AI Foundry]
            EA2[Azure OpenAI]
        end
    end
    
    subgraph "Region 2: West Europe"
        subgraph "AKS Cluster West"
            W1[Orchestrator Pods]
            W2[Agent Pods]
            W3[API Gateway]
        end
        subgraph "Data Services West"
            WD1[(Replica Database)]
            WD2[(Data Lake)]
            WD3[(Redis Cache)]
        end
        subgraph "AI Services West"
            WA1[Azure AI Foundry]
            WA2[Azure OpenAI]
        end
    end
    
    subgraph "Region 3: Asia Pacific"
        subgraph "AKS Cluster APAC"
            A1[Orchestrator Pods]
            A2[Agent Pods]
            A3[API Gateway]
        end
        subgraph "Data Services APAC"
            AD1[(Replica Database)]
            AD2[(Data Lake)]
            AD3[(Redis Cache)]
        end
        subgraph "AI Services APAC"
            AA1[Azure AI Foundry]
            AA2[Azure OpenAI]
        end
    end
    
    subgraph "Global Services"
        Monitor[Application Insights]
        KeyVault[Azure Key Vault]
        ServiceBus[Azure Service Bus]
    end
    
    %% Connections
    GLB --> E3
    GLB --> W3
    GLB --> A3
    
    E1 --> ED1
    E1 --> ED2
    E1 --> ED3
    E2 --> EA1
    E2 --> EA2
    
    W1 --> WD1
    W1 --> WD2
    W1 --> WD3
    W2 --> WA1
    W2 --> WA2
    
    A1 --> AD1
    A1 --> AD2
    A1 --> AD3
    A2 --> AA1
    A2 --> AA2
    
    %% Data replication
    ED1 -.-> WD1
    ED1 -.-> AD1
    
    %% Global services connections
    E1 --> Monitor
    W1 --> Monitor
    A1 --> Monitor
    
    E1 --> KeyVault
    W1 --> KeyVault
    A1 --> KeyVault
    
    E1 --> ServiceBus
    W1 --> ServiceBus
    A1 --> ServiceBus
    
    %% Styling
    classDef primaryRegion fill:#e8f5e8
    classDef replicaRegion fill:#fff3e0
    classDef globalServices fill:#e1f5fe
    
    class E1,E2,E3,ED1,ED2,ED3,EA1,EA2 primaryRegion
    class W1,W2,W3,WD1,WD2,WD3,WA1,WA2,A1,A2,A3,AD1,AD2,AD3,AA1,AA2 replicaRegion
    class GLB,Monitor,KeyVault,ServiceBus globalServices
```

### Kubernetes Deployment Details

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            Ingress[NGINX Ingress Controller]
            Cert[Cert Manager]
        end
        
        subgraph "Application Namespace"
            subgraph "Orchestrator"
                OrcPods[Orchestrator Pods<br/>Replicas: 3]
                OrcService[Orchestrator Service]
                OrcHPA[HPA: 3-10 replicas]
            end
            
            subgraph "SCOR Agents"
                PlanPods[Plan Agent Pods<br/>Replicas: 2]
                SourcePods[Source Agent Pods<br/>Replicas: 2]
                MakePods[Make Agent Pods<br/>Replicas: 2]
                DeliverPods[Deliver Agent Pods<br/>Replicas: 2]
                ReturnPods[Return Agent Pods<br/>Replicas: 2]
                
                AgentService[Agent Services]
                AgentHPA[HPA: 2-5 replicas each]
            end
            
            subgraph "Supporting Services"
                Redis[Redis Cluster]
                MessageQueue[Message Queue]
                ConfigMaps[Config Maps]
                Secrets[Kubernetes Secrets]
            end
        end
        
        subgraph "Monitoring Namespace"
            Prometheus[Prometheus]
            Grafana[Grafana]
            AlertManager[Alert Manager]
            Jaeger[Jaeger Tracing]
        end
        
        subgraph "System Namespace"
            CoreDNS[CoreDNS]
            Metrics[Metrics Server]
            CSI[CSI Drivers]
        end
    end
    
    subgraph "External Dependencies"
        AzureAI[Azure AI Services]
        Database[(Azure SQL)]
        Storage[(Azure Storage)]
        KeyVault[Azure Key Vault]
    end
    
    %% Connections
    Ingress --> OrcService
    OrcService --> OrcPods
    OrcPods --> AgentService
    AgentService --> PlanPods
    AgentService --> SourcePods
    AgentService --> MakePods
    AgentService --> DeliverPods
    AgentService --> ReturnPods
    
    OrcPods --> Redis
    OrcPods --> MessageQueue
    OrcPods --> ConfigMaps
    OrcPods --> Secrets
    
    OrcHPA --> OrcPods
    AgentHPA --> PlanPods
    AgentHPA --> SourcePods
    AgentHPA --> MakePods
    AgentHPA --> DeliverPods
    AgentHPA --> ReturnPods
    
    OrcPods --> AzureAI
    OrcPods --> Database
    OrcPods --> Storage
    Secrets --> KeyVault
    
    Prometheus --> OrcPods
    Prometheus --> PlanPods
    Prometheus --> SourcePods
    Prometheus --> MakePods
    Prometheus --> DeliverPods
    Prometheus --> ReturnPods
```

## Integration Diagrams

### Enterprise System Integration

```mermaid
graph TB
    subgraph "Healthcare Supply Chain Orchestrator"
        Core[Core System]
        API[Integration APIs]
        Adapters[System Adapters]
    end
    
    subgraph "Enterprise Resource Planning"
        ERP1[SAP ERP]
        ERP2[Oracle ERP]
        ERP3[Microsoft Dynamics]
    end
    
    subgraph "Manufacturing Systems"
        MES[Manufacturing Execution Systems]
        QMS[Quality Management Systems]
        LIMS[Laboratory Information Systems]
        DCS[Distributed Control Systems]
    end
    
    subgraph "Supply Chain Systems"
        WMS[Warehouse Management Systems]
        TMS[Transportation Management]
        SRM[Supplier Relationship Management]
        PLM[Product Lifecycle Management]
    end
    
    subgraph "Regulatory Systems"
        FDA[FDA FURLS]
        EMA[EMA Systems]
        ICH[ICH Guidelines]
        Local[Local Regulatory Bodies]
    end
    
    subgraph "External Services"
        Weather[Weather APIs]
        Traffic[Traffic Data]
        Economic[Economic Indicators]
        News[News & Events]
    end
    
    subgraph "Clinical Systems"
        CTMS[Clinical Trial Management]
        EDC[Electronic Data Capture]
        IWRS[Interactive Web Response]
        Safety[Pharmacovigilance]
    end
    
    %% Integration connections
    Core --> API
    API --> Adapters
    
    Adapters <--> ERP1
    Adapters <--> ERP2
    Adapters <--> ERP3
    
    Adapters <--> MES
    Adapters <--> QMS
    Adapters <--> LIMS
    Adapters <--> DCS
    
    Adapters <--> WMS
    Adapters <--> TMS
    Adapters <--> SRM
    Adapters <--> PLM
    
    Adapters <--> FDA
    Adapters <--> EMA
    Adapters <--> ICH
    Adapters <--> Local
    
    Adapters <--> Weather
    Adapters <--> Traffic
    Adapters <--> Economic
    Adapters <--> News
    
    Adapters <--> CTMS
    Adapters <--> EDC
    Adapters <--> IWRS
    Adapters <--> Safety
    
    %% Styling
    classDef coreSystem fill:#4caf50
    classDef enterpriseSystem fill:#2196f3
    classDef manufacturingSystem fill:#ff9800
    classDef supplySystem fill:#9c27b0
    classDef regulatorySystem fill:#f44336
    classDef externalSystem fill:#607d8b
    classDef clinicalSystem fill:#e91e63
    
    class Core,API,Adapters coreSystem
    class ERP1,ERP2,ERP3 enterpriseSystem
    class MES,QMS,LIMS,DCS manufacturingSystem
    class WMS,TMS,SRM,PLM supplySystem
    class FDA,EMA,ICH,Local regulatorySystem
    class Weather,Traffic,Economic,News externalSystem
    class CTMS,EDC,IWRS,Safety clinicalSystem
```

### API Integration Architecture

```mermaid
sequenceDiagram
    participant Client as External Client
    participant Gateway as API Gateway
    participant Auth as Authentication
    participant Rate as Rate Limiter
    participant Cache as Response Cache
    participant Orch as Orchestrator
    participant Agents as SCOR Agents
    participant Monitor as Monitoring
    
    Client->>Gateway: API Request
    Gateway->>Auth: Validate credentials
    Auth-->>Gateway: Authentication result
    
    alt Authenticated
        Gateway->>Rate: Check rate limits
        Rate-->>Gateway: Rate limit OK
        
        Gateway->>Cache: Check cache
        Cache-->>Gateway: Cache miss
        
        Gateway->>Orch: Forward request
        Orch->>Agents: Process with agents
        Agents-->>Orch: Agent responses
        Orch-->>Gateway: Orchestrated response
        
        Gateway->>Cache: Store response
        Gateway->>Monitor: Log metrics
        Gateway-->>Client: API Response
        
    else Authentication Failed
        Gateway-->>Client: 401 Unauthorized
        
    else Rate Limited
        Gateway-->>Client: 429 Too Many Requests
    end
```

---

*These comprehensive mermaid diagrams provide visual representations of the Healthcare Supply Chain Orchestrator's architecture, processes, and integrations, supporting both technical understanding and business communication.*