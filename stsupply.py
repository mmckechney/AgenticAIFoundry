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

def supplychain_agent(query: str) -> str:
    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )

    plan_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="planagent",
        instructions="""You are an AI agent in the Plan stage of the healthcare and life sciences supply chain, focused on demand and supply planning. Your goal is to forecast needs, allocate resources, and align strategies to balance supply with demand while considering regulatory changes, market volatility, and patient-centric outcomes.
        When given a query or scenario (e.g., product type like a vaccine or medical device, market data, or disruption event), perform the following tasks step-by-step:

        Analyze provided data: Review historical sales, market trends, emerging health issues, and patient feedback to forecast demand. Use tools like statistical models or AI simulations if available.
        Develop supply plans: Calculate inventory levels, production schedules, and resource needs (e.g., staff, equipment). Factor in regulatory timelines such as clinical trials.
        Conduct risk assessments: Simulate scenarios for disruptions (e.g., raw material shortages) and recommend mitigation strategies like buffer stocks.
        Align teams: Integrate inputs from R&D, commercial, and supply chain teams, emphasizing patient-centric elements like personalization for therapies.
        Leverage analytics: Apply AI, digital twins, or data visualization to enhance visibility and accuracy across the chain.

        Output a structured report including forecasts, plans, risks, and recommendations. Ensure compliance with standards like FDA/EMA guidelines. If data is missing, request it explicitly.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "planagent"
    plan_connected_agent = ConnectedAgentTool(
        id=plan_agent.id, name=connected_agent_name, description="Plan stage of the healthcare and life sciences supply chain, focused on demand and supply planning."
    )

    source_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="sourceagent",
        instructions="""You are an AI agent in the Source stage of the healthcare and life sciences supply chain, specializing in procurement and supplier management. Your objective is to source high-quality raw materials, components, and services while ensuring ethical standards, compliance, and supply resilience.
        When provided with a sourcing request (e.g., APIs for pharmaceuticals, biological materials for biotech, or components for devices), execute these tasks sequentially:

        Identify suppliers: Search and evaluate potential vendors based on quality certifications (e.g., GMP), reliability, ethical practices (e.g., fair labor, no conflict minerals), and sustainability.
        Negotiate contracts: Draft or review terms including quality assurances, contingency plans, and buffers for emergencies. Aim for cost-effectiveness and risk reduction.
        Perform audits: Simulate or plan supplier due diligence, including traceability checks (e.g., via blockchain) for upstream materials.
        Manage partnerships: Recommend supplier diversification to avoid dependencies (e.g., multiple regions for APIs) and foster strategic relationships.
        Procure materials: Specify requirements meeting regulatory standards (e.g., FDA preclinical) and align with ESG goals like low-carbon sourcing.

        Generate an output summary with supplier recommendations, contract outlines, audit findings, and procurement plans. Highlight any risks like global dependencies. If additional data (e.g., supplier databases) is needed, query for it.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "sourceagent"
    source_connected_agent = ConnectedAgentTool(
        id=source_agent.id, name=connected_agent_name, description="Source stage of the healthcare and life sciences supply chain, specializing in procurement and supplier management."
    )

    make_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="makeagent",
        instructions="""You are an AI agent in the Make stage of the healthcare and life sciences supply chain, responsible for manufacturing and production. Your focus is on transforming raw materials into finished products with strict quality control, scalability, and regulatory adherence.
        Upon receiving a production directive (e.g., for drug formulation, biotech cell cultures, or device assembly), follow these steps:

        Secure approvals: Verify or simulate regulatory clearances (e.g., FDA manufacturing authorization) and prepare facilities with necessary tech and supplies.
        Execute production: Detail processes like chemical compounding, biologics fermentation, or assembly, ensuring GMP and GLP compliance.
        Implement quality controls: Plan in-process inspections, stability tests, and deviation handling, incorporating AI for real-time monitoring.
        Package and label: Specify protective packaging (e.g., tamper-evident) and accurate labeling with serialization for traceability.
        Scale operations: Recommend automation (e.g., robotics) and continuous manufacturing to optimize lead times and efficiency.

        Produce a detailed production report including process flows, quality metrics, packaging specs, and scaling strategies. Note challenges like material delays and ensure patient safety emphasis. Request any missing inputs like raw material specs.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "makeagent"
    make_connected_agent = ConnectedAgentTool(
        id=make_agent.id, name=connected_agent_name, description="Make stage of the healthcare and life sciences supply chain, responsible for manufacturing and production."
    )

    deliver_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="deliveragent",
        instructions="""You are an AI agent in the Deliver stage of the healthcare and life sciences supply chain, handling distribution and logistics. Your aim is to ensure efficient, compliant delivery of products to wholesalers, providers, or patients, with special attention to cold-chain requirements.
        When tasked with a delivery scenario (e.g., shipping vaccines or devices, including routes and quantities), perform these actions in order:

        Manage fulfillment: Outline picking, packing, and shipping from warehouses to distributors.
        Coordinate logistics: Plan transport modes (e.g., refrigerated trucks, air freight) compliant with standards like IATA for hazardous items.
        Handle distribution: Detail wholesaler/reseller processes (e.g., bulk storage and resale) or repackaging for markets.
        Ensure last-mile: Specify delivery to end-points (e.g., hospitals, direct-to-patient) with real-time tracking and temperature monitoring.
        Collaborate for visibility: Use IoT or control towers for monitoring and rerouting during issues.

        Deliver an output with logistics plans, timelines, tracking methods, and cost estimates. Address challenges like spoilage risks. If logistics data (e.g., routes) is unavailable, request it.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "deliveragent"
    deliver_connected_agent = ConnectedAgentTool(
        id=deliver_agent.id, name=connected_agent_name, description="Deliver stage of the healthcare and life sciences supply chain, handling distribution and logistics."
    )

    return_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="returnagent",
        instructions="""You are an AI agent in the Return stage of the healthcare and life sciences supply chain, managing reverse logistics and post-market activities. Your purpose is to handle returns, recalls, waste, and surveillance for safety and sustainability.
        Given a return or post-market event (e.g., product recall, expired items, or adverse reports), proceed step-by-step:

        Process returns/recalls: Quarantine items, notify regulators and stakeholders, and execute retrieval.
        Manage disposal: Plan compliant handling of hazardous waste (e.g., expired drugs) per environmental regulations.
        Monitor post-market: Analyze adverse events or efficacy data to inform improvements.
        Implement traceability: Use systems for efficient recall tracking to minimize impacts.
        Promote sustainability: Suggest recycling or repurposing, aligning with ESG objectives.

        Output a comprehensive report on actions taken, compliance checks, monitoring insights, and sustainability recommendations. Emphasize ethical waste management. Query for any needed data like event details.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "returnagent"
    return_connected_agent = ConnectedAgentTool(
        id=return_agent.id, name=connected_agent_name, description="Return stage of the healthcare and life sciences supply chain, managing reverse logistics and post-market activities."
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="PresalesAgent",
        instructions="""
         You are a Supply chain specialist and orchestrator. Use the provided tools to answer the user's questions comprehensively.
        Be postive and professional in your responses. Provide detailed and structured answers.

        Analyzing the Query: Understand the user's question, identify key elements (e.g., specific products like vaccines or devices, scenarios like disruptions or optimizations, or broad overviews), and determine which supply chain stages are relevant. Not all stages need to be invoked for every query—select only those that apply to provide efficient, targeted responses.
        Decomposing and Delegating: Break the query into sub-tasks if needed. Invoke the appropriate sub-agents sequentially or in parallel (e.g., Plan before Make for forecasting-dependent queries). Use their outputs to build a holistic answer.
        Integrating Outputs: Synthesize responses from sub-agents into a cohesive, expert-level reply. Highlight interconnections between stages (e.g., how sourcing risks affect manufacturing). Ensure the response is patient-centric, compliant with regulations (e.g., FDA/EMA), and addresses challenges like resilience, sustainability, and digital tools.
        Maintaining Chat Style: Respond conversationally—be engaging, ask clarifying questions if the query is ambiguous (e.g., "Could you specify the product type or region?"), and build on previous context in multi-turn chats. Use bullet points, tables, or structured formats for clarity when presenting data or tasks.
        Reasoning Step-by-Step: Before responding, think internally: Outline the relevant stages, why they're chosen, and how to sequence invocations. If no sub-agents are needed (e.g., for general advice), provide direct expertise.
        Invocation Format: To call a sub-agent, use a clear internal command like: [Invoke: Plan Agent] followed by the specific query or scenario for that agent. Assume sub-agents will return structured reports as per their prompts. Do not simulate their responses—treat invocations as actual calls in your system.

        Here are the list of Agents to involve and get response from all
        Plan Agent: Plan stage of the healthcare and life sciences supply chain, focused on demand and supply planning.
        Source Agent: Source stage of the healthcare and life sciences supply chain, specializing in procurement and supplier management.
        Make Agent: Make stage of the healthcare and life sciences supply chain, responsible for manufacturing and production.
        Deliver Agent: Deliver stage of the healthcare and life sciences supply chain, ensuring quality assurance and analytical support in adhesive R&D.
        Return Agent: Return stage of the healthcare and life sciences supply chain, facilitating collaborative integration in the final R&D stage for adhesive products.

        
        Final Response Guidelines: Always end with a complete, standalone answer. If the query spans multiple stages, present in SCOR order. Emphasize real-world applicability, innovations (e.g., AI, blockchain), and any overarching considerations like ESG or digital transformation.  
        Summarize all the results and also provide Detail flow and sequence diagram in Mermaid format
        Also provide the Architecture pro's and con's.       
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            plan_connected_agent.definitions[0],
            source_connected_agent.definitions[0],
            make_connected_agent.definitions[0],
            deliver_connected_agent.definitions[0],
            return_connected_agent.definitions[0],
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
    agent_outputs = parse_agent_outputs(run_steps)
    
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
            returntxt += f"Source: {message.content[0].text.value}\n"

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)    
    project_client.agents.threads.delete(thread.id)
    # print("Deleted agent")
    # Delete the connected Agent when done
    project_client.agents.delete_agent(plan_agent.id)
    project_client.agents.delete_agent(source_agent.id)
    project_client.agents.delete_agent(make_agent.id)
    project_client.agents.delete_agent(deliver_agent.id)
    project_client.agents.delete_agent(return_agent.id)
    print("Deleted connected agent")
    # # Cleanup resources
    

    return returntxt, agent_outputs, token_usage

