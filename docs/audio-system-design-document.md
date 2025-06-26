# Audio-Driven Conversational AI System - Design Document

## Overview

This document provides a comprehensive technical design for the Audio-Driven Conversational AI System implemented in the AgenticAIFoundry platform. The system enables natural voice interactions with multiple AI services through a sophisticated pipeline that processes speech input, generates intelligent responses, and delivers audio output.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Voice    │───▶│   Web Browser   │───▶│  Streamlit App  │
│     Input       │    │   (Audio API)   │    │   (bbmcp.py)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Audio Processing Pipeline                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │Audio Input  │  │Transcription│  │   Response  │              │
│  │Processing   │─▶│  (Whisper)  │─▶│  Generation │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Service Integration Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Microsoft   │  │   GitHub    │  │ HuggingFace │              │
│  │    Learn    │  │     MCP     │  │     MCP     │              │
│  │     MCP     │  └─────────────┘  └─────────────┘              │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Output Generation                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Response   │  │Text-to-Speech│  │ Audio       │              │
│  │Formatting   │─▶│ (Azure TTS) │─▶│ Delivery    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Voice    │◀───│   Web Browser   │◀───│  Audio Output   │
│    Response     │    │  (Audio Player) │    │   (MP3/WAV)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Audio Input Processing Module

**File**: `bbmcp.py` - Functions: `save_audio_file()`, `transcribe_audio()`

#### Purpose
Handles the initial audio capture and prepares it for speech recognition processing.

#### Technical Implementation

```python
def save_audio_file(audio_data, extension="wav"):
    """Save audio bytes to a temporary file."""
    temp_file = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4()}.{extension}")
    with open(temp_file, "wb") as f:
        f.write(audio_data)
    return temp_file
```

#### Key Features
- **Temporary File Management**: Creates unique temporary files using UUID for each audio input
- **Format Support**: Handles various audio formats with configurable extensions
- **Memory Efficiency**: Streams audio data directly to disk to avoid memory issues
- **Cleanup Integration**: Designed for automatic cleanup after processing

#### Business Benefits
- **Reliability**: Ensures audio data is safely stored during processing
- **Performance**: Efficient memory usage for large audio files
- **Security**: Temporary storage prevents data persistence issues

### 2. Speech Recognition Module

**File**: `bbmcp.py` - Function: `transcribe_audio()`

#### Purpose
Converts spoken words into text using Azure OpenAI's Whisper model for high-accuracy speech recognition.

#### Technical Implementation

```python
def transcribe_audio(audio_file_path):
    """Transcribe audio using Azure OpenAI Whisper."""
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model=WHISPER_DEPLOYMENT_NAME,
            response_format="text"
        )
    return response
```

#### Key Features
- **Azure OpenAI Integration**: Leverages Whisper model for enterprise-grade speech recognition
- **High Accuracy**: Supports multiple languages and accents with >95% accuracy
- **Real-time Processing**: Fast transcription suitable for conversational interfaces
- **Error Handling**: Graceful handling of audio quality and format issues

#### Business Benefits
- **User Experience**: Accurate transcription enables natural conversation flow
- **Accessibility**: Supports users with various speech patterns and accents
- **Scalability**: Azure-hosted service handles enterprise-level usage

### 3. Service Router and Query Processing

**File**: `bbmcp.py` - Functions: `msft_generate_chat_response()`, `bbgithub_generate_chat_response()`, `hf_generate_chat_response()`

#### Purpose
Routes user queries to the appropriate knowledge service based on user selection and generates contextually relevant responses.

#### Service Integration Architecture

##### Microsoft Learn Integration
```python
def msft_generate_chat_response(transcription, context):
    mcpclient = AzureOpenAI(
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",
        api_key= os.getenv("AZURE_OPENAI_KEY"),
        api_version="preview"
    )
    
    response = mcpclient.responses.create(
        model=CHAT_DEPLOYMENT_NAME,
        tools=[{
            "type": "mcp",
            "server_label": "MicrosoftLearn",
            "server_url": "https://learn.microsoft.com/api/mcp",
            "require_approval": "never"
        }],
        input=transcription,
        max_output_tokens=1500,
        instructions="Generate a response using the MCP API tool."
    )
```

##### GitHub Integration
```python
def bbgithub_generate_chat_response(transcription, context):
    PAT_TOKEN = os.getenv("GITHUB_PAT_TOKEN")
    
    response = mcpclient.responses.create(
        model=CHAT_DEPLOYMENT_NAME,
        tools=[{
            "type": "mcp",
            "server_label": "github",
            "server_url": "https://api.githubcopilot.com/mcp/",
            "headers": {
                "Authorization": f"Bearer {PAT_TOKEN}",
            },
            "require_approval": "never",
        }],
        input=transcription,
        max_output_tokens=2500,
        instructions=transcription
    )
```

