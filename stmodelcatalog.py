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
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import FilePurpose, FileSearchTool
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import pandas as pd

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration using managed identity for security
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_ENDPOINT_WEST = os.getenv("AZURE_OPENAI_ENDPOINT_WEST")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
WHISPER_DEPLOYMENT_NAME = "whisper"
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
CHAT_DEPLOYMENT_NAME_WEST = os.getenv("AZURE_OPENAI_DEPLOYMENT_WEST")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

# Azure AI Projects configuration
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 
project_endpoint = os.environ["PROJECT_ENDPOINT"]

# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

# Function to get model list and deployment status with proper error handling
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_model_list():
    """
    Retrieve models and deployments from Azure AI Projects with fallback support.
    
    Returns:
        Tuple of (DataFrame, deployed_models_list, catalog_models_list)
    """
    try:
        catalog_models = []
        deployed_models = []
        deployed_model_names = []
        
        # Try to get deployments first (more reliable)
        try:
            deployments = list(project_client.deployments.list())
            
            for deployment in deployments:
                try:
                    # Extract deployment information
                    model_name = getattr(deployment, 'model_name', getattr(deployment, 'name', 'Unknown'))
                    deployment_name = getattr(deployment, 'name', getattr(deployment, 'deployment_name', model_name))
                    status = getattr(deployment, 'status', 'Active')
                    inference_url = f"{project_endpoint}/models/{deployment_name}/chat/completions"
                    # print(f"Deployment: {deployment_name}, Endpoint URL: {inference_url}")
                    
                    deployed_model_info = {
                        'name': model_name,
                        'deployment_name': deployment_name,
                        'status': status,
                        'endpoint': getattr(deployment, 'endpoint', AZURE_ENDPOINT),
                        'created_at': getattr(deployment, 'created_at', 'N/A'),
                        'inferenceurl': inference_url
                    }
                    
                    deployed_models.append(deployed_model_info)
                    deployed_model_names.append(deployment_name)  # Use deployment name for selection
                    
                except Exception as e:
                    continue
            
        except AttributeError:
            # Fallback to known deployments
            deployed_models = get_fallback_deployed_models_simple()
            deployed_model_names = [model['deployment_name'] for model in deployed_models]
        except Exception as e:
            deployed_models = get_fallback_deployed_models_simple()
            deployed_model_names = [model['deployment_name'] for model in deployed_models]
        
        # Try to get catalog models
        try:
            models_iter = project_client.models.list()
            catalog_models = list(models_iter)
            
        except AttributeError:
            catalog_models = get_fallback_catalog_models_simple()
        except Exception as e:
            catalog_models = get_fallback_catalog_models_simple()
        
        # Create comprehensive model list
        all_models = []
        
        # Add deployed models
        for model in deployed_models:
            all_models.append({
                'Model Name': model['name'],
                'Deployment Name': model['deployment_name'],
                'Status': '🟢 Deployed',
                'Type': 'Deployed',
                'Details': f"Status: {model.get('status', 'Active')}"
            })
        
        # Add catalog models that aren't deployed
        for model in catalog_models:
            model_name = getattr(model, 'name', getattr(model, 'model_name', str(model)))
            if model_name not in [dm['name'] for dm in deployed_models]:
                all_models.append({
                    'Model Name': model_name,
                    'Deployment Name': 'Not Deployed',
                    'Status': '🔴 Available',
                    'Type': 'Available',
                    'Details': 'Available for deployment'
                })
        
        # If no models found, use fallback
        if not all_models:
            deployed_models = get_fallback_deployed_models_simple()
            deployed_model_names = [model['deployment_name'] for model in deployed_models]
            
            for model in deployed_models:
                all_models.append({
                    'Model Name': model['name'],
                    'Deployment Name': model['deployment_name'],
                    'Status': '🟢 Deployed (Fallback)',
                    'Type': 'Deployed',
                    'Details': model['description']
                })
        
        # Create DataFrame
        model_df = pd.DataFrame(all_models)
        
        return model_df, deployed_model_names, deployed_models
        
    except Exception as e:
        # Return fallback data
        deployed_models = get_fallback_deployed_models_simple()
        deployed_model_names = [model['deployment_name'] for model in deployed_models]
        
        fallback_data = []
        for model in deployed_models:
            fallback_data.append({
                'Model Name': model['name'],
                'Deployment Name': model['deployment_name'],
                'Status': '🟢 Deployed (Fallback)',
                'Type': 'Deployed',
                'Details': model['description']
            })
        
        return pd.DataFrame(fallback_data), deployed_model_names, deployed_models

