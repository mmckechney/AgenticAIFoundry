# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with custom functions from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_functions.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import json
import os, time, sys
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    ListSortOrder,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
)
from typing import Any, Callable, Set, Dict, List, Optional

current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from utils import send_email


project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
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


def sendemailagent():

    functions_to_use: Set = {
        # fetch_current_datetime,
        send_email,  # This references the AzureLogicAppTool instance via closure
    }
    # Initialize function tool with user functions
    functions = FunctionTool(functions=functions_to_use)

    with project_client:
        agents_client = project_client.agents

        # Create an agent and run user's request with function calls
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="Email-agent",
            instructions="You are a helpful agent",
            tools=functions.definitions,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, send an email with the datetime and weather information in New York to bala at babal@microsoft.com with subject as current news. Don't ask for followup questions.",
        )
        print(f"Created message, ID: {message.id}")

        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
        print(f"Created run, ID: {run.id}")

        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

            # if run.status == "requires_action":
            #     print("Run requires action — breaking and closing")
            #     # Optionally cancel the run before breaking
            #     agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
            #     break
            
            # break
            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredFunctionToolCall):
                        try:
                            print(f"Executing tool call: {tool_call}")
                            tool_call_id = tool_call.id
                            function_name = tool_call.function.name
                            print(f"Function name: {function_name}, Tool call ID: {tool_call_id}")
                            arguments = tool_call.function.arguments  # usually a JSON str
                            # Convert arguments to a dictionary
                            args = json.loads(arguments)
                            print(f"Arguments for function {function_name}: {args}")
                            output = functions.execute(tool_call)
                            tool_outputs.append(
                                ToolOutput(
                                    tool_call_id=tool_call.id,
                                    output=output,
                                )
                            )
                            break
                        except Exception as e:
                            print(f"Error executing tool_call {tool_call.id}: {e}")
                break
                # print(f"Tool outputs: {tool_outputs}")
                # if tool_outputs:
                #     agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

            print(f"Current run status: {run.status}")

        print(f"Run completed with status: {run.status}")

        # Delete the agent when done
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        # for msg in messages:
        #     if msg.text_messages:
        #         last_text = msg.text_messages
        #         print(f"{msg.role}: {last_text.text.value}")

if __name__ == "__main__":
    with tracer.start_as_current_span("EmailAgent-tracing"):
        sendemailagent()
        #send_email("babal@microsoft.com", "Test Email", "This is a test email sent from the Azure AI Foundry project.")
        print("Email sent successfully.")