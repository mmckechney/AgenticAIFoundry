import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureFunctionStorageQueue, AzureFunctionTool
from dotenv import load_dotenv

load_dotenv()

# Retrieve the storage service endpoint from environment variables
storage_service_endpoint = os.environ["STORAGE_SERVICE_ENDPONT"]



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
        content="What is the most prevalent element in the universe? What would foo say?",  
    )
    print(f"Created message, message ID: {message['id']}")

    # Create and process a run for the agent to handle the message
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Retrieve and print all messages from the thread
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for msg in messages:
        print(f"Role: {msg['role']}, Content: {msg['content']}")# Get messages from the assistant thread

    # Get the last message from the assistant
    last_msg = messages.get_last_text_message_by_sender("assistant")
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print(f"Deleted agent")

    return returntxt

if __name__ == "__main__":
    query = "What is the weather in Ney York City"
    response = azurefunc_test(query)
    print(f"Response: {response}")  