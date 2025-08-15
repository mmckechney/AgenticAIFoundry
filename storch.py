import asyncio
from concurrent.futures import thread
from datetime import datetime
import time
import os, json
import pandas as pd
from typing import Any, Callable, Set, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI, _client
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType, MessageRole, ListSortOrder, ToolDefinition, FilePurpose, FileSearchTool
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval
from azure.ai.agents.models import CodeInterpreterTool, FunctionTool, ToolSet
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
        "citations": [], # list of URLs extracted from messages/tool output
    "tool_outputs": [], # raw tool outputs if retrievable
    "search_results": [], # structured items extracted from tool outputs
    "steps_count": 0,
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
        instructions="You are a helpful AI agent. Answer only from the tools. please provide urls as citation [url] [url].",
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

    # Extract citations (URLs) from assistant/message texts
    def _extract_urls(text: str) -> List[str]:
        if not text:
            return []
        try:
            import re as _re
            # matches http/https URLs until whitespace or closing bracket/paren
            pattern = _re.compile(r"https?://[^\s\]\)]+", _re.IGNORECASE)
            return pattern.findall(text)
        except Exception:
            return []

    url_set: Set[str] = set()
    for m in result["messages"]:
        for url in _extract_urls(m.get("text", "")):
            url_set.add(url)
    for url in _extract_urls(result.get("assistant_text", "")):
        url_set.add(url)

    # Optionally: attempt to fetch tool call steps and capture outputs (best-effort)
    try:
        run_id = getattr(run, "id", None) or (run.get("id") if isinstance(run, dict) else None)
        if run_id and hasattr(project_client.agents.runs, 'list_steps'):
            steps = project_client.agents.runs.list_steps(thread_id=thread.id, run_id=run_id, order=ListSortOrder.ASCENDING)
            count_steps = 0
            for s in steps:
                count_steps += 1
                # Capture any visible text from step output/details
                text_bits: List[str] = []
                for attr in ("output", "result", "details", "content", "message"):
                    try:
                        v = getattr(s, attr, None)
                    except Exception:
                        v = None
                    if not v and isinstance(s, dict):
                        v = s.get(attr)
                    if v:
                        try:
                            if isinstance(v, (list, tuple)):
                                text_bits.extend([str(x) for x in v if x is not None])
                            elif isinstance(v, (dict,)):
                                text_bits.append(json.dumps(v))
                            else:
                                text_bits.append(str(v))
                        except Exception:
                            pass
                raw = "\n".join([b for b in text_bits if b])
                if raw:
                    result["tool_outputs"].append(raw)
                    for url in _extract_urls(raw):
                        url_set.add(url)

                    # Try to parse structured results from JSON-looking raw
                    def _try_json_parse(text: str):
                        try:
                            return json.loads(text)
                        except Exception:
                            return None

                    parsed = _try_json_parse(raw)
                    items: List[Dict[str, Any]] = []
                    if isinstance(parsed, dict):
                        items = [parsed]
                    elif isinstance(parsed, list):
                        items = [x for x in parsed if isinstance(x, (dict, str))]

                    def _as_result(obj) -> Optional[Dict[str, str]]:
                        try:
                            if isinstance(obj, str):
                                # Single URL string
                                if obj.startswith("http"):
                                    return {"title": obj, "url": obj, "snippet": ""}
                                return None
                            # Dict shape: look for common fields
                            title = obj.get("title") or obj.get("name") or obj.get("caption") or obj.get("source") or ""
                            url = obj.get("url") or obj.get("link") or obj.get("sourceUrl") or obj.get("href") or ""
                            snippet = obj.get("snippet") or obj.get("summary") or obj.get("content") or obj.get("chunk") or obj.get("text") or ""
                            if not url:
                                # Try pulling first URL-like token from any string fields
                                for k, v in obj.items():
                                    if isinstance(v, str):
                                        found = _extract_urls(v)
                                        if found:
                                            url = found[0]
                                            break
                            if not url and not title and not snippet:
                                return None
                            if not title:
                                title = url or "Result"
                            # Clamp snippet length
                            if isinstance(snippet, str) and len(snippet) > 400:
                                snippet = snippet[:400] + "…"
                            return {"title": str(title), "url": str(url), "snippet": str(snippet) if snippet is not None else ""}
                        except Exception:
                            return None

                    for it in items:
                        r = _as_result(it)
                        if r:
                            result["search_results"].append(r)
            result["steps_count"] = count_steps
    except Exception:
        pass

    result["citations"] = sorted(url_set)

    # Fetch and log all messages in the thread
    # messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    # for message in messages.data:
    #     print(f"Role: {message.role}, Content: {message.content}")
    #     returntxt += f"Role: {message.role}, Content: {message.content}\n"

    # Delete the agent
    project_client.agents.delete_agent(agent.id)
    project_client.agents.threads.delete(thread.id)
    print("Search agent Deleted agent and thread")


    return result

