# AI Maturity Assessment Tool - Technical Architecture

## 📐 Architecture Overview

The AI Maturity Assessment Tool (`stasses.py`) implements a modern web-based assessment platform built on Azure AI Foundry with Streamlit frontend, Azure OpenAI integration, and comprehensive observability features.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Architecture](#component-architecture)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Integration Architecture](#integration-architecture)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Performance Architecture](#performance-architecture)
8. [Monitoring Architecture](#monitoring-architecture)

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Maturity Assessment Tool                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  Streamlit  │  │ Assessment  │  │   Azure     │  │ Telemetry│ │
│  │   Frontend  │  │   Engine    │  │   OpenAI    │  │ & Monitor│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   Azure AI Foundry Platform                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Project   │  │   Azure     │  │   Default   │  │  Azure  │ │
│  │   Client    │  │   Monitor   │  │   Azure     │  │ Identity│ │
│  │             │  │ OpenTelemetry│  │ Credential  │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Patterns
- **Model-View-Controller (MVC)**: Clear separation of concerns
- **Configuration-Driven**: JSON-based assessment structure
- **Event-Driven**: Streamlit reactive programming model
- **Service-Oriented**: Azure AI Foundry service integration
- **Observability-First**: Comprehensive telemetry integration

## 🧩 Component Architecture

### Core Components

#### 1. Frontend Layer (Streamlit)
```python
# UI Components
class StreamlitUI:
    - Page Configuration
    - Assessment Form Generation
    - Data Visualization (Plotly)
    - Session State Management
    - User Interaction Handling
```

**Responsibilities**:
- User interface rendering and interaction
- Form data collection and validation
- Results visualization and presentation
- Session state management

#### 2. Assessment Engine
```python
# Assessment Processing
class AssessmentEngine:
    - Dimension Scoring Calculation
    - Weighted Score Aggregation
    - Quadrant Classification Logic
    - Results Analysis and Formatting
```

**Responsibilities**:
- Load assessment configuration from JSON
- Calculate dimension scores and weighted totals
- Determine quadrant positioning
- Prepare data for visualization

#### 3. AI Recommendation Service
```python
# Azure OpenAI Integration
class RecommendationService:
    - Azure OpenAI Client Management
    - Prompt Engineering for Assessment Context
    - Response Processing and Formatting
    - Error Handling and Retry Logic
```

**Responsibilities**:
- Generate personalized recommendations
- Process assessment results through AI
- Format and deliver strategic guidance
- Handle Azure OpenAI service interactions

#### 4. Configuration Manager
```python
# Configuration Management
class ConfigManager:
    - JSON Assessment Structure Loading
    - Environment Variable Management
    - Quadrant Definition Management
    - Weight and Dimension Configuration
```

**Responsibilities**:
- Load and validate assessment configuration
- Manage environment variables and settings
- Provide configuration data to other components

#### 5. Telemetry Service
```python
# Observability and Monitoring
class TelemetryService:
    - OpenTelemetry Integration
    - Azure Monitor Configuration
    - Trace Collection and Management
    - Performance Metrics Collection
```

**Responsibilities**:
- Collect application telemetry
- Configure distributed tracing
- Monitor performance and errors
- Integrate with Azure Monitor

### Component Interaction Patterns

#### Dependency Injection
```python
# Service Dependencies
StreamlitUI -> AssessmentEngine
AssessmentEngine -> ConfigManager
RecommendationService -> AzureOpenAIClient
TelemetryService -> AzureMonitor
```

#### Data Flow
```python
# Processing Pipeline
User Input -> Form Validation -> Score Calculation -> 
Quadrant Assignment -> AI Recommendation -> Result Display
```

## 🔄 Data Flow Architecture

### Assessment Data Flow

#### 1. Configuration Loading Phase
```
aiassessment.json -> ConfigManager -> Assessment Dimensions
    ↓
Dimension Weights + Questions + Descriptions
    ↓
Streamlit Form Generation
```

#### 2. User Assessment Phase
```
User Interactions -> Slider Values -> Session State
    ↓
Form Submission -> Data Validation -> Score Calculation
    ↓
Weighted Scoring -> Quadrant Classification
```

#### 3. AI Recommendation Phase
```
Assessment Results -> Prompt Construction -> Azure OpenAI
    ↓
AI Response -> Recommendation Processing -> UI Display
```

#### 4. Visualization Phase
```
Scores + Quadrant -> Plotly Chart Generation -> Interactive Display
    ↓
Results Table -> DataFrame Creation -> Streamlit Display
```

### Data Structures

#### Assessment Configuration
```json
{
  "name": "Dimension Name",
  "weight": 0.2,
  "questions": [
    {
      "text": "Question text",
      "desc": "Scoring guidance"
    }
  ]
}
```

#### Runtime Data Model
```python
@dataclass
class AssessmentResult:
    dimension_scores: Dict[str, float]
    weighted_scores: Dict[str, float]
    total_score: float
    quadrant: int
    x_coordinate: float  # Results & Impact
    y_coordinate: float  # Strategy & Governance
    bubble_size: int     # Technology readiness
    color_score: float   # Responsible AI maturity
```

## 🔗 Integration Architecture

### Azure AI Foundry Integration

#### Project Client Setup
```python
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)
```

**Integration Points**:
- **Authentication**: DefaultAzureCredential for secure access
- **Telemetry**: Connection string retrieval for monitoring
- **Service Discovery**: Endpoint and resource management

#### Azure OpenAI Integration
```python
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-12-01-preview"
)
```

**Features**:
- **Chat Completions**: GPT model integration for recommendations
- **System Prompts**: Specialized AI assessment assistant configuration
- **Response Processing**: Structured recommendation generation

### External Service Dependencies

#### Required Services
- **Azure OpenAI**: AI-powered recommendation generation
- **Azure Monitor**: Telemetry and observability
- **Azure Identity**: Authentication and authorization

#### Optional Integrations
- **Custom Functions**: User-defined function tracing
- **Agent Utils**: Shared utility functions
- **Additional Azure Services**: Extensible architecture

## 🔒 Security Architecture

### Authentication & Authorization
```python
# Azure Identity Integration
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=credential
)
```

### Data Security
- **No Persistent Storage**: Session-only data retention
- **Secure Transmission**: HTTPS/TLS encryption
- **Credential Management**: Azure Key Vault integration
- **API Security**: Azure OpenAI key management

### Privacy Controls
- **Session Isolation**: Individual user session management
- **Data Minimization**: Collect only necessary assessment data
- **Secure Disposal**: Automatic session cleanup
- **Audit Trails**: Telemetry-based activity logging

## 🚀 Deployment Architecture

### Local Development
```bash
# Development Stack
Python 3.8+ -> Streamlit -> Azure Services
    ↓
Local Environment -> .env Configuration -> Cloud Integration
```

### Production Deployment Options

#### Option 1: Azure Container Instances
```yaml
# Container Deployment
containerInstances:
  - name: ai-assessment-tool
    image: assessment-tool:latest
    resources:
      requests:
        cpu: 1
        memoryInGB: 2
    environmentVariables:
      - name: AZURE_OPENAI_ENDPOINT
        secureValue: ${AZURE_OPENAI_ENDPOINT}
```

#### Option 2: Azure App Service
```yaml
# App Service Configuration
webApp:
  name: ai-maturity-assessment
  runtime: python:3.9
  appSettings:
    - AZURE_OPENAI_ENDPOINT
    - PROJECT_ENDPOINT
    - AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED
```

#### Option 3: Azure Kubernetes Service
```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: assessment-tool
spec:
  replicas: 3
  selector:
    matchLabels:
      app: assessment-tool
  template:
    spec:
      containers:
      - name: assessment-tool
        image: assessment-tool:latest
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: openai-endpoint
```

## ⚡ Performance Architecture

### Scalability Patterns
- **Stateless Design**: No server-side session storage
- **Caching Strategy**: Configuration and static data caching
- **Lazy Loading**: On-demand resource initialization
- **Connection Pooling**: Azure service connection optimization

### Performance Optimizations
```python
# Streamlit Optimization
@st.cache_data
def load_assessment_config():
    """Cache assessment configuration"""
    return json.load(open("aiassessment.json"))

@st.cache_resource
def initialize_azure_client():
    """Cache Azure client initialization"""
    return AzureOpenAI(...)
```

### Resource Management
- **Memory Efficiency**: Minimal data structures
- **CPU Optimization**: Efficient calculation algorithms
- **Network Optimization**: Batch API requests
- **Storage Optimization**: Temporary data only

## 📊 Monitoring Architecture

### OpenTelemetry Integration
```python
# Telemetry Configuration
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor(connection_string=connection_string)
tracer = trace.get_tracer(__name__)
```

### Monitoring Layers

#### 1. Application Performance Monitoring
- **Request Tracing**: End-to-end request tracking
- **Error Monitoring**: Exception capture and analysis
- **Performance Metrics**: Response time and throughput
- **Custom Metrics**: Assessment-specific measurements

#### 2. Infrastructure Monitoring
- **Resource Utilization**: CPU, memory, and network usage
- **Service Health**: Azure service dependency monitoring
- **Availability Monitoring**: Uptime and reliability tracking

#### 3. Business Intelligence
- **Usage Analytics**: Assessment completion rates
- **User Behavior**: Interaction patterns and preferences
- **Feature Adoption**: Component usage statistics

### Observability Features

#### Distributed Tracing
```python
with tracer.start_as_current_span("assessment_processing"):
    scores = calculate_scores(user_input)
    
    with tracer.start_as_current_span("ai_recommendation"):
        recommendations = generate_recommendations(scores)
```

#### Custom Metrics
```python
# Business Metrics
- assessment_completions_total
- quadrant_distribution
- recommendation_generation_time
- user_session_duration
```

#### Alerting Rules
- **High Error Rate**: > 5% error rate threshold
- **Slow Response Time**: > 10 second response time
- **Service Unavailability**: Azure service connection failures
- **Resource Exhaustion**: Memory or CPU threshold breaches

## 🔄 Extension Architecture

### Plugin Architecture
The system supports extensible functionality through:

#### Custom Assessment Dimensions
```json
{
  "name": "Custom Dimension",
  "weight": 0.1,
  "questions": [...],
  "custom_logic": "optional_custom_processing"
}
```

#### Additional Recommendation Sources
```python
class CustomRecommendationProvider:
    def generate_recommendations(self, assessment_data):
        # Custom recommendation logic
        return formatted_recommendations
```

#### Enhanced Visualization Components
```python
class CustomVisualization:
    def render_custom_chart(self, data):
        # Custom Plotly/visualization logic
        return interactive_chart
```

### API Integration Points
- **REST API**: Future web service API
- **Webhook Integration**: External system notifications
- **Data Export**: CSV/JSON result export capabilities
- **Third-party Integrations**: External assessment tools

---

*This technical architecture provides a comprehensive foundation for the AI Maturity Assessment Tool, ensuring scalability, maintainability, and extensibility while leveraging Azure AI Foundry's full capabilities.*