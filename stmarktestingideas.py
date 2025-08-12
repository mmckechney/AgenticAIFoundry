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
# model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini
WHISPER_DEPLOYMENT_NAME = "whisper"
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

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
# Helper: parse agent outputs from run steps
# -----------------------
def parse_agent_outputs(run_steps):
    """Parse agent outputs from run steps to extract individual agent responses."""
    agent_outputs = {}
    
    for step in run_steps:
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])
        
        if tool_calls:
            for call in tool_calls:
                connected_agent = call.get("connected_agent", {})
                if connected_agent:
                    agent_name = connected_agent.get("name", "Unknown Agent")
                    agent_output = connected_agent.get("output", "No output available")
                    agent_outputs[agent_name] = agent_output
    
    return agent_outputs

# -----------------------
# Helper: summarization (light heuristic)
# -----------------------
def build_summary(agent_outputs: List[Dict[str, str]]) -> str:
    if not agent_outputs:
        return "No agent outputs yet. Submit an ideation prompt to generate content."
    lines = []
    for item in agent_outputs:
        name = item.get('agent', 'Agent')
        raw = item.get('output', '') or ''
        # Extract first 2 sentences / 220 chars max
        snippet = raw.replace('\n', ' ')
        if len(snippet) > 220:
            snippet = snippet[:217] + '...'
        lines.append(f"- {name}: {snippet}")
    return "\n".join(lines)

