import datetime
import os, time, json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
    FunctionTool,
    MessageRole,
    ConnectedAgentTool,
    FilePurpose,
)
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini

# Get MCP server configuration from environment variables
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "MicrosoftLearn")

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
# connection_string = project_client.telemetry.get_application_insights_connection_string()
connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

# Load the JSON data
@st.cache_data
def load_data():
    with open('agentlist.json', 'r') as f:
        data = json.load(f)
    return data['users'], data['agents']

users, agents = load_data()

def main():

    st.set_page_config(
        page_title="Agents Access Dashboard",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Dropdown to select user
    usernames = [user['username'] for user in users]
    selected_username = st.selectbox("Select a User:", usernames)

    # Find selected user
    selected_user = next((user for user in users if user['username'] == selected_username), None)

    if selected_user:
        st.subheader(f"Access for User: {selected_username}")
        
        # Get accessible agent IDs
        access_ids = selected_user['access_agents']
        
        # Filter accessible agents
        accessible_agents = [agent for agent in agents if agent['id'] in access_ids]
        
        if accessible_agents:
            # Current date for expiration check
            current_date = datetime(2025, 9, 29)
            
            # Get unique values for filters from accessible agents
            purposes = sorted(list(set(agent['purpose'] for agent in accessible_agents)))
            certified_options = ['All'] + ['Yes' if agent['certified'] else 'No' for agent in accessible_agents]
            certified_options = sorted(list(set(certified_options)))
            business_units = sorted(list(set(agent['business_unit'] for agent in accessible_agents)))
            owners = sorted(list(set(agent['owner'] for agent in accessible_agents)))
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                selected_purpose = st.multiselect("Filter by Purpose:", purposes, default=purposes)
            with col2:
                selected_certified = st.selectbox("Filter by Certified:", certified_options, index=0)
            
            col3, col4 = st.columns(2)
            with col3:
                selected_business_unit = st.multiselect("Filter by Business Unit:", business_units, default=business_units)
            with col4:
                selected_owner = st.multiselect("Filter by Owner:", owners, default=owners)
            
            # Apply filters
            filtered_agents = accessible_agents
            if selected_purpose != []:
                filtered_agents = [a for a in filtered_agents if a['purpose'] in selected_purpose]
            if selected_certified != 'All':
                filtered_agents = [a for a in filtered_agents if ('Yes' if a['certified'] else 'No') == selected_certified]
            if selected_business_unit != []:
                filtered_agents = [a for a in filtered_agents if a['business_unit'] in selected_business_unit]
            if selected_owner != []:
                filtered_agents = [a for a in filtered_agents if a['owner'] in selected_owner]
            
            # Create a DataFrame for display
            agent_data = []
            for agent in filtered_agents:
                exp_date = datetime.strptime(agent['expiration_date'], '%Y-%m-%d')
                is_expired = exp_date < current_date
                
                agent_data.append({
                    'ID': agent['id'],
                    'Name': agent['name'],
                    'Certified': 'Yes' if agent['certified'] else 'No',
                    'Expiration Date': agent['expiration_date'],
                    'Expired?': 'Yes' if is_expired else 'No',
                    'Business Unit': agent['business_unit'],
                    'Owner': agent['owner'],
                    'Purpose': agent['purpose'],
                    'Instructions': agent['instructions'][:50] + '...' if len(agent['instructions']) > 50 else agent['instructions'],
                    'Prompt': agent['prompt'][:50] + '...' if len(agent['prompt']) > 50 else agent['prompt']
                })
            
            df = pd.DataFrame(agent_data)
            
            # Display the table
            st.dataframe(df, width='stretch')
            
            # Optionally, show detailed info in expanders
            for agent in filtered_agents:
                with st.expander(f"Details for {agent['name']}"):
                    st.write("**Instructions:**", agent['instructions'])
                    st.write("**Prompt:**", agent['prompt'])
                    st.write("**Parameters:**", agent['parameters'])
                    st.write("**Auth Method:**", agent['auth']['method'])
                    st.write("**Auth Credentials:**", agent['auth']['credentials'])
        else:
            st.warning("No accessible agents for this user.")
    else:
        st.info("Please select a user.")

if __name__ == "__main__":
    main()