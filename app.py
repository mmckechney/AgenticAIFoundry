import streamlit as st
import asyncio
import io
import os
import time
import base64
from datetime import datetime
from typing import Optional, Dict, Any
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Import the main functions from agenticai.py
# Handle missing dependencies gracefully for demo purposes
try:
    from agenticai import (
        code_interpreter,
        eval as ai_eval,
        redteam,
        agent_eval,
        connected_agent,
        ai_search_agent,
        delete_agent,
        process_message_reasoning,
        existing_connected_agent,
        aiactionplat_agent,
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ Some Azure AI dependencies are not installed: {e}")
    st.info("Running in demo mode with simulated responses.")
    DEPENDENCIES_AVAILABLE = False

from stasses import assesmentmain
from stfinetuneasses import finetuneassesment

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
project_endpoint = os.environ["PROJECT_ENDPOINT"]
# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)


from azure.monitor.opentelemetry import configure_azure_monitor
# connection_string = project_client.telemetry.get_application_insights_connection_string()
connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

from bbmcp import main

# Configure Streamlit page with Material Design 3 theme
st.set_page_config(
    page_title="AgenticAI Foundry",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Material Design 3 CSS styling
st.markdown("""
<style>
    /* Material Design 3 Color Scheme */
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
        --md-sys-color-outline: #79747E;
        --md-sys-color-outline-variant: #CAC4D0;
        --md-sys-color-success: #00A86B;
        --md-sys-color-warning: #FF8F00;
        --md-sys-color-error: #BA1A1A;
    }

    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, var(--md-sys-color-surface) 0%, var(--md-sys-color-primary-container) 100%);
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-tertiary) 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(103, 80, 164, 0.2);
        text-align: center;
    }

    .main-header h1 {
        color: var(--md-sys-color-on-primary);
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .main-header p {
        color: var(--md-sys-color-on-primary);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    /* Card container styling */
    .card-container {
        background: var(--md-sys-color-surface);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid var(--md-sys-color-outline-variant);
        transition: all 0.3s ease;
    }

    .card-container:hover {
        box-shadow: 0 4px 20px rgba(103, 80, 164, 0.12);
        transform: translateY(-2px);
    }

    /* Button styling with Material Design 3 */
    .stButton > button {
        background: var(--md-sys-color-primary) !important;
        color: var(--md-sys-color-on-primary) !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(103, 80, 164, 0.2) !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }

    .stButton > button:hover {
        background: #5a4593 !important;
        box-shadow: 0 4px 16px rgba(103, 80, 164, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(103, 80, 164, 0.2) !important;
    }

    /* Feature card styling */
    .feature-card {
        background: var(--md-sys-color-surface);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--md-sys-color-primary);
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        box-shadow: 0 4px 20px rgba(103, 80, 164, 0.12);
        transform: translateX(4px);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .feature-title {
        color: var(--md-sys-color-primary);
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: var(--md-sys-color-on-surface-variant);
        font-size: 0.9rem;
        line-height: 1.4;
    }

    /* Status indicators */
    .status-success {
        background: var(--md-sys-color-success);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .status-warning {
        background: var(--md-sys-color-warning);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* Spinner customization */
    .stSpinner {
        color: var(--md-sys-color-primary) !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: var(--md-sys-color-surface) !important;
    }

    /* Progress indicators */
    .workflow-step {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        color: var(--md-sys-color-on-surface-variant);
    }

    .workflow-step.active {
        color: var(--md-sys-color-primary);
        font-weight: 600;
    }

    .workflow-connector {
        height: 2px;
        background: var(--md-sys-color-outline-variant);
        margin: 0.5rem 0;
    }

    .workflow-connector.active {
        background: var(--md-sys-color-primary);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if "show_mcp_chat" not in st.session_state:
        st.session_state.show_mcp_chat = False
    if "mcp_messages" not in st.session_state:
        st.session_state.mcp_messages = []
    if "show_ai_assessment" not in st.session_state:
        st.session_state.show_ai_assessment = False
    if "show_finetune_assessment" not in st.session_state:
        st.session_state.show_finetune_assessment = False
    
    # Main header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AgenticAI Foundry</h1>
        <p>Enterprise-Grade AI Agent Development Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Workflow overview
    st.markdown("""
    <div class="card-container">
        <h3 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🔄 AI Development Workflow</h3>
        <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
            <span class="workflow-step">📝 Code Interpreter</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">📊 AI Evaluation</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">🛡️ RedTeam Testing</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">✅ Agent Evaluation</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">🔗 MCP Servers</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">🌐 Connected Agents</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">🗑️ Cleanup</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🚀 Agent Operations")

        # Assessment Phase
        with st.expander("📝 Assessment Phase", expanded=True):
            # Create a scrollable container for the assessment content
            st.markdown("""
            <div style="
                max-height: 600px; 
                overflow-y: auto; 
                padding: 15px; 
                border: 1px solid var(--md-sys-color-outline-variant); 
                border-radius: 12px;
                background: var(--md-sys-color-surface);
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                margin: 10px 0;
            ">
            """, unsafe_allow_html=True)
            
            col_eval1, col_eval2 = st.columns(2)

            with col_eval1:
                st.markdown("### 🎯 AI Maturity Assessment")
                st.write("Evaluate your organization's AI maturity across key dimensions")
                
                if st.button("📊 Start AI Maturity Assessment", key="start_assessment"):
                    st.session_state.show_ai_assessment = True
                    st.session_state.show_finetune_assessment = False
                    st.rerun()

            with col_eval2:
                st.markdown("### 🔧 Fine-Tuning Assessment")
                st.write("Get personalized guidance for AI model fine-tuning")
                
                if st.button("📊 Start Fine Tuning Assessment", key="start_finetuneassesment"):
                    st.session_state.show_finetune_assessment = True
                    st.session_state.show_ai_assessment = False
                    st.rerun()
            
            # Display the selected assessment
            if st.session_state.get("show_ai_assessment", False):
                st.markdown("---")
                st.markdown("### 🤖 AI Maturity Assessment")
                try:
                    assesmentmain()
                except Exception as e:
                    st.error(f"Error loading AI assessment: {str(e)}")
                    if st.button("� Retry AI Assessment", key="retry_ai_assessment"):
                        st.rerun()
            
            elif st.session_state.get("show_finetune_assessment", False):
                st.markdown("---")
                st.markdown("### 🔧 Fine-Tuning Assessment")
                try:
                    finetuneassesment()
                except Exception as e:
                    st.error(f"Error loading fine-tuning assessment: {str(e)}")
                    if st.button("🔄 Retry Fine-Tuning Assessment", key="retry_finetune_assessment"):
                        st.rerun()
            
            # Close assessment buttons
            if st.session_state.get("show_ai_assessment", False) or st.session_state.get("show_finetune_assessment", False):
                st.markdown("---")
                col_close1, col_close2, col_close3 = st.columns([1, 1, 1])
                with col_close2:
                    if st.button("❌ Close Assessment", key="close_assessment"):
                        st.session_state.show_ai_assessment = False
                        st.session_state.show_finetune_assessment = False
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Development Phase
        with st.expander("🔧 Development Phase", expanded=True):
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">📝</span>
                <div class="feature-title">Code Interpreter</div>
                <div class="feature-description">Execute and validate your AI agent code with our intelligent interpreter</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Execute Code Interpreter", key="code_interpreter"):
                with st.spinner("🔄 Executing code interpreter...", show_time=True):
                    if DEPENDENCIES_AVAILABLE:
                        code_interpreter()
                        st.success("✅ Code interpreter executed successfully!")
                    else:
                        time.sleep(2)  # Simulate processing
                        st.success("✅ Code interpreter executed successfully! (Demo mode)")

        # Evaluation Phase
        with st.expander("📊 Evaluation Phase", expanded=True):
            col_eval1, col_eval2 = st.columns(2)
            
            with col_eval1:
                st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">📊</span>
                    <div class="feature-title">AI Evaluation</div>
                    <div class="feature-description">Comprehensive performance analysis of your AI agents</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📈 Run AI Evaluation", key="ai_eval"):
                    with st.spinner("🔄 Running AI evaluation...", show_time=True):
                        if DEPENDENCIES_AVAILABLE:
                            evalrs = ai_eval()
                            # st.json(evalrs)
                            st.write(evalrs)
                        else:
                            time.sleep(3)
                            st.success("✅ AI evaluation completed! (Demo mode)")

            with col_eval2:
                st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">✅</span>
                    <div class="feature-title">Agent Evaluation</div>
                    <div class="feature-description">Detailed agent performance metrics and insights</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔍 Evaluate Agent", key="agent_eval"):
                    with st.spinner("🔄 Running agent evaluation...", show_time=True):
                        if DEPENDENCIES_AVAILABLE:
                            agent_evalrs = agent_eval()
                            st.json(agent_evalrs)
                        else:
                            time.sleep(3)
                            st.success("✅ Agent evaluation completed! (Demo mode)")

        # Security Phase
        with st.expander("🛡️ Security Testing", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🛡️</span>
                <div class="feature-title">RedTeam Agent</div>
                <div class="feature-description">Advanced security testing and vulnerability assessment</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔒 Launch RedTeam Testing", key="redteam"):
                with st.spinner("🔄 Running RedTeam security analysis...", show_time=True):
                    if DEPENDENCIES_AVAILABLE:
                        redteamrs = asyncio.run(redteam())
                        # st.json(redteamrs)
                        st.write(redteamrs)
                    else:
                        time.sleep(4)
                        st.success("✅ Security testing completed! (Demo mode)")

        # MCP Servers Phase
        with st.expander("🔗 MCP Server Integration", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🔗</span>
                <div class="feature-title">Model Context Protocol (MCP) Servers</div>
                <div class="feature-description">Connect to external MCP servers for enhanced capabilities</div>
            </div>
            """, unsafe_allow_html=True)
            
            # MCP Server options
            col_mcp1, col_mcp2 = st.columns(2)
            
            with col_mcp1:
                mcp_options = ['Microsoft Learn', 'Github', 'HuggingFace']
                selected_mcp = st.selectbox(
                    "🌐 Choose MCP Server:", 
                    mcp_options,
                    key="mcp_server_select",
                    help="Select which Model Context Protocol server to connect to"
                )
            
            with col_mcp2:
                mcp_query = st.text_input(
                    "💭 MCP Query:", 
                    value="Tell me about Azure AI services",
                    key="mcp_query_input",
                    help="Enter your query for the MCP server"
                )
            
            if st.button("🚀 Connect to MCP Server", key="mcp_server"):
                with st.spinner(f"🔄 Connecting to {selected_mcp} MCP server...", show_time=True):
                    if DEPENDENCIES_AVAILABLE:
                        try:
                            # Import the MCP functions from bbmcp
                            from bbmcp import msft_generate_chat_response, bbgithub_generate_chat_response, hf_generate_chat_response
                            
                            if selected_mcp == 'Microsoft Learn':
                                mcp_response, _ = msft_generate_chat_response(mcp_query, "")
                                st.success("✅ Connected to Microsoft Learn MCP server!")
                                st.write("**MCP Server Response:**")
                                st.info(mcp_response)
                            elif selected_mcp == 'Github':
                                mcp_response, _ = bbgithub_generate_chat_response(mcp_query, "")
                                st.success("✅ Connected to GitHub MCP server!")
                                st.write("**MCP Server Response:**")
                                st.info(mcp_response)
                            elif selected_mcp == 'HuggingFace':
                                mcp_response, _ = hf_generate_chat_response(mcp_query, "")
                                st.success("✅ Connected to HuggingFace MCP server!")
                                st.write("**MCP Server Response:**")
                                st.info(mcp_response)
                        except ImportError as e:
                            st.error(f"❌ Error importing MCP functions: {e}")
                        except Exception as e:
                            st.error(f"❌ Error connecting to MCP server: {e}")
                    else:
                        time.sleep(3)
                        st.success(f"✅ Connected to {selected_mcp} MCP server! (Demo mode)")
                        st.info(f"**Demo Response:** This is a simulated response from {selected_mcp} MCP server for query: '{mcp_query}'")

        # Production Phase
        with st.expander("🌐 Production Operations", expanded=False):
            col_prod1, col_prod2 = st.columns(2)
            
            with col_prod1:
                st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">🔗</span>
                    <div class="feature-title">Connected Agent</div>
                    <div class="feature-description">Live agent interaction and real-time queries</div>
                </div>
                """, unsafe_allow_html=True)
                
                query = st.text_input("💬 Enter your query:", value="What is the stock price of Microsoft?", key="query_input")
                
                if st.button("🚀 Connect to Agent", key="connected_agent"):
                    with st.spinner("🔄 Connecting to agent...", show_time=True):
                        if DEPENDENCIES_AVAILABLE:
                            connected_agentrs = connected_agent(query)
                            st.write("**Agent Response:**")
                            st.info(connected_agentrs)
                        else:
                            time.sleep(2)
                            st.info(f"**Agent Response:** The current stock price of Microsoft (MSFT) is $425.67 (Demo response for: '{query}')")
                if st.button("🚀 Connect to Existing Agent", key="connected_agent_existing"):
                    with st.spinner("🔄 Connecting to agent...", show_time=True):
                        if DEPENDENCIES_AVAILABLE:
                            ex_connected_agentrs = existing_connected_agent(query)
                            st.write("**Agent Response:**")
                            st.info(ex_connected_agentrs)
                        else:
                            time.sleep(2)
                            st.info(f"**Agent Response:** The current stock price of Microsoft (MSFT) is $425.67 (Demo response for: '{query}')")

            with col_prod2:
                st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">🗑️</span>
                    <div class="feature-title">Agent Cleanup</div>
                    <div class="feature-description">Safely remove agents and clean up resources</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Delete Agent", key="delete_agent"):
                    with st.spinner("🔄 Cleaning up agent resources...", show_time=True):
                        if DEPENDENCIES_AVAILABLE:
                            delete_agentrs = delete_agent()
                            st.success(f"✅ {delete_agentrs}")
                        else:
                            time.sleep(2)
                            st.success("✅ Agent successfully deleted! (Demo mode)")

        # AI Action Plan Agent
        with st.expander("🇺🇸 Americas AI Action Plan Agent", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🇺🇸</span>
                <div class="feature-title">AI Action Plan Query Agent</div>
                <div class="feature-description">Ask questions about the Americas AI Action Plan using voice or text input</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize AI Action Plan chat history
            if 'ai_action_plan_messages' not in st.session_state:
                st.session_state.ai_action_plan_messages = []
            
            # Chat history display
            if st.session_state.ai_action_plan_messages:
                st.markdown("### 💬 AI Action Plan Chat History")
                
                # Create scrollable chat container
                chat_container_html = """
                <div style="
                    height: 300px;
                    overflow-y: auto;
                    border: 2px solid var(--md-sys-color-outline-variant);
                    border-radius: 12px;
                    padding: 15px;
                    background: var(--md-sys-color-surface);
                    margin: 10px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                ">
                """
                
                for i, message in enumerate(st.session_state.ai_action_plan_messages):
                    role_icon = "🧑‍💻" if message["role"] == "user" else "🇺🇸"
                    role_name = "You" if message["role"] == "user" else "AI Action Plan Agent"
                    message_class = "user-message" if message["role"] == "user" else "assistant-message"
                    bg_color = "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)" if message["role"] == "user" else "linear-gradient(135deg, #fff3e0 0%, #ffcc02 30%)"
                    border_color = "#2196f3" if message["role"] == "user" else "#ff6f00"
                    
                    escaped_content = message["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")
                    
                    chat_container_html += f"""
                    <div style="
                        margin: 10px 0;
                        padding: 12px;
                        border-radius: 10px;
                        background: {bg_color};
                        border-left: 4px solid {border_color};
                        word-wrap: break-word;
                    ">
                        <div style="font-weight: bold; color: #333; margin-bottom: 8px;">
                            {role_icon} {role_name}
                        </div>
                        <div style="color: #555; line-height: 1.5; white-space: pre-wrap;">
                            {escaped_content}
                        </div>
                    </div>
                    """
                
                chat_container_html += "</div>"
                st.markdown(chat_container_html, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    height: 150px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px dashed #ddd;
                    border-radius: 15px;
                    background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 30%);
                    margin: 15px 0;
                    text-align: center;
                    color: #333;
                ">
                    <div>
                        <h5>🇺🇸 Ready to explore the AI Action Plan!</h5>
                        <p>Ask questions using voice or text input below.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Input options
            col_ai_action1, col_ai_action2 = st.columns([2, 1])
            
            with col_ai_action1:
                # Text input
                ai_action_query = st.text_input(
                    "💬 Ask about the AI Action Plan:", 
                    value="What are the key priorities in the Americas AI Action Plan?",
                    key="ai_action_plan_query"
                )
                
                # Voice input
                st.markdown("**🎤 Voice Input:**")
                ai_action_audio = st.audio_input("Record your question about the AI Action Plan", key="ai_action_plan_audio")
            
            with col_ai_action2:
                # Action buttons
                if st.button("💬 Ask via Text", key="ai_action_plan_text"):
                    if ai_action_query.strip():
                        with st.spinner("🔄 Querying AI Action Plan agent...", show_time=True):
                            # Add user message
                            st.session_state.ai_action_plan_messages.append({"role": "user", "content": ai_action_query})
                            
                            if DEPENDENCIES_AVAILABLE:
                                try:
                                    ai_action_response = aiactionplat_agent(ai_action_query)
                                    # Add assistant response
                                    st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": ai_action_response})
                                    st.success("✅ Response received!")
                                    st.rerun()
                                except Exception as e:
                                    error_msg = f"❌ Error querying AI Action Plan agent: {str(e)}"
                                    st.error(error_msg)
                                    st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                                    st.rerun()
                            else:
                                time.sleep(2)
                                demo_response = f"The Americas AI Action Plan focuses on responsible AI development, ensuring ethical guidelines, promoting innovation while maintaining security standards, and fostering international cooperation. (Demo response for: '{ai_action_query}')"
                                st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": demo_response})
                                st.success("✅ Response received! (Demo mode)")
                                st.rerun()
                    else:
                        st.warning("⚠️ Please enter a question first.")
                
                if st.button("🗑️ Clear Chat", key="clear_ai_action_chat"):
                    st.session_state.ai_action_plan_messages = []
                    st.success("✅ Chat history cleared!")
                    st.rerun()
            
            # Process voice input
            if ai_action_audio:
                with st.spinner("🔄 Processing voice input...", show_time=True):
                    try:
                        # Import audio processing functions from bbmcp
                        from bbmcp import save_audio_file, transcribe_audio, generate_audio_response_gpt
                        
                        # Save and transcribe audio
                        audio_file_path = save_audio_file(ai_action_audio.getvalue())
                        transcription = transcribe_audio(audio_file_path)
                        
                        st.markdown(f"""
                        <div class="feature-card" style="border-left-color: var(--md-sys-color-tertiary);">
                            <h5 style="color: var(--md-sys-color-tertiary);">🎤 Voice Input Transcribed:</h5>
                            <p style="font-style: italic;">{transcription}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add user message
                        st.session_state.ai_action_plan_messages.append({"role": "user", "content": f"[Voice] {transcription}"})
                        
                        if DEPENDENCIES_AVAILABLE:
                            try:
                                # Get response from AI Action Plan agent
                                ai_action_response = aiactionplat_agent(transcription)
                                
                                # Generate audio response
                                response_audio_path = generate_audio_response_gpt(ai_action_response)
                                
                                # Display text response
                                st.markdown("""
                                <div class="feature-card" style="border-left-color: #ff6f00;">
                                    <h5 style="color: #ff6f00;">🇺🇸 AI Action Plan Agent Response:</h5>
                                </div>
                                """, unsafe_allow_html=True)
                                st.info(ai_action_response)
                                
                                # Display audio response
                                import base64
                                with open(response_audio_path, "rb") as f:
                                    audio_bytes = f.read()
                                    audio_base64 = base64.b64encode(audio_bytes).decode()
                                    audio_html = f"""
                                    <div class="feature-card">
                                        <h5 style="color: #ff6f00;">🔊 Audio Response:</h5>
                                        <audio controls autoplay style="width: 100%;">
                                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                        </audio>
                                    </div>
                                    """
                                    st.markdown(audio_html, unsafe_allow_html=True)
                                
                                # Add assistant response to chat history
                                st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": ai_action_response})
                                
                                # Clean up audio files
                                if os.path.exists(audio_file_path):
                                    os.remove(audio_file_path)
                                if os.path.exists(response_audio_path):
                                    os.remove(response_audio_path)
                                
                                st.success("✅ Voice input processed successfully!")
                                
                            except Exception as e:
                                error_msg = f"❌ Error processing voice query: {str(e)}"
                                st.error(error_msg)
                                st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": f"I apologize, but I encountered an error processing your voice input: {str(e)}"})
                        else:
                            time.sleep(3)
                            demo_response = f"The Americas AI Action Plan emphasizes collaborative governance and responsible AI deployment across member nations. (Demo voice response for: '{transcription}')"
                            st.session_state.ai_action_plan_messages.append({"role": "assistant", "content": demo_response})
                            st.success("✅ Voice input processed! (Demo mode)")
                        
                    except ImportError as e:
                        st.error(f"❌ Error importing audio processing functions: {e}")
                    except Exception as e:
                        st.error(f"❌ Error processing voice input: {str(e)}")
            
            # Information section
            with st.expander("ℹ️ About the AI Action Plan Agent", expanded=False):
                st.markdown("""
                **🇺🇸 Americas AI Action Plan Agent** provides insights and answers questions about:
                
                - **Policy Framework**: Key policies and regulations in the Americas AI Action Plan
                - **Strategic Priorities**: Main focus areas and objectives
                - **Implementation**: How the plan is being executed across member nations
                - **Collaboration**: Inter-country cooperation initiatives
                - **Ethical Guidelines**: AI ethics and responsible development practices
                - **Security Measures**: AI safety and security protocols
                
                💡 **Tips**: 
                - Use specific questions for better responses
                - Try both text and voice input modes
                - Voice responses include audio playback
                - Chat history is maintained during your session
                """)

    with col2:
        st.markdown("### 📊 System Status")
        
        # Status Dashboard
        st.markdown("""
        <div class="card-container">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🔧 System Health</h4>
        """, unsafe_allow_html=True)
        
        if DEPENDENCIES_AVAILABLE:
            st.markdown('<span class="status-success">🟢 Dependencies Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-warning">🟡 Demo Mode</span>', unsafe_allow_html=True)
        
        # MCP Server Status
        st.markdown('<br><h5 style="color: var(--md-sys-color-secondary); margin: 1rem 0 0.5rem 0;">🔗 MCP Servers</h5>', unsafe_allow_html=True)
        st.markdown('<span class="status-success">🟢 Microsoft Learn</span>', unsafe_allow_html=True)
        
        # Check GitHub PAT token
        github_pat = os.getenv("GITHUB_PAT_TOKEN")
        if github_pat:
            st.markdown('<span class="status-success">🟢 GitHub</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-warning">🟡 GitHub (PAT needed)</span>', unsafe_allow_html=True)
        
        st.markdown('<span class="status-success">🟢 HuggingFace</span>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("""
        <div class="card-container">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">⚡ Quick Actions</h4>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Run Full Pipeline", key="full_pipeline"):
            st.info("🚀 Full pipeline execution would run all components sequentially")
        
        if st.button("📋 View Logs", key="view_logs"):
            st.info("📄 Log viewer would display recent system activity")
        
        if st.button("🎙️ Open MCP Audio Chat", key="mcp_audio_chat"):
            # Use session state to control the MCP interface display
            if "show_mcp_chat" not in st.session_state:
                st.session_state.show_mcp_chat = False
            
            st.session_state.show_mcp_chat = not st.session_state.show_mcp_chat
            
            if st.session_state.show_mcp_chat:
                st.success("✅ MCP Audio Chat activated! Scroll down to see the interface.")
            else:
                st.info("📱 MCP Audio Chat hidden.")
        
        if st.button("⚙️ Settings", key="settings"):
            st.info("🛠️ Configuration panel would allow system customization")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Recent Activity & MCP Info
        st.markdown("""
        <div class="card-container">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">📈 Recent Activity</h4>
            <div style="font-size: 0.9rem; color: var(--md-sys-color-on-surface-variant);">
                <p>🕐 <strong>2 minutes ago:</strong> Code interpreter executed</p>
                <p>🕑 <strong>5 minutes ago:</strong> AI evaluation completed</p>
                <p>🕒 <strong>10 minutes ago:</strong> MCP server connected</p>
            </div>
        </div>
        
        <div class="card-container">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🔗 MCP Server Info</h4>
            <div style="font-size: 0.85rem; color: var(--md-sys-color-on-surface-variant);">
                <p><strong>🟢 Microsoft Learn:</strong> Documentation & learning resources</p>
                <p><strong>🟢 GitHub:</strong> Code repositories & issues (requires PAT)</p>
                <p><strong>🟢 HuggingFace:</strong> ML models & datasets</p>
                <br>
                <p style="font-style: italic;">💡 Use the MCP Audio Chat for voice-based interactions!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--md-sys-color-on-surface-variant); padding: 1rem;">
        <p>🤖 <strong>AgenticAI Foundry</strong> - Enterprise AI Agent Development Platform</p>
        <p style="font-size: 0.8rem;">Built with ❤️ using Azure AI Services & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

    # MCP Audio Chat Interface (conditionally displayed)
    if st.session_state.get("show_mcp_chat", False):
        st.markdown("---")
        st.markdown("""
        <div class="main-header" style="margin-top: 2rem;">
            <h2>🎙️ MCP Audio Chat Interface</h2>
            <p>Voice-powered interaction with Model Context Protocol servers</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Embedded MCP functionality without page config conflicts
        mcp_audio_chat_interface()

def mcp_audio_chat_interface():
    """Embedded MCP audio chat interface that doesn't conflict with main app."""
    try:
        import base64
        import tempfile
        import uuid
        from bbmcp import (
            save_audio_file, 
            transcribe_audio, 
            generate_audio_response_gpt,
            msft_generate_chat_response,
            bbgithub_generate_chat_response,
            hf_generate_chat_response,
            retrieve_relevant_content
        )
        
        # Initialize MCP chat session state
        if "mcp_messages" not in st.session_state:
            st.session_state.mcp_messages = []
        
        # MCP Interface styling
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">🎯 MCP Server Selection</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display MCP chat history
        if st.session_state.mcp_messages:
            st.markdown("""
            <div class="feature-card">
                <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">💬 Chat History</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for i, message in enumerate(st.session_state.mcp_messages):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="feature-card" style="border-left-color: var(--md-sys-color-tertiary); margin: 0.5rem 0;">
                        <h6 style="color: var(--md-sys-color-tertiary); margin-bottom: 0.5rem;">👤 You:</h6>
                        <p style="margin: 0;">{message["content"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="feature-card" style="border-left-color: var(--md-sys-color-primary); margin: 0.5rem 0;">
                        <h6 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">🤖 Assistant:</h6>
                        <p style="margin-bottom: 0.5rem;">{message["content"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if message.get("audio"):
                        audio_base64 = base64.b64encode(message["audio"]).decode()
                        audio_html = f"""
                        <div style="margin: 0.5rem 0;">
                            <audio controls style="width: 100%;">
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            </audio>
                        </div>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-card">
                <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">💬 Chat History</h4>
                <p style="color: var(--md-sys-color-on-surface-variant); font-style: italic; text-align: center;">
                    No conversation yet. Record your first voice message to start chatting with MCP servers!
                </p>
            </div>
            """, unsafe_allow_html=True)

        # MCP Server selection
        col_mcp_audio1, col_mcp_audio2 = st.columns(2)
        
        with col_mcp_audio1:
            mcp_audio_options = ['Microsoft', 'Github', 'HuggingFace']
            selected_mcp_audio = st.radio(
                "🌐 Choose MCP Server:", 
                mcp_audio_options, 
                horizontal=True,
                key="mcp_audio_server_select"
            )
        
        with col_mcp_audio2:
            if st.button("🗑️ Clear MCP Chat", key="clear_mcp_chat"):
                st.session_state.mcp_messages = []
                st.success("✅ MCP chat history cleared!")
                st.rerun()

        # Audio input
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: var(--md-sys-color-primary);">🎤 Voice Input</h4>
            <p>Record your voice message to interact with the selected MCP server</p>
        </div>
        """, unsafe_allow_html=True)
        
        audio_value = st.audio_input("🎙️ Record your voice message", key="mcp_audio_input")

        if audio_value:
            # Process user input without nested chat messages
            st.audio(audio_value)
            
            with st.spinner("🔄 Transcribing audio...", show_time=True):
                try:
                    audio_file_path = save_audio_file(audio_value.getvalue())
                    transcription = transcribe_audio(audio_file_path)
                    
                    # Display user input
                    st.markdown("""
                    <div class="feature-card" style="border-left-color: var(--md-sys-color-tertiary);">
                        <h5 style="color: var(--md-sys-color-tertiary); margin-bottom: 0.5rem;">👤 You said:</h5>
                        <p style="font-style: italic;">{}</p>
                    </div>
                    """.format(transcription), unsafe_allow_html=True)
                    
                    # Save user message
                    st.session_state.mcp_messages.append({"role": "user", "content": transcription})

                    # Process assistant response
                    with st.spinner(f"🔄 Generating response from {selected_mcp_audio} MCP server...", show_time=True):
                        # Retrieve relevant content from JSON (empty for now)
                        context = ""
                        
                        # Generate response based on selected MCP server
                        if selected_mcp_audio == 'Github':
                            response_text, _ = bbgithub_generate_chat_response(transcription, context)
                        elif selected_mcp_audio == 'Microsoft':
                            response_text, _ = msft_generate_chat_response(transcription, context)
                        elif selected_mcp_audio == 'HuggingFace':
                            response_text, _ = hf_generate_chat_response(transcription, context)
                        else:
                            response_text = "Invalid MCP server selection."

                        # Generate audio response
                        response_audio_path = generate_audio_response_gpt(response_text)
                        
                        # Display AI response
                        st.markdown("""
                        <div class="feature-card" style="border-left-color: var(--md-sys-color-primary);">
                            <h5 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">🤖 {} MCP Response:</h5>
                        </div>
                        """.format(selected_mcp_audio), unsafe_allow_html=True)
                        
                        st.info(response_text)
                        
                        # Display audio response
                        with open(response_audio_path, "rb") as f:
                            audio_bytes = f.read()
                            audio_base64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f"""
                            <div class="feature-card">
                                <h5 style="color: var(--md-sys-color-primary); margin-bottom: 0.5rem;">🔊 Audio Response:</h5>
                                <audio controls autoplay style="width: 100%;">
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                </audio>
                            </div>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # Save assistant message
                        st.session_state.mcp_messages.append({
                            "role": "assistant",
                            "content": f"**{selected_mcp_audio} Response:** {response_text}",
                            "audio": audio_bytes
                        })

                    # Clean up temporary files
                    if os.path.exists(audio_file_path):
                        os.remove(audio_file_path)
                    if os.path.exists(response_audio_path):
                        os.remove(response_audio_path)
                        
                    # Success message
                    st.success("✅ Audio processed successfully! Your conversation has been added to the chat history.")
                        
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")
                    import traceback
                    st.error(f"📋 Debug info: {traceback.format_exc()}")
                        
    except ImportError as e:
        st.error(f"❌ Error importing MCP functions: {e}")
        st.info("💡 Make sure all required dependencies are installed.")
    except Exception as e:
        st.error(f"❌ Error in MCP Audio Chat: {str(e)}")

if __name__ == "__main__":
    with tracer.start_as_current_span("AzureAIFoundrye2eAgent-tracing"):
        main()