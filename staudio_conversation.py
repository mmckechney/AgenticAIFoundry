import asyncio
import nest_asyncio
import io
import json
import os
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
from aiortc.contrib.media import MediaRecorder
import wave
import numpy as np
import streamlit as st
import soundfile as sf
from scipy.signal import resample
from openai import AzureOpenAI
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TIMEOUT_DURATION = 60
OUTPUT_WAV_FILE = "output.wav"

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
        instructions="Generate a response using the MCP API tool.",
    )
    # returntxt = response.choices[0].message.content.strip()
    returntxt = response.output_text
    print(f"Response: {returntxt}")
        
    return returntxt, None

class RealtimeWebRtcSession:
    def __init__(self, api_key, api_url, model, voice, webrtc_url, wav_file, bearer_token=None):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.voice = voice
        self.webrtc_url = webrtc_url
        self.wav_file = wav_file
        self.bearer_token = bearer_token
        self.peer_connection = None
        self.data_channel = None
        self.session_id = ""
        self.data_messages = []
        self.audio_messages = []
        self.session_closed = False
        self.transcript = []
        self.recorder = None
        self.remote_audio_ended = False
        self.audio_done_received = False
        self.recorder_stopped = False
        self.recorder_stop_time = None
        self.rag_context = None
        self.conversation_history = []  # List of dicts: {"role": "user"/"assistant", "content": str}

    async def open_session(self, rag_context=None, conversation_history=None):
        self.rag_context = rag_context
        self.conversation_history = conversation_history or []
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            if self.bearer_token is not None:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            else:
                headers["api-key"] = self.api_key
            if os.getenv("TEST_REDIRECT") is not None:
                redirection = os.getenv("TEST_REDIRECT", "junk")
                headers["x-ms-oai-assistants-testenv"] = redirection
            body = {"model": self.model, "voice": self.voice}
            async with session.post(self.api_url, headers=headers, json=body) as resp:
                if resp.status != 200:
                    print(f"API request failed: {resp.status} {await resp.text()}")
                    return
                data = await resp.json()
                self.session_id = data.get("id")
                ephemeral_key = data.get("client_secret", {}).get("value")
                await self._initialize_session(ephemeral_key, rag_context=rag_context, conversation_history=self.conversation_history)

    async def _initialize_session(self, ephemeral_key, rag_context=None, conversation_history=None):
        self.peer_connection = RTCPeerConnection()
        self._setup_peer_connection()
        self._setup_data_channel(rag_context=rag_context, conversation_history=conversation_history)
        offer = await self.peer_connection.createOffer()
        await self.peer_connection.setLocalDescription(offer)
        await self._send_offer_and_receive_answer(ephemeral_key, offer)
        await self._wait_for_session_events()

    def _setup_peer_connection(self):
        def on_track(track):
            if track.kind == "audio":
                self._handle_audio_track(track)
        self.peer_connection.on("track", on_track)
        player = MediaPlayer(self.wav_file)
        audio_track = player.audio
        if audio_track:
            self.peer_connection.addTrack(audio_track)

    def _handle_audio_track(self, track):
        if self.recorder is None:
            recorder = MediaRecorder(OUTPUT_WAV_FILE)
            recorder.addTrack(track)
            self.audio_messages.append(OUTPUT_WAV_FILE)
            self.recorder = recorder
            asyncio.ensure_future(recorder.start())
        @track.on("ended")
        async def on_ended():
            self.remote_audio_ended = True
            await self._maybe_stop_recorder()

    async def _maybe_stop_recorder(self):
        if self.audio_done_received and self.remote_audio_ended and not self.recorder_stopped:
            if self.recorder:
                await self.recorder.stop()
                await asyncio.sleep(1)
            self.recorder_stopped = True
            self.on_ended_event.set()

    def _setup_data_channel(self, rag_context=None, conversation_history=None):
        self.data_channel = self.peer_connection.createDataChannel("oai-events")
        @self.data_channel.on("open")
        def on_open():
            self.update_session(rag_context=rag_context, conversation_history=conversation_history)
        @self.data_channel.on("message")
        def on_message(message):
            self._handle_data_channel_message(message)
        @self.data_channel.on("close")
        def on_close():
            self.on_close_event.set()

    def _handle_data_channel_message(self, message):
        try:
            json_data = json.loads(message)
            if 'type' in json_data:
                msg_type = json_data['type']
                self.data_messages.append(msg_type)
                if msg_type == "response.audio_transcript.delta":
                    delta_text = json_data.get("delta")
                    if delta_text:
                        self.transcript.append(delta_text)
                if msg_type == "response.audio.done":
                    self.audio_done_received = True
                    asyncio.ensure_future(self._maybe_stop_recorder())
                if msg_type == "response.done" and not self.session_closed:
                    self.session_closed = True
                    async def close_after_recorder():
                        await self.on_ended_event.wait()
                        await self.peer_connection.close()
                    asyncio.ensure_future(close_after_recorder())
        except Exception:
            pass

    async def _send_offer_and_receive_answer(self, ephemeral_key, offer):
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {ephemeral_key}",
                "Content-Type": "application/sdp"
            }
            async with session.post(f"{self.webrtc_url}?model={self.model}", data=offer.sdp, headers=headers) as resp:
                answer_sdp = await resp.text()
                answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
                await self.peer_connection.setRemoteDescription(answer)

    async def _wait_for_session_events(self):
        self.on_close_event = asyncio.Event()
        self.on_ended_event = asyncio.Event()
        try:
            await asyncio.wait_for(
                asyncio.gather(self.on_close_event.wait(), self.on_ended_event.wait()),
                timeout=TIMEOUT_DURATION
            )
        except asyncio.TimeoutError:
            await self.peer_connection.close()
        if not self.session_closed:
            await self.peer_connection.close()

    def update_session(self, rag_context=None, conversation_history=None):
        instructions = "You are a helpful AI assistant responding in natural, engaging language."
        if rag_context:
            instructions += f"\n\nUse the following context to answer the user's questions:\n{rag_context}"
        # Add conversation history as context
        if conversation_history:
            history_text = "\n".join([
                f"{turn['role'].capitalize()}: {turn['content']}" for turn in conversation_history
            ])
            instructions += f"\n\nConversation so far:\n{history_text}"
        event = {
            "type": "session.update",
            "session": {
                "instructions": instructions
            }
        }
        self.data_channel.send(json.dumps(event))

    def validate_session(self) -> tuple[bool, str]:
        required_messages = {
            "response.done", 
            "session.created", 
            "response.audio.done", 
            "response.audio_transcript.delta", 
            "output_audio_buffer.started"
        }
        if not required_messages.issubset(self.data_messages):
            return False, "Missing some required messages"
        if "error" in self.data_messages:
            return False, "Received an error message in the session"
        try:
            if self.audio_messages:
                file_path = self.audio_messages[0]
                if os.path.getsize(file_path) <= 100:
                    return False, "Output audio file is too small"
                with wave.open(file_path, 'rb') as wav_file:
                    wav_file.readframes(1)
            else:
                return False, "No audio messages received"
        except (OSError, IndexError, wave.Error):
            return False, "Output audio file is not a valid WAV file or does not exist"
        return True, "None"

