# Azure Function Agent Integration - API Reference

## Table of Contents
1. [Module Overview](#module-overview)
2. [Functions](#functions)
3. [Helper Functions](#helper-functions)
4. [Configuration](#configuration)
5. [Error Handling](#error-handling)
6. [Usage Examples](#usage-examples)

## Module Overview

The `stazfunctest.py` module provides Azure Function integration capabilities with Azure AI Foundry agents, enabling serverless compute integration with intelligent agent orchestration.

### Key Features
- Azure Function tool integration with AI agents
- Connected agent orchestration patterns
- Queue-based asynchronous messaging
- Comprehensive error handling and resource management
- Environment-based configuration

### Dependencies
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureFunctionStorageQueue, AzureFunctionTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from dotenv import load_dotenv
```

## Functions

### azurefunc_test(query: str) -> str

Basic Azure Function agent integration test implementation.

#### Parameters
- **query** (str): The user query to process through the Azure Function agent

#### Returns
- **str**: The processed response from the Azure Function agent

#### Functionality
1. Creates an `AzureFunctionTool` with input/output queue configuration
2. Initializes an `AIProjectClient` with Azure credentials
3. Creates an AI agent with the function tool attached
4. Processes the query through a communication thread
5. Extracts and returns the agent's response
6. Performs cleanup by deleting the created agent

#### Example Usage
```python
response = azurefunc_test("What is the weather in New York?")
print(response)
```

#### Error Handling
- Validates environment configuration before execution
- Monitors run status and reports failures
- Ensures agent cleanup even on errors

---

### connected_azure_function_agent(query: str) -> str

Advanced connected agent orchestration with Azure Function integration.

#### Parameters
- **query** (str): The user query to process through the connected agent system

#### Returns
- **str**: The processed response from the connected agent orchestration

#### Functionality
1. Creates a specialized Azure Function agent
2. Establishes a connected agent relationship
3. Creates a main orchestrator agent that delegates to the function agent
4. Processes queries through the connected agent pattern
5. Monitors run execution with polling mechanism
6. Handles tool calls and agent interactions
7. Performs comprehensive cleanup of all resources

#### Example Usage
```python
response = connected_azure_function_agent("What would foo say?")
print(response)
```

#### Advanced Features
- **Connected Agent Pattern**: Implements agent delegation and orchestration
- **Run Polling**: Monitors execution status with detailed logging
- **Tool Call Handling**: Processes complex tool interactions
- **Comprehensive Cleanup**: Deletes both agents and threads

## Helper Functions

### _extract_text_from_message(msg) -> str

Safely extracts text content from agent message objects.

#### Parameters
- **msg**: Agent message object (dict or SDK object)

#### Returns
- **str**: Extracted text content or empty string if extraction fails

#### Functionality
```python
def _extract_text_from_message(msg) -> str:
    """Extract text content from an agents message item safely."""
    try:
        content_list = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
        if not content_list:
            return ""
        # content is typically a list of blocks like { 'type': 'text', 'text': { 'value': '...', 'annotations': [] } }
        for block in content_list:
            if isinstance(block, dict) and block.get("type") == "text":
                text_obj = block.get("text")
                if isinstance(text_obj, dict):
                    return str(text_obj.get("value", ""))
                # sometimes SDK may flatten
                if isinstance(text_obj, str):
                    return text_obj
        return ""
    except Exception:
        return ""
```

#### Use Cases
- Parsing agent responses from different SDK versions
- Handling various message content formats
- Providing fallback for message extraction failures

## Configuration

### Environment Variables

#### Required Variables
- **PROJECT_ENDPOINT_ENT**: Azure AI Foundry project endpoint
- **MODEL_DEPLOYMENT_NAME**: The model deployment name to use
- **STORAGE_SERVICE_ENDPOINT**: Azure Storage queue service endpoint

#### Environment Setup
```bash
# Azure AI Foundry Configuration
PROJECT_ENDPOINT_ENT=https://your-project.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=your-model-deployment

# Azure Storage Configuration
STORAGE_SERVICE_ENDPOINT=https://account.queue.core.windows.net
```

### Configuration Validation

The module performs comprehensive configuration validation:

```python
# Storage endpoint validation
storage_service_endpoint = (
    os.getenv("STORAGE_SERVICE_ENDPOINT")
    or os.getenv("STORAGE_SERVICE_ENDPONT")  # fallback to legacy typo
)

if not storage_service_endpoint:
    print("Missing STORAGE_SERVICE_ENDPOINT", file=sys.stderr)
    sys.exit(1)

if not storage_service_endpoint.startswith("https://") or ".queue.core.windows.net" not in storage_service_endpoint:
    print(f"STORAGE_SERVICE_ENDPOINT looks invalid: {storage_service_endpoint}", file=sys.stderr)
    sys.exit(1)
```

### Azure Function Tool Configuration

```python
azure_function_tool = AzureFunctionTool(
    name="foo",  # Tool name identifier
    description="Get answers from the foo bot.",  # Tool purpose description
    parameters={  # JSON schema for tool parameters
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The question to ask."},
            "outputqueueuri": {"type": "string", "description": "The full output queue URI."},
        },
    },
    input_queue=AzureFunctionStorageQueue(  # Input queue configuration
        queue_name="azure-function-foo-input",
        storage_service_endpoint=storage_service_endpoint,
    ),
    output_queue=AzureFunctionStorageQueue(  # Output queue configuration
        queue_name="azure-function-foo-output",
        storage_service_endpoint=storage_service_endpoint,
    ),
)
```

## Error Handling

### Error Categories

#### 1. Configuration Errors
- Missing environment variables
- Invalid storage endpoint format
- Authentication failures

#### 2. Runtime Errors
- Agent creation failures
- Thread creation failures
- Run execution failures

#### 3. Resource Management Errors
- Cleanup failures
- Resource deletion errors

### Error Handling Patterns

```python
# Environment validation
if not storage_service_endpoint:
    print("Missing STORAGE_SERVICE_ENDPOINT", file=sys.stderr)
    sys.exit(1)

# Run status checking
if run.status == "failed":
    print(f"Run failed: {run.last_error}")

# Safe resource cleanup
try:
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
except Exception as e:
    print(f"Error deleting agent: {e}")
```

## Usage Examples

### Basic Function Agent Test

```python
from stazfunctest import azurefunc_test

# Simple query processing
query = "What is the current weather?"
response = azurefunc_test(query)
print(f"Response: {response}")
```

### Connected Agent Orchestration

```python
from stazfunctest import connected_azure_function_agent

# Complex query with function delegation
query = "What would foo say about the weather in New York City?"
response = connected_azure_function_agent(query)
print(f"Connected Agent Response: {response}")
```

### Complete Application Example

```python
import os
from dotenv import load_dotenv
from stazfunctest import azurefunc_test, connected_azure_function_agent

# Load environment configuration
load_dotenv()

def main():
    # Test queries
    queries = [
        "What is the weather today?",
        "What would foo say about machine learning?",
        "How can I get stock prices?"
    ]
    
    print("=== Basic Function Agent Tests ===")
    for query in queries[:1]:  # Test first query only
        try:
            response = azurefunc_test(query)
            print(f"Query: {query}")
            print(f"Response: {response}\n")
        except Exception as e:
            print(f"Error processing query '{query}': {e}\n")
    
    print("=== Connected Agent Tests ===")
    for query in queries[1:]:  # Test remaining queries
        try:
            response = connected_azure_function_agent(query)
            print(f"Query: {query}")
            print(f"Response: {response}\n")
        except Exception as e:
            print(f"Error processing query '{query}': {e}\n")

if __name__ == "__main__":
    main()
```

### Advanced Configuration Example

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureFunctionStorageQueue, AzureFunctionTool

# Custom configuration
def create_custom_function_tool(function_name: str, storage_endpoint: str):
    return AzureFunctionTool(
        name=function_name,
        description=f"Custom {function_name} function integration",
        parameters={
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Function input"},
                "options": {"type": "object", "description": "Additional options"}
            }
        },
        input_queue=AzureFunctionStorageQueue(
            queue_name=f"azure-function-{function_name}-input",
            storage_service_endpoint=storage_endpoint,
        ),
        output_queue=AzureFunctionStorageQueue(
            queue_name=f"azure-function-{function_name}-output",
            storage_service_endpoint=storage_endpoint,
        ),
    )

# Usage
tool = create_custom_function_tool("weather", os.getenv("STORAGE_SERVICE_ENDPOINT"))
```

---

*For implementation details and architecture overview, see the [Technical Architecture](stazfunctest-technical-architecture.md) and [Mermaid Diagrams](stazfunctest-mermaid-diagrams.md) documentation.*