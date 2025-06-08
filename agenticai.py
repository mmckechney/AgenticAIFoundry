import asyncio
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
from typing import Set, Callable, Any
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
from azure.ai.projects.models import (
    EvaluatorConfiguration,
    EvaluatorIds,
)
from azure.ai.projects.models import (
    Evaluation,
    InputDataset
)
from azure.ai.evaluation import AIAgentConverter, IntentResolutionEvaluator
from azure.ai.evaluation import (
    ToolCallAccuracyEvaluator,
    AzureOpenAIModelConfiguration,
    IntentResolutionEvaluator,
    TaskAdherenceEvaluator,
    ResponseCompletenessEvaluator
)
from pprint import pprint
# specific to agentic workflows
from azure.ai.evaluation import IntentResolutionEvaluator, TaskAdherenceEvaluator, ToolCallAccuracyEvaluator 
# other quality as well as risk and safety metrics
from azure.ai.evaluation import RelevanceEvaluator, CoherenceEvaluator, CodeVulnerabilityEvaluator, ContentSafetyEvaluator, IndirectAttackEvaluator, FluencyEvaluator
from azure.ai.projects.models import ConnectionType
from pathlib import Path
from opentelemetry import trace
# from config import get_logger
from azure.ai.evaluation.red_team import RedTeam, RiskCategory
from openai import AzureOpenAI
from azure.ai.evaluation import evaluate
from azure.ai.evaluation import GroundednessEvaluator, AzureOpenAIModelConfiguration

from dotenv import load_dotenv

load_dotenv()

import logging
# logging.basicConfig(level=logging.DEBUG)

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

def code_interpreter() -> str:
    code_interpreter = CodeInterpreterTool()
    with project_client:
        # Create an agent with the Bing Grounding tool
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
            name="codeint-agent",  # Name of the agent
            instructions="You are a helpful agent",  # Instructions for the agent
            tools=code_interpreter.definitions,  # Attach the tool
        )
        print(f"Created agent, ID: {agent.id}")

        # Create a thread for communication
        thread = project_client.agents.threads.create()
        print(f"Created thread, ID: {thread.id}")
        
        # Add a message to the thread
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",  # Role of the message sender
            content="What is the weather in Seattle today?",  # Message content
        )
        print(f"Created message, ID: {message['id']}")
        
        # Create and process an agent run
        run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")
        
        # Check if the run failed
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
        
        # Fetch and log all messages
        messages = project_client.agents.messages.list(thread_id=thread.id)
        for message in messages:
            print(f"Role: {message.role}, Content: {message.content}")
        
        # Delete the agent when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

def eval()-> str:
    returntxt = ""
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_KEY"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.environ.get("AZURE_API_VERSION"),
    )
    ## Using Azure AI Foundry Hub project
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }

    # Initializing Groundedness and Groundedness Pro evaluators
    groundedness_eval = GroundednessEvaluator(model_config)
    # instantiate an evaluator with image and multi-modal support
    safety_evaluator = ContentSafetyEvaluator(credential=DefaultAzureCredential(), azure_ai_project=azure_ai_project)

    result = evaluate(
        data="datarfp.jsonl", # provide your data here
        evaluators={
            "groundedness": groundedness_eval,
            "content_safety": safety_evaluator
        },
        # column mapping
        evaluator_config={
            "content_safety": {"query": "${data.query}", "response": "${data.response}"},
            "groundedness": {
                "column_mapping": {
                    "query": "${data.query}",
                    "context": "${data.context}",
                    "response": "${data.response}"
                } 
            }
        },
        # Optionally provide your Azure AI Foundry project information to track your evaluation results in your project portal
        # azure_ai_project = azure_ai_project,
        # Optionally provide an output path to dump a json of metric summary, row level data and metric and Azure AI project URL
        output_path="./myevalresults.json"
    )
    returntxt = f"Completed Evaluation: {result.studio_url}"    
    return returntxt

# A simple example application callback function that always returns a fixed response
def simple_callback(query: str) -> str:
    return "I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

# Function to process user input (simple echo bot for demonstration)
def process_message_reasoning(query: str) -> str:
    returntxt = ""
    excelsheetinfo = ""

    client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-12-01-preview",
    )

    system_prompt = (
        """You are a Red Team Agent AI assistant, 
        Format the output to be professional and easy to read — suitable for presentation to IT operations or service management leadership. """
    )

    txtmessages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
        ]
    model_name_reasoning = "o4-mini"
    # model_name_reasoning = "o3"

    response = client.chat.completions.create(
        model=model_name_reasoning,
        #reasoning={"effort": "high"},
        reasoning_effort="high",
        messages=txtmessages,
        # temperature=0.7,
        max_completion_tokens=4000
    )
    print("Response received from Azure OpenAI:", response)
    # returntxt = response.output_text.strip()
    returntxt = response.choices[0].message.content
    return f"{returntxt}"

# A simple example application callback function that always returns a fixed response
def aoai_callback(query: str) -> str:
    returntxt = ""
    excelsheetinfo = ""

    client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-12-01-preview",
    )
    system_prompt = (
        """You are a Red Team Agent AI assistant, Process the user query and provide a detailed response.
        """
    )
    txtmessages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
        ]
    model_name = "gpt-4.1"
    # model_name_reasoning = "o3"

    response = client.chat.completions.create(
        model=model_name,
        #reasoning={"effort": "high"},
        # reasoning_effort="high",
        messages=txtmessages,
        temperature=0.7,
        max_tokens=4000
    )
    print("Response received from Azure OpenAI:", response)
    # returntxt = response.output_text.strip()
    returntxt = response.choices[0].message.content
    return returntxt

