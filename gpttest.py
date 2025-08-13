import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from openai import AzureOpenAI, OpenAIError

import base64
import os
from gtts import gTTS
import tempfile
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration (replace with your credentials)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
WHISPER_DEPLOYMENT_NAME = "whisper"
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
GPT5_DEPLOYMENT_NAME = os.getenv("GPT5_DEPLOYMENT_NAME")


# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

def get_chat_response_stream(query: str):
    """Get streaming response from Azure OpenAI"""
    try:
        completion = client.chat.completions.create(
            model=GPT5_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": query}],
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True
        )
        
        full_response = ""
        for chunk in completion:
            # Check if chunk has choices and if choices is not empty
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                # Check if delta exists and has content
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content
        
        # Estimate token usage since streaming doesn't provide exact counts
        prompt_tokens = len(query.split()) * 1.3  # Rough estimation
        completion_tokens = len(full_response.split()) * 1.3
        total_tokens = prompt_tokens + completion_tokens
        
        token_usage = {
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(completion_tokens),
            'total_tokens': int(total_tokens)
        }
        
        yield ("FINAL_TOKEN_USAGE", token_usage)
        
    except OpenAIError as e:
        st.error(f"Error communicating with Azure OpenAI: {e}")
        yield f"An error occurred while processing your request. {e}"
    except Exception as e:
        st.error(f"Unexpected error during streaming: {e}")
        yield f"An unexpected error occurred: {e}"

def get_chat_response(query: str) -> tuple[str, dict]:
    """Fallback non-streaming response for compatibility"""
    returntxt = ""
    token_usage = {}
    try:
        completion = client.chat.completions.create(
            model=GPT5_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": query}],
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        returntxt = completion.choices[0].message.content
        print('Entire completion:', completion.choices[0])

        # Extract token usage information
        if hasattr(completion, 'usage') and completion.usage:
            token_usage = {
                'prompt_tokens': getattr(completion.usage, 'prompt_tokens', 0),
                'completion_tokens': getattr(completion.usage, 'completion_tokens', 0),
                'total_tokens': getattr(completion.usage, 'total_tokens', 0)
            }
        
        return returntxt, token_usage
    except OpenAIError as e:
        st.error(f"Error communicating with Azure OpenAI: {e}")
        returntxt = f"An error occurred while processing your request. {e}"
        return returntxt, token_usage
    
def get_chat_response_gpt5(query: str) -> tuple[str, dict]:
    """Fallback non-streaming response for compatibility"""
    returntxt = ""
    model_name = "gpt-5"
    deployment = "gpt-5"
    
    token_usage = {}
    reasonclient = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="2025-01-01-preview",
)
    try:
        completion = reasonclient.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": query}],
            max_completion_tokens=16384,
            stop=None,
            stream=False,
            reasoning_effort="high",
        )
        returntxt = completion.choices[0].message.content
        #print('Entire completion:', completion.choices[0])

        # Extract token usage information
        if hasattr(completion, 'usage') and completion.usage:
            token_usage = {
                'prompt_tokens': getattr(completion.usage, 'prompt_tokens', 0),
                'completion_tokens': getattr(completion.usage, 'completion_tokens', 0),
                'total_tokens': getattr(completion.usage, 'total_tokens', 0)
            }

        print(completion.to_json())
        
        return returntxt, token_usage
    except OpenAIError as e:
        st.error(f"Error communicating with Azure OpenAI: {e}")
        returntxt = f"An error occurred while processing your request. {e}"
        return returntxt, token_usage
    
def get_chat_response_gpt5_response(query: str) -> str:
    returntxt = ""

    responseclient = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="preview",
    )
    deployment = "gpt-5"

    response = responseclient.responses.create(
        model=deployment,
        input= [{ 'role': 'developer', 'content': query }, 
                { 'role': 'user', 'content': 'You are AI assistant, respond to users queries.' }],
        reasoning = {
            "effort": "high"
        },
        max_output_tokens=15000,
    )

    # Extract model's text output
    output_text = ""
    for item in response.output:
        if hasattr(item, "content"):
            for content in item.content:
                if hasattr(content, "text"):
                    output_text += content.text

    # Token usage details
    usage = response.usage

    print("--------------------------------")
    print("Output:")
    print(output_text)
    returntxt = output_text

    return returntxt, usage
        
