# AgenticAIFoundry

A comprehensive collection of Azure AI Foundry samples demonstrating advanced agentic AI capabilities, evaluation frameworks, and red team testing. This repository showcases the latest Azure AI Foundry platform features for building, evaluating, and securing AI agents.

## ⚠️ Python Version Requirement

**This project requires Python 3.12**. Python 3.13 is not supported due to compatibility issues with the Azure AI SDK dependencies.

## Features

This repository demonstrates the following Azure AI Foundry capabilities:

### 🤖 AI Agents
- **Code Interpreter Agent**: Execute Python code and data analysis tasks with file upload support
- **Connected Agent**: Multi-agent system coordination with:
  - Stock price lookup capabilities
  - Azure AI Search integration for knowledge retrieval
  - Email functionality with custom SMTP configuration
  - Multi-step workflow orchestration
- **AI Search Agent**: Dedicated Azure AI Search integration for construction RFP document search
- **Weather Agent**: Custom function tool integration example with external API calls
- **Multi-Agent Team Framework**: Advanced agent coordination and task delegation with:
  - **AgentTeam Management**: Create, coordinate, and manage teams of specialized agents
  - **Task Delegation**: Automatic task distribution based on agent capabilities
  - **Team Leader Coordination**: Intelligent orchestration of multi-step workflows
  - **Specialized Agent Roles**: TimeWeather, Email, Temperature conversion agents
  - **Collaborative Workflows**: Inter-agent communication and result sharing
- **Agent Management**: Complete agent lifecycle management with creation, monitoring, and cleanup

### 🔍 Evaluation Framework
- **Agent-specific evaluators**: Intent resolution, task adherence, tool call accuracy
- **Quality metrics**: Relevance, coherence, groundedness, fluency, similarity
- **Safety evaluators**: Content safety, hate/unfairness, violence, sexual content, self-harm
- **Advanced metrics**: BLEU, GLEU, ROUGE, METEOR, F1 scores
- **Security evaluators**: Protected material detection, indirect attack detection, code vulnerability assessment
- **Performance metrics**: Response completeness, retrieval accuracy, groundedness pro evaluation

### 🛡️ Red Team Testing
- **Automated red team scanning**: Multi-strategy attack simulation with advanced callback mechanisms
- **Risk category coverage**: Violence, hate/unfairness, sexual content, self-harm
- **Attack strategies**: 
  - Character manipulation and Unicode confusables
  - Encoding techniques (ROT13, Base64, Morse code, binary)
  - Prompt injection and conversation steering
  - Advanced callback-based attacks
- **Comprehensive reporting**: Detailed security assessment with vulnerability scoring
- **Compliance monitoring**: Risk level assessment and mitigation recommendations

### 📊 Reasoning Models
- **Azure OpenAI O1 series integration**: Advanced reasoning capabilities with o4-mini and o3 models
- **High-effort reasoning**: Complex problem-solving scenarios with configurable reasoning effort
- **Professional output formatting**: Enterprise-ready response formatting
- **Latest API support**: Compatible with 2024-12-01-preview API version

### 🌐 Web Application Interface
- **Comprehensive Streamlit dashboard**: Full-featured web interface for all capabilities
- **Multi-tab navigation**: Organized access to agents, evaluation, and testing
- **Real-time progress tracking**: Live feedback during long-running operations
- **File upload support**: Images, audio, video, and document processing
- **Speech input capability**: Voice-to-text integration (configurable)
- **Interactive configuration**: Environment status checking and settings management
- **Debug mode**: Detailed execution information for development and troubleshooting

### 🎤 MCP Servers Integration
- **Voice Chat Interface**: Audio recording and transcription using Azure OpenAI Whisper
- **Multi-Provider MCP Support**: Integration with Microsoft Learn, GitHub Copilot, and HuggingFace MCP servers
- **Real-time Audio Response**: Text-to-speech conversion using Azure OpenAI TTS
- **Interactive MCP Selection**: Dynamic switching between different MCP server providers
- **Conversational AI**: Optimized responses for voice interaction and accessibility

