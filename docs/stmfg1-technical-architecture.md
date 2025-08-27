# AgenticAI Foundry - stmfg1.py Technical Architecture Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Technical Components](#technical-components)
4. [Agent Architecture](#agent-architecture)
5. [Data Flow Architecture](#data-flow-architecture)
6. [Integration Architecture](#integration-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Performance Architecture](#performance-architecture)
10. [Technical Requirements](#technical-requirements)
11. [Implementation Details](#implementation-details)

## Executive Summary

The Adhesive Manufacturing Orchestrator (stmfg1.py) is built on a sophisticated multi-agent architecture leveraging Azure AI Project services, Streamlit web framework, and advanced AI orchestration patterns. The system implements a three-phase manufacturing workflow with 16 specialized AI agents that collaborate to provide comprehensive manufacturing guidance from R&D through commercialization.

### Key Technical Features
- **Multi-Agent Orchestration**: 16 specialized AI agents across 3 manufacturing phases
- **Azure AI Integration**: Native Azure AI Project Client for agent management
- **Real-time Collaboration**: Connected agent tools enabling inter-agent communication
- **Streamlit Interface**: Modern, responsive web UI with tabbed navigation
- **Telemetry Integration**: Azure Application Insights for monitoring and analytics
- **Token Usage Tracking**: Comprehensive usage analytics and cost optimization

## System Architecture Overview

### High-Level Architecture

The system follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Streamlit Web Interface                      │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │ │
│  │  │ Phase 1 │  │ Phase 2 │  │      Phase 3            │  │ │
│  │  │   R&D   │  │Testing  │  │    Production           │  │ │
│  │  └─────────┘  └─────────┘  └─────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Agent Orchestration Engine                    │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │ │
│  │  │Phase 1  │  │Phase 2  │  │      Phase 3            │  │ │
│  │  │Agents   │  │Agents   │  │     Agents              │  │ │
│  │  │(5)      │  │(5)      │  │       (6)               │  │ │
│  │  └─────────┘  └─────────┘  └─────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │        Connected Agent Communication Layer              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Azure AI Project Services                  │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │ │
│  │  │Agent    │  │Thread   │  │    Message              │  │ │
│  │  │Manager  │  │Manager  │  │    Manager              │  │ │
│  │  └─────────┘  └─────────┘  └─────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Telemetry Services                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Azure Cloud Platform                    │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │ │
│  │  │AI       │  │App      │  │   Authentication        │  │ │
│  │  │Services │  │Insights │  │   Services              │  │ │
│  │  └─────────┘  └─────────┘  └─────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Model

The system implements a hub-and-spoke pattern where each phase orchestrates multiple specialized agents:

- **Phase Orchestrators**: Main agents that coordinate connected agents within each phase
- **Connected Agents**: Specialized domain agents that provide expert knowledge
- **Communication Layer**: Handles inter-agent messaging and data flow
- **State Management**: Streamlit session state for UI consistency

## Technical Components

### Core Dependencies

```python
# Core Azure AI Components
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ConnectedAgentTool, MessageRole

# Web Framework
import streamlit as st

# Monitoring & Telemetry
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Data Processing
import pandas as pd
import json
```

### System Configuration

```python
# Environment Configuration
endpoint = os.environ["PROJECT_ENDPOINT"]
model_endpoint = os.environ["MODEL_ENDPOINT"] 
model_api_key = os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

# Azure AI Project Client
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Telemetry Configuration
connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=connection_string)
```

## Agent Architecture

### Phase 1: Research and Development Agents

#### Agent Hierarchy and Specializations

```
Phase 1 Orchestrator (PresalesAgent)
├── Ideation Agent
│   ├── Role: Creative ideation and innovation catalyst
│   ├── Capabilities: Market analysis, trend identification, concept generation
│   └── Output: 3-5 innovative adhesive concepts with feasibility analysis
├── Raw Material Agent  
│   ├── Role: Materials science specialist
│   ├── Capabilities: Material selection, cost analysis, regulatory compliance
│   └── Output: Material shortlist with justifications and alternatives
├── Formulation Agent
│   ├── Role: Chemical engineering expert
│   ├── Capabilities: Recipe development, property prediction, iteration planning
│   └── Output: 2-3 formulation recipes with predicted properties
├── Initial Lab Test Agent
│   ├── Role: Quality assurance and analytical specialist  
│   ├── Capabilities: Test planning, result simulation, failure analysis
│   └── Output: Test plans, simulated results, and recommendations
└── Concept Validation Agent
    ├── Role: Collaborative integrator
    ├── Capabilities: Feedback synthesis, SWOT analysis, concept refinement
    └── Output: Validation analysis and refined concept specifications
```

#### Agent Implementation Pattern

```python
def create_agent_with_connected_tool(project_client, agent_config):
    """Standard pattern for creating agents with connected tool capabilities"""
    
    # Create the specialized agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=agent_config["name"],
        instructions=agent_config["instructions"]
    )
    
    # Create connected agent tool for inter-agent communication
    connected_agent = ConnectedAgentTool(
        id=agent.id, 
        name=agent_config["connected_name"], 
        description=agent_config["description"]
    )
    
    return agent, connected_agent
```

### Phase 2: Prototyping and Testing Agents

```
Phase 2 Orchestrator (PresalesAgent)
├── Prototype Creation Agent
│   ├── Specialization: Chemical engineering and process optimization
│   ├── Focus: Batch preparation, homogeneity, scalability considerations
├── Performance Testing Agent
│   ├── Specialization: Analytical and materials testing
│   ├── Focus: Standardized testing, quantitative analysis, performance metrics
├── Customer Field Trial Agent
│   ├── Specialization: Customer collaboration and real-world validation
│   ├── Focus: Trial planning, feedback collection, adjustment recommendations
├── Iteration and Refinement Agent
│   ├── Specialization: Problem-solving and optimization
│   ├── Focus: Issue analysis, formulation refinement, compliance verification
└── Quality Assurance Agent
    ├── Specialization: Quality control and consistency
    ├── Focus: QC planning, batch uniformity, production readiness
```

### Phase 3: Production Scaling Agents

```
Phase 3 Orchestrator (PresalesAgent)
├── Design Optimization Agent
│   ├── Specialization: Process engineering for scale
│   ├── Focus: Production method optimization, tolerance management
├── Pilot Production Ramp-Up Agent
│   ├── Specialization: Production transition specialist
│   ├── Focus: Scale-up planning, process optimization, risk mitigation
├── Full-Scale Manufacturing Agent
│   ├── Specialization: Production engineering
│   ├── Focus: Equipment selection, process flow, throughput optimization
├── Quality Control Production Agent
│   ├── Specialization: Production quality assurance
│   ├── Focus: Continuous monitoring, compliance, batch release
├── Packaging Agent
│   ├── Specialization: Logistics and packaging
│   ├── Focus: Package design, storage conditions, distribution planning
└── Commercialization Agent
    ├── Specialization: Market entry and customer support
    ├── Focus: Launch strategy, customer feedback, market positioning
```

## Data Flow Architecture

### Agent Communication Flow

```
User Query Input
        │
        ▼
Phase Orchestrator Agent
        │
        ▼
┌─────────────────────────┐
│ Agent Execution Engine  │
│                         │
│ 1. Create Thread        │
│ 2. Send Message         │
│ 3. Execute Run          │
│ 4. Monitor Status       │
│ 5. Process Tool Calls   │
│ 6. Extract Results      │
└─────────────────────────┘
        │
        ▼
Connected Agent Network
┌─────────┐  ┌─────────┐  ┌─────────┐
│Agent 1  │  │Agent 2  │  │Agent N  │
│         │  │         │  │         │
│Execute  │  │Execute  │  │Execute  │
│& Return │  │& Return │  │& Return │
└─────────┘  └─────────┘  └─────────┘
        │         │         │
        ▼         ▼         ▼
┌─────────────────────────────────────┐
│    Result Aggregation Engine        │
│                                     │
│ 1. Collect Agent Outputs           │
│ 2. Parse Results                   │
│ 3. Track Token Usage              │
│ 4. Generate Summary               │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│        UI Update Engine             │
│                                     │
│ 1. Update Session State           │
│ 2. Refresh Agent Outputs          │
│ 3. Display Summary                │
│ 4. Show Individual Results        │
└─────────────────────────────────────┘
```

### Data Processing Pipeline

```python
def process_agent_workflow(query: str, phase_function):
    """Standard data processing pipeline for all phases"""
    
    # 1. Initialize tracking variables
    returntxt = ""
    agent_outputs = {}
    token_usage = {}
    
    # 2. Create Azure AI Project client
    project_client = create_project_client()
    
    # 3. Create and configure agents
    agents = create_phase_agents(project_client)
    
    # 4. Create orchestrator agent with connected tools
    orchestrator = create_orchestrator_agent(project_client, agents)
    
    # 5. Execute workflow
    thread = create_thread(project_client)
    message = create_message(thread, query)
    run = execute_agent_run(thread, orchestrator)
    
    # 6. Monitor and process results
    run_steps = monitor_run_completion(run)
    agent_outputs = parse_agent_outputs(run_steps)
    token_usage = calculate_token_usage(run)
    
    # 7. Cleanup resources
    cleanup_agents_and_threads(project_client, agents, orchestrator, thread)
    
    return returntxt, agent_outputs, token_usage
```

### Session State Management

```python
# Streamlit Session State Structure
{
    "p1_history": [],        # Phase 1 conversation history
    "p2_history": [],        # Phase 2 conversation history  
    "p3_history": [],        # Phase 3 conversation history
    "p1_agents": {},         # Phase 1 agent outputs
    "p2_agents": {},         # Phase 2 agent outputs
    "p3_agents": {}          # Phase 3 agent outputs
}
```

## Integration Architecture

### Azure Services Integration

#### Azure AI Project Services
```python
# Project Client Configuration
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

# Core Operations
- Agent Management: Create, configure, delete agents
- Thread Management: Conversation context handling  
- Message Management: User and agent message handling
- Run Management: Agent execution and monitoring
```

#### Azure Application Insights Integration
```python
# Telemetry Configuration
connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=connection_string)

# Tracing Implementation
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("agent_execution"):
    # Agent execution code
```

### External API Integration Points

The system is designed with extensibility for external service integration:

```python
# Potential Integration Points (currently disabled in code)
external_services = {
    "material_databases": "Chemical composition and properties lookup",
    "regulatory_apis": "Compliance and standards verification", 
    "testing_equipment": "Lab equipment integration and results",
    "erp_systems": "Enterprise resource planning integration",
    "customer_portals": "Customer feedback and collaboration"
}
```

## Security Architecture

### Authentication and Authorization

```python
# Azure Identity Integration
credential = DefaultAzureCredential()

# Environment-based Configuration
required_env_vars = [
    "PROJECT_ENDPOINT",
    "MODEL_ENDPOINT", 
    "MODEL_API_KEY",
    "MODEL_DEPLOYMENT_NAME"
]
```

### Data Security Measures

#### Input Sanitization
```python
def _html_escape(text):
    """Escape HTML characters to prevent injection."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")
```

#### Session Isolation
- Each user session maintains isolated state
- Agent instances are created and destroyed per request
- No persistent data storage in application layer

#### Communication Security
- HTTPS enforcement for all external communications
- Azure-managed encryption in transit and at rest
- Role-based access control through Azure Identity

## Deployment Architecture

### Container Deployment

```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "stmfg1.py"]
```

### Environment Configuration

```bash
# Required Environment Variables
PROJECT_ENDPOINT=https://<project>.services.ai.azure.com/api/projects/<project_name>
MODEL_ENDPOINT=https://<model>.services.ai.azure.com
MODEL_API_KEY=<api_key>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true
```

### Scaling Configuration

```yaml
# Kubernetes Deployment Example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adhesive-manufacturing-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: stmfg1
  template:
    metadata:
      labels:
        app: stmfg1
    spec:
      containers:
      - name: stmfg1
        image: stmfg1:latest
        ports:
        - containerPort: 8501
        env:
        - name: PROJECT_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-config
              key: project_endpoint
```

## Performance Architecture

### Performance Optimization Strategies

#### Agent Lifecycle Management
```python
# Efficient agent cleanup to prevent resource leaks
def cleanup_resources(project_client, agents, orchestrator, thread):
    """Systematic cleanup of all created resources"""
    project_client.agents.delete_agent(orchestrator.id)    
    project_client.agents.threads.delete(thread.id)
    
    for agent in agents:
        project_client.agents.delete_agent(agent.id)
```

#### Token Usage Optimization
```python
def calculate_token_usage(run):
    """Comprehensive token usage tracking"""
    token_usage = {}
    
    if hasattr(run, 'usage') and run.usage:
        token_usage = {
            'prompt_tokens': getattr(run.usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(run.usage, 'completion_tokens', 0),
            'total_tokens': getattr(run.usage, 'total_tokens', 0)
        }
    
    return token_usage
```

#### UI Performance
```python
# Streamlit optimization techniques
- Container height limits for scrollable content
- Efficient session state management
- Lazy loading of agent outputs
- Minimal re-rendering through targeted updates
```

### Performance Monitoring

```python
# Built-in performance metrics
performance_metrics = {
    "agent_execution_time": "Time from query to response",
    "token_consumption": "LLM token usage per interaction", 
    "memory_usage": "Application memory consumption",
    "concurrent_users": "Active user sessions",
    "error_rates": "Failed agent executions"
}
```

## Technical Requirements

### System Requirements

#### Minimum Hardware Requirements
- **CPU**: 2 cores, 2.5 GHz
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB available space
- **Network**: Stable internet connection for Azure services

#### Software Dependencies
```
Python >= 3.8
streamlit >= 1.24.0
azure-ai-projects >= 1.0.0
azure-identity >= 1.12.0
azure-monitor-opentelemetry >= 1.0.0
pandas >= 1.5.0
python-dotenv >= 0.19.0
```

### Azure Service Requirements

#### Required Azure Services
- **Azure AI Project**: Core agent orchestration service
- **Azure OpenAI**: LLM model deployment (GPT-4 series recommended)
- **Azure Application Insights**: Telemetry and monitoring
- **Azure Identity**: Authentication and authorization

#### Service Configuration
```python
azure_services_config = {
    "ai_project": {
        "tier": "Standard",
        "region": "East US 2",
        "model_deployment": "gpt-4o-mini"
    },
    "app_insights": {
        "sampling_rate": 0.1,
        "retention_days": 90
    }
}
```

## Implementation Details

### Agent Instruction Templates

Each agent follows a structured instruction template:

```python
agent_instruction_template = """
You are the {AGENT_NAME}, a {SPECIALIZATION} in the {PHASE} of adhesive product development. 
Your role is to {PRIMARY_FUNCTION}.

When {INPUT_CONDITION}, respond by:
1. {ACTION_1}
2. {ACTION_2}
3. {ACTION_3}
4. {ACTION_4}

Structure your output as: [{OUTPUT_FORMAT}]. {ADDITIONAL_GUIDANCE}
"""
```

### Error Handling Strategy

```python
def robust_agent_execution(query, phase_function):
    """Comprehensive error handling for agent workflows"""
    try:
        return phase_function(query)
    except TimeoutError:
        return handle_timeout_error()
    except ConnectionError:
        return handle_connection_error()
    except AgentExecutionError:
        return handle_agent_error()
    except Exception as e:
        return handle_general_error(e)
```

### Monitoring and Logging

```python
# Comprehensive logging strategy
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('stmfg1.log')
    ]
)

def log_agent_execution(agent_name, execution_time, token_usage):
    """Structured logging for agent performance"""
    logging.info(f"Agent: {agent_name}, Time: {execution_time}s, Tokens: {token_usage}")
```

### Future Extensibility

The architecture supports future enhancements:

```python
# Extension points for future development
extension_points = {
    "custom_agents": "Add domain-specific agents",
    "external_tools": "Integrate third-party services",
    "data_connectors": "Connect to enterprise systems", 
    "workflow_templates": "Pre-configured manufacturing workflows",
    "reporting_modules": "Advanced analytics and reporting"
}
```

## Conclusion

The Adhesive Manufacturing Orchestrator's technical architecture provides a robust, scalable, and maintainable foundation for AI-driven manufacturing processes. The multi-agent design pattern, combined with Azure's cloud services, delivers enterprise-grade capabilities while maintaining flexibility for future enhancements and integrations.