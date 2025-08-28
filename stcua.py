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
from typing import Optional, Dict, Any, List
from scipy.signal import resample
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration (replace with your credentials)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

def cuarun(query: str) -> str:
    cuaclient = AzureOpenAI(  
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
        api_key= os.getenv("AZURE_OPENAI_KEY"),
        api_version="preview"
        )

    response = cuaclient.responses.create(
        model="computer-use-preview", # set this to your model deployment name
        tools=[{
            "type": "computer_use_preview",
            "display_width": 1024,
            "display_height": 768,
            "environment": "windows" # other possible values: "mac", "windows", "ubuntu", "browser"
        }],
        input=[
            {
                "role": "user",
                "content": "Can you open microsoft word."
            }
        ],
        truncation="auto",
        max_output_tokens= 1500,
        # instructions="Generate a response using the MCP API tool.",
    )
    # returntxt = response.choices[0].message.content.strip()
    # retturntxt = response.output_text
    # print(f"Response: {retturntxt}")
    print('Output:', response.output)
    ## response.output is the previous response from the model
    computer_calls = [item for item in response.output if item.type == "computer_call"]
    if not computer_calls:
        print("No computer call found. Output from model:")
        for item in response.output:
            print(item)

    computer_call = computer_calls[0]
    last_call_id = computer_call.call_id
    action = computer_call.action

    print(f"Last call ID: {last_call_id}")
    print(f"Action: {action}")

    # Your application would now perform the action suggested by the model
    # And create a screenshot of the updated state of the environment before sending another response

    # response_2 = cuaclient.responses.create(
    #     model="computer-use-preview",
    #     previous_response_id=response.id,
    #     tools=[{
    #         "type": "computer_use_preview",
    #         "display_width": 1024,
    #         "display_height": 768,
    #         "environment": "browser" # other possible values: "mac", "windows", "ubuntu"
    #     }],
    #     input=[
    #         {
    #             "call_id": last_call_id,
    #             "type": "computer_call_output",
    #             "output": {
    #                 "type": "input_image",
    #                 # Image should be in base64
    #                 "image_url": f"data:image/png;base64,{<base64_string>}"
    #             }
    #         }
    #     ],
    #     truncation="auto"
    # )

if __name__ == "__main__":
    # query = "Check the latest AI news on bing.com."
    query = "Summarize the content from https://www.gethalfbaked.com/p/startup-ideas-425-cognitive-fitness"
    cuarun(query)
    # You can also use asyncio.run(cuarun(query)) if you want to run it in an async context