import asyncio
from datetime import datetime
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RedTeam,
    AzureOpenAIModelConfiguration,
    AttackStrategy,
    RiskCategory,
)
import os, json
import pandas as pd
from typing import Any, Callable, Set, Dict, List, Optional
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
from azure.ai.projects.models import (
    EvaluatorConfiguration,
    EvaluatorIds,
)
from azure.ai.projects.models import (
    Evaluation,
    InputDataset
)
from pathlib import Path
from opentelemetry import trace
# from config import get_logger
from azure.ai.evaluation.red_team import RedTeam, RiskCategory
from openai import AzureOpenAI
from user_logic_apps import AzureLogicAppTool, create_send_email_function
from azure.ai.agents.models import ListSortOrder
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool

from dotenv import load_dotenv

load_dotenv()

import logging
endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini
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
connection_string = project_client.telemetry.get_connection_string()

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def loginappagent(query: str) -> str:
    returntxt = ""
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    # Extract subscription and resource group from the project scope
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]

    # Logic App details
    logic_app_name = "agenttoolemail"
    trigger_name = "When_a_HTTP_request_is_received"

    # Create and initialize AzureLogicAppTool utility
    logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
    logic_app_tool.register_logic_app(logic_app_name, trigger_name)
    print(f"Registered logic app '{logic_app_name}' with trigger '{trigger_name}'.")

    # Create the specialized "send_email_via_logic_app" function for your agent tools
    send_email_func = create_send_email_function(logic_app_tool, logic_app_name)

    # Prepare the function tools for the agent
    functions_to_use: Set = {
        # fetch_current_datetime,
        send_email_func,  # This references the AzureLogicAppTool instance via closure
    }
    # [END register_logic_app]

    # Create an agent
    functions = FunctionTool(functions=functions_to_use)
    toolset = ToolSet()
    toolset.add(functions)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SendEmailAgent",
        instructions="You are a specialized agent for sending emails.",
        toolset=toolset,
    )
    # sendemail_connected_agent_name = "SendEmailagent"
    # sendemail_connected_agent = ConnectedAgentTool(
    #     id=Emailagent.id, name=sendemail_connected_agent_name, description="Get the content from other agents and send an email"
    # )
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
                print(f"    Function Name: {call.get('function', {}).get('name')}")
    
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.role == MessageRole.AGENT and message.url_citation_annotations:
            placeholder_annotations = {
                annotation.text: f" [see {annotation.url_citation.title}] ({annotation.url_citation.url})"
                for annotation in message.url_citation_annotations
            }
            for message_text in message.text_messages:
                message_str = message_text.text.value
                returntxt += message_str
                for k, v in placeholder_annotations.items():
                    message_str = message_str.replace(k, v)
                print(f"{message.role}: {message_str}")
        else:
            for message_text in message.text_messages:
                print(f"{message.role}: {message_text.text.value}")
                returntxt += message_text.text.value
    print()  # add an extra newline between steps
    # Delete the agent when done
    project_client.agents.threads.delete(thread.id)

    return returntxt

def existinglogicapp(query: str) -> str:
    returntxt = ""
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    # Extract subscription and resource group from the project scope
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]

    agent = project_client.agents.get_agent("asst_g3hRNabXnYHg3mzqBxvgDRG6")

    # thread = project_client.agents.threads.get("thread_wsqdVyYbze0HYBjs9oUNxJK7")
    print(f"Created agent, ID: {agent.id}")
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"{query}",
    )

    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id)

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    else:
        messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

        for message in messages:
            if message.text_messages:
                print(f"{message.role}: {message.text_messages[-1].text.value}")
                returntxt += message.text_messages[-1].text.value

if __name__ == "__main__":
    with tracer.start_as_current_span("Logicapp-tracing"):
        query = "Create a Strategy to build Quantum in space and email to Bala at babal@microsoft.com "
        # emailrs = loginappagent(query)
        emailrs = existinglogicapp(query)
        print(f"Email response: {emailrs}")
