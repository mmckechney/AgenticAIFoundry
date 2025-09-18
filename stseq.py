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

strvulnerabilities = """
    [
    {
        "vulnerability": "SQL Injection (SQLi)",
        "description": "Attackers insert malicious SQL code into input fields (e.g., login forms or search bars) to manipulate a database, potentially gaining unauthorized access, extracting sensitive data, or modifying database content.",
        "example": "An attacker enters '; DROP TABLE users; --' into a login form, causing the database to delete the users table if not properly sanitized.",
        "impact": "Data theft, unauthorized access, or data loss.",
        "mitigation": "Use parameterized queries, input validation, and prepared statements to sanitize user inputs."
    },
    {
        "vulnerability": "Cross-Site Scripting (XSS)",
        "description": "Attackers inject malicious scripts (e.g., JavaScript) into web pages viewed by users, allowing the script to execute in the victim's browser. This can steal session cookies, redirect users, or display fake content.",
        "example": "A malicious script '<script>alert('Hacked!');</script>' is embedded in a comment section of a website, executing when other users view the page.",
        "impact": "Session hijacking, credential theft, or malware distribution.",
        "mitigation": "Sanitize and escape user inputs, implement Content Security Policy (CSP), and use secure coding practices."
    },
    {
        "vulnerability": "Insecure Direct Object References (IDOR)",
        "description": "Attackers access unauthorized resources by manipulating input parameters (e.g., URLs or form fields) due to insufficient access controls.",
        "example": "Changing a URL parameter from 'user_id=123' to 'user_id=124' allows an attacker to view another user’s private data without proper authorization checks.",
        "impact": "Exposure of sensitive data, unauthorized account access, or data tampering.",
        "mitigation": "Implement proper access controls, validate user permissions, and use indirect references (e.g., tokens) instead of direct IDs."
    }
    ]
    """

def get_data_1():

    returntxt = ""

    

    returntxt = """{
        "message" : {strvulnerabilities}
    }
    """

    return returntxt

def get_data_2(strdata):

    returntxt = ""

    returntxt = """[build a pretty UI]
    {strdata}
    Thank you for the information
    """

    return returntxt

def multi_agent(query: str) -> str:

    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    devsecops_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="devsecopsagent",
        instructions="""Provide the security vulnerabilities information.
        Here is the data to use: {strvulnerabilities}
        """,
        #tools=... # tools to help the agent get stock prices
    )

    devsecops_agent_name = "devsecopsagent"
    devsecops_conn_agent = ConnectedAgentTool(
        id=devsecops_agent.id, name=devsecops_agent_name, description="Gets the information from the devsecops agent"
    )

    ui_generation_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="ui_generation_agent",
        instructions="""Build a visually appealing user interface to display security vulnerabilities. 
        Use the data provided by the DevSecOps agent as input and incorporate the necessary UI components to present the information effectively. 
        Include the header text '[build a pretty UI]' at the top and the footer text 'Thank you for the information' at the bottom.
        """,
        #tools=... # tools to help the agent get stock prices
    )

    ui_generation_agent_name = "ui_generation_agent"
    ui_generation_conn_agent = ConnectedAgentTool(
        id=ui_generation_agent.id, name=ui_generation_agent_name, description="Gets the information from the ui_generation_agent"
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="MultiAgent_Demo",
        instructions="""
        You are a helpful assistant, and use the connected agents to get stock prices, construction RFP Data, 
        Sustainability Paper.
        Dev sec ops agent: show vulnerabilities data from dataset.
        UI generation agent: generate a nice UI to show the data.

        Can you please get the UI generation agent output and include it in the final response?
        please respond output as JSON.
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            devsecops_conn_agent.definitions[0],
            ui_generation_conn_agent.definitions[0],
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
                                                        temperature=0.0)
    
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
    
     # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)    
    project_client.agents.threads.delete(thread.id)
    # print("Deleted agent")
    # Delete the connected Agent when done
    project_client.agents.delete_agent(devsecops_agent.id)
    project_client.agents.delete_agent(ui_generation_agent.id)

    # Token usage (if provided by SDK)
    token_usage = None
    usage = getattr(run, "usage", None)
    if usage:
        token_usage = {k: getattr(usage, k) for k in ["prompt_tokens", "completion_tokens", "total_tokens"] if hasattr(usage, k)} or None


    return {"summary": returntxt, "token_usage": token_usage, "status": run.status}


if __name__ == "__main__":
    query = "Show me vulnerabilities"

    print("Calling existing agent example...")
    starttime = datetime.now()
    # exsitingagentrs = load_existing_agent("Show me details on Construction management services experience we have done before and email Bala at babal@microsoft.com with subject as construction manager")
    exsitingagentrs = multi_agent(query=query)
    print()
    print("Final output ===========================================")
    print(exsitingagentrs.get('summary', "N/A"))
    print()
    print("Token information: ", exsitingagentrs.get("token_usage", "N/A"))
    print()
    print("Status information: ", exsitingagentrs.get("status", "N/A"))
    endtime = datetime.now()
    print(f"Delete agent example completed in {endtime - starttime} seconds")
    print(" ------------------ Completed ----------------------------")