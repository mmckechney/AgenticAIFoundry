import streamlit as st
import asyncio
import io
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Import the main functions from agenticai.py
# Handle missing dependencies gracefully for demo purposes
try:
    from agenticai import (
        code_interpreter,
        eval as ai_eval,
        redteam,
        agent_eval,
        connected_agent,
        ai_search_agent,
        delete_agent,
        process_message_reasoning
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ Some Azure AI dependencies are not installed: {e}")
    st.info("Running in demo mode with simulated responses.")
    DEPENDENCIES_AVAILABLE = False


# Configure Streamlit page
st.set_page_config(
    page_title="AgenticAI Foundry",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("AgenticAI Foundry 🤖")
    st.header("Code interpreter -> AI Evaluation -> RedTeam Agent -> Agent Evaluation -> Connected Agents -> Delete Agent")
    # https://github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo/blob/main/enterprise-streaming-agent.ipynb

    if st.button("Code Interpreter"):
        with st.spinner("Executing code interpreter..."):
            code_interpreter()
            st.write("Code interpreter executed successfully.")
        
    if st.button("AI Evaluation"):
        with st.spinner("Running AI evaluation..."):
            evalrs = ai_eval()
            st.write(evalrs)
    if st.button("RedTeam Agent"):
        with st.spinner("Running RedTeam agent..."):
            redteamrs = asyncio.run(redteam())
            st.write(redteamrs)
    if st.button("Agent Evaluation"):
        with st.spinner("Running agent evaluation..."):
            agent_evalrs = agent_eval()
            st.write(agent_evalrs)
    if st.button("Connected Agent"):
        with st.spinner("Connecting to agent..."):
            connected_agentrs = connected_agent()
            st.write(connected_agentrs)
    if st.button("Delete Agent"):
        with st.spinner("Deleting agent..."):
            delete_agentrs = delete_agent()
            st.write(delete_agentrs)

if __name__ == "__main__":
    main()