### 🖼️ Computer Vision & Image Analysis
- **Advanced Vision Models**: Dual-model support for Azure GPT-4.1 Vision and O3 models
- **Technical Drawing Analysis**: Specialized processing for engineering and architectural drawings
- **Structured Data Extraction**: Automated extraction of materials, quantities, and dimensions
- **Multi-format Support**: Compatible with JPG, JPEG, PNG image formats
- **JSON Output**: Structured data output for integration with other systems

## 📚 Documentation

For detailed architecture and implementation information, see the comprehensive documentation in the `docs/` directory:

- **[Architecture Blueprint](docs/architecture-blueprint.md)** - Complete system design and architecture overview
- **[Mermaid Architecture Diagrams](docs/mermaid-architecture-diagram.md)** - Interactive visual diagrams showing agent connections and data flows
- **[Technical Diagrams](docs/technical-diagrams.md)** - Detailed ASCII component diagrams
- **[Implementation Guide](docs/implementation-guide.md)** - Agent implementation patterns and examples
- **[Quick Reference](docs/quick-reference.md)** - Quick reference for common tasks
- **[Web Application Guide](WEB_APP_README.md)** - Comprehensive web interface documentation

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
# For O1 models, use the preview API version
# AZURE_API_VERSION=2024-12-01-preview
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

### Optional: Email Configuration (for connected agent email functionality)
```bash
# Google SMTP configuration for email sending
GOOGLE_EMAIL=<your_gmail_address>
GOOGLE_APP_PASSWORD=<your_gmail_app_password>
```

### Optional: MCP Servers Configuration
```bash
# GitHub Personal Access Token for GitHub MCP server
GITHUB_PAT_TOKEN=<your_github_personal_access_token>

# Azure OpenAI TTS deployment (for voice responses)
# Uses gpt-4o-mini-tts model deployment
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

### 🌐 Web Application (Recommended)

Launch the comprehensive Streamlit web interface to interact with all features:

```bash
# Quick start with launch script
chmod +x run_app.sh
./run_app.sh

# Or run directly
streamlit run streamlit_app.py
```

**Web Interface Features:**
- 🏠 **Interactive Dashboard**: Visual overview of all capabilities
- 🎯 **Easy Navigation**: Tab-based interface for all agents and tools
- 📊 **Real-time Progress**: Visual feedback during execution
- 🎤 **Multiple Input Types**: Text, file uploads, speech-to-text
- ⚙️ **Configuration Management**: Environment status and settings
- 📱 **Responsive Design**: Optimized for various screen sizes

Access the application at: **http://localhost:8501**

See [WEB_APP_README.md](WEB_APP_README.md) for detailed web interface documentation.

### 🎤 MCP Servers Application

For voice-enabled MCP (Microsoft Cloud Protocol) server interactions:

```bash
streamlit run bbmcp.py
```

**MCP Features:**
- 🎙️ **Voice Input**: Record questions using your microphone
- 🔊 **Audio Output**: Text-to-speech responses for accessibility
- 🌐 **Multi-Provider Support**: Choose between Microsoft Learn, GitHub Copilot, or HuggingFace MCP servers
- 💬 **Chat History**: Persistent conversation tracking with audio playback
- 🔄 **Real-time Processing**: Live transcription and response generation

**Supported MCP Servers:**
- **Microsoft Learn**: Access Microsoft documentation and learning resources
- **GitHub Copilot**: Leverage GitHub's AI capabilities for code assistance
- **HuggingFace**: Integrate with HuggingFace models and datasets

Access the MCP interface at: **http://localhost:8501**

### 🖼️ Technical Drawing Analysis

For image analysis using advanced vision models:

```bash
streamlit run stdrawing.py
```

**Image Analysis Features:**
- 📸 **Multi-format Support**: Upload JPG, JPEG, PNG images
- 🔍 **Dual Model Analysis**: Choose between Azure GPT-4.1 Vision and O3 models
- 📊 **Technical Extraction**: Extract materials, quantities, and dimensions from technical drawings
- 💾 **JSON Output**: Structured data extraction for further processing
- 🎯 **Custom Questions**: Ask specific questions about uploaded images

Access the analysis interface at: **http://localhost:8501**

### 📋 Command Line Usage

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
# Basic usage
connected_agent_result = connected_agent("What is the stock price of Microsoft")
print(connected_agent_result)

# With email functionality
connected_agent_result = connected_agent("Show me details on Construction management services and email the summary to user@example.com")
print(connected_agent_result)
```

