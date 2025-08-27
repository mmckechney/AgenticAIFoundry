import asyncio
from datetime import datetime
import time
import os, json
import pandas as pd
from typing import Any, Callable, Set, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval
import streamlit as st
from html import escape as _html_escape
from dotenv import load_dotenv
import tempfile
import uuid
import requests
import io
import re
import html

load_dotenv()

import logging

endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini
WHISPER_DEPLOYMENT_NAME = "whisper"
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 

# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-10-21",
)

from azure.monitor.opentelemetry import configure_azure_monitor
connection_string = project_client.telemetry.get_application_insights_connection_string()

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection


from opentelemetry import trace
tracer = trace.get_tracer(__name__)

CHAT_DEPLOYMENT_NAME="o3-mini"

def msft_generate_chat_response(query):
    """Generate a chat response using Azure OpenAI with tool calls."""
    
    prompt = f"""
    You are a task planner AI assistant specialized in building 3D object models using Universal Scene Description (USD) code.

    IMPORTANT: Act as a task planner. For any user query to build a 3D scene or model, break it down into steps:
    1. Identify the key objects/components needed for the scene (e.g., for a conference room: table, chairs, projector, etc.).
    2. For each object, generate clean, functional OpenUSD code to define it.
    3. Assemble all objects into a complete scene by combining them under a root Xform, applying transforms for positioning.
    
    Always generate actual OpenUSD code for the final assembled scene. Format your response as follows:
    - Step 1: List of objects needed
    - Step 2: Individual OpenUSD code snippets for each object
    - Step 3: Complete assembled OpenUSD code in ```usda code blocks
    - Additional tips or variations if helpful

    Generate clean, functional OpenUSD (.usda) code that includes:
    - Proper #usda 1.0 header
    - def statements for primitives
    - Xform, Mesh, Sphere, Cube, or other USD primitives
    - Materials and shaders when appropriate
    - Transform matrices for positioning

    User Query: {query}
    
    Example format for a simple scene:
    Step 1: Objects needed - Sphere and Cube
    
    Step 2: Individual objects
    - Sphere:
    def Sphere "MySphere" {{
        double radius = 1.0
    }}
    - Cube:
    def Cube "MyCube" {{
        double size = 2.0
    }}
    
    Step 3: Assembled scene
    ```usda
    #usda 1.0
    
    def Xform "World"
    {{
        def Sphere "MySphere"
        {{
            double radius = 1.0
            matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
        }}
        
        def Cube "MyCube"
        {{
            double size = 2.0
            matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (5, 0, 0, 1) )
        }}
    }}
    """
    
    try:
        # Use simple OpenAI chat completion instead of MCP
        # simple_client = AzureOpenAI(
        #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        #     api_key=os.getenv("AZURE_OPENAI_KEY"),
        #     api_version="2024-12-01-preview"
        # )

        simple_client = AzureOpenAI(  
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
            api_key= os.getenv("AZURE_OPENAI_KEY"),
            api_version="preview"
            )
        
        messages = [
            {"role": "system", "content": "You are a specialized OpenUSD code generator. Always provide functional USD code in your responses wrapped in ```usda code blocks."},
            {"role": "user", "content": prompt}
        ]
        
        # response = simple_client.chat.completions.create(
        #     model=CHAT_DEPLOYMENT_NAME,
        #     messages=messages,
        #     max_tokens=2000,
        #     temperature=0.7
        # )
        
        # result = response.choices[0].message.content.strip()
        # print(f"Response: {result}")
        response = simple_client.responses.create(
            model=CHAT_DEPLOYMENT_NAME,
            input=messages,
            max_output_tokens= 2000,
            instructions="Generate functional OpenUSD code wrapped in ```usda code blocks. Always include complete, working USD scenes.",
        )

        result = response.output_text 

        return result
        
    except Exception as e:
        print(f"Error in simple client, falling back to MCP: {e}")
        
        # Fallback to original MCP method
        mcpclient = AzureOpenAI(  
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
            api_key= os.getenv("AZURE_OPENAI_KEY"),
            api_version="preview"
            )

        response = mcpclient.responses.create(
            model=CHAT_DEPLOYMENT_NAME,
            # tools=[
            #     {
            #         "type": "mcp",
            #         "server_label": "MicrosoftLearn",
            #         "server_url": "https://learn.microsoft.com/api/mcp",
            #         "require_approval": "never"
            #     },
            # ],
            input=prompt,
            max_output_tokens= 2000,
            instructions="Generate functional OpenUSD code wrapped in ```usda code blocks. Always include complete, working USD scenes.",
        )
        
        retturntxt = response.output_text    
        print(f"MCP Response: {retturntxt}")
        return retturntxt
    