def get_fallback_deployed_models_simple():
    """Simple fallback deployed models for when API fails."""
    return [
        {
            'name': 'GPT-4o',
            'deployment_name': CHAT_DEPLOYMENT_NAME or 'gpt-4o',
            'description': 'Advanced language model for complex reasoning',
            'status': 'Active',
            'endpoint': AZURE_ENDPOINT
        },
        {
            'name': 'GPT-4o-West',
            'deployment_name': CHAT_DEPLOYMENT_NAME_WEST or 'gpt-4o-west',
            'description': 'West region deployment for improved latency',
            'status': 'Active',
            'endpoint': AZURE_ENDPOINT_WEST
        },
        {
            'name': 'Whisper',
            'deployment_name': WHISPER_DEPLOYMENT_NAME or 'whisper',
            'description': 'Speech-to-text transcription model',
            'status': 'Active',
            'endpoint': AZURE_ENDPOINT
        }
    ]

def get_fallback_catalog_models_simple():
    """Simple fallback catalog models for when API fails."""
    return [
        {'name': 'GPT-4-Turbo', 'model_name': 'GPT-4-Turbo'},
        {'name': 'GPT-3.5-Turbo', 'model_name': 'GPT-3.5-Turbo'},
        {'name': 'DALL-E-3', 'model_name': 'DALL-E-3'},
        {'name': 'Text-Embedding-3-Large', 'model_name': 'Text-Embedding-3-Large'}
    ]

# Function to get inference client for a deployed model
def get_inference_client(deployment_name, deployed_models_list):
    """
    Get an appropriate OpenAI client for the selected deployment.
    
    Args:
        deployment_name: Name of the deployment to use
        deployed_models_list: List of deployed models with their configurations
        
    Returns:
        AzureOpenAI client instance or None if not found
    """
    try:
        # Find the deployment in our list
        selected_deployment = None
        for model in deployed_models_list:
            if model['deployment_name'] == deployment_name:
                selected_deployment = model
                break
        
        if not selected_deployment:
            st.error(f"❌ Deployment '{deployment_name}' not found in available models")
            return None
        
        # Determine which endpoint to use
        endpoint = selected_deployment.get('endpoint', AZURE_ENDPOINT)
        
        # Use appropriate client based on endpoint
        if endpoint == AZURE_ENDPOINT_WEST:
            return AzureOpenAI(
                azure_endpoint=AZURE_ENDPOINT_WEST,
                api_key=AZURE_API_KEY,
                api_version="2024-12-01-preview"
            )
        else:
            return AzureOpenAI(
                azure_endpoint=AZURE_ENDPOINT,
                api_key=AZURE_API_KEY,
                api_version="2024-12-01-preview"
            )
            
    except Exception as e:
        st.error(f"❌ Error initializing inference client for '{deployment_name}': {str(e)}")
        return None
    
# Function to get inference client for a deployed model
def get_ai_inference_client_openai(model_name, messages, modelname):
    returntxt = ""

    api_version = "2024-12-01-preview"
    api_base = AZURE_ENDPOINT
    api_key = AZURE_API_KEY

    infclient = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=api_version  # Adjust API version as needed
    )

    response = infclient.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            max_tokens=2000,
                            temperature=0.7,
                            top_p=0.95
                        )

    print(response.choices[0].message.content)
    print(f"\nToken usage: {response.usage}")

    returntxt = response.choices[0].message.content

    return returntxt

