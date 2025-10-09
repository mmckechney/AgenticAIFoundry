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


def analyze_contunder(file_url: str, analyzer_id: str = "prebuilt-documentAnalyzer") -> dict:
    """Call Azure Content Understanding analyzer using Python requests.

    Args:
        file_url: URL to the document that the analyzer should process.
        analyzer_id: Analyzer identifier (default: prebuilt-documentAnalyzer).

    Returns:
        Parsed JSON response from the service.
    """

    api_version = "2025-05-01-preview"
    endpoint = os.getenv("CONT_UNDER_ENDPOINT")
    subscription_key = os.getenv("CONT_UNDER_KEY")

    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
    if not subscription_key:
        raise ValueError("AZURE_OPENAI_KEY environment variable is not set")

    url = f"{endpoint.rstrip('/')}/contentunderstanding/analyzers/{analyzer_id}:analyze"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json",
    }
    payload = {"url": file_url}

    response = requests.post(
        url,
        params={"api-version": api_version},
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

def get_analyzer_result(
    analyze_response: dict,
    analyzer_id: str | None = None,
    poll_interval: float = 2.0,
    max_polls: int = 20,
) -> dict:
    """Fetch analyzer result using the request id returned by ``analyze_contunder``.

    Args:
        analyze_response: JSON response from ``analyze_contunder`` (must contain a result id).
        analyzer_id: Optional override if API requires analyzer id in future (reserved).
        poll_interval: Seconds to wait between status polls.
        max_polls: Maximum number of GET attempts before timing out.

    Returns:
        Analyzer result payload once status is ``Succeeded`` or ``Failed``.

    Raises:
        ValueError: If the endpoint/key/result id are missing.
        TimeoutError: If the analyzer does not complete within ``max_polls``.
        requests.HTTPError: Propagated for unexpected HTTP responses.
    """

    endpoint = os.getenv("CONT_UNDER_ENDPOINT")
    subscription_key = os.getenv("CONT_UNDER_KEY")
    api_version = "2025-05-01-preview"

    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
    if not subscription_key:
        raise ValueError("AZURE_OPENAI_KEY environment variable is not set")

    # Attempt to pull request identifier from common fields.
    result_id = (
        analyze_response.get("resultId")
        or analyze_response.get("analyzerResultId")
        or analyze_response.get("operationId")
        or analyze_response.get("id")
        or analyze_response.get("requestId")
    )
    if not result_id:
        raise ValueError("Unable to determine analyzer result id from response")

    url = f"{endpoint.rstrip('/')}/contentunderstanding/analyzerResults/{result_id}"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json",
    }

    terminal_statuses = {"succeeded", "failed", "completed"}
    in_progress_statuses = {"running", "notstarted", "queued", "pending"}

    # Give the service a moment before the first poll to reduce immediate RUNNING results.
    time.sleep(max(poll_interval, 0))

    for attempt in range(1, max_polls + 1):
        response = requests.get(
            url,
            params={"api-version": api_version},
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()

        # Some payloads surface status at the top level, others nest inside result/status
        status = (
            payload.get("status")
            or payload.get("result", {}).get("status")
            or ""
        ).strip().lower()

        if status in terminal_statuses:
            return payload

        if attempt == max_polls:
            break

        # Respect Retry-After header when provided, otherwise use poll_interval
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                sleep_seconds = float(retry_after)
            except ValueError:
                sleep_seconds = poll_interval
        else:
            sleep_seconds = poll_interval

        if status and status not in in_progress_statuses:
            # Unknown status – continue polling but log minimal delay
            sleep_seconds = max(1.0, sleep_seconds)

        time.sleep(sleep_seconds)

    raise TimeoutError(
        f"Analyzer result {result_id} did not complete after {max_polls} polls ({poll_interval * max_polls:.1f} seconds)."
    )
def main():
    st.set_page_config(page_title="Content Understanding Analyzer", page_icon="📄", layout="centered")
    st.title("Azure Content Understanding Analyzer")

    st.write(
        "Analyze a document accessible via URL using Azure Content Understanding. "
        "We'll submit the document, poll for the result, and display the structured response."
    )

    with st.sidebar:
        st.header("Configuration")
        analyzer_id = st.text_input("Analyzer ID", value="prebuilt-documentAnalyzer")
        poll_interval = st.number_input(
            "Poll Interval (seconds)", min_value=0.5, max_value=10.0, value=2.0, step=0.5
        )
        max_polls = st.number_input(
            "Max Poll Attempts", min_value=1, max_value=100, value=20, step=1
        )

    file_url = st.text_input(
        "Document URL",
        value="https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf", # "https://github.com/balakreshnan/AgenticAIFoundry/blob/main/pdfs/StateofAIReport-2025ONLINE.pdf",
        placeholder="https://example.com/sample.pdf",
    )
    run_button = st.button("Analyze Document", type="primary")

    if run_button:
        if not file_url.strip():
            st.warning("Please provide a document URL before running the analyzer.")
            return

        try:
            with st.spinner("Submitting document for analysis...", show_time=True):
                analyze_response = analyze_contunder(
                    file_url=file_url.strip(),
                    analyzer_id=analyzer_id.strip() or "prebuilt-documentAnalyzer",
                )

            st.success("Analysis request submitted successfully.")
            with st.expander("Raw Analyze Response", expanded=False):
                st.json(analyze_response)

            with st.spinner("Waiting for analyzer result...", show_time=True):
                result_payload = get_analyzer_result(
                    analyze_response=analyze_response,
                    analyzer_id=analyzer_id.strip() or None,
                    poll_interval=float(poll_interval),
                    max_polls=int(max_polls),
                )

            status = result_payload.get("status", "Unknown")
            status_lower = status.lower()
            if status_lower == "succeeded":
                st.success("Analyzer completed successfully.")
            elif status_lower == "failed":
                st.error("Analyzer reported a failure.")
            else:
                st.info(f"Analyzer status: {status}")

            st.subheader("Analyzer Result")
            st.json(result_payload)

            st.download_button(
                label="Download Result JSON",
                data=json.dumps(result_payload, indent=2),
                file_name="analyzer_result.json",
                mime="application/json",
            )

        except TimeoutError as timeout_err:
            st.error(str(timeout_err))
        except requests.HTTPError as http_err:
            resp = http_err.response
            if resp is not None:
                st.error(f"HTTP error {resp.status_code}: {resp.text}")
            else:
                st.error(f"HTTP error: {http_err}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()