def extract_clean_usd_code(content: str) -> str:
    """Extract clean OpenUSD code from assistant response."""
    
    if not content:
        return ""
    
    content = content.strip()
    
    # Simple approach: Find ```usda and extract everything until the next ```
    if "```usda" in content:
        start_marker = "```usda"
        start_pos = content.find(start_marker)
        if start_pos != -1:
            # Find the start of the actual code (after the marker and newline)
            code_start = start_pos + len(start_marker)
            if content[code_start:code_start+1] == '\n':
                code_start += 1
            
            # Find the end marker
            end_pos = content.find("```", code_start)
            if end_pos != -1:
                raw_code = content[code_start:end_pos]
                return raw_code
    
    # Fallback: Look for any ``` block that contains #usda
    if "```" in content:
        parts = content.split("```")
        for i in range(1, len(parts), 2):  # Odd indices are code blocks
            code_block = parts[i]
            if "#usda" in code_block:
                return code_block
    
    # Last resort: Extract from #usda to end of meaningful content
    if "#usda" in content:
        start_pos = content.find("#usda")
        if start_pos != -1:
            # Take everything from #usda onwards, but stop at common end markers
            remaining = content[start_pos:]
            
            # Stop at common end patterns
            end_markers = ["\n\n**", "\n**Tips", "\n**Variations", "\nTips:", "\nHere"]
            end_pos = len(remaining)
            
            for marker in end_markers:
                marker_pos = remaining.find(marker)
                if marker_pos != -1 and marker_pos < end_pos:
                    end_pos = marker_pos
            
            return remaining[:end_pos].strip()
    
    return ""


