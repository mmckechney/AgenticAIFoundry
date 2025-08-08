# Azure Function Agent Integration - Mermaid Architecture Diagrams

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Azure Function Integration Flow](#azure-function-integration-flow)
3. [Connected Agent Orchestration](#connected-agent-orchestration)
4. [Queue-Based Messaging Flow](#queue-based-messaging-flow)
5. [Agent Lifecycle Management](#agent-lifecycle-management)
6. [Error Handling Flow](#error-handling-flow)
7. [Component Interaction Diagram](#component-interaction-diagram)

## System Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        A[Query Processing] --> B[Response Formatting]
        B --> C[Error Handling]
    end
    
    subgraph "Agent Orchestration Layer"
        D[Agent Management] --> E[Connected Agent]
        E --> F[Thread Management]
    end
    
    subgraph "Azure Function Integration Layer"
        G[Function Tool] --> H[Input Queue]
        H --> I[Output Queue]
    end
    
    subgraph "Azure Infrastructure Layer"
        J[Azure AI Foundry] --> K[Azure Functions]
        K --> L[Azure Storage]
    end
    
    A --> D
    D --> G
    G --> J
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style G fill:#e8f5e8
    style J fill:#fff3e0
```

## Azure Function Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant FunctionTool
    participant InputQueue
    participant AzureFunction
    participant OutputQueue
    
    User->>Agent: Send Query
    Agent->>FunctionTool: Process with Tool
    FunctionTool->>InputQueue: Queue Message
    InputQueue->>AzureFunction: Trigger Function
    AzureFunction->>OutputQueue: Send Response
    OutputQueue->>FunctionTool: Retrieve Response
    FunctionTool->>Agent: Return Result
    Agent->>User: Send Response
    
    Note over InputQueue,OutputQueue: Asynchronous Processing
    Note over Agent,FunctionTool: Tool Integration
```

## Connected Agent Orchestration

```mermaid
graph LR
    subgraph "Main Orchestrator Agent"
        A[Receive Query] --> B[Route to Connected Agent]
    end
    
    subgraph "Connected Function Agent"
        C[Process Function Call] --> D[Execute Azure Function]
        D --> E[Return Function Result]
    end
    
    subgraph "Azure Function"
        F[Input Processing] --> G[Business Logic]
        G --> H[Output Generation]
    end
    
    B --> C
    E --> I[Format Response]
    I --> J[Return to User]
    
    D -.-> F
    H -.-> E
    
    style A fill:#e3f2fd
    style C fill:#f1f8e9
    style F fill:#fff8e1
```

## Queue-Based Messaging Flow

```mermaid
flowchart TD
    A[User Query] --> B[Agent Processing]
    B --> C{Function Call Required?}
    
    C -->|Yes| D[Prepare Function Parameters]
    D --> E[Send to Input Queue]
    E --> F[Azure Function Execution]
    F --> G[Result to Output Queue]
    G --> H[Agent Retrieves Result]
    H --> I[Process Response]
    
    C -->|No| J[Direct Agent Response]
    J --> I
    
    I --> K[Format Final Response]
    K --> L[Return to User]
    
    subgraph "Queue Infrastructure"
        E
        G
    end
    
    style E fill:#ffebee
    style G fill:#e8f5e8
    style F fill:#fff3e0
```

## Agent Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Creating
    Creating --> Configuring: Agent Created
    Configuring --> Ready: Tools Attached
    Ready --> Processing: Message Received
    Processing --> Waiting: Function Called
    Waiting --> Processing: Response Received
    Processing --> Ready: Response Sent
    Ready --> Cleanup: Session End
    Cleanup --> [*]: Resources Deleted
    
    Processing --> Error: Failure Detected
    Error --> Cleanup: Error Handled
    Error --> Processing: Retry Attempt
    
    note right of Creating
        - AIProjectClient initialization
        - Agent creation with model
    end note
    
    note right of Configuring
        - Tool definitions attachment
        - Instructions setup
    end note
    
    note right of Cleanup
        - Delete agent
        - Delete thread
        - Release resources
    end note
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Start Process] --> B{Environment Valid?}
    B -->|No| C[Exit with Error]
    B -->|Yes| D[Create Agent]
    
    D --> E{Agent Created?}
    E -->|No| F[Log Error & Exit]
    E -->|Yes| G[Create Thread]
    
    G --> H{Thread Created?}
    H -->|No| I[Delete Agent & Exit]
    H -->|Yes| J[Process Message]
    
    J --> K{Run Successful?}
    K -->|No| L[Log Run Error]
    K -->|Yes| M[Extract Response]
    
    L --> N[Cleanup Resources]
    M --> N
    N --> O[End Process]
    
    style C fill:#ffcdd2
    style F fill:#ffcdd2
    style I fill:#ffcdd2
    style L fill:#fff3e0
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "External Environment"
        ENV[Environment Variables]
        USER[User Input]
    end
    
    subgraph "Core Components"
        VALIDATE[Environment Validator]
        CLIENT[AIProjectClient]
        AGENT[AI Agent]
        THREAD[Communication Thread]
    end
    
    subgraph "Function Integration"
        TOOL[AzureFunctionTool]
        INQUEUE[Input Queue]
        OUTQUEUE[Output Queue]
        FUNC[Azure Function]
    end
    
    subgraph "Message Processing"
        EXTRACT[Message Extractor]
        PROCESS[Response Processor]
        FORMAT[Response Formatter]
    end
    
    subgraph "Resource Management"
        CLEANUP[Resource Cleanup]
        DELETE[Agent Deletion]
    end
    
    ENV --> VALIDATE
    USER --> AGENT
    VALIDATE --> CLIENT
    CLIENT --> AGENT
    AGENT --> THREAD
    AGENT --> TOOL
    TOOL --> INQUEUE
    INQUEUE --> FUNC
    FUNC --> OUTQUEUE
    OUTQUEUE --> TOOL
    TOOL --> EXTRACT
    EXTRACT --> PROCESS
    PROCESS --> FORMAT
    FORMAT --> USER
    AGENT --> CLEANUP
    CLEANUP --> DELETE
    
    style ENV fill:#e8eaf6
    style AGENT fill:#e3f2fd
    style TOOL fill:#e8f5e8
    style FUNC fill:#fff8e1
    style CLEANUP fill:#fce4ec
```

## Function Tool Configuration Flow

```mermaid
flowchart LR
    A[Define Parameters Schema] --> B[Configure Input Queue]
    B --> C[Configure Output Queue]
    C --> D[Create Function Tool]
    D --> E[Attach to Agent]
    
    subgraph "Tool Configuration"
        F[Tool Name: 'foo']
        G[Description: Function purpose]
        H[Parameters: JSON Schema]
    end
    
    subgraph "Queue Configuration"
        I[Input Queue Name]
        J[Output Queue Name]
        K[Storage Endpoint]
    end
    
    A --> F
    A --> G
    A --> H
    B --> I
    C --> J
    B --> K
    C --> K
    
    style F fill:#e1f5fe
    style I fill:#e8f5e8
    style J fill:#e8f5e8
```

## Data Flow Architecture

```mermaid
flowchart TB
    subgraph "Input Processing"
        A[User Query] --> B[Query Validation]
        B --> C[Parameter Extraction]
    end
    
    subgraph "Agent Processing"
        D[Agent Instruction Processing] --> E[Tool Selection]
        E --> F[Function Parameter Preparation]
    end
    
    subgraph "Function Execution"
        G[Queue Message Creation] --> H[Function Invocation]
        H --> I[Function Processing]
        I --> J[Result Queue Population]
    end
    
    subgraph "Response Processing"
        K[Queue Result Retrieval] --> L[Response Parsing]
        L --> M[Text Extraction]
        M --> N[Response Formatting]
    end
    
    C --> D
    F --> G
    J --> K
    N --> O[Final Response to User]
    
    style A fill:#e8eaf6
    style H fill:#fff8e1
    style O fill:#e8f5e8
```

---

*These Mermaid diagrams provide visual representations of the Azure Function Agent Integration architecture and workflows. They can be rendered in any Mermaid-compatible viewer or documentation platform.*