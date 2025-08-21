import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureFunctionStorageQueue, AzureFunctionTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from dotenv import load_dotenv
import sys
from typing import Optional

load_dotenv()

# Retrieve the storage service endpoint from environment variables (fix typo and validate)
storage_service_endpoint = (
    os.getenv("STORAGE_SERVICE_ENDPOINT")
    or os.getenv("STORAGE_SERVICE_ENDPONT")  # fallback to legacy typo if present
)

if not storage_service_endpoint:
    print(
        "Missing STORAGE_SERVICE_ENDPOINT. Set it to your Queue service endpoint, e.g.: https://<account>.queue.core.windows.net",
        file=sys.stderr,
    )
    sys.exit(1)

if not storage_service_endpoint.startswith("https://") or ".queue.core.windows.net" not in storage_service_endpoint:
    print(
        f"STORAGE_SERVICE_ENDPOINT looks invalid: {storage_service_endpoint}. Expected like https://<account>.queue.core.windows.net",
        file=sys.stderr,
    )
    sys.exit(1)


def _extract_text_from_message(msg) -> str:
    """Extract text content from an agents message item safely."""
    try:
        content_list = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
        if not content_list:
            return ""
        # content is typically a list of blocks like { 'type': 'text', 'text': { 'value': '...', 'annotations': [] } }
        for block in content_list:
            if isinstance(block, dict) and block.get("type") == "text":
                text_obj = block.get("text")
                if isinstance(text_obj, dict):
                    return str(text_obj.get("value", ""))
                # sometimes SDK may flatten
                if isinstance(text_obj, str):
                    return text_obj
        return ""
    except Exception:
        return ""



def azurefunc_test(query: str) -> str:
    returntxt = ""

    # Define the Azure Function tool
    azure_function_tool = AzureFunctionTool(
        name="foo",  # Name of the tool
        description="Get answers from the foo bot.",  # Description of the tool's purpose
        parameters={  # Define the parameters required by the tool
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to ask."},
                "outputqueueuri": {"type": "string", "description": "The full output queue URI."},
            },
        },
        input_queue=AzureFunctionStorageQueue(  # Input queue configuration
            queue_name="azure-function-foo-input",
            storage_service_endpoint=storage_service_endpoint,
        ),
        output_queue=AzureFunctionStorageQueue(  # Output queue configuration
            queue_name="azure-function-foo-output",
            storage_service_endpoint=storage_service_endpoint,
        ),
    )

    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT_ENT"],
        credential=DefaultAzureCredential()
    )
    # Create an agent with the Azure Function tool
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="azure-function-agent-foo",  # Name of the agent
        instructions=(
            "You are a helpful support agent. Use the provided function any time the prompt contains the string "
            "'What would foo say?'. When you invoke the function, ALWAYS specify the output queue URI parameter as "
            f"'{storage_service_endpoint}/azure-function-tool-output'. Always respond with \"Foo says\" and then the response from the tool."
        ),
        tools=azure_function_tool.definitions,  # Attach the tool definitions to the agent
    )
    print(f"Created agent, agent ID: {agent.id}")
    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message in the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=query,  
    )
    print(f"Created message, message ID: {message['id']}")

    # Create and process a run for the agent to handle the message
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Retrieve and print all messages from the thread
    messages_paged = project_client.agents.messages.list(thread_id=thread.id)
    last_assistant_text: Optional[str] = None
    last_assistant_msg = None
    for msg in messages_paged:
        role_obj = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        # role may be a string ("assistant") or an Enum (MessageRole.ASSISTANT)
        role_val = getattr(role_obj, "value", None) if role_obj is not None else None
        if role_val is None:
            role_val = role_obj if isinstance(role_obj, str) else str(role_obj)
        role_lower = role_val.lower() if isinstance(role_val, str) else ""

        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
        print(f"Role: {role_val}, Content: {content}")
        returntxt += f"Role: {role_val}, Content: {content}\n"

        # Accept both 'assistant' and 'agent' to be safe across SDKs
        if role_lower in ("assistant", "agent"):
            txt = _extract_text_from_message(msg)
            if txt:
                last_assistant_text = txt
                last_assistant_msg = msg

    if last_assistant_text:
        print("\n=== Assistant response ===\n" + last_assistant_text + "\n==========================\n")
        returntxt = last_assistant_text
    else:
        print("No assistant text message found in thread.")

    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print(f"Deleted agent")

    return returntxt

def connected_azure_function_agent(query: str) -> str:
    # Here you would implement the logic to connect to the Azure Function
    # and pass the query to it, then return the response.
    returntxt = ""

    # Define the Azure Function tool
    azure_function_tool = AzureFunctionTool(
        name="foo",  # Name of the tool
        description="Get answers from the foo bot.",  # Description of the tool's purpose
        parameters={  # Define the parameters required by the tool
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to ask."},
                "outputqueueuri": {"type": "string", "description": "The full output queue URI."},
            },
        },
        input_queue=AzureFunctionStorageQueue(  # Input queue configuration
            queue_name="azure-function-foo-input",
            storage_service_endpoint=storage_service_endpoint,
        ),
        output_queue=AzureFunctionStorageQueue(  # Output queue configuration
            queue_name="azure-function-foo-output",
            storage_service_endpoint=storage_service_endpoint,
        ),
    )

    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT_ENT"],
        credential=DefaultAzureCredential()
    )
    # Create an agent with the Azure Function tool
    azfuncagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="azure-function-agent-foo",  # Name of the agent
        instructions=(
            "You are a helpful support agent. Use the provided function any time the prompt contains the string "
            "'What would foo say?'. When you invoke the function, ALWAYS specify the output queue URI parameter as "
            f"'{storage_service_endpoint}/azure-function-tool-output'. Always respond with \"Foo says\" and then the response from the tool."
        ),
        tools=azure_function_tool.definitions,  # Attach the tool definitions to the agent
    )
    print(f"Created agent, agent ID: {azfuncagent.id}")

    azfunc_connected_agent_name = "AzureFunctionAgentFoo"
    azfunc_connected_agent_name = ConnectedAgentTool(
        id=azfuncagent.id, name=azfunc_connected_agent_name, description="Get the stock from Azure Functions."
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="AzfuncConnectedAgent",
        instructions="""
        You are a helpful assistant, and use the connected agents to get stock prices using Azure functions.
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            azfunc_connected_agent_name.definitions[0],
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
    project_client.agents.delete_agent(azfuncagent.id)

    return returntxt

if __name__ == "__main__":
    query = "what would foo say about What is the Today's weather in Ney York City, confirmed city is New York City."
    response = azurefunc_test(query)
    # response = connected_azure_function_agent(query)
    print(f"Response: {response}")  