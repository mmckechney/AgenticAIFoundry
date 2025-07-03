# ServiceNow AI Assistant - API Documentation

## Table of Contents
1. [Class Reference](#class-reference)
2. [Function Reference](#function-reference)
3. [Configuration Reference](#configuration-reference)
4. [Type Definitions](#type-definitions)
5. [Error Handling](#error-handling)
6. [Usage Examples](#usage-examples)

## Class Reference

### ServiceNowIncidentManager

The core class responsible for managing ServiceNow incident data and coordinating AI interactions.

```python
class ServiceNowIncidentManager:
    """Manager for ServiceNow incident data and AI interactions."""
```

#### Constructor

```python
def __init__(self, data_file: str = "servicenow_incidents_full.json") -> None
```

**Parameters:**
- `data_file` (str): Path to the ServiceNow incidents JSON file. Default: "servicenow_incidents_full.json"

**Description:**
Initializes the ServiceNow incident manager with the specified data file. Automatically loads incident data upon instantiation.

**Example:**
```python
# Use default file
manager = ServiceNowIncidentManager()

# Use custom file
manager = ServiceNowIncidentManager("/path/to/custom_incidents.json")
```

#### Methods

##### load_data()

```python
def load_data(self) -> None
```

**Description:**
Loads ServiceNow incident data from the configured JSON file. Displays success/error messages in the Streamlit interface.

**Raises:**
- `FileNotFoundError`: If the data file doesn't exist
- `JSONDecodeError`: If the file contains invalid JSON
- `Exception`: For other loading errors

**Example:**
```python
manager = ServiceNowIncidentManager()
manager.load_data()  # Reload data from file
```

##### search_incidents()

```python
def search_incidents(self, query: str, limit: int = 10) -> List[Dict]
```

**Parameters:**
- `query` (str): Search query string to match against incident data
- `limit` (int): Maximum number of results to return. Default: 10

**Returns:**
- `List[Dict]`: List of matching incident dictionaries

**Description:**
Searches through incident data using fuzzy text matching across multiple fields including incident ID, descriptions, priority, status, and solution text.

**Search Fields:**
- `incident_id`: Incident identifier
- `short_description`: Brief incident description
- `long_description`: Detailed incident description
- `priority`: Incident priority level
- `status`: Current incident status
- `solution`: Resolution description

**Example:**
```python
# Search for high priority incidents
incidents = manager.search_incidents("high priority network", limit=5)

# Search for specific incident
incidents = manager.search_incidents("INC0000001")

# Broad search
incidents = manager.search_incidents("Copilot access denied")
```

##### get_incident_context()

```python
def get_incident_context(self, incidents: List[Dict]) -> str
```

**Parameters:**
- `incidents` (List[Dict]): List of incident dictionaries to process

**Returns:**
- `str`: Formatted context string for AI processing

**Description:**
Generates a structured context string from incident data for use by AI agents. Includes incident details, interactions, and metadata formatted for optimal AI comprehension.

**Output Format:**
```
Found {count} relevant ServiceNow incidents:

Incident #1:
- ID: INC0000001
- Priority: High
- Status: Open
- Description: Brief description
- Details: Detailed description...
- Solution: Resolution steps
- Start Time: 2024-01-01T10:00:00Z
- Recent Interactions: 3 interactions
  * user1: Latest comment...
  * user2: Previous comment...
```

**Example:**
```python
incidents = manager.search_incidents("database issues")
context = manager.get_incident_context(incidents)
print(context)  # Formatted context for AI processing
```

## Function Reference

### AI Agent Functions

#### ai_search_agent()

```python
def ai_search_agent(query: str) -> str
```

**Parameters:**
- `query` (str): Search query to execute against Azure AI Search

**Returns:**
- `str`: Formatted search results with citations and URLs

**Description:**
Executes intelligent search using Azure AI Search with vector-semantic hybrid capabilities. Creates a specialized search agent, processes the query, and returns formatted results with proper citations.

**Environment Variables Required:**
- `PROJECT_ENDPOINT`: Azure AI Project endpoint URL
- `MODEL_DEPLOYMENT_NAME`: Azure OpenAI model deployment name

**Azure Resources Created:**
- AI Search Agent with vector-semantic hybrid search tool
- Thread for query processing
- Message for user query

**Azure Resources Cleaned:**
- Agent instance
- Thread instance

**Search Configuration:**
- **Connection ID**: "vecdb"
- **Index Name**: "svcindex"
- **Query Type**: Vector-Semantic Hybrid
- **Top K**: 5 results
- **Filter**: None (empty string)

**Example:**
```python
# Basic search
response = ai_search_agent("Show me Copilot authentication issues")

# Complex query
response = ai_search_agent("Network connectivity problems in the last 30 days")

# Solution-focused search
response = ai_search_agent("How to resolve Azure AD synchronization errors")
```

**Response Format:**
```
Search results with citations and source URLs. Results include:
- Relevant content from the search index
- Citation markers with URLs
- Relevance-ranked information
```

#### generate_response_file()

```python
def generate_response_file(user_query: str, context: str, conversation_history: List[Dict]) -> str
```

**Parameters:**
- `user_query` (str): User's question or request
- `context` (str): Contextual information for the query
- `conversation_history` (List[Dict]): Previous conversation messages

**Returns:**
- `str`: AI-generated response based on file content

**Description:**
Processes file-based queries using Azure AI Foundry vector stores. Uploads ServiceNow incident files, creates vector embeddings, and generates responses using file search capabilities.

**Environment Variables Required:**
- `PROJECT_ENDPOINT`: Azure AI Project endpoint URL
- `MODEL_DEPLOYMENT_NAME`: Azure OpenAI model deployment name

**File Processing:**
- **Input File**: "./servicenow_incidents_full.json"
- **Purpose**: FilePurpose.AGENTS
- **Vector Store**: Named "svcnowstore"
- **Search Tool**: FileSearchTool with vector store integration

**Azure Resources Created:**
- File upload to Azure AI Foundry
- Vector store with document embeddings
- File search agent with specialized instructions
- Thread for conversation management
- Message with conversation context

**Azure Resources Cleaned:**
- Vector store
- Uploaded file
- Agent instance
- Thread instance

**Agent Instructions:**
```
"You are a helpful agent and can search information from uploaded files"
```

**Example:**
```python
# Document analysis
response = generate_response_file(
    user_query="What are the common causes of Copilot failures?",
    context="ServiceNow incident analysis",
    conversation_history=[
        {"role": "user", "content": "Tell me about recent issues"},
        {"role": "assistant", "content": "I found several recent issues..."}
    ]
)

# Solution extraction
response = generate_response_file(
    user_query="How was incident INC123456 resolved?",
    context="Looking for resolution details",
    conversation_history=[]
)
```

#### sendemail()

```python
def sendemail(query: str) -> str
```

**Parameters:**
- `query` (str): Email request containing recipient and content instructions

**Returns:**
- `str`: Email processing status and confirmation

**Description:**
Processes email requests using Azure AI Foundry Connected Agent functionality. Uses a pre-configured agent to handle email composition and sending.

**Environment Variables Required:**
- `PROJECT_ENDPOINT`: Azure AI Project endpoint URL

**Agent Configuration:**
- **Agent ID**: "asst_g3hRNabXnYHg3mzqBxvgDRG6" (pre-configured email agent)
- **Thread**: Created for each email request
- **Message Role**: User

**Azure Resources Created:**
- Thread for email processing
- Message with email request

**Azure Resources Cleaned:**
- Thread instance (automatic cleanup)

**Query Format Examples:**
```python
# Basic email
query = "Send email to admin@company.com with subject 'Daily Report'"

# Detailed email
query = """
Send an email to team@company.com with:
Subject: Incident Summary Report
Body: Summary of today's high priority incidents with resolution status
"""

# Multiple recipients
query = "Send incident update to manager@company.com and team-lead@company.com"
```

**Example:**
```python
# Send incident summary
email_query = """
Send email to admin@company.com with subject 'High Priority Incidents' 
containing a summary of all open high priority incidents
"""
result = sendemail(email_query)
print(result)  # Email status confirmation
```

### Audio Processing Functions

#### transcribe_audio()

```python
def transcribe_audio(audio_data) -> str
```

**Parameters:**
- `audio_data`: Audio input data from Streamlit audio input widget

**Returns:**
- `str`: Transcribed text from the audio input

**Description:**
Transcribes audio input using Azure OpenAI Whisper model. Converts audio data to the format expected by the Whisper API and returns the transcribed text.

**Azure Service Used:**
- **Model**: "whisper" (configured in WHISPER_DEPLOYMENT_NAME)
- **API**: Azure OpenAI Audio Transcriptions

**Audio Processing:**
- Converts audio data to BytesIO format
- Sets filename as "audio.wav" for API compatibility
- Uses Azure OpenAI Whisper transcription service

**Error Handling:**
- Displays error messages in Streamlit interface
- Returns empty string on transcription failure

**Example:**
```python
# In Streamlit application
audio_data = st.audio_input("Record your question")
if audio_data:
    transcription = transcribe_audio(audio_data)
    if transcription:
        st.write(f"You said: {transcription}")
        # Process transcribed text
        response = ai_search_agent(transcription)
```

#### generate_audio_response()

```python
def generate_audio_response(text: str) -> Optional[bytes]
```

**Parameters:**
- `text` (str): Text to convert to speech

**Returns:**
- `Optional[bytes]`: Audio content in MP3 format, or None if generation fails

**Description:**
Generates professional audio responses using Azure OpenAI TTS with optimized settings for clarity and professionalism.

**Audio Configuration:**
- **Model**: "gpt-4o-mini-tts" (high-definition TTS)
- **Voice**: "nova" (professional, clear female voice)
- **Format**: MP3
- **Speed**: 0.9 (slightly slower for clarity)

**Text Processing:**
- Removes markdown formatting (`*`, `#`, `` ` ``)
- Adds natural pauses for better speech flow
- Limits text length to 3000 characters for optimal quality
- Adds professional greeting context if needed

**Fallback Strategy:**
- Primary: High-definition TTS model
- Fallback: Basic "tts-1" model with limited text length

**Example:**
```python
# Generate professional audio
response_text = "Here are the high priority incidents for today..."
audio_content = generate_audio_response(response_text)

if audio_content:
    st.audio(audio_content, format="audio/mp3")
else:
    st.warning("Could not generate audio response")
```

#### generate_audio_response_gpt_1()

```python
def generate_audio_response_gpt_1(text: str, selected_voice: str) -> str
```

**Parameters:**
- `text` (str): Text content to convert to speech
- `selected_voice` (str): Voice persona to use for synthesis

**Returns:**
- `str`: Path to generated temporary audio file

**Description:**
Advanced TTS generation with streaming capabilities and voice persona selection. Creates temporary audio files with professional audio quality optimization.

**Supported Voices:**
- "alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "nova"

**Audio Configuration:**
- **Model**: "gpt-4o-mini-tts"
- **API Version**: "2025-03-01-preview"
- **Streaming**: Yes (with streaming response)
- **Instructions**: Optimized for conversational tone

**File Management:**
- Creates temporary files in system temp directory
- Unique filenames using UUID to prevent conflicts
- Returns file path for Streamlit audio playback

**Advanced Features:**
- Streaming audio generation for real-time processing
- Voice persona customization
- Professional tone optimization
- Conversational instruction enhancement

**Example:**
```python
# Generate audio with specific voice
response_text = "Welcome to the ServiceNow AI Assistant..."
audio_file = generate_audio_response_gpt_1(response_text, "nova")

# Play in Streamlit
st.audio(audio_file, format="audio/mp3")

# Use different voice
audio_file_coral = generate_audio_response_gpt_1(response_text, "coral")
```

### Utility Functions

#### process_audio_input()

```python
def process_audio_input(
    audio_data, 
    incident_manager: ServiceNowIncidentManager, 
    conversation_history: List[Dict]
) -> tuple[str, str]
```

**Parameters:**
- `audio_data`: Audio input from Streamlit widget
- `incident_manager`: ServiceNowIncidentManager instance
- `conversation_history`: List of previous conversation messages

**Returns:**
- `tuple[str, str]`: (transcription, AI response)

**Description:**
Complete audio processing pipeline that transcribes audio input, searches for relevant incidents, and generates AI responses.

**Processing Steps:**
1. Transcribe audio using Whisper
2. Search incidents based on transcription
3. Generate context from found incidents
4. Generate AI response using search agent

**Example:**
```python
audio_data = st.audio_input("Ask about incidents")
if audio_data:
    transcription, response = process_audio_input(
        audio_data, 
        st.session_state.incident_manager, 
        st.session_state.conversation_history
    )
    
    if transcription:
        st.write(f"You asked: {transcription}")
        st.write(f"AI Response: {response}")
```

#### process_text_input()

```python
def process_text_input(
    user_input: str, 
    incident_manager: ServiceNowIncidentManager, 
    conversation_history: List[Dict], 
    selected_voice: str
) -> tuple[str, Optional[bytes]]
```

**Parameters:**
- `user_input` (str): User's text query
- `incident_manager`: ServiceNowIncidentManager instance
- `conversation_history`: List of previous conversation messages
- `selected_voice` (str): Voice persona for audio response

**Returns:**
- `tuple[str, Optional[bytes]]`: (text response, audio response)

**Description:**
Complete text processing pipeline that handles text queries and optionally generates audio responses.

**Processing Steps:**
1. Search incidents based on user input
2. Generate context from found incidents
3. Generate AI response using search agent
4. Optionally generate audio response if enabled

**Example:**
```python
user_input = "Show me network issues"
response, audio = process_text_input(
    user_input,
    st.session_state.incident_manager,
    st.session_state.conversation_history,
    "nova"
)

st.write(response)
if audio and st.session_state.audio_enabled:
    st.audio(audio, format="audio/mp3")
```

## Configuration Reference

### Environment Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | str | Yes | Azure OpenAI service endpoint | `https://your-openai.openai.azure.com` |
| `AZURE_OPENAI_KEY` | str | Yes | Azure OpenAI API key | `your-api-key-here` |
| `PROJECT_ENDPOINT` | str | Yes | Azure AI Project endpoint | `https://your-project.cognitiveservices.azure.com` |
| `MODEL_DEPLOYMENT_NAME` | str | Yes | Azure OpenAI model deployment | `gpt-4o` |
| `AZURE_OPENAI_DEPLOYMENT` | str | No | Chat model deployment name | `gpt-4o` |
| `SEARCH_ENDPOINT` | str | No | Azure AI Search endpoint | `https://your-search.search.windows.net` |
| `SEARCH_KEY` | str | No | Azure AI Search admin key | `your-search-key` |

### Default Configuration Values

```python
WHISPER_DEPLOYMENT_NAME = "whisper"
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
DEFAULT_DATA_FILE = "servicenow_incidents_full.json"
DEFAULT_VECTOR_STORE_NAME = "svcnowstore"
DEFAULT_SEARCH_INDEX = "svcindex"
DEFAULT_SEARCH_CONNECTION = "vecdb"
```

### Azure AI Search Configuration

```python
# AI Search Tool Configuration
ai_search_config = {
    "index_connection_id": "vecdb",
    "index_name": "svcindex",
    "query_type": "VECTOR_SEMANTIC_HYBRID",
    "top_k": 5,
    "filter": "",
}
```

### TTS Voice Options

```python
AVAILABLE_VOICES = [
    'alloy',    # Neutral, balanced
    'ash',      # Slightly deeper, professional
    'ballad',   # Warm, conversational
    'coral',    # Friendly, energetic
    'echo',     # Clear, authoritative
    'sage',     # Calm, thoughtful
    'shimmer',  # Bright, engaging
    'verse',    # Expressive, dynamic
    'nova'      # Professional, clear (default)
]
```

## Type Definitions

### Data Types

```python
from typing import Dict, List, Optional, Any, Union

# Incident data structure
IncidentDict = Dict[str, Any]
"""
{
    "incident_id": str,
    "short_description": str,
    "long_description": str,
    "priority": str,  # "High" | "Medium" | "Low"
    "status": str,    # "Open" | "In Progress" | "Resolved" | "Closed"
    "solution": Optional[str],
    "start_time": str,  # ISO format datetime
    "interactions": List[InteractionDict]
}
"""

# Interaction data structure
InteractionDict = Dict[str, str]
"""
{
    "user": str,
    "comment": str,
    "timestamp": str  # ISO format datetime
}
"""

# Conversation message structure
ConversationMessage = Dict[str, str]
"""
{
    "role": str,     # "user" | "assistant"
    "content": str   # Message content
}
"""

# Agent response structure
AgentResponse = Dict[str, Any]
"""
{
    "content": str,
    "citations": Optional[List[Dict]],
    "metadata": Optional[Dict[str, Any]]
}
"""
```

### Function Signatures

```python
# Core function type signatures
SearchFunction = Callable[[str], str]
ProcessingFunction = Callable[[str, str, List[Dict]], str]
AudioFunction = Callable[[Any], str]
EmailFunction = Callable[[str], str]

# Manager class type
IncidentManagerType = ServiceNowIncidentManager

# Audio data types
AudioData = Union[bytes, Any]  # Streamlit audio input type
AudioResponse = Optional[bytes]
```

## Error Handling

### Exception Types

```python
class ServiceNowAIError(Exception):
    """Base exception for ServiceNow AI Assistant errors."""
    pass

class AgentExecutionError(ServiceNowAIError):
    """Raised when agent execution fails."""
    pass

class ResourceCleanupError(ServiceNowAIError):
    """Raised when Azure resource cleanup fails."""
    pass

class ConfigurationError(ServiceNowAIError):
    """Raised when configuration is invalid or missing."""
    pass

class DataLoadError(ServiceNowAIError):
    """Raised when incident data loading fails."""
    pass
```

### Error Handling Patterns

#### Graceful Degradation

```python
def robust_agent_execution(agent_function, fallback_response="I apologize, but I'm having trouble processing your request."):
    try:
        return agent_function()
    except Exception as e:
        st.error(f"Agent execution failed: {e}")
        return fallback_response
```

#### Retry with Exponential Backoff

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[[], T], 
    max_retries: int = 3, 
    base_delay: float = 1.0
) -> T:
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
```

#### Resource Cleanup

```python
from contextlib import contextmanager

@contextmanager
def azure_resource_manager(project_client):
    """Context manager for automatic Azure resource cleanup."""
    resources = []
    try:
        yield resources
    finally:
        # Cleanup all tracked resources
        for resource_type, resource_id in resources:
            try:
                if resource_type == "agent":
                    project_client.agents.delete_agent(resource_id)
                elif resource_type == "thread":
                    project_client.agents.threads.delete(resource_id)
                elif resource_type == "vector_store":
                    project_client.agents.vector_stores.delete(resource_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup {resource_type} {resource_id}: {e}")
```

### Common Error Scenarios

#### Authentication Errors
```python
def handle_auth_error():
    """Handle Azure authentication errors."""
    st.error("❌ Authentication failed. Please check your Azure credentials.")
    st.info("Required environment variables:")
    st.code("""
    AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
    AZURE_OPENAI_KEY=your-api-key
    PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com
    """)
```

#### Service Unavailable
```python
def handle_service_unavailable():
    """Handle Azure service unavailability."""
    st.warning("⚠️ Azure AI services are temporarily unavailable.")
    st.info("Please try again in a few moments or contact support if the issue persists.")
```

#### Data Loading Errors
```python
def handle_data_load_error(file_path: str):
    """Handle ServiceNow data loading errors."""
    st.error(f"❌ Failed to load ServiceNow data from {file_path}")
    st.info("Please ensure:")
    st.write("- File exists and is accessible")
    st.write("- File contains valid JSON")
    st.write("- JSON structure matches expected format")
```

## Usage Examples

### Complete Application Integration

```python
import streamlit as st
import os
from typing import Dict, List

def main():
    """Complete ServiceNow AI Assistant application."""
    
    # Initialize session state
    if 'incident_manager' not in st.session_state:
        st.session_state.incident_manager = ServiceNowIncidentManager()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # UI setup
    st.title("🛠️ ServiceNow AI Assistant")
    
    # Input methods
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Text input
        user_input = st.text_input("Ask about incidents:")
        if st.button("Send") and user_input:
            process_user_query(user_input)
        
        # Voice input
        audio_data = st.audio_input("Record question:")
        if audio_data and st.button("Process Audio"):
            process_audio_query(audio_data)
    
    with col2:
        # Display conversation
        display_conversation_history()

def process_user_query(user_input: str):
    """Process text-based user query."""
    try:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": user_input
        })
        
        # Generate AI response
        response = ai_search_agent(user_input)
        
        # Add AI response to history
        st.session_state.conversation_history.append({
            "role": "assistant", 
            "content": response
        })
        
        # Generate audio if enabled
        if st.session_state.get('audio_enabled', False):
            audio_file = generate_audio_response_gpt_1(response, "nova")
            st.audio(audio_file, format="audio/mp3")
            
    except Exception as e:
        st.error(f"Error processing query: {e}")

def process_audio_query(audio_data):
    """Process voice-based user query."""
    try:
        # Transcribe audio
        transcription = transcribe_audio(audio_data)
        if transcription:
            # Process as text query
            process_user_query(f"🎤 {transcription}")
        else:
            st.error("Failed to transcribe audio")
            
    except Exception as e:
        st.error(f"Error processing audio: {e}")

def display_conversation_history():
    """Display conversation history with proper formatting."""
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

if __name__ == "__main__":
    main()
```

### Advanced Agent Orchestration

```python
class MultiAgentOrchestrator:
    """Advanced orchestrator for multi-agent coordination."""
    
    def __init__(self, project_client):
        self.project_client = project_client
        self.active_agents = {}
        
    def execute_parallel_search(self, query: str) -> Dict[str, str]:
        """Execute parallel searches across multiple agents."""
        tasks = [
            ("search", lambda: ai_search_agent(query)),
            ("file", lambda: generate_response_file(query, "", [])),
        ]
        
        results = {}
        for agent_type, task in tasks:
            try:
                results[agent_type] = task()
            except Exception as e:
                results[agent_type] = f"Error: {e}"
        
        return results
    
    def aggregate_responses(self, responses: Dict[str, str]) -> str:
        """Aggregate responses from multiple agents."""
        aggregated = "Based on multiple AI agents:\n\n"
        
        for agent_type, response in responses.items():
            if not response.startswith("Error:"):
                aggregated += f"**{agent_type.title()} Agent:**\n{response}\n\n"
        
        return aggregated

# Usage
orchestrator = MultiAgentOrchestrator(project_client)
results = orchestrator.execute_parallel_search("Copilot authentication issues")
final_response = orchestrator.aggregate_responses(results)
```

---

*This API documentation provides comprehensive reference information for developing with the ServiceNow AI Assistant. For implementation examples and architectural details, refer to the accompanying technical documentation.*