def digitaltwin_main():
    # Configure page settings
    st.set_page_config(
        page_title="OpenUSD Digital Twin Assistant",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Professional CSS styling
    st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.1rem;
        margin: 0;
        font-weight: 300;
    }
    
    /* Chat container styling */
    .chat-container {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    /* Dynamic height: full viewport minus header + input area (approx) */
    height: calc(80vh - 360px);
    overflow-y: auto;
    }
    
    /* Individual message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px 50px;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        color: #1a202c;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 50px 10px 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        word-wrap: break-word;
    }
    
    /* Code output styling */
    .usd-code-container {
        background: linear-gradient(145deg, #1a202c 0%, #2d3748 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid #4a5568;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .usd-code-container pre {
        background: transparent !important;
        border: none !important;
        color: #e2e8f0 !important;
        font-family: 'Fira Code', 'Consolas', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Message header styling */
    .message-header {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 8px;
        opacity: 0.8;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Statistics and metrics */
    .stats-container {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Input area styling */
    .input-section {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Custom scrollbar */
    .chat-container::-webkit-scrollbar,
    .usd-code-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track,
    .usd-code-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb,
    .usd-code-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Success/Error message styling */
    .success-message {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 3px 10px rgba(72, 187, 120, 0.3);
    }
    
    .error-message {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 3px 10px rgba(245, 101, 101, 0.3);
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.7);
        margin-left: auto;
    }
    
    .timestamp-assistant {
        font-size: 0.7rem;
        color: #64748b;
        margin-left: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # Inject sticky chat input CSS (after base styles to override if needed)
    st.markdown(
        """
        <style>
        /* Sticky chat input */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(6px);
            padding: 0.75rem 2rem 1rem 2rem;
            border-top: 1px solid #e2e8f0;
            z-index: 1000;
        }
        div[data-testid="stChatInput"] textarea {
            min-height: 60px;
        }
        /* Add bottom padding so content not hidden behind sticky bar */
        .stApp .block-container { padding-bottom: 140px !important; }
        @media (max-width: 900px) {
            .chat-container { height: calc(80vh - 400px); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'total_messages' not in st.session_state:
        st.session_state.total_messages = 0
    if 'total_usd_codes' not in st.session_state:
        st.session_state.total_usd_codes = 0
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ OpenUSD Digital Twin Assistant</h1>
        <p>Generate 3D scenes and digital twins with AI-powered OpenUSD code</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create layout columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat History Display
        st.markdown("### 💬 Conversation History")
        
        # Create scrollable chat container
        chat_html = '<div class="chat-container">'
        
        if st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    escaped_user_content = message["content"].replace('\n', '<br>')
                    escaped_user_content = html.escape(escaped_user_content).replace('&lt;br&gt;', '<br>')
                    chat_html += f'''
                    <div class="user-message">
                        <div class="message-header">
                            👤 You
                            <span class="timestamp">{message.get("timestamp", "")}</span>
                        </div>
                        {escaped_user_content}
                    </div>'''
                else:
                    # Check if the response contains USD code
                    content = message["content"]
                    
                    # Extract clean USD code
                    clean_usd_code = extract_clean_usd_code(content)
                    print('clean_usd_code:', clean_usd_code)
                    
                    if clean_usd_code:
                        # Remove the code block from the content to get just the explanatory text
                        text_content = content
                        
                        # Remove various code block formats
                        if f"```usda\n{clean_usd_code}\n```" in text_content:
                            text_content = text_content.replace(f"```usda\n{clean_usd_code}\n```", "")
                        elif f"```usd\n{clean_usd_code}\n```" in text_content:
                            text_content = text_content.replace(f"```usd\n{clean_usd_code}\n```", "")
                        elif f"```\n{clean_usd_code}\n```" in text_content:
                            text_content = text_content.replace(f"```\n{clean_usd_code}\n```", "")
                        elif f"```{clean_usd_code}```" in text_content:
                            text_content = text_content.replace(f"```{clean_usd_code}```", "")
                        
                        # Clean up extra whitespace and format
                        text_content = text_content.strip()
                        # Convert line breaks to HTML breaks for proper display
                        text_content = text_content.replace('\n', '<br>')
                        text_content = html.escape(text_content).replace('&lt;br&gt;', '<br>')
                        
                        if text_content:
                            chat_html += f'''
                            <div class="assistant-message">
                                <div class="message-header">
                                    🤖 OpenUSD Assistant
                                    <span class="timestamp-assistant">{message.get("timestamp", "")}</span>
                                </div>
                                {text_content}
                            </div>'''
                        
                        # Display clean USD code - RAW without HTML escaping
                        chat_html += f'''
                        <div class="usd-code-container">
                            <div style="color: #a0aec0; font-size: 0.85rem; margin-bottom: 10px;">
                                📄 Generated OpenUSD Code:
                            </div>
                            <pre>{clean_usd_code}</pre>
                        </div>'''
                    else:
                        # No USD code detected - show full response with debug info
                        escaped_content = content.replace('\n', '<br>')
                        escaped_content = html.escape(escaped_content).replace('&lt;br&gt;', '<br>')
                        chat_html += f'''
                        <div class="assistant-message">
                            <div class="message-header">
                                🤖 OpenUSD Assistant
                                <span class="timestamp-assistant">{message.get("timestamp", "")}</span>
                            </div>
                            {escaped_content}
                        </div>'''
                        
                        # Add debug info if no USD code found
                        chat_html += f'''
                        <div style="
                            background: #fef3c7;
                            border: 1px solid #f59e0b;
                            border-radius: 8px;
                            padding: 10px;
                            margin: 10px 0;
                            font-size: 0.85rem;
                            color: #92400e;
                        ">
                            💡 <strong>Debug:</strong> No OpenUSD code detected in response. 
                            Try asking more specifically like "Generate OpenUSD code for a blue cube" or "Create a USD scene with a sphere".
                        </div>'''
        else:
            chat_html += '''
            <div style="text-align: center; color: #64748b; padding: 100px 20px;">
                <h3>🚀 Welcome to OpenUSD Digital Twin Assistant!</h3>
                <p>Start by describing the 3D scene or digital twin you'd like to create.</p>
                <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 20px;">
                    <p><strong>Example prompts:</strong></p>
                    <ul style="text-align: left; display: inline-block; margin: 0;">
                        <li>"Generate OpenUSD code for a red cube"</li>
                        <li>"Create a USD scene with a sphere and lighting"</li>
                        <li>"Build a house with windows using OpenUSD"</li>
                        <li>"Make a car model in USD format"</li>
                        <li>"Create a digital twin of a robot arm"</li>
                    </ul>
                </div>
            </div>'''
        
        chat_html += '</div>'
        st.html(chat_html)

        # --- OpenUSD Rendering (latest scene) ---
        latest_usd_code = get_latest_usd_code()
        if latest_usd_code:
            with st.expander("🖼 Render Latest OpenUSD Scene", expanded=True):
                prims = parse_usd_prims(latest_usd_code)
                if prims:
                    render_usd_scene(prims)
                else:
                    st.info("No supported primitives (Sphere / Cube with optional Xform) detected to render.")
        
        # Input Section
        st.markdown("### 💭 Describe Your 3D Scene")
        with st.container():
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            
            # Chat input
            if prompt := st.chat_input("Generate OpenUSD code for... (e.g., 'Create a red cube', 'Build a house with windows')"):
                if not st.session_state.processing:
                    process_usd_request(prompt)
            
            # Additional controls
            col_input1, col_input2 = st.columns([3, 1])
            with col_input1:
                st.markdown("💡 **Tips:** Be specific about shapes, materials, colors, and positioning for better results.")
            
            with col_input2:
                if st.button("🗑️ Clear History"):
                    st.session_state.chat_history = []
                    st.session_state.total_messages = 0
                    st.session_state.total_usd_codes = 0
                    st.success("Chat history cleared!")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Statistics and Info Panel
        st.markdown("### 📊 Session Statistics")
        
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        
        # Metrics
        col_metric1, col_metric2 = st.columns(2)
        
        with col_metric1:
            total_conversations = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{total_conversations}</div>
                <div class="metric-label">Conversations</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_metric2:
            usd_codes_generated = len([msg for msg in st.session_state.chat_history if msg["role"] == "assistant" and extract_clean_usd_code(msg["content"])])
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{usd_codes_generated}</div>
                <div class="metric-label">USD Codes</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processing Status
        if st.session_state.processing:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 3px 10px rgba(251, 191, 36, 0.3);
                margin: 15px 0;
            ">
                <strong>🔄 Generating OpenUSD Code...</strong><br>
                <small>Please wait while the AI creates your 3D scene</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.session_state.chat_history:
            # Export chat history
            chat_export = create_chat_export()
            st.download_button(
                label="📄 Export Chat",
                data=chat_export,
                file_name=f"openUSD_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # Export latest USD code
            latest_usd_code = get_latest_usd_code()
            if latest_usd_code:
                st.download_button(
                    label="💾 Export USD Code",
                    data=latest_usd_code,
                    file_name=f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.usda",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Information Panel
        st.markdown("### ℹ️ About OpenUSD")
        st.markdown("""
        **Universal Scene Description (USD)** is a framework for interchange of 3D computer graphics data.
        
        **Features:**
        - 🎯 Professional 3D scene generation
        - 🏗️ Digital twin creation
        - 🎨 Material and lighting setup
        - 📐 Precise geometry definition
        - 🔄 Real-time collaboration
        
        **Tips for better results:**
        - Be specific about shapes and dimensions
        - Mention materials and colors
        - Describe spatial relationships
        - Include lighting preferences
        """)


def process_usd_request(user_input: str):
    """Process a USD generation request through the AI assistant."""
    
    # Set processing state
    st.session_state.processing = True
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Maintain only last 10 conversations (20 messages total - 10 user + 10 assistant)
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]
    
    # Show processing indicator
    with st.spinner("🏗️ Generating OpenUSD code for your 3D scene...", show_time=True):
        try:
            # Call the USD generation function
            response = msft_generate_chat_response(user_input)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Update statistics
            st.session_state.total_messages += 1
            if extract_clean_usd_code(response):
                st.session_state.total_usd_codes += 1
            
            # Reset processing state
            st.session_state.processing = False
            
            # Rerun to update the UI
            st.rerun()
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ Error generating USD code: {str(e)}")
            
            # Add error message to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ Sorry, I encountered an error while generating the OpenUSD code: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()


def create_chat_export():
    """Create exportable text of the chat history."""
    export_text = f"OpenUSD Digital Twin Assistant - Chat Export\n"
    export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_text += "=" * 50 + "\n\n"
    
    for i, message in enumerate(st.session_state.chat_history):
        role = "User" if message["role"] == "user" else "OpenUSD Assistant"
        timestamp = message.get("timestamp", "")
        export_text += f"{role} ({timestamp}):\n{message['content']}\n\n"
        export_text += "-" * 30 + "\n\n"
    
    return export_text


def get_latest_usd_code():
    """Extract the latest USD code from chat history."""
    for message in reversed(st.session_state.chat_history):
        if message["role"] == "assistant":
            content = message["content"]
            clean_code = extract_clean_usd_code(content)
            if clean_code:
                return clean_code
    return None

# ---------------- Rendering Utilities -----------------
import random, json as _json, re as _re

USD_SPHERE_RE = _re.compile(r'def\s+Sphere\s+"(?P<name>[^"]+)"[^{]*{(?P<body>[^}]*)}', _re.MULTILINE | _re.DOTALL)
USD_CUBE_RE = _re.compile(r'def\s+Cube\s+"(?P<name>[^"]+)"[^{]*{(?P<body>[^}]*)}', _re.MULTILINE | _re.DOTALL)
USD_XFORM_RE = _re.compile(r'def\s+Xform\s+"(?P<name>[^"]+)"[^{]*{(?P<body>[^}]*)}', _re.MULTILINE | _re.DOTALL)

def _extract_translate(xform_body:str):
    # crude parse of xformOp:translate = (x, y, z)
    m = _re.search(r'xformOp:translate\s*=\s*\(([^)]+)\)', xform_body)
    if m:
        parts = [p.strip() for p in m.group(1).split(',')]
        if len(parts) == 3:
            try:
                return [float(parts[0]), float(parts[1]), float(parts[2])]
            except:
                return [0,0,0]
    return [0,0,0]

def parse_usd_prims(usd_code:str):
    """Very lightweight USD parser for simple Sphere / Cube prims inside optional Xforms.
    Returns list of dicts: {type, name, position[x,y,z], size|radius}
    """
    prims = []
    # Map of child prim names to translation from parent Xform
    xform_positions = {}
    for xm in USD_XFORM_RE.finditer(usd_code):
        xname = xm.group('name')
        body = xm.group('body')
        t = _extract_translate(body)
        # Track for any nested child mention (simplified: if child defined inside we add translation)
        for sm in USD_SPHERE_RE.finditer(body):
            cname = sm.group('name')
            xform_positions[cname] = t
        for cm in USD_CUBE_RE.finditer(body):
            cname = cm.group('name')
            xform_positions[cname] = t

    for sm in USD_SPHERE_RE.finditer(usd_code):
        name = sm.group('name')
        body = sm.group('body')
        rad_match = _re.search(r'radius\s*=\s*([0-9.+-eE]+)', body)
        radius = float(rad_match.group(1)) if rad_match else 1.0
        pos = xform_positions.get(name, [0,0,0])
        prims.append({"type":"sphere", "name":name, "radius":radius, "position":pos})
    for cm in USD_CUBE_RE.finditer(usd_code):
        name = cm.group('name')
        body = cm.group('body')
        # extent or size not always given; default 1
        size_match = _re.search(r'size\s*=\s*([0-9.+-eE]+)', body)
        size = float(size_match.group(1)) if size_match else 1.0
        pos = xform_positions.get(name, [0,0,0])
        prims.append({"type":"cube", "name":name, "size":size, "position":pos})
    return prims

def render_usd_scene(prims:List[Dict[str,Any]]):
    """Render simple USD prims using Three.js via Streamlit components."""
    scene_data = _json.dumps(prims)
    prim_count = len(prims)
    html_viewer = """
<div id='usd-viewer' style='width:100%;height:400px;border:1px solid #e2e8f0;border-radius:8px;position:relative;background:#111;'>
    <div style='position:absolute;top:8px;left:12px;color:#fff;font:12px/1.2 monospace;z-index:10;'>Scene Primitives: __PRIM_COUNT__</div>
</div>
<script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js'></script>
<script>
    const data = __SCENE_DATA__;
    const container = document.getElementById('usd-viewer');
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);
    const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.1, 1000);
    camera.position.set(4,4,6);
    const hemi = new THREE.HemisphereLight(0xffffff,0x222222,1.0); scene.add(hemi);
    const dir = new THREE.DirectionalLight(0xffffff,0.8); dir.position.set(5,10,7); scene.add(dir);
    const group = new THREE.Group(); scene.add(group);
    const rndColor = () => new THREE.Color().setHSL(Math.random(),0.6,0.55);
    data.forEach(p => {
        let mesh;
        if (p.type === 'sphere') {
            const geo = new THREE.SphereGeometry(p.radius,32,32);
            const mat = new THREE.MeshStandardMaterial({ color: rndColor() });
            mesh = new THREE.Mesh(geo,mat);
        } else if (p.type === 'cube') {
            const geo = new THREE.BoxGeometry(p.size,p.size,p.size);
            const mat = new THREE.MeshStandardMaterial({ color: rndColor() });
            mesh = new THREE.Mesh(geo,mat);
        }
        if (mesh) {
            const pos = p.position || [0,0,0];
            mesh.position.set(pos[0], pos[1], pos[2]);
            mesh.userData = p;
            group.add(mesh);
        }
    });
    // simple orbit (drag)
    let isDown=false, prevX=0, prevY=0, rotY=0, rotX=0;
    container.addEventListener('mousedown', e => { isDown=true; prevX=e.clientX; prevY=e.clientY; });
    window.addEventListener('mouseup', () => { isDown=false; });
    window.addEventListener('mousemove', e => { if(!isDown) return; const dx=e.clientX-prevX; const dy=e.clientY-prevY; rotY+=dx*0.005; rotX+=dy*0.005; prevX=e.clientX; prevY=e.clientY; group.rotation.y=rotY; group.rotation.x=rotX; });
    function animate(){ requestAnimationFrame(animate); renderer.render(scene,camera); }
    animate();
    window.addEventListener('resize', () => { const w=container.clientWidth, h=container.clientHeight; renderer.setSize(w,h); camera.aspect=w/h; camera.updateProjectionMatrix(); });
</script>
<div style='font-size:0.75rem;color:#64748b;margin-top:4px;'>Simple preview (Sphere/Cube). For full USD features integrate a dedicated USD viewer.</div>
"""
    html_viewer = html_viewer.replace('__PRIM_COUNT__', str(prim_count)).replace('__SCENE_DATA__', scene_data)
    st.html(html_viewer)


if __name__ == "__main__":
    digitaltwin_main()