# AgenticAI Access Management - Mermaid Architecture Diagrams

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [MCP Server Access Management](#mcp-server-access-management)
3. [Agent Access Management](#agent-access-management)
4. [User Access Flow Diagrams](#user-access-flow-diagrams)
5. [Administrative Workflows](#administrative-workflows)
6. [Authentication and Security](#authentication-and-security)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Integration Architecture](#integration-architecture)

## System Architecture Overview

### High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        WEB[Web Browser]
        STUI[Streamlit UI]
    end
    
    subgraph "Application Layer"
        MCP_APP[MCP Server Dashboard<br/>stmcplist.py]
        AGENT_APP[Agent Dashboard<br/>stagentlist.py]
        SHARED[Shared Components]
    end
    
    subgraph "Data Management Layer"
        MCP_DATA[mcplist.json<br/>MCP Servers & Users]
        AGENT_DATA[agentlist.json<br/>Agents & Users]
        CACHE[Streamlit Cache]
        SESSION[Session State]
    end
    
    subgraph "External Services"
        AZURE_AI[Azure AI Services]
        MCP_SERVERS[MCP Servers]
        AI_AGENTS[AI Agents]
        APP_INSIGHTS[Application Insights]
        OAUTH[OAuth2 Providers]
    end
    
    WEB --> STUI
    STUI --> MCP_APP
    STUI --> AGENT_APP
    MCP_APP --> SHARED
    AGENT_APP --> SHARED
    
    MCP_APP --> MCP_DATA
    AGENT_APP --> AGENT_DATA
    SHARED --> CACHE
    SHARED --> SESSION
    
    SHARED --> AZURE_AI
    MCP_APP --> MCP_SERVERS
    AGENT_APP --> AI_AGENTS
    SHARED --> APP_INSIGHTS
    AGENT_APP --> OAUTH
    
    style MCP_APP fill:#e1f5fe
    style AGENT_APP fill:#f3e5f5
    style AZURE_AI fill:#fff3e0
    style APP_INSIGHTS fill:#e8f5e8
```

### Component Interaction Model

```mermaid
graph LR
    subgraph "Frontend Components"
        UD[User Dashboard]
        AD[Admin Dashboard]
        FI[Filter Interface]
        FM[Form Manager]
    end
    
    subgraph "Core Services"
        AM[Access Manager]
        DM[Data Manager]
        VM[Validation Manager]
        CM[Cache Manager]
    end
    
    subgraph "External Integrations"
        AI[Azure AI]
        Tel[Telemetry]
        Auth[Authentication]
    end
    
    UD --> AM
    AD --> AM
    FI --> AM
    FM --> VM
    
    AM --> DM
    VM --> DM
    DM --> CM
    
    AM --> AI
    DM --> Tel
    VM --> Auth
    
    style UD fill:#e3f2fd
    style AD fill:#fce4ec
    style AM fill:#e8f5e8
    style DM fill:#fff3e0
```

## MCP Server Access Management

### MCP Server Management Architecture

```mermaid
graph TB
    subgraph "MCP Dashboard Interface"
        MCP_UI[MCP Server Dashboard UI]
        USER_TAB[User Access Tab]
        ADMIN_TAB[Admin Management Tab]
    end
    
    subgraph "MCP Access Control"
        UAC[User Access Controller]
        SAC[Server Access Controller]
        PM[Permission Manager]
    end
    
    subgraph "MCP Data Layer"
        MCP_JSON[mcplist.json]
        MCP_CACHE[MCP Data Cache]
        MCP_SESSION[MCP Session State]
    end
    
    subgraph "MCP External Services"
        MCP_SRV[MCP Servers]
        AZURE[Azure AI Project]
        INSIGHTS[Application Insights]
    end
    
    MCP_UI --> USER_TAB
    MCP_UI --> ADMIN_TAB
    
    USER_TAB --> UAC
    ADMIN_TAB --> SAC
    SAC --> PM
    UAC --> PM
    
    PM --> MCP_JSON
    PM --> MCP_CACHE
    PM --> MCP_SESSION
    
    SAC --> MCP_SRV
    PM --> AZURE
    PM --> INSIGHTS
    
    style MCP_UI fill:#e1f5fe
    style UAC fill:#e8f5e8
    style SAC fill:#fff3e0
    style MCP_JSON fill:#fce4ec
```

### MCP Server Access Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as MCP Dashboard UI
    participant AC as Access Controller
    participant DM as Data Manager
    participant MCP as MCP Server
    
    U->>UI: Access MCP Dashboard
    UI->>AC: Request user servers
    AC->>DM: Load user permissions
    DM-->>AC: Return accessible servers
    AC->>DM: Load server details
    DM-->>AC: Return server metadata
    AC-->>UI: Filtered server list
    UI-->>U: Display accessible servers
    
    U->>UI: Apply filters
    UI->>AC: Process filter criteria
    AC-->>UI: Filtered results
    UI-->>U: Updated server list
    
    U->>UI: Select server
    UI->>AC: Request server connection
    AC->>MCP: Establish connection
    MCP-->>AC: Connection response
    AC-->>UI: Server access granted
    UI-->>U: Server interface available
```

## Agent Access Management

### Agent Management Architecture

```mermaid
graph TB
    subgraph "Agent Dashboard Interface"
        AGENT_UI[Agent Dashboard UI]
        USER_DASH[User Dashboard]
        ADMIN_DASH[Admin Dashboard]
        FILTER_UI[Filter Interface]
    end
    
    subgraph "Agent Management Services"
        AAM[Agent Access Manager]
        APM[Agent Parameter Manager]
        AUM[Agent User Manager]
        VAL[Validation Service]
    end
    
    subgraph "Authentication Services"
        API_KEY[API Key Auth]
        OAUTH2[OAuth2 Auth]
        BASIC[Basic Auth]
        JWT[JWT Auth]
    end
    
    subgraph "Agent Data Layer"
        AGENT_JSON[agentlist.json]
        AGENT_CACHE[Agent Data Cache]
        AGENT_SESSION[Agent Session State]
        PARAMS[Parameter Storage]
    end
    
    subgraph "External Agent Services"
        AI_AGENTS[AI Agents]
        AZURE_AI[Azure AI Services]
        EXT_AUTH[External Auth Providers]
        MONITORING[Monitoring Services]
    end
    
    AGENT_UI --> USER_DASH
    AGENT_UI --> ADMIN_DASH
    AGENT_UI --> FILTER_UI
    
    USER_DASH --> AAM
    ADMIN_DASH --> APM
    ADMIN_DASH --> AUM
    FILTER_UI --> AAM
    
    APM --> VAL
    AUM --> VAL
    AAM --> VAL
    
    AAM --> API_KEY
    AAM --> OAUTH2
    AAM --> BASIC
    AAM --> JWT
    
    VAL --> AGENT_JSON
    VAL --> AGENT_CACHE
    VAL --> AGENT_SESSION
    APM --> PARAMS
    
    API_KEY --> AI_AGENTS
    OAUTH2 --> EXT_AUTH
    BASIC --> AI_AGENTS
    JWT --> AI_AGENTS
    
    VAL --> AZURE_AI
    VAL --> MONITORING
    
    style AGENT_UI fill:#f3e5f5
    style AAM fill:#e8f5e8
    style VAL fill:#fff3e0
    style AGENT_JSON fill:#fce4ec
```

### Agent Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Agent Dashboard
    participant AM as Agent Manager
    participant Auth as Auth Service
    participant Agent as AI Agent
    participant Ext as External Service
    
    U->>UI: Request agent access
    UI->>AM: Validate user permissions
    AM-->>UI: Permission granted
    
    UI->>AM: Initialize agent session
    AM->>Auth: Get authentication method
    Auth-->>AM: Return auth config
    
    alt API Key Authentication
        AM->>Agent: Configure API key
        Agent->>Ext: API request with key
        Ext-->>Agent: Response
    else OAuth2 Authentication
        AM->>Auth: Request OAuth2 token
        Auth->>Ext: Token exchange
        Ext-->>Auth: Access token
        Auth-->>AM: Token provided
        AM->>Agent: Configure OAuth2
        Agent->>Ext: Request with token
        Ext-->>Agent: Response
    else Basic Authentication
        AM->>Agent: Configure basic auth
        Agent->>Ext: Request with credentials
        Ext-->>Agent: Response
    else JWT Authentication
        AM->>Agent: Configure JWT
        Agent->>Ext: Request with JWT
        Ext-->>Agent: Response
    end
    
    Agent-->>AM: Agent response
    AM-->>UI: Processed response
    UI-->>U: Display results
```

## User Access Flow Diagrams

### User Dashboard Access Workflow

```mermaid
flowchart TD
    START([User Accesses Dashboard])
    LOGIN{User Authenticated?}
    SELECT_TYPE{Select Dashboard Type}
    
    MCP_DASH[MCP Server Dashboard]
    AGENT_DASH[Agent Dashboard]
    
    LOAD_USER[Load User Profile]
    GET_PERMISSIONS[Get User Permissions]
    LOAD_RESOURCES[Load Accessible Resources]
    
    APPLY_FILTERS[Apply Filters]
    DISPLAY_LIST[Display Resource List]
    
    SELECT_RESOURCE{Select Resource}
    VALIDATE_ACCESS[Validate Access]
    CONNECT[Establish Connection]
    
    SUCCESS([Access Granted])
    ERROR([Access Denied])
    
    START --> LOGIN
    LOGIN -->|No| ERROR
    LOGIN -->|Yes| SELECT_TYPE
    
    SELECT_TYPE -->|MCP| MCP_DASH
    SELECT_TYPE -->|Agent| AGENT_DASH
    
    MCP_DASH --> LOAD_USER
    AGENT_DASH --> LOAD_USER
    
    LOAD_USER --> GET_PERMISSIONS
    GET_PERMISSIONS --> LOAD_RESOURCES
    LOAD_RESOURCES --> APPLY_FILTERS
    APPLY_FILTERS --> DISPLAY_LIST
    
    DISPLAY_LIST --> SELECT_RESOURCE
    SELECT_RESOURCE --> VALIDATE_ACCESS
    VALIDATE_ACCESS -->|Valid| CONNECT
    VALIDATE_ACCESS -->|Invalid| ERROR
    CONNECT --> SUCCESS
    
    style START fill:#e8f5e8
    style SUCCESS fill:#c8e6c9
    style ERROR fill:#ffcdd2
    style LOGIN fill:#fff3e0
```

### Admin Management Workflow

```mermaid
flowchart TD
    ADMIN_START([Admin Access])
    AUTH_CHECK{Admin Authorized?}
    
    SELECT_OPERATION{Select Operation}
    
    MANAGE_SERVERS[Manage MCP Servers]
    MANAGE_AGENTS[Manage Agents]
    MANAGE_USERS[Manage User Access]
    
    SELECT_RESOURCE[Select Resource to Edit]
    LOAD_CONFIG[Load Current Configuration]
    
    EDIT_METADATA[Edit Metadata]
    EDIT_AUTH[Edit Authentication]
    EDIT_PARAMS[Edit Parameters]
    EDIT_ACCESS[Edit User Access]
    
    VALIDATE_CHANGES[Validate Changes]
    SAVE_CHANGES[Save Changes]
    
    UPDATE_CACHE[Update Cache]
    NOTIFY_SUCCESS[Notify Success]
    
    ERROR_HANDLE[Handle Error]
    
    ADMIN_START --> AUTH_CHECK
    AUTH_CHECK -->|No| ERROR_HANDLE
    AUTH_CHECK -->|Yes| SELECT_OPERATION
    
    SELECT_OPERATION --> MANAGE_SERVERS
    SELECT_OPERATION --> MANAGE_AGENTS
    SELECT_OPERATION --> MANAGE_USERS
    
    MANAGE_SERVERS --> SELECT_RESOURCE
    MANAGE_AGENTS --> SELECT_RESOURCE
    MANAGE_USERS --> SELECT_RESOURCE
    
    SELECT_RESOURCE --> LOAD_CONFIG
    LOAD_CONFIG --> EDIT_METADATA
    LOAD_CONFIG --> EDIT_AUTH
    LOAD_CONFIG --> EDIT_PARAMS
    LOAD_CONFIG --> EDIT_ACCESS
    
    EDIT_METADATA --> VALIDATE_CHANGES
    EDIT_AUTH --> VALIDATE_CHANGES
    EDIT_PARAMS --> VALIDATE_CHANGES
    EDIT_ACCESS --> VALIDATE_CHANGES
    
    VALIDATE_CHANGES -->|Valid| SAVE_CHANGES
    VALIDATE_CHANGES -->|Invalid| ERROR_HANDLE
    
    SAVE_CHANGES --> UPDATE_CACHE
    UPDATE_CACHE --> NOTIFY_SUCCESS
    
    style ADMIN_START fill:#f3e5f5
    style VALIDATE_CHANGES fill:#fff3e0
    style NOTIFY_SUCCESS fill:#c8e6c9
    style ERROR_HANDLE fill:#ffcdd2
```

## Administrative Workflows

### Server/Agent Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : Submit for Review
    Review --> Certified : Approve
    Review --> Draft : Reject
    Certified --> Active : Deploy
    Active --> Maintenance : Schedule Maintenance
    Maintenance --> Active : Complete Maintenance
    Active --> Deprecated : Mark Deprecated
    Deprecated --> Retired : Retirement Date
    Retired --> [*]
    
    Active --> Expired : Expiration Date
    Expired --> Renewed : Renew
    Expired --> Retired : Not Renewed
    Renewed --> Active
    
    note right of Certified
        Certified resources can be
        accessed by authorized users
    end note
    
    note right of Expired
        Expired resources are
        automatically blocked
    end note
```

### User Access Management State

```mermaid
stateDiagram-v2
    [*] --> Requested
    Requested --> UnderReview : Admin Review
    UnderReview --> Approved : Grant Access
    UnderReview --> Denied : Deny Access
    Approved --> Active : Access Granted
    Active --> Suspended : Violation/Security
    Suspended --> Active : Restore Access
    Active --> Revoked : Remove Access
    Denied --> [*]
    Revoked --> [*]
    Suspended --> Revoked : Permanent Removal
    
    note right of Active
        User can access assigned
        servers/agents
    end note
    
    note right of Suspended
        Temporary access suspension
        pending investigation
    end note
```

## Authentication and Security

### Multi-Factor Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Dashboard UI
    participant Auth as Auth Service
    participant Azure as Azure AD
    participant MFA as MFA Provider
    participant Resource as Server/Agent
    
    U->>UI: Request access
    UI->>Auth: Initiate authentication
    Auth->>Azure: Validate credentials
    Azure-->>Auth: Primary auth success
    
    Auth->>MFA: Request MFA challenge
    MFA->>U: Send MFA challenge
    U->>MFA: Provide MFA response
    MFA-->>Auth: MFA verified
    
    Auth->>Auth: Generate session token
    Auth-->>UI: Authentication complete
    UI->>Resource: Request with token
    Resource->>Auth: Validate token
    Auth-->>Resource: Token valid
    Resource-->>UI: Access granted
    UI-->>U: Resource available
```

### Security Access Control Matrix

```mermaid
graph TB
    subgraph "Security Layers"
        L1[Network Security]
        L2[Application Security]
        L3[Data Security]
        L4[Resource Security]
    end
    
    subgraph "Authentication Methods"
        PWD[Password]
        MFA[Multi-Factor Auth]
        SSO[Single Sign-On]
        API[API Key]
    end
    
    subgraph "Authorization Levels"
        USER[User Level]
        ADMIN[Admin Level]
        SUPER[Super Admin]
        SYS[System Level]
    end
    
    subgraph "Access Controls"
        RBAC[Role-Based Access]
        ABAC[Attribute-Based Access]
        MAC[Mandatory Access Control]
        DAC[Discretionary Access Control]
    end
    
    L1 --> PWD
    L1 --> MFA
    L2 --> SSO
    L2 --> API
    
    PWD --> USER
    MFA --> ADMIN
    SSO --> SUPER
    API --> SYS
    
    USER --> RBAC
    ADMIN --> ABAC
    SUPER --> MAC
    SYS --> DAC
    
    style L1 fill:#ffebee
    style L2 fill:#f3e5f5
    style L3 fill:#e8eaf6
    style L4 fill:#e0f2f1
```

## Data Flow Diagrams

### Configuration Data Flow

```mermaid
flowchart LR
    subgraph "Data Sources"
        MCP_JSON[(mcplist.json)]
        AGENT_JSON[(agentlist.json)]
        ENV[Environment Variables]
    end
    
    subgraph "Data Processing"
        LOADER[Data Loader]
        VALIDATOR[Data Validator]
        TRANSFORMER[Data Transformer]
    end
    
    subgraph "Runtime Storage"
        CACHE[Application Cache]
        SESSION[Session State]
        MEMORY[In-Memory Objects]
    end
    
    subgraph "UI Components"
        DASHBOARD[Dashboard Views]
        FORMS[Admin Forms]
        FILTERS[Filter Controls]
    end
    
    MCP_JSON --> LOADER
    AGENT_JSON --> LOADER
    ENV --> LOADER
    
    LOADER --> VALIDATOR
    VALIDATOR --> TRANSFORMER
    TRANSFORMER --> CACHE
    CACHE --> SESSION
    SESSION --> MEMORY
    
    MEMORY --> DASHBOARD
    MEMORY --> FORMS
    MEMORY --> FILTERS
    
    FORMS --> VALIDATOR
    VALIDATOR --> TRANSFORMER
    TRANSFORMER --> MCP_JSON
    TRANSFORMER --> AGENT_JSON
    
    style MCP_JSON fill:#e1f5fe
    style AGENT_JSON fill:#f3e5f5
    style CACHE fill:#fff3e0
    style DASHBOARD fill:#e8f5e8
```

### User Access Decision Flow

```mermaid
graph TD
    REQUEST[Access Request]
    USER_AUTH{User Authenticated?}
    LOAD_PROFILE[Load User Profile]
    CHECK_PERMISSIONS[Check Permissions]
    RESOURCE_AVAILABLE{Resource Available?}
    RESOURCE_ACTIVE{Resource Active?}
    ACCESS_GRANTED[Access Granted]
    ACCESS_DENIED[Access Denied]
    
    REQUEST --> USER_AUTH
    USER_AUTH -->|No| ACCESS_DENIED
    USER_AUTH -->|Yes| LOAD_PROFILE
    LOAD_PROFILE --> CHECK_PERMISSIONS
    CHECK_PERMISSIONS -->|No Permission| ACCESS_DENIED
    CHECK_PERMISSIONS -->|Has Permission| RESOURCE_AVAILABLE
    RESOURCE_AVAILABLE -->|No| ACCESS_DENIED
    RESOURCE_AVAILABLE -->|Yes| RESOURCE_ACTIVE
    RESOURCE_ACTIVE -->|Expired/Inactive| ACCESS_DENIED
    RESOURCE_ACTIVE -->|Active| ACCESS_GRANTED
    
    style ACCESS_GRANTED fill:#c8e6c9
    style ACCESS_DENIED fill:#ffcdd2
    style USER_AUTH fill:#fff3e0
    style CHECK_PERMISSIONS fill:#e8f5e8
```

## Integration Architecture

### Azure Services Integration

```mermaid
graph TB
    subgraph "AgenticAI Applications"
        MCP_APP[MCP Dashboard]
        AGENT_APP[Agent Dashboard]
        SHARED_COMP[Shared Components]
    end
    
    subgraph "Azure AI Services"
        AI_PROJECT[Azure AI Project]
        OPENAI[Azure OpenAI]
        COGNITIVE[Cognitive Services]
        SEARCH[Azure AI Search]
    end
    
    subgraph "Azure Infrastructure"
        APP_INSIGHTS[Application Insights]
        KEY_VAULT[Azure Key Vault]
        STORAGE[Azure Storage]
        IDENTITY[Azure AD/Identity]
    end
    
    subgraph "External Services"
        MCP_SERVERS[MCP Servers]
        AI_AGENTS[AI Agents]
        OAUTH_PROVIDERS[OAuth Providers]
    end
    
    MCP_APP --> AI_PROJECT
    AGENT_APP --> AI_PROJECT
    SHARED_COMP --> OPENAI
    
    AI_PROJECT --> COGNITIVE
    AI_PROJECT --> SEARCH
    OPENAI --> COGNITIVE
    
    SHARED_COMP --> APP_INSIGHTS
    SHARED_COMP --> KEY_VAULT
    SHARED_COMP --> STORAGE
    SHARED_COMP --> IDENTITY
    
    MCP_APP --> MCP_SERVERS
    AGENT_APP --> AI_AGENTS
    IDENTITY --> OAUTH_PROVIDERS
    
    style AI_PROJECT fill:#e3f2fd
    style OPENAI fill:#e8f5e8
    style APP_INSIGHTS fill:#fff3e0
    style IDENTITY fill:#f3e5f5
```

### External Service Integration

```mermaid
sequenceDiagram
    participant App as AgenticAI App
    participant Azure as Azure Services
    participant MCP as MCP Server
    participant Agent as AI Agent
    participant Auth as Auth Provider
    participant Monitor as Monitoring
    
    App->>Azure: Initialize connection
    Azure-->>App: Connection established
    
    App->>Auth: Authenticate user
    Auth-->>App: User authenticated
    
    App->>MCP: Request MCP service
    MCP->>Azure: Validate request
    Azure-->>MCP: Request validated
    MCP-->>App: MCP response
    
    App->>Agent: Request agent service
    Agent->>Auth: Validate agent access
    Auth-->>Agent: Access validated
    Agent-->>App: Agent response
    
    App->>Monitor: Send telemetry
    Monitor-->>App: Telemetry recorded
    
    Note over App,Monitor: All interactions are logged and monitored
```

### Data Synchronization Flow

```mermaid
graph LR
    subgraph "Configuration Sources"
        JSON[JSON Files]
        ENV[Environment]
        AZURE[Azure Config]
    end
    
    subgraph "Synchronization Layer"
        SYNC[Sync Manager]
        CONFLICT[Conflict Resolver]
        VALIDATOR[Config Validator]
    end
    
    subgraph "Runtime Configuration"
        CACHE[Active Cache]
        SESSION[Session Config]
        RUNTIME[Runtime State]
    end
    
    subgraph "Persistence Layer"
        LOCAL[Local Storage]
        REMOTE[Remote Storage]
        BACKUP[Backup Storage]
    end
    
    JSON --> SYNC
    ENV --> SYNC
    AZURE --> SYNC
    
    SYNC --> CONFLICT
    CONFLICT --> VALIDATOR
    VALIDATOR --> CACHE
    
    CACHE --> SESSION
    SESSION --> RUNTIME
    
    VALIDATOR --> LOCAL
    VALIDATOR --> REMOTE
    VALIDATOR --> BACKUP
    
    RUNTIME --> SYNC
    
    style SYNC fill:#e8f5e8
    style CACHE fill:#fff3e0
    style VALIDATOR fill:#f3e5f5
```

---

## Usage Notes

### Viewing These Diagrams

These Mermaid diagrams can be viewed in:

1. **GitHub**: Natively rendered in README and documentation files
2. **VS Code**: With Mermaid preview extensions
3. **Online Editors**: 
   - [Mermaid Live Editor](https://mermaid.live/)
   - [Draw.io](https://draw.io/) with Mermaid support
4. **Documentation Platforms**: 
   - GitBook, Notion, Confluence with Mermaid support

### Diagram Maintenance

- Keep diagrams synchronized with code changes
- Update architectural diagrams when adding new components
- Validate sequence diagrams against actual implementation
- Use consistent styling and naming conventions

### Integration with Development

- Include relevant diagrams in pull request reviews
- Reference diagrams in technical specifications
- Use diagrams for onboarding new team members
- Maintain diagram versioning alongside code releases