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

def save_data(updated_users, updated_servers, file_path='mcplist.json'):
    try:
        with open(file_path, 'r') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = {}
    existing['users'] = updated_users
    existing['mcp_servers'] = updated_servers
    try:
        with open(file_path, 'w') as f:
            json.dump(existing, f, indent=2)
        st.cache_data.clear()
        return True, None
    except Exception as e:
        return False, str(e)

def get_server_by_id(server_list, server_id):
    """Return server object by ID (type-agnostic)."""
    sid = str(server_id).strip()
    for s in server_list:
        if str(s.get('id')).strip() == sid:
            return s
    return None

def update_user_access_for_server(server_id, selected_usernames, users_list):
    username_set = set(selected_usernames)
    for u in users_list:
        has_access = server_id in u.get('access_servers', [])
        if u['username'] in username_set and not has_access:
            u.setdefault('access_servers', []).append(server_id)
        elif u['username'] not in username_set and has_access:
            u['access_servers'] = [sid for sid in u['access_servers'] if sid != server_id]
    # normalize ordering
    for u in users_list:
        if 'access_servers' in u:
            u['access_servers'] = sorted(set(u['access_servers']))

def main():
    # Set page config early
    st.set_page_config(
        page_title="MCP Server Access Dashboard",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state copies to allow mutation without reloading module-level globals directly
    if 'users_data' not in st.session_state:
        st.session_state['users_data'] = users
    if 'servers_data' not in st.session_state:
        st.session_state['servers_data'] = mcp_servers

    st.title("MCP Server Access & Administration")
    tab_options = ["User Access Dashboard", "Admin: Edit MCP Server & Access"]
    # Persist active tab in session state
    if 'active_tab' not in st.session_state:
        st.session_state['active_tab'] = tab_options[0]
    selected_tab = st.radio("View", tab_options, index=tab_options.index(st.session_state['active_tab']), horizontal=True, key="active_tab_selector")
    st.session_state['active_tab'] = selected_tab

    # ----------------------------- DASHBOARD VIEW ---------------------------------
    if selected_tab == "User Access Dashboard":
        usernames = [user['username'] for user in st.session_state['users_data']]
        selected_username = st.selectbox("Select a User:", usernames, key="dashboard_user_select")
        selected_user = next((user for user in st.session_state['users_data'] if user['username'] == selected_username), None)

        if selected_user:
            st.subheader(f"Access for User: {selected_username}")

            access_ids = selected_user.get('access_servers', [])
            accessible_servers = [s for s in st.session_state['servers_data'] if s['id'] in access_ids]

            if accessible_servers:
                certified_map = { 'Yes' if s.get('certified') else 'No' for s in accessible_servers }
                purpose_set = { s.get('purpose') for s in accessible_servers if s.get('purpose') }
                bu_set = { s.get('business_unit') for s in accessible_servers if s.get('business_unit') }

                certified_options = sorted(certified_map)
                purpose_options = sorted(purpose_set)
                bu_options = sorted(bu_set)

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

                if not selected_certified:
                    selected_certified = certified_options
                if not selected_purposes:
                    selected_purposes = purpose_options
                if not selected_business_units:
                    selected_business_units = bu_options

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
                else:
                    server_data = []
                    # Use current date
                    current_date = datetime.utcnow().date()
                    for server in filtered_servers:
                        try:
                            exp_date = datetime.strptime(server['expiration_date'], '%Y-%m-%d').date()
                        except Exception:
                            exp_date = current_date
                        is_expired = exp_date < current_date
                        server_data.append({
                            'ID': server['id'],
                            'Name': server['name'],
                            'Certified': 'Yes' if server.get('certified') else 'No',
                            'Expiration Date': server.get('expiration_date'),
                            'Expired?': 'Yes' if is_expired else 'No',
                            'Company': server.get('company_name'),
                            'Business Unit': server.get('business_unit'),
                            'Cost Center': server.get('cost_center'),
                            'Purpose': server.get('purpose'),
                            'Instructions': server.get('instructions'),
                            'Prompt': server.get('prompt')
                        })
                    df = pd.DataFrame(server_data)
                    st.caption(f"Showing {len(filtered_servers)} of {len(accessible_servers)} accessible servers.")
                    st.dataframe(df, width='stretch')

                    with st.expander("Show Authentication Details"):
                        for server in filtered_servers:
                            st.write(f"**{server['name']} Auth:**")
                            st.write(f"Username: {server['auth']['username']}")
                            st.write(f"API Key: {server['auth']['api_key']}")
            else:
                st.warning("No accessible servers for this user.")
        else:
            st.info("Please select a user.")

    # ----------------------------- ADMIN EDIT VIEW --------------------------------
    elif selected_tab == "Admin: Edit MCP Server & Access":
        st.subheader("Edit MCP Server & User Access")
        admin_cols = st.columns([2,1])
        with admin_cols[0]:
            server_select_display = [f"{s['id']} - {s['name']}" for s in st.session_state['servers_data']]
            if not server_select_display:
                st.info("No servers available to edit.")
                return  # early exit stays on admin tab
            selected_server_display = st.selectbox("Select MCP Server to Edit", server_select_display, key="admin_server_select")
            # Defensive parsing in case name includes delimiter
            parts = selected_server_display.split(' - ')
            selected_server_id = parts[0].strip() if parts else ''
            server_obj = get_server_by_id(st.session_state['servers_data'], selected_server_id)
            with st.expander("Debug Server Selection", expanded=False):
                st.write("Selected display:", selected_server_display)
                st.write("Parsed ID:", selected_server_id)
                st.write("All IDs:", [str(s.get('id')) for s in st.session_state['servers_data']])
        with admin_cols[1]:
            st.markdown("Use this panel to modify server metadata and adjust which users have access.")

        if server_obj:
            with st.form(key=f"edit_server_form_{server_obj['id']}"):
                st.markdown("### Server Metadata")
                name = st.text_input("Name", value=server_obj.get('name',''))
                certified = st.checkbox("Certified", value=bool(server_obj.get('certified')))
                try:
                    exp_date_default = datetime.strptime(server_obj.get('expiration_date','1970-01-01'), '%Y-%m-%d').date()
                except Exception:
                    exp_date_default = datetime.utcnow().date()
                exp_date = st.date_input("Expiration Date", value=exp_date_default)
                company_name = st.text_input("Company Name", value=server_obj.get('company_name',''))
                business_unit = st.text_input("Business Unit", value=server_obj.get('business_unit',''))
                cost_center = st.text_input("Cost Center", value=server_obj.get('cost_center',''))
                purpose = st.text_input("Purpose", value=server_obj.get('purpose',''))
                instructions = st.text_area("Instructions", value=server_obj.get('instructions',''), height=120)
                prompt_val = st.text_area("Prompt", value=server_obj.get('prompt',''), height=120)
                st.markdown("### Authentication")
                auth_username = st.text_input("Auth Username", value=server_obj.get('auth',{}).get('username',''))
                auth_api_key_input = st.text_input("Auth API Key (leave blank to keep existing)", value="", type="password")

                st.markdown("### User Access")
                all_usernames = [u['username'] for u in st.session_state['users_data']]
                current_access_usernames = [u['username'] for u in st.session_state['users_data'] if server_obj['id'] in u.get('access_servers', [])]
                selected_users_for_access = st.multiselect(
                    "Users with Access", options=all_usernames, default=current_access_usernames,
                    help="Select which users should have access to this MCP server"
                )

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    # Update server object in place
                    server_obj['name'] = name
                    server_obj['certified'] = certified
                    server_obj['expiration_date'] = exp_date.strftime('%Y-%m-%d')
                    server_obj['company_name'] = company_name
                    server_obj['business_unit'] = business_unit
                    server_obj['cost_center'] = cost_center
                    server_obj['purpose'] = purpose
                    server_obj['instructions'] = instructions
                    server_obj['prompt'] = prompt_val
                    server_obj.setdefault('auth', {})['username'] = auth_username
                    if auth_api_key_input.strip():
                        server_obj['auth']['api_key'] = auth_api_key_input.strip()

                    # Update user access lists
                    update_user_access_for_server(server_obj['id'], selected_users_for_access, st.session_state['users_data'])

                    # Persist changes to disk
                    ok, err = save_data(st.session_state['users_data'], st.session_state['servers_data'])
                    if ok:
                        st.success("Changes saved successfully.")
                    else:
                        st.error(f"Failed to save changes: {err}")
        else:
            st.warning("Selected server not found.")

if __name__ == "__main__":
    main()