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
    retturntxt = response.output_text
    print(f"Response: {retturntxt}")
        
    return retturntxt, None

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
        page_title="Realtime Audio WebRTC Conversation",
        layout="wide"
    )
    st.title("Realtime WebRTC Conversation Example")
    json_str = ""

    # Sidebar for JSON input
    with st.sidebar:
        st.header("RAG Data Source")
        option_to_file = {
            'Learner': 'ai_learning_paths.json',
            'Administrator': 'learning_admin_data.json',
            'Coach': 'ai_learning_paths.json',
        }
        voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse']
        selected_voice = st.selectbox("Choose a voice", voices)
        options = list(option_to_file.keys())
        selected_option = st.radio("Choose an option:", options, horizontal=False)
        file_path = option_to_file[selected_option]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
        except Exception as e:
            json_str = "{}"
            st.warning(f"Could not load {file_path}: {e}")
        json_input = st.text_area("Enter JSON string for RAG content", height=200, value=json_str)
        st.info("Enter a valid JSON string containing key-value pairs or a list of documents.")
        url = f"https://agentnew-resource.openai.azure.com/openai/realtimeapi/sessions?api-version=2025-04-01-preview"
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        apikey = os.getenv("AZURE_OPENAI_KEY")
        model = "gpt-4o-mini-realtime-preview"
        voice = selected_voice
        webrtc_url = "https://eastus2.realtimeapi-preview.ai.azure.com/v1/realtimertc"
        input_wav = "hello.wav"
        bearer_token = os.getenv("BEARER_TOKEN") if os.getenv("BEARER_TOKEN") else None

    # Initialize conversation history in session state
    if "conversation_history" not in st.session_state:
        st.session_state["conversation_history"] = []
    if "transcript_history" not in st.session_state:
        st.session_state["transcript_history"] = []

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

    # --- AUDIO INPUT AND SEND BUTTON AT THE TOP ---
    st.subheader("Record your voice message")
    audio_data = st.audio_input("Record your voice message")
    send_col, clear_col = st.columns([1, 1])
    with send_col:
        send_clicked = st.button("Send Message")
    with clear_col:
        clear_clicked = st.button("Clear Conversation", type="secondary")

    # Handle clear conversation
    if clear_clicked:
        st.session_state["conversation_history"] = []
        st.session_state["transcript_history"] = []
        st.session_state["user_profile"] = {k: None for k, _ in required_profile_fields}
        st.experimental_rerun()

    # --- LAYOUT: AUDIO/TRANSCRIPT LEFT, CHAT HISTORY RIGHT ---
    left_col, right_col = st.columns([1, 2])

    with right_col:
        st.markdown("""
        <style>
        /* Material Design-inspired chat container */
        .chat-history-container {
            max-height: 400px;
            overflow-y: auto;
            background: #FAFAFA;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(60,60,60,0.08), 0 1.5px 4px rgba(60,60,60,0.06);
            padding: 1.2em 1em 1em 1em;
            margin-bottom: 1.5em;
            font-size: 1.08em;
            border: none;
        }
        .chat-message-user {
            background: #E3F2FD;
            color: #1565c0;
            margin-bottom: 0.5em;
            margin-right: 2.5em;
            padding: 0.7em 1em;
            border-radius: 18px 18px 4px 18px;
            box-shadow: 0 1px 3px rgba(21,101,192,0.07);
            font-weight: 500;
            width: fit-content;
            max-width: 80%;
            align-self: flex-end;
            float: right;
            clear: both;
        }
        .chat-message-assistant {
            background: #E8F5E9;
            color: #2e7d32;
            margin-bottom: 1em;
            margin-left: 2.5em;
            padding: 0.7em 1em;
            border-radius: 18px 18px 18px 4px;
            box-shadow: 0 1px 3px rgba(46,125,50,0.07);
            width: fit-content;
            max-width: 80%;
            align-self: flex-start;
            float: left;
            clear: both;
        }
        .chat-message-user::after, .chat-message-assistant::after {
            content: "";
            display: table;
            clear: both;
        }
        /* Remove default Streamlit padding for a more app-like look */
        section.main > div { padding-top: 1.5rem; }
        </style>
        """, unsafe_allow_html=True)

        chat_html = "<div class='chat-history-container' id='chat-history'>"
        if st.session_state["conversation_history"]:
            for turn in st.session_state["conversation_history"]:
                if turn["role"] == "user":
                    chat_html += f"<div class='chat-message-user'>You: {turn['content']}</div>"
                else:
                    chat_html += f"<div class='chat-message-assistant'>Assistant: {turn['content']}</div>"
        else:
            chat_html += "<div>No conversation yet. Record your first message!</div>"
        chat_html += "</div>"
        # Add JS to scroll to bottom on update
        chat_html += """
        <script>
        var chatDiv = document.getElementById('chat-history');
        if (chatDiv) { chatDiv.scrollTop = chatDiv.scrollHeight; }
        </script>
        """
        st.markdown(chat_html, unsafe_allow_html=True)

    # --- AUDIO PROCESSING AND SESSION LOGIC ---
    with left_col:
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
                    # --- Simulated streaming audio output ---
                    audio_placeholder = st.empty()
                    async def run_and_stream():
                        # cnt, others = st.session_state["conversation_history"][-1]["content"]
                        # learncontext = msft_generate_chat_response(cnt, json_input)
                        task = asyncio.create_task(session.open_session(rag_context=json_input, conversation_history=st.session_state["conversation_history"]))
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
                    st.info(f"Assistant: {personalized_instructions}")
                end_time = _time.time()
                elapsed = end_time - start_time
                st.info(f"⏱️ Time taken to process audio: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
