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
# specific to agentic workflows
from azure.ai.evaluation import IntentResolutionEvaluator, TaskAdherenceEvaluator, ToolCallAccuracyEvaluator 
# other quality as well as risk and safety metrics
from azure.ai.evaluation import RelevanceEvaluator, CoherenceEvaluator, CodeVulnerabilityEvaluator, ContentSafetyEvaluator, IndirectAttackEvaluator, FluencyEvaluator
from azure.ai.projects.models import ConnectionType
from pathlib import Path
from opentelemetry import trace
# from config import get_logger

from dotenv import load_dotenv

load_dotenv()

import logging
logging.basicConfig(level=logging.DEBUG)

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

    # Upload a local jsonl file (skip if you already have a Dataset registered)
    # data_id = project_client.datasets.upload_file(
    #     name="evaluate_test_data",
    #     version=1,
    #     file_path="datarfp.jsonl",
    # ).id
    # Built-in evaluator configurations
    evaluators = {
        "relevance": EvaluatorConfiguration(
            id=EvaluatorIds.RELEVANCE.value,
            init_params={"deployment_name": model_deployment_name},
            data_mapping={
                "query": "${data.query}",
                "response": "${data.response}",
            },
        ),
        "violence": EvaluatorConfiguration(
            id=EvaluatorIds.VIOLENCE.value,
            init_params={"azure_ai_project": endpoint},
        ),
        "bleu_score": EvaluatorConfiguration(
            id=EvaluatorIds.BLEU_SCORE.value,
        ),
    }
    # Create an evaluation with the dataset and evaluators specified
    evaluation = Evaluation(
        display_name="Cloud evaluation",
        description="Evaluation of dataset",
        #data=InputDataset(id=data_id),
        data="datarfp.jsonl",
        evaluators=evaluators,
    )

    # Run the evaluation 
    evaluation_response = project_client.evaluations.create(
        evaluation,
        headers={
            "model-endpoint": model_endpoint,
            "api-key": model_api_key,
        },
    )

    print("Created evaluation:", evaluation_response.name)
    print("Status:", evaluation_response.status)

    
    return returntxt

def redteam() -> str:
    returntxt = ""

    with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    ) as project_client:
                
        # Create target configuration for testing an Azure OpenAI model
        target_config = AzureOpenAIModelConfiguration(model_deployment_name="gpt-4o")

        # Instantiate the AI Red Teaming Agent
        red_team_agent = RedTeam(
            attack_strategies=[AttackStrategy.BASE64],
            risk_categories=[RiskCategory.VIOLENCE],
            display_name="red-team-cloud-run", 
            target=target_config,
        )
        
        # Create and run the red teaming scan
        red_team_response = project_client.red_teams.create(red_team=red_team_agent, headers={"model-endpoint": model_endpoint, "api-key": model_api_key,})
        # Use the name returned by the create operation for the get call
        get_red_team_response = project_client.red_teams.get(name=red_team_response.name)
        print(f"Red Team scan status: {get_red_team_response.status}")
        for scan in project_client.red_teams.list():
            print(f"Found scan: {scan.name}, Status: {scan.status}")

        returntxt += f"Red Team scan status: {get_red_team_response.status}\n"
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


    # Create the agent
    AGENT_NAME = "Foundry Agent Eval Assistant"

    #project_client = AIProjectClient.from_connection_string(
    #    credential=DefaultAzureCredential(),
    #    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    #)

    with project_client:
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=AGENT_NAME,
            instructions="You are a helpful assistant",
            toolset=toolset,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = project_client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        # Create message to thread
        MESSAGE = "Can you fetch me the weather in Seattle?"

        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=MESSAGE,
        )
        print(f"Created message, ID: {message.id}")

        run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)

        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        print(f"Run ID: {run.id}")

        # display messages
        for message in project_client.agents.list_messages(thread.id, order="asc").data:
            print(f"Role: {message.role}")
            print(f"Content: {message.content[0].text.value}")
            print("-" * 40)
        
        # Initialize the converter for Azure AI agents
        converter = AIAgentConverter(project_client)

        # Specify the thread and run id
        thread_id = thread.id
        run_id = run.id

        converted_data = converter.convert(thread_id, run_id)
        model_config = project_client.connections.get_default(
                                                connection_type=ConnectionType.AZURE_OPEN_AI,
                                                include_credentials=True) \
                                            .to_evaluator_model_config(
                                                deployment_name="o4-mini",
                                                api_version="2023-05-15",
                                                include_credentials=True
                                            )

        quality_evaluators = {evaluator.__name__: evaluator(model_config=model_config) for evaluator in [IntentResolutionEvaluator, TaskAdherenceEvaluator, ToolCallAccuracyEvaluator, CoherenceEvaluator, FluencyEvaluator, RelevanceEvaluator]}


        ## Using Azure AI Foundry Hub
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        ## Using Azure AI Foundry Development Platform, example: AZURE_AI_PROJECT=https://your-account.services.ai.azure.com/api/projects/your-project
        azure_ai_project = os.environ.get("AZURE_AI_PROJECT")

        safety_evaluators = {evaluator.__name__: evaluator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential()) for evaluator in[ContentSafetyEvaluator, IndirectAttackEvaluator, CodeVulnerabilityEvaluator]}

        # reference the quality and safety evaluator list above
        quality_and_safety_evaluators = {**quality_evaluators, **safety_evaluators}

        for name, evaluator in quality_and_safety_evaluators.items():
            try:
                result = evaluator(**converted_data)
                print(name)
                print(json.dumps(result, indent=4)) 
            except:
                print("Note: if there is no tool call to evaluate in the run history, ToolCallAccuracyEvaluator will raise an error")
                pass
    
    return returntxt

def main():
    with tracer.start_as_current_span("azureaifoundryagent-tracing"):
        print("Running code interpreter example...")
        code_interpreter()
        
        print("Running evaluation example...")
        # eval()
        
        print("Running red teaming example...")
        # redteam()
        
        print("Running agent evaluation example...")
        # agent_eval()

if __name__ == "__main__":
    main()