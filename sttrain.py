import tempfile
import uuid
from openai import AzureOpenAI
import requests
import streamlit as st
import asyncio
import io
import os
import time
import json
import re
import soundfile as sf
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List
from scipy.signal import resample
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import FilePurpose, FileSearchTool
from azure.ai.agents.models import MessageTextContent, ListSortOrder

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

os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
project_endpoint = os.environ["PROJECT_ENDPOINT"]
# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

def msft_generate_chat_response(transcription, context):
    """Generate a chat response using Azure OpenAI with tool calls."""
    returntxt = ""

    prompt = f"""
    You are a helpful assistant. Use the following context and tools to answer the user's query.
    If the context or tools are not relevant, provide a general response based on the query.
    Only respond with the tool call.
    Ask for followup until you get the right information. Probe the user for more details if necessary.
    If the context is not relevant, provide a general response based on the query.
    Be positive and encouraging in your response. Ignore any negative or irrelevant information.
    please ignore any questions that are not related to learning. 
    DOn't get annoyed or frustrated. if user asks probing questions, please politely ignore them.
    Provide sources and citations for your responses.
    Can you make the output more conversational so that a text to speech model can read it out loud it more practical way.
    Please format your response as clean, readable text without HTML tags or div elements.

    User Query:
    {transcription}
    
    Response:
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to the MCP API."},
        {"role": "user", "content": prompt}
    ]

    mcpclient = AzureOpenAI(  
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
        api_key= os.getenv("AZURE_OPENAI_KEY"),
        api_version="preview"
        )

    response = mcpclient.responses.create(
        model=CHAT_DEPLOYMENT_NAME, # replace with your model deployment name 
        tools=[
            {
                "type": "mcp",
                "server_label": "MicrosoftLearn",
                "server_url": "https://learn.microsoft.com/api/mcp",
                "require_approval": "never"
            },
        ],
        input=transcription,
        max_output_tokens= 1500,
        instructions="Generate a response using the MCP API tool. Format the response as clean, readable text without HTML tags.",
    )
    
    # Get the raw response
    raw_response = response.output_text    
    # print(f"Raw Response: {raw_response}")
    print("Got response from MSFT Learn MCP Tools")
    
    # Clean up HTML/div elements and format the response
    cleaned_response = clean_response_text(raw_response)
    # print(f"Cleaned Response: {cleaned_response}")
        
    return cleaned_response

def clean_response_text(text: str) -> str:
    """Clean up response text by removing HTML tags and formatting properly."""
    
    if not text:
        return "I apologize, but I couldn't generate a proper response. Please try asking your question again."
    
    # Remove HTML tags completely
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities
    text = re.sub(r'&lt;.*?&gt;', '', text)
    text = re.sub(r'&[a-zA-Z0-9]+;', '', text)
    
    # Clean markdown artifacts
    text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # Keep bold formatting
    text = re.sub(r'\*(.*?)\*', r'*\1*', text)        # Keep italic formatting
    
    # Format numbered lists properly
    text = re.sub(r'(\d+)\.\s*\*\*([^*]+)\*\*', r'\1. **\2**', text)
    
    # Format bullet points properly
    text = re.sub(r'^\s*-\s+', '• ', text, flags=re.MULTILINE)
    
    # Clean up multiple whitespace but preserve line breaks
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    
    # Clean up spacing around punctuation
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    text = re.sub(r'([,.!?])\s*', r'\1 ', text)
    
    # Ensure proper spacing after colons
    text = re.sub(r':\s*', ': ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # If the text is still problematic or too short, provide a fallback
    if len(text) < 10 or text.count('<') > 0:
        return "I apologize, but I'm having trouble formatting the response properly. Let me try to help you with your question in a different way. Could you please rephrase your question?"
    
    # Ensure the response ends with proper punctuation
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

def msft_learn_mcp_agent(query: str) -> str:
    returntxt = ""

    # Retrieve the endpoint from environment variables
    project_endpoint = os.environ["PROJECT_ENDPOINT_WEST"]
    # https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/azure-ai-search-samples?pivots=python

    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        # api_version="latest",
    )

    with project_client:
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"], 
            name="msftlearnmcp-agent", 
            instructions="You are a helpful assistant. Use the tools provided to answer the user's questions. Be sure to cite your sources.",
            tools= [
                {
                    "type": "mcp",
                    "server_label": "MicrosoftLearn",
                    "server_url": "https://learn.microsoft.com/api/mcp",
                    "require_approval": "never"
                }
            ],
            tool_resources=None
        )
        print(f"Created agent, agent ID: {agent.id}")
        thread = project_client.agents.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = project_client.agents.messages.create(
            thread_id=thread.id, role="user", content="<a question for your MCP server>",
        )
        print(f"Created message, message ID: {message.id}")

        run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
        
        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second
            time.sleep(1)
            run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        if run.status == "failed":
            print(f"Run error: {run.last_error}")

        run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            print(f"Run step: {step.id}, status: {step.status}, type: {step.type}")
            if step.type == "tool_calls":
                print(f"Tool call details:")
                for tool_call in step.step_details.tool_calls:
                    print(json.dumps(tool_call.as_dict(), indent=2))

        messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for data_point in messages:
            last_message_content = data_point.content[-1]
            if isinstance(last_message_content, MessageTextContent):
                print(f"{data_point.role}: {last_message_content.text.value}")
                returntxt += f"{data_point.role}: {last_message_content.text.value}\n"
    project_client.agents.delete_agent(agent.id)
    print(f"Deleted agent, agent ID: {agent.id}")

    return returntxt

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

def generate_audio_response(text: str) -> Optional[bytes]:
    """Generate professional audio from text using Azure OpenAI TTS with human-like persona."""
    try:

        audio_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-06-01"  # Adjust API version as needed
        )
        
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
        response = audio_client.audio.speech.create(
            model="gpt-4o-mini-tts",  # Use high-definition TTS model for better quality
            voice="nova",      # Professional, clear female voice (alternatives: alloy, echo, fable, onyx, shimmer)
            input=clean_text,
            response_format="mp3",
            speed=0.9          # Slightly slower for clarity and professionalism
        )
        
        return response.content
        
    except Exception as e:
        st.error(f"❌ Error generating audio response: {str(e)}")
        return None
    
def generate_audio_response_gpt(text):
    """Generate audio response using Azure OpenAI TTS API directly."""
    try:
        # Clean and optimize text for TTS
        clean_text = text.replace('*', '').replace('#', '').replace('`', '')
        clean_text = clean_text.replace('- ', '• ').replace('  ', ' ').strip()
        
        # Limit text length for optimal TTS quality
        if len(clean_text) > 3000:
            clean_text = clean_text[:3000] + "... I can provide more details if needed."
        
        url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/deployments/gpt-4o-mini-tts/audio/speech?api-version=2025-03-01-preview"  
      
        headers = {  
            "Content-Type": "application/json",  
            "Authorization": f"Bearer {os.environ['AZURE_OPENAI_KEY']}"  
        }  
        
        data = {  
            "model": "gpt-4o-mini-tts",  
            "input": clean_text,  
            "voice": "nova",  # Use consistent professional voice
            "response_format": "mp3",
            "speed": 0.9
        }  
        
        response = requests.post(url, headers=headers, json=data)  
        
        print(f"TTS API Response Status: {response.status_code}")
        
        if response.status_code == 200:  
            # Create a unique temporary file
            temp_file = os.path.join(tempfile.gettempdir(), f"response_{uuid.uuid4()}.mp3")
            
            with open(temp_file, "wb") as f:  
                f.write(response.content)  
            
            print(f"MP3 file saved successfully: {temp_file}")
            return temp_file
        else:  
            print(f"TTS API Error: {response.status_code}\n{response.text}")
            st.error(f"❌ Error generating audio: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error in generate_audio_response_gpt: {str(e)}")
        st.error(f"❌ Error generating audio response: {str(e)}")
        return None

def socratic_type_learning():
    st.set_page_config(
        page_title="Socratic Learning Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional and interactive design
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .learning-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #dee2e6;
    }
    .chat-history-container {
        max-height: 500px;
        overflow-y: auto;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 15px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .chat-history-container::-webkit-scrollbar {
        width: 10px;
    }
    .chat-history-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .chat-history-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    .chat-message {
        margin: 15px 0;
        padding: 15px;
        border-radius: 15px;
        word-wrap: break-word;
        animation: fadeIn 0.5s ease-in;
    }
    .learner-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        margin-left: 0px;
        margin-right: 50px;
    }
    .tutor-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 5px solid #9c27b0;
        margin-left: 50px;
        margin-right: 0px;
    }
    .voice-message {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
    }
    .message-header {
        font-weight: bold;
        color: #333;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .message-content {
        color: #555;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .score-container {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #28a745;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .feedback-container {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #ffc107;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .audio-controls {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #007acc;
        text-align: center;
    }
    .topic-selection {
        background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #ddd;
    }
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 10px;
        margin: 10px 0;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Socratic Learning Assistant</h1>
        <p>Interactive AI-powered learning with voice capabilities and real-time feedback</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'learning_chat_history' not in st.session_state:
        st.session_state.learning_chat_history = []
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    if 'learning_score' not in st.session_state:
        st.session_state.learning_score = {"understanding": 0, "engagement": 0, "progress": 0}
    if 'interaction_count' not in st.session_state:
        st.session_state.interaction_count = 0
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None
    
    # Create layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Topic Selection
        st.markdown('<div class="topic-selection">', unsafe_allow_html=True)
        st.markdown("### 📚 Choose Your Learning Topic")
        
        # Predefined topics or custom input
        topic_options = [
            "Machine Learning Fundamentals",
            "Data Science Concepts",
            "Python Programming",
            "Statistics and Probability",
            "Azure AI Services",
            "Deep Learning",
            "Natural Language Processing",
            "Custom Topic"
        ]
        
        selected_topic = st.selectbox(
            "Select a topic to explore:",
            options=topic_options,
            index=topic_options.index(st.session_state.current_topic) if st.session_state.current_topic in topic_options else 0
        )
        
        if selected_topic == "Custom Topic":
            custom_topic = st.text_input("Enter your custom topic:", value=st.session_state.current_topic if st.session_state.current_topic not in topic_options else "")
            if custom_topic:
                st.session_state.current_topic = custom_topic
        else:
            st.session_state.current_topic = selected_topic
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat History Display
        st.markdown("### 💬 Learning Conversation")
        
        if st.session_state.learning_chat_history:
            # Build the complete chat HTML with all messages inside the scrollable container
            chat_html = '<div class="chat-history-container">'
            
            for i, message in enumerate(st.session_state.learning_chat_history):
                role_icon = "🧑‍🎓" if message["role"] == "learner" else "🤖"
                role_name = "You" if message["role"] == "learner" else "Socratic Tutor"
                message_class = "learner-message" if message["role"] == "learner" else "tutor-message"
                
                if message.get("is_voice", False):
                    message_class += " voice-message"
                    role_icon = "🎤" if message["role"] == "learner" else "🔊"
                
                # Clean the content first to remove any HTML artifacts
                clean_content = clean_response_text(message["content"]) if message["role"] == "tutor" else message["content"]
                
                # Escape content for safe HTML display
                escaped_content = clean_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                # Convert newlines to HTML breaks for proper display
                escaped_content = escaped_content.replace("\n", "<br>")
                
                chat_html += f'''
                <div class="chat-message {message_class}">
                    <div class="message-header">
                        {role_icon} {role_name}{" (Voice)" if message.get("is_voice", False) else ""}
                    </div>
                    <div class="message-content">{escaped_content}</div>
                </div>'''
            
            chat_html += '</div>'
            # Add JavaScript to auto-scroll to bottom
            chat_html += '''
            <script>
            setTimeout(function() {
                var chatContainer = document.querySelector('.chat-history-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }, 100);
            </script>'''
            
            # Display the complete chat as a single HTML block
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="chat-history-container">
                <div style="text-align: center; color: #6c757d; padding: 50px;">
                    <h4>🚀 Ready to start learning!</h4>
                    <p>Ask a question about <strong>{}</strong> to begin your Socratic learning journey.</p>
                </div>
            </div>
            """.format(st.session_state.current_topic), unsafe_allow_html=True)
        
        # Audio Response Player
        if st.session_state.current_audio:
            st.markdown('<div class="audio-controls">', unsafe_allow_html=True)
            st.markdown("#### 🔊 Tutor's Voice Response")
            st.audio(st.session_state.current_audio, format="audio/mp3")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input Methods
        st.markdown("### 💭 Your Learning Input")
        
        # Create tabs for different input methods
        input_tab1, input_tab2 = st.tabs(["💬 Text Input", "🎤 Voice Input"])
        
        with input_tab1:
            # Text input form
            with st.form("text_learning_form"):
                user_question = st.text_area(
                    f"Ask a question about {st.session_state.current_topic}:",
                    placeholder="What would you like to learn about? The AI tutor will guide you through Socratic questioning...",
                    height=100
                )
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    text_submit = st.form_submit_button("🚀 Ask Question", use_container_width=True)
                with col_b:
                    enable_voice_response = st.checkbox("🔊 Generate Voice Response", value=st.session_state.audio_enabled)
                
                if text_submit and user_question.strip():
                    process_learning_interaction(user_question, False, enable_voice_response)
        
        with input_tab2:
            st.markdown('<div class="audio-controls">', unsafe_allow_html=True)
            st.markdown("#### 🎤 Record Your Question")
            
            # Audio input
            audio_input = st.audio_input("Record your question:")
            
            col_c, col_d = st.columns([1, 1])
            with col_c:
                process_voice = st.button("🎤 Process Voice Question", use_container_width=True)
            with col_d:
                voice_response_enabled = st.checkbox("🔊 Voice Response", value=st.session_state.audio_enabled, key="voice_response_check")
            
            if process_voice and audio_input:
                process_voice_learning_interaction(audio_input, voice_response_enabled)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Learning Progress and Scoring
        st.markdown("### 📊 Learning Progress")
        
        if st.session_state.interaction_count > 0:
            # Display scores in an attractive format
            st.markdown('<div class="score-container">', unsafe_allow_html=True)
            
            # Progress metrics
            col_score1, col_score2, col_score3 = st.columns(3)
            
            with col_score1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #28a745; margin: 0;">{st.session_state.learning_score['understanding']}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">Understanding</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_score2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #007acc; margin: 0;">{st.session_state.learning_score['engagement']}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">Engagement</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_score3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #9c27b0; margin: 0;">{st.session_state.learning_score['progress']}</h3>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">Progress</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Overall progress bar
            overall_score = sum(st.session_state.learning_score.values()) / 3
            progress_width = (overall_score / 100) * 100
            
            st.markdown(f"""
            <div style="margin: 15px 0;">
                <h4 style="margin-bottom: 10px;">Overall Learning Score: {overall_score:.1f}/100</h4>
                <div style="background: #e0e0e0; border-radius: 10px; height: 10px;">
                    <div class="progress-bar" style="width: {progress_width}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Personalized Feedback
            if st.session_state.interaction_count >= 3:
                st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
                st.markdown("### 💡 Personalized Feedback")
                
                feedback = generate_learning_feedback(st.session_state.learning_score, st.session_state.interaction_count)
                st.markdown(feedback)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.info("📈 Start learning to see your progress and scores!")
        
        # Learning Statistics
        st.markdown("### 📈 Session Statistics")
        
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("Questions Asked", st.session_state.interaction_count)
        with stats_col2:
            voice_interactions = len([msg for msg in st.session_state.learning_chat_history if msg.get("is_voice", False)])
            st.metric("Voice Interactions", voice_interactions)
        
        # Learning Controls
        st.markdown("### 🛠️ Learning Controls")
        
        if st.button("🔄 Start New Topic", use_container_width=True):
            st.session_state.learning_chat_history = []
            st.session_state.learning_score = {"understanding": 0, "engagement": 0, "progress": 0}
            st.session_state.interaction_count = 0
            st.session_state.current_audio = None
            st.rerun()
        
        if st.button("📄 Export Learning Session", use_container_width=True):
            export_learning_session()
        
        # Audio Settings
        st.markdown("### 🔊 Audio Settings")
        st.session_state.audio_enabled = st.checkbox("Enable Voice Responses", value=st.session_state.audio_enabled)
        
        # Topic Information
        if st.session_state.current_topic:
            with st.expander("ℹ️ About This Topic"):
                topic_info = get_topic_information(st.session_state.current_topic)
                st.markdown(topic_info)

def process_learning_interaction(user_input: str, is_voice: bool = False, enable_audio: bool = True):
    """Process a learning interaction with Socratic questioning."""
    
    with st.spinner("🤔 Tutor is thinking about your question..." if not is_voice else "🎤 Processing your voice question..."):
        try:
            # Add user message to chat history
            st.session_state.learning_chat_history.append({
                "role": "learner",
                "content": user_input,
                "is_voice": is_voice,
                "timestamp": datetime.now()
            })
            
            # Create Socratic learning context
            socratic_context = f"""
            You are an expert Socratic tutor helping a student learn about {st.session_state.current_topic}.
            
            Your teaching approach:
            1. Ask probing questions that lead the student to discover answers themselves
            2. Build on their existing knowledge
            3. Use analogies and examples to clarify complex concepts
            4. Encourage critical thinking and deeper exploration
            5. Be encouraging and supportive while challenging their thinking
            6. Speak conversationally as if you're having a real discussion
            
            Current learning session: {st.session_state.interaction_count + 1} interactions
            
            Student's question/response: {user_input}
            
            Previous conversation context:
            {get_recent_conversation_context()}
            
            Respond as a caring, knowledgeable tutor who uses the Socratic method.
            Make your response conversational and engaging, as it may be converted to speech.
            """
            
            # Generate response using MCP-enhanced agent
            tutor_response = msft_generate_chat_response(user_input, socratic_context)
            
            # Add tutor response to chat history
            st.session_state.learning_chat_history.append({
                "role": "tutor",
                "content": tutor_response,
                "is_voice": False,
                "timestamp": datetime.now()
            })
            
            # Generate audio response if enabled
            if enable_audio and st.session_state.audio_enabled:
                with st.spinner("🔊 Converting response to speech..."):
                    # Create more conversational audio version
                    conversational_response = make_response_conversational(tutor_response)
                    # Use the custom GPT audio function that returns file path
                    audio_file_path = generate_audio_response_gpt(conversational_response)
                    if audio_file_path and os.path.exists(audio_file_path):
                        # Read the audio file and store it in session state
                        with open(audio_file_path, 'rb') as f:
                            st.session_state.current_audio = f.read()
                        # Clean up the temporary file
                        try:
                            os.remove(audio_file_path)
                        except:
                            pass  # Ignore cleanup errors
            
            # Update learning scores
            update_learning_scores(user_input, tutor_response)
            
            # Increment interaction count
            st.session_state.interaction_count += 1
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing your learning interaction: {str(e)}")

def process_voice_learning_interaction(audio_input, enable_audio_response: bool = True):
    """Process voice input for learning interaction."""
    
    with st.spinner("🎤 Transcribing your voice question..."):
        try:
            # Transcribe audio
            transcription = transcribe_audio(audio_input)
            
            if transcription:
                st.success(f"📝 Transcribed: {transcription}")
                
                # Process as regular learning interaction
                process_learning_interaction(transcription, is_voice=True, enable_audio=enable_audio_response)
            else:
                st.error("❌ Could not transcribe audio. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error processing voice input: {str(e)}")

def make_response_conversational(text: str) -> str:
    """Make the response more conversational for TTS."""
    
    # Add conversational elements
    conversational_starters = [
        "That's a great question! ",
        "I'm glad you asked that. ",
        "Let me help you think through this. ",
        "Interesting point! ",
        "Here's something to consider: "
    ]
    
    # Add natural speech patterns
    text = text.replace(" and ", " and, ")
    text = text.replace(" but ", " but, ")
    text = text.replace(" so ", " so, ")
    
    # Add thinking pauses
    text = text.replace("However,", "However... ")
    text = text.replace("Therefore,", "So therefore... ")
    text = text.replace("For example,", "For example... ")
    
    # Make questions more engaging
    text = text.replace("?", "? Think about it... ")
    
    # Add a conversational starter if needed
    if not any(text.startswith(starter) for starter in conversational_starters):
        import random
        starter = random.choice(conversational_starters)
        text = starter + text
    
    return text

def update_learning_scores(user_input: str, tutor_response: str):
    """Update learning scores based on interaction quality."""
    
    # Simple scoring algorithm (can be enhanced with more sophisticated NLP)
    
    # Understanding score (based on question complexity and depth)
    understanding_boost = 0
    if len(user_input.split()) > 10:  # Detailed questions
        understanding_boost += 5
    if any(word in user_input.lower() for word in ['why', 'how', 'what if', 'explain', 'because']):
        understanding_boost += 3
    if any(word in user_input.lower() for word in ['compare', 'contrast', 'difference', 'similar']):
        understanding_boost += 4
    
    # Engagement score (based on follow-up questions and participation)
    engagement_boost = 2  # Base engagement for asking questions
    if st.session_state.interaction_count > 0:  # Continued engagement
        engagement_boost += 3
    if '?' in user_input:  # Asking questions shows engagement
        engagement_boost += 2
    
    # Progress score (increases with sustained interaction)
    progress_boost = min(3, st.session_state.interaction_count)  # Cap at 3 per interaction
    
    # Update scores (with maximum caps)
    st.session_state.learning_score['understanding'] = min(100, 
        st.session_state.learning_score['understanding'] + understanding_boost)
    st.session_state.learning_score['engagement'] = min(100, 
        st.session_state.learning_score['engagement'] + engagement_boost)
    st.session_state.learning_score['progress'] = min(100, 
        st.session_state.learning_score['progress'] + progress_boost)

def generate_learning_feedback(scores: dict, interaction_count: int) -> str:
    """Generate personalized learning feedback."""
    
    avg_score = sum(scores.values()) / 3
    
    if avg_score >= 80:
        feedback = "🌟 **Excellent Learning Progress!** You're demonstrating deep understanding and high engagement."
    elif avg_score >= 60:
        feedback = "👍 **Good Learning Progress!** You're on the right track. Keep asking thoughtful questions."
    elif avg_score >= 40:
        feedback = "📈 **Making Progress!** Try asking more detailed questions to deepen your understanding."
    else:
        feedback = "🚀 **Just Getting Started!** Don't worry, learning takes time. Keep exploring!"
    
    # Add specific suggestions
    suggestions = []
    
    if scores['understanding'] < 50:
        suggestions.append("💡 Try asking 'why' and 'how' questions to build deeper understanding")
    
    if scores['engagement'] < 50:
        suggestions.append("🤔 Consider asking follow-up questions based on the tutor's responses")
    
    if scores['progress'] < 50:
        suggestions.append("⏰ Consistent practice will help you progress faster")
    
    if interaction_count < 5:
        suggestions.append("🔄 Continue the conversation to explore the topic more thoroughly")
    
    if suggestions:
        feedback += "\n\n**Suggestions for improvement:**\n"
        for suggestion in suggestions:
            feedback += f"\n• {suggestion}"
    
    return feedback

def get_recent_conversation_context() -> str:
    """Get recent conversation context for the tutor."""
    
    if not st.session_state.learning_chat_history:
        return "This is the start of our learning conversation."
    
    # Get last 4 messages for context
    recent_messages = st.session_state.learning_chat_history[-4:]
    context = ""
    
    for msg in recent_messages:
        role = "Student" if msg["role"] == "learner" else "Tutor"
        context += f"{role}: {msg['content']}\n"
    
    return context

def get_topic_information(topic: str) -> str:
    """Get information about the learning topic."""
    
    topic_info = {
        "Machine Learning Fundamentals": """
        **Core Concepts:**
        • Supervised vs Unsupervised Learning
        • Training and Testing Data
        • Model Evaluation Metrics
        • Overfitting and Underfitting
        • Feature Engineering
        """,
        "Data Science Concepts": """
        **Key Areas:**
        • Data Collection and Cleaning
        • Exploratory Data Analysis
        • Statistical Analysis
        • Data Visualization
        • Hypothesis Testing
        """,
        "Python Programming": """
        **Essential Topics:**
        • Basic Syntax and Data Types
        • Control Structures
        • Functions and Classes
        • Libraries (NumPy, Pandas, Matplotlib)
        • Error Handling
        """,
        "Azure AI Services": """
        **Main Services:**
        • Azure OpenAI Service
        • Computer Vision
        • Speech Services
        • Language Understanding
        • Azure ML Studio
        """
    }
    
    return topic_info.get(topic, f"**Learning about: {topic}**\n\nThis is a custom topic. The Socratic tutor will guide you through discovery-based learning.")

def export_learning_session():
    """Export the learning session data."""
    
    session_data = {
        "topic": st.session_state.current_topic,
        "scores": st.session_state.learning_score,
        "interaction_count": st.session_state.interaction_count,
        "chat_history": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "is_voice": msg.get("is_voice", False),
                "timestamp": msg["timestamp"].isoformat() if "timestamp" in msg else None
            }
            for msg in st.session_state.learning_chat_history
        ],
        "export_timestamp": datetime.now().isoformat()
    }
    
    st.download_button(
        label="📄 Download Learning Session",
        data=json.dumps(session_data, indent=2),
        file_name=f"socratic_learning_{st.session_state.current_topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    socratic_type_learning()