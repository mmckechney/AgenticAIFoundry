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

# imgfile = "img/layout-2.jpg"
imgfile = "img/csifactoryengdraw1.jpg"

st.set_page_config(page_title="AI Agents with Azure AI Foundry", page_icon=imgfile, layout="wide")

async def process_img_agent(query: str) -> str:
    returntxt = ""

        
    # Authenticate using DefaultAzureCredential (supports managed identity, CLI login, etc.)
    credential = DefaultAzureCredential()

    
    # Create AI Project client
    client = AIProjectClient(endpoint=endpoint, credential=credential)

    # Read image and upload to agent files
    # image_path = "img/layout-2.jpg"
    image_path = "img/csifactoryengdraw1.jpg"
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()


      
    # Create the agents client
    agents_client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Prepare multimodal content for the agent (text + uploaded image reference)
    # Upload the local image file
    image_file = await agents_client.files.upload_and_poll(file_path=imgfile, purpose="assistants")

    # Construct content using uploaded image
    file_param = MessageImageFileParam(file_id=image_file.id, detail="high")
    content_blocks = [
        MessageInputTextBlock(text=f"{query}"),
        MessageInputImageFileBlock(image_file=file_param),
    ]

    # Create a agent
    agent = await agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="ImageAnalysisAgent",
        instructions="You are a civil/mechanical engineering agent, Analyze this image for user query and provide detailed insights",
    )

    print(f"Created agent, ID: {agent.id}")
    thread = await agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = await agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=content_blocks,
    )
    print(f"Created message, ID: {message.id}")
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

    print(" Clean up -------------------------------------")
    agents_client.delete_agent(agent.id)
    agents_client.threads.delete(thread.id)
    
    try:
        print(" Clean up -------------------------------------")
        agents_client.delete_agent(agent.id)
        agents_client.threads.delete(thread.id)
    except Exception:
        pass

    return {"summary": returntxt, "token_usage": token_usage, "status": run.status}

def main():

    st.set_page_config(
        page_title="Civil Engineering Agents",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Engineering Drawings")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # if prompt := st.chat_input(""):
    #     st.session_state.messages.append({"role": "user", "content": prompt})
    #     st.chat_message("user").markdown(prompt)
    #     query = "can you extract how many bathrooms are there and their square footage for tiles?"
    #     rs = asyncio.run(process_img_agent(query=prompt))
    #     print(rs["summary"])
    #     print(rs["token_usage"])
    #     st.session_state.messages.append({"role": "assistant", "content": rs["summary"]})
    #     st.session_state.messages.append({"role": "assistant", "content": rs["token_usage"]})


    with st.container(height=500):
        # st.markdown("Content")
        # st.markdown(st.session_state.messages)
        # st.rerun()
        if prompt := st.chat_input(""):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)
            query = "can you extract how many bathrooms are there and their square footage for tiles?"
            rs = asyncio.run(process_img_agent(query=prompt))
            print(rs["summary"])
            print(rs["token_usage"])
            st.session_state.messages.append({"role": "assistant", "content": rs["summary"]})
            st.session_state.messages.append({"role": "assistant", "content": rs["token_usage"]})
            st.markdown(rs["summary"])
            st.markdown(rs["token_usage"])

    # query = "can you extract how many bathrooms are there and their square footage for tiles?"
    # rs = asyncio.run(process_img_agent(query=query))
    # print(rs["summary"])
    # print(rs["token_usage"])

if __name__ == "__main__":
    main()