# Function to get inference client for a deployed model
def get_ai_inference_client(model_name, query, modelname):
    # endpoint = "https://agentnew-resource.eastus2.models.ai.azure.com"
    #endpoint = f"https://{model_name}.eastus2.models.ai.azure.com"
    endpoint = f"https://agentnew-resource.eastus2.models.ai.azure.com"
    # endpoint = f"https://agentnew-resource.services.ai.azure.com/api/projects/agentnew"


    if 'gpt' in model_name or 'openai' in model_name or 'ada' in model_name:
        endpoint = f"https://{model_name}.eastus2.models.ai.azure.com"
    else:
        endpoint = f"https://agentnew-resource.eastus2.models.ai.azure.com"

    aiclient = ChatCompletionsClient(endpoint=endpoint, 
                                     credential=AzureKeyCredential(AZURE_API_KEY))
    
    # Prepare messages with context
    messages = [
        SystemMessage(content="You are a helpful AI assistant. Provide clear, accurate, and helpful responses.")
    ]

    # Add chat history to context
    for msg in st.session_state.chat_history:
        if msg["role"] == "system":
            messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            messages.append(UserMessage(content=msg["content"]))

    response = aiclient.complete(
        # messages=[
        #     SystemMessage("You are a Multiple AI model helpful assistant."),
        #     UserMessage(query),
        # ],
        messages=messages,
        model=model_name,
        max_tokens=2500,
    )

    print('Output from model: ', response.choices[0].message.content)
    print(f"\nToken usage: {response.usage}")


    return returntxt

    
