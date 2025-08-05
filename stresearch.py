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
from azure.ai.agents.models import DeepResearchTool, MessageRole, ThreadMessage
from azure.ai.agents import AgentsClient


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
project_endpoint = os.environ["PROJECT_ENDPOINT_WEST"]
# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)


from azure.monitor.opentelemetry import configure_azure_monitor
connection_string = project_client.telemetry.get_application_insights_connection_string()

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def fetch_and_print_new_agent_response(
    thread_id: str,
    agents_client: AgentsClient,
    last_message_id: Optional[str] = None,
) -> Optional[str]:
    response = agents_client.messages.get_last_message_by_role(
        thread_id=thread_id,
        role=MessageRole.AGENT,
    )
    if not response or response.id == last_message_id:
        return last_message_id  # No new content

    print("\nAgent response:")
    print("\n".join(t.text.value for t in response.text_messages))

    for ann in response.url_citation_annotations:
        print(f"URL Citation: [{ann.url_citation.title}]({ann.url_citation.url})")

    return response.id


def create_research_summary(
        message : ThreadMessage,
        filepath: str = "research_summary.md"
) -> None:
    if not message:
        print("No message content provided, cannot create research summary.")
        return

    with open(filepath, "w", encoding="utf-8") as fp:
        # Write text summary
        text_summary = "\n\n".join([t.text.value.strip() for t in message.text_messages])
        fp.write(text_summary)

        # Write unique URL citations, if present
        if message.url_citation_annotations:
            fp.write("\n\n## References\n")
            seen_urls = set()
            for ann in message.url_citation_annotations:
                url = ann.url_citation.url
                title = ann.url_citation.title or url
                if url not in seen_urls:
                    fp.write(f"- [{title}]({url})\n")
                    seen_urls.add(url)

    print(f"Research summary written to '{filepath}'.")

def research_agent(query: str) -> str:
    """
    Research tool that performs a web search and returns the results.
    """
    returntxt = ""
    with tracer.start_as_current_span("research_tool"):
        # Simulate a web search
        time.sleep(2)  # Simulate network delay
        return f"Research results for query: {query}"
        project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT_WEST"],
            credential=DefaultAzureCredential(),
        )

        conn_id = project_client.connections.get(name=os.environ["BING_RESOURCE_NAME"]).id


        # Initialize a Deep Research tool with Bing Connection ID and Deep Research model deployment name
        deep_research_tool = DeepResearchTool(
            bing_grounding_connection_id=conn_id,
            deep_research_model=os.environ["DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME"],
        )

        # Create Agent with the Deep Research tool and process Agent run
        with project_client:

            with project_client.agents as agents_client:

                # Create a new agent that has the Deep Research tool attached.
                # NOTE: To add Deep Research to an existing agent, fetch it with `get_agent(agent_id)` and then,
                # update the agent with the Deep Research tool.
                agent = agents_client.create_agent(
                    model=os.environ["MODEL_DEPLOYMENT_NAME"],
                    name="research-agent",
                    instructions="You are a helpful Agent that assists in researching scientific topics.",
                    tools=deep_research_tool.definitions,
                )

                # [END create_agent_with_deep_research_tool]
                print(f"Created agent, ID: {agent.id}")

                # Create thread for communication
                thread = agents_client.threads.create()
                print(f"Created thread, ID: {thread.id}")

                # Create message to thread
                message = agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=query
                )
                print(f"Created message, ID: {message.id}")

                print(f"Start processing the message... this may take a few minutes to finish. Be patient!")
                # Poll the run as long as run status is queued or in progress
                run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
                last_message_id = None
                while run.status in ("queued", "in_progress"):
                    time.sleep(1)
                    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                    last_message_id = fetch_and_print_new_agent_response(
                        thread_id=thread.id,
                        agents_client=agents_client,
                        last_message_id=last_message_id,
                    )
                    print(f"Run status: {run.status}")

                print(f"Run finished with status: {run.status}, ID: {run.id}")

                if run.status == "failed":
                    print(f"Run failed: {run.last_error}")

                # Fetch the final message from the agent in the thread and create a research summary
                final_message = agents_client.messages.get_last_message_by_role(
                    thread_id=thread.id, role=MessageRole.AGENT
                )
                if final_message:
                    create_research_summary(final_message)

                # Clean-up and delete the agent once the run is finished.
                # NOTE: Comment out this line if you plan to reuse the agent later.
                agents_client.delete_agent(agent.id)
                print("Deleted agent")

    return returntxt

def research_main():
    
    query = "What is the latest research on quantum computing?"
    resds = research_agent(query)
    print(resds)

if __name__ == "__main__":
    research_main()