# -----------------------
# Helper: group outputs per agent
# -----------------------
def group_by_agent(outputs: List[Dict[str, str]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    
    # Handle cases where outputs might be corrupted or wrong type
    if not outputs:
        return grouped
        
    for o in outputs:
        # Handle case where o might not be a dictionary
        if not isinstance(o, dict):
            print(f"Warning: Expected dict but got {type(o)}: {o}")
            continue
            
        agent = o.get('agent', 'Agent')
        grouped.setdefault(agent, []).append(o.get('output', '') or '')
    return grouped

def connected_agent_productideation(query: str) -> str:
    returntxt = ""
    #https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/connected-agents?pivots=python

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    ideation_agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="ideationagent",
        instructions="""You are a Creative Product Ideation Agent, part of a marketing team AI system. Your sole task is to generate innovative product design ideas based on the user's input seed (e.g., industry, problem, or concept). 

        Follow these steps strictly:
        1. Understand the input seed and brainstorm 3-5 unique product concepts. Each concept should include:
        - Product Name: A catchy, memorable name.
        - Description: A 2-3 sentence overview of what the product is and how it works.
        - Key Features: Bullet list of 4-6 main features.
        - Unique Selling Points (USPs): What makes it stand out from competitors.
        - Initial Target Audience: Broad demographics (e.g., age groups, interests) without specific personas yet.
        2. Ensure ideas are feasible, market-relevant, and diverse (e.g., vary in complexity or price point).
        3. Output in JSON format for easy parsing:
        {
            "ideas": [
            {
                "name": "...",
                "description": "...",
                "features": ["...", "..."],
                "usps": ["...", "..."],
                "target_audience": "..."
            },
            ...
            ]
        }

        Do not add extra commentary, questions, or steps outside this structure. If no seed is provided, default to a general category like 'consumer tech'.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "ideationagent"
    ideation_connected_agent = ConnectedAgentTool(
        id=ideation_agent.id, name=connected_agent_name, description="Creative ideation and innovation catalyst"
    )

    personagenerator_agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="personageneratoragent",
        instructions="""You are a User Persona Generator Agent, part of a marketing team AI system. Your task is to create diverse, realistic user personas for testing product ideas. Input will be a JSON list of product ideas from the ideation phase.

        Follow these steps strictly:
        1. For each product idea, generate 8-10 personas that cover a wide demographic spectrum:
        - Ages: Include young adults (18-25), millennials (26-40), Gen X (41-60), seniors (60+).
        - Sexes: Male, female, non-binary, or other.
        - Ethnicities: Caucasian, African American, Hispanic/Latino, Asian, Middle Eastern, Indigenous, etc. (aim for global diversity).
        - Other Factors: Vary occupations (e.g., student, professional, retiree), income levels (low, middle, high), locations (urban, rural, international), tech-savviness, interests, and pain points related to the product category.
        2. Each persona should include:
        - Name: Realistic full name.
        - Age: Number.
        - Gender: String.
        - Ethnicity: String.
        - Occupation: String.
        - Location: City/Country.
        - Income Level: Low/Medium/High.
        - Interests: Bullet list of 3-5.
        - Pain Points: Bullet list of 2-4 related to the product idea.
        3. Output in JSON format, grouped by product idea:
        {
            "product_ideas_personas": [
            {
                "product_name": "...",
                "personas": [
                {
                    "name": "...",
                    "age": ...,
                    "gender": "...",
                    "ethnicity": "...",
                    "occupation": "...",
                    "location": "...",
                    "income_level": "...",
                    "interests": ["...", "..."],
                    "pain_points": ["...", "..."]
                },
                ...
                ]
            },
            ...
            ]
        }

        Ensure personas are unbiased, inclusive, and varied. Do not repeat similar personas. No extra text outside the JSON.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "personageneratoragent"
    personagenerator_connected_agent = ConnectedAgentTool(
        id=personagenerator_agent.id, name=connected_agent_name, description="Persona Generation Expert, part of a marketing team AI system"
    )

    usertesting_analyst = project_client.agents.create_agent(
        model=model_deployment_name,
        name="usertesting",
        instructions="""
        You are a User Testing Simulation Agent, part of a marketing team AI system. Your task is to simulate feedback from diverse personas on a product idea. Input will be a JSON with product ideas and their associated personas.

        Follow these steps strictly:
        1. For each product idea and each persona:
        - Role-play as the persona: Respond in first-person as if they are evaluating the product.
        - Provide balanced, realistic feedback based on the persona's age, gender, ethnicity, occupation, interests, and pain points.
        - Cover:
            - Likes: 3-5 positive aspects.
            - Dislikes: 2-4 potential issues.
            - Suggestions: 1-3 improvements.
            - Likelihood to Buy: Score from 1-10 (1=not at all, 10=definitely), with a brief reason.
        2. Simulate cultural/ethnic sensitivities where relevant (e.g., accessibility for different backgrounds).
        3. Output in JSON format:
        {
            "testing_results": [
            {
                "product_name": "...",
                "persona_name": "...",
                "feedback": {
                "likes": ["...", "..."],
                "dislikes": ["...", "..."],
                "suggestions": ["...", "..."],
                "likelihood_to_buy": ...,
                "reason": "..."
                }
            },
            ...
            ]
        }

        Keep feedback concise and persona-specific. No extra analysis or output outside JSON.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "usertesting"
    usertesting_connected_agent = ConnectedAgentTool(
        id=usertesting_analyst.id, name=connected_agent_name, description="User testing and feedback expert"
    )

    marketfit_advisor = project_client.agents.create_agent(
        model=model_deployment_name,
        name="marketfitadvisor",
        instructions="""
        You are a Market Fit Analysis Agent, part of a marketing team AI system. Your task is to analyze simulated user testing feedback for product ideas and determine market fit. Input will be a JSON of testing results from multiple personas.

        Follow these steps strictly:
        1. Aggregate feedback across all personas for each product idea:
        - Calculate average Likelihood to Buy score.
        - Identify common themes: Strengths (recurring likes), Weaknesses (recurring dislikes), Opportunities (from suggestions).
        - Segment by demographics: E.g., high fit for young Asians but low for senior Caucasians.
        - Overall Market Fit: Rate as Poor/Fair/Good/Excellent, with justification based on diversity coverage (ages, sexes, ethnicities).
        2. Provide recommendations: 3-5 actionable steps to improve fit (e.g., add features for specific groups).
        3. Output in JSON format:
        {
            "analysis": [
            {
                "product_name": "...",
                "average_likelihood": ...,
                "strengths": ["...", "..."],
                "weaknesses": ["...", "..."],
                "opportunities": ["...", "..."],
                "demographic_segments": {
                "high_fit": "... (e.g., ages 18-25, Asian ethnicity)",
                "low_fit": "..."
                },
                "overall_fit": "Poor/Fair/Good/Excellent",
                "justification": "...",
                "recommendations": ["...", "..."]
            },
            ...
            ]
        }

        Be objective, data-driven, and consider diversity biases. No extra text outside JSON.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "marketfitadvisor"
    marketfit_connected_agent = ConnectedAgentTool(
        id=marketfit_advisor.id, name=connected_agent_name, description="Market fit analysis expert"
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="MarketProductIdeasAgent",
        instructions="""
        You are a Marketing AI Agent your team is provided as agents. Use the provided tools to answer the user's questions comprehensively.
        Be postive and professional in your responses. Provide detailed and structured answers.

        Here are the list of Agents to involve and get response from all
        Ideation Agent: Creative ideation and innovation catalyst
        Persona Generator: User persona creation and analysis expert
        User Testing Agent: User testing and feedback specialist
        Market Fit Advisor: Market fit analysis expert

        Summarize all the results from each agent's output.
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            ideation_connected_agent.definitions[0],
            personagenerator_connected_agent.definitions[0],
            usertesting_connected_agent.definitions[0],
            marketfit_connected_agent.definitions[0],
        ]
    )
    
    print(f"Created agent, ID: {agent.id}")
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        # content="What is the stock price of Microsoft?",
        content=query,
    )
    print(f"Created message, ID: {message.id}")
    # Create and process Agent run in thread with tools
    # run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    # print(f"Run finished with status: {run.status}")
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    # Poll the run status until it is completed or requires action
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                print(f"Tool call: {tool_call.name}, ID: {tool_call.id}")

    print(f"Run completed with status: {run.status}")
    # print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Capture token usage information
    token_usage = {}
    if hasattr(run, 'usage') and run.usage:
        token_usage = {
            'prompt_tokens': getattr(run.usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(run.usage, 'completion_tokens', 0),
            'total_tokens': getattr(run.usage, 'total_tokens', 0)
        }
        print(f"Token usage - Prompt: {token_usage['prompt_tokens']}, Completion: {token_usage['completion_tokens']}, Total: {token_usage['total_tokens']}")
    else:
        # Try to get usage from run steps if not available in run object
        total_prompt_tokens = 0
        total_completion_tokens = 0
        run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            if hasattr(step, 'usage') and step.usage:
                total_prompt_tokens += getattr(step.usage, 'prompt_tokens', 0)
                total_completion_tokens += getattr(step.usage, 'completion_tokens', 0)
        
        token_usage = {
            'prompt_tokens': total_prompt_tokens,
            'completion_tokens': total_completion_tokens,
            'total_tokens': total_prompt_tokens + total_completion_tokens
        }
        print(f"Token usage from steps - Prompt: {token_usage['prompt_tokens']}, Completion: {token_usage['completion_tokens']}, Total: {token_usage['total_tokens']}")

    # Fetch run steps to get the details of the agent run
    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
    
    # Parse individual agent outputs
    agent_outputs_dict = parse_agent_outputs(run_steps)
    
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                connected_agent = call.get("connected_agent", {})
                if connected_agent:
                    print(f"    Connected Input(Name of Agent): {connected_agent.get('name')}")
                    print(f"    Connected Output: {connected_agent.get('output')}")

        print()  # add an extra newline between steps

    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        if message.role == MessageRole.AGENT:
            print(f"Role: {message.role}, Content: {message.content}")
            # returntxt += f"Role: {message.role}, Content: {message.content}\n"
            # returntxt += f"Source: {message.content[0]['text']['value']}\n"
            returntxt += f"Source: {message.content[0].text.value}\n"
    # returntxt = f"{message.content[-1].text.value}"

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)    
    project_client.agents.threads.delete(thread.id)
    # print("Deleted agent")
    # Delete the connected Agent when done
    project_client.agents.delete_agent(ideation_agent.id)
    project_client.agents.delete_agent(personagenerator_agent.id)
    project_client.agents.delete_agent(usertesting_analyst.id)
    project_client.agents.delete_agent(marketfit_advisor.id)

    print("Deleted connected agent")
    # # Cleanup resources
    

    return returntxt, agent_outputs_dict, token_usage

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
        
        /* Main layout container - removed flex since using st.columns */
        .main-content-height {
            height: calc(100vh - 280px);
            margin-bottom: 24px;
        }
        
        /* Content panels */
        .content-panel {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            height: calc(100vh - 280px);
        }
        
        .panel-header {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-bottom: 1px solid #e2e8f0;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .panel-title {
            font-size: 1rem;
            font-weight: 600;
            color: #374151;
            margin: 0;
        }
        .panel-icon {
            font-size: 1.2rem;
        }
        
        /* Scrollable content areas */
        .scrollable-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
        }
        
        /* Summary content styling */
        .summary-text {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #374151;
            white-space: pre-wrap;
            background: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        /* Agent cards styling */
        .agent-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 12px;
            overflow: hidden;
            transition: all 0.2s ease;
        }
        .agent-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
        }
        
        /* Input section */
        .input-container {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        .input-label {
            font-size: 1rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 12px;
            display: block;
        }
        
        /* Controls section */
        .controls-container {
            display: flex;
            gap: 16px;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
        }
        .metric-card {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 0.875rem;
            color: #1e40af;
        }
        .metric-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 0.75rem;
            opacity: 0.8;
        }
        
        /* Custom scrollbars */
        .scrollable-content::-webkit-scrollbar {
            width: 8px;
        }
        .scrollable-content::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        .scrollable-content::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 4px;
        }
        .scrollable-content::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
        }
        
        /* Empty state styling */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #64748b;
        }
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        .empty-text {
            font-size: 1rem;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )    # Session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # type: ignore
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = []  # type: ignore
    
    # Safety check: ensure agent_outputs is a list
    if not isinstance(st.session_state.agent_outputs, list):
        print(f"Warning: agent_outputs was {type(st.session_state.agent_outputs)}, resetting to list")
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

    # Create layout with summary on left and individual agents on right
    col1, col2 = st.columns([1, 1], gap="large")

    # LEFT COLUMN: Executive Summary Only
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
            with st.container(height=600):
                st.markdown(combined_response)
        else:
            st.info("No analysis available yet. Submit a product idea to generate comprehensive insights.")

    # RIGHT COLUMN: Individual Agent Sections
    with col2:
        st.markdown("### 🤖 Individual Agent Outputs")
        
        if st.session_state.agent_outputs:
            grouped = group_by_agent(st.session_state.agent_outputs)
            
            # Create scrollable container for all agents
            with st.container(height=600):
                # Create expandable sections for each agent
                for agent_name, outputs in grouped.items():
                    outputs_ordered = list(reversed(outputs))
                    latest = outputs_ordered[0]
                    count_text = f" ({len(outputs)} versions)" if len(outputs) > 1 else ""
                    
                    # Create expander for each agent
                    with st.expander(f"🔧 {agent_name}{count_text}", expanded=False):
                        # Format latest output - check if it's JSON first
                        formatted_latest = latest
                        is_json = False
                        try:
                            parsed = json.loads(latest)
                            formatted_latest = json.dumps(parsed, indent=2)
                            is_json = True
                        except Exception:
                            pass
                        
                        # Display latest output
                        st.markdown("**Latest Output:**")
                        if is_json:
                            st.code(formatted_latest, language='json')
                        else:
                            st.markdown(formatted_latest)
                        
                        # Show previous versions if any
                        if len(outputs_ordered) > 1:
                            st.markdown("---")  # Separator
                            st.markdown("**Previous Versions:**")
                            for i, older in enumerate(outputs_ordered[1:], 1):
                                with st.expander(f"📜 Version {i}", expanded=False):
                                    # Check if JSON
                                    try:
                                        parsed_old = json.loads(older)
                                        fm = json.dumps(parsed_old, indent=2)
                                        st.code(fm, language='json')
                                    except Exception:
                                        st.markdown(older)
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
                combined, agent_outputs_dict, usage = connected_agent_productideation(user_prompt)

                # Convert agent_outputs dictionary to list format expected by UI
                agent_outputs_list = []
                for agent_name, output in agent_outputs_dict.items():
                    agent_outputs_list.append({
                        'agent': agent_name,
                        'output': output
                    })

                # print combined output
                print(f"Combined output: {combined[:60]}...")  # Print first 60 chars for brevity
                # print agent_outputs
                print(' Individual agent outputs:')
                for ao in agent_outputs_list:
                    print(f" - {ao.get('agent')}: {ao.get('output')[:60]}...")

                # Update outputs (dedupe by agent+hash of output snippet)
                existing_pairs = {(o['agent'], o.get('output')[:60]) for o in st.session_state.agent_outputs}
                for ao in agent_outputs_list:
                    pair = (ao.get('agent'), ao.get('output','')[:60])
                    if pair not in existing_pairs:
                        st.session_state.agent_outputs.append(ao)
                
                # Append combined text as system summary message
                st.session_state.chat_history.append({'role':'system','content': combined})
                # Token usage
                st.session_state.token_totals['prompt'] += usage.get('prompt_tokens',0)
                st.session_state.token_totals['completion'] += usage.get('completion_tokens',0)
                st.session_state.token_totals['total'] += usage.get('total_tokens',0)
            except Exception as e:
                st.session_state.chat_history.append({'role':'system','content': f'Error: {e}'})
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