def code_interpreter(query: str) -> str:
    returntxt = ""
    code_interpreter = CodeInterpreterTool()
    # Use a fresh client instance for this operation
    with AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential()) as _client:
        agent = _client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="codeint-agent",
            instructions="You are a helpful agent",
            tools=code_interpreter.definitions,
        )
        print(f"Created agent, ID: {agent.id}")

        thread = _client.agents.threads.create()
        print(f"Created thread, ID: {thread.id}")

        message = _client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        print(f"Created message, ID: {message['id']}")

        run = _client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        messages = _client.agents.messages.list(thread_id=thread.id)
        for message in messages:
            print(f"Role: {message.role}, Content: {message.content}")
            returntxt += f"Role: {message.role}, Content: {message.content}\n"

        _client.agents.delete_agent(agent.id)
        _client.agents.threads.delete(thread.id)
        print("Code interpreter Deleted agent and thread")

    return returntxt

def ideation_agent(query: str) -> str:
    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    ideation_agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="ideationagent",
        instructions="""You are an Ideation Catalyst, a creative powerhouse for brainstorming sessions.
        
        Your role is to:
        - Generate creative and innovative ideas
        - Expand on initial concepts with fresh perspectives
        - Ask thought-provoking questions to stimulate creativity
        - Encourage out-of-the-box thinking
        - Build upon ideas to create new possibilities
        
        Structure your responses as:
        ## 💡 Creative Insights
        ### Initial Ideas
        - [List 3-5 innovative ideas]
        ### Expansion Opportunities
        - [Ways to expand or modify ideas]
        ### Provocative Questions
        - [Questions to spark further creativity]
        
        Be enthusiastic, creative, and push boundaries while remaining practical.
        """,
        #tools=... # tools to help the agent get stock prices
    )

    print(f"Created agent, ID: {ideation_agent.id}")

    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=query,
    )
    print(f"Created message, ID: {message['id']}")

    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=ideation_agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        print(f"Role: {message.role}, Content: {message.content}")
        returntxt += f"Role: {message.role}, Content: {message.content}\n"

    project_client.agents.delete_agent(ideation_agent.id)
    project_client.agents.threads.delete(thread.id)
    print("ideation_agent Deleted agent and thread")

    return returntxt