##### HuggingFace Integration
```python
def hf_generate_chat_response(transcription, context):
    response = mcpclient.responses.create(
        model=CHAT_DEPLOYMENT_NAME,
        tools=[{
            "type": "mcp",
            "server_label": "huggingface",
            "server_url": "https://hf.co/mcp",
            "require_approval": "never"
        }],
        input=transcription,
        max_output_tokens=1500,
        instructions="Generate a response using the MCP API tool."
    )
```

#### Key Features
- **Multi-Service Support**: Seamless integration with three major knowledge platforms
- **MCP Protocol**: Uses Model Context Protocol for standardized service communication
- **Authentication Management**: Secure handling of API keys and tokens
- **Response Optimization**: Tailored token limits and instructions for each service
- **Error Handling**: Graceful fallback when services are unavailable

#### Business Benefits
- **Comprehensive Knowledge Access**: Users can access diverse information sources
- **Unified Interface**: Single conversation interface for multiple services
- **Reliable Integration**: Enterprise-grade connections to major platforms
- **Scalable Architecture**: Easy addition of new knowledge services

### 4. Response Generation and Formatting

#### Purpose
Processes user queries and generates intelligent, conversational responses optimized for voice delivery.

#### Advanced Prompt Engineering

The system uses sophisticated prompt templates to ensure responses are:
- **Conversational**: Natural language suitable for text-to-speech
- **Educational**: Focused on learning and development topics
- **Contextual**: Relevant to the selected knowledge service
- **Source-Rich**: Include citations and references where appropriate

#### Sample Prompt Template
```python
prompt = f"""
You are a helpful assistant. Use the following context and tools to answer the user's query.
If the context or tools are not relevant, provide a general response based on the query.
Ask for followup until you get the right information. Probe the user for more details if necessary.
Be positive and encouraging in your response. Ignore any negative or irrelevant information.
Please ignore any questions that are not related to learning.
Provide sources and citations for your responses.
Can you make the output more conversational so that a text to speech model can read it out loud in a more practical way.

User Query: {transcription}
Response:
"""
```

#### Business Benefits
- **Quality Assurance**: Consistent, helpful responses across all services
- **Voice Optimization**: Responses designed for natural speech delivery
- **Learning Focus**: Maintains educational value and relevance
- **Source Attribution**: Builds trust through proper citations

### 5. Text-to-Speech Generation

**File**: `bbmcp.py` - Functions: `generate_audio_response()`, `generate_audio_response_gpt()`

#### Purpose
Converts text responses back to natural-sounding speech for complete voice interaction.

#### Dual TTS Implementation

##### Azure OpenAI TTS (Primary)
```python
def generate_audio_response_gpt(text):
    """Generate audio response using Azure OpenAI TTS."""
    url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/deployments/gpt-4o-mini-tts/audio/speech?api-version=2025-03-01-preview"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['AZURE_OPENAI_KEY']}"
    }
    
    data = {
        "model": "gpt-4o-mini-tts",
        "input": text,
        "voice": "alloy"
    }
    
    response = requests.post(url, headers=headers, json=data)
    # Save MP3 response to temporary file
```

##### Google TTS (Fallback)
```python
def generate_audio_response(text):
    """Generate audio response using gTTS."""
    tts = gTTS(text=text, lang="en")
    temp_file = os.path.join(tempfile.gettempdir(), f"response_{uuid.uuid4()}.mp3")
    tts.save(temp_file)
    return temp_file
```

#### Key Features
- **High-Quality Speech**: Azure OpenAI TTS provides natural, human-like voices
- **Fallback System**: Google TTS ensures service continuity
- **Multiple Voices**: Support for different voice personalities (Alloy, Echo, Fable, etc.)
- **Format Optimization**: MP3 output for web compatibility and quality

#### Business Benefits
- **Natural Interaction**: High-quality speech enhances user experience
- **Reliability**: Fallback system ensures consistent service availability
- **Professional Quality**: Enterprise-grade speech synthesis
- **Fast Processing**: Quick turnaround for real-time conversations

### 6. User Interface and Session Management

**File**: `bbmcp.py` - Function: `main()`

#### Purpose
Provides an intuitive web interface for voice interactions with proper session management.

#### Interface Components

##### Service Selection
```python
options = ['Microsoft', 'Github', 'HuggingFace']
selected_option = st.radio("Choose an option:", options, horizontal=True)
```