def main_screen():
    st.set_page_config(
        page_title="AI Assessment Assistant",
        page_icon=":robot_face:",
        layout="wide"
    )
    
    # Custom CSS for professional styling with light yellow background
    st.markdown("""
    <style>
    /* Global container adjustments for full screen fit */
    .main .block-container {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
        max-width: 100%;
        height: 100vh;
        max-height: 100vh;
        overflow: hidden;
    }
    .main-header {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        padding: 6px;
        border-radius: 6px;
        color: #000000;
        text-align: center;
        margin-bottom: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #f59e0b;
    }
    .main-header h1 {
        color: #92400e !important;
        margin-bottom: 2px;
        font-size: 1.2em;
        font-weight: bold;
    }
    .main-header p {
        color: #451a03 !important;
        margin: 0;
        font-size: 0.7em;
    }
    .chat-flex-wrapper {
        display: flex;
        flex-direction: column;
        position: relative;
        height: 10px; /* fixed smaller height */
        max-height: 40px;
        transition: height .2s ease;
        margin-bottom: 2px;
        overflow: hidden;
    }
    .chat-container {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-radius: 6px;
        padding: 4px 6px;
        margin: 1px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f59e0b;
        flex: 1 1 auto;
        overflow-y: auto;
        overflow-x: hidden;
        min-height: 300px;
        max-height: 400px;
        height: 400px;
    }
    .chat-message {
        margin: 4px 0;
        padding: 6px;
        border-radius: 6px;
        word-wrap: break-word;
        font-size: 0.8em;
    }
    .user-message {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        margin-right: 30px;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-left: 4px solid #6b7280;
        margin-left: 30px;
    }
    .message-header {
        font-weight: bold;
        color: #374151;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85em;
    }
    .message-content {
        color: #374151;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .streaming-message {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0ea5e9;
        margin-left: 30px;
        border-radius: 10px;
        padding: 12px;
        margin: 10px 0;
        font-size: 0.9em;
    }
    .streaming-header {
        font-weight: bold;
        color: #0c4a6e;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85em;
    }
    .streaming-content {
        color: #0c4a6e;
        line-height: 1.5;
        white-space: pre-wrap;
        min-height: 20px;
    }
    .token-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 6px;
        padding: 8px;
        margin-top: 8px;
        border-left: 3px solid #0ea5e9;
        font-size: 0.75em;
        color: #0c4a6e;
    }
    .stats-container {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #10b981;
        text-align: center;
    }
    .input-container {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border-radius: 6px;
        padding: 4px 6px 2px 6px;
        margin-top: 1px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f59e0b;
        position: sticky;
        bottom: 0;
        z-index: 50;
        flex-shrink: 0;
    }
    /* Streamlit chat input native element adjustments when fixed */
    div[data-testid="stChatInput"] { margin-top: 1px; }
    @media (max-height: 900px){
        .chat-flex-wrapper { height: 350px; }
    }
    @media (max-height: 750px){
        .chat-flex-wrapper { height: 300px; }
    }
    @media (max-height: 600px){
        .chat-flex-wrapper { height: 250px; }
        .main-header { padding: 2px; margin-bottom: 1px; }
        .main-header h1 { font-size: 0.9em; }
        .main-header p { font-size: 0.5em; }
    }
    @media (max-height: 500px){
        .chat-flex-wrapper { height: 200px; }
        .main-header { display: none; }
    }
    .scrollable-container::-webkit-scrollbar {
        width: 8px;
    }
    .scrollable-container::-webkit-scrollbar-track {
        background: #fef3c7;
        border-radius: 10px;
    }
    .scrollable-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-radius: 10px;
    }
    .scrollable-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    }
    /* Ensure scrollable container has defined height */
    .scrollable-container {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        height: 100% !important;
    }
    .metric-card {
        background: white;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 3px 0;
        border: 1px solid #f59e0b;
    }
    .sidebar-content {
        height: 80vh;
        overflow-y: auto;
        position: fixed;
        top: 10px;
        right: 20px;
        width: 280px;
        z-index: 100;
    }
    /* Reduce spacing for compact view */
    h3 {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
        font-size: 1.0em !important;
    }
    /* Make sections more compact */
    .section-title {
        font-size: 0.9em !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'total_session_tokens' not in st.session_state:
        st.session_state.total_session_tokens = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Assessment Assistant</h1>
        <p>Professional AI-powered assistance for your queries and assessments</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create main layout with adjusted ratios for fixed sidebar
    main_col1, main_col2 = st.columns([4, 1])
    
    with main_col1:
        # Chat Interface Section
        st.markdown('<h3 class="section-title">💬 Conversation</h3>', unsafe_allow_html=True)
        # Open flex wrapper to constrain chat height and allow internal scrolling
        st.markdown('<div class="chat-flex-wrapper">', unsafe_allow_html=True)
        max_display_messages = 12
        total_msgs = len(st.session_state.chat_history)
        if total_msgs > max_display_messages:
            older = st.session_state.chat_history[:-max_display_messages]
            with st.expander(f"Show earlier messages ({len(older)})"):
                for m in older:
                    prefix = "You:" if m['role'] == 'user' else 'AI:'
                    st.markdown(f"<div style='font-size:0.65em; padding:2px 4px;'><strong>{prefix}</strong> {m['content'][:80].replace('<','&lt;').replace('>','&gt;')}...</div>", unsafe_allow_html=True)
            recent_messages = st.session_state.chat_history[-max_display_messages:]
        else:
            recent_messages = st.session_state.chat_history

        # Chat History Display (recent messages only)
        # chat-container will flex and scroll within chat-flex-wrapper
        chat_html = '<div class="chat-container scrollable-container">'

        if recent_messages:
            for i, message in enumerate(recent_messages):
                message_class = "user-message" if message["role"] == "user" else "assistant-message"
                role_icon = "👤" if message["role"] == "user" else "🤖"
                role_name = "You" if message["role"] == "user" else "AI Assistant"
                content = message["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                content = content.replace("\n", "<br>")
                chat_html += f'''
                <div class="chat-message {message_class}">
                    <div class="message-header">
                        {role_icon} {role_name}
                        <span style="font-size: 0.75em; color: #6b7280; margin-left: auto;">
                            {message.get("timestamp", "")}
                        </span>
                    </div>
                    <div class="message-content">{content}</div>'''
                if message["role"] == "assistant" and message.get("token_usage"):
                    token_info = message["token_usage"]
                    chat_html += f'''
                    <div class="token-info">
                        📊 Tokens: {token_info.get("prompt_tokens", 0)} prompt + {token_info.get("completion_tokens", 0)} completion = {token_info.get("total_tokens", 0)} total
                    </div>'''
                chat_html += '</div>'
        else:
            chat_html += '''
            <div style="text-align: center; color: #6b7280; padding: 50px 20px;">
                <h3>🚀 Ready to Assist!</h3>
                <p>Ask me anything and I'll provide detailed responses with token usage information.</p>
            </div>'''

        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # Input Section (sticky within wrapper)
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">💭 Ask Your Question</h3>', unsafe_allow_html=True)

        # Mode selection buttons (stream vs reasoning)
        if 'response_mode' not in st.session_state:
            st.session_state.response_mode = 'Stream'
        mode_col1, mode_col2, mode_col3 = st.columns([1,1,2], gap="medium")
        with mode_col1:
            if st.button("▶ Stream", type="primary", disabled=st.session_state.response_mode == 'Stream'):
                st.session_state.response_mode = 'Stream'
                st.rerun()
        with mode_col2:
            if st.button("🧠 Reasoning", disabled=st.session_state.response_mode == 'Reasoning'):
                st.session_state.response_mode = 'Reasoning'
                st.rerun()
        with mode_col3:
            st.markdown(f"<div style='font-size:0.7em; padding-top:6px;'>Mode: <strong>{st.session_state.response_mode}</strong></div>", unsafe_allow_html=True)

        # Chat input (sticky) replacing form with native st.chat_input
        prompt = st.chat_input("Type your question here...")
        
        # Clear button outside of input
        clear_clicked = st.button("🗑️ Clear History", key="clear_chat")
        if clear_clicked:
            st.session_state.chat_history = []
            st.session_state.total_session_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
            st.rerun()
            
        if prompt and not st.session_state.processing:
            st.session_state.processing = True
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            user_message = {"role": "user", "content": prompt.strip(), "timestamp": timestamp}
            st.session_state.chat_history.append(user_message)
            response_placeholder = st.empty()
            response_placeholder.markdown('''<div class="streaming-message"><div class="streaming-header">🤖 AI Assistant <span style="font-size:0.75em; color:#6b7280; margin-left:auto;">Typing...</span></div><div class="streaming-content"><span class="typing-indicator"></span><span class="typing-indicator"></span><span class="typing-indicator"></span></div></div>''', unsafe_allow_html=True)
            full_response = ""; token_usage = {}
            if st.session_state.response_mode == 'Stream':
                try:
                    for chunk in get_chat_response_stream(prompt.strip()):
                        if isinstance(chunk, tuple) and chunk[0] == "FINAL_TOKEN_USAGE":
                            token_usage = chunk[1]
                        elif isinstance(chunk, str):
                            full_response += chunk
                            escaped_response = full_response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                            response_placeholder.markdown(f'<div class="streaming-message"><div class="streaming-header">🤖 AI Assistant <span style="font-size:0.75em; color:#6b7280; margin-left:auto;">{datetime.now().strftime("%H:%M:%S")}</span></div><div class="streaming-content">{escaped_response}</div></div>', unsafe_allow_html=True)
                            import time; time.sleep(0.01)
                    response_placeholder.empty()
                except Exception as e:
                    response_placeholder.error(f"Error during streaming: {e}")
                    full_response, token_usage = get_chat_response(prompt.strip())
            else:
                try:
                    # full_response, token_usage = get_chat_response_gpt5_response(prompt.strip())
                    full_response, token_usage = get_chat_response_gpt5(prompt.strip())
                    escaped_response = full_response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                    response_placeholder.markdown(f'<div class="streaming-message"><div class="streaming-header">🧠 Reasoning (GPT-5) <span style="font-size:0.75em; color:#6b7280; margin-left:auto;">{datetime.now().strftime("%H:%M:%S")}</span></div><div class="streaming-content">{escaped_response}</div></div>', unsafe_allow_html=True)
                except Exception as e:
                    response_placeholder.error(f"Error during reasoning request: {e}")
                    full_response = f"Error: {e}"; token_usage = {}
            if token_usage:
                st.session_state.total_session_tokens['prompt_tokens'] += token_usage.get('prompt_tokens', 0)
                st.session_state.total_session_tokens['completion_tokens'] += token_usage.get('completion_tokens', 0)
                st.session_state.total_session_tokens['total_tokens'] += token_usage.get('total_tokens', 0)
            assistant_message = {"role": "assistant", "content": full_response, "timestamp": datetime.now().strftime("%H:%M:%S"), "token_usage": token_usage, "mode": st.session_state.response_mode}
            st.session_state.chat_history.append(assistant_message)
            if len(st.session_state.chat_history) > 50:
                st.session_state.chat_history = st.session_state.chat_history[-50:]
            st.session_state.processing = False
            st.rerun()

        # Auto-scroll script (runs every render) and close wrappers
        components.html("""
        <script>
        (function(){
           const chat = parent.document.querySelector('.chat-container');
           if(chat){ chat.scrollTop = chat.scrollHeight; }
        })();
        </script>
        """, height=0)
        st.markdown('</div>', unsafe_allow_html=True)  # close input container
        st.markdown('</div>', unsafe_allow_html=True)  # close chat-flex-wrapper
    
    with main_col2:
        # Statistics Panel - with compact sidebar
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📊 Chat Statistics</h3>', unsafe_allow_html=True)
        
        # Conversation count
        conversation_count = len(st.session_state.chat_history) // 2
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #f59e0b; margin: 0; font-size: 1.0em;">{conversation_count}</h3>
            <p style="margin: 3px 0 0 0; font-size: 0.7em;">Conversations</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Total messages
        total_messages = len(st.session_state.chat_history)
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #10b981; margin: 0; font-size: 1.0em;">{total_messages}</h3>
            <p style="margin: 3px 0 0 0; font-size: 0.7em;">Total Messages</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Session Token Usage
        session_tokens = st.session_state.total_session_tokens
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #0ea5e9; margin: 0; font-size: 0.9em;">{session_tokens['total_tokens']}</h3>
            <p style="margin: 3px 0 0 0; font-size: 0.7em;">Session Tokens</p>
            <p style="margin: 1px 0 0 0; font-size: 0.6em; color: #6b7280;">
                {session_tokens['prompt_tokens']} prompt + {session_tokens['completion_tokens']} completion
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Status
        status_color = "#f59e0b" if st.session_state.processing else "#10b981"
        status_text = "Processing..." if st.session_state.processing else "Ready"
        st.markdown(f'''
        <div class="stats-container" style="padding: 8px; margin: 5px 0;">
            <h4 style="color: {status_color}; margin: 0; font-size: 0.9em;">Status: {status_text}</h4>
        </div>
        ''', unsafe_allow_html=True)
        
        # Recent activity - more compact
        if st.session_state.chat_history:
            st.markdown('<h4 class="section-title" style="font-size: 0.9em;">📝 Recent Activity</h4>', unsafe_allow_html=True)
            recent_messages = st.session_state.chat_history[-4:]  # Last 2 conversations
            
            for msg in recent_messages:
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                
                # Show token info for assistant messages
                token_info = ""
                if msg["role"] == "assistant" and msg.get("token_usage"):
                    tokens = msg["token_usage"].get("total_tokens", 0)
                    token_info = f"<br><span style='color: #0ea5e9; font-size: 0.55em;'>🔢 {tokens} tokens</span>"
                
                st.markdown(f"""
                <div style="background: white; padding: 6px; border-radius: 4px; margin: 2px 0; border-left: 2px solid #f59e0b;">
                    <strong style="font-size: 0.65em;">{role_icon} {msg["timestamp"]}</strong><br>
                    <small style="font-size: 0.6em;">{content_preview}</small>{token_info}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main_screen()