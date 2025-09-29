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

def save_agent_data(updated_users, updated_agents, file_path='agentlist.json'):
    """Persist modified users and agents back to JSON and clear cache."""
    try:
        with open(file_path, 'r') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = {}
    existing['users'] = updated_users
    existing['agents'] = updated_agents
    try:
        with open(file_path, 'w') as f:
            json.dump(existing, f, indent=2)
        st.cache_data.clear()
        return True, None
    except Exception as e:
        return False, str(e)

def get_agent_by_id(agent_list, agent_id):
    aid = str(agent_id).strip()
    for a in agent_list:
        if str(a.get('id')).strip() == aid:
            return a
    return None

def update_user_access_for_agent(agent_id, selected_usernames, users_list):
    # Normalize agent id to string for stable comparisons
    agent_id_str = str(agent_id)
    username_set = set(selected_usernames)
    for u in users_list:
        # Normalize stored list to strings for comparison
        access_list = [str(aid) for aid in u.get('access_agents', [])]
        has_access = agent_id_str in access_list
        if u['username'] in username_set and not has_access:
            u.setdefault('access_agents', []).append(agent_id_str)
        elif u['username'] not in username_set and has_access:
            u['access_agents'] = [aid for aid in access_list if aid != agent_id_str]
    for u in users_list:
        if 'access_agents' in u:
            # Ensure uniqueness & string type
            u['access_agents'] = sorted({str(aid) for aid in u['access_agents']})