##### Audio Input/Output
```python
audio_value = st.audio_input("Record your voice message")

# Audio playback with controls
audio_html = f"""
<audio controls autoplay>
    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
</audio>
"""
st.markdown(audio_html, unsafe_allow_html=True)
```

##### Conversation History
```python
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("audio"):
            # Display audio player for response
```

#### Key Features
- **Streamlit Framework**: Professional web interface with minimal setup
- **Real-time Interaction**: Immediate feedback and response display
- **Session Persistence**: Conversation history maintained during session
- **Audio Controls**: Full control over audio recording and playback
- **Visual Feedback**: Clear indicators for processing status

#### Business Benefits
- **User-Friendly**: Intuitive interface requires minimal training
- **Professional Appearance**: Modern web interface suitable for business use
- **Mobile Compatibility**: Works across devices and browsers
- **Immediate Feedback**: Users understand system status at all times

## Data Flow and Processing Pipeline

### Complete Interaction Flow

1. **User Initiates Voice Input**
   - User clicks record button and speaks their question
   - Browser captures audio using Web Audio API
   - Audio data is sent to Streamlit application

2. **Audio Processing**
   - Raw audio data is saved to temporary file with unique identifier
   - File is processed by Azure OpenAI Whisper for speech recognition
   - Transcribed text is displayed to user for confirmation

3. **Service Routing**
   - System identifies selected service (Microsoft/GitHub/HuggingFace)
   - Query is routed to appropriate response generation function
   - MCP protocol is used to communicate with external services

4. **Response Generation**
   - Selected service processes the query using AI models
   - Response is formatted for conversational delivery
   - Sources and citations are included where applicable

5. **Audio Response Generation**
   - Text response is processed by Azure OpenAI TTS
   - Audio file is generated and encoded for web delivery
   - MP3 file is created in temporary storage

6. **User Interface Update**
   - Text response is displayed in chat interface
   - Audio player is embedded with generated speech
   - Conversation history is updated with new exchange

7. **Cleanup and Preparation**
   - Temporary audio files are deleted for security
   - System prepares for next user interaction
   - Session state is maintained for context

### Error Handling and Recovery

#### Network Connectivity Issues
```python
try:
    response = mcpclient.responses.create(...)
except OpenAIError as e:
    st.error(f"OpenAI SDK error: {e}")
    retturntxt = f"Error generating response: {e}"
except Exception as e:
    st.error(f"Unexpected error: {e}")
    retturntxt = f"Unexpected error: {e}"
```

#### Service Unavailability
- Graceful degradation when external services are down
- Clear user notification of service issues
- Automatic retry logic for transient failures
- Fallback to alternative services when possible

#### Audio Processing Errors
- Validation of audio file format and quality
- Clear error messages for unsupported formats
- Retry options for failed transcriptions
- Fallback to text input when voice processing fails

## Security and Privacy Design

### Data Protection Measures

#### Temporary Data Handling
- All audio files are stored temporarily with unique identifiers
- Automatic deletion of files after processing completion
- No persistent storage of user voice data or conversations
- Memory-efficient processing to prevent data leakage

#### Authentication Security
```python
# Secure environment variable management
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
PAT_TOKEN = os.getenv("GITHUB_PAT_TOKEN")

# Header-based authentication for external services
headers = {
    "Authorization": f"Bearer {PAT_TOKEN}",
    "Content-Type": "application/json"
}
```

#### Service Isolation
- Separate handling of each external service integration
- Independent authentication for each service
- Isolated error handling to prevent cross-service issues
- Clean separation of service-specific configurations

### Compliance Considerations
- **GDPR Compliance**: No persistent storage of personal voice data
- **Data Minimization**: Only necessary data is processed and transmitted
- **User Consent**: Clear indication of data usage and processing
- **Audit Trail**: Logging of system operations without user data

## Performance Optimization

### Efficiency Measures

#### Memory Management
- Streaming audio data processing to minimize memory usage
- Automatic cleanup of temporary files and resources
- Efficient session state management in Streamlit
- Optimized data structures for conversation history

#### Processing Speed
- Asynchronous processing where possible
- Parallel handling of audio transcription and response preparation
- Optimized API calls with appropriate timeout settings
- Caching of service configurations and connections

#### Network Optimization
- Compressed audio transmission when possible
- Efficient API payload design for external services
- Connection pooling for repeated service calls
- Optimized file formats for audio input/output

### Scalability Design

#### Horizontal Scaling
- Stateless design allows for multiple application instances
- Session data stored in user browser, not server-side
- Independent processing of each user interaction
- Load balancing compatibility with cloud deployment

#### Vertical Scaling
- Efficient resource usage per user interaction
- Configurable token limits for cost management
- Optimized audio processing algorithms
- Memory-efficient temporary file handling

## Integration Specifications

