import streamlit as st
import asyncio
import io
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

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
        process_message_reasoning
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ Some Azure AI dependencies are not installed: {e}")
    st.info("Running in demo mode with simulated responses.")
    DEPENDENCIES_AVAILABLE = False


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
            <span class="workflow-step">🔗 Connected Agents</span>
            <div class="workflow-connector"></div>
            <span class="workflow-step">🗑️ Cleanup</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🚀 Agent Operations")
        
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
                with st.spinner("🔄 Executing code interpreter..."):
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
                    with st.spinner("🔄 Running AI evaluation..."):
                        if DEPENDENCIES_AVAILABLE:
                            evalrs = ai_eval()
                            st.json(evalrs)
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
                    with st.spinner("🔄 Running agent evaluation..."):
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
                with st.spinner("🔄 Running RedTeam security analysis..."):
                    if DEPENDENCIES_AVAILABLE:
                        redteamrs = asyncio.run(redteam())
                        st.json(redteamrs)
                    else:
                        time.sleep(4)
                        st.success("✅ Security testing completed! (Demo mode)")

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
                    with st.spinner("🔄 Connecting to agent..."):
                        if DEPENDENCIES_AVAILABLE:
                            connected_agentrs = connected_agent(query)
                            st.write("**Agent Response:**")
                            st.info(connected_agentrs)
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
                    with st.spinner("🔄 Cleaning up agent resources..."):
                        if DEPENDENCIES_AVAILABLE:
                            delete_agentrs = delete_agent()
                            st.success(f"✅ {delete_agentrs}")
                        else:
                            time.sleep(2)
                            st.success("✅ Agent successfully deleted! (Demo mode)")

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
        
        if st.button("⚙️ Settings", key="settings"):
            st.info("🛠️ Configuration panel would allow system customization")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Recent Activity
        st.markdown("""
        <div class="card-container">
            <h4 style="color: var(--md-sys-color-primary); margin-bottom: 1rem;">📈 Recent Activity</h4>
            <div style="font-size: 0.9rem; color: var(--md-sys-color-on-surface-variant);">
                <p>🕐 <strong>2 minutes ago:</strong> Code interpreter executed</p>
                <p>🕑 <strong>5 minutes ago:</strong> AI evaluation completed</p>
                <p>🕒 <strong>10 minutes ago:</strong> Agent connected successfully</p>
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

if __name__ == "__main__":
    main()