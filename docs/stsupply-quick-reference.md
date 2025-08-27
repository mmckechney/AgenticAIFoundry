# Healthcare Supply Chain Orchestrator - Quick Reference Guide

## System Overview

**Application**: Healthcare Supply Chain Orchestrator  
**File**: `stsupply.py`  
**Purpose**: AI-powered SCOR-based supply chain optimization for healthcare and life sciences  
**Framework**: Streamlit + Azure AI Project Services  
**Agents**: 5 specialized agents (Plan, Source, Make, Deliver, Return)

## Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROJECT_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<name>"
export MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
export AZURE_OPENAI_ENDPOINT="https://<account>.openai.azure.com/"
export AZURE_OPENAI_KEY="<your-api-key>"

# Run application
streamlit run stsupply.py
```

## Agent Reference

### SCOR Agents Overview

| Agent | Purpose | Key Functions | Typical Use Cases |
|-------|---------|---------------|-------------------|
| **Plan Agent** | Demand & Supply Planning | • Demand forecasting<br/>• Resource allocation<br/>• Risk assessment | Market analysis, capacity planning, disruption scenarios |
| **Source Agent** | Procurement & Suppliers | • Supplier identification<br/>• Contract negotiation<br/>• Compliance audits | API sourcing, vendor selection, ESG compliance |
| **Make Agent** | Manufacturing & Production | • Production planning<br/>• Quality control<br/>• Batch management | GMP compliance, serialization, scale-up |
| **Deliver Agent** | Distribution & Logistics | • Logistics optimization<br/>• Cold-chain management<br/>• Last-mile delivery | Vaccine distribution, global shipping, tracking |
| **Return Agent** | Reverse Logistics | • Product recalls<br/>• Sustainability<br/>• Post-market surveillance | Recall management, waste reduction, adverse events |

### Agent Instructions Summary

```python
# Plan Agent Focus Areas
- Historical sales analysis and trend identification
- Market volatility and emerging health issues impact
- Regulatory timeline integration (FDA, EMA approvals)
- Resource planning (staff, equipment, facilities)
- Risk scenarios and mitigation strategies

# Source Agent Focus Areas  
- GMP-certified supplier identification and evaluation
- Contract terms with quality assurances and contingencies
- Blockchain-based traceability for upstream materials
- Supplier diversification across regions for APIs
- ESG compliance and low-carbon sourcing

# Make Agent Focus Areas
- GMP and GLP compliance in manufacturing processes
- Real-time quality control with AI monitoring
- Serialization and batch record management
- Automation and robotics for efficiency optimization
- Patient safety emphasis throughout production

# Deliver Agent Focus Areas
- Cold-chain requirements for biologics and vaccines
- IATA compliance for hazardous material shipping
- IoT integration for real-time monitoring
- Last-mile delivery to hospitals and patients
- Control tower visibility for issue resolution

# Return Agent Focus Areas
- Regulatory compliance for product recalls
- Environmental regulations for waste disposal
- Post-market adverse event analysis
- Sustainability initiatives and recycling
- Traceability systems for recall efficiency
```

## Key Functions

### Core Workflow Functions
```python
# Main function for supply chain analysis
def supplychain_agent(query: str) -> tuple[str, dict, dict]
    """
    Process supply chain query through SCOR agents
    
    Returns:
        - response_text: Integrated analysis from all agents
        - agent_outputs: Individual agent responses dict
        - token_usage: Token consumption metrics dict
    """

# Utility function for parsing agent responses
def parse_agent_outputs(run_steps) -> dict
    """
    Extract individual agent responses from run steps
    
    Returns:
        - Dict mapping agent names to their outputs
    """

# Main UI function
def supplychain_analyst() -> None
    """
    Streamlit UI for supply chain analysis with chat interface
    """
```

### Return Values
```python
# Standard return pattern for supplychain_agent()
response_text: str          # Integrated response from orchestrator
agent_outputs: dict = {     # Individual agent outputs
    "planagent": "planning analysis...",
    "sourceagent": "sourcing recommendations...",
    "makeagent": "manufacturing insights...",
    "deliveragent": "distribution strategy...",
    "returnagent": "return considerations..."
}
token_usage: dict = {       # Token consumption metrics
    "prompt_tokens": int,
    "completion_tokens": int,
    "total_tokens": int
}
```

## Configuration Reference

### Environment Variables

```bash
# Required Azure Configuration
PROJECT_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<name>"
MODEL_DEPLOYMENT_NAME="gpt-4o-mini"                    # or gpt-4o
MODEL_ENDPOINT="https://<account>.services.ai.azure.com"
MODEL_API_KEY="<your-model-api-key>"