async def redteam() -> str:
    returntxt = ""
                
    ## Using Azure AI Foundry Hub project
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }
    ## Using Azure AI Foundry project, example: AZURE_AI_PROJECT=https://your-account.services.ai.azure.com/api/projects/your-project
    azure_ai_project = os.environ.get("AZURE_AI_PROJECT")

    # Instantiate your AI Red Teaming Agent
    # red_team_agent = RedTeam(
    #     azure_ai_project=azure_ai_project, # required
    #     credential=DefaultAzureCredential() # required
    # )
    # Specifying risk categories and number of attack objectives per risk categories you want the AI Red Teaming Agent to cover
    red_team_agent = RedTeam(
        azure_ai_project=azure_ai_project, # required
        credential=DefaultAzureCredential(), # required
        risk_categories=[ # optional, defaults to all four risk categories
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm
        ], 
        num_objectives=5, # optional, defaults to 10
    )
    # Runs a red teaming scan on the simple callback target
    red_team_result = await red_team_agent.scan(target=simple_callback)

    returntxt += f"Red Team scan completed with status: {red_team_agent.ai_studio_url}\n"
        
    return returntxt

# Define some custom python function
def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # Here, we'll mock the response.
    mock_weather_data = {"Seattle": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json

def agent_eval() -> str:
    returntxt = ""
    user_functions: Set[Callable[..., Any]] = {
        fetch_weather,
    }

    # Adding Tools to be used by Agent 
    functions = FunctionTool(user_functions)

    toolset = ToolSet()
    toolset.add(functions)


    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    AGENT_NAME = "Agentic Eval Assistant"

    # Add Tools to be used by Agent
    functions = FunctionTool(user_functions)

    toolset = ToolSet()
    toolset.add(functions)

    # To enable tool calls executed automatically
    project_client.agents.enable_auto_function_calls(tools=toolset)
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name=AGENT_NAME,
        instructions="You are a helpful assistant",
        toolset=toolset,
    )

    print(f"Created agent, ID: {agent.id}")
    # https://github.com/Azure-Samples/azureai-samples/blob/main/scenarios/evaluate/Supported_Evaluation_Metrics/Agent_Evaluation/Evaluate_Azure_AI_Agent_Quality.ipynb
    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")
    # Create message to thread

    MESSAGE = "Can you email me weather info for Seattle ?"

    # Add a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",  # Role of the message sender
        content=MESSAGE,  # Message content
    )
    print(f"Created message, ID: {message['id']}")
    # Create and process an agent run
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")
    
    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    
    # Fetch and log all messages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        print(f"Role: {message.role}, Content: {message.content}")
    # Initialize the converter that will be backed by the project.
    converter = AIAgentConverter(project_client)

    thread_id = thread.id
    run_id = run.id
    file_name = "evaluation_input_data.jsonl"

    # Get a single agent run data
    evaluation_data_single_run = converter.convert(thread_id=thread_id, run_id=run_id)

    # Run this to save thread data to a JSONL file for evaluation
    # Save the agent thread data to a JSONL file
    # evaluation_data = converter.prepare_evaluation_data(thread_ids=thread_id, filename=<>)
    # print(json.dumps(evaluation_data, indent=4))
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_KEY"],
        api_version=os.environ["AZURE_API_VERSION"],
        azure_deployment=os.environ["MODEL_DEPLOYMENT_NAME"],
    )
    # Needed to use content safety evaluators
    azure_ai_project = {
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
        "project_name": os.environ["AZURE_PROJECT_NAME"],
        "resource_group_name": os.environ["AZURE_RESOURCE_GROUP"],
    }

    intent_resolution = IntentResolutionEvaluator(model_config=model_config)
    tool_call_accuracy = ToolCallAccuracyEvaluator(model_config=model_config)
    task_adherence = TaskAdherenceEvaluator(model_config=model_config)
    response_completeness_evaluator = ResponseCompletenessEvaluator(model_config=model_config)
    response = evaluate(
        data=file_name,
        evaluators={
            "tool_call_accuracy": tool_call_accuracy,
            "intent_resolution": intent_resolution,
            "task_adherence": task_adherence,
            "response_completeness": response_completeness_evaluator,
        },
        # azure_ai_project={
        #     "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
        #     "project_name": os.environ["AZURE_PROJECT_NAME"],
        #     "resource_group_name": os.environ["AZURE_RESOURCE_GROUP"],
        # },
    )
    pprint(f'AI Foundary URL: {response.get("studio_url")}')
    # average scores across all runs
    pprint(response["metrics"])

    # Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
    
    return returntxt

def main():
    with tracer.start_as_current_span("azureaifoundryagent-tracing"):
        print("Running code interpreter example...")
        #code_interpreter()
        
        print("Running evaluation example...")
        # eval()
        
        print("Running red teaming example...")
        # asyncio.run(redteam())
        
        print("Running agent evaluation example...")
        agent_eval()

if __name__ == "__main__":
    main()