def business_agent(query: str) -> str:
    returntxt = ""

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )

    business_analyst = project_client.agents.create_agent(
        model=model_deployment_name,
        name="businessanalyst",
        instructions="""
        You are a Business Analyst specializing in market and financial analysis.
        
        Your role is to:
        - Analyze market potential and sizing
        - Evaluate revenue models and financial viability
        - Assess competitive landscape
        - Identify target customer segments
        - Evaluate business model feasibility
        
        Structure your responses as:
        ## 💼 Business Analysis
        ### Market Opportunity
        - Market size and growth potential
        - Target customer segments
        ### Revenue Model
        - Potential revenue streams
        - Pricing strategies
        ### Competitive Landscape
        - Key competitors and differentiation
        ### Financial Viability
        - Investment requirements and ROI projections
        
        Provide data-driven insights and realistic business assessments.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    print(f"Created agent, ID: {business_analyst.id}")

    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=query,
    )
    print(f"Created message, ID: {message['id']}")

    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=business_analyst.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        print(f"Role: {message.role}, Content: {message.content}")
        returntxt += f"Role: {message.role}, Content: {message.content}\n"

    project_client.agents.delete_agent(business_analyst.id)
    project_client.agents.threads.delete(thread.id)
    print("business_analyst Deleted agent and thread")

    return returntxt

# --- Configure available agents here (easy list/array) ---
# Add new steps by appending a dict with: id, label, fn, needs_query, is_async, returns_dict
AGENT_STEPS: List[Dict[str, Any]] = [
    {
        "id": "code_interpreter",
        "label": "Code Interpreter",
        "fn": code_interpreter,
        "needs_query": True,
        "is_async": False,
        "returns_dict": False,
    },
    {
        "id": "search_query_agent",
        "label": "AI Search Agent",
        "fn": search_query_agent,
        "needs_query": True,
        "is_async": False,
        "returns_dict": True,
    },
    {
        "id": "business_analyst",
        "label": "Business Analyst",
        "fn": business_agent,
        "needs_query": True,
        "is_async": False,
        "returns_dict": True,
    },
    {
        "id": "ideation_agent",
        "label": "Ideation Agent",
        "fn": ideation_agent,
        "needs_query": True,
        "is_async": False,
        "returns_dict": True,
    }
]

def main_orch():
    # Orchestration UI: choose agents, order them, and run the flow
    st.set_page_config(page_title="Agent Orchestrator", layout="wide")

    # --- Styles: fixed-height panels with internal scroll ---
    st.markdown(
        """
        <style>
        .orch-wrapper { height: 82vh; display: flex; gap: 16px; }
        .panel { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; background: #fff; }
        .builder { height: 1vh; overflow: hidden; display: flex; flex-direction: column; }
        .builder-body { flex: 1; overflow: auto; }
        .runner { height: 1vh; overflow: hidden; display: flex; flex-direction: column; }
        .runner-body { flex: 1; overflow: auto; }
        .seq-item { display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; border: 1px solid #f1f5f9; border-radius: 6px; margin-bottom: 6px; background: #fafafa; }
        .seq-item .name { font-weight: 600; }
        .seq-controls { display: flex; gap: 6px; }
        .log-card { border: 1px solid #eef2f7; border-radius: 6px; padding: 8px 10px; margin-bottom: 8px; background: #fcfdff; }
        .muted { color: #6b7280; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Define available steps (metadata) ---
    from inspect import iscoroutinefunction as _is_coro

    def _steps_catalog():
        # Build catalog from AGENT_STEPS list
        return {s["id"]: {k: s[k] for k in ("label","fn","needs_query","is_async","returns_dict")}
                for s in AGENT_STEPS}

    catalog = _steps_catalog()

    # --- Session State ---
    if "selected_steps" not in st.session_state:
        # Default to the requested order: code_interpreter, search_query_agent
        st.session_state.selected_steps = ["code_interpreter", "search_query_agent"]
    if "run_logs" not in st.session_state:
        st.session_state.run_logs = []  # list of dicts per step run

    # --- Layout ---
    col_left, col_right = st.columns([5, 7], gap="medium")

    with col_left:
        st.markdown("<div class='panel builder'>", unsafe_allow_html=True)
        st.subheader("Build Flow")
        st.caption("Choose steps, order them, then run. Steps with a dot need the flow input.")

        # Add step selector
        options = {v["label"]: k for k, v in catalog.items()}
        add_label = st.selectbox("Add a step", ["— Select —"] + list(options.keys()), index=0)
        if add_label != "— Select —":
            step_id = options[add_label]
            if step_id not in st.session_state.selected_steps:
                st.session_state.selected_steps.append(step_id)
                st.rerun()

        # Current sequence
        st.markdown("### Sequence")
        st.markdown("<div class='builder-body'>", unsafe_allow_html=True)
        if not st.session_state.selected_steps:
            st.info("No steps yet. Add from the dropdown above.")
        else:
            for idx, step_id in enumerate(st.session_state.selected_steps):
                meta = catalog.get(step_id, {"label": step_id, "needs_query": False})
                with st.container():
                    st.markdown("<div class='seq-item'>", unsafe_allow_html=True)
                    left_c, right_c = st.columns([8, 4])
                    with left_c:
                        dot = "• " if meta.get("needs_query") else ""
                        st.markdown(f"<span class='name'>{idx+1}. {dot}{meta['label']}</span>", unsafe_allow_html=True)
                    with right_c:
                        c1, c2, c3 = st.columns(3)
                        if c1.button("↑", key=f"up_{step_id}_{idx}"):
                            if idx > 0:
                                lst = st.session_state.selected_steps
                                lst[idx-1], lst[idx] = lst[idx], lst[idx-1]
                                st.rerun()
                        if c2.button("↓", key=f"down_{step_id}_{idx}"):
                            lst = st.session_state.selected_steps
                            if idx < len(lst)-1:
                                lst[idx+1], lst[idx] = lst[idx], lst[idx+1]
                                st.rerun()
                        if c3.button("Remove", key=f"rm_{step_id}_{idx}"):
                            st.session_state.selected_steps.pop(idx)
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        ccol1, ccol2 = st.columns(2)
        if ccol1.button("Clear Flow"):
            st.session_state.selected_steps = []
            st.rerun()
        if ccol2.button("Clear Logs"):
            st.session_state.run_logs = []
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='panel runner'>", unsafe_allow_html=True)
        st.subheader("Run Flow")
        flow_input = st.text_area("Flow input (passed to steps that need it)", height=100, placeholder="Enter a question or instruction…")
        run_now = st.button("Run Flow", type="primary")

        st.markdown("### Execution Log")
        st.markdown("<div class='runner-body'>", unsafe_allow_html=True)

        def _run_step(step_id: str, query: Optional[str]):
            meta = catalog.get(step_id)
            if not meta:
                return {"step": step_id, "status": "skipped", "error": "Unknown step"}
            fn = meta["fn"]
            needs_query = meta.get("needs_query", False)
            is_async = meta.get("is_async", False)
            started = time.time()
            try:
                if needs_query and not (query and query.strip()):
                    return {
                        "step": meta["label"],
                        "status": "skipped",
                        "error": "Missing flow input",
                        "elapsed_s": round(time.time() - started, 2),
                    }

                if is_async or _is_coro(fn):
                    out = asyncio.run(fn(query) if needs_query else fn())
                else:
                    out = fn(query) if needs_query else fn()

                elapsed = round(time.time() - started, 2)
                # Shape output
                disp = ""
                citations = []
                if isinstance(out, dict):
                    disp = out.get("assistant_text") or json.dumps(out)[:1200]
                    citations = out.get("citations", [])
                elif isinstance(out, str):
                    disp = out
                else:
                    disp = str(out) if out is not None else "(no output)"

                return {
                    "step": meta["label"],
                    "status": "done",
                    "elapsed_s": elapsed,
                    "output": disp,
                    "citations": citations,
                }
            except Exception as e:
                return {
                    "step": meta.get("label", step_id),
                    "status": "error",
                    "error": str(e),
                    "elapsed_s": round(time.time() - started, 2),
                }

        if run_now:
            st.session_state.run_logs = []
            for sid in st.session_state.selected_steps:
                log = _run_step(sid, flow_input)
                st.session_state.run_logs.append(log)
            st.rerun()

        # Render logs
        if not st.session_state.run_logs:
            st.caption("Run the flow to see logs here.")
        else:
            for i, log in enumerate(st.session_state.run_logs, start=1):
                with st.container():
                    st.markdown("<div class='log-card'>", unsafe_allow_html=True)
                    top_c1, top_c2, top_c3 = st.columns([6, 2, 2])
                    top_c1.markdown(f"**{i}. {log.get('step','Step')}**")
                    top_c2.metric("Status", log.get("status", "-"))
                    top_c3.metric("Time (s)", log.get("elapsed_s", 0))

                    if log.get("error"):
                        st.error(log["error"])
                    if log.get("output"):
                        st.write(log["output"])
                    cites = log.get("citations") or []
                    if cites:
                        with st.expander("Citations"):
                            for u in cites:
                                st.markdown(f"- [{u}]({u})")
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer hint
    st.markdown("\n<p class='muted'>Tip: Use ↑/↓ to reorder. Dotted steps need the flow input.</p>", unsafe_allow_html=True)


# Auto-run when executed via `streamlit run storch.py`
if __name__ == "__main__":
    main_orch()