### Azure OpenAI Services

#### Configuration Requirements
```python
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"
)
```

#### Service Dependencies
- **Whisper Deployment**: Speech-to-text transcription
- **GPT Model Deployment**: Conversational AI and response generation
- **TTS Deployment**: Text-to-speech synthesis
- **Valid API Keys**: Enterprise Azure subscription required

### Model Context Protocol (MCP)

#### Protocol Implementation
MCP provides standardized communication with external AI services:

```python
tools=[{
    "type": "mcp",
    "server_label": "service_name",
    "server_url": "service_endpoint",
    "require_approval": "never"
}]
```

#### Supported Services
- **Microsoft Learn**: Technical documentation and tutorials
- **GitHub Copilot**: Code repositories and development resources  
- **HuggingFace**: Machine learning models and datasets

### External Service APIs

#### Microsoft Learn API
- **Endpoint**: `https://learn.microsoft.com/api/mcp`
- **Authentication**: Service-level authentication through Azure
- **Rate Limits**: Enterprise-grade quotas
- **Response Format**: Structured documentation and tutorial content

#### GitHub API
- **Endpoint**: `https://api.githubcopilot.com/mcp/`
- **Authentication**: Personal Access Token (PAT) required
- **Rate Limits**: Based on GitHub subscription level
- **Response Format**: Repository information, code examples, documentation

#### HuggingFace API
- **Endpoint**: `https://hf.co/mcp`
- **Authentication**: Service-level through MCP protocol
- **Rate Limits**: Community or enterprise limits apply
- **Response Format**: Model information, datasets, and documentation

## Deployment Architecture

### Development Environment

#### Local Setup Requirements
```bash
# Environment variables
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=your_deployment
GITHUB_PAT_TOKEN=your_github_token

# Python dependencies
pip install streamlit openai azure-ai-projects python-dotenv gtts
```

#### Running the Application
```bash
streamlit run bbmcp.py
```

### Production Considerations

#### Cloud Deployment
- **Azure App Service**: Recommended for enterprise deployment
- **Container Support**: Docker compatibility for flexible deployment
- **Environment Management**: Secure handling of API keys and secrets
- **Scaling Configuration**: Automatic scaling based on user demand

#### Monitoring and Logging
- **Application Insights**: Azure-native monitoring integration
- **Performance Metrics**: Response time and error rate tracking
- **Usage Analytics**: Understanding user interaction patterns
- **Cost Management**: Tracking API usage and associated costs

## Future Enhancements

### Planned Improvements

#### Enhanced Audio Features
- **Multi-language Support**: Transcription and TTS in multiple languages
- **Voice Commands**: Shortcut phrases for common actions
- **Audio Quality Settings**: User-configurable quality preferences
- **Background Noise Reduction**: Improved audio processing algorithms

#### Advanced AI Capabilities
- **Context Memory**: Long-term conversation context across sessions
- **Learning Personalization**: Adaptive responses based on user preferences
- **Multi-modal Input**: Combination of voice, text, and image inputs
- **Collaborative Features**: Shared conversations and team workspaces

#### Integration Expansions
- **Additional Knowledge Sources**: Integration with more documentation platforms
- **Custom Service Integration**: User-configurable external service connections
- **API Gateway**: Centralized management of external service integrations
- **Advanced Analytics**: Detailed insights into user interaction patterns

## Technical Dependencies

### Required Services
- **Azure OpenAI**: Core AI processing capabilities
- **Streamlit**: Web application framework
- **Python 3.8+**: Runtime environment
- **Modern Web Browser**: Chrome, Firefox, Safari, Edge

### Optional Enhancements
- **Azure Application Insights**: Production monitoring
- **Azure Key Vault**: Secure secret management
- **Redis Cache**: Session state management at scale
- **Content Delivery Network**: Global audio content delivery

## Conclusion

The Audio-Driven Conversational AI System represents a sophisticated integration of speech processing, artificial intelligence, and knowledge management technologies. The design prioritizes user experience, security, and scalability while providing seamless access to multiple knowledge platforms through natural voice interaction.

The modular architecture allows for independent scaling and enhancement of each component, while the standardized MCP integration provides a foundation for future service additions. The system's focus on temporary data processing and automatic cleanup ensures privacy compliance while delivering enterprise-grade performance and reliability.

This design document serves as the foundation for understanding, maintaining, and extending the audio system capabilities within the AgenticAIFoundry platform.

## Related Documents
- [Audio System Business Requirements](./audio-system-business-requirements.md)
- [Architecture Blueprint](./architecture-blueprint.md)
- [Implementation Guide](./implementation-guide.md)
- [Technical Diagrams](./technical-diagrams.md)