def modelcatalogmain():
    st.set_page_config(
        page_title="Azure Model Catalog & Chat",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .model-dropdown {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .model-catalog-container {
        max-height: 600px;
        overflow-y: auto;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        margin: 10px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .model-catalog-container::-webkit-scrollbar {
        width: 8px;
    }
    .model-catalog-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 6px;
    }
    .model-catalog-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #007acc 0%, #005999 100%);
        border-radius: 6px;
    }
    .model-catalog-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #005999 0%, #003d6b 100%);
    }
    /* Custom scrollbar for chat containers */
    div[style*="overflow-y: auto"]::-webkit-scrollbar {
        width: 8px;
    }
    div[style*="overflow-y: auto"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 6px;
    }
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #007acc 0%, #005999 100%);
        border-radius: 6px;
    }
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #005999 0%, #003d6b 100%);
    }
    .stats-container {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .compact-metric {
        text-align: center;
        padding: 10px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 8px;
        margin: 5px;
    }
    .section-header {
        color: #2c3e50;
        font-weight: 600;
        margin: 20px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Azure Model Catalog & Chat Interface</h1>
        <p>Discover and interact with Azure OpenAI models</p>
    </div>
    """, unsafe_allow_html=True)

    # Load model data with loading indicator
    with st.spinner("🔄 Loading model catalog...", show_time=True):
        # Create a compact container for status messages
        status_container = st.empty()
        with status_container.container():
            st.markdown("""
            <style>
            .status-messages-container {
                max-height: 80px;
                overflow-y: auto;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                background: #f8f9fa;
                margin: 10px 0;
                font-size: 0.9em;
            }
            .status-messages-container::-webkit-scrollbar {
                width: 6px;
            }
            .status-messages-container::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }
            .status-messages-container::-webkit-scrollbar-thumb {
                background: #007acc;
                border-radius: 3px;
            }
            </style>
            <div class="status-messages-container">
                <div>📊 Initializing model catalog...</div>
            </div>
            """, unsafe_allow_html=True)
        
        model_df, deployed_model_names, deployed_models_list = get_model_list()
        
        # Clear the status container after loading
        status_container.empty()

    # Create two-column layout
    left_col, right_col = st.columns([1, 1])
    
    # LEFT COLUMN - Model Catalog
    with left_col:
        st.markdown('<div class="section-header">📋 Model Catalog</div>', unsafe_allow_html=True)
        
        if not model_df.empty:
            # Compact header with refresh button and stats
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Show compact statistics in a row
                deployed_count = len([m for m in model_df['Status'] if '🟢' in m])
                available_count = len([m for m in model_df['Status'] if '🔴' in m])
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin: 10px 0;">
                    <div class="compact-metric"><strong>{deployed_count}</strong><br>🟢 Deployed</div>
                    <div class="compact-metric"><strong>{available_count}</strong><br>🔴 Available</div>
                    <div class="compact-metric"><strong>{len(model_df)}</strong><br>📊 Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 Refresh", key="refresh_models"):
                    st.cache_data.clear()
                    st.rerun()
            
            # Scrollable model table container
            st.markdown('<div class="model-catalog-container">', unsafe_allow_html=True)
            
            # Display model table with better formatting
            st.dataframe(
                model_df, 
                use_container_width=True,
                hide_index=True,
                height=550,  # Increased height for better visibility
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Model Name": st.column_config.TextColumn("Model", width="medium"),
                    "Deployment Name": st.column_config.TextColumn("Deployment", width="medium"),
                    "Details": st.column_config.TextColumn("Details", width="large")
                }
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No models found in the catalog.")
    
    # RIGHT COLUMN - Model Selection and Chat
    with right_col:
        # Model Selection Section
        st.markdown('<div class="section-header">🎯 Model Selection</div>', unsafe_allow_html=True)
        
        if deployed_model_names:
            st.markdown('<div class="model-dropdown">', unsafe_allow_html=True)
            
            # Create dropdown with better formatting
            deployment_options = []
            for model in deployed_models_list:
                option_text = f"{model['name']} ({model['deployment_name']})"
                deployment_options.append(option_text)
            
            # Initialize session state for selected model
            if 'selected_model_option' not in st.session_state:
                st.session_state.selected_model_option = deployment_options[0] if deployment_options else None
            
            # Compact model selection
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_option = st.selectbox(
                    "🤖 Choose a deployed model:",
                    options=deployment_options,
                    index=deployment_options.index(st.session_state.selected_model_option) if st.session_state.selected_model_option in deployment_options else 0,
                    help="Select from available deployed models to start chatting",
                    key="model_selector"
                )
            
            with col2:
                # Show model status
                if selected_option:
                    st.success("✅ Ready")
            
            # Extract deployment name from selection
            if selected_option:
                # Parse selection to get deployment name
                deployment_name = selected_option.split('(')[1].split(')')[0]
                model_name = selected_option.split('(')[0].strip()  # Add this line
                st.session_state.selected_model_option = selected_option
                st.session_state.selected_deployment = deployment_name
                st.session_state.selected_model_name = model_name
                
                # Find the selected model info
                selected_model_info = next(
                    (model for model in deployed_models_list if model['deployment_name'] == deployment_name), 
                    None
                )
                
                if selected_model_info:
                    # Compact model details
                    with st.expander(f"ℹ️ Model Details", expanded=False):
                        st.write(f"**Model:** {selected_model_info['name']}")
                        st.write(f"**Deployment:** {selected_model_info['deployment_name']}")
                        st.write(f"**Status:** {selected_model_info.get('status', 'Active')}")
                        st.write(f"**Endpoint:** {selected_model_info.get('endpoint', 'Default').split('/')[-1]}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ No deployed models found. Please ensure models are deployed in your Azure AI Projects.")
            st.info("💡 Contact your administrator to deploy models to the Azure AI Projects workspace.")
            return

        # Chat Interface Section
        st.markdown('<div class="section-header">💬 Chat Interface</div>', unsafe_allow_html=True)
        
        if 'selected_deployment' in st.session_state and st.session_state.selected_deployment:
            # Initialize inference client
            client_instance = get_inference_client(st.session_state.selected_deployment, deployed_models_list)
            
            if client_instance:
                # Initialize chat history
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                
                # Chat history display in scrollable container
                if st.session_state.chat_history:
                    # Create a scrollable container using Streamlit's container with custom CSS
                    with st.container():
                        st.markdown("""
                        <style>
                        .chat-container {
                            height: 400px;
                            overflow-y: auto;
                            border: 2px solid #e0e0e0;
                            border-radius: 15px;
                            padding: 15px;
                            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            margin: 15px 0;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        }
                        .chat-message {
                            margin: 10px 0;
                            padding: 12px;
                            border-radius: 10px;
                            word-wrap: break-word;
                        }
                        .user-message {
                            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                            border-left: 4px solid #2196f3;
                        }
                        .assistant-message {
                            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                            border-left: 4px solid #9c27b0;
                        }
                        .message-header {
                            font-weight: bold;
                            color: #333;
                            margin-bottom: 8px;
                        }
                        .message-content {
                            color: #555;
                            line-height: 1.5;
                            white-space: pre-wrap;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Create the chat container with fixed height
                        chat_html = '<div class="chat-container">'
                        
                        # Add all messages to the HTML
                        for i, message in enumerate(st.session_state.chat_history):
                            role_icon = "🧑‍💻" if message["role"] == "user" else "🤖"
                            role_name = "You" if message["role"] == "user" else st.session_state.selected_deployment
                            message_class = "user-message" if message["role"] == "user" else "assistant-message"
                            
                            # Escape HTML content properly
                            escaped_content = message["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")
                            
                            chat_html += f'''<div class="chat-message {message_class}">
                                <div class="message-header">
                                    {role_icon} {role_name}
                                </div>
                                <div class="message-content">
                                    {escaped_content}
                                </div>
                            </div>'''
                        
                        # Close the chat container
                        chat_html += '</div>'
                        
                        # Add JavaScript to scroll to bottom
                        chat_html += '''
<script>
setTimeout(function() {
    var chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}, 100);
</script>'''
                        
                        st.markdown(chat_html, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="
                        height: 200px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border: 2px dashed #ddd;
                        border-radius: 15px;
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        margin: 15px 0;
                        text-align: center;
                        color: #6c757d;
                    ">
                        <div>
                            <h5>💡 Ready to chat!</h5>
                            <p>Start a conversation with {deployment_name}.</p>
                        </div>
                    </div>
                    """.format(deployment_name=st.session_state.selected_deployment), unsafe_allow_html=True)
                
                # Chat input
                prompt = st.chat_input(f"Ask {st.session_state.selected_deployment} anything...")
                
                if prompt:
                    # Add user message to chat history
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    
                    # Prepare messages with context
                    messages = [
                        {"role": "system", "content": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses."}
                    ]
                    
                    # Add chat history to context
                    for msg in st.session_state.chat_history:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    # Get response from model
                    with st.spinner(f"🧠 {st.session_state.selected_deployment} is thinking...", show_time=True):
                        try:
                            # response = client_instance.chat.completions.create(
                            #     model=st.session_state.selected_deployment,
                            #     messages=messages,
                            #     max_tokens=1000,
                            #     temperature=0.7,
                            #     top_p=0.95
                            # )
                            
                            # assistant_response = response.choices[0].message.content

                            # st.session_state.selected_model_name
                            model_name = st.session_state.selected_model_name
                            assistant_response = get_ai_inference_client_openai(st.session_state.selected_deployment, messages, model_name)
                            # assistant_response = get_ai_inference_client_openai(st.session_state.selected_deployment, messages)

                            # result = get_ai_inference_client(prompt, st.session_state.selected_deployment)
                            # assistant_response = result
                            
                            # Add assistant response to chat history
                            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                            
                            # Rerun to display new messages
                            st.rerun()
                            
                        except Exception as e:
                            error_msg = f"❌ Error getting response from {st.session_state.selected_deployment}: {str(e)}"
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                            st.rerun()
                
                # Compact chat management
                if st.session_state.chat_history:
                    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_messages = len(st.session_state.chat_history)
                        user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
                        st.metric("💬", f"{user_messages}/{total_messages}", help="User / Total messages")
                    
                    with col2:
                        if st.button("🗑️ Clear", key="clear_chat", help="Clear chat history"):
                            st.session_state.chat_history = []
                            st.rerun()
                    
                    with col3:
                        chat_data = {
                            "model": st.session_state.selected_deployment,
                            "timestamp": datetime.now().isoformat(),
                            "messages": st.session_state.chat_history
                        }
                        
                        st.download_button(
                            label="💾 Export",
                            data=json.dumps(chat_data, indent=2),
                            file_name=f"chat_{st.session_state.selected_deployment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            help="Download chat history"
                        )
                    
                    with col4:
                        avg_length = sum(len(m["content"]) for m in st.session_state.chat_history) // len(st.session_state.chat_history) if st.session_state.chat_history else 0
                        st.metric("📊", f"{avg_length}", help="Avg message length")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ Failed to initialize client for {st.session_state.selected_deployment}")
        else:
            st.info("🎯 Please select a deployed model above to start chatting.")

if __name__ == "__main__":
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    
    # Run the model catalog main function
    modelcatalogmain()
