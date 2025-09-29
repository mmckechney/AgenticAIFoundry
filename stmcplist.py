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
    with open('mcplist.json', 'r') as f:
        data = json.load(f)
    return data['users'], data['mcp_servers']

users, mcp_servers = load_data()

def main():
    # Streamlit app title
    # st.title("MCP Server Access Dashboard")
    st.set_page_config(
        page_title="MCP Server Access Dashboard",
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
        
        # Get accessible server IDs
        access_ids = selected_user['access_servers']

        # Filter accessible servers
        accessible_servers = [server for server in mcp_servers if server['id'] in access_ids]

        if accessible_servers:
            # ------------------------------------------------------------------
            # Build filter option sets
            # ------------------------------------------------------------------
            certified_map = { 'Yes' if s.get('certified') else 'No' for s in accessible_servers }
            purpose_set = { s.get('purpose') for s in accessible_servers if s.get('purpose') }
            bu_set = { s.get('business_unit') for s in accessible_servers if s.get('business_unit') }

            certified_options = sorted(certified_map)
            purpose_options = sorted(purpose_set)
            bu_options = sorted(bu_set)

            # ------------------------------------------------------------------
            # Filter widgets (default = all selected)
            # ------------------------------------------------------------------
            with st.expander("Filters", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    selected_certified = st.multiselect(
                        "Certified", certified_options, default=certified_options, help="Filter by certification status"
                    )
                with c2:
                    selected_purposes = st.multiselect(
                        "Purpose", purpose_options, default=purpose_options, help="Filter by server purpose"
                    )
                with c3:
                    selected_business_units = st.multiselect(
                        "Business Unit", bu_options, default=bu_options, help="Filter by business unit"
                    )

            # Treat empty selections (if user unselects all) as 'show all'
            if not selected_certified:
                selected_certified = certified_options
            if not selected_purposes:
                selected_purposes = purpose_options
            if not selected_business_units:
                selected_business_units = bu_options

            # ------------------------------------------------------------------
            # Apply filter logic
            # ------------------------------------------------------------------
            filtered_servers = []
            for s in accessible_servers:
                cert_label = 'Yes' if s.get('certified') else 'No'
                if cert_label not in selected_certified:
                    continue
                if purpose_options and s.get('purpose') not in selected_purposes:
                    continue
                if bu_options and s.get('business_unit') not in selected_business_units:
                    continue
                filtered_servers.append(s)

            if not filtered_servers:
                st.warning("No servers match the selected filter criteria.")
                return

            # Create a DataFrame for display
            server_data = []
            current_date = datetime(2025, 9, 29)  # Given current date
            
            for server in filtered_servers:
                exp_date = datetime.strptime(server['expiration_date'], '%Y-%m-%d')
                is_expired = exp_date < current_date
                
                server_data.append({
                    'ID': server['id'],
                    'Name': server['name'],
                    'Certified': 'Yes' if server['certified'] else 'No',
                    'Expiration Date': server['expiration_date'],
                    'Expired?': 'Yes' if is_expired else 'No',
                    'Company': server['company_name'],
                    'Business Unit': server['business_unit'],
                    'Cost Center': server['cost_center'],
                    'Purpose': server['purpose'],
                    'Instructions': server['instructions'],
                    'Prompt': server['prompt']
                })
            
            df = pd.DataFrame(server_data)
            
            # Display the table
            st.dataframe(df, width='stretch')
            
            # Optionally, show auth details in expanders for security
            with st.expander("Show Authentication Details"):
                for server in filtered_servers:
                    st.write(f"**{server['name']} Auth:**")
                    st.write(f"Username: {server['auth']['username']}")
                    st.write(f"API Key: {server['auth']['api_key']}")
        else:
            st.warning("No accessible servers for this user.")
    else:
        st.info("Please select a user.")

if __name__ == "__main__":
    main()