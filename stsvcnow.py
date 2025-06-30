import tempfile
import uuid
from openai import AzureOpenAI
import streamlit as st
import asyncio
import io
import os
import time
import json
import soundfile as sf
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List
from scipy.signal import resample
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration (replace with your credentials)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
WHISPER_DEPLOYMENT_NAME = "whisper"
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

class ServiceNowIncidentManager:
    """Manager for ServiceNow incident data and AI interactions."""
    
    def __init__(self, data_file: str = "servicenow_incidents_full.json"):
        self.data_file = data_file
        self.incidents = []
        self.load_data()
    
    def load_data(self):
        """Load ServiceNow incident data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.incidents = data.get('incidents', [])
            st.success(f"✅ Loaded {len(self.incidents)} incidents from {self.data_file}")
        except FileNotFoundError:
            st.error(f"❌ ServiceNow data file {self.data_file} not found")
            self.incidents = []
        except Exception as e:
            st.error(f"❌ Error loading ServiceNow data: {e}")
            self.incidents = []
    
    def search_incidents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search incidents based on query."""
        if not query:
            return self.incidents[:limit]
        
        query_lower = query.lower()
        matching_incidents = []
        
        for incident in self.incidents:
            # Search in various fields
            searchable_text = f"""
            {incident.get('incident_id', '')} 
            {incident.get('short_description', '')} 
            {incident.get('long_description', '')} 
            {incident.get('priority', '')} 
            {incident.get('status', '')}
            {incident.get('solution', '') or ''}
            """.lower()
            
            if query_lower in searchable_text:
                matching_incidents.append(incident)
        
        return matching_incidents[:limit]
    
    def get_incident_context(self, incidents: List[Dict]) -> str:
        """Generate context string from incidents."""
        if not incidents:
            return "No incidents found matching your query."
        
        context = f"Found {len(incidents)} relevant ServiceNow incidents:\n\n"
        
        for i, incident in enumerate(incidents[:5], 1):  # Limit to top 5 for context
            context += f"""
Incident #{i}:
- ID: {incident.get('incident_id', 'N/A')}
- Priority: {incident.get('priority', 'N/A')}
- Status: {incident.get('status', 'N/A')}
- Description: {incident.get('short_description', 'N/A')}
- Details: {incident.get('long_description', 'N/A')[:200]}...
- Solution: {incident.get('solution', 'No solution yet') or 'No solution yet'}
- Start Time: {incident.get('start_time', 'N/A')}
"""
            
            # Add interactions if available
            interactions = incident.get('interactions', [])
            if interactions:
                context += f"- Recent Interactions: {len(interactions)} interactions\n"
                for interaction in interactions[:2]:  # Show recent interactions
                    context += f"  * {interaction.get('user', 'Unknown')}: {interaction.get('comment', '')[:100]}...\n"
            
            context += "\n"
        
        return context

