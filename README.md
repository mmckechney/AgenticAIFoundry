# AgenticAIFoundry

A comprehensive collection of Azure AI Foundry samples demonstrating advanced agentic AI capabilities, evaluation frameworks, and red team testing. This repository showcases the latest Azure AI Foundry platform features for building, evaluating, and securing AI agents.

## ⚠️ Python Version Requirement

**This project requires Python 3.12**. Python 3.13 is not supported due to compatibility issues with the Azure AI SDK dependencies.

## Features

This repository demonstrates the following Azure AI Foundry capabilities:

### 🤖 AI Agents
- **Code Interpreter Agent**: Execute Python code and data analysis tasks
- **Connected Agent**: Integration with external services and APIs
- **AI Search Agent**: Azure AI Search integration for knowledge retrieval
- **Weather Agent**: Custom function tool integration example

### 🔍 Evaluation Framework
- **Agent-specific evaluators**: Intent resolution, task adherence, tool call accuracy
- **Quality metrics**: Relevance, coherence, groundedness, fluency
- **Safety evaluators**: Content safety, hate/unfairness, violence, sexual content, self-harm
- **Advanced metrics**: BLEU, GLEU, ROUGE, METEOR, F1 scores
- **Protected material and indirect attack detection**

### 🛡️ Red Team Testing
- **Automated red team scanning**: Multi-strategy attack simulation
- **Risk category coverage**: Violence, hate/unfairness, sexual content, self-harm
- **Attack strategies**: Character manipulation, encoding techniques, prompt injection
- **Comprehensive reporting**: Detailed security assessment results

### 📊 Reasoning Models
- **Azure OpenAI O1 series integration**: Advanced reasoning capabilities
- **High-effort reasoning**: Complex problem-solving scenarios
- **Professional output formatting**: Enterprise-ready response formatting

## Prerequisites

- **Python 3.12** (Required - Python 3.13 not supported)
- Azure subscription with Azure AI Foundry access
- Azure OpenAI service deployment
- Azure AI Search service (for search agent features)

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Core Azure AI Foundry Configuration
```bash
# Azure AI Foundry Project Configuration
PROJECT_ENDPOINT=https://<account_name>.services.ai.azure.com/api/projects/<project_name>
MODEL_ENDPOINT=https://<account_name>.services.ai.azure.com
MODEL_API_KEY=<your_model_api_key>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Alternative project configuration
AZURE_AI_PROJECT=https://<account_name>.services.ai.azure.com/api/projects/<project_name>
```

### Azure OpenAI Configuration
```bash
# Primary OpenAI endpoint
AZURE_OPENAI_ENDPOINT=https://<account_name>.openai.azure.com/
AZURE_OPENAI_KEY=<your_openai_key>
AZURE_OPENAI_API_KEY=<your_openai_api_key>

# For red team testing (can be same as primary)
AZURE_OPENAI_ENDPOINT_REDTEAM=https://<account_name>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your_deployment_name>

# API Configuration
AZURE_API_VERSION=2024-10-21
```

### Azure Resource Configuration
```bash
# Azure subscription and resource details
AZURE_SUBSCRIPTION_ID=<your_subscription_id>
AZURE_RESOURCE_GROUP=<your_resource_group>
AZURE_PROJECT_NAME=<your_project_name>
```

### Optional: Azure AI Search (for search agent)
```bash
# Azure AI Search configuration
AZURE_SEARCH_ENDPOINT=https://<search_service>.search.windows.net
AZURE_SEARCH_KEY=<your_search_key>
AZURE_SEARCH_INDEX=<your_index_name>
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/balakreshnan/AgenticAIFoundry.git
   cd AgenticAIFoundry
   ```

2. **Ensure Python 3.12 is installed**:
   ```bash
   python --version  # Should show Python 3.12.x
   ```

3. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   # Copy the example and fill in your values
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

## Usage

### Running the Main Application

The main script demonstrates various AI agent capabilities:

```bash
python agenticai.py
```

