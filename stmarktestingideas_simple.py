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
from dotenv import load_dotenv
import tempfile
import uuid
import requests
import io
import re

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

# -----------------------
# Helper: group outputs per agent
# -----------------------
def group_by_agent(outputs: List[Dict[str, str]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for o in outputs:
        agent = o.get('agent', 'Agent')
        grouped.setdefault(agent, []).append(o.get('output', '') or '')
    return grouped

def connected_agent_productideation(query: str) -> tuple:
    """Simplified single-agent approach that simulates multi-agent workflow"""
    
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Create a single orchestrator agent that provides comprehensive analysis
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="ProductIdeationOrchestrator",
        instructions=f"""
        You are a Product Ideation Orchestrator that provides comprehensive product analysis. 
        
        For the user query: "{query}"
        
        Please provide a detailed analysis with the following sections:

        ## 1. PRODUCT IDEATION
        Generate 3-5 innovative product concepts based on the user's input. For each concept include:
        - **Product Name**: A catchy, memorable name
        - **Description**: 2-3 sentence overview
        - **Key Features**: 4-6 main features
        - **Unique Selling Points**: What makes it stand out
        - **Target Audience**: Broad demographics

        ## 2. USER PERSONAS
        Create 6-8 diverse user personas covering different demographics:
        - Name, Age, Gender, Ethnicity, Occupation, Location
        - Income Level (Low/Medium/High)
        - Interests and Pain Points related to the product ideas

        ## 3. USER TESTING SIMULATION
        For each product idea, simulate feedback from the personas:
        - **Likes**: 3-5 positive aspects
        - **Dislikes**: 2-4 potential issues  
        - **Suggestions**: 1-3 improvements
        - **Likelihood to Buy**: Score 1-10 with reason

        ## 4. MARKET FIT ANALYSIS
        Analyze the feedback and provide:
        - Average likelihood scores
        - Common themes (strengths, weaknesses, opportunities)
        - Demographic segments (high fit vs low fit)
        - Overall market fit rating (Poor/Fair/Good/Excellent)
        - 3-5 actionable recommendations

        Structure your response clearly with markdown headers and bullet points. Be comprehensive and data-driven.
        """,
    )
    
    print(f"Created orchestrator agent, ID: {agent.id}")
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=query,
    )
    print(f"Created message, ID: {message.id}")

    # Create and process Agent run
    print("Starting agent run...")
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    
    # Wait for completion with timeout
    max_iterations = 60  # 60 seconds timeout
    iteration = 0
    while run.status in ["queued", "in_progress"] and iteration < max_iterations:
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status} (iteration {iteration})")
        iteration += 1

    print(f"Run completed with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
        # Cleanup
        project_client.agents.delete_agent(agent.id)
        project_client.agents.threads.delete(thread.id)
        return "Error: Agent run failed", [], {}

    # Capture token usage
    token_usage = {}
    if hasattr(run, 'usage') and run.usage:
        token_usage = {
            'prompt_tokens': getattr(run.usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(run.usage, 'completion_tokens', 0),
            'total_tokens': getattr(run.usage, 'total_tokens', 0)
        }
        print(f"Token usage - Prompt: {token_usage['prompt_tokens']}, Completion: {token_usage['completion_tokens']}, Total: {token_usage['total_tokens']}")
    else:
        token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    # Get the agent's response
    messages = project_client.agents.messages.list(thread_id=thread.id)
    agent_response = ""
    
    print(f"Found {len(messages)} messages")
    for message in messages:
        print(f"Message role: {message.role}")
        if message.role == MessageRole.AGENT:
            print(f"Found agent message with {len(message.content)} content items")
            if message.content and len(message.content) > 0:
                agent_response = message.content[0].text.value
                print(f"Agent response length: {len(agent_response)} characters")
                break

    # Create simulated individual agent outputs by parsing the response
    agent_outputs = []
    if agent_response:
        # Split response into sections and create individual agent outputs
        sections = agent_response.split('##')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            if '1. PRODUCT IDEATION' in section.upper():
                agent_outputs.append({'agent': 'Ideation Agent', 'output': section})
            elif '2. USER PERSONAS' in section.upper():
                agent_outputs.append({'agent': 'Persona Generator Agent', 'output': section})
            elif '3. USER TESTING' in section.upper():
                agent_outputs.append({'agent': 'User Testing Agent', 'output': section})
            elif '4. MARKET FIT' in section.upper():
                agent_outputs.append({'agent': 'Market Fit Advisor', 'output': section})

    print(f"Generated {len(agent_outputs)} simulated agent outputs")
    for i, output in enumerate(agent_outputs):
        print(f"  {i+1}. {output['agent']}: {len(output['output'])} characters")

    # Clean up
    project_client.agents.delete_agent(agent.id)
    project_client.agents.threads.delete(thread.id)
    print("Cleanup completed")

    return agent_response, agent_outputs, token_usage

# -----------------------
# Streamlit UI Application
# -----------------------
def main():
    st.set_page_config(page_title="Product Ideation Suite", page_icon="💡", layout="wide")

    # Professional Modern CSS
    st.markdown(
        """
        <style>
        /* Global styling */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .header-title {
            font-size: 2rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0 0 8px 0;
            letter-spacing: -0.025em;
        }
        .header-subtitle {
            font-size: 1rem;
            color: #64748b;
            margin: 0;
            font-weight: 400;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'token_totals' not in st.session_state:
        st.session_state.token_totals = {'prompt':0,'completion':0,'total':0}

    # Modern Header
    st.markdown(
        """
        <div class='header-container'>
            <div class='header-title'>💡 Product Ideation Suite</div>
            <div class='header-subtitle'>Multi-agent AI system for comprehensive product development analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Create two columns for the main content
    col1, col2 = st.columns([1.2, 1], gap="large")

    # LEFT COLUMN: Summarized Response
    with col1:
        st.markdown("### 📋 Executive Summary")
        
        # Get the latest combined response from chat history
        combined_response = ""
        if st.session_state.chat_history:
            for msg in reversed(st.session_state.chat_history):
                if msg.get('role') == 'system' and not msg.get('content', '').startswith('Error:'):
                    combined_response = msg.get('content', '')
                    break
        
        if combined_response:
            # Display in a scrollable container
            with st.container(height=500):
                st.markdown(combined_response)
        else:
            st.info("No analysis available yet. Submit a product idea to generate comprehensive insights.")

    # RIGHT COLUMN: Individual Agent Outputs
    with col2:
        st.markdown("### 🤖 Agent Insights")
        
        if st.session_state.agent_outputs:
            grouped = group_by_agent(st.session_state.agent_outputs)
            
            # Debug information
            st.write(f"**Debug Info:** Found {len(st.session_state.agent_outputs)} total agent outputs")
            st.write(f"**Debug Info:** Grouped into {len(grouped)} different agents")
            for agent, outputs in grouped.items():
                st.write(f"- {agent}: {len(outputs)} outputs")
            
            # Display agent outputs in scrollable container
            with st.container(height=500):
                for agent_name, outputs in grouped.items():
                    outputs_ordered = list(reversed(outputs))
                    latest = outputs_ordered[0]
                    count_text = f" ({len(outputs)} outputs)" if len(outputs) > 1 else ""
                    
                    with st.expander(f"🔧 {agent_name}{count_text}", expanded=False):
                        st.markdown(latest)
        else:
            st.info("No agent outputs available yet. Submit a prompt to see individual agent analyses.")
    
    # Input and Controls Section
    st.markdown("### 💭 New Product Ideation Prompt")
    
    user_prompt = st.chat_input("Enter your product idea (e.g., 'AI-driven fitness coaching platform for seniors' or 'Eco-friendly packaging for meal kits')")
    
    if user_prompt and not st.session_state.processing:
        st.session_state.processing = True
        st.session_state.chat_history.append({'role':'user','content':user_prompt})
        
        with st.spinner('Running multi-agent ideation pipeline...'):
            try:
                combined, agent_outputs, usage = connected_agent_productideation(user_prompt)
                
                # Debug outputs
                st.write(f"**Debug:** Returned {len(agent_outputs)} agent outputs from function")
                for i, ao in enumerate(agent_outputs):
                    st.write(f"  {i+1}. Agent: {ao.get('agent', 'Unknown')}, Output length: {len(str(ao.get('output', '')))}")
                
                # Update outputs (dedupe by agent+hash of output snippet)
                existing_pairs = {(o['agent'], o.get('output')[:60]) for o in st.session_state.agent_outputs}
                for ao in agent_outputs:
                    pair = (ao.get('agent'), ao.get('output','')[:60])
                    if pair not in existing_pairs:
                        st.session_state.agent_outputs.append(ao)
                
                st.write(f"**Debug:** Total agent outputs in session state: {len(st.session_state.agent_outputs)}")
                
                # Append combined text as system summary message
                st.session_state.chat_history.append({'role':'system','content': combined})
                
                # Token usage
                st.session_state.token_totals['prompt'] += usage.get('prompt_tokens',0)
                st.session_state.token_totals['completion'] += usage.get('completion_tokens',0)
                st.session_state.token_totals['total'] += usage.get('total_tokens',0)
                
            except Exception as e:
                st.session_state.chat_history.append({'role':'system','content': f'Error: {e}'})
                st.error(f"Error: {e}")
        
        st.session_state.processing = False
        st.rerun()
    
    # Controls and metrics
    st.divider()
    
    col1, col2, col3, col4 = st.columns([1.5, 2, 2, 1.5])
    
    with col1:
        if st.button('🗑️ Clear All', help='Reset all data', use_container_width=True):
            st.session_state.chat_history.clear()
            st.session_state.agent_outputs.clear()
            st.session_state.token_totals = {'prompt':0,'completion':0,'total':0}
            st.rerun()
    
    with col2:
        st.metric(
            label="📊 Token Usage",
            value=f"{st.session_state.token_totals['total']:,}",
            delta=f"Prompt: {st.session_state.token_totals['prompt']:,} | Completion: {st.session_state.token_totals['completion']:,}"
        )
    
    with col3:
        status_text = "🔄 Processing..." if st.session_state.processing else "✅ Ready"
        agents_count = len(set(o.get('agent', '') for o in st.session_state.agent_outputs))
        st.metric(
            label=f"Status: {status_text}",
            value=f"{agents_count} agents",
            delta=f"{len(st.session_state.agent_outputs)} outputs"
        )
    
    with col4:
        if st.session_state.chat_history:
            sessions = len([msg for msg in st.session_state.chat_history if msg.get('role') == 'user'])
            st.metric(
                label="📈 Sessions",
                value=f"{sessions} completed"
            )

if __name__ == "__main__":
    main()