def transcribe_audio(audio_data) -> str:
    """Transcribe audio using Azure OpenAI Whisper."""
    try:
        # Convert audio data to the format expected by Whisper
        audio_file = io.BytesIO(audio_data.getvalue())
        audio_file.name = "audio.wav"
        
        transcript = client.audio.transcriptions.create(
            model=WHISPER_DEPLOYMENT_NAME,
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        st.error(f"❌ Audio transcription failed: {e}")
        return ""

def generate_response(user_query: str, context: str, conversation_history: List[Dict]) -> str:
    """Generate AI response using Azure OpenAI with ServiceNow context."""
    try:
        # Build conversation messages
        messages = [
            {
                "role": "system",
                "content": f"""You are a ServiceNow IT Service Management expert assistant. 
                Use the following ServiceNow incident data to help users with their queries:

                {context}

                Instructions:
                - Provide helpful, accurate information about ServiceNow incidents
                - When discussing incidents, reference specific incident IDs when relevant
                - Suggest solutions based on similar resolved incidents
                - Be conversational and helpful
                - If asked about trends, analyze the data provided
                - Format responses clearly with bullet points or numbered lists when appropriate
                - Keep responses concise and clear for both text and audio playback
                """
            }
        ]
        
        # Add conversation history (last 6 messages for context)
        for msg in conversation_history[-6:]:
            messages.append(msg)
        
        # Add current user query
        messages.append({"role": "user", "content": user_query})
        
        response = client.chat.completions.create(
            model=CHAT_DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        st.error(f"❌ AI response generation failed: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
def generate_response_file(user_query: str, context: str, conversation_history: List[Dict]) -> str:
    """Generate AI response using Azure OpenAI with ServiceNow context."""
    returntxt = ""
    try:
        
        # Build conversation messages
        messages = [
            {
                "role": "system",
                "content": f"""You are a ServiceNow IT Service Management expert assistant. 
                Use the following ServiceNow incident data to help users with their queries:

                {context}

                Instructions:
                - Provide helpful, accurate information about ServiceNow incidents
                - When discussing incidents, reference specific incident IDs when relevant
                - Suggest solutions based on similar resolved incidents
                - Be conversational and helpful
                - If asked about trends, analyze the data provided
                - Format responses clearly with bullet points or numbered lists when appropriate
                - Keep responses concise and clear for both text and audio playback
                """
            }
        ]
        
        # Add conversation history (last 6 messages for context)
        for msg in conversation_history[-6:]:
            messages.append(msg)
        
        # Add current user query
        messages.append({"role": "user", "content": user_query})
        
        # response = client.chat.completions.create(
        #     model=CHAT_DEPLOYMENT_NAME,
        #     messages=messages,
        #     max_tokens=1500,
        #     temperature=0.7
        # )
        # Define the project endpoint
        project_endpoint = os.environ["PROJECT_ENDPOINT"]  # Ensure the PROJECT_ENDPOINT environment variable is set

        # Initialize the AIProjectClient
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),  # Use Azure Default Credential for authentication
            # api_version="latest",
        )
        # Define the path to the file to be uploaded
        file_path = "./servicenow_incidents_full.json"

        # Upload the file
        file = project_client.agents.files.upload_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
        print(f"Uploaded file, file ID: {file.id}")

        vector_store = project_client.agents.vector_stores.create_and_poll(file_ids=[file.id], name="svcnowstore")
        print(f"Created vector store, vector store ID: {vector_store.id}")
        # Create a file search tool
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])

        # Create an agent with the file search tool
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
            name="svcnow-agent",  # Name of the agent
            instructions="You are a helpful agent and can search information from uploaded files",  # Instructions for the agent
            tools=file_search.definitions,  # Tools available to the agent
            tool_resources=file_search.resources,  # Resources for the tools
        )
        print(f"Created agent, ID: {agent.id}")
        # Create a thread
        thread = project_client.agents.threads.create()
        print(f"Created thread, ID: {thread.id}")

        # Send a message to the thread
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=messages,  # Message content
            instructions="You are a helpful agent and can search information from uploaded files",  # Instructions for the agent
        )
        print(f"Created message, ID: {message['id']}")
        # Create and process an agent run in the thread
        run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Cleanup resources
        project_client.agents.vector_stores.delete(vector_store.id)
        print("Deleted vector store")

        project_client.agents.files.delete(file.id)
        print("Deleted file")

        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages from the thread
        # messages = project_client.agents.messages.list(thread_id=thread.id)
        # for message in messages.data:
        #     print(f"Role: {message.role}, Content: {message.content}")
        #     returntxt += message.content.strip()
        messages = project_client.agents.messages.list(thread_id=thread.id)
        for message in messages:
            if message.role == MessageRole.AGENT:
                print(f"Role: {message.role}, Content: {message.content}")
                # returntxt += f"Role: {message.role}, Content: {message.content}\n"
                # returntxt += f"Source: {message.content[0]['text']['value']}\n"
                returntxt += f"Source: {message.content[0].text.value}\n"

        
        return returntxt #response.choices[0].message.content.strip()
    
    except Exception as e:
        st.error(f"❌ AI response generation failed: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
def ai_search_agent(query: str) -> str:
    returntxt = ""

    # Retrieve the endpoint from environment variables
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    # https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/azure-ai-search-samples?pivots=python

    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        # api_version="latest",
    )
    # Define the Azure AI Search connection ID and index name
    azure_ai_conn_id = "vecdb"
    index_name = "svcindex"

    # Initialize the Azure AI Search tool
    ai_search = AzureAISearchTool(
        index_connection_id=azure_ai_conn_id,
        index_name=index_name,
        query_type=AzureAISearchQueryType.SIMPLE,  # Use SIMPLE query type
        top_k=5,  # Retrieve the top 3 results
        filter="",  # Optional filter for search results
        # vector_search_profile="my-vector-profile",  # Use the default vector search profile
    )
    # Define the model deployment name
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    # Create an agent with the Azure AI Search tool
    agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="Svcnow-agent",
        instructions="You are a helpful agent",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
    print(f"Created agent, ID: {agent.id}")
    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Send a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=query,
    )
    print(f"Created message, ID: {message['id']}")

    # Create and process a run with the specified thread and agent
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch and log all messages in the thread
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    print(str(messages))
    # for message in messages.data:
    #     print(f"Role: {message.role}, Content: {message.content}")
    #     returntxt += f"Role: {message.role}, Content: {message.content}\n"
    for page in messages.by_page():
        for item in page:
            # print(item)
            #returntxt += f"Role: {item.role}, Content: {item.content[0]['text']['value']}\n"
            returntxt = f"{item.content[0]['text']['value']}\n"

    # Delete the agent
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
    

    return returntxt