By default, the script runs the AI Search agent example. You can uncomment other examples in the `main()` function to test different features.

### Individual Feature Examples

#### 1. Code Interpreter Agent
```python
# Uncomment in main() function
code_interpreter()
```

#### 2. AI Evaluation
```python
# Uncomment in main() function
evalrs = eval()
print(evalrs)
```

#### 3. Red Team Testing
```python
# Uncomment in main() function
redteamrs = asyncio.run(redteam())
print(redteamrs)
```

#### 4. Agent Evaluation
```python
# Uncomment in main() function
agent_eval()
```

#### 5. Connected Agent
```python
# Uncomment in main() function
connected_agent_result = connected_agent()
print(connected_agent_result)
```

#### 6. Reasoning with O1 Models
```python
# Example usage
query = "Analyze the security implications of this AI system"
result = process_message_reasoning(query)
print(result)
```

## Project Structure

```
AgenticAIFoundry/
│
├── agenticai.py              # Main application with all agent examples
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── .env                     # Environment variables (create from template)
│
├── Data Files/
├── datarfp.jsonl            # Evaluation dataset
├── datarfpagent.jsonl       # Agent evaluation dataset
├── evaluation_input_data.jsonl # Input data for evaluations
│
└── Output Files/
├── myevalresults.json       # Evaluation results
├── Advanced-Callback-Scan.json # Red team scan results
└── redteam.log              # Red team testing logs
```

## Key Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| `code_interpreter()` | Demonstrates code execution agent | Data analysis, Python code execution |
| `eval()` | Comprehensive AI evaluation framework | Model quality assessment |
| `redteam()` | Red team security testing | Security vulnerability assessment |
| `agent_eval()` | Agent-specific evaluation metrics | Agentic workflow evaluation |
| `ai_search_agent()` | Azure AI Search integration | Knowledge retrieval and search |
| `connected_agent()` | External service integration | API integration and external data |
| `process_message_reasoning()` | O1 model reasoning | Complex reasoning tasks |

## Telemetry and Monitoring

The application includes Azure Monitor OpenTelemetry integration for comprehensive observability:

- Automatic request tracing
- Performance monitoring
- Error tracking
- Custom span creation for detailed analysis

## Security Features

### Red Team Testing Capabilities
- **Multiple attack strategies**: Character manipulation, encoding, prompt injection
- **Risk assessment**: Comprehensive coverage of AI safety categories
- **Automated scanning**: Batch processing of security tests
- **Detailed reporting**: JSON output with security findings

### Content Safety
- **Built-in evaluators**: Violence, hate speech, sexual content detection
- **Protected material scanning**: Copyright and sensitive data detection
- **Indirect attack detection**: Advanced prompt injection identification

## Troubleshooting

### Common Issues

1. **Python 3.13 Compatibility Error**:
   - Solution: Downgrade to Python 3.12. Python 3.13 is not supported.

2. **Authentication Errors**:
   - Verify your Azure credentials and environment variables
   - Ensure your Azure AI Foundry project is properly configured
   - Check that DefaultAzureCredential has access to your resources

3. **Model Deployment Issues**:
   - Verify `MODEL_DEPLOYMENT_NAME` matches your actual deployment
   - Ensure the model is deployed and accessible

4. **Import Errors**:
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

### Environment Validation

To validate your environment setup:

```bash
# Check Python version
python --version

# Verify package installation
python -c "import azure.ai.projects; print('Azure AI Projects installed successfully')"

# Test environment variables
python -c "import os; print('PROJECT_ENDPOINT:', os.getenv('PROJECT_ENDPOINT', 'Not set'))"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with Python 3.12
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in this repository
- Consult the [Azure AI Foundry documentation](https://docs.microsoft.com/azure/ai-foundry/)
- Check the [Azure AI SDK documentation](https://docs.microsoft.com/python/api/overview/azure/ai/)

## Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.12.x | Required - 3.13 not supported |
| Azure AI Projects SDK | Latest | Auto-installed via requirements |
| Azure OpenAI API | 2024-10-21+ | Configurable via environment |
