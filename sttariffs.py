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
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import FilePurpose, FileSearchTool

from dotenv import load_dotenv

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

def tariff_agent(query: str) -> str:
    returntxt = ""

    # Define the path to the file to be uploaded
    file_path = "tariffs/tariff_database_2025.txt"

    # Upload the file
    file = project_client.agents.files.upload_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")
    #print(f"File name: {file.name}, File size: {file.size} bytes")

    # Create a vector store with the uploaded file
    vector_store = project_client.agents.vector_stores.create_and_poll(file_ids=[file.id], name="tariff_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create a file search tool
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    # Create an agent with the file search tool
    agent = project_client.agents.create_agent(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # Model deployment name
        name="tariff-agent",  # Name of the agent
        instructions=f"""You are a knowledgeable customs and trade assistant specializing in tariff information. You are helping end users understand tariffs, duties, and related trade regulations based on the data provided in the tariff database.
        The data includes fields such as:
        - HS Code (Harmonized System Code)
        - Product Description
        - Country of Origin
        - Tariff Rate (%)
        - Tariff Type (MFN, Preferential, etc.)
        - Additional Duties (if applicable)
        - Exemptions or Notes

        When answering questions:
        - Always interpret HS Codes when provided.
        - If a country is mentioned, filter by “Country of Origin”.
        - If a product name is mentioned (e.g., "laptops", "machinery"), use the description field to find relevant records.
        - Clearly explain what the tariff rate is, if it varies by country or trade agreement.
        - If exemptions exist, list them and explain briefly.

        If no matching record is found, politely inform the user and suggest checking for typos or using more general keywords.

        Examples of good responses:
        - "The tariff for '8501 – Electric motors and generators' from Germany is 7.5% under MFN terms."
        - "There is a duty exemption on coffee imported from Ethiopia under the Preferential Trade Agreement."
        - "For HS Code 9403 (furniture), the standard tariff from China is 15%, but it may vary under specific trade deals."

        Stay concise, clear, and user-friendly.

        """,  # Instructions for the agent
        tools=file_search.definitions,  # Tools available to the agent
        tool_resources=file_search.resources,  # Resources for the tools
    )
    print(f"Created agent, ID: {agent.id}")
    # Create a thread
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Send a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=query,  # Message content
    )
    print(f"Created message, ID: {message['id']}")

    # Create and process an agent run in the thread
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Cleanup resources
    project_client.agents.vector_stores.delete(vector_store.id)
    print("Deleted vector store")

    project_client.agents.files.delete(file_id=file.id)
    print("Deleted file")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # project_client.agents.threads.delete(thread.id)
    # print("Deleted thread")

    # Fetch and log all messages from the thread
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    file_name = os.path.split(file_path)[-1]
    
    # Only return the assistant's response (the last assistant message)
    for msg in messages:
        if msg.role == "assistant" and msg.text_messages:
            last_text = msg.text_messages[-1].text.value
            for annotation in msg.text_messages[-1].text.annotations:
                citation = (
                    file_name if annotation.file_citation.file_id == file.id else annotation.file_citation.file_id
                )
                last_text = last_text.replace(annotation.text, f" [{citation}]")
            print(f"Assistant response: {last_text}")
            returntxt += last_text + "\n"  # Only store the assistant's response
            break  # Take the first (and should be only) assistant response

    return returntxt

def tariff_chat():
    st.set_page_config(
        page_title="US Tariff AI Assistant",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🛠️ US Tariff AI Assistant")
    st.write("Ask questions about US tariffs and get detailed information from our comprehensive database.")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a scrollable container for chat history
    st.markdown("### 💬 Chat History")
    
    # Display chat history in a scrollable container
    if st.session_state.messages:
        st.markdown("""
        <div style="
            max-height: 500px; 
            overflow-y: auto; 
            padding: 20px; 
            border: 2px solid #e0e0e0; 
            border-radius: 12px;
            background: #f8f9fa;
            margin: 10px 0;
        ">
        """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: #007acc; 
                    color: white; 
                    padding: 12px 16px; 
                    border-radius: 18px; 
                    margin: 8px 0 8px 40px; 
                    max-width: 80%;
                    margin-left: auto;
                    text-align: right;
                ">
                    <strong>👤 You:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: #e3f2fd; 
                    color: #1565c0; 
                    padding: 12px 16px; 
                    border-radius: 18px; 
                    margin: 8px 40px 8px 0; 
                    max-width: 80%;
                    border-left: 4px solid #2196f3;
                ">
                    <strong>🤖 Assistant:</strong><br>
                    <div style="white-space: pre-wrap; font-family: 'Segoe UI', sans-serif;">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 Start a conversation by asking a question about US tariffs in the input box below.")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("What are the tariffs for Toughened (tempered) safety glass, of size and shape suitable for incorporation in vehicles, aircraft, spacecraft or vessels text_rate?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show loading spinner while processing
        with st.spinner("🔍 Searching tariff database and generating response..."):
            try:
                # Call the tariff agent function
                response = tariff_agent(prompt)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Rerun to display the new messages
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing your request: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I apologize, but I encountered an error while processing your request: {str(e)}"
                })
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Chat History", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()
    

if __name__ == "__main__":
    # Run the tariff agent with a sample query
    # sample_query = "What are the tariffs for Bovine carcasses and halves, fresh or chld for Australia?"
    # sample_query = "what is the tax rate for Meat and edible meat offal of camels and other camelids, fresh, chilled or frozen?"
    # response = tariff_agent(sample_query)
    # print("Response from tariff agent:")
    # print(response)

    tariff_chat()