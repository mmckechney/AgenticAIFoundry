import asyncio
from datetime import datetime
import time
import os, json
import pandas as pd
from typing import Any, Callable, Set, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval
import streamlit as st
from dotenv import load_dotenv
import tempfile
import uuid
import requests
import io
import re

load_dotenv()

import logging

endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
# model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini
WHISPER_DEPLOYMENT_NAME = "whisper"
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

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
connection_string = project_client.telemetry.get_application_insights_connection_string()

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection


from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def ft_status():

    # https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/fine-tuning?context=%2Fazure%2Fai-foundry%2Fcontext%2Fcontext&tabs=azure-openai&pivots=programming-language-python
    runid = "ftjob-316ef9689e4049b9b61d98bcca98ec49"
    result = client.fine_tuning.jobs.retrieve(runid)
    print(result)
    response = client.fine_tuning.jobs.list_events(fine_tuning_job_id=runid, limit=10)
    print(response.model_dump_json(indent=2))
    response = client.fine_tuning.jobs.checkpoints.list(runid)
    print(response.model_dump_json(indent=2))
    # Retrieve the file ID of the first result file from the fine-tuning job
    # for the customized model.
    response = client.fine_tuning.jobs.retrieve(runid)
    if response.status == 'succeeded':
        result_file_id = response.result_files[0]

    retrieve = client.files.retrieve(result_file_id)

    # Download the result file.
    print(f'Downloading result file: {result_file_id}')

    with open(retrieve.filename, "wb") as file:
        result = client.files.content(result_file_id).read()
        file.write(result)

if __name__ == "__main__":
    ft_status()