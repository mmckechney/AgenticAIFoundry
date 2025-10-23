import asyncio
import base64
import datetime
import os, time, json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
    FunctionTool,
    MessageRole,
    ConnectedAgentTool,
    FilePurpose,
    MessageInputTextBlock,
    MessageInputImageFileBlock,
    MessageImageFileParam,
)
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
from azure.ai.agents.aio import AgentsClient
import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini

# Get MCP server configuration from environment variables
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "MicrosoftLearn")

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
# connection_string = project_client.telemetry.get_application_insights_connection_string()
connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def collect_supply_chain_data():
    # Simulate data collection from multi-tier supply chain
    return json.dumps({
        "tier1": {"status": "active", "delay": 0},
        "tier2": {"status": "active", "delay": 2},
        "tier3": {"status": "delayed", "delay": 5}
    })

def predict_disruptions(data):
    # Simulate disruption prediction
    risk_score = sum(item["delay"] for item in data.values()) * 10
    return json.dumps({"risk_score": risk_score, "mitigation": "Increase buffer stock"})

def simulate_sourcing_scenarios(data):
    # Simulate alternative sourcing scenarios
    scenarios = [
        {"scenario": "Switch to Tier1", "cost": 1000, "time": 3},
        {"scenario": "Switch to Tier2", "cost": 1500, "time": 5}
    ]
    return json.dumps(scenarios)

