import streamlit as st
import io
import contextlib
import json
import os
from datetime import datetime, UTC

# Import agent functions from stcondemo.py
from stcondemo import single_agent, connected_agent


st.set_page_config(page_title="Agent Demo (Single vs Multi)", layout="wide")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
	st.session_state.chat_history = []  # list of {role, content, timestamp}
if "runs" not in st.session_state:
	st.session_state.runs = []  # list of run dicts with summary, tools, mode, raw
if "last_mode" not in st.session_state:
	st.session_state.last_mode = "Single Agent"

from azure.monitor.opentelemetry import configure_azure_monitor
# connection_string = project_client.telemetry.get_application_insights_connection_string()
connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

st.title("Agent Chat Demo: Single vs Connected (Multi) Agents")
st.caption("Use Azure AI Foundry agents via single local tools or a connected multi-agent orchestration.")

with st.sidebar:
	st.header("Configuration")
	mode = st.radio(
		"Agent Mode",
		["Single Agent", "Multi Agent"],
		index=0 if st.session_state.last_mode == "Single Agent" else 1,
		help="Choose whether to use the single agent with function/MCP tools or the multi (connected) agent orchestration.",
	)
	st.session_state.last_mode = mode
	if st.button("Clear Chat / Reset", type="secondary"):
		st.session_state.chat_history.clear()
		st.session_state.runs.clear()
		st.rerun()
	st.markdown("---")
	st.markdown("Environment variables must be set (MODEL_DEPLOYMENT_NAME, PROJECT_ENDPOINT, etc.).")

# --- Helper Functions ---
def _truncate(txt: str, limit: int = 1200):
	if txt is None:
		return ""
	t = str(txt)
	return t if len(t) <= limit else t[: limit - 3] + "..."

def _render_chat_history(container):
	for msg in st.session_state.chat_history:
		role = msg["role"]
		content = msg["content"]
		timestamp = msg.get("timestamp")
		label = f"**{role.capitalize()}**" + (f" · {timestamp}" if timestamp else "")
		container.markdown(label)
		container.markdown(content)
		container.markdown("---")

def _parse_connected_stdout(stdout_lines):
	"""Parse stdout from connected_agent() to extract tool / agent outputs.
	Returns list of dicts: {type, agent_name, output, raw, tool_call_id}
	"""
	results = []
	current = {}
	for line in stdout_lines:
		line = line.strip()
		if line.startswith("Tool call:"):
			# commit previous
			if current:
				results.append(current)
			# Start new
			try:
				parts = line.split(",")
				name_part = parts[0].split(":", 1)[1].strip()
				current = {"type": "tool_call", "agent_name": name_part, "raw": line}
			except Exception:
				current = {"type": "tool_call", "agent_name": "unknown", "raw": line}
		elif "Connected Input(Name of Agent):" in line:
			agent_name = line.split(":", 1)[1].strip()
			current.setdefault("agent_name", agent_name)
			current.setdefault("raw", "")
			current["raw"] += "\n" + line
		elif line.startswith("Connected Output:"):
			output = line.split(":", 1)[1].strip()
			current["output"] = output
			current.setdefault("raw", "")
			current["raw"] += "\n" + line
		elif line.startswith("Run status:") or line.startswith("Created agent"):
			# treat as log
			pass
		else:
			# other lines ignored or appended
			pass
	if current:
		results.append(current)
	return results

def run_single_agent(user_text: str):
	result = single_agent(user_text)
	# steps -> tool calls
	tool_events = []
	for step in result.get("steps", []):
		for tc in step.get("tool_calls", []):
			tool_events.append({
				"name": tc.get("name"),
				"arguments": tc.get("arguments"),
				"output": tc.get("output"),
				"step_id": step.get("id"),
				"status": step.get("status"),
			})
	run_record = {
		"mode": "Single Agent",
		"summary": result.get("summary"),
		"details": result.get("details"),
		"tools": tool_events,
		"raw": result,
	"token_usage": result.get("token_usage"),
		"timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
	}
	st.session_state.runs.append(run_record)
	return run_record

