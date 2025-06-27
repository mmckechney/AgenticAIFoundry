# AgenticAI Foundry - app.py Technical Documentation

## Table of Contents
1. [Technical Overview](#technical-overview)
2. [System Requirements](#system-requirements)
3. [Architecture & Design](#architecture--design)
4. [API Documentation](#api-documentation)
5. [Implementation Details](#implementation-details)
6. [Configuration Management](#configuration-management)
7. [Performance & Optimization](#performance--optimization)
8. [Security Implementation](#security-implementation)
9. [Testing Strategy](#testing-strategy)
10. [Troubleshooting](#troubleshooting)
11. [Development Guidelines](#development-guidelines)

## Technical Overview

The `app.py` file is the primary user interface for the AgenticAI Foundry platform, built using Streamlit framework. It provides a comprehensive web-based interface for AI agent development, evaluation, and management.

### Key Technical Features
- **Framework**: Streamlit 1.x compatible
- **UI Design**: Material Design 3 implementation
- **Architecture**: Modular component-based design
- **Backend Integration**: RESTful service integration
- **Real-time Processing**: Asynchronous operation support
- **Audio Processing**: Voice-to-text and text-to-voice capabilities
- **Session Management**: Stateful user interactions
- **Error Handling**: Graceful degradation and fallback mechanisms

## System Requirements

### Software Dependencies

#### Core Dependencies
```python
# Primary Framework
streamlit >= 1.28.0

# Standard Libraries
asyncio          # Asynchronous operations
io              # Input/output operations
os              # Operating system interface
time            # Time-related functions
datetime        # Date and time handling
typing          # Type hints support
```

#### Backend Integration Dependencies
```python
# AgenticAI Foundry Backend
agenticai       # Core AI agent functionality
bbmcp          # Model Context Protocol interface

# Optional Dependencies (graceful fallback if missing)
azure-openai    # Azure OpenAI API client
requests        # HTTP client library
numpy          # Numerical computations
pandas         # Data manipulation
```

#### Audio Processing Dependencies
```python
# Audio handling
wave           # WAV file processing
pydub          # Audio format conversion
soundfile      # Audio file I/O
base64         # Binary data encoding
```

### Environment Variables

#### Required Configuration
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-api-key"
MODEL_DEPLOYMENT_NAME="your-gpt4-deployment"
WHISPER_DEPLOYMENT_NAME="your-whisper-deployment"
TTS_DEPLOYMENT_NAME="your-tts-deployment"

# MCP Server Configuration
GITHUB_PAT_TOKEN="your-github-personal-access-token"
HUGGINGFACE_API_KEY="your-huggingface-api-key"
```

#### Optional Configuration
```bash
# Performance Tuning
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Debug Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 1 GB free space
- **Network**: Stable internet connection for API calls

#### Recommended Requirements
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Storage**: 5+ GB free space
- **Network**: High-speed internet (>10 Mbps)

## Architecture & Design

### Component Architecture

```python
# Main Application Structure
app.py
├── Configuration & Imports
├── Material Design 3 Styling
├── Session State Management
├── Main UI Controller (main())
├── Phase Managers
│   ├── Development Phase
│   ├── Evaluation Phase
│   ├── Security Testing Phase
│   └── Production Phase
├── Audio Chat Interface
└── Utility Functions
```

### Design Patterns Implemented

#### 1. Model-View-Controller (MVC)
- **Model**: Backend service integration (agenticai.py, bbmcp.py)
- **View**: Streamlit UI components and layouts
- **Controller**: Main UI controller and phase managers

#### 2. Factory Pattern
```python
def create_phase_manager(phase_type: str):
    """Factory pattern for phase manager creation"""
    if phase_type == "development":
        return DevelopmentPhaseManager()
    elif phase_type == "evaluation":
        return EvaluationPhaseManager()
    # ... other phases
```

#### 3. Observer Pattern
```python
# Session state changes trigger UI updates
if "workflow_state" in st.session_state:
    update_ui_based_on_state(st.session_state.workflow_state)
```

#### 4. Strategy Pattern
```python
# Different execution strategies based on dependency availability
if DEPENDENCIES_AVAILABLE:
    strategy = ProductionExecutionStrategy()
else:
    strategy = DemoExecutionStrategy()
```

## API Documentation

### Core Functions

#### main()
```python
def main() -> None:
    """
    Main application entry point.
    
    Initializes session state, renders UI components,
    and handles user interactions.
    
    Returns:
        None
    
    Raises:
        StreamlitError: If UI rendering fails
        ImportError: If critical dependencies missing
    """
```

#### mcp_audio_chat_interface()
```python
def mcp_audio_chat_interface() -> None:
    """
    Renders the MCP audio chat interface.
    
    Handles voice input, speech-to-text conversion,
    MCP server communication, and audio response generation.
    
    Returns:
        None
    
    Raises:
        AudioProcessingError: If audio conversion fails
        MCPConnectionError: If MCP server unavailable
    """
```

### Backend Integration APIs

#### agenticai.py Integration
```python
# Function signatures and usage
from agenticai import (
    code_interpreter,              # Execute code interpretation
    eval as ai_eval,              # Perform AI evaluation
    redteam,                      # Execute red team testing
    agent_eval,                   # Evaluate agent performance
    connected_agent,              # Connect to external agents
    ai_search_agent,              # Search functionality
    delete_agent,                 # Agent cleanup
    process_message_reasoning     # Reasoning operations
)

# Usage examples
result = code_interpreter()
evaluation = ai_eval()
security_report = redteam()
```

#### bbmcp.py Integration
```python
# MCP server communication functions
from bbmcp import (
    msft_generate_chat_response,     # Microsoft Learn integration
    bbgithub_generate_chat_response, # GitHub API integration
    hf_generate_chat_response        # HuggingFace integration
)

# Usage examples
response, metadata = msft_generate_chat_response(query, context)
github_data, _ = bbgithub_generate_chat_response(query, "")
hf_result, _ = hf_generate_chat_response(query, "")
```

### Session State API

#### State Variables
```python
# Critical session state variables
session_state = {
    "show_mcp_chat": bool,          # Audio chat visibility toggle
    "mcp_messages": List[Dict],     # Conversation history
    "workflow_state": Dict,         # Current workflow status
    "user_preferences": Dict,       # UI customization settings
    "last_operation": str,          # Last executed operation
    "error_count": int,             # Error tracking
    "demo_mode": bool              # Demo mode indicator
}
```

#### State Management Functions
```python
def initialize_session_state():
    """Initialize default session state values"""
    if "show_mcp_chat" not in st.session_state:
        st.session_state.show_mcp_chat = False
    if "mcp_messages" not in st.session_state:
        st.session_state.mcp_messages = []

def update_workflow_state(phase: str, status: str):
    """Update workflow state for tracking progress"""
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = {}
    st.session_state.workflow_state[phase] = status
```

## Implementation Details

### UI Component Implementation

#### Material Design 3 Styling
```python
# CSS Variable Definition
MD3_COLORS = {
    "--md-sys-color-primary": "#6750A4",
    "--md-sys-color-on-primary": "#FFFFFF",
    "--md-sys-color-primary-container": "#EADDFF",
    "--md-sys-color-on-primary-container": "#21005D",
    # ... additional color definitions
}

# Dynamic CSS generation
def generate_md3_css():
    """Generate Material Design 3 CSS styling"""
    return f"""
    <style>
    :root {{
        {'; '.join([f'{k}: {v}' for k, v in MD3_COLORS.items()])}
    }}
    /* Component styles */
    .feature-card {{
        background: var(--md-sys-color-surface);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    </style>
    """
```

#### Responsive Layout System
```python
# Column-based layout implementation
def create_responsive_layout():
    """Create responsive two-column layout"""
    col1, col2 = st.columns([2, 1])  # 2:1 ratio
    
    with col1:
        render_main_content()
    
    with col2:
        render_sidebar_content()
```

#### Dynamic Component Rendering
```python
# Phase-based component rendering
def render_phase_expander(phase_name: str, phase_config: Dict):
    """Render expandable phase section"""
    with st.expander(f"{phase_config['icon']} {phase_name}", 
                     expanded=phase_config.get('expanded', False)):
        for component in phase_config['components']:
            render_component(component)
```

### Audio Processing Implementation

#### Audio File Handling
```python
def process_audio_upload(uploaded_file):
    """
    Process uploaded audio file for speech recognition
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Path to processed audio file
        
    Raises:
        AudioProcessingError: If conversion fails
    """
    # Save uploaded file
    temp_path = f"/tmp/audio_input_{int(time.time())}.wav"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Convert to required format (PCM 16kHz mono)
    processed_path = convert_audio_format(temp_path)
    return processed_path

def convert_audio_format(input_path: str) -> str:
    """Convert audio to PCM 16kHz mono format"""
    try:
        from pydub import AudioSegment
        
        # Load audio file
        audio = AudioSegment.from_wav(input_path)
        
        # Convert to mono, 16kHz
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # Export as PCM WAV
        output_path = input_path.replace('.wav', '_processed.wav')
        audio.export(output_path, format="wav", codec="pcm_s16le")
        
        return output_path
    except Exception as e:
        raise AudioProcessingError(f"Audio conversion failed: {e}")
```

#### Speech Processing Integration
```python
async def process_speech_to_text(audio_path: str) -> str:
    """
    Convert speech audio to text using Azure OpenAI Whisper
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        str: Transcribed text
        
    Raises:
        SpeechRecognitionError: If transcription fails
    """
    try:
        # Azure OpenAI Whisper API call
        with open(audio_path, 'rb') as audio_file:
            response = await azure_openai_client.audio.transcriptions.create(
                model=os.getenv("WHISPER_DEPLOYMENT_NAME"),
                file=audio_file,
                response_format="text"
            )
        return response.text
    except Exception as e:
        raise SpeechRecognitionError(f"Speech recognition failed: {e}")

async def process_text_to_speech(text: str) -> str:
    """
    Convert text to speech using Azure OpenAI TTS
    
    Args:
        text: Text to convert to speech
        
    Returns:
        str: Path to generated audio file
        
    Raises:
        TextToSpeechError: If TTS generation fails
    """
    try:
        response = await azure_openai_client.audio.speech.create(
            model=os.getenv("TTS_DEPLOYMENT_NAME"),
            voice="alloy",
            input=text,
            response_format="mp3"
        )
        
        # Save audio response
        output_path = f"/tmp/tts_response_{int(time.time())}.mp3"
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    except Exception as e:
        raise TextToSpeechError(f"Text-to-speech failed: {e}")
```

### Error Handling Implementation

#### Exception Hierarchy
```python
class AgenticAIError(Exception):
    """Base exception for AgenticAI application"""
    pass

class DependencyError(AgenticAIError):
    """Raised when required dependencies are missing"""
    pass

class AudioProcessingError(AgenticAIError):
    """Raised when audio processing fails"""
    pass

class MCPConnectionError(AgenticAIError):
    """Raised when MCP server connection fails"""
    pass

class SpeechRecognitionError(AgenticAIError):
    """Raised when speech recognition fails"""
    pass

class TextToSpeechError(AgenticAIError):
    """Raised when text-to-speech generation fails"""
    pass
```

#### Error Handling Patterns
```python
def safe_execute_with_fallback(operation_func, fallback_func, operation_name: str):
    """
    Execute operation with automatic fallback to demo mode
    
    Args:
        operation_func: Primary operation function
        fallback_func: Fallback demo function
        operation_name: Name for logging/display
        
    Returns:
        Operation result or demo result
    """
    try:
        if DEPENDENCIES_AVAILABLE:
            return operation_func()
        else:
            st.info(f"🎭 Running {operation_name} in demo mode")
            return fallback_func()
    except ImportError as e:
        st.warning(f"⚠️ {operation_name} dependencies missing: {e}")
        return fallback_func()
    except Exception as e:
        st.error(f"❌ {operation_name} failed: {e}")
        if st.checkbox("Show debug info"):
            st.code(traceback.format_exc())
        return fallback_func()
```

## Configuration Management

### Environment Configuration
```python
class Config:
    """Application configuration management"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4")
    WHISPER_DEPLOYMENT = os.getenv("WHISPER_DEPLOYMENT_NAME", "whisper")
    TTS_DEPLOYMENT = os.getenv("TTS_DEPLOYMENT_NAME", "tts-1")
    
    # MCP Server Configuration
    GITHUB_PAT_TOKEN = os.getenv("GITHUB_PAT_TOKEN")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    
    # Application Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "200"))
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "MODEL_DEPLOYMENT_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise DependencyError(f"Missing required environment variables: {missing_vars}")
```

### Streamlit Configuration
```python
# streamlit configuration via .streamlit/config.toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#6750A4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#1C1B1F"
```

## Performance & Optimization

### Streamlit Performance Optimization

#### Caching Strategies
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_static_data():
    """Load and cache static configuration data"""
    return {
        "mcp_servers": ["Microsoft Learn", "GitHub", "HuggingFace"],
        "workflow_phases": ["Development", "Evaluation", "Security", "Production"],
        "ui_themes": ["Light", "Dark", "Auto"]
    }

@st.cache_resource
def initialize_backend_clients():
    """Initialize and cache backend service clients"""
    return {
        "azure_client": create_azure_client(),
        "mcp_client": create_mcp_client()
    }
```

#### State Management Optimization
```python
def optimize_session_state():
    """Optimize session state for performance"""
    # Limit conversation history size
    if "mcp_messages" in st.session_state:
        if len(st.session_state.mcp_messages) > 50:
            st.session_state.mcp_messages = st.session_state.mcp_messages[-25:]
    
    # Clean up temporary data
    temp_keys = [k for k in st.session_state.keys() if k.startswith("temp_")]
    for key in temp_keys:
        if time.time() - st.session_state[key].get("timestamp", 0) > 3600:
            del st.session_state[key]
```

### Resource Management

#### Memory Management
```python
def cleanup_resources():
    """Clean up temporary resources"""
    import gc
    
    # Remove temporary files
    temp_files = glob.glob("/tmp/audio_*")
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
    
    # Force garbage collection
    gc.collect()
```

#### Asynchronous Operations
```python
async def async_operation_manager():
    """Manage asynchronous operations for better performance"""
    tasks = []
    
    # Parallel processing for independent operations
    if st.button("Run Parallel Evaluation"):
        tasks.append(asyncio.create_task(ai_eval_async()))
        tasks.append(asyncio.create_task(agent_eval_async()))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

## Security Implementation

### Input Validation
```python
def validate_user_input(user_input: str, input_type: str) -> bool:
    """
    Validate user input for security
    
    Args:
        user_input: User provided input
        input_type: Type of input (query, file, etc.)
        
    Returns:
        bool: True if input is valid
        
    Raises:
        ValidationError: If input is invalid
    """
    # Basic sanitization
    if not user_input or len(user_input) > 10000:
        raise ValidationError("Input length invalid")
    
    # Check for potential injection attempts
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            raise ValidationError("Potentially dangerous input detected")
    
    return True
```

### File Upload Security
```python
def secure_file_upload(uploaded_file) -> bool:
    """
    Secure file upload validation
    
    Args:
        uploaded_file: Streamlit uploaded file
        
    Returns:
        bool: True if file is safe
    """
    # Check file size
    if uploaded_file.size > 50 * 1024 * 1024:  # 50MB limit
        raise ValidationError("File too large")
    
    # Check file type
    allowed_types = ['audio/wav', 'audio/mp3', 'audio/m4a']
    if uploaded_file.type not in allowed_types:
        raise ValidationError("File type not allowed")
    
    # Check file extension
    allowed_extensions = ['.wav', '.mp3', '.m4a']
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValidationError("File extension not allowed")
    
    return True
```

### API Security
```python
def secure_api_call(api_function, *args, **kwargs):
    """
    Secure wrapper for API calls
    
    Args:
        api_function: Function to call
        *args, **kwargs: Function arguments
        
    Returns:
        API response
    """
    # Rate limiting
    if not check_rate_limit():
        raise SecurityError("Rate limit exceeded")
    
    # API key validation
    if not validate_api_keys():
        raise SecurityError("Invalid API credentials")
    
    # Execute with timeout
    try:
        return asyncio.wait_for(api_function(*args, **kwargs), timeout=30)
    except asyncio.TimeoutError:
        raise SecurityError("API call timeout")
```

## Testing Strategy

### Unit Testing Framework
```python
import unittest
from unittest.mock import patch, MagicMock
import streamlit as st

class TestAppFunctionality(unittest.TestCase):
    """Test suite for app.py functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Streamlit session state
        st.session_state.clear()
        
    def test_session_state_initialization(self):
        """Test session state initialization"""
        main()
        self.assertIn("show_mcp_chat", st.session_state)
        self.assertIn("mcp_messages", st.session_state)
        
    @patch('agenticai.code_interpreter')
    def test_code_interpreter_integration(self, mock_interpreter):
        """Test code interpreter integration"""
        mock_interpreter.return_value = "Test result"
        
        # Simulate button click
        result = safe_execute_with_fallback(
            mock_interpreter, 
            lambda: "Demo result", 
            "Code Interpreter"
        )
        
        self.assertIsNotNone(result)
        
    def test_audio_processing_validation(self):
        """Test audio file validation"""
        # Create mock audio file
        mock_file = MagicMock()
        mock_file.size = 1024 * 1024  # 1MB
        mock_file.type = "audio/wav"
        mock_file.name = "test.wav"
        
        # Should pass validation
        self.assertTrue(secure_file_upload(mock_file))
```

### Integration Testing
```python
class TestIntegration(unittest.TestCase):
    """Integration tests for external services"""
    
    @patch('bbmcp.msft_generate_chat_response')
    def test_mcp_server_integration(self, mock_mcp):
        """Test MCP server integration"""
        mock_mcp.return_value = ("Test response", {})
        
        # Test Microsoft Learn integration
        response, metadata = msft_generate_chat_response("test query", "")
        
        self.assertEqual(response, "Test response")
        mock_mcp.assert_called_once()
```

### Performance Testing
```python
def test_performance_benchmarks():
    """Performance benchmarks for critical operations"""
    import time
    
    # Test UI rendering time
    start_time = time.time()
    main()
    render_time = time.time() - start_time
    
    assert render_time < 2.0, f"UI rendering too slow: {render_time}s"
    
    # Test session state operations
    start_time = time.time()
    for i in range(1000):
        st.session_state[f"test_key_{i}"] = f"test_value_{i}"
    state_time = time.time() - start_time
    
    assert state_time < 1.0, f"Session state operations too slow: {state_time}s"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Dependencies Missing
**Problem**: ImportError when loading agenticai or bbmcp modules
**Solution**:
```python
# Check dependency availability
def diagnose_dependencies():
    """Diagnose missing dependencies"""
    missing_deps = []
    
    try:
        import agenticai
    except ImportError:
        missing_deps.append("agenticai")
    
    try:
        import bbmcp
    except ImportError:
        missing_deps.append("bbmcp")
    
    if missing_deps:
        st.error(f"Missing dependencies: {missing_deps}")
        st.info("Install with: pip install -r requirements.txt")
    else:
        st.success("All dependencies available")
```

#### 2. Audio Processing Errors
**Problem**: Audio upload or processing failures
**Solution**:
```python
def debug_audio_processing(uploaded_file):
    """Debug audio processing issues"""
    try:
        # Check file properties
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size} bytes")
        st.write(f"File type: {uploaded_file.type}")
        
        # Test audio loading
        audio_data = uploaded_file.getbuffer()
        st.write(f"Audio data length: {len(audio_data)}")
        
        # Test format conversion
        temp_path = f"/tmp/debug_audio_{int(time.time())}.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        
        # Attempt conversion
        processed_path = convert_audio_format(temp_path)
        st.success(f"Audio processing successful: {processed_path}")
        
    except Exception as e:
        st.error(f"Audio processing failed: {e}")
        st.code(traceback.format_exc())
```

#### 3. API Connection Issues
**Problem**: Azure OpenAI or MCP server connection failures
**Solution**:
```python
def diagnose_api_connections():
    """Diagnose API connection issues"""
    # Test Azure OpenAI connection
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01"
        )
        
        # Test simple completion
        response = client.chat.completions.create(
            model=os.getenv("MODEL_DEPLOYMENT_NAME"),
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10
        )
        st.success("Azure OpenAI connection successful")
        
    except Exception as e:
        st.error(f"Azure OpenAI connection failed: {e}")
    
    # Test MCP server connections
    mcp_servers = ["Microsoft Learn", "GitHub", "HuggingFace"]
    for server in mcp_servers:
        try:
            if server == "Microsoft Learn":
                response, _ = msft_generate_chat_response("test", "")
            elif server == "GitHub":
                response, _ = bbgithub_generate_chat_response("test", "")
            elif server == "HuggingFace":
                response, _ = hf_generate_chat_response("test", "")
            
            st.success(f"{server} MCP server connection successful")
        except Exception as e:
            st.error(f"{server} MCP server connection failed: {e}")
```

### Debug Mode Implementation
```python
def enable_debug_mode():
    """Enable comprehensive debug mode"""
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        st.sidebar.markdown("## 🐛 Debug Panel")
        
        # Session state inspector
        if st.sidebar.checkbox("Show Session State"):
            st.sidebar.json(dict(st.session_state))
        
        # Performance metrics
        if st.sidebar.checkbox("Show Performance Metrics"):
            show_performance_metrics()
        
        # Error log viewer
        if st.sidebar.checkbox("Show Error Log"):
            show_error_log()
        
        # Configuration viewer
        if st.sidebar.checkbox("Show Configuration"):
            show_configuration()
```

## Development Guidelines

### Code Style and Standards

#### Python Code Standards
```python
# Follow PEP 8 style guidelines
# Use type hints for all functions
def process_user_query(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Process user query with optional context
    
    Args:
        query: User input query
        context: Optional context information
        
    Returns:
        Dict containing response and metadata
        
    Raises:
        ValidationError: If query is invalid
        ProcessingError: If processing fails
    """
    pass

# Use descriptive variable names
user_audio_file_path = "/tmp/user_audio.wav"
mcp_server_response_data = {"response": "...", "metadata": {}}

# Error handling best practices
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    handle_specific_error(e)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    handle_generic_error(e)
```

#### Streamlit Best Practices
```python
# Use session state efficiently
def efficient_state_management():
    """Efficient session state usage"""
    # Initialize once
    if "expensive_data" not in st.session_state:
        st.session_state.expensive_data = load_expensive_data()
    
    # Use cached data
    return st.session_state.expensive_data

# Optimize rerunning
@st.cache_data
def expensive_computation(input_data):
    """Cache expensive computations"""
    return complex_calculation(input_data)

# Use columns for layout
def create_layout():
    """Create efficient column layout"""
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        render_main_content()
    with col2:
        render_sidebar()
    with col3:
        render_controls()
```

### Contributing Guidelines

#### Development Workflow
1. **Setup Development Environment**
   ```bash
   git clone <repository>
   cd AgenticAIFoundry
   pip install -r requirements.txt
   cp .env.example .env  # Configure environment variables
   ```

2. **Testing Before Commit**
   ```bash
   python -m pytest tests/
   python -m flake8 app.py
   python -m mypy app.py
   ```

3. **Documentation Updates**
   - Update docstrings for new functions
   - Update this technical documentation for major changes
   - Update user-facing documentation as needed

#### Code Review Checklist
- [ ] Type hints added for new functions
- [ ] Error handling implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Accessibility considerations

This technical documentation provides comprehensive coverage of the app.py implementation, enabling developers to understand, maintain, and extend the application effectively.