#### 6. AI Search Agent
```python
# Uncomment in main() function
ai_search_result = ai_search_agent("Show me details on Construction management services experience we have done before?")
print(ai_search_result)
```

#### 7. Agent Management
```python
# Load existing agent
result = load_existing_agent("Query for existing agent")
print(result)

# Delete agents (cleanup)
delete_agent()
```

#### 8. Reasoning with O1 Models
```python
# Example usage
query = "Analyze the security implications of this AI system"
result = process_message_reasoning(query)
print(result)
```

#### 9. Multi-Agent Team Coordination
```python
# Run the multi-agent team sample
python sample_agents_multi_agent_team.py

# Example: Create and coordinate a team of specialized agents
from agentutils.agent_team import AgentTeam
from agentutils.user_functions_with_traces import fetch_current_datetime, fetch_weather

# Create agent team
agent_team = AgentTeam("example_team", agents_client=agents_client)

# Add specialized agents
agent_team.add_agent(
    model="gpt-4o-mini",
    name="TimeWeatherAgent",
    instructions="You are specialized for time and weather queries.",
    toolset=time_weather_toolset,
    can_delegate=True
)

# Process complex multi-step requests
agent_team.process_request("Get current time and weather, then email summary")
```

## 🌐 Deployment

### Azure Web App Deployment

Deploy the application to Azure Web App using the provided GitHub Actions workflow:

1. **Setup**: Follow the [Deployment Guide](DEPLOYMENT.md) for complete instructions
2. **Configuration**: Configure Azure Web App with Python 3.12 runtime
3. **Secrets**: Add `AZUREAPPSERVICE_PUBLISHPROFILE` secret to GitHub repository
4. **Environment Variables**: Set required Azure AI service credentials in Azure Web App configuration
5. **Deploy**: Push to main branch or manually trigger the workflow

The application includes automatic environment detection and will run in demo mode if Azure AI dependencies are not fully configured.

For detailed setup instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Project Structure