def optimize_inventory(data):
    # Simulate inventory optimization
    optimized_levels = {key: 100 + value["delay"] * 10 for key, value in data.items()}
    return json.dumps(optimized_levels)

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
    # Define user functions
    user_functions = {collect_supply_chain_data}
    # Initialize the FunctionTool with user-defined functions
    functions = FunctionTool(functions=user_functions)
    supplychainmonitoragent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="supplychainmonitoragent",
        instructions="""Continuously collect and analyze data from various tiers of the supply chain. 
        Identify anomalies and report status updates.
        """,
        #tools=functions.definitions,
        #tools=... # tools to help the agent get stock prices
    )
    supplychainmonitor_agent_name = "supplychainmonitoragent"
    supplychainmonitoragent_connected_agent = ConnectedAgentTool(
        id=supplychainmonitoragent.id, name=supplychainmonitor_agent_name, description="Monitors real-time data across the multi-tier supply chain."
    )

    user_functions_disruption = {predict_disruptions}
    # Initialize the FunctionTool with user-defined functions
    functions = FunctionTool(functions=user_functions_disruption)
    disruptionpredictionagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="disruptionpredictionagent",
        instructions="""Use historical and real-time data to forecast potential disruptions. 
        Provide risk scores and mitigation suggestions.
        """,
        #tools=functions.definitions,
        #tools=... # tools to help the agent get stock prices
    )
    disruptionprediction_agent_name = "disruptionpredictionagent"
    disruptionpredictionagent_connected_agent = ConnectedAgentTool(
        id=disruptionpredictionagent.id, name=disruptionprediction_agent_name, description="Analyzes data to predict potential disruptions."
    )

    user_functions_simulation = {simulate_sourcing_scenarios}
    # Initialize the FunctionTool with user-defined functions
    functions = FunctionTool(functions=user_functions_simulation)
    scenariosimulationagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="scenariosimulationagent",
        instructions="""Generate and evaluate alternative sourcing scenarios based on current supply chain data and predicted disruptions.
        """,
        #tools=functions.definitions,
        #tools=... # tools to help the agent get stock prices
    )
    scenariosimulation_agent_name = "scenariosimulationagent"
    scenariosimulationagent_connected_agent = ConnectedAgentTool(
        id=scenariosimulationagent.id, name=scenariosimulation_agent_name, description="Simulates alternative sourcing scenarios."
    )

    user_functions_optimize = {optimize_inventory}
    # Initialize the FunctionTool with user-defined functions
    functions = FunctionTool(functions=user_functions_optimize)
    inventoryoptimizationagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="inventoryoptimizationagent",
        instructions="""Analyze inventory levels across global facilities and recommend adjustments to maintain resilience and efficiency.
        """,
        #tools=functions.definitions,
        #tools=... # tools to help the agent get stock prices
    )
    inventoryoptimization_agent_name = "inventoryoptimizationagent"
    inventoryoptimizationagent_connected_agent = ConnectedAgentTool(
        id=inventoryoptimizationagent.id, name=inventoryoptimization_agent_name, description="Optimizes inventory levels across global facilities."
    )
    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SupplyChainMFGAgent",
        instructions="""You are a Manufacturing Supply chain specialist and orchestrator. Use the provided tools to answer the user's questions comprehensively.
        Be positive and professional in your responses. Provide detailed and structured answers.

        Analyzing the Query: Understand the user's question, identify key elements (e.g., specific products like vaccines or devices, scenarios like disruptions or optimizations, or broad overviews), and determine which supply chain stages are relevant. Not all stages need to be invoked for every query—select only those that apply to provide efficient, targeted responses.
        Decomposing and Delegating: Break the query into sub-tasks if needed. Invoke the appropriate sub-agents sequentially or in parallel (e.g., Plan before Make for forecasting-dependent queries). Use their outputs to build a holistic answer.
        Integrating Outputs: Synthesize responses from sub-agents into a cohesive, expert-level reply. Highlight interconnections between stages (e.g., how sourcing risks affect manufacturing). Ensure the response is patient-centric, compliant with regulations (e.g., FDA/EMA), and addresses challenges like resilience, sustainability, and digital tools.
        Maintaining Chat Style: Respond conversationally—be engaging, ask clarifying questions if the query is ambiguous (e.g., "Could you specify the product type or region?"), and build on previous context in multi-turn chats. Use bullet points, tables, or structured formats for clarity when presenting data or tasks.
        Reasoning Step-by-Step: Before responding, think internally: Outline the relevant stages, why they're chosen, and how to sequence invocations. If no sub-agents are needed (e.g., for general advice), provide direct expertise.
        Invocation Format: To call a sub-agent, use a clear internal command like: [Invoke: Supply Chain Monitor Agent] followed by the specific query or scenario for that agent. Assume sub-agents will return structured reports as per their prompts. Do not simulate their responses—treat invocations as actual calls in your system.

        Here are the list of Agents to involve and get response from all
        Supply Chain Monitor Agent: Monitors real-time data across the multi-tier supply chain.
        Disruption Prediction Agent: Analyzes data to predict potential disruptions.
        Scenario Simulation Agent: Simulates alternative sourcing scenarios.
        Inventory Optimization Agent: Optimizes inventory levels across global facilities.

        Final Response Guidelines: Always end with a complete, standalone answer. If the query spans multiple stages, present in SCOR order. Emphasize real-world applicability, innovations (e.g., AI, blockchain), and any overarching considerations like ESG or digital transformation.
        Summarize all the results and also provide Detail flow and sequence diagram in Mermaid format
        Also provide the Architecture pro's and con's.       
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            supplychainmonitoragent_connected_agent.definitions[0],
            disruptionpredictionagent_connected_agent.definitions[0],
            scenariosimulationagent_connected_agent.definitions[0],
            inventoryoptimizationagent_connected_agent.definitions[0],
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
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id,
                                                        temperature=0, parallel_tool_calls=False)
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
    project_client.agents.delete_agent(supplychainmonitoragent.id)
    project_client.agents.delete_agent(disruptionpredictionagent.id)
    project_client.agents.delete_agent(scenariosimulationagent.id)
    project_client.agents.delete_agent(inventoryoptimizationagent.id)
    print("Deleted connected agent")
    # # Cleanup resources
    

    return returntxt, agent_outputs, token_usage

def supplychainmain():
    st.set_page_config(
        page_title="Manufacturing Supply Chain Analyst", 
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
    st.title("� Manufacturing Supply Chain Analyst")
    st.markdown("*End-to-end supply chain analysis for manufacturing and production*")
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
                st.write("Welcome! Ask me anything about manufacturing supply chain management.")
                st.write("I can help with supply chain monitoring, disruption prediction, scenario simulation, and inventory optimization.")
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
                st.write("Each specialized agent will provide detailed analysis:")
                st.write("• **Supply Chain Monitor Agent** - Real-time data monitoring across multi-tier supply chain")
                st.write("• **Disruption Prediction Agent** - Forecasting potential disruptions with risk scores")
                st.write("• **Scenario Simulation Agent** - Alternative sourcing scenario evaluation")
                st.write("• **Inventory Optimization Agent** - Global inventory level recommendations")
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
        
        # Supply chain agents info
        st.subheader("🤖 Active Agents")
        st.write("**Supply Chain Monitor** - Multi-tier data collection & anomaly detection")
        st.write("**Disruption Prediction** - Risk forecasting & mitigation strategies")
        st.write("**Scenario Simulation** - Alternative sourcing evaluation")  
        st.write("**Inventory Optimization** - Global facility inventory management")
        
        st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.agent_outputs = []
            st.session_state.token_usage = []
            st.success("Chat history cleared!")
            st.rerun()

if __name__ == "__main__":
    supplychainmain()