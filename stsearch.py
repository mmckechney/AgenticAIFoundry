import asyncio
from concurrent.futures import thread
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

# Configure telemetry only if available (don't exit in Streamlit context)
if connection_string:
    configure_azure_monitor(connection_string=connection_string)  # enable telemetry collection
else:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")


from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def search_query_agent(query: str) -> Dict[str, Any]:
    """Run a search-enabled agent and return structured details for UI rendering."""
    result: Dict[str, Any] = {
        "assistant_text": "",
        "messages": [],  # list of {role, text}
        "agent_id": None,
        "thread_id": None,
        "run_status": None,
    "usage": None,   # {prompt_tokens, completion_tokens, total_tokens, is_estimated}
    }

    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        # api_version="latest",
    )
    # Define the Azure AI Search connection ID and index name
    azure_ai_conn_id = "vecdb"
    index_name = "constructionrfpdocs1"

    # Initialize the Azure AI Search tool
    ai_search = AzureAISearchTool(
        index_connection_id=azure_ai_conn_id,
        index_name=index_name,
        query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,  # Use SIMPLE query type
        top_k=5,  # Retrieve the top 3 results
        filter="",  # Optional filter for search results
    )
    # Define the model deployment name
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    # Create an agent with the Azure AI Search tool
    agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="AISearch-agent",
        instructions="You are a helpful AI agent, please provide urls as citation [url] [url].",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
    print(f"Created agent, ID: {agent.id}")
    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")
    result["agent_id"] = agent.id
    result["thread_id"] = thread.id

    # Send a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=query,
    )
    print(f"Created message, ID: {message['id']}")

    # Create and process a run with the specified thread and agent
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")
    result["run_status"] = str(run.status)

    # Check if the run failed
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch and log all messages in the thread
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    print(str(messages))

    def _extract_text_parts(content) -> str:
        parts: List[str] = []
        try:
            for part in (content or []):
                # Dict-like shapes
                if isinstance(part, dict):
                    txt = None
                    if 'text' in part:
                        t = part.get('text')
                        if isinstance(t, dict):
                            txt = t.get('value') or t.get('content')
                        else:
                            txt = t
                    elif 'value' in part:
                        txt = part.get('value')
                    if txt:
                        parts.append(str(txt))
                else:
                    # Object-like shapes
                    txt = None
                    if hasattr(part, 'text'):
                        t = getattr(part, 'text')
                        if isinstance(t, str):
                            txt = t
                        elif hasattr(t, 'value'):
                            txt = getattr(t, 'value', None)
                        elif hasattr(t, 'content'):
                            txt = getattr(t, 'content', None)
                    elif hasattr(part, 'value'):
                        txt = getattr(part, 'value')
                    if txt:
                        parts.append(str(txt))
        except Exception:
            pass
        return "\n".join([p for p in parts if p])

    # Iterate items directly (avoids PageIterator constructor error)
    last_assistant_text = ""
    for item in messages:
        try:
            role = getattr(item, 'role', None) or (item.get('role') if isinstance(item, dict) else None)
            content = getattr(item, 'content', None) or (item.get('content') if isinstance(item, dict) else None)
            text_val = _extract_text_parts(content)
            result["messages"].append({"role": str(role), "text": text_val})
            if str(role).lower() == "assistant" and text_val:
                last_assistant_text = text_val
        except Exception:
            result["messages"].append({"role": "unknown", "text": str(item)})
    result["assistant_text"] = last_assistant_text or (result["messages"][-1]["text"] if result["messages"] else "")

    # Try to fetch token usage from run details; fall back to an estimate
    def _to_int(x):
        try:
            return int(x)
        except Exception:
            return 0

    usage = None
    try:
        run_id = getattr(run, "id", None) or (run.get("id") if isinstance(run, dict) else None)
        if run_id:
            run_detail = project_client.agents.runs.get(thread_id=thread.id, run_id=run_id)
            ru = getattr(run_detail, "usage", None) or (run_detail.get("usage") if isinstance(run_detail, dict) else None)
            if ru:
                # Support multiple shapes
                prompt = _to_int(getattr(ru, "prompt_tokens", None) if not isinstance(ru, dict) else ru.get("prompt_tokens"))
                completion = _to_int(getattr(ru, "completion_tokens", None) if not isinstance(ru, dict) else ru.get("completion_tokens"))
                input_tokens = _to_int(getattr(ru, "input_tokens", None) if not isinstance(ru, dict) else ru.get("input_tokens"))
                output_tokens = _to_int(getattr(ru, "output_tokens", None) if not isinstance(ru, dict) else ru.get("output_tokens"))
                total = _to_int(getattr(ru, "total_tokens", None) if not isinstance(ru, dict) else ru.get("total_tokens"))

                prompt_tokens = prompt if prompt else input_tokens
                completion_tokens = completion if completion else output_tokens
                if not total:
                    total = (prompt_tokens or 0) + (completion_tokens or 0)
                usage = {
                    "prompt_tokens": prompt_tokens or 0,
                    "completion_tokens": completion_tokens or 0,
                    "total_tokens": total or 0,
                    "is_estimated": False,
                }
    except Exception:
        usage = None

    if not usage:
        # Estimate tokens if actual usage isn't available
        def estimate_tokens(text: str) -> int:
            if not text:
                return 0
            # Roughly 4 chars/token; clamp at >= 1 for non-empty text
            return max(1, len(text) // 4)

        prompt_tokens_est = estimate_tokens(query)
        completion_tokens_est = estimate_tokens(result["assistant_text"]) if result["assistant_text"] else 0
        usage = {
            "prompt_tokens": prompt_tokens_est,
            "completion_tokens": completion_tokens_est,
            "total_tokens": prompt_tokens_est + completion_tokens_est,
            "is_estimated": True,
        }

    result["usage"] = usage

    # Fetch and log all messages in the thread
    # messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    # for message in messages.data:
    #     print(f"Role: {message.role}, Content: {message.content}")
    #     returntxt += f"Role: {message.role}, Content: {message.content}\n"

    # Delete the agent
    project_client.agents.delete_agent(agent.id)
    project_client.agents.threads.delete(thread.id)
    print("Deleted agent and thread")


    return result
def main_screen():
    st.set_page_config(page_title="AI Search Assistant", page_icon=":mag:", layout="wide")
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 0.3rem;
            padding-bottom: 0.3rem;
            max-width: 100%;
            height: 100vh;
            max-height: 100vh;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            border: 1px solid #c7d2fe;
            border-radius: 8px;
            padding: 6px 10px;
            margin-bottom: 6px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        }
        .chat-wrapper { display: flex; flex-direction: column; height: 1vh; }
        .chat-container {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 8px 10px;
            overflow-y: auto; overflow-x: hidden;
            height: 30vh; min-height: 400px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.03);
        }
        .input-container {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 6px 10px 2px 10px;
            margin-top: 6px;
        }
        .msg { margin: 6px 0; padding: 8px; border-radius: 8px; font-size: 0.9em; }
        .user { background: #ecfeff; border-left: 4px solid #06b6d4; }
        .assistant { background: #f3f4f6; border-left: 4px solid #6b7280; }
        .agent-panel { height: 1vh; overflow-y: auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 10px; }
        .metric { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px; padding: 6px; margin: 4px 0; text-align: center; }
        .section-title { font-size: 0.95em; margin: 4px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list of {role, content, ts}
    if "last_agent_details" not in st.session_state:
        st.session_state.last_agent_details = None

    # Header
    st.markdown('<div class="header"><h3 style="margin:0; color:#1f2937;">🔎 AI Search Assistant</h3><p style="margin:2px 0 0 0; color:#6b7280; font-size:0.85em;">Business-grade answers powered by Azure AI Search + Agents</p></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 3], gap="medium")

    with col_left:
        st.markdown('<div class="section-title">💬 Conversation</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        # Chat history
        chat_html = '<div class="chat-container">'
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history[-30:]:
                role_class = 'user' if msg["role"] == 'user' else 'assistant'
                role_label = 'You' if msg["role"] == 'user' else 'AI'
                safe = (
                    msg["content"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>")
                )
                chat_html += f'<div class="msg {role_class}"><strong>{role_label}:</strong> {safe}</div>'
        else:
            chat_html += '<div style="color:#6b7280; text-align:center; padding:40px 10px;">Ask a question to get started.</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # Input
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        prompt = st.chat_input("show me details for railcar in virginia railway express rfp?")
        clear = st.button("🗑️ Clear", key="clear_chat")
        if clear:
            st.session_state.chat_history = []
            st.session_state.last_agent_details = None
            st.rerun()

        if prompt:
            from datetime import datetime
            st.session_state.chat_history.append({"role": "user", "content": prompt.strip(), "ts": datetime.now().strftime("%H:%M:%S")})
            with st.spinner("Querying agent…", show_time=True):
                details = search_query_agent(prompt.strip())
            assistant_text = details.get("assistant_text", "") or "(No response)"
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_text, "ts": datetime.now().strftime("%H:%M:%S")})
            st.session_state.last_agent_details = details
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)  # close input-container
        st.markdown('</div>', unsafe_allow_html=True)  # close chat-wrapper

    with col_right:
        st.markdown('<div class="section-title">🧠 Agent Output</div>', unsafe_allow_html=True)
        st.markdown('<div class="agent-panel">', unsafe_allow_html=True)
        details = st.session_state.last_agent_details
        if not details:
            st.markdown('<div style="color:#6b7280;">Run a query to see agent details.</div>', unsafe_allow_html=True)
        else:
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Run</div><div style="font-weight:700; color:#111827;">{details.get("run_status", "-")}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Agent</div><div style="font-weight:700; color:#111827;">{(details.get("agent_id") or "-")[:8]}…</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Thread</div><div style="font-weight:700; color:#111827;">{(details.get("thread_id") or "-")[:8]}…</div></div>', unsafe_allow_html=True)

            # Token Usage
            usage = details.get("usage") or {}
            label = "Estimated" if usage.get("is_estimated") else "Actual"
            st.markdown('<div class="section-title" style="margin-top:6px;">Token Usage</div>', unsafe_allow_html=True)
            u1, u2, u3 = st.columns(3)
            u1.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Total ({label})</div><div style="font-weight:700; color:#111827;">{usage.get("total_tokens", 0)}</div></div>', unsafe_allow_html=True)
            u2.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Prompt</div><div style="font-weight:700; color:#111827;">{usage.get("prompt_tokens", 0)}</div></div>', unsafe_allow_html=True)
            u3.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Completion</div><div style="font-weight:700; color:#111827;">{usage.get("completion_tokens", 0)}</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title" style="margin-top:6px;">Messages</div>', unsafe_allow_html=True)
            msgs = details.get("messages", [])
            if msgs:
                for m in msgs:
                    role = m.get("role", "-")
                    txt = (m.get("text") or "").strip()
                    if not txt:
                        continue
                    st.markdown(f"**{role.capitalize()}**\n\n{txt}")
            else:
                st.markdown("(No messages)")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    # Run as Streamlit app: `streamlit run stsearch.py`
    main_screen()