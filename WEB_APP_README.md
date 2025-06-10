# AgenticAI Foundry - Web Application

A comprehensive Streamlit web interface showcasing all AI agents, evaluation frameworks, and red team security testing capabilities of the AgenticAI Foundry platform.

## 🚀 Quick Start

### Option 1: Using the Launch Script (Recommended)
```bash
# Make the script executable
chmod +x run_app.sh

# Launch the application
./run_app.sh
```

### Option 2: Direct Streamlit Command
```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run streamlit_app.py
```

The application will be available at: **http://localhost:8501**

## 🌟 Features

### 🏠 Overview Dashboard
- Platform capabilities summary
- Feature highlights with visual cards
- Quick statistics and metrics
- Environment status check

### 💻 Code Interpreter Agent
- Execute Python code and data analysis
- Upload files for processing
- Example code suggestions
- Real-time execution progress

### 🔍 AI Evaluation Framework
- Comprehensive quality metrics evaluation
- Safety and content analysis
- Advanced scoring (BLEU, ROUGE, F1, etc.)
- Configurable evaluation types
- Detailed metric explanations

### 🛡️ Red Team Security Testing
- Multi-strategy attack simulation
- Risk category coverage (Violence, Hate, Sexual, Self-Harm)
- Configurable attack complexity
- Detailed security assessment reports
- Safety compliance monitoring

### 🤖 Agent-Specific Evaluation
- Intent resolution testing
- Task adherence measurement
- Tool call accuracy assessment
- Agent performance metrics

### 🔗 Connected Agents
- Multi-agent system coordination
- Stock price lookup capabilities
- AI search integration
- Email functionality
- Example query suggestions

### 🔎 AI Search Agent
- Azure AI Search integration
- Knowledge base querying
- Construction RFP document search
- Intelligent result ranking

### 🗑️ Agent Management
- Agent lifecycle management
- Thread and conversation cleanup
- Resource monitoring
- Bulk deletion with safety confirmations

## 🎨 User Interface Features

### 📱 Responsive Design
- Wide layout optimizing screen space
- Modern card-based design
- Intuitive navigation with tabs
- Mobile-friendly interface

### 🎤 Input Options
- **Text Input**: Standard text areas for queries
- **File Upload**: Support for images, audio, video, documents
- **Speech Input**: Voice-to-text capability (configurable)
- **Example Queries**: Pre-built suggestions for each feature

### 📊 Progress & Feedback
- Real-time progress bars during execution
- Success/error message notifications
- Debug information (when enabled)
- Clear output formatting

### ⚙️ Configuration
- Environment variable status checking
- Global settings in sidebar
- Feature-specific configuration options
- Debug mode toggle

## 🔧 Configuration

### Environment Variables
The application checks for the following environment variables:

**Required:**
- `PROJECT_ENDPOINT`: Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME`: AI model deployment name
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_KEY`: Azure OpenAI API key

**Optional:**
- `AZURE_SEARCH_ENDPOINT`: For AI search functionality
- `AZURE_SEARCH_KEY`: Search service authentication
- `GOOGLE_EMAIL`: For email functionality
- `GOOGLE_APP_PASSWORD`: Gmail app password

### Demo Mode
If Azure AI dependencies are not available, the application automatically switches to demo mode with simulated responses, allowing you to explore the interface and functionality.

## 🛠️ Technical Details

### Dependencies
- **streamlit**: Web application framework
- **azure-ai-projects**: Azure AI project integration
- **azure-ai-evaluation**: Evaluation frameworks
- **azure-identity**: Authentication
- **python-dotenv**: Environment configuration
- **asyncio**: Asynchronous operations support

### Architecture
- **Modular Design**: Each feature is implemented as a separate function
- **State Management**: Session state for maintaining user data
- **Error Handling**: Graceful degradation and error reporting
- **Async Support**: Proper handling of async operations like red team testing

### Performance Considerations
- Progress indicators for long-running operations
- Efficient state management
- Lazy loading of expensive operations
- Memory-efficient file handling

## 🎯 Usage Tips

### Getting Started
1. Start with the **Overview** tab to understand available features
2. Check the **Environment Status** in the sidebar
3. Enable **Speech Input** if desired
4. Use **Example Queries** to test functionality quickly

### Best Practices
- Use **Debug Mode** during development
- Check environment variables before running evaluations
- Review **Feature Details** in expandable sections
- Clear outputs regularly to maintain performance

### Troubleshooting
- **Missing Dependencies**: App will run in demo mode automatically
- **Environment Issues**: Check sidebar status indicators
- **Performance Issues**: Clear outputs and restart if needed
- **Connection Problems**: Verify Azure credentials and endpoints

## 🔒 Security & Privacy

- Red team testing is conducted in controlled environments
- No sensitive data is stored persistently
- All API communications use secure protocols
- Environment variables are handled securely

## 🚀 Advanced Usage

### Custom Queries
Each agent supports custom queries tailored to your specific use case:

- **Code Interpreter**: Python code execution and analysis
- **Evaluation**: Custom datasets and evaluation criteria  
- **Red Team**: Specific risk categories and attack strategies
- **Connected Agents**: Multi-step workflows with external services

### Integration
The web interface is designed to complement the command-line tools, providing:
- Visual feedback for long-running operations
- Interactive parameter configuration
- Results visualization and export
- Collaborative sharing capabilities

## 📊 Monitoring & Analytics

The application provides insights into:
- Agent execution times and success rates
- Evaluation metric trends
- Security scan results over time
- Resource utilization patterns

---

For more information about the underlying AI capabilities, see the main [README.md](README.md) file.