def main():
    st.set_page_config(
        page_title="AI Voice Conversation Hub",
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Material Design 3 CSS with light theme
    st.markdown("""
    <style>
        /* Material Design 3 Light Color Scheme */
        :root {
            --md-sys-color-primary: #6750A4;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #EADDFF;
            --md-sys-color-on-primary-container: #21005D;
            --md-sys-color-secondary: #625B71;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-secondary-container: #E8DEF8;
            --md-sys-color-on-secondary-container: #1D192B;
            --md-sys-color-tertiary: #7D5260;
            --md-sys-color-on-tertiary: #FFFFFF;
            --md-sys-color-tertiary-container: #FFD8E4;
            --md-sys-color-on-tertiary-container: #31111D;
            --md-sys-color-surface: #FEF7FF;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-surface-variant: #E7E0EC;
            --md-sys-color-on-surface-variant: #49454F;
            --md-sys-color-surface-container: #F3EDF7;
            --md-sys-color-surface-container-high: #ECE6F0;
            --md-sys-color-outline: #79747E;
            --md-sys-color-outline-variant: #CAC4D0;
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
            padding: 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(103, 80, 164, 0.15);
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
            font-size: 2.5rem;
            font-weight: 600;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }

        .main-header p {
            color: var(--md-sys-color-on-primary);
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        /* Card styling */
        .feature-card {
            background: var(--md-sys-color-surface);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid var(--md-sys-color-outline-variant);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .feature-card:hover {
            box-shadow: 0 6px 24px rgba(103, 80, 164, 0.15);
            transform: translateY(-4px);
        }

        /* Button styling */
        .stButton > button {
            background: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
            border: none !important;
            border-radius: 24px !important;
            padding: 0.875rem 2rem !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 3px 12px rgba(103, 80, 164, 0.2) !important;
            width: 100% !important;
            margin: 0.5rem 0 !important;
            letter-spacing: 0.025em !important;
        }

        .stButton > button:hover {
            background: #5a4593 !important;
            box-shadow: 0 6px 20px rgba(103, 80, 164, 0.3) !important;
            transform: translateY(-2px) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 3px 12px rgba(103, 80, 164, 0.2) !important;
        }

        /* Audio input styling */
        .stAudioInput {
            background: var(--md-sys-color-surface-container) !important;
            border-radius: 16px !important;
            padding: 1rem !important;
            border: 2px solid var(--md-sys-color-outline-variant) !important;
            transition: all 0.3s ease !important;
        }

        .stAudioInput:focus-within {
            border-color: var(--md-sys-color-primary) !important;
            box-shadow: 0 0 0 3px rgba(103, 80, 164, 0.1) !important;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background: var(--md-sys-color-surface) !important;
            border-right: 1px solid var(--md-sys-color-outline-variant) !important;
        }

        /* Selectbox and radio styling */
        .stSelectbox > div > div {
            background: var(--md-sys-color-surface-container) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            border-radius: 12px !important;
        }

        .stRadio > div {
            background: var(--md-sys-color-surface-container) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }

        /* Text area styling */
        .stTextArea > div > div > textarea {
            background: var(--md-sys-color-surface-container) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            border-radius: 12px !important;
            color: var(--md-sys-color-on-surface) !important;
        }

        /* Status indicators */
        .status-success {
            background: var(--md-sys-color-success);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            display: inline-block;
            margin: 0.25rem;
        }

        .status-info {
            background: var(--md-sys-color-primary);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            display: inline-block;
            margin: 0.25rem;
        }

        /* Section headers */
        .section-header {
            color: var(--md-sys-color-primary);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--md-sys-color-primary-container);
        }

        /* Profile card styling */
        .profile-card {
            background: var(--md-sys-color-tertiary-container);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid var(--md-sys-color-tertiary);
        }

        .profile-field {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--md-sys-color-outline-variant);
        }

        .profile-field:last-child {
            border-bottom: none;
        }

        .profile-label {
            font-weight: 500;
            color: var(--md-sys-color-on-tertiary-container);
        }

        .profile-value {
            color: var(--md-sys-color-on-tertiary-container);
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ AI Voice Conversation Hub</h1>
        <p>Intelligent Real-time Audio Conversations with AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    json_str = ""

    # Enhanced sidebar with Material Design 3
    with st.sidebar:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🎯 Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🎵 Voice Settings")
        option_to_file = {
            '👨‍🎓 Learner': 'ai_learning_paths.json',
            '👨‍💼 Administrator': 'learning_admin_data.json',
            '🏃‍♂️ Coach': 'ai_learning_paths.json',
        }
        voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse']
        
        selected_voice = st.selectbox(
            "🗣️ Choose AI Voice", 
            voices, 
            help="Select the voice personality for your AI assistant"
        )
        
        st.markdown("#### 🎯 Learning Profile")
        options = list(option_to_file.keys())
        selected_option = st.radio(
            "Choose your learning role:", 
            options, 
            horizontal=False,
            help="Select your role to get personalized learning content"
        )
        
        file_path = option_to_file[selected_option]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
        except Exception as e:
            json_str = "{}"
            st.warning(f"⚠️ Could not load {file_path}: {e}")
        
        st.markdown("#### 📚 Knowledge Base")
        json_input = st.text_area(
            "RAG Content (JSON)", 
            height=200, 
            value=json_str,
            help="Enter JSON data that will be used as context for the AI assistant"
        )
        
        st.markdown("""
        <div style="background: var(--md-sys-color-surface-container); 
                    padding: 1rem; border-radius: 12px; margin: 1rem 0;">
            <small style="color: var(--md-sys-color-on-surface-variant);">
                💡 <strong>Enhanced RAG:</strong> The AI will use this knowledge base PLUS real-time context from Microsoft Learn MCP server based on your audio questions for more accurate responses.
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # Show enhanced RAG status
        st.markdown("#### 🧠 Smart RAG Status")
        st.markdown("""
        <div class="feature-card">
            <div style="margin-bottom: 0.5rem;">
                <span class="status-success">🟢 Base Knowledge Ready</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span class="status-info">🤖 MCP Enhancement Active</span>
            </div>
            <div>
                <span class="status-success">🧠 Smart RAG Enabled</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        url = f"https://agentnew-resource.openai.azure.com/openai/realtimeapi/sessions?api-version=2025-04-01-preview"
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        apikey = os.getenv("AZURE_OPENAI_KEY")
        model = "gpt-4o-mini-realtime-preview"
        voice = selected_voice
        webrtc_url = "https://eastus2.realtimeapi-preview.ai.azure.com/v1/realtimertc"
        input_wav = "hello.wav"
        bearer_token = os.getenv("BEARER_TOKEN") if os.getenv("BEARER_TOKEN") else None

    # Initialize conversation history and enhanced context in session state
    if "conversation_history" not in st.session_state:
        st.session_state["conversation_history"] = []
    if "transcript_history" not in st.session_state:
        st.session_state["transcript_history"] = []
    if "last_enhanced_context" not in st.session_state:
        st.session_state["last_enhanced_context"] = ""

    # Initialize user profile in session state
    required_profile_fields = [
        ("first_name", "What is your first name?"),
        ("last_name", "What is your last name?"),
        ("job_title", "What is your job title?"),
        ("duration_of_work", "How long have you been working in your current role?"),
        ("learning_topic", "What learning topic are you interested in?")
    ]
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = {k: None for k, _ in required_profile_fields}

    # --- ENHANCED AUDIO INPUT SECTION ---
    st.markdown('<div class="section-header">🎙️ Voice Message Center</div>', unsafe_allow_html=True)
    
    # Audio input in a styled container
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">📹 Record Your Message</h4>
        <p style="color: var(--md-sys-color-on-surface-variant); margin-bottom: 1rem;">
            Click the microphone button below to start recording your voice message. The AI will process your audio and respond with both text and voice.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    audio_data = st.audio_input("🎤 Record your voice message")
    
    # Action buttons with improved layout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        send_clicked = st.button("🚀 Send & Process Message", type="primary")
    with col2:
        clear_clicked = st.button("🗑️ Clear Chat", type="secondary")
    with col3:
        if st.button("ℹ️ Help"):
            st.info("""
            **How to use:**
            1. Click the microphone to record
            2. Speak your message clearly
            3. Click 'Send & Process Message'
            4. Wait for AI response (text + audio)
            """)

    # Handle clear conversation
    if clear_clicked:
        st.session_state["conversation_history"] = []
        st.session_state["transcript_history"] = []
        st.session_state["user_profile"] = {k: None for k, _ in required_profile_fields}
        st.success("✅ Conversation cleared!")
        st.experimental_rerun()

    # --- ENHANCED LAYOUT: USER PROFILE, CHAT HISTORY, AND STATUS ---
    col_left, col_right = st.columns([1, 2])

    with col_left:
        
        # Enhanced Context Display
        if st.session_state.get("last_enhanced_context"):
            st.markdown('<div class="section-header">🧠 Enhanced Context</div>', unsafe_allow_html=True)
            with st.expander("📋 View Last MCP Enhancement", expanded=False):
                st.markdown("""
                <div class="feature-card">
                    <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">Latest MCP Enhancement:</h6>
                </div>
                """, unsafe_allow_html=True)
                st.text_area(
                    "Enhanced Context from Microsoft Learn MCP:",
                    value=st.session_state["last_enhanced_context"],
                    height=150,
                    disabled=True,
                    key="enhanced_context_display"
                )
        
        # Processing status
        st.markdown('<div class="section-header">📊 Status</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <div style="margin-bottom: 0.5rem;">
                <span class="status-info">🟢 System Ready</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span class="status-success">🎙️ Audio Processing Active</span>
            </div>
            <div>
                <span class="status-info">🤖 AI Assistant Online</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">💬 Conversation History</div>', unsafe_allow_html=True)
        
        # Enhanced chat styling
        st.markdown("""
        <style>
        /* Enhanced Material Design chat container */
        .chat-history-container {
            max-height: 500px;
            overflow-y: auto;
            background: var(--md-sys-color-surface-container);
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--md-sys-color-outline-variant);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .chat-message-user {
            background: linear-gradient(135deg, var(--md-sys-color-primary) 0%, #8A2BE2 100%);
            color: var(--md-sys-color-on-primary);
            margin: 0.75rem 0 0.75rem 3rem;
            padding: 1rem 1.25rem;
            border-radius: 20px 20px 8px 20px;
            box-shadow: 0 3px 12px rgba(103, 80, 164, 0.2);
            font-weight: 500;
            max-width: 85%;
            float: right;
            clear: both;
            position: relative;
            animation: slideInRight 0.3s ease-out;
        }
        
        .chat-message-assistant {
            background: linear-gradient(135deg, var(--md-sys-color-tertiary-container) 0%, #E1F5FE 100%);
            color: var(--md-sys-color-on-tertiary-container);
            margin: 0.75rem 3rem 0.75rem 0;
            padding: 1rem 1.25rem;
            border-radius: 20px 20px 20px 8px;
            box-shadow: 0 3px 12px rgba(125, 82, 96, 0.15);
            max-width: 85%;
            float: left;
            clear: both;
            position: relative;
            animation: slideInLeft 0.3s ease-out;
            line-height: 1.5;
        }
        
        .chat-message-user::before {
            content: "👤";
            position: absolute;
            right: -2.5rem;
            top: 0.75rem;
            font-size: 1.5rem;
        }
        
        .chat-message-assistant::before {
            content: "🤖";
            position: absolute;
            left: -2.5rem;
            top: 0.75rem;
            font-size: 1.5rem;
        }
        
        .chat-message-user::after, .chat-message-assistant::after {
            content: "";
            display: table;
            clear: both;
        }
        
        @keyframes slideInRight {
            from { transform: translateX(50px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { transform: translateX(-50px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .chat-empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--md-sys-color-on-surface-variant);
            font-style: italic;
        }
        
        .chat-empty-state::before {
            content: "💭";
            display: block;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

        chat_html = "<div class='chat-history-container' id='chat-history'>"
        if st.session_state["conversation_history"]:
            for turn in st.session_state["conversation_history"]:
                if turn["role"] == "user":
                    content = turn['content'].replace('\n', '<br>')
                    chat_html += f"<div class='chat-message-user'>{content}</div>"
                else:
                    content = turn['content'].replace('\n', '<br>')
                    chat_html += f"<div class='chat-message-assistant'>{content}</div>"
        else:
            chat_html += """
            <div class='chat-empty-state'>
                <strong>Ready to start your conversation!</strong><br>
                Record your first message to begin chatting with the AI assistant.
            </div>
            """
        chat_html += "</div>"
        
        # Enhanced auto-scroll script
        chat_html += """
        <script>
        function scrollToBottom() {
            var chatDiv = document.getElementById('chat-history');
            if (chatDiv) { 
                chatDiv.scrollTop = chatDiv.scrollHeight;
                chatDiv.style.scrollBehavior = 'smooth';
            }
        }
        scrollToBottom();
        // Auto-scroll after a brief delay to ensure content is loaded
        setTimeout(scrollToBottom, 100);
        </script>
        """
        st.markdown(chat_html, unsafe_allow_html=True)

    # --- AUDIO PROCESSING AND SESSION LOGIC ---
    with col_left:
        def extract_and_update_profile_from_transcript(transcript, required_profile_fields):
            """
            Extracts and updates user profile fields from the transcript using simple keyword/regex matching.
            """
            import re
            profile = st.session_state["user_profile"]
            text = transcript.lower() if transcript else ""
            # Simple patterns for each field
            patterns = {
                "first_name": r"(?:my name is|i am|i'm|this is) ([a-zA-Z]+)",
                "last_name": r"(?:last name is|surname is|family name is) ([a-zA-Z]+)",
                "job_title": r"(?:i am a|i'm a|my job title is|i work as|i am an|i'm an) ([a-zA-Z ]+)",
                "duration_of_work": r"(?:i have been working for|i've been working for|i have worked for|i've worked for|for) ([0-9]+ ?(?:years?|months?))",
                "learning_topic": r"(?:i want to learn|i am interested in|i'd like to learn|learning topic is|about) ([a-zA-Z0-9 ,\-]+)"
            }
            for field, pattern in patterns.items():
                if not profile[field]:
                    match = re.search(pattern, text)
                    if match:
                        value = match.group(1).strip().capitalize()
                        profile[field] = value
            st.session_state["user_profile"] = profile

        if send_clicked:
            if audio_data:
                import time as _time
                start_time = _time.time()
                with st.spinner("Processing and sending audio message...", show_time=True):
                    audio_bytes = io.BytesIO(audio_data.getvalue())
                    data, samplerate = sf.read(audio_bytes)
                    if len(data.shape) > 1 and data.shape[1] > 1:
                        data = data.mean(axis=1)
                    target_samplerate = 24000
                    if samplerate != target_samplerate:
                        num_samples = int(len(data) * target_samplerate / samplerate)
                        data = resample(data, num_samples)
                        samplerate = target_samplerate
                    data_int16 = np.int16(np.clip(data, -1.0, 1.0) * 32767)
                    output_filename = "output_pcm16_24khz_mono.wav"
                    sf.write(
                        output_filename,
                        data_int16,
                        samplerate,
                        format='WAV',
                        subtype='PCM_16',
                        endian='LITTLE'
                    )
                    st.success(f"Saved: {output_filename} (16-bit PCM, 24kHz, mono, little-endian)")
                    st.audio(output_filename)
                    # Add user turn to conversation history
                    st.session_state["conversation_history"].append({"role": "user", "content": "[User audio message]"})

                    transcript_text = ""
                    session = None
                    full_transcript = ""
                    # Restore: process audio, then play output after session completes
                    session = RealtimeWebRtcSession(
                        apikey,
                        url,
                        model,
                        voice,
                        webrtc_url,
                        output_filename,
                        bearer_token=bearer_token
                    )
                    # --- Enhanced RAG with MCP Integration ---
                    audio_placeholder = st.empty()
                    async def run_and_stream():
                        # Extract the user's audio content for RAG processing
                        user_audio_content = "[User audio message]"
                        
                        # Try to get a more meaningful user question for MCP enhancement
                        # First, try to transcribe the current audio if possible
                        try:
                            # Use a simple approach to get the user's intent
                            if audio_data:
                                # For now, we'll use a generic learning-focused query
                                # In a production system, you'd want to transcribe the audio first
                                user_audio_content = f"User is asking about learning topics related to {selected_option} role. Please provide relevant educational content and resources."
                        except Exception as e:
                            st.warning(f"Could not extract specific user question: {e}")
                            user_audio_content = f"Provide learning assistance for {selected_option} role"
                        
                        # Also check conversation history for more context
                        if st.session_state["conversation_history"]:
                            recent_user_messages = [msg["content"] for msg in st.session_state["conversation_history"][-3:] if msg["role"] == "user"]
                            if recent_user_messages:
                                user_audio_content += f" Recent context: {' '.join(recent_user_messages)}"
                        
                        # Use MCP to generate enhanced context based on user's question
                        try:
                            with st.spinner("🔄 Generating enhanced context with MCP..."):
                                # Generate RAG context using MCP based on the user's audio question
                                rag_context, _ = msft_generate_chat_response(user_audio_content, json_input)
                                
                                # Enhance the original JSON input with MCP-generated context
                                enhanced_context = f"""
                                Original Knowledge Base:
                                {json_input}
                                
                                Enhanced Context from Microsoft Learn MCP:
                                {rag_context}
                                
                                User Profile Context:
                                Learning Role: {selected_option}
                                Voice: {selected_voice}
                                
                                Instructions: Use this enhanced context to provide personalized, accurate responses. Focus on practical learning advice and actionable recommendations.
                                """
                                
                                # Save the enhanced context to session state
                                st.session_state["last_enhanced_context"] = rag_context
                                
                                st.success("✅ Enhanced context generated with MCP!")
                                
                        except Exception as e:
                            st.warning(f"⚠️ MCP enhancement failed: {e}")
                            # Fallback to original context
                            enhanced_context = json_input
                            st.session_state["last_enhanced_context"] = "MCP enhancement failed - using base knowledge only"
                        
                        # Start the real-time session with enhanced context
                        task = asyncio.create_task(session.open_session(rag_context=enhanced_context, conversation_history=st.session_state["conversation_history"]))
                        last_size = 0
                        while not session.session_closed:
                            await asyncio.sleep(0.5)
                            try:
                                if os.path.exists(OUTPUT_WAV_FILE):
                                    size = os.path.getsize(OUTPUT_WAV_FILE)
                                    if size > last_size and size > 1000:
                                        with open(OUTPUT_WAV_FILE, "rb") as f:
                                            audio_bytes = f.read()
                                            audio_placeholder.audio(audio_bytes)
                                            st.markdown("""
                                            <script>
                                            var audios = document.getElementsByTagName('audio');
                                            if (audios.length > 0) {
                                                var lastAudio = audios[audios.length - 1];
                                                lastAudio.autoplay = true;
                                                lastAudio.play().catch(()=>{});
                                            }
                                            </script>
                                            """, unsafe_allow_html=True)
                                        last_size = size
                            except Exception:
                                pass
                        await task
                        # Final audio
                        if os.path.exists(OUTPUT_WAV_FILE):
                            with open(OUTPUT_WAV_FILE, "rb") as f:
                                audio_bytes = f.read()
                                audio_placeholder.audio(audio_bytes)
                                st.markdown("""
                                <script>
                                var audios = document.getElementsByTagName('audio');
                                if (audios.length > 0) {
                                    var lastAudio = audios[audios.length - 1];
                                    lastAudio.autoplay = true;
                                    lastAudio.play().catch(()=>{});
                                }
                                </script>
                                """, unsafe_allow_html=True)
                    asyncio.run(run_and_stream())
                    st.success("WebRTC session completed!")
                    if session.transcript:
                        full_transcript = " ".join(session.transcript)
                        transcript_text = full_transcript.lower()
                        st.subheader("Transcript (Latest Turn)")
                        st.markdown("""
                        <div style='max-height: 180px; overflow-y: auto; background: #f5f5f5; border-radius: 8px; padding: 1em; margin-bottom: 1em; font-size: 1.08em; border: 1px solid #e0e0e0;'>
                        """ + full_transcript.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                        st.session_state["conversation_history"].append({"role": "assistant", "content": full_transcript})
                        st.session_state["transcript_history"].append(full_transcript)
                        # Extract and update profile info from transcript
                        extract_and_update_profile_from_transcript(full_transcript, required_profile_fields)
                    else:
                        st.warning("No transcript was received.")
                    # Example: Use user_profile in your model prompt
                    user_profile = st.session_state["user_profile"]
                    profile_str = f"First Name: {user_profile['first_name']}, Last Name: {user_profile['last_name']}, Job Title: {user_profile['job_title']}, Duration of Work: {user_profile['duration_of_work']}, Learning Topic: {user_profile['learning_topic']}"
                    personalized_instructions = f"User profile: {profile_str}\nPlease provide a personalized learning recommendation."
                    st.session_state["conversation_history"].append({"role": "assistant", "content": personalized_instructions})
                    # st.info(f"Assistant: {personalized_instructions}")
                end_time = _time.time()
                elapsed = end_time - start_time
                st.info(f"⏱️ Time taken to process audio: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