```
AgenticAIFoundry/
│
├── agenticai.py              # Main application with all agent examples
├── streamlit_app.py          # Web interface for all functionality
├── bbmcp.py                  # MCP Servers voice chat interface
├── stdrawing.py              # Technical drawing analysis with vision models
├── utils.py                  # Utility functions (email sending, etc.)
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── WEB_APP_README.md        # Web application documentation
├── run_app.sh               # Web application launcher script
├── .env                     # Environment variables (create from template)
├── .env.example             # Environment variables template
│
├── agentutils/              # Multi-agent framework utilities
│   ├── agent_team.py        # Multi-agent team coordination framework
│   ├── agent_team_config.yaml # Team configuration settings
│   ├── agent_trace_configurator.py # OpenTelemetry tracing setup
│   └── user_functions_with_traces.py # User functions with telemetry
│
├── sample_agents_multi_agent_team.py # Multi-agent team demonstration
│
├── docs/                    # Documentation directory
├──── architecture-blueprint.md     # Architecture design document
├──── technical-diagrams.md         # Technical component diagrams (ASCII)
├──── mermaid-architecture-diagram.md # Interactive mermaid diagrams
├──── implementation-guide.md       # Implementation patterns and examples
├──── quick-reference.md           # Quick reference guide
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
| `connected_agent()` | External service integration with email capabilities | API integration, external data, and email notifications |
| `process_message_reasoning()` | O1 model reasoning | Complex reasoning tasks |
| `send_email()` (utils.py) | Email sending functionality | Automated email notifications and communications |

### MCP Servers Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| `bbmcp.py main()` | Voice-enabled MCP servers interface | Interactive voice chat with multiple MCP providers |
| `msft_generate_chat_response()` | Microsoft Learn MCP integration | Access Microsoft documentation and learning resources |
| `bbgithub_generate_chat_response()` | GitHub Copilot MCP integration | Code assistance and GitHub repository interaction |
| `hf_generate_chat_response()` | HuggingFace MCP integration | Machine learning models and datasets access |
| `transcribe_audio()` | Azure OpenAI Whisper transcription | Voice-to-text conversion |
| `generate_audio_response_gpt()` | Azure OpenAI TTS audio generation | Text-to-speech response creation |

### Technical Drawing Analysis Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| `stdrawing.py main()` | Technical drawing analysis interface | Image analysis with advanced vision models |
| `analyze_with_azure()` | Azure GPT-4.1 Vision analysis | Technical drawing interpretation and data extraction |
| `analyze_with_o3()` | O3 model image analysis | Advanced reasoning for complex technical drawings |
| `image_to_base64()` | Image encoding for API calls | Prepare images for vision model processing |

### Multi-Agent Team Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| `AgentTeam()` | Multi-agent team coordination framework | Complex workflow orchestration |
| `fetch_current_datetime()` | Get current timestamp with formatting | Time-based agent functions |
| `fetch_weather()` | Weather information retrieval | Environmental data for agents |
| `send_email_using_recipient_name()` | Email functionality for agents | Agent-to-user communication |
| `convert_temperature()` | Temperature conversion utility | Unit conversion tasks |
| `AgentTraceConfigurator()` | OpenTelemetry tracing setup | Performance monitoring and debugging |

## Telemetry and Monitoring

The application includes comprehensive observability features for tracking agent performance and system behavior:

### Azure Monitor OpenTelemetry Integration
- Automatic request tracing across all agent operations
- Performance monitoring with detailed metrics collection
- Error tracking and diagnostic information
- Custom span creation for detailed execution analysis

### Agent Team Tracing
- **Multi-Agent Coordination Tracking**: Trace task delegation and inter-agent communication
- **Task Lifecycle Monitoring**: Track individual tasks from creation to completion
- **Team Performance Metrics**: Measure collaboration efficiency and bottlenecks
- **Custom Function Tracing**: Monitor user-defined functions with OpenTelemetry spans

### Tracing Configuration Options
- **Azure Monitor**: Production-ready cloud telemetry with Application Insights
- **Console Tracing**: Development-friendly local trace output
- **Agent-Specific Traces**: Detailed Azure AI Agents instrumentation
- **Flexible Setup**: Interactive configuration based on environment needs

## Utility Functions

The `utils.py` file provides additional functionality:

### Email Integration
- **Gmail SMTP support**: Send emails through Gmail's SMTP server
- **Multiple recipients**: Support for comma-separated email addresses
- **Secure authentication**: Uses Gmail App Password for secure authentication
- **Error handling**: Comprehensive error handling for email delivery

```python
from utils import send_email

# Send an email
result = send_email("recipient@example.com", "Subject", "Email body content")
print(result)  # Returns confirmation message
```

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

5. **Email Functionality Issues**:
   - Verify `GOOGLE_EMAIL` and `GOOGLE_APP_PASSWORD` environment variables are set
   - Use Gmail App Password, not your regular Gmail password
   - Enable 2-factor authentication and generate an App Password in your Google Account settings
   - Ensure less secure app access is enabled (if not using App Password)

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
| Azure OpenAI API (O1 Models) | 2024-12-01-preview | Required for O1 series models |
