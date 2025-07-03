# Insurance Quote Assistant - Technical Architecture & Design

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Connected Agent Pattern](#connected-agent-pattern)
3. [Azure AI Foundry Integration](#azure-ai-foundry-integration)
4. [Multi-Agent Orchestration Design](#multi-agent-orchestration-design)
5. [Vector Store Implementation](#vector-store-implementation)
6. [Event-Driven Architecture](#event-driven-architecture)
7. [Scalability & Performance](#scalability--performance)
8. [Deployment Architecture](#deployment-architecture)
9. [Monitoring & Observability](#monitoring--observability)
10. [Future Architecture Considerations](#future-architecture-considerations)

## Architecture Overview

The Insurance Quote Assistant demonstrates a sophisticated implementation of Azure AI Foundry's Connected Agent pattern, creating a multi-agent orchestration system that coordinates specialized AI agents to deliver comprehensive insurance services.

### Core Architectural Principles

1. **Separation of Concerns**: Each agent has a specific, well-defined responsibility
2. **Loose Coupling**: Agents communicate through standardized interfaces
3. **Scalable Design**: Stateless agent design enables horizontal scaling
4. **Resource Efficiency**: Dynamic agent lifecycle management
5. **Fault Tolerance**: Comprehensive error handling and cleanup procedures

### System Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Streamlit  │  │   Chat UI   │  │   Session   │            │
│  │   Server    │  │  Components │  │  Management │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Request   │  │   Agent     │  │  Response   │            │
│  │ Processing  │  │Orchestration│  │ Formatting  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Insurance   │  │  Document   │  │    Email    │            │
│  │Price Agent  │  │Search Agent │  │   Agent     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Platform Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Azure AI  │  │ Vector Store│  │   External  │            │
│  │  Foundry    │  │   Service   │  │  Services   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Connected Agent Pattern

The system implements Azure AI Foundry's Connected Agent pattern, which enables sophisticated multi-agent workflows through standardized agent-to-agent communication.

### Connected Agent Implementation

```python
# Connected Agent Tool Definition
class ConnectedAgentImplementation:
    def __init__(self, agent_id: str, name: str, description: str):
        self.connected_tool = ConnectedAgentTool(
            id=agent_id,
            name=name,
            description=description
        )
    
    def get_definitions(self) -> List[ToolDefinition]:
        return self.connected_tool.definitions
    
    def execute(self, input_data: str) -> str:
        # Agent execution logic handled by Azure AI Foundry
        pass
```

### Agent Communication Protocol

| Component | Purpose | Communication Method |
|-----------|---------|---------------------|
| **Main Orchestrator** | Workflow coordination | Direct tool invocation |
| **Connected Agents** | Specialized processing | Tool call responses |
| **Azure AI Foundry** | Message routing | Thread-based messaging |
| **External Services** | Data/service integration | API calls |

### Tool Definition Architecture

Each Connected Agent exposes its capabilities through standardized tool definitions:

```python
def create_agent_tool_definition(agent: Agent) -> ConnectedAgentTool:
    return ConnectedAgentTool(
        id=agent.id,
        name=agent.name,
        description=agent.capabilities_description
    )

# Usage in Main Orchestrator
main_agent_tools = [
    insurance_agent_tool.definitions[0],
    document_agent_tool.definitions[0], 
    email_agent_tool.definitions[0]
]
```

## Azure AI Foundry Integration

The system leverages multiple Azure AI Foundry services to provide comprehensive agent management and orchestration capabilities.

### Service Integration Architecture

```python
class AzureAIFoundryIntegration:
    def __init__(self):
        self.project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        
        # Service interfaces
        self.agents = self.project_client.agents
        self.threads = self.project_client.agents.threads
        self.messages = self.project_client.agents.messages
        self.runs = self.project_client.agents.runs
        self.vector_stores = self.project_client.agents.vector_stores
        self.files = self.project_client.agents.files
```

### Core Service Components

| Service | Responsibility | Usage Pattern |
|---------|----------------|---------------|
| **Agent Management** | Agent lifecycle | Create, configure, delete |
| **Thread Management** | Conversation state | Per-session threads |
| **Message Processing** | Communication | Asynchronous processing |
| **Run Orchestration** | Execution control | Status polling, error handling |
| **Vector Store** | Document storage | Semantic search capabilities |
| **File Management** | Document upload | PDF processing, indexing |

### Authentication Architecture

```python
# Multi-layer authentication strategy
authentication_chain = [
    ServicePrincipalAuthentication(),  # Production
    ManagedIdentityAuthentication(),   # Azure-hosted scenarios
    AzureCLIAuthentication(),         # Development
    EnvironmentCredentialAuthentication()  # Local development
]

credential = DefaultAzureCredential()  # Automatic failover
```

## Multi-Agent Orchestration Design

The orchestration design implements a hierarchical agent structure with sophisticated coordination mechanisms.

### Orchestration Patterns

#### 1. Sequential Orchestration
```python
async def sequential_orchestration(query: str):
    # Step 1: Collect user information
    insurance_info = await insurance_agent.collect_information(query)
    
    # Step 2: Generate quote
    quote = await insurance_agent.generate_quote(insurance_info)
    
    # Step 3: Retrieve terms
    terms = await document_agent.search_terms(quote.policy_type)
    
    # Step 4: Send email
    confirmation = await email_agent.send_quote(quote, terms, user.email)
    
    return format_response(quote, terms, confirmation)
```

#### 2. Conditional Orchestration
```python
def conditional_orchestration(user_state: UserState):
    if not user_state.has_required_info():
        return insurance_agent.request_information()
    
    if user_state.needs_quote():
        quote = insurance_agent.generate_quote()
        
        if quote.requires_terms():
            terms = document_agent.search_terms()
            
        if user_state.wants_email():
            email_agent.send_quote(quote, terms)
    
    return orchestrate_response(quote, terms, email_status)
```

### Agent Coordination Mechanisms

#### Message Passing Architecture
```python
class AgentCoordinator:
    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.agent_registry = {}
        self.workflow_state = WorkflowState()
    
    async def coordinate_agents(self, workflow: Workflow):
        for step in workflow.steps:
            agent = self.agent_registry[step.agent_name]
            result = await agent.execute(step.input, step.context)
            self.workflow_state.update(step.name, result)
            
            # Conditional next step execution
            next_steps = workflow.get_next_steps(step.name, result)
            for next_step in next_steps:
                await self.message_queue.put(next_step)
```

#### Error Handling and Recovery
```python
class OrchestrationErrorHandler:
    def __init__(self):
        self.retry_policies = {
            "agent_creation": ExponentialBackoff(max_retries=3),
            "communication": LinearBackoff(max_retries=5),
            "external_service": CircuitBreaker(failure_threshold=3)
        }
    
    async def handle_agent_failure(self, agent_name: str, error: Exception):
        policy = self.retry_policies.get(type(error).__name__)
        
        if policy.should_retry():
            return await self.retry_agent_operation(agent_name, policy)
        else:
            return await self.fallback_operation(agent_name, error)
```

## Vector Store Implementation

The document search capabilities are powered by Azure AI Foundry's Vector Store service, enabling sophisticated semantic search across insurance documentation.

### Vector Store Architecture

```python
class InsuranceVectorStore:
    def __init__(self, project_client: AIProjectClient):
        self.client = project_client
        self.vector_store = None
        self.file_search_tool = None
    
    async def initialize(self, document_paths: List[str]):
        # Upload documents
        file_ids = []
        for path in document_paths:
            file = await self.client.agents.files.upload_and_poll(
                file_path=path,
                purpose=FilePurpose.AGENTS
            )
            file_ids.append(file.id)
        
        # Create vector store
        self.vector_store = await self.client.agents.vector_stores.create_and_poll(
            file_ids=file_ids,
            name="insurance_vector_store"
        )
        
        # Configure search tool
        self.file_search_tool = FileSearchTool(
            vector_store_ids=[self.vector_store.id]
        )
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        return {
            "definitions": self.file_search_tool.definitions,
            "resources": self.file_search_tool.resources,
            "vector_store_id": self.vector_store.id
        }
```

### Semantic Search Implementation

```python
class SemanticSearchEngine:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.search_strategies = {
            "exact_match": ExactMatchStrategy(),
            "semantic_similarity": SemanticSimilarityStrategy(),
            "hybrid_search": HybridSearchStrategy()
        }
    
    async def search(self, query: str, strategy: str = "hybrid_search") -> SearchResults:
        search_strategy = self.search_strategies[strategy]
        return await search_strategy.execute(query, self.vector_store)
    
    async def get_terms_and_conditions(self, policy_type: str) -> str:
        query = f"terms and conditions for {policy_type} insurance policy"
        results = await self.search(query, "semantic_similarity")
        return self.format_terms(results)
```

### Document Processing Pipeline

```
Document Upload → PDF Processing → Text Extraction → Chunking → 
Embedding Generation → Vector Storage → Index Creation → Search Ready
```

## Event-Driven Architecture

The system implements event-driven patterns for asynchronous processing and improved responsiveness.

### Event Flow Architecture

```python
class InsuranceEventBus:
    def __init__(self):
        self.event_handlers = defaultdict(list)
        self.event_queue = asyncio.Queue()
        self.processing_task = None
    
    def subscribe(self, event_type: str, handler: Callable):
        self.event_handlers[event_type].append(handler)
    
    async def publish(self, event: Event):
        await self.event_queue.put(event)
    
    async def process_events(self):
        while True:
            event = await self.event_queue.get()
            handlers = self.event_handlers[event.type]
            
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    await self.handle_event_error(event, handler, e)
```

### Event Types and Handlers

| Event Type | Trigger | Handlers |
|------------|---------|----------|
| **UserInfoCollected** | Complete user data received | QuoteGenerationHandler |
| **QuoteGenerated** | Insurance quote created | DocumentSearchHandler, EmailPrepHandler |
| **DocumentsRetrieved** | Terms found | EmailIntegrationHandler |
| **EmailSent** | Quote delivered | NotificationHandler, AnalyticsHandler |
| **AgentError** | Agent failure | ErrorHandler, RetryHandler |

## Scalability & Performance

### Horizontal Scaling Design

```python
class ScalableAgentManager:
    def __init__(self):
        self.agent_pools = {
            "insurance": AgentPool(max_size=10, min_size=2),
            "document": AgentPool(max_size=5, min_size=1),
            "email": AgentPool(max_size=3, min_size=1)
        }
        self.load_balancer = AgentLoadBalancer()
    
    async def get_agent(self, agent_type: str) -> Agent:
        pool = self.agent_pools[agent_type]
        
        if pool.available_count() == 0:
            await pool.scale_up()
        
        return await pool.acquire_agent()
    
    async def release_agent(self, agent: Agent):
        pool = self.agent_pools[agent.type]
        await pool.release_agent(agent)
        
        if pool.utilization_rate() < 0.3:
            await pool.scale_down()
```

### Performance Optimization Strategies

#### 1. Agent Pooling
```python
class AgentPool:
    def __init__(self, max_size: int, min_size: int):
        self.max_size = max_size
        self.min_size = min_size
        self.available_agents = asyncio.Queue(maxsize=max_size)
        self.active_agents = set()
        self.warmup_task = None
    
    async def warmup(self):
        """Pre-create minimum number of agents"""
        for _ in range(self.min_size):
            agent = await self.create_agent()
            await self.available_agents.put(agent)
```

#### 2. Caching Strategy
```python
class ResponseCache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
    
    async def get_cached_quote(self, user_hash: str) -> Optional[Quote]:
        if user_hash in self.cache:
            entry = self.cache[user_hash]
            if time.time() - entry.timestamp < self.ttl:
                return entry.quote
        return None
    
    async def cache_quote(self, user_hash: str, quote: Quote):
        self.cache[user_hash] = CacheEntry(quote, time.time())
```

#### 3. Async Processing
```python
async def process_concurrent_requests(requests: List[Request]):
    semaphore = asyncio.Semaphore(10)  # Limit concurrent processing
    
    async def process_single_request(request: Request):
        async with semaphore:
            return await connected_agent(request.query)
    
    tasks = [process_single_request(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if not isinstance(r, Exception)]
```

## Deployment Architecture

### Container-Based Deployment

```dockerfile
# Streamlit Application Container
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "stins.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Azure Container Instances Deployment

```yaml
# Azure Container Instance Configuration
apiVersion: '2021-03-01'
location: eastus
name: insurance-assistant
properties:
  containers:
  - name: insurance-app
    properties:
      image: youracr.azurecr.io/insurance-assistant:latest
      ports:
      - port: 8501
        protocol: TCP
      environmentVariables:
      - name: PROJECT_ENDPOINT
        secureValue: '[secure]'
      - name: MODEL_DEPLOYMENT_NAME
        value: 'gpt-4'
      resources:
        requests:
          cpu: 1
          memoryInGB: 2
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 8501
```

### Azure App Service Deployment

```python
# Azure App Service Configuration
class AppServiceConfig:
    def __init__(self):
        self.app_settings = {
            "PROJECT_ENDPOINT": os.environ.get("PROJECT_ENDPOINT"),
            "MODEL_DEPLOYMENT_NAME": os.environ.get("MODEL_DEPLOYMENT_NAME"),
            "AZURE_OPENAI_ENDPOINT": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "WEBSITES_PORT": "8501",
            "SCM_DO_BUILD_DURING_DEPLOYMENT": "true"
        }
    
    def configure_startup(self):
        return "python -m streamlit run stins.py --server.port=$PORT --server.address=0.0.0.0"
```

## Monitoring & Observability

### Application Performance Monitoring

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

class InsuranceAgentTracing:
    def __init__(self):
        # Configure Azure Monitor
        configure_azure_monitor(
            connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
        )
        
        self.tracer = trace.get_tracer(__name__)
        HTTPXClientInstrumentor().instrument()
    
    def trace_agent_operation(self, operation_name: str):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    span.set_attribute("agent.operation", operation_name)
                    span.set_attribute("agent.timestamp", time.time())
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("agent.status", "success")
                        return result
                    except Exception as e:
                        span.set_attribute("agent.status", "error")
                        span.set_attribute("agent.error", str(e))
                        raise
            return wrapper
        return decorator
```

### Custom Metrics Collection

```python
class InsuranceMetrics:
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "quotes_generated": 0,
            "emails_sent": 0,
            "errors_total": 0,
            "response_times": [],
            "agent_utilization": {}
        }
    
    def record_request(self, request_type: str, duration: float):
        self.metrics["requests_total"] += 1
        self.metrics["response_times"].append(duration)
        
        if request_type == "quote_generation":
            self.metrics["quotes_generated"] += 1
    
    def record_error(self, error_type: str, agent_name: str):
        self.metrics["errors_total"] += 1
        
        error_key = f"errors.{error_type}.{agent_name}"
        self.metrics[error_key] = self.metrics.get(error_key, 0) + 1
    
    def get_health_status(self) -> Dict[str, Any]:
        avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        error_rate = self.metrics["errors_total"] / max(self.metrics["requests_total"], 1)
        
        return {
            "status": "healthy" if error_rate < 0.05 else "degraded",
            "metrics": {
                "avg_response_time": avg_response_time,
                "error_rate": error_rate,
                "total_requests": self.metrics["requests_total"]
            }
        }
```

### Health Check Implementation

```python
class HealthCheckService:
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client
        self.health_checks = [
            self.check_azure_ai_foundry_connectivity,
            self.check_vector_store_availability,
            self.check_email_service_connectivity
        ]
    
    async def perform_health_check(self) -> HealthStatus:
        results = []
        
        for check in self.health_checks:
            try:
                result = await check()
                results.append(result)
            except Exception as e:
                results.append(HealthCheckResult(
                    name=check.__name__,
                    status="unhealthy",
                    error=str(e)
                ))
        
        overall_status = "healthy" if all(r.status == "healthy" for r in results) else "unhealthy"
        
        return HealthStatus(
            status=overall_status,
            checks=results,
            timestamp=datetime.utcnow()
        )
```

## Future Architecture Considerations

### Microservices Evolution

```python
# Future microservices architecture
class MicroserviceArchitecture:
    def __init__(self):
        self.services = {
            "agent_orchestrator": AgentOrchestratorService(),
            "quote_generator": QuoteGeneratorService(),
            "document_search": DocumentSearchService(),
            "email_delivery": EmailDeliveryService(),
            "user_management": UserManagementService()
        }
    
    async def deploy_service_mesh(self):
        # Implement service mesh for inter-service communication
        pass
    
    async def implement_api_gateway(self):
        # Central API gateway for external access
        pass
```

### Multi-Tenant Architecture

```python
class MultiTenantInsuranceSystem:
    def __init__(self):
        self.tenant_configurations = {}
        self.tenant_vector_stores = {}
        self.tenant_agents = {}
    
    async def provision_tenant(self, tenant_id: str, config: TenantConfig):
        # Create tenant-specific resources
        vector_store = await self.create_tenant_vector_store(tenant_id, config.documents)
        agents = await self.create_tenant_agents(tenant_id, config.agent_settings)
        
        self.tenant_configurations[tenant_id] = config
        self.tenant_vector_stores[tenant_id] = vector_store
        self.tenant_agents[tenant_id] = agents
    
    async def process_tenant_request(self, tenant_id: str, request: Request):
        tenant_agents = self.tenant_agents[tenant_id]
        return await self.orchestrate_agents(tenant_agents, request)
```

### AI Model Upgrade Strategy

```python
class ModelUpgradeManager:
    def __init__(self):
        self.model_versions = {
            "current": "gpt-4-0613",
            "next": "gpt-4-1106-preview",
            "experimental": "gpt-5-preview"
        }
        self.traffic_split = {
            "current": 80,
            "next": 15,
            "experimental": 5
        }
    
    async def gradual_rollout(self, new_model: str):
        # Implement blue-green deployment for model upgrades
        pass
    
    async def a_b_testing(self, model_a: str, model_b: str, traffic_split: int):
        # A/B testing for model performance comparison
        pass
```

This technical architecture provides a comprehensive foundation for understanding, implementing, and extending the Insurance Quote Assistant system while maintaining scalability, reliability, and performance standards.