def run_multi_agent(user_text: str):
	buffer = io.StringIO()
	with contextlib.redirect_stdout(buffer):
		result_obj = connected_agent(user_text)
	stdout_lines = buffer.getvalue().splitlines()
	tool_events = _parse_connected_stdout(stdout_lines)
	if isinstance(result_obj, dict):
		summary_text = result_obj.get("summary")
		token_usage = result_obj.get("token_usage")
		status = result_obj.get("status")
	else:  # backward compatibility if function returns string
		summary_text = result_obj
		token_usage = None
		status = None
	run_record = {
		"mode": "Multi Agent",
		"summary": summary_text or "(no response)",
		"details": "\n".join(stdout_lines[-400:]),  # keep tail
		"tools": tool_events,
		"raw": {"stdout": stdout_lines, "summary": summary_text},
		"token_usage": token_usage,
		"status": status,
		"timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
	}
	st.session_state.runs.append(run_record)
	return run_record

def ui_main():
	# --- Layout ---
	col_left, col_right = st.columns([0.55, 0.45], gap="medium")

	with col_left:
		st.subheader("Summaries & Chat History")
		summary_container = st.container(height=200, border=True)
		history_container = st.container(height=300, border=True)

	with col_right:
		st.subheader("Tools & Agent Outputs")
		tools_container = st.container(height=520, border=True)

	# --- Chat Input ---
	user_prompt = st.chat_input("Ask a question (weather, stocks, docs, RFP, sustainability)...")

	if user_prompt:
		# Add user message
		st.session_state.chat_history.append({
			"role": "user",
			"content": user_prompt,
			"timestamp": datetime.now(UTC).strftime("%H:%M:%S"),
		})
		# Execute agent
		if mode == "Single Agent":
			with tracer.start_as_current_span("SingleAgentExecution"):
				run_record = run_single_agent(user_prompt)
			
		else:
			with tracer.start_as_current_span("MultiAgentExecution"):
				run_record = run_multi_agent(user_prompt)
				
		# Add assistant summary to chat history
		st.session_state.chat_history.append({
			"role": "assistant",
			"content": run_record.get("summary", "(no summary)"),
			"timestamp": datetime.now(UTC).strftime("%H:%M:%S"),
		})
		st.rerun()

	# --- Render Left Column ---
	with summary_container:
		if st.session_state.runs:
			latest = st.session_state.runs[-1]
			st.markdown(f"**Latest Mode:** {latest['mode']}  ")
			st.markdown(f"**Summary:** {_truncate(latest.get('summary'))}")
			tu = latest.get("token_usage")
			if tu:
				st.markdown(
					f"**Token Usage:** Prompt={tu.get('prompt_tokens','?')} · Completion={tu.get('completion_tokens','?')} · Total={tu.get('total_tokens','?')}"
				)
			else:
				st.markdown("**Token Usage:** N/A")
		else:
			st.info("No runs yet. Ask a question below.")

	with history_container:
		_render_chat_history(history_container)

	# --- Render Right Column ---
	with tools_container:
		if not st.session_state.runs:
			st.write("No tool activity yet.")
		else:
			latest = st.session_state.runs[-1]
			tools = latest.get("tools", [])
			# Moved Run Logs here from summary section
			if latest.get("details"):
				with st.expander("Run Logs (tail)", expanded=False):
					st.code(_truncate(latest.get("details"), 8000), language="text")
			if not tools:
				st.write("No tool outputs captured for this run.")
			for idx, t in enumerate(tools, start=1):
				name = t.get("name") or t.get("agent_name") or "(unknown)"
				label = f"{idx}. {name}"
				with st.expander(label, expanded=False):
					st.markdown(f"**Step:** {t.get('step_id','-')}  ")
					if t.get("arguments"):
						st.code(_truncate(t.get("arguments"), 500), language="json")
					output = t.get("output") or t.get("raw") or "(no output)"
					st.markdown("**Output:**")
					st.code(_truncate(output, 4000), language="text")
			if latest["mode"] == "Multi Agent":
				st.caption("Parsed from stdout of connected agent run.")

	st.markdown("---")
	st.caption("Chat input stays visible below. Scroll containers independently to review summaries, history, and tool outputs.")

if __name__ == "__main__":
    ui_main()