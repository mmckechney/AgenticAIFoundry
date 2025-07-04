import tempfile
import uuid
from openai import AzureOpenAI
import streamlit as st
import asyncio
import io
import os
import time
import json
import soundfile as sf
import numpy as np
from datetime import datetime
from typing import Any, Callable, Set, Dict, List, Optional
from scipy.signal import resample
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import FunctionTool


from dotenv import load_dotenv

from agentutils.user_functions_with_traces import fetch_weather

# Load environment variables
load_dotenv()

# Azure OpenAI configuration (replace with your credentials)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
WHISPER_DEPLOYMENT_NAME = "whisper"
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
project_endpoint = os.environ["PROJECT_ENDPOINT"]
# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)


from azure.monitor.opentelemetry import configure_azure_monitor
connection_string = project_client.telemetry.get_connection_string()

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def fetch_insurance(firstname: str, lastname: str, dob: str, company: str, age: int, preexisting_conditions: str) -> str:
    """
    Fetches the insurance information for the specified user.

    :param firstname: The first name of the user.
    :param lastname: The last name of the user.
    :param dob: The date of birth of the user.
    :param company: The name of the insurance company.
    :param age: The age of the user.
    :param preexisting_conditions: A list of pre-existing conditions the user has.
    :return: Insurance information as a JSON string.
    """
    returntxt = ""
    # Mock insurance data for demonstration purposes
    # Get the data from parameter passed to the function
    if not firstname or not lastname or not dob or not company or age is None or not preexisting_conditions:
        return json.dumps({"error": "Missing required information. Please provide all details."})

    user_info = {
        "firstname": firstname,
        "lastname": lastname,
        "dob": dob,
        "company": company,
        "age": age,
        "preexisting_conditions": preexisting_conditions
    }

    if user_info.age < 18:
        returntxt = "Cost is $400 per month for minors."
    elif user_info.age < 30:
        returntxt = "Cost is $600 per month for young adults."
    elif user_info.age < 50:
        returntxt = "Cost is $800 per month for adults."
    else:
        returntxt = "Cost is $1000 per month for seniors."

    return returntxt


def connected_agent(query: str) -> str:
    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    insurance_price_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="insurancepricebot",
        instructions="""Your job is to get the insurance price of a company. 
        please ask the user for First Name, Last Name, Date of Birth, and Company Name.
        Also ask for age and preexisting conditions.
        Only process the request if the user provides all the information.
        If the user does not provide all the information, ask them to provide the missing information.
        If you don't know the realtime insurance price, return the last known insurance price.""",
        #tools=... # tools to help the agent get insurance prices
        temperature=0.7,
    )
    insurance_agent_name = "insurancepricebot"
    insurance_agent = ConnectedAgentTool(
        id=insurance_price_agent.id, name=insurance_agent_name, description="Create a insurance quote for the user"
    )

    sendemail_connected_agent = project_client.agents.get_agent("asst_g3hRNabXnYHg3mzqBxvgDRG6")
    sendemail_connected_agent_name = "sendemail"
    sendemail_connected_agent = ConnectedAgentTool(
        id=sendemail_connected_agent.id, name=sendemail_connected_agent_name, description="Get the quote and Sends an email to the user"
    )

    # Define user functions
    user_functions = {fetch_insurance}
    # Initialize the FunctionTool with user-defined functions
    functions = FunctionTool(functions=user_functions)

    # File search agent
    # Define the path to the file to be uploaded
    file_path = "./data/insurancetc.pdf"

    # Upload the file
    file = project_client.agents.files.upload_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create a vector store with the uploaded file
    vector_store = project_client.agents.vector_stores.create_and_poll(file_ids=[file.id], name="insurance_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")
    # Create a file search tool
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    # Create an agent with the file search tool
    insdocagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="insdocagent",  # Name of the agent
        instructions="You are a Insurance Process agent and can search information from uploaded files",  # Instructions for the agent
        tools=file_search.definitions,  # Tools available to the agent
        tool_resources=file_search.resources,  # Resources for the tools
    )
    # print(f"Created agent, ID: {agent.id}")
    insdocconnectedagentname = "insdocagent"
    insdoc_connected_agent = ConnectedAgentTool(
        id=insdocagent.id, name=insdocconnectedagentname, description="Summarize the content of the uploaded files and format it for email."
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="InsuranceQuoteAssistant",
        instructions="""
        You are an insurance quote assistant. Your job is to:
        1. Use the insurance quote agent: insurancepricebot to generate an insurance quote for the user, using all provided information.
        2. After generating the quote, use the insdocagent and get the summarized process like terms and conditions, append to quote and 
        ALWAYS use the email agent to send the quote to the user's email address.
        3. Return your response in the following format:
        [QUOTE]\n<insurance quote here>\n[EMAIL OUTPUT]\n<email agent output here>
        Do not skip the email step. If any required information is missing, ask the user for it. If all information is present, always send the quote by email and return both outputs as above.
        """,
        tools=[
            insurance_agent.definitions[0],
            insdoc_connected_agent.definitions[0],
            sendemail_connected_agent.definitions[0],
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

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)    
    project_client.agents.threads.delete(thread.id)
    # print("Deleted agent")
    # Delete the connected Agent when done
    project_client.agents.delete_agent(insurance_price_agent.id)
    # project_client.agents.delete_agent(insdoc_connected_agent.id)
    project_client.agents.vector_stores.delete(vector_store.id)

    return returntxt

def insurance_chat_ui():
    st.set_page_config(
        page_title="Insurance Quote Assistant",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a scrollable container for chat history
    chat_container = st.container(height=600)
    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Generate assistant response
        response = connected_agent(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Add a clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

def main():
    with tracer.start_as_current_span("InsurnaceAgent-tracing"):
        insurance_chat_ui()

if __name__ == "__main__":
    main()