def supplychain_analyst():
    """Streamlit UI for Supply Chain Agent with chat history and individual agent outputs."""
    st.set_page_config(
        page_title="Healthcare Supply Chain Analyst", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for scrollable containers
    st.markdown("""
        <style>
        .chat-container {
            height: 10px;
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 15px;
            background-color: #f8f9fa;
            margin-bottom: 20px;
        }
        
        .agent-container {
            height: 10;
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 15px;
            background-color: #ffffff;
            margin-bottom: 20px;
        }
        
        /* Ensure Streamlit components fit within containers */
        .chat-container .element-container,
        .agent-container .element-container {
            margin-bottom: 1rem;
        }
        
        /* Style for better readability */
        .chat-container p,
        .agent-container p {
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }
        
        /* Expander styling within containers */
        .agent-container .streamlit-expanderHeader {
            background-color: #f0f2f6;
            border-radius: 4px;
            padding: 8px 12px;
            margin-bottom: 8px;
        }
        
        .agent-container .streamlit-expanderContent {
            padding: 10px;
            background-color: #fafbfc;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        /* Divider styling */
        .chat-container hr {
            margin: 10px 0;
            border-color: #dee2e6;
        }
        
        /* Prevent content overflow */
        .chat-container > div,
        .agent-container > div {
            max-width: 100%;
            word-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = []
    if 'token_usage' not in st.session_state:
        st.session_state.token_usage = []
    
    # Header
    st.title("🏥 Healthcare Supply Chain Analyst")
    st.markdown("*End-to-end supply chain analysis for healthcare and life sciences*")
    st.divider()
    
    # Create two columns for chat history and agent outputs
    left_col, right_col = st.columns([1, 1.2], gap="medium")
    
    # Left column: Chat History
    with left_col:
        st.subheader("💬 Chat History")
        
        # Create a container with scrollable content
        chat_container = st.container(height=600)
        with chat_container:
            # Apply custom styling for scrollable area
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            if not st.session_state.chat_history:
                st.write("Welcome! Ask me anything about healthcare supply chain management.")
                st.write("I can help with planning, sourcing, manufacturing, delivery, and returns.")
            else:
                # Display each message in the chat history
                for i, (role, message, timestamp) in enumerate(st.session_state.chat_history):
                    if role == "user":
                        st.markdown(f"**🧑‍💼 You** *({timestamp})*")
                        st.write(message)
                    else:
                        st.markdown(f"**🤖 Assistant** *({timestamp})*")
                        st.write(message)
                    st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Right column: Agent Outputs
    with right_col:
        st.subheader("🤖 Individual Agent Outputs")
        
        # Create a container with scrollable content for agent outputs
        agent_container = st.container(height=600)
        with agent_container:
            # Apply custom styling for scrollable area
            st.markdown('<div class="agent-container">', unsafe_allow_html=True)
            
            if not st.session_state.agent_outputs:
                st.write("Individual agent outputs will appear here after you submit a question.")
                st.write("Each supply chain stage agent will provide detailed analysis:")
                st.write("• **Plan Agent** - Demand & supply planning")
                st.write("• **Source Agent** - Procurement & suppliers")
                st.write("• **Make Agent** - Manufacturing & production")
                st.write("• **Deliver Agent** - Distribution & logistics")
                st.write("• **Return Agent** - Reverse logistics & recalls")
            else:
                # Show agent outputs from the most recent query
                latest_outputs = st.session_state.agent_outputs[-1] if st.session_state.agent_outputs else {}
                
                if latest_outputs:
                    for agent_name, output in latest_outputs.items():
                        # Use expander for each agent output
                        with st.expander(f"🔍 {agent_name.title()}", expanded=False):
                            st.write(output)
                else:
                    st.write("No individual agent outputs available for the latest response.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✏️ Ask a Question")
    
    user_input = st.chat_input("Type your supply chain question here...")
    
    if user_input:
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append(("user", user_input, timestamp))
        
        # Show processing message
        with st.spinner("🔄 Processing your request through the supply chain agents...", show_time=True):
            try:
                # Call the supply chain agent
                response, agent_outputs, token_usage = supplychain_agent(user_input)
                
                # Add assistant response to history
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history.append(("assistant", response, timestamp))
                
                # Store agent outputs and token usage
                st.session_state.agent_outputs.append(agent_outputs)
                st.session_state.token_usage.append(token_usage)
                
                # Show success message
                st.success("✅ Analysis complete! Check the outputs above.")
                
            except Exception as e:
                st.error(f"❌ Error processing request: {str(e)}")
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history.append(
                    ("assistant", f"Sorry, I encountered an error: {str(e)}", timestamp)
                )
        
        # Rerun to update the display
        st.rerun()
    
    # Sidebar with additional information
    with st.sidebar:
        st.header("📊 Session Info")
        
        # Chat statistics
        st.metric("Total Messages", len(st.session_state.chat_history))
        st.metric("Agent Responses", len(st.session_state.agent_outputs))
        
        # Token usage summary
        if st.session_state.token_usage:
            total_tokens = sum(usage.get('total_tokens', 0) for usage in st.session_state.token_usage)
            st.metric("Total Tokens Used", total_tokens)
        
        st.divider()
        
        # Supply chain stages info
        st.subheader("🔄 Supply Chain Stages")
        st.write("**Plan** - Demand & supply planning")
        st.write("**Source** - Procurement & suppliers")
        st.write("**Make** - Manufacturing & production")  
        st.write("**Deliver** - Distribution & logistics")
        st.write("**Return** - Reverse logistics & recalls")
        
        st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.agent_outputs = []
            st.session_state.token_usage = []
            st.success("Chat history cleared!")
            st.rerun()

if __name__ == "__main__":
    supplychain_analyst()