def main():
    st.set_page_config(
        page_title="Agents Access Dashboard",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state copies for safe mutation
    if 'users_data' not in st.session_state:
        st.session_state['users_data'] = users
    if 'agents_data' not in st.session_state:
        st.session_state['agents_data'] = agents
    if 'active_agent_tab' not in st.session_state:
        st.session_state['active_agent_tab'] = "User Access Dashboard"

    st.title("Agents Access & Administration")
    tab_options = ["User Access Dashboard", "Admin: Edit Agent & Access"]
    selected_tab = st.radio("View", tab_options, index=tab_options.index(st.session_state['active_agent_tab']), horizontal=True, key="agent_tab_selector")
    st.session_state['active_agent_tab'] = selected_tab

    # --------------------- DASHBOARD VIEW ---------------------
    if selected_tab == "User Access Dashboard":
        usernames = [user['username'] for user in st.session_state['users_data']]
        selected_username = st.selectbox("Select a User:", usernames, key="agent_dashboard_user")
        selected_user = next((user for user in st.session_state['users_data'] if user['username'] == selected_username), None)

        if selected_user:
            st.subheader(f"Access for User: {selected_username}")
            access_ids = selected_user.get('access_agents', [])
            accessible_agents = [a for a in st.session_state['agents_data'] if a['id'] in access_ids]

            if accessible_agents:
                current_date = datetime.utcnow().date()
                purposes = sorted({a.get('purpose') for a in accessible_agents if a.get('purpose')})
                certified_options = ['All'] + sorted({ 'Yes' if a.get('certified') else 'No' for a in accessible_agents })
                business_units = sorted({a.get('business_unit') for a in accessible_agents if a.get('business_unit')})
                owners = sorted({a.get('owner') for a in accessible_agents if a.get('owner')})

                fc1, fc2 = st.columns(2)
                with fc1:
                    selected_purpose = st.multiselect("Filter by Purpose:", purposes, default=purposes)
                with fc2:
                    selected_certified = st.selectbox("Filter by Certified:", certified_options, index=0)

                fc3, fc4 = st.columns(2)
                with fc3:
                    selected_business_unit = st.multiselect("Filter by Business Unit:", business_units, default=business_units)
                with fc4:
                    selected_owner = st.multiselect("Filter by Owner:", owners, default=owners)

                filtered_agents = accessible_agents
                if selected_purpose:
                    filtered_agents = [a for a in filtered_agents if a.get('purpose') in selected_purpose]
                if selected_certified != 'All':
                    filtered_agents = [a for a in filtered_agents if ('Yes' if a.get('certified') else 'No') == selected_certified]
                if selected_business_unit:
                    filtered_agents = [a for a in filtered_agents if a.get('business_unit') in selected_business_unit]
                if selected_owner:
                    filtered_agents = [a for a in filtered_agents if a.get('owner') in selected_owner]

                agent_rows = []
                for agent in filtered_agents:
                    try:
                        exp_date_obj = datetime.strptime(agent.get('expiration_date','1970-01-01'), '%Y-%m-%d').date()
                    except Exception:
                        exp_date_obj = current_date
                    is_expired = exp_date_obj < current_date
                    instructions_preview = agent.get('instructions','')
                    if len(instructions_preview) > 50:
                        instructions_preview = instructions_preview[:50] + '...'
                    prompt_preview = agent.get('prompt','')
                    if len(prompt_preview) > 50:
                        prompt_preview = prompt_preview[:50] + '...'
                    agent_rows.append({
                        'ID': agent.get('id'),
                        'Name': agent.get('name'),
                        'Certified': 'Yes' if agent.get('certified') else 'No',
                        'Expiration Date': agent.get('expiration_date'),
                        'Expired?': 'Yes' if is_expired else 'No',
                        'Business Unit': agent.get('business_unit'),
                        'Owner': agent.get('owner'),
                        'Purpose': agent.get('purpose'),
                        'Instructions': instructions_preview,
                        'Prompt': prompt_preview
                    })
                if agent_rows:
                    df = pd.DataFrame(agent_rows)
                    st.caption(f"Showing {len(filtered_agents)} of {len(accessible_agents)} accessible agents.")
                    st.dataframe(df, width='stretch')
                    for agent in filtered_agents:
                        with st.expander(f"Details for {agent.get('name')}"):
                            st.write("**Instructions:**", agent.get('instructions'))
                            st.write("**Prompt:**", agent.get('prompt'))
                            st.write("**Parameters:**", agent.get('parameters'))
                            auth = agent.get('auth', {})
                            st.write("**Auth Method:**", auth.get('method'))
                            st.write("**Auth Credentials:**", auth.get('credentials'))
                else:
                    st.warning("No agents match selected filters.")
            else:
                st.warning("No accessible agents for this user.")
        else:
            st.info("Please select a user.")

    # --------------------- ADMIN EDIT VIEW ---------------------
    elif selected_tab == "Admin: Edit Agent & Access":
        st.subheader("Edit Agent & User Access")
        left, right = st.columns([2,1])
        with left:
            agent_select_display = [f"{a['id']} - {a['name']}" for a in st.session_state['agents_data']]
            if not agent_select_display:
                st.info("No agents available to edit.")
                return
            selected_agent_display = st.selectbox("Select Agent to Edit", agent_select_display, key="admin_agent_select")
            parts = selected_agent_display.split(' - ')
            selected_agent_id = parts[0].strip() if parts else ''
            agent_obj = get_agent_by_id(st.session_state['agents_data'], selected_agent_id)
        with right:
            st.markdown("Modify agent metadata and assign or revoke user access.")

        if agent_obj:
            with st.form(key=f"edit_agent_form_{agent_obj.get('id')}"):
                st.markdown("### Agent Metadata")
                a_name = st.text_input("Name", value=agent_obj.get('name',''))
                a_cert = st.checkbox("Certified", value=bool(agent_obj.get('certified')))
                try:
                    exp_default = datetime.strptime(agent_obj.get('expiration_date','1970-01-01'), '%Y-%m-%d').date()
                except Exception:
                    exp_default = datetime.utcnow().date()
                a_exp = st.date_input("Expiration Date", value=exp_default)
                a_bu = st.text_input("Business Unit", value=agent_obj.get('business_unit',''))
                a_owner = st.text_input("Owner", value=agent_obj.get('owner',''))
                a_purpose = st.text_input("Purpose", value=agent_obj.get('purpose',''))
                a_instructions = st.text_area("Instructions", value=agent_obj.get('instructions',''), height=120)
                a_prompt = st.text_area("Prompt", value=agent_obj.get('prompt',''), height=120)
                st.markdown("### Parameters (JSON)")
                params_raw = st.text_area("Parameters JSON", value=json.dumps(agent_obj.get('parameters', {}), indent=2), height=180)
                st.markdown("### Authentication")
                auth_method = st.text_input("Auth Method", value=agent_obj.get('auth',{}).get('method',''))
                auth_credentials = st.text_area("Auth Credentials", value=agent_obj.get('auth',{}).get('credentials',''), height=100)

                st.markdown("### User Access")
                all_usernames = [u['username'] for u in st.session_state['users_data']]
                # Normalize comparison for current access detection
                agent_id_norm = str(agent_obj.get('id'))
                current_access_usernames = [
                    u['username'] for u in st.session_state['users_data']
                    if agent_id_norm in {str(aid) for aid in u.get('access_agents', [])}
                ]
                selected_access_users = st.multiselect(
                    "Users with Access", options=all_usernames, default=current_access_usernames,
                    help="Select users who should have access to this agent"
                )

                with st.expander("Access Matrix", expanded=False):
                    access_matrix_rows = []
                    for u in st.session_state['users_data']:
                        access_matrix_rows.append({
                            'Username': u['username'],
                            'Has Access': 'Yes' if agent_id_norm in {str(aid) for aid in u.get('access_agents', [])} else 'No'
                        })
                    matrix_df = pd.DataFrame(access_matrix_rows)
                    st.dataframe(matrix_df, width='stretch', height=300)

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    # Parse parameters JSON
                    try:
                        parsed_params = json.loads(params_raw) if params_raw.strip() else {}
                    except Exception as e:
                        st.error(f"Invalid Parameters JSON: {e}")
                        parsed_params = agent_obj.get('parameters', {})

                    # Update agent fields
                    agent_obj['name'] = a_name
                    agent_obj['certified'] = a_cert
                    agent_obj['expiration_date'] = a_exp.strftime('%Y-%m-%d')
                    agent_obj['business_unit'] = a_bu
                    agent_obj['owner'] = a_owner
                    agent_obj['purpose'] = a_purpose
                    agent_obj['instructions'] = a_instructions
                    agent_obj['prompt'] = a_prompt
                    agent_obj['parameters'] = parsed_params
                    agent_obj.setdefault('auth', {})['method'] = auth_method
                    agent_obj.setdefault('auth', {})['credentials'] = auth_credentials

                    # Update user access
                    update_user_access_for_agent(agent_obj.get('id'), selected_access_users, st.session_state['users_data'])

                    ok, err = save_agent_data(st.session_state['users_data'], st.session_state['agents_data'])
                    if ok:
                        st.success("Agent changes saved.")
                    else:
                        st.error(f"Failed to save: {err}")
        else:
            st.warning("Selected agent not found.")

if __name__ == "__main__":
    main()