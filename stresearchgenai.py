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

def normalize_token_usage(usage) -> dict:
    """Normalize various usage objects/dicts into a standard dict.
    Returns {'prompt_tokens', 'completion_tokens', 'total_tokens'} or {} if unavailable.
    """
    try:
        if not usage:
            return {}
        # If it's already a dict, use it directly
        if isinstance(usage, dict):
            d = usage
        else:
            # Attempt attribute access (e.g., ResponseUsage pydantic model)
            d = {}
            for name in ("prompt_tokens", "completion_tokens", "total_tokens", "input_tokens", "output_tokens"):
                val = getattr(usage, name, None)
                if val is not None:
                    d[name] = val

        prompt = int(d.get("prompt_tokens", d.get("input_tokens", 0)) or 0)
        completion = int(d.get("completion_tokens", d.get("output_tokens", 0)) or 0)
        total = int(d.get("total_tokens", prompt + completion) or 0)
        return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}
    except Exception:
        return {}

def get_chat_response_gpt5_response(query: str) -> str:
    returntxt = ""

    responseclient = AzureOpenAI(
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
        api_key= os.getenv("AZURE_OPENAI_KEY"),
        api_version="preview"
        )
    deployment = "gpt-5"

    # Some new parameters!  
    response = responseclient.responses.create(
        input=query,
        model=deployment,
        reasoning={
            "effort": "medium",
            "summary": "auto" # auto, concise, or detailed 
        },
        text={
            "verbosity": "low" # New with GPT-5 models
        }
    )

    # # Token usage details
    usage = normalize_token_usage(response.usage)

    # print("--------------------------------")
    # print("Output:")
    # print(output_text)
    returntxt = response.output_text

    return returntxt, usage

def _build_conversation_input(history: List[Dict[str, Any]], current_prompt: str, max_pairs: int = 6) -> str:
    """Build a simple conversation transcript string for the responses API.
    Includes the last N user/assistant message pairs plus the current prompt.
    """
    lines: List[str] = []
    # Take last max_pairs*2 messages from history
    recent = history[-max_pairs*2:]
    for m in recent:
        role = m.get("role", "user").capitalize()
        content = m.get("content", "")
        lines.append(f"{role}: {content}")
    lines.append(f"User: {current_prompt}")
    lines.append("Assistant:")
    return "\n".join(lines)


def research_main():
    st.set_page_config(page_title="Research Assistant", page_icon=":microscope:", layout="wide")

    # CSS to keep entire UI within viewport and scroll only inside panels
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
            height: 40vh; min-height: 300px;
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
        .right-panel { height: 2vh; overflow-y: auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 10px; }
        .metric { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px; padding: 6px; margin: 4px 0; text-align: center; }
        .section-title { font-size: 0.95em; margin: 4px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "total_usage" not in st.session_state:
        st.session_state.total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # Header
    st.markdown('<div class="header"><h3 style="margin:0; color:#1f2937;">🔬 Research Assistant</h3><p style="margin:2px 0 0 0; color:#6b7280; font-size:0.85em;">Ask science questions and follow up in a chat—summary on the left, stats on the right</p></div>', unsafe_allow_html=True)

    left, right = st.columns([5, 3], gap="medium")

    with left:
        st.markdown('<div class="section-title">💬 Conversation</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

        # Chat history display
        chat_html = '<div class="chat-container">'
        if st.session_state.chat_history:
            for m in st.session_state.chat_history[-40:]:
                role = m.get("role")
                role_class = 'user' if role == 'user' else 'assistant'
                role_label = 'You' if role == 'user' else 'AI'
                content = (
                    m.get("content", "")
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>")
                )
                chat_html += f'<div class="msg {role_class}"><strong>{role_label}:</strong> {content}</div>'
        else:
            chat_html += '<div style="color:#6b7280; text-align:center; padding:40px 10px;">Ask any science topic to begin.</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # Input
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        prompt = st.chat_input("Ask a science question…")
        clear = st.button("🗑️ Clear", key="clear_chat")
        if clear:
            st.session_state.chat_history = []
            st.session_state.total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            st.rerun()

        if prompt:
            ts = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({"role": "user", "content": prompt.strip(), "ts": ts})
            with st.spinner("Thinking…", show_time=True):
                convo_input = _build_conversation_input(st.session_state.chat_history, prompt.strip())
                response, usage = get_chat_response_gpt5_response(convo_input)
            # Append assistant message
            ts2 = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({"role": "assistant", "content": response, "ts": ts2, "usage": usage})
            # Update totals
            u = normalize_token_usage(usage)
            st.session_state.total_usage["prompt_tokens"] += u.get("prompt_tokens", 0)
            st.session_state.total_usage["completion_tokens"] += u.get("completion_tokens", 0)
            st.session_state.total_usage["total_tokens"] += u.get("total_tokens", 0)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">📊 Token Usage & Stats</div>', unsafe_allow_html=True)
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)

        totals = st.session_state.total_usage
        # Totals
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Total</div><div style="font-weight:700; color:#111827;">{totals.get("total_tokens", 0)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Prompt</div><div style="font-weight:700; color:#111827;">{totals.get("prompt_tokens", 0)}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Completion</div><div style="font-weight:700; color:#111827;">{totals.get("completion_tokens", 0)}</div></div>', unsafe_allow_html=True)

        # Recent usage
        last_usage = {}
        for m in reversed(st.session_state.chat_history):
            if m.get("role") == "assistant" and m.get("usage"):
                last_usage = normalize_token_usage(m.get("usage"))
                break
        st.markdown('<div class="section-title" style="margin-top:6px;">Last Response</div>', unsafe_allow_html=True)
        if last_usage:
            l1, l2, l3 = st.columns(3)
            l1.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Total</div><div style="font-weight:700; color:#111827;">{last_usage.get("total_tokens", 0)}</div></div>', unsafe_allow_html=True)
            l2.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Prompt</div><div style="font-weight:700; color:#111827;">{last_usage.get("prompt_tokens", 0)}</div></div>', unsafe_allow_html=True)
            l3.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Completion</div><div style="font-weight:700; color:#111827;">{last_usage.get("completion_tokens", 0)}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#6b7280;">No responses yet.</div>', unsafe_allow_html=True)

        # Conversation stats
        st.markdown('<div class="section-title" style="margin-top:6px;">Conversation</div>', unsafe_allow_html=True)
        total_msgs = len(st.session_state.chat_history)
        convos = total_msgs // 2
        s1, s2 = st.columns(2)
        s1.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Messages</div><div style="font-weight:700; color:#111827;">{total_msgs}</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="metric"><div style="font-size:0.8em; color:#6b7280;">Conversations</div><div style="font-weight:700; color:#111827;">{convos}</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    research_main()