# Azure OpenAI Configuration  
AZURE_OPENAI_ENDPOINT="https://<account>.openai.azure.com/"
AZURE_OPENAI_KEY="<your-openai-api-key>"

# Optional Whisper Configuration
WHISPER_DEPLOYMENT_NAME="whisper"

# Telemetry Configuration
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED="true"
```

### Azure Services Required

```python
# Core Services
azure_services = {
    "ai_foundry": "Azure AI Foundry Project",
    "openai": "Azure OpenAI Service", 
    "insights": "Application Insights",
    "identity": "Azure Active Directory"
}

# Optional Services for Production
production_services = {
    "key_vault": "Azure Key Vault",
    "service_bus": "Azure Service Bus", 
    "redis": "Azure Cache for Redis",
    "sql": "Azure SQL Database",
    "storage": "Azure Data Lake Storage"
}
```

## UI Components

### Main Interface Elements

```python
# Streamlit UI Structure
st.title("🏥 Healthcare Supply Chain Analyst")

# Two-column layout
left_col, right_col = st.columns([1, 1.2])

# Left column: Chat History
with left_col:
    st.subheader("💬 Chat History")
    chat_container = st.container(height=600)

# Right column: Agent Outputs  
with right_col:
    st.subheader("🤖 Individual Agent Outputs")
    agent_container = st.container(height=600)

# Bottom: Chat Input
user_input = st.chat_input("Type your supply chain question here...")
```

### Session State Management

```python
# Session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []         # List of (role, message, timestamp)
    
if 'agent_outputs' not in st.session_state:
    st.session_state.agent_outputs = []       # List of agent output dicts
    
if 'token_usage' not in st.session_state:
    st.session_state.token_usage = []         # List of token usage dicts
```

## Common Usage Patterns

### Basic Supply Chain Query
```python
# Simple demand forecasting query
query = "Analyze demand forecast for oncology drugs in Q2 2024"
response, outputs, usage = supplychain_agent(query)

# Access individual agent insights
planning_insights = outputs.get("planagent", "No planning data")
sourcing_strategy = outputs.get("sourceagent", "No sourcing data")
```

### Complex Multi-Stage Analysis
```python
# Comprehensive supply chain optimization
query = """
Optimize the supply chain for a new CAR-T cell therapy launch:
- Patient demand forecast for personalized medicine
- Specialized reagent and material sourcing 
- Custom manufacturing with quality controls
- Cold-chain distribution network setup
- Patient outcome tracking and returns
"""
response, outputs, usage = supplychain_agent(query)
```

### Regulatory Compliance Check
```python
# FDA/EMA compliance analysis
query = """
Evaluate regulatory compliance for pharmaceutical manufacturing:
- GMP facility requirements
- API sourcing standards
- Quality control processes  
- Distribution controls
- Post-market surveillance
"""
response, outputs, usage = supplychain_agent(query)
```

### Supply Chain Disruption Response
```python
# Crisis management and contingency planning
query = """
Develop contingency plan for API supply disruption:
- Alternative supplier identification
- Inventory buffer strategies
- Manufacturing process adjustments
- Distribution rerouting options
- Customer communication plan
"""
response, outputs, usage = supplychain_agent(query)
```

## Performance Optimization

### Caching Strategies
```python
# Enable caching for repeated queries
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_supply_chain_analysis(query_hash: str):
    return supplychain_agent(query)

# Use session state for UI performance
if st.button("Analyze", key="analyze_btn"):
    with st.spinner("Processing..."):
        result = supplychain_agent(user_input)
        st.session_state.last_result = result
```

### Resource Management
```python
# Monitor token usage
def track_usage(usage_dict):
    total_tokens = usage_dict.get('total_tokens', 0)
    if total_tokens > 10000:  # Warning threshold
        st.warning(f"High token usage: {total_tokens}")
    
# Cleanup agents after processing
try:
    # Agent processing
    pass
finally:
    # Cleanup is handled automatically in supplychain_agent()
    pass
