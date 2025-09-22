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
)
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
import requests
import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
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

# Environment variables
AZURE_SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
AZURE_RESOURCE_GROUP = os.environ["AZURE_RESOURCE_GROUP"]
# AZURE_DATA_FACTORY_NAME = os.environ["AZURE_DATA_FACTORY_NAME"]

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

# idea here is to create agents first and then get them using name

def create_agents():
    """Create required agents (idempotent)."""
    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Helper: find by name
    def _find(name: str):
        try:
            for ag in project_client.agents.list_agents():
                if getattr(ag, 'name', None) == name:
                    return ag
        except Exception as ex:
            print(f"List error: {ex}")
        return None

    # Base agent
    base_agent = _find("baseagent")
    if not base_agent:
        base_agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="baseagent",
            instructions="Generic base agent to answer general knowledge questions.",
        )
        print(f"Created base agent, ID: {base_agent.id}")
    else:
        print(f"Base agent already exists: {base_agent.id}")

    azure_ai_conn_id = "vecdb"
    index_name = "constructionrfpdocs1"

    # Initialize the Azure AI Search tool
    ai_search = AzureAISearchTool(
        index_connection_id=azure_ai_conn_id,
        index_name=index_name,
        query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,  # Use VECTOR_SEMANTIC_HYBRID query type
        top_k=5,  # Retrieve the top 5 results
        filter="",  # Optional filter for search results
    )

    
    # Define the model deployment name
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    # Create an agent with the Azure AI Search tool
    rfp_agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="AISearchagent",
        instructions="You are a helpful agent",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )

    print(f"Created agent, ID: {rfp_agent.id}")
    #MCP microsoft Learn agent
    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
        allowed_tools=[],
    )
    Mcplearnagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="Mcplearnagent",
        instructions="You are a helpful agent and can search information from Microsoft Learn",
        tools=mcp_tool.definitions,
        tool_resources=mcp_tool.resources,
    )

    print(f"Created agent, ID: {Mcplearnagent.id}")

    return returntxt

def get_agent_by_name(name):
    """Client-side name lookup; returns first agent whose name matches exactly or None."""
    try:
        for ag in project_client.agents.list_agents():
            if getattr(ag, 'name', None) == name:
                return ag
    except Exception as ex:
        print(f"Error listing agents: {ex}")
    return None
    
def multi_agent(query: str) -> str:
    returntxt = ""

    base_agent_name = "baseagent"
    rfp_agent_name = "AISearchagent"
    mcp_agent_name = "Mcplearnagent"

    base_agent = get_agent_by_name(base_agent_name)
    if not base_agent:
        print("Base agent missing; creating now...")
        base_agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=base_agent_name,
            instructions="Generic base agent to answer general knowledge questions.",
        )
        print(f"Created base agent dynamically: {base_agent.id}")
    connected_agent_name = base_agent_name
    connected_agent = ConnectedAgentTool(
        id=base_agent.id, name=connected_agent_name, description="Gets the information from the base agent"
    )

    rfp_agent = get_agent_by_name(rfp_agent_name)
    rfp_agent = get_agent_by_name(rfp_agent_name)
    if not rfp_agent:
        print("RFP agent missing; please run create_agents() first or create manually.")
        return {"summary": "RFP agent missing", "token_usage": None, "status": "failed"}
    search_connected_agent_name = rfp_agent_name
    search_connected_agent = ConnectedAgentTool(
        id=rfp_agent.id, name=search_connected_agent_name, description="Gets the construction proposals from the RFP documents"
    )

    mcp_agent = get_agent_by_name(mcp_agent_name)
    mcp_agent = get_agent_by_name(mcp_agent_name)
    if not mcp_agent:
        print("MCP Learn agent missing; please run create_agents() first or create manually.")
        return {"summary": "MCP Learn agent missing", "token_usage": None, "status": "failed"}
    mcplearn_connected_agent_name = mcp_agent_name
    mcp_connected_agent = ConnectedAgentTool(
        id=mcp_agent.id, name=mcplearn_connected_agent_name, description="Gets the information from Microsoft Learn"
    )
    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="Existing_MultiAgent_Demo",
        instructions="""
        You are a helpful assistant, and use the connected agents to get stock prices, construction RFP Data, 
        Sustainability Paper.
        For basic general knowledge question use base agent but let the user know it's from base agent.
        For RFP related questions, use the RFP connected agent and provide citatons and sources.
        For Azure or general technical documentation questions, use the MCP connected agent.
        Summarize the output from the connected agents to answer the user's question.
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            connected_agent.definitions[0],
            search_connected_agent.definitions[0],
            mcp_connected_agent.definitions[0],
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
            #     if tool_call.name == "fetch_weather":
            #         output = fetch_weather("New York")
            #         tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
            # project_client.agents.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

    print(f"Run completed with status: {run.status}")
    # print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch run steps to get the details of the agent run
    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
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

    

    # Token usage (if provided by SDK)
    token_usage = None
    usage = getattr(run, "usage", None)
    if usage:
        token_usage = {k: getattr(usage, k) for k in ["prompt_tokens", "completion_tokens", "total_tokens"] if hasattr(usage, k)} or None

    # delete agent and thread
    # Cleanup
    
    try:
        print(" Clean up -------------------------------------")
        project_client.agents.delete_agent(agent.id)
        project_client.agents.threads.delete(thread.id)
    except Exception:
        pass

    return {"summary": returntxt, "token_usage": token_usage, "status": run.status}

def parse_and_display_json_multi(json_input):
    try:
        # Check if input is already a dictionary
        if isinstance(json_input, dict):
            data = json_input
        else:
            # Assume input is a JSON string and parse it
            data = json.loads(json_input)
        
        # Display Summary
        print("=== Construction Management Services Summary ===")
        summary_lines = data['summary'].split('\n')
        for line in summary_lines:
            if line.strip() and not line.startswith('Would you like'):
                print(line.strip())
        print()  # Add spacing
        
        # Display Token Usage
        print("=== Token Usage ===")
        token_usage = data['token_usage']
        print(f"Prompt Tokens: {token_usage['prompt_tokens']}")
        print(f"Completion Tokens: {token_usage['completion_tokens']}")
        print(f"Total Tokens: {token_usage['total_tokens']}")
        print()
        
        # Display Status
        print("=== Status ===")
        print(f"Run Status: {data['status'].capitalize()}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
    except TypeError as e:
        print(f"Type error: {e}")

def main():
    # print("---------------- Creating agents ------------------")
    # create_agents()
    # print("----------------- Creation complete ---------------")
    print()
    with tracer.start_as_current_span("Existing_MultiAgent_Demo-tracing"):

        print( "------------------------Executing Existing Agents-----------------")
        starttime = datetime.now()
        # query = "what is quantum computing"
        # query = "What is Azure AI Foundry Agents?"
        query = "Show me details on Construction management services experience we have done before"
        rs = multi_agent(query)
        print("Output from agents: ", parse_and_display_json_multi(rs))
        endtime = datetime.now()
        print(f"Connected agent example completed in {endtime - starttime} seconds")
        print( "------------------------Completing Existing Agents-----------------")
    


if __name__ == "__main__":
    main()