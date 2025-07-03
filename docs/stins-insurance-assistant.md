# Insurance Quote Assistant (stins.py) - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Multi-Agent System Design](#multi-agent-system-design)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [API Integration](#api-integration)
7. [Configuration](#configuration)
8. [Usage Guide](#usage-guide)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)
11. [Security](#security)

## Overview

The Insurance Quote Assistant (`stins.py`) is a sophisticated multi-agent orchestration system built on Azure AI Foundry that provides comprehensive insurance quote generation services. The application demonstrates advanced agentic AI capabilities through the coordination of specialized Connected Agents.

### Key Features
- **Multi-Agent Orchestration**: Three specialized AI agents working in coordination
- **Document Intelligence**: Vector-based search through insurance documentation
- **Email Integration**: Automated quote delivery via email
- **Interactive UI**: Streamlit-based chat interface
- **Azure AI Foundry Integration**: Native Connected Agent architecture

### Business Use Case
The system automates the complete insurance quote generation process:
1. Collects user information through conversational AI
2. Generates personalized insurance quotes
3. Retrieves relevant terms and conditions from documentation
4. Delivers complete quote packages via email

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Insurance Quote Assistant                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  Streamlit  │  │ Main Agent  │  │ Connected   │  │  Azure  │ │
│  │     UI      │  │Orchestrator │  │   Agents    │  │   AI    │ │
│  │             │  │             │  │             │  │Foundry  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   Connected Agent Ecosystem                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Insurance   │  │  Document   │  │    Email    │             │
│  │ Price Agent │  │Search Agent │  │   Agent     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Vector    │  │  File       │  │   Email     │             │
│  │   Store     │  │ Storage     │  │  Service    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### System Components

| Component | Type | Purpose |
|-----------|------|---------|
| **Main Orchestrator Agent** | Primary Agent | Coordinates all connected agents and manages workflow |
| **Insurance Price Agent** | Connected Agent | Collects user information and generates insurance quotes |
| **Document Search Agent** | Connected Agent | Searches insurance documents for terms and conditions |
| **Email Agent** | Connected Agent | Delivers quotes and documentation via email |
| **Vector Store** | Data Store | Enables semantic search through insurance documents |
| **Streamlit UI** | Interface | Provides conversational chat interface |

## Multi-Agent System Design

### Connected Agent Pattern

The system implements Azure AI Foundry's Connected Agent pattern, where specialized agents are orchestrated by a main coordinator:

```python
# Agent Creation Pattern
def create_specialized_agent(client, name, instructions, tools=None):
    agent = client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=name,
        instructions=instructions,
        tools=tools or [],
        temperature=0.7
    )
    return ConnectedAgentTool(
        id=agent.id, 
        name=name, 
        description=f"Specialized agent for {name}"
    )
```

### Agent Coordination Flow

1. **Request Reception**: Main orchestrator receives user query
2. **Task Analysis**: Determines which connected agents are needed
3. **Sequential Execution**: Coordinates agent execution in logical order
4. **Result Aggregation**: Combines outputs from all agents
5. **Response Formatting**: Structures final response for user

## Component Details

### 1. Insurance Price Agent (`insurancepricebot`)

**Purpose**: Collects user information and generates personalized insurance quotes

**Required Information**:
- First Name
- Last Name  
- Date of Birth
- Company Name
- Age
- Preexisting Conditions

**Behavior**:
- Validates that all required information is provided
- Prompts for missing information
- Generates insurance quotes based on provided data
- Returns last known prices if real-time data unavailable

```python
insurance_price_agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="insurancepricebot",
    instructions="""Your job is to get the insurance price of a company. 
    please ask the user for First Name, Last Name, Date of Birth, and Company Name.
    Also ask for age and preexisting conditions.
    Only process the request if the user provides all the information.
    If the user does not provide all the information, ask them to provide the missing information.
    If you don't know the realtime insurance price, return the last known insurance price.""",
    temperature=0.7,
)
```

### 2. Document Search Agent (`insdocagent`)

**Purpose**: Searches insurance documentation for relevant terms, conditions, and policies

**Capabilities**:
- Vector-based semantic search through uploaded documents
- Contextual information retrieval
- Terms and conditions extraction
- Policy detail summarization

**Technical Implementation**:
- Uses Azure AI Foundry Vector Store
- FileSearchTool for document querying
- PDF document processing capabilities

```python
# Vector Store Creation
vector_store = project_client.agents.vector_stores.create_and_poll(
    file_ids=[file.id], 
    name="insurance_vector_store"
)

# File Search Tool Configuration
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

# Agent with Document Search Capabilities
insdocagent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="insdocagent",
    instructions="You are a Insurance Process agent and can search information from uploaded files",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

### 3. Email Agent (`sendemail`)

**Purpose**: Delivers complete insurance quotes and documentation via email

**Functionality**:
- Formats insurance quotes for email delivery
- Includes terms and conditions
- Sends personalized emails to users
- Handles email delivery confirmation

**Integration**: 
- Pre-configured Connected Agent (`asst_g3hRNabXnYHg3mzqBxvgDRG6`)
- External email service integration
- Template-based email formatting

### 4. Main Orchestrator Agent (`InsuranceQuoteAssistant`)

**Purpose**: Coordinates all connected agents and manages the complete workflow

**Workflow Logic**:
1. Uses Insurance Price Agent to generate quotes
2. Retrieves terms/conditions via Document Search Agent
3. Formats and sends complete package via Email Agent
4. Returns structured response to user

**Response Format**:
```
[QUOTE]
<insurance quote here>
[EMAIL OUTPUT]
<email agent output here>
```

## Data Flow

### Request Processing Flow

```
User Input → Streamlit UI → Main Orchestrator
                                    ↓
                            Task Distribution
                                    ↓
        ┌─────────────────────────────────────────────────┐
        ↓                           ↓                     ↓
Insurance Price Agent    Document Search Agent    Email Agent
        ↓                           ↓                     ↓
    Quote Generation        Terms Retrieval        Email Delivery
        ↓                           ↓                     ↓
        └─────────────────────────────────────────────────┘
                                    ↓
                            Result Aggregation
                                    ↓
                            Response Formatting
                                    ↓
                            User Response
```

### Data Persistence

1. **Vector Store**: Insurance documents stored in Azure AI Foundry Vector Store
2. **Thread Management**: Conversation threads maintained during session
3. **Agent Lifecycle**: Agents created per request, cleaned up after completion
4. **Session State**: Chat history maintained in Streamlit session state

## API Integration

### Azure AI Foundry Services

- **AIProjectClient**: Core project management and agent orchestration
- **Agent Management**: Creation, deletion, and lifecycle management
- **Thread Management**: Conversation thread handling
- **Message Processing**: Asynchronous message processing with status polling
- **Vector Store**: Document storage and semantic search

### Azure OpenAI Integration

- **Model Deployment**: Configurable model deployment names
- **Temperature Control**: Controlled randomness in responses
- **Token Management**: Efficient token usage across agents

### External Service Integration

- **Email Service**: Pre-configured email agent for delivery
- **File Storage**: PDF document upload and processing
- **Authentication**: Azure DefaultAzureCredential for service authentication

## Configuration

### Environment Variables

```bash
# Azure AI Foundry Configuration
PROJECT_ENDPOINT=<Azure AI Foundry Project Endpoint>
MODEL_DEPLOYMENT_NAME=<Model Deployment Name>

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=<Azure OpenAI Endpoint>
AZURE_OPENAI_KEY=<Azure OpenAI API Key>
AZURE_OPENAI_DEPLOYMENT=<Deployment Name>

# Authentication
AZURE_CLIENT_ID=<Service Principal Client ID>
AZURE_CLIENT_SECRET=<Service Principal Secret>
AZURE_TENANT_ID=<Azure Tenant ID>
```

### File Dependencies

- **Insurance Documentation**: `./data/insurancetc.pdf`
- **Environment File**: `.env` for configuration
- **Dependencies**: Listed in `requirements.txt`

## Usage Guide

### Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run stins.py
```

### User Interaction Flow

1. **Access Interface**: Navigate to Streamlit application URL
2. **Start Conversation**: Enter insurance quote request
3. **Provide Information**: Respond to agent prompts for required details
4. **Review Quote**: Examine generated insurance quote
5. **Email Delivery**: Receive complete quote package via email
6. **Chat Management**: Use "Clear Chat" to start new session

### Sample Interaction

```
User: "I need an insurance quote"

Agent: "I'd be happy to help you with an insurance quote. To provide you with an accurate quote, I'll need the following information:
- First Name
- Last Name  
- Date of Birth
- Company Name
- Age
- Any preexisting conditions

Could you please provide these details?"

User: "My name is John Smith, DOB is 01/15/1985, I work at TechCorp, I'm 38 years old, and I have diabetes."

Agent: "Thank you for providing all the required information. Let me generate your insurance quote and gather the relevant terms and conditions..."

[System processes through all three agents]

Agent: "[QUOTE]
Based on your information:
- Name: John Smith
- Age: 38
- Company: TechCorp
- Preexisting condition: Diabetes
- Estimated Premium: $245/month
- Coverage: $500,000

[EMAIL OUTPUT]
Your complete insurance quote has been sent to your email address including detailed terms and conditions."
```

## Error Handling

### Agent Management Errors

- **Agent Creation Failures**: Automatic retry with exponential backoff
- **Connection Timeouts**: Configurable timeout settings
- **Resource Cleanup**: Guaranteed cleanup of agents and vector stores

### Runtime Error Handling

```python
try:
    # Agent operations
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id, 
        agent_id=agent.id
    )
    
    # Status polling with error detection
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            break
            
except Exception as e:
    st.error(f"Agent processing failed: {e}")
    return "I apologize, but I'm having trouble processing your request."
    
finally:
    # Guaranteed cleanup
    project_client.agents.delete_agent(agent.id)
    project_client.agents.threads.delete(thread.id)
    project_client.agents.vector_stores.delete(vector_store.id)
```

### User Input Validation

- **Required Information Checking**: Agents validate completeness of user data
- **Format Validation**: Date, age, and contact information format checking
- **Error Messages**: Clear, actionable error messages for missing information

## Performance Considerations

### Agent Lifecycle Management

- **Dynamic Creation**: Agents created per request to avoid resource conflicts
- **Automatic Cleanup**: Guaranteed deletion of agents, threads, and vector stores
- **Resource Optimization**: Minimal resource footprint per session

### Scalability Factors

| Component | Scalability Consideration | Mitigation Strategy |
|-----------|---------------------------|-------------------|
| **Agent Creation** | Azure AI Foundry rate limits | Request queuing and retry logic |
| **Vector Store** | Document size limitations | Document chunking and optimization |
| **Concurrent Users** | Shared resource conflicts | Per-session resource isolation |
| **Email Delivery** | External service dependencies | Asynchronous processing and fallback |

### Performance Optimization

```python
# Efficient resource management
def optimize_agent_performance():
    # 1. Reuse vector stores when possible
    # 2. Implement agent pooling for high-traffic scenarios  
    # 3. Cache frequently accessed documents
    # 4. Use asynchronous processing where applicable
    pass
```

## Security

### Authentication & Authorization

- **Azure Identity**: DefaultAzureCredential for service authentication
- **Environment Variables**: Secure credential storage
- **API Key Management**: Rotation-ready configuration

### Data Security

| Security Layer | Implementation | Purpose |
|----------------|----------------|---------|
| **Transport Security** | HTTPS/TLS encryption | Secure data transmission |
| **Authentication** | Azure AD integration | Service identity verification |
| **Access Control** | RBAC on Azure resources | Principle of least privilege |
| **Data Encryption** | Azure-managed encryption | Data at rest protection |

### Privacy Considerations

- **PII Handling**: Secure processing of personal information
- **Data Retention**: Automatic cleanup of temporary data
- **Audit Logging**: Comprehensive operation logging
- **Compliance**: GDPR and healthcare data compliance ready

### Security Best Practices

```python
# Secure configuration example
def secure_agent_setup():
    # 1. Use environment variables for all secrets
    # 2. Implement proper error handling without exposing internals
    # 3. Validate all user inputs
    # 4. Use least-privilege service principals
    # 5. Enable audit logging
    # 6. Implement proper session management
    pass
```

## Troubleshooting

### Common Issues

1. **Agent Creation Failures**
   - Check Azure AI Foundry project configuration
   - Verify model deployment availability
   - Confirm proper authentication

2. **Vector Store Issues**
   - Ensure PDF file exists at specified path
   - Check file upload permissions
   - Verify vector store creation success

3. **Email Delivery Problems**
   - Confirm email agent configuration
   - Check external email service connectivity
   - Verify recipient email addresses

### Debugging Tools

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor agent execution
def debug_agent_execution(run_steps):
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        # Additional debugging information
```

### Monitoring and Observability

- **Azure Monitor Integration**: Performance and error tracking
- **Custom Metrics**: Agent execution time and success rates
- **Health Checks**: Automated system health verification
- **Alert Configuration**: Proactive issue notification

## Integration Examples

### Extending the System

```python
# Adding a new connected agent
def add_claims_processing_agent():
    claims_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="claimsprocessor",
        instructions="Process insurance claims and provide status updates",
        temperature=0.5
    )
    
    return ConnectedAgentTool(
        id=claims_agent.id,
        name="claimsprocessor", 
        description="Processes insurance claims"
    )

# Integrating with external APIs
def integrate_external_pricing_api():
    # Implementation for real-time pricing integration
    pass
```

### Custom Workflows

The architecture supports extension for additional insurance workflows:
- Claims processing
- Policy renewals
- Risk assessments
- Customer service automation

## Conclusion

The Insurance Quote Assistant demonstrates sophisticated multi-agent orchestration using Azure AI Foundry Connected Agents. The system provides a complete solution for insurance quote generation, document search, and automated delivery, showcasing best practices for:

- **Agent Coordination**: Effective multi-agent workflow management
- **Document Intelligence**: Vector-based search and retrieval
- **User Experience**: Conversational AI interfaces
- **System Integration**: Cloud-native Azure service integration
- **Security**: Enterprise-grade security implementations

The modular architecture enables easy extension and customization for various insurance workflows and business requirements.