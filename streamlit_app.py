"""
AgenticAI Foundry - Streamlit Web Application
============================================

A comprehensive web interface showcasing all AI agents, evaluation, and red team capabilities.
"""

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
    
    # Create mock functions for demo
    def code_interpreter():
        return "✅ Code interpreter executed successfully (simulated)"
    
    def ai_eval():
        return "✅ AI evaluation completed with high scores (simulated)"
    
    async def redteam():
        return "🛡️ Red team scan completed - no vulnerabilities found (simulated)"
    
    def agent_eval():
        return "🎯 Agent evaluation: High performance metrics (simulated)"
    
    def connected_agent(query):
        return f"🔗 Connected agent response for: {query} (simulated)"
    
    def ai_search_agent(query):
        return f"🔍 Search results for: {query} (simulated)"
    
    def delete_agent():
        return "🗑️ All agents deleted successfully (simulated)"
    
    def process_message_reasoning(query):
        return f"🧠 Reasoning response for: {query} (simulated)"

# Configure Streamlit page
st.set_page_config(
    page_title="AgenticAI Foundry",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .output-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    # 🤖 AgenticAI Foundry
    ### Comprehensive AI Agent Platform with Evaluation & Security Testing
    
    Welcome to the AgenticAI Foundry - your one-stop platform for AI agents, comprehensive evaluation frameworks, 
    and advanced red team security testing capabilities.
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Environment status check
        st.markdown("### Environment Status")
        env_vars = [
            "PROJECT_ENDPOINT",
            "MODEL_DEPLOYMENT_NAME", 
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var}")
        
        st.markdown("---")
        
        # Global settings
        st.markdown("### Global Settings")
        enable_speech = st.checkbox("🎤 Enable Speech Input", value=False)
        show_debug = st.checkbox("🐛 Show Debug Info", value=False)
        
        st.markdown("---")
        st.markdown("### 📚 Quick Help")
        st.info("""
        **Navigation**: Use the tabs above to access different features.
        
        **Input Types**: Most agents support text, and some support file uploads.
        
        **Progress**: Watch the progress bars during execution.
        """)
    
    # Main content tabs
    tabs = st.tabs([
        "🏠 Overview",
        "💻 Code Interpreter", 
        "🔍 AI Evaluation",
        "🛡️ Red Team Testing",
        "🤖 Agent Evaluation", 
        "🔗 Connected Agents",
        "🔎 AI Search",
        "🗑️ Agent Management"
    ])
    
    with tabs[0]:
        show_overview()
    
    with tabs[1]:
        show_code_interpreter(enable_speech, show_debug)
    
    with tabs[2]:
        show_ai_evaluation(enable_speech, show_debug)
    
    with tabs[3]:
        show_red_team_testing(enable_speech, show_debug)
    
    with tabs[4]:
        show_agent_evaluation(enable_speech, show_debug)
    
    with tabs[5]:
        show_connected_agents(enable_speech, show_debug)
    
    with tabs[6]:
        show_ai_search(enable_speech, show_debug)
    
    with tabs[7]:
        show_agent_management(show_debug)

def show_overview():
    """Display overview of all capabilities"""
    
    st.markdown("## 🌟 Platform Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI Agents</h3>
            <ul>
                <li><strong>Code Interpreter Agent</strong>: Execute Python code and data analysis</li>
                <li><strong>Connected Agent</strong>: External service integration with email</li>
                <li><strong>AI Search Agent</strong>: Azure AI Search integration</li>
                <li><strong>Weather Agent</strong>: Custom function tool integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🛡️ Red Team Testing</h3>
            <ul>
                <li>Automated red team scanning</li>
                <li>Multi-strategy attack simulation</li>
                <li>Risk category coverage</li>
                <li>Comprehensive security reporting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Evaluation Framework</h3>
            <ul>
                <li><strong>Agent-specific evaluators</strong>: Intent, task adherence, tool accuracy</li>
                <li><strong>Quality metrics</strong>: Relevance, coherence, groundedness, fluency</li>
                <li><strong>Safety evaluators</strong>: Content safety, hate/unfairness detection</li>
                <li><strong>Advanced metrics</strong>: BLEU, GLEU, ROUGE, METEOR, F1 scores</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🔧 Management Tools</h3>
            <ul>
                <li>Agent lifecycle management</li>
                <li>Thread and conversation cleanup</li>
                <li>Resource monitoring</li>
                <li>Performance tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("## 📊 Quick Stats")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Available Agents", "4+", delta="Ready")
    
    with stat_col2:
        st.metric("Evaluation Metrics", "15+", delta="Comprehensive")
    
    with stat_col3:
        st.metric("Security Tests", "Multiple", delta="Advanced")
    
    with stat_col4:
        st.metric("Input Types", "Text, Files, Speech", delta="Flexible")

def create_input_section(title: str, enable_speech: bool = False, support_files: bool = False) -> Dict[str, Any]:
    """Create a standardized input section"""
    
    st.markdown(f"### {title}")
    
    inputs = {}
    
    # Text input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        inputs['text'] = st.text_area(
            "Enter your message:",
            height=100,
            placeholder="Type your message here...",
            key=f"text_{title.replace(' ', '_').lower()}"
        )
    
    with col2:
        if enable_speech:
            st.markdown("#### 🎤 Speech Input")
            if st.button("🎙️ Record", key=f"speech_{title.replace(' ', '_').lower()}"):
                st.info("Speech-to-text functionality would be implemented here using browser APIs or external services.")
                # Note: Real speech-to-text would require additional packages like speech_recognition
                # and integration with browser APIs
    
    # File upload section
    if support_files:
        st.markdown("#### 📁 File Uploads")
        file_col1, file_col2 = st.columns(2)
        
        with file_col1:
            inputs['image'] = st.file_uploader(
                "Upload Image",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key=f"image_{title.replace(' ', '_').lower()}"
            )
            inputs['audio'] = st.file_uploader(
                "Upload Audio", 
                type=['mp3', 'wav', 'ogg'],
                key=f"audio_{title.replace(' ', '_').lower()}"
            )
        
        with file_col2:
            inputs['video'] = st.file_uploader(
                "Upload Video",
                type=['mp4', 'avi', 'mov'],
                key=f"video_{title.replace(' ', '_').lower()}"
            )
            inputs['document'] = st.file_uploader(
                "Upload Document",
                type=['pdf', 'txt', 'docx'],
                key=f"doc_{title.replace(' ', '_').lower()}"
            )
    
    return inputs

def show_output_section(title: str, output: str, show_debug: bool = False):
    """Display output in a formatted section"""
    
    st.markdown(f"### {title}")
    
    if output:
        st.markdown(f"""
        <div class="output-container">
            <pre>{output}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        if show_debug:
            st.markdown("#### 🐛 Debug Info")
            st.json({
                "output_length": len(output),
                "timestamp": datetime.now().isoformat(),
                "type": type(output).__name__
            })
    else:
        st.info("No output yet. Run a function to see results here.")

def show_code_interpreter(enable_speech: bool, show_debug: bool):
    """Code Interpreter Agent interface"""
    
    st.markdown("## 💻 Code Interpreter Agent")
    st.markdown("Execute Python code and perform data analysis tasks with the AI agent.")
    
    inputs = create_input_section("Code Interpreter Input", enable_speech, True)
    
    # Code example suggestions
    st.markdown("#### 💡 Example Requests")
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        if st.button("📊 Data Analysis", key="code_data_analysis"):
            st.session_state['code_interpreter_input'] = "Create a simple data analysis with pandas on a sample dataset"
        if st.button("📈 Plot Generation", key="code_plot"):
            st.session_state['code_interpreter_input'] = "Generate a matplotlib plot showing sample data trends"
    
    with example_col2:
        if st.button("🧮 Mathematical Calculation", key="code_math"):
            st.session_state['code_interpreter_input'] = "Calculate the mean, median, and standard deviation of a list of numbers"
        if st.button("🔢 Statistics", key="code_stats"):
            st.session_state['code_interpreter_input'] = "Perform statistical analysis on sample data"
    
    # Use example input if set
    if 'code_interpreter_input' in st.session_state:
        inputs['text'] = st.session_state['code_interpreter_input']
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Run Code Interpreter", type="primary"):
            if inputs['text']:
                with st.spinner("Running code interpreter..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        if DEPENDENCIES_AVAILABLE:
                            # Note: The original function doesn't return a value, so we'll modify this
                            code_interpreter()
                            result = "Code interpreter executed successfully. Check console for detailed output."
                        else:
                            result = f"🤖 Code interpreter would execute: '{inputs['text']}'\n\n✅ Simulated execution complete with data analysis results."
                        
                        st.session_state['code_interpreter_output'] = result
                        st.success("✅ Code interpreter completed!")
                        
                        if show_debug:
                            st.json({"function": "code_interpreter", "status": "completed", "dependencies": DEPENDENCIES_AVAILABLE})
                            
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.session_state['code_interpreter_output'] = error_msg
                        st.error(f"❌ {error_msg}")
            else:
                st.warning("Please enter a message first.")
    
    with col2:
        if st.button("📋 Clear Output"):
            st.session_state['code_interpreter_output'] = ""
            if 'code_interpreter_input' in st.session_state:
                del st.session_state['code_interpreter_input']
            st.rerun()
    
    # Output section
    output = st.session_state.get('code_interpreter_output', '')
    show_output_section("📤 Code Interpreter Output", output, show_debug)

def show_ai_evaluation(enable_speech: bool, show_debug: bool):
    """AI Evaluation interface"""
    
    st.markdown("## 🔍 AI Evaluation Framework")
    st.markdown("Comprehensive evaluation with quality metrics, safety evaluators, and advanced scoring.")
    
    # Show evaluation details upfront
    with st.expander("📊 What Gets Evaluated", expanded=False):
        eval_col1, eval_col2 = st.columns(2)
        
        with eval_col1:
            st.markdown("""
            **Quality Metrics:**
            - Relevance & Coherence
            - Groundedness & Fluency
            - Content Safety
            """)
            
        with eval_col2:
            st.markdown("""
            **Advanced Scoring:**
            - BLEU, GLEU, ROUGE scores
            - METEOR & F1 scores  
            - Protected material detection
            """)
    
    inputs = create_input_section("Evaluation Input", enable_speech, True)
    
    # Evaluation configuration
    st.markdown("#### ⚙️ Evaluation Configuration")
    eval_config_col1, eval_config_col2 = st.columns(2)
    
    with eval_config_col1:
        eval_type = st.selectbox(
            "Evaluation Type",
            ["Full Evaluation", "Quality Only", "Safety Only", "Custom"],
            index=0
        )
        
    with eval_config_col2:
        data_source = st.selectbox(
            "Data Source", 
            ["Default Dataset (datarfp.jsonl)", "Custom Input"],
            index=0
        )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📊 Run AI Evaluation", type="primary"):
            with st.spinner("Running comprehensive AI evaluation..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                try:
                    if DEPENDENCIES_AVAILABLE:
                        result = ai_eval()
                    else:
                        result = f"""🔍 AI Evaluation Results (Simulated):

**Evaluation Type**: {eval_type}
**Data Source**: {data_source}

📊 **Quality Metrics:**
- Relevance: 0.92/1.00
- Coherence: 0.89/1.00  
- Groundedness: 0.87/1.00
- Fluency: 0.94/1.00

🛡️ **Safety Scores:**
- Content Safety: PASSED
- Hate/Unfairness: PASSED
- Violence Detection: PASSED
- Sexual Content: PASSED

📈 **Advanced Metrics:**
- BLEU Score: 0.78
- ROUGE-4: 0.82
- F1 Score: 0.85
- METEOR: 0.79

✅ **Overall Assessment**: High quality responses with excellent safety compliance.

📄 **Report**: Results saved to myevalresults.json
"""
                    
                    st.session_state['ai_eval_output'] = result
                    st.success("✅ AI evaluation completed!")
                    
                    if show_debug:
                        st.json({
                            "function": "ai_eval", 
                            "eval_type": eval_type,
                            "data_source": data_source,
                            "status": "completed",
                            "dependencies": DEPENDENCIES_AVAILABLE
                        })
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.session_state['ai_eval_output'] = error_msg
                    st.error(f"❌ {error_msg}")
    
    with col2:
        if st.button("📋 Clear Results"):
            st.session_state['ai_eval_output'] = ""
            st.rerun()
    
    # Output section
    output = st.session_state.get('ai_eval_output', '')
    show_output_section("📈 Evaluation Results", output, show_debug)
    
    # Show evaluation metrics info
    with st.expander("ℹ️ Evaluation Metrics Details"):
        st.markdown("""
        ### 📊 Quality Metrics
        - **Relevance**: How well the response addresses the query
        - **Coherence**: Logical flow and consistency of the response
        - **Groundedness**: How well the response is supported by provided context
        - **Fluency**: Language quality and readability
        
        ### 🛡️ Safety Evaluators  
        - **Content Safety**: Overall content appropriateness
        - **Hate/Unfairness**: Detection of biased or discriminatory content
        - **Violence**: Identification of violent content
        - **Sexual Content**: Detection of inappropriate sexual content
        - **Self-Harm**: Recognition of self-harm related content
        
        ### 📈 Advanced Metrics
        - **BLEU**: Bilingual Evaluation Understudy score
        - **GLEU**: Google-BLEU score variant
        - **ROUGE**: Recall-Oriented Understudy for Gisting Evaluation
        - **METEOR**: Metric for Evaluation of Translation with Explicit ORdering
        - **F1 Score**: Harmonic mean of precision and recall
        """)

def show_red_team_testing(enable_speech: bool, show_debug: bool):
    """Red Team Testing interface"""
    
    st.markdown("## 🛡️ Red Team Security Testing")
    st.markdown("Advanced security vulnerability assessment with multi-strategy attack simulation.")
    
    st.warning("⚠️ Red team testing may take several minutes to complete and requires proper Azure AI configuration.")
    
    # Red team configuration
    with st.expander("🔧 Red Team Configuration", expanded=False):
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("""
            **Risk Categories:**
            - 🔴 Violence
            - 🟠 Hate/Unfairness  
            - 🟡 Sexual Content
            - 🔵 Self-Harm
            """)
            
            num_objectives = st.slider("Number of Objectives per Category", 1, 10, 5)
            
        with config_col2:
            st.markdown("""
            **Attack Strategies:**
            - 🟢 Easy Complexity
            - 🟡 Moderate Complexity
            - 🔴 Advanced Encoding
            - 🟣 Prompt Injection
            """)
            
            attack_complexity = st.selectbox(
                "Attack Complexity Level",
                ["Easy", "Moderate", "Advanced", "All Levels"],
                index=0
            )
    
    inputs = create_input_section("Red Team Input", enable_speech, False)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔒 Run Red Team Scan", type="primary"):
            with st.spinner("Running red team security scan..."):
                progress_bar = st.progress(0)
                
                try:
                    if DEPENDENCIES_AVAILABLE:
                        # Run async function
                        result = asyncio.run(redteam())
                    else:
                        result = f"""🛡️ Red Team Security Scan Results (Simulated):

**Scan Configuration:**
- Risk Categories: Violence, Hate/Unfairness, Sexual, Self-Harm
- Objectives per Category: {num_objectives}
- Attack Complexity: {attack_complexity}
- Scan Duration: ~3.2 minutes

🔍 **Attack Strategies Tested:**
- Character manipulation attacks
- Encoding-based bypasses (ROT13, Base64)
- Unicode confusable characters
- Prompt injection techniques
- Conversation steering attempts

📊 **Scan Results:**
- Total Attack Attempts: {num_objectives * 4}
- Successful Bypasses: 0
- Risk Level: LOW
- Overall Security Score: 95/100

🛡️ **Security Assessment:**
✅ Strong resistance to prompt injection
✅ Effective content filtering active
✅ No harmful content generation detected
✅ Consistent safety behavior across attack vectors

⚠️ **Recommendations:**
- Continue monitoring for emerging attack patterns
- Regular re-testing with updated strategies
- Review conversation logs for edge cases

📄 **Detailed Report**: Advanced-Callback-Scan.json
🔗 **Azure AI Studio URL**: Available in full environment
"""
                    
                    for i in range(100):
                        time.sleep(0.03)
                        progress_bar.progress(i + 1)
                    
                    st.session_state['redteam_output'] = result
                    st.success("✅ Red team scan completed!")
                    
                    if show_debug:
                        st.json({
                            "function": "redteam", 
                            "num_objectives": num_objectives,
                            "attack_complexity": attack_complexity,
                            "status": "completed",
                            "dependencies": DEPENDENCIES_AVAILABLE
                        })
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.session_state['redteam_output'] = error_msg
                    st.error(f"❌ {error_msg}")
    
    with col2:
        if st.button("📋 Clear Scan Results"):
            st.session_state['redteam_output'] = ""
            st.rerun()
    
    # Output section
    output = st.session_state.get('redteam_output', '')
    show_output_section("🛡️ Red Team Scan Results", output, show_debug)
    
    # Show red team info
    with st.expander("🔍 Red Team Testing Details"):
        st.markdown("""
        ### 🎯 What is Red Team Testing?
        Red team testing simulates real-world adversarial attacks to identify security vulnerabilities 
        and safety issues in AI systems before they reach production.
        
        ### 🚨 Risk Categories Tested
        - **Violence**: Content promoting or describing violent acts
        - **Hate/Unfairness**: Discriminatory, biased, or hateful content
        - **Sexual Content**: Inappropriate sexual material
        - **Self-Harm**: Content that could encourage self-destructive behavior
        
        ### ⚔️ Attack Strategies
        - **Character Manipulation**: Swapping, spacing, and Unicode tricks
        - **Encoding Techniques**: ROT13, Base64, Morse code, binary encoding
        - **Prompt Injection**: Attempts to override system instructions
        - **Conversation Steering**: Gradually leading to prohibited topics
        
        ### 📊 Output Analysis
        - **Vulnerability Detection**: Identifies successful bypass attempts
        - **Risk Assessment**: Quantified security posture evaluation  
        - **Mitigation Recommendations**: Actionable security improvements
        - **Compliance Reporting**: Documentation for security audits
        """)
        
    # Safety notice
    st.info("""
    🔒 **Safety Note**: Red team testing is conducted in a controlled environment with proper safeguards. 
    All attack simulations are logged and monitored for research and security improvement purposes.
    """)

def show_agent_evaluation(enable_speech: bool, show_debug: bool):
    """Agent Evaluation interface"""
    
    st.markdown("## 🤖 Agent-Specific Evaluation")
    st.markdown("Evaluate agent performance with intent resolution, task adherence, and tool call accuracy.")
    
    inputs = create_input_section("Agent Evaluation Input", enable_speech, False)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🎯 Run Agent Evaluation", type="primary"):
            with st.spinner("Running agent-specific evaluation..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                try:
                    result = agent_eval()
                    st.session_state['agent_eval_output'] = result
                    st.success("✅ Agent evaluation completed!")
                    
                    if show_debug:
                        st.json({"function": "agent_eval", "status": "completed"})
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.session_state['agent_eval_output'] = error_msg
                    st.error(f"❌ {error_msg}")
    
    with col2:
        if st.button("📋 Clear Results"):
            st.session_state['agent_eval_output'] = ""
            st.rerun()
    
    # Output section
    output = st.session_state.get('agent_eval_output', '')
    show_output_section("🎯 Agent Evaluation Results", output, show_debug)

def show_connected_agents(enable_speech: bool, show_debug: bool):
    """Connected Agents interface"""
    
    st.markdown("## 🔗 Connected Agents")
    st.markdown("Multi-agent system with stock price lookup, AI search, and email capabilities.")
    
    inputs = create_input_section("Connected Agent Query", enable_speech, True)
    
    # Example queries
    st.markdown("#### 💡 Example Queries")
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        if st.button("📈 Stock Price Query"):
            st.session_state['connected_agent_input'] = "What is the stock price of Microsoft?"
        if st.button("🏗️ Construction Query"):
            st.session_state['connected_agent_input'] = "Show me details on Construction management services"
    
    with example_col2:
        if st.button("📧 Email Query"):
            st.session_state['connected_agent_input'] = "Show me construction details and email summary to user@example.com"
        if st.button("🔍 Search Query"):
            st.session_state['connected_agent_input'] = "Search for fiber optic construction best practices"
    
    # Use example input if set
    if 'connected_agent_input' in st.session_state:
        inputs['text'] = st.session_state['connected_agent_input']
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Run Connected Agent", type="primary"):
            if inputs['text']:
                with st.spinner("Running connected multi-agent system..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.025)
                        progress_bar.progress(i + 1)
                    
                    try:
                        result = connected_agent(inputs['text'])
                        st.session_state['connected_agent_output'] = result
                        st.success("✅ Connected agents completed!")
                        
                        if show_debug:
                            st.json({"function": "connected_agent", "query": inputs['text'], "status": "completed"})
                            
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.session_state['connected_agent_output'] = error_msg
                        st.error(f"❌ {error_msg}")
            else:
                st.warning("Please enter a query first.")
    
    with col2:
        if st.button("📋 Clear Output"):
            st.session_state['connected_agent_output'] = ""
            if 'connected_agent_input' in st.session_state:
                del st.session_state['connected_agent_input']
            st.rerun()
    
    # Output section
    output = st.session_state.get('connected_agent_output', '')
    show_output_section("🔗 Connected Agent Response", output, show_debug)

def show_ai_search(enable_speech: bool, show_debug: bool):
    """AI Search Agent interface"""
    
    st.markdown("## 🔎 AI Search Agent")
    st.markdown("Azure AI Search integration for knowledge retrieval from construction RFP documents.")
    
    inputs = create_input_section("Search Query", enable_speech, False)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 Run AI Search", type="primary"):
            if inputs['text']:
                with st.spinner("Searching knowledge base..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    try:
                        result = ai_search_agent(inputs['text'])
                        st.session_state['ai_search_output'] = result
                        st.success("✅ AI search completed!")
                        
                        if show_debug:
                            st.json({"function": "ai_search_agent", "query": inputs['text'], "status": "completed"})
                            
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.session_state['ai_search_output'] = error_msg
                        st.error(f"❌ {error_msg}")
            else:
                st.warning("Please enter a search query first.")
    
    with col2:
        if st.button("📋 Clear Results"):
            st.session_state['ai_search_output'] = ""
            st.rerun()
    
    # Output section
    output = st.session_state.get('ai_search_output', '')
    show_output_section("🔍 Search Results", output, show_debug)

def show_agent_management(show_debug: bool):
    """Agent Management interface"""
    
    st.markdown("## 🗑️ Agent Management")
    st.markdown("Manage agent lifecycle, cleanup threads, and monitor resources.")
    
    st.warning("⚠️ **Warning**: Deleting agents will remove ALL agents and their associated threads. This action cannot be undone.")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Delete All Agents", type="secondary"):
            # Confirmation dialog
            if st.session_state.get('confirm_delete', False):
                with st.spinner("Deleting all agents and threads..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        delete_agent()
                        st.session_state['agent_mgmt_output'] = "All agents and threads deleted successfully."
                        st.success("✅ All agents deleted!")
                        st.session_state['confirm_delete'] = False
                        
                        if show_debug:
                            st.json({"function": "delete_agent", "status": "completed"})
                            
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.session_state['agent_mgmt_output'] = error_msg
                        st.error(f"❌ {error_msg}")
            else:
                st.session_state['confirm_delete'] = True
                st.warning("⚠️ Click again to confirm deletion of ALL agents!")
                st.rerun()
    
    with col2:
        if st.button("📋 Clear Status"):
            st.session_state['agent_mgmt_output'] = ""
            st.session_state['confirm_delete'] = False
            st.rerun()
    
    # Reset confirmation state if other actions taken
    if 'confirm_delete' in st.session_state and st.session_state['confirm_delete']:
        if st.button("❌ Cancel Deletion"):
            st.session_state['confirm_delete'] = False
            st.rerun()
    
    # Output section
    output = st.session_state.get('agent_mgmt_output', '')
    show_output_section("🗑️ Management Status", output, show_debug)
    
    # Management info
    with st.expander("ℹ️ Agent Management Information"):
        st.markdown("""
        **What gets deleted:**
        - All AI agents created in your project
        - All conversation threads associated with agents
        - All message history within those threads
        
        **What is preserved:**
        - Your project configuration
        - Environment variables
        - Evaluation results and files
        - Red team scan results
        """)

if __name__ == "__main__":
    main()