```

## Code Snippets

### Custom Agent Creation
```python
# Create specialized agent with custom instructions
def create_custom_agent(specialization: str, instructions: str):
    return project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=f"{specialization}_agent",
        instructions=instructions
    )

# Example: Regulatory specialist agent
regulatory_agent = create_custom_agent(
    "regulatory",
    "You are a regulatory affairs specialist for pharmaceutical supply chains..."
)
```

### Telemetry Integration
```python
# Add custom telemetry tracking
with tracer.start_as_current_span("supply_chain_analysis") as span:
    span.set_attribute("query.type", "pharmaceutical")
    span.set_attribute("agents.count", 5)
    
    result = supplychain_agent(query)
    
    span.set_attribute("tokens.used", result[2]['total_tokens'])
    span.set_attribute("status", "success")
```

### Error Handling
```python
# Robust error handling pattern
try:
    response, outputs, usage = supplychain_agent(user_input)
    st.success("✅ Analysis complete!")
    
except Exception as e:
    error_msg = f"Analysis failed: {str(e)}"
    st.error(f"❌ {error_msg}")
    
    # Log error for monitoring
    logging.error(error_msg, exc_info=True)
    
    # Fallback response
    st.info("Please try rephrasing your query or contact support.")
```

## API Reference Summary

### Core Classes and Methods

```python
# Azure AI Project Client
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

# Agent creation and management
agent = project_client.agents.create_agent(model, name, instructions)
thread = project_client.agents.threads.create()
message = project_client.agents.messages.create(thread_id, role, content)
run = project_client.agents.runs.create_and_process(thread_id, agent_id)

# Connected agent tools
connected_tool = ConnectedAgentTool(id, name, description)

# Telemetry configuration
configure_azure_monitor(connection_string)
tracer = trace.get_tracer(__name__)
```

## Architecture Quick View

### System Layers
```
┌─────────────────────────────────────┐
│           User Interface            │ ← Streamlit UI
├─────────────────────────────────────┤
│       Orchestration Layer          │ ← Main Agent + Message Queue
├─────────────────────────────────────┤
│          SCOR Agents               │ ← Plan, Source, Make, Deliver, Return
├─────────────────────────────────────┤
│         AI Services                │ ← Azure AI + OpenAI
├─────────────────────────────────────┤
│        Data & Storage              │ ← Databases + Cache + File Storage  
├─────────────────────────────────────┤
│     Integration Layer              │ ← ERP, WMS, Regulatory APIs
├─────────────────────────────────────┤
│     Infrastructure                 │ ← Azure Services + Monitoring
└─────────────────────────────────────┘
```

### Data Flow Summary
```
User Query → UI → Orchestrator → SCOR Agents → AI Services → Response Synthesis → UI Display
    ↑                                ↓
    └── Chat History ←─── Agent Outputs ←─── Individual Processing
```

## File Structure
```
stsupply.py
├── Imports & Configuration     (Lines 1-58)
├── Utility Functions          (Lines 59-76)
├── Core Agent Function        (Lines 77-332)
├── UI Implementation          (Lines 334-554)
└── Main Entry Point          (Lines 555-557)
```

## Troubleshooting

### Common Issues

**Issue**: "Authentication failed"
```bash
# Solution: Check Azure credentials
az login
az account show
export PROJECT_ENDPOINT="correct_endpoint_here"
```

**Issue**: "Model deployment not found"
```bash
# Solution: Verify model deployment name
export MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
# Or check available deployments in Azure OpenAI Studio
```

**Issue**: "Token limit exceeded"
```python
# Solution: Monitor token usage and split large queries
if usage['total_tokens'] > 8000:
    st.warning("Consider breaking down your query into smaller parts")
```

**Issue**: "Agent creation timeout"
```python
# Solution: Implement retry logic with exponential backoff
import time
import random

def retry_agent_creation(max_retries=3):
    for attempt in range(max_retries):
        try:
            return project_client.agents.create_agent(...)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt + random.uniform(0, 1))
```

## Support Contacts

- **Repository**: [AgenticAI Foundry](https://github.com/balakreshnan/AgenticAIFoundry)
- **Documentation**: `/docs/stsupply-*` files
- **Issues**: GitHub Issues for bug reports and feature requests
- **Azure Support**: For Azure service-related issues

---

*This quick reference provides essential information for developers and users working with the Healthcare Supply Chain Orchestrator system.*