def generate_audio_response(text: str) -> Optional[bytes]:
    """Generate professional audio from text using Azure OpenAI TTS with human-like persona."""
    try:
        # Clean and optimize text for professional TTS
        clean_text = text.replace('*', '').replace('#', '').replace('`', '')
        clean_text = clean_text.replace('- ', '• ').replace('  ', ' ').strip()
        
        # Add natural pauses and professional tone
        clean_text = clean_text.replace('.', '. ').replace(':', ': ').replace(';', '; ')
        clean_text = clean_text.replace('  ', ' ')  # Remove double spaces
        
        # Limit text length for optimal TTS quality
        if len(clean_text) > 3000:
            clean_text = clean_text[:3000] + "... I can provide more details if needed."
        
        # Add professional greeting context for better voice tone
        if not clean_text.lower().startswith(('hello', 'hi', 'good', 'welcome')):
            clean_text = f"Here's what I found: {clean_text}"
        
        # Use the TTS model with professional voice settings
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",  # Use high-definition TTS model for better quality
            voice="nova",      # Professional, clear female voice (alternatives: alloy, echo, fable, onyx, shimmer)
            input=clean_text,
            response_format="mp3",
            speed=0.9          # Slightly slower for clarity and professionalism
        )
        
        return response.content
    
    except Exception as e:
        st.error(f"❌ Professional audio generation failed: {e}")
        # Try fallback with basic model
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=clean_text[:1000] if 'clean_text' in locals() else "I apologize, but I'm having trouble generating audio right now.",
                response_format="mp3"
            )
            return response.content
        except:
            return None
        
def generate_audio_response_gpt_1(text, selected_voice):
    """Generate audio response using gTTS."""
    # tts = gTTS(text=text, lang="en")
    url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/deployments/gpt-4o-mini-tts/audio/speech?api-version=2025-03-01-preview"  
  
    headers = {  
        "Content-Type": "application/json",  
        "Authorization": f"Bearer {os.environ['AZURE_OPENAI_KEY']}"  
    }  

    prompt = f"""can you make this content as short and sweet rather than reading the text and make it personally to user to listen to it.
    Keep in conversation and with out confirming to user about the story telling.
    Also make the content few sentences long and make it more practical to user.
    {text}"""

    audioclient = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2025-03-01-preview"
    )

    # speech_file_path = Path(__file__).parent / "speech.mp3"
    temp_file = os.path.join(tempfile.gettempdir(), f"response_{uuid.uuid4()}.mp3")

    with audioclient.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=selected_voice.lower(), #"coral",
        input=text,
        instructions="Speak in a cheerful and positive tone. Can you make this content as story telling rather than reading the text and make it personally to user to listen to it.",
    ) as response:
        response
        response.stream_to_file(temp_file)

    return temp_file

def process_audio_input(audio_data, incident_manager: ServiceNowIncidentManager, conversation_history: List[Dict]) -> tuple[str, str]:
    """Process audio input and generate response."""
    # Transcribe audio
    transcription = transcribe_audio(audio_data)
    if not transcription:
        return "", "Failed to transcribe audio"
    
    # Search for relevant incidents
    incidents = incident_manager.search_incidents(transcription)
    context = incident_manager.get_incident_context(incidents)
    
    # Generate AI response
    # response = generate_response(transcription, context, conversation_history)
    # response = generate_response_file(transcription, context, conversation_history)
    response = ai_search_agent(transcription)
    
    return transcription, response

def process_text_input(user_input: str, incident_manager: ServiceNowIncidentManager, conversation_history: List[Dict], selected_voice) -> tuple[str, Optional[bytes]]:
    """Process text input and generate both text and audio response."""
    # Search for relevant incidents
    incidents = incident_manager.search_incidents(user_input)
    context = incident_manager.get_incident_context(incidents)
    
    # Generate AI response
    # response = generate_response(user_input, context, conversation_history)
    # response = generate_response_file(user_input, context, conversation_history)
    response = ai_search_agent(user_input)
    
    # Generate audio response with better error handling
    audio_response = None
    if st.session_state.get('audio_enabled', False):
        try:
            audio_response = generate_audio_response_gpt_1(response, selected_voice=selected_voice)  # Use a professional voice
        except Exception as e:
            st.warning(f"⚠️ Could not generate audio: {str(e)}")
            audio_response = None
    
    return response, audio_response

def main():
    """Main Streamlit application for ServiceNow Incident Management."""
    
    st.set_page_config(
        page_title="ServiceNow AI Assistant",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Material Design 3 CSS styling
    st.markdown("""
    <style>
        /* Material Design 3 Light Color Scheme */
        :root {
            --md-sys-color-primary: #1976D2;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #D4E4FF;
            --md-sys-color-on-primary-container: #001B3A;
            --md-sys-color-secondary: #4A5568;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-secondary-container: #E2E8F0;
            --md-sys-color-on-secondary-container: #1A202C;
            --md-sys-color-tertiary: #00897B;
            --md-sys-color-on-tertiary: #FFFFFF;
            --md-sys-color-tertiary-container: #B2DFDB;
            --md-sys-color-on-tertiary-container: #004D40;
            --md-sys-color-surface: #FAFAFA;
            --md-sys-color-on-surface: #1A1A1A;
            --md-sys-color-surface-variant: #F5F5F5;
            --md-sys-color-on-surface-variant: #424242;
            --md-sys-color-surface-container: #F8F9FA;
            --md-sys-color-surface-container-high: #E8EAED;
            --md-sys-color-outline: #757575;
            --md-sys-color-outline-variant: #BDBDBD;
            --md-sys-color-success: #2E7D32;
            --md-sys-color-warning: #F57C00;
            --md-sys-color-error: #D32F2F;
        }

        /* Global app styling */
        .stApp {
            background: linear-gradient(135deg, var(--md-sys-color-surface) 0%, var(--md-sys-color-primary-container) 100%);
            color: var(--md-sys-color-on-surface);
        }

        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-tertiary) 100%);
            padding: 1rem 1.5rem; /* Reduced vertical padding */
            border-radius: 16px;   /* Slightly smaller border radius */
            margin-bottom: 1.2rem; /* Slightly less margin below */
            box-shadow: 0 6px 20px rgba(25, 118, 210, 0.15);
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        }

        .main-header h1 {
            color: var(--md-sys-color-on-primary);
            font-size: 2.1rem; /* Slightly smaller font */
            font-weight: 600;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }

        .main-header p {
            color: var(--md-sys-color-on-primary);
            font-size: 1rem;
            margin: 0.3rem 0 0 0;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        /* Card styling */
        .feature-card {
            background: var(--md-sys-color-surface);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
            border: 1px solid var(--md-sys-color-outline-variant);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .feature-card h4, .feature-card h6 {
            margin-bottom: 0.5rem !important;
        }

        .feature-card p {
            margin-bottom: 0.5rem !important;
        }

        .feature-card:hover {
            box-shadow: 0 3px 12px rgba(25, 118, 210, 0.10);
            transform: translateY(-2px);
        }

        /* Reduce margin for input sections */
        .section-header {
            margin: 1rem 0 0.5rem 0;
            font-size: 1.2rem;
        }

        /* Chat history container: make it fill the right column and always scrollable */
        .chat-history-container {
            height: 70vh;
            max-height: 70vh;
            min-height: 350px;
            overflow-y: auto;
            overflow-x: hidden;
            background: var(--md-sys-color-surface-container);
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            border: 1px solid var(--md-sys-color-outline-variant);
            scroll-behavior: smooth;
        }
        
        .chat-history-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-history-container::-webkit-scrollbar-track {
            background: var(--md-sys-color-surface-variant);
            border-radius: 10px;
        }
        
        .chat-history-container::-webkit-scrollbar-thumb {
            background: var(--md-sys-color-primary);
            border-radius: 10px;
            opacity: 0.7;
        }
        
        .chat-history-container::-webkit-scrollbar-thumb:hover {
            background: var(--md-sys-color-primary);
            opacity: 1;
        }

        .chat-empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--md-sys-color-on-surface-variant);
            font-style: italic;
        }
        
        .chat-empty-state::before {
            content: "🛠️";
            display: block;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        /* Audio player styling */
        .audio-container {
            margin: 0.5rem 0 1rem 0;
            padding: 1rem;
            background: linear-gradient(135deg, var(--md-sys-color-tertiary-container) 0%, #E8F5E8 100%);
            border-radius: 16px;
            max-width: 85%;
            border: 1px solid var(--md-sys-color-tertiary);
            box-shadow: 0 2px 12px rgba(0, 137, 123, 0.15);
            position: relative;
            animation: fadeIn 0.3s ease-out;
        }
        
        .audio-container::before {
            content: "🎵 Professional Voice Response";
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--md-sys-color-on-tertiary-container);
            display: block;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--md-sys-color-outline-variant);
        }
        
        /* Enhanced audio element styling */
        audio {
            width: 100%;
            height: 40px;
            outline: none;
            border-radius: 8px;
            background: var(--md-sys-color-surface);
        }
        
        audio::-webkit-media-controls-panel {
            background-color: var(--md-sys-color-surface);
            border-radius: 8px;
            border: 1px solid var(--md-sys-color-outline-variant);
        }
        
        audio::-webkit-media-controls-play-button {
            background-color: var(--md-sys-color-primary);
            border-radius: 50%;
            margin-left: 8px;
        }
        
        audio::-webkit-media-controls-current-time-display,
        audio::-webkit-media-controls-time-remaining-display {
            color: var(--md-sys-color-on-surface);
            font-size: 0.875rem;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ ServiceNow AI Assistant</h1>
        <p>Intelligent IT Service Management with Voice & Chat Interface</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize ServiceNow incident manager
    if 'incident_manager' not in st.session_state:
        st.session_state.incident_manager = ServiceNowIncidentManager()
    
    # Initialize conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Initialize search results
    if 'last_search_results' not in st.session_state:
        st.session_state.last_search_results = []
    
    # Initialize audio responses storage
    if 'audio_responses' not in st.session_state:
        st.session_state.audio_responses = {}
    
    # Initialize audio settings
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True
    
    # Sidebar with statistics and controls
    with st.sidebar:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">📊 ServiceNow Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Display incident statistics
        incidents = st.session_state.incident_manager.incidents
        if incidents:
            total_incidents = len(incidents)
            high_priority = len([i for i in incidents if i.get('priority') == 'High'])
            resolved = len([i for i in incidents if i.get('status') == 'Resolved'])
            
            st.markdown(f"""
            <div class="feature-card">
                <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">Incident Statistics</h6>
                <div style="margin-bottom: 0.5rem;">
                    <span class="status-info">📊 Total: {total_incidents}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span class="status-success">✅ Resolved: {resolved}</span>
                </div>
                <div>
                    <span class="status-info">🔥 High Priority: {high_priority}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse', 'nova']
        
        selected_voice = st.selectbox(
            "🗣️ Choose AI Voice", 
            voices, 
            help="Select the voice personality for your AI assistant"
        )
        
        # Quick Actions
        st.markdown('<div class="section-header">🎯 Quick Actions</div>', unsafe_allow_html=True)
        
        # Audio settings
        st.markdown("""
        <div class="feature-card">
            <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">🔊 Professional Audio</h6>
            <p style="font-size: 0.85rem; color: var(--md-sys-color-on-surface-variant); margin: 0;">
                High-quality voice responses with human-like persona
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        audio_enabled = st.checkbox("🎤 Enable Voice Responses", value=st.session_state.audio_enabled, help="Toggle professional audio playback of AI responses")
        if audio_enabled != st.session_state.audio_enabled:
            st.session_state.audio_enabled = audio_enabled
            if audio_enabled:
                st.success("🔊 Professional voice responses enabled!")
            else:
                st.info("🔇 Voice responses disabled")
            st.rerun()
        
        st.divider()
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.session_state.last_search_results = []
            st.session_state.audio_responses = {}
            st.success("Conversation cleared!")
            st.rerun()
        
        # Reload data button
        if st.button("🔄 Reload Data"):
            st.session_state.incident_manager.load_data()
            st.rerun()
    
    # Main content area - Left: Input, Right: Chat History
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="section-header">💭 Ask Questions</div>', unsafe_allow_html=True)
        
        # Text input interface
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">💬 Text Input</h4>
        </div>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input(
            "Type your question:",
            placeholder="e.g., 'Show me high priority incidents' or 'How to resolve access denied errors?'",
            key="text_input"
        )
        
        col_send, col_examples = st.columns([1, 1])
        with col_send:
            send_button = st.button("🚀 Send Message", type="primary")
        with col_examples:
            if st.button("💡 Examples"):
                st.info("""
                **Example Questions:**
                - "Show me all high priority incidents"
                - "What are the most common Copilot issues?"
                - "How was INC0000001 resolved?"
                - "Find incidents related to access denied"
                """)
        
        # Voice input section
        st.markdown("""
        <div class="feature-card" style="margin-top: 1.5rem;">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🎤 Voice Input</h4>
            <p style="color: var(--md-sys-color-on-surface-variant); margin-bottom: 1rem;">
                Record your question about ServiceNow incidents.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        audio_data = st.audio_input("🎤 Record your question")
        
        if audio_data:
            col_process, col_clear = st.columns([2, 1])
            with col_process:
                process_audio = st.button("🎯 Process Audio", type="primary")
            with col_clear:
                if st.button("🗑️ Clear Audio"):
                    st.rerun()
        
        # Display current search results in left column
        if st.session_state.last_search_results:
            st.markdown('<div class="section-header">🔍 Latest Search</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="feature-card">
                <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">
                    Found {len(st.session_state.last_search_results)} incidents
                </h6>
            </div>
            """, unsafe_allow_html=True)
            
            # Show top 3 results in compact format
            for i, incident in enumerate(st.session_state.last_search_results[:3]):
                priority_color = {
                    'High': 'var(--md-sys-color-error)',
                    'Medium': 'var(--md-sys-color-warning)',
                    'Low': 'var(--md-sys-color-success)'
                }.get(incident.get('priority', 'Medium'), 'var(--md-sys-color-primary)')
                
                st.markdown(f"""
                <div style="background: var(--md-sys-color-surface-variant); 
                           border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
                           border-left: 4px solid {priority_color};">
                    <h6 style="color: {priority_color}; margin: 0 0 0.25rem 0; font-size: 0.9rem;">
                        {incident.get('incident_id', 'N/A')} - {incident.get('priority', 'N/A')}
                    </h6>
                    <p style="font-size: 0.8rem; margin: 0; color: var(--md-sys-color-on-surface-variant);">
                        {incident.get('short_description', 'No description')[:80]}...
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Processing logic for text input
        if send_button and user_input:
            with st.spinner("🤖 Processing your request and generating professional response...", show_time=True):
                # Process text input and generate response with audio
                response, audio_response = process_text_input(
                    user_input, 
                    st.session_state.incident_manager, 
                    st.session_state.conversation_history,
                    selected_voice
                )
                
                # Add to conversation history
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                st.session_state.conversation_history.append({"role": "assistant", "content": response})
                
                # Store audio response if generated and audio is enabled
                if audio_response and st.session_state.audio_enabled:
                    response_id = len(st.session_state.conversation_history) - 1
                    st.session_state.audio_responses[response_id] = audio_response
                    st.success("✅ Response ready with professional voice!")
                else:
                    st.success("✅ Response ready!")
                
                # Update search results
                incidents = st.session_state.incident_manager.search_incidents(user_input)
                st.session_state.last_search_results = incidents
                
                st.rerun()
        
        # Processing logic for voice input
        if audio_data and 'process_audio' in locals() and process_audio:
            with st.spinner("🎤 Processing audio and generating professional response...", show_time=True):
                transcription, response = process_audio_input(
                    audio_data, 
                    st.session_state.incident_manager, 
                    st.session_state.conversation_history
                )
                
                if transcription:
                    # Add to conversation history with voice indicator
                    st.session_state.conversation_history.append({"role": "user", "content": f"🎤 {transcription}"})
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Generate audio response for voice input
                    if st.session_state.audio_enabled:
                        with st.spinner("🎵 Generating professional voice response...", show_time=True):
                            audio_response = generate_audio_response_gpt_1(response, selected_voice)
                            if audio_response:
                                response_id = len(st.session_state.conversation_history) - 1
                                st.session_state.audio_responses[response_id] = audio_response
                    
                    # Also update search results
                    incidents = st.session_state.incident_manager.search_incidents(transcription)
                    st.session_state.last_search_results = incidents
                    
                    st.success("✅ Audio processed with professional voice response!")
                    st.rerun()
    
    with col2:
        st.markdown('<div class="section-header">💬 Conversation History</div>', unsafe_allow_html=True)
        
        # Enhanced chat history display (text only, no audio here)
        if st.session_state.conversation_history:
            for i, message in enumerate(st.session_state.conversation_history):
                if message["role"] == "user":
                    content = message['content'].replace('\n', '<br>')
                    if content.startswith('🎤'):
                        content = content[2:].strip()
                        st.markdown(f"<div class='chat-message-user'>🎤 {content}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-message-user'>{content}</div>", unsafe_allow_html=True)
                else:
                    content = message['content'].replace('\n', '<br>')
                    # Render assistant response INSIDE the chat-history-container (text only)
                    st.markdown(f"<div class='chat-message-assistant'>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='chat-empty-state'>
                <strong>Welcome to ServiceNow AI Assistant!</strong><br>
                Ask me about incidents, search for specific issues, or get help with IT service management.<br>
                <small>Use text input or voice recording on the left.</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- Only show audio player for the latest assistant response with audio, directly after chat history ---
        if st.session_state.audio_enabled and st.session_state.conversation_history:
            # Find the last assistant message with audio
            for i in range(len(st.session_state.conversation_history) - 1, -1, -1):
                msg = st.session_state.conversation_history[i]
                if msg["role"] == "assistant" and i in st.session_state.audio_responses:
                    audio_data = st.session_state.audio_responses[i]
                    st.markdown('<div class="audio-container">', unsafe_allow_html=True)
                    st.audio(audio_data, format="audio/mp3", autoplay=False)
                    st.markdown("</div>", unsafe_allow_html=True)
                    break

        # Enhanced auto-scroll script for chat
        st.markdown("""
        <script>
        function scrollChatToBottom() {
            setTimeout(function() {
                var chatContainer = document.querySelector('.chat-history-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    chatContainer.style.scrollBehavior = 'smooth';
                }
            }, 100);
            
            // Additional scroll after potential audio loading
            setTimeout(function() {
                var chatContainer = document.querySelector('.chat-history-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }, 500);
        }
        
        // Call scroll function
        scrollChatToBottom();
        
        // Observer for new content
        const chatContainer = document.querySelector('.chat-history-container');
        if (chatContainer) {
            const observer = new MutationObserver(scrollChatToBottom);
            observer.observe(chatContainer, { childList: true, subtree: true });
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Quick actions at bottom of chat
        st.markdown("""
        <div class="feature-card" style="margin-top: 1rem;">
            <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">⚡ Quick Actions</h6>
        </div>
        """, unsafe_allow_html=True)
        
        col_clear, col_stats = st.columns([1, 1])
        with col_clear:
            if st.button("🗑️ Clear Chat", key="clear_chat_main"):
                st.session_state.conversation_history = []
                st.session_state.last_search_results = []
                st.session_state.audio_responses = {}
                st.success("Chat cleared!")
                st.rerun()
        
        with col_stats:
            if st.button("📊 Show Stats"):
                incidents = st.session_state.incident_manager.incidents
                if incidents:
                    total = len(incidents)
                    high_priority = len([i for i in incidents if i.get('priority') == 'High'])
                    resolved = len([i for i in incidents if i.get('status') == 'Resolved'])
                    st.info(f"📊 **Total:** {total} | ✅ **Resolved:** {resolved} | 🔥 **High Priority:** {high_priority}")

if __name__ == "__main__":
    main()
