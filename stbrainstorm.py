import asyncio
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
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini
WHISPER_DEPLOYMENT_NAME = "whisper"
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" 

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

if not connection_string:
    print("Application Insights is not enabled. Enable by going to Tracing in your Azure AI Foundry project.")
    exit()

configure_azure_monitor(connection_string=connection_string) #enable telemetry collection


from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def connected_agent_brainstorm(query: str) -> str:
    returntxt = ""
    #https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/connected-agents?pivots=python

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
        # api_version="latest",
    )
    ideation_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
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
    connected_agent_name = "ideationagent"
    ideation_connected_agent = ConnectedAgentTool(
        id=ideation_agent.id, name=connected_agent_name, description="Creative ideation and innovation catalyst"
    )

    inquiry_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="inquiryagent",
        instructions="""You are an Inquiry Specialist, focused on asking the right questions to uncover insights.
        
        Your role is to:
        - Ask strategic follow-up questions
        - Probe deeper into assumptions and ideas
        - Uncover hidden opportunities and challenges
        - Challenge thinking to strengthen concepts
        - Guide discovery through targeted questioning
        
        Structure your responses as:
        ## ❓ Strategic Inquiry
        ### Key Questions to Explore
        - [5-7 strategic questions]
        ### Assumptions to Validate
        - [Critical assumptions that need testing]
        ### Areas for Deep Dive
        - [Topics requiring further investigation]
        
        Focus on questions that lead to actionable insights and better understanding..
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "inquiryagent"
    inquiry_connected_agent = ConnectedAgentTool(
        id=inquiry_agent.id, name=connected_agent_name, description="Strategic questioning and deep analysis specialist"
    )
    #create AI Search tool
    # Define the Azure AI Search connection ID and index name
    business_analyst = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
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
    connected_agent_name = "businessanalyst"
    business_connected_agent = ConnectedAgentTool(
        id=business_analyst.id, name=connected_agent_name, description="Market and financial analysis expert"
    )

    tech_advisor = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="techadvisor",
        instructions="""
        You are a Technology Advisor focused on emerging technologies and implementation.
        
        Your role is to:
        - Recommend relevant emerging technologies
        - Assess technical feasibility
        - Identify technology trends and opportunities
        - Suggest implementation approaches
        - Evaluate technical risks and mitigation strategies
        
        Structure your responses as:
        ## 🚀 Technology Recommendations
        ### Emerging Technologies
        - [Relevant cutting-edge technologies]
        ### Implementation Approach
        - [Technical architecture and approach]
        ### Technology Stack
        - [Recommended tools and platforms]
        ### Innovation Opportunities
        - [Ways to leverage technology for competitive advantage]
        
        Focus on practical, market-ready technology solutions.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "techadvisor"
    techadv_connected_agent = ConnectedAgentTool(
        id=tech_advisor.id, name=connected_agent_name, description="Technology trends and implementation expert"
    )

    strategic_analyst = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="strategicanalyst",
        instructions="""
        You are a Strategic Analyst specializing in comprehensive strategic analysis.
        
        Your role is to:
        - Conduct SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
        - Perform PESTEL analysis (Political, Economic, Social, Technological, Environmental, Legal)
        - Identify strategic opportunities and risks
        - Assess market positioning
        - Evaluate strategic alternatives
        
        Structure your responses as:
        ## 📊 Strategic Analysis
        ### SWOT Analysis
        - **Strengths**: [Internal advantages]
        - **Weaknesses**: [Internal challenges]
        - **Opportunities**: [External possibilities]
        - **Threats**: [External risks]
        ### PESTEL Analysis
        - **Political**: [Political factors]
        - **Economic**: [Economic conditions]
        - **Social**: [Social trends]
        - **Technological**: [Technology impact]
        - **Environmental**: [Environmental considerations]
        - **Legal**: [Legal/regulatory factors]
        ### Strategic Recommendations
        - [Key strategic priorities and actions]
        
        Provide comprehensive analysis with actionable strategic insights.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "strategicanalyst"
    strategic_connected_agent = ConnectedAgentTool(
        id=strategic_analyst.id, name=connected_agent_name, description="SWOT, PESTEL, and strategic analysis expert"
    )

    resource_planner = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="ResourcePlanner",
        instructions="""
        You are a Resource Planner focused on practical implementation planning.
        
        Your role is to:
        - Plan resource requirements (human, financial, technical)
        - Create realistic project timelines
        - Estimate costs and budgets
        - Identify critical dependencies
        - Suggest team structure and skills needed
        
        Structure your responses as:
        ## 📋 Resource Planning
        ### Team Requirements
        - [Roles and skills needed]
        ### Timeline & Milestones
        - [Project phases and key milestones]
        ### Budget Estimation
        - [Cost breakdown and financial requirements]
        ### Critical Dependencies
        - [Key dependencies and risk factors]
        ### Implementation Roadmap
        - [Step-by-step execution plan]
        
        Focus on realistic, actionable planning with clear deliverables.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "ResourcePlanner"
    resource_planner_connected_agent = ConnectedAgentTool(
        id=resource_planner.id, name=connected_agent_name, description="Resource allocation and project planning expert"
    )

    success_metrics_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SuccessMetricsAgent",
        instructions="""
        You are a Success Metrics Expert focused on defining and measuring success.
        
        Your role is to:
        - Define key performance indicators (KPIs)
        - Create measurement frameworks
        - Establish success criteria
        - Design monitoring and evaluation systems
        - Recommend analytics and tracking tools
        
        Structure your responses as:
        ## 🎯 Success Metrics Framework
        ### Key Performance Indicators
        - [Primary KPIs and metrics]
        ### Success Criteria
        - [Clear success definitions]
        ### Measurement Framework
        - [How to track and measure progress]
        ### Monitoring Tools
        - [Recommended analytics and tracking tools]
        ### Review & Optimization
        - [Regular review processes and optimization approaches]
        
        Provide measurable, actionable metrics that drive results.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "SuccessMetricsAgent"
    success_metrics_connected_agent = ConnectedAgentTool(
        id=success_metrics_agent.id, name=connected_agent_name, description="KPI definition and success measurement expert"
    )

    techarch_metrics_agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="TechArchMetricsAgent",
        instructions="""
        You are a Cloud Technical Architect specializing in Azure PaaS services and AI-first architectures.
        
        Your role is to:
        - Design scalable, secure Azure cloud architectures using PaaS services
        - Implement AI-first design principles and patterns
        - Apply Security by Design and Zero Trust principles
        - Create comprehensive technical documentation
        - Design system integrations and data flows
        - Recommend Azure AI and cognitive services integration
        
        Structure your responses as:
        ## 🏗️ Technical Architecture Design
        ### Azure Services Recommendation
        - [Core Azure PaaS services for the solution]
        ### Architecture Patterns
        - [Recommended architectural patterns and designs]
        ### Mermaid Architecture Diagram
        ```mermaid
        [Include detailed architecture diagram showing components, data flows, and integrations]
        ```
        ### Security Architecture
        - [Security by Design principles and Zero Trust implementation]
        ### AI Integration Strategy
        - [Azure AI services integration and AI-first design patterns]
        ### Implementation Roadmap
        - [Technical implementation phases and milestones]
        ### Performance & Scalability
        - [Scalability patterns and performance optimization strategies]
        
        Always include Mermaid diagrams to visualize the architecture and provide clear technical implementation guidance.
        """,
        #tools=... # tools to help the agent get stock prices
    )
    connected_agent_name = "TechArchMetricsAgent"
    techarch_metrics_connected_agent = ConnectedAgentTool(
        id=techarch_metrics_agent.id, name=connected_agent_name, description="Azure cloud architecture and AI-first design expert"
    )
    # Create an agent
    # Extract subscription and resource group from the project scope
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]

    # File search agent
    # Define the path to the file to be uploaded
    file_path = "./papers/ssrn-4072178.pdf"

    # Upload the file
    file = project_client.agents.files.upload_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create a vector store with the uploaded file
    # vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="suspaperstore")
    vector_store = project_client.agents.vector_stores.create_and_poll(file_ids=[file.id], name="suspaperstore")
    print(f"Created vector store, vector store ID: {vector_store.id}")
    # Create a file search tool
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    # Create an agent with the file search tool
    Sustainablityagent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="Sustainabilitypaperagent",  # Name of the agent
        instructions="You are a helpful agent and can search information from uploaded files",  # Instructions for the agent
        tools=file_search.definitions,  # Tools available to the agent
        tool_resources=file_search.resources,  # Resources for the tools
    )
    # print(f"Created agent, ID: {agent.id}")
    sustaibilityconnectedagentname = "Sustainabilitypaperagent"
    sustainability_connected_agent = ConnectedAgentTool(
        id=Sustainablityagent.id, name=sustaibilityconnectedagentname, description="Summarize the content of the uploaded files and answer questions about it"
    )

    # Orchestrate the connected agent with the main agent
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="PresalesAgent",
        instructions="""
        You are a Presales Solution Architect and specialist. Use the provided tools to answer the user's questions comprehensively.
        Be postive and professional in your responses. Provide detailed and structured answers.
        Here are the list of Agents to involve and get response from all
        Ideation Agent: Creative ideation and innovation catalyst
        Inquiry Agent: In-depth research and inquiry specialist
        Business Analyst: Business analysis and strategy expert
        Technology Advisor: Technology guidance and advisory specialist
        Strategic Analyst: Strategic planning and analysis expert
        Resource Planner: Resource management and planning specialist
        Success Metrics Expert: Success metrics and KPIs specialist
        Technical Architect: Technical architecture and design expert

        Summarize all the results and also provide architecture diagram in Mermaid format.
        Also provide the Architecture pro's and con's.        
        """,
        # tools=list(unique_tools.values()), #search_connected_agent.definitions,  # Attach the connected agents
        tools=[
            ideation_connected_agent.definitions[0],
            inquiry_connected_agent.definitions[0],
            business_connected_agent.definitions[0],
            techadv_connected_agent.definitions[0],
            strategic_connected_agent.definitions[0],           
            # sustainability_connected_agent.definitions[0],
            resource_planner_connected_agent.definitions[0],
            success_metrics_connected_agent.definitions[0],
            techarch_metrics_connected_agent.definitions[0],
        ]
    )

    print(f"Created agent, ID: {agent.id}")
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        # content="What is the stock price of Microsoft?",
        content=query,
    )
    print(f"Created message, ID: {message.id}")
    # Create and process Agent run in thread with tools
    # run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    # print(f"Run finished with status: {run.status}")
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    # Poll the run status until it is completed or requires action
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                print(f"Tool call: {tool_call.name}, ID: {tool_call.id}")
            #     if tool_call.name == "fetch_weather":
            #         output = fetch_weather("New York")
            #         tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
            # project_client.agents.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

    print(f"Run completed with status: {run.status}")
    # print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Capture token usage information
    token_usage = {}
    if hasattr(run, 'usage') and run.usage:
        token_usage = {
            'prompt_tokens': getattr(run.usage, 'prompt_tokens', 0),
            'completion_tokens': getattr(run.usage, 'completion_tokens', 0),
            'total_tokens': getattr(run.usage, 'total_tokens', 0)
        }
        print(f"Token usage - Prompt: {token_usage['prompt_tokens']}, Completion: {token_usage['completion_tokens']}, Total: {token_usage['total_tokens']}")
    else:
        # Try to get usage from run steps if not available in run object
        total_prompt_tokens = 0
        total_completion_tokens = 0
        run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            if hasattr(step, 'usage') and step.usage:
                total_prompt_tokens += getattr(step.usage, 'prompt_tokens', 0)
                total_completion_tokens += getattr(step.usage, 'completion_tokens', 0)
        
        token_usage = {
            'prompt_tokens': total_prompt_tokens,
            'completion_tokens': total_completion_tokens,
            'total_tokens': total_prompt_tokens + total_completion_tokens
        }
        print(f"Token usage from steps - Prompt: {token_usage['prompt_tokens']}, Completion: {token_usage['completion_tokens']}, Total: {token_usage['total_tokens']}")

    # Fetch run steps to get the details of the agent run
    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
    
    # Parse individual agent outputs
    agent_outputs = parse_agent_outputs(run_steps)
    
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                connected_agent = call.get("connected_agent", {})
                if connected_agent:
                    print(f"    Connected Input(Name of Agent): {connected_agent.get('name')}")
                    print(f"    Connected Output: {connected_agent.get('output')}")

        print()  # add an extra newline between steps

    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        if message.role == MessageRole.AGENT:
            print(f"Role: {message.role}, Content: {message.content}")
            # returntxt += f"Role: {message.role}, Content: {message.content}\n"
            # returntxt += f"Source: {message.content[0]['text']['value']}\n"
            returntxt += f"Source: {message.content[0].text.value}\n"
    # returntxt = f"{message.content[-1].text.value}"

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)    
    project_client.agents.threads.delete(thread.id)
    # print("Deleted agent")
    # Delete the connected Agent when done
    project_client.agents.delete_agent(ideation_agent.id)
    project_client.agents.delete_agent(inquiry_agent.id)
    project_client.agents.delete_agent(business_analyst.id)
    project_client.agents.delete_agent(tech_advisor.id)
    project_client.agents.delete_agent(strategic_analyst.id)
    project_client.agents.delete_agent(success_metrics_agent.id)
    project_client.agents.delete_agent(resource_planner.id)
    project_client.agents.delete_agent(techarch_metrics_agent.id)
    project_client.agents.delete_agent(Sustainablityagent.id)
    print("Deleted connected agent")
    # # Cleanup resources
    

    return returntxt, agent_outputs, token_usage

def parse_agent_outputs(run_steps):
    """Parse agent outputs from run steps to extract individual agent responses."""
    agent_outputs = {}
    
    for step in run_steps:
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])
        
        if tool_calls:
            for call in tool_calls:
                connected_agent = call.get("connected_agent", {})
                if connected_agent:
                    agent_name = connected_agent.get("name", "Unknown Agent")
                    agent_output = connected_agent.get("output", "No output available")
                    agent_outputs[agent_name] = agent_output
    
    return agent_outputs

def extract_mermaid_diagrams(text):
    """Extract Mermaid diagrams from text content."""
    import re
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(mermaid_pattern, text, re.DOTALL | re.IGNORECASE)
    return matches

def clean_mermaid_code(mermaid_code):
    """Clean and format Mermaid code for proper rendering."""
    import re  # Import at the top of function to avoid scoping issues
    
    if not mermaid_code:
        return ""
    
    # Remove any extra whitespace and normalize line endings
    cleaned = mermaid_code.strip()
    
    # Fix common text replacement issues
    cleaned = cleaned.replace('less thanbr / greater than', '')
    cleaned = cleaned.replace('less than', '<')
    cleaned = cleaned.replace('greater than', '>')
    cleaned = cleaned.replace('&lt;br&gt;', '')
    cleaned = cleaned.replace('&lt;', '<')
    cleaned = cleaned.replace('&gt;', '>')
    cleaned = cleaned.replace('&amp;', '&')
    
    # Fix common Mermaid syntax issues
    lines = cleaned.split('\n')
    fixed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip comment lines that start with %%
        if line.startswith('%%'):
            fixed_lines.append(line)
            continue
            
        # Fix node labels with problematic characters, including newlines
        if '[' in line and ']' in line:
            # Pattern to match various node label formats
            # This will match: NodeName["Label"] or NodeName[""Label""] or NodeName[Label]
            pattern = r'(\w+)\[(.*?)\]'
            
            def fix_label(match):
                node_name = match.group(1)
                label_text = match.group(2)
                
                # Remove quotes first to clean the text
                label_text = label_text.strip('"').strip("'")
                
                # Fix newline characters - this is the main issue
                label_text = label_text.replace('\\n', ' ')  # Replace \n with space
                label_text = label_text.replace('\n', ' ')   # Replace actual newlines with space
                
                # Only remove problematic parentheses content, not all parentheses
                # Remove parentheses that contain newlines or other problematic syntax
                label_text = re.sub(r'\([^)]*\\n[^)]*\)', '', label_text)  # Remove parentheses with \n
                label_text = re.sub(r'\([^)]*\n[^)]*\)', '', label_text)   # Remove parentheses with actual newlines
                
                # Clean up any remaining HTML entities or problematic text
                label_text = label_text.replace('""', '"')  # Fix double quotes
                label_text = label_text.replace('less than', '<')
                label_text = label_text.replace('greater than', '>')
                
                # Replace problematic characters in labels
                label_text = label_text.replace('&', 'and')  # Replace ampersands
                
                # Clean up multiple spaces and trim
                label_text = ' '.join(label_text.split()).strip()
                
                # Always use double quotes for labels to ensure proper escaping
                return f'{node_name}["{label_text}"]'
            
            line = re.sub(pattern, fix_label, line)
        
        # Clean up arrow syntax and node connections
        line = re.sub(r'\s*-->\s*', ' --> ', line)  # Normalize arrows
        
        # Clean up edge labels but preserve useful content like (OAuth2)
        # Only clean up edge labels that have problematic characters
        def clean_edge_label(match):
            full_match = match.group(0)
            edge_content = match.group(1)
            
            # Only remove newlines from edge labels, keep other content
            edge_content = edge_content.replace('\\n', ' ')
            edge_content = edge_content.replace('\n', ' ')
            edge_content = ' '.join(edge_content.split()).strip()
            
            return f'|{edge_content}|'
        
        line = re.sub(r'\|([^|]*)\|', clean_edge_label, line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def clean_mermaid_simple(mermaid_code):
    """Simplified Mermaid cleaning that focuses on the most common issues."""
    if not mermaid_code:
        return ""
    
    # Remove extra whitespace
    cleaned = mermaid_code.strip()
    
    # Simple fixes for the most common issues
    # Fix labels with forward slashes - wrap them in quotes
    # This pattern finds [Text with / characters] and wraps them in quotes
    pattern = r'\[([^\]]*\/[^\]]*)\]'
    
    def quote_labels_with_slashes(match):
        label_content = match.group(1)
        return f'["{label_content}"]'
    
    cleaned = re.sub(pattern, quote_labels_with_slashes, cleaned)
    
    # Normalize arrows
    cleaned = re.sub(r'\s*-->\s*', ' --> ', cleaned)
    
    return cleaned

def test_mermaid_cleaning():
    """Test the Mermaid cleaning function with the provided example."""
    # Test with the user's specific OAuth2 example
    test_diagram = """graph TD
subgraph Email Integrations
O365["Outlook 365"]
Gmail["Gmail"]
Other["Other Providers"]
LogicApp["Azure Logic Apps"]
O365 -->|Webhooks/OAuth|LogicApp
Gmail -->|API/OAuth|LogicApp
Other -->|Adapters/OAuth|LogicApp
end
subgraph User Access
UI["Web/Mobile App"]
UI -->|REST API|APIM["API Management"]
end
APIM -->|Secure API Call|AppSvc["Azure App Service/API"]
LogicApp -->|Trigger/Event|EventGrid["Azure Event Grid"]
EventGrid -->|Trigger|Function["Azure Function"]
AppSvc -->|Invoke|OpenAI["Azure OpenAI"]
AppSvc -->|NLU/AI Analysis|CognService["Cognitive Services"]
Function -->|Task Workflow|AppSvc
AppSvc -->|DB Ops|Cosmos["Azure Cosmos DB"]
AppSvc -->|Store/Read|Storage["Azure Storage Account"]
AppSvc -->|Secrets|KeyVault["Azure Key Vault"]
APIM -->|Auth|AAD["Azure AD"]
UI -->|Auth (OAuth2)|AAD
AppSvc -->|Logs/Telemetry|AppInsights["App Insights/Monitor"]"""
    
    # Test with the user's specific problematic diagram
    problematic_diagram = """flowchart TD

subgraph User Interaction WebUI[""Azure App Serviceless thanbr / greater thanWeb UI / Dashboard""] AppAPI[""Azure App Serviceless thanbr / greater thanAPI Backend""] end subgraph Identity Auth[""Azure AD B2C""] end subgraph Email Integration Gmail[""Gmail API""] Outlook[""Microsoft Graph API""] LogicApp[""Azure Logic Appsless thanbr / greater thanEmail Ingestion""] APIM[""Azure API Management""] end subgraph Processing FuncPre[""Azure Functionsless thanbr / greater thanPreprocessing""] NLP[""Azure Cognitive Servicesless thanbr / greater thanText Analytics""] OpenAI[""Azure OpenAI Serviceless thanbr / greater thanPrioritization / NLP Engine""] EventGrid[""Azure Event Grid""] end subgraph Storage CosmosDB[""Azure Cosmos DB""] KeyVault[""Azure Key Vault""] end subgraph Ops&Monitoring Insights[""Azure Monitor andless thanbr / greater thanApp Insights""] end %% User authentication WebUI <-- OAuth --> Auth WebUI <--API calls --> AppAPI AppAPI -->|Mail API calls via|APIM %% Email flows APIM --> LogicApp LogicApp --Gmail OAuth --> Gmail LogicApp --Graph OAuth --> Outlook LogicApp -->|New mail event|EventGrid %% Email Processing EventGrid --> FuncPre FuncPre --> NLP NLP --> FuncPre FuncPre --> OpenAI OpenAI --> FuncPre FuncPre --> CosmosDB %% UI interaction with processed data CosmosDB --> AppAPI AppAPI --> WebUI %% Feedback Loop WebUI -->|User Feedback|AppAPI AppAPI --> FuncPre FuncPre --> OpenAI %% Security APIM -.-> KeyVault LogicApp -.-> KeyVault FuncPre -.-> KeyVault %% Monitoring AppAPI --> Insights LogicApp --> Insights FuncPre --> Insights"""
    
    # Clean the OAuth2 test diagram
    cleaned_oauth2 = clean_mermaid_code(test_diagram)
    
    # Clean the problematic diagram
    cleaned_problematic = clean_mermaid_code(problematic_diagram)
    
    # Return both for testing
    return cleaned_oauth2, cleaned_problematic

def update_mermaid_diagrams():
    """Update session state with Mermaid diagrams from agent outputs and chat history."""
    all_diagrams = []
    
    # Extract from agent outputs
    for agent_name, output in st.session_state.agent_outputs.items():
        diagrams = extract_mermaid_diagrams(output)
        for i, diagram in enumerate(diagrams):
            cleaned_diagram = clean_mermaid_code(diagram)
            all_diagrams.append({
                'source': f"{agent_name} (Agent Output)",
                'diagram': cleaned_diagram,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
    
    # Extract from chat history
    for msg in st.session_state.chat_history:
        if msg['role'] == 'assistant':
            diagrams = extract_mermaid_diagrams(msg['content'])
            for i, diagram in enumerate(diagrams):
                cleaned_diagram = clean_mermaid_code(diagram)
                all_diagrams.append({
                    'source': "Chat Response",
                    'diagram': cleaned_diagram,
                    'timestamp': msg.get('timestamp', 'Unknown')
                })
    
    # Update session state
    st.session_state.mermaid_diagrams = all_diagrams

def transcribe_audio(audio_data) -> str:
    """Transcribe audio using Azure OpenAI Whisper."""
    try:
        # Convert audio data to the format expected by Whisper
        audio_file = io.BytesIO(audio_data.getvalue())
        audio_file.name = "audio.wav"
        
        transcript = client.audio.transcriptions.create(
            model=WHISPER_DEPLOYMENT_NAME,
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        st.error(f"❌ Audio transcription failed: {e}")
        return ""
    
def generate_audio_response_gpt(text):
    """Generate audio response using Azure OpenAI TTS API directly."""
    try:
        # Clean and optimize text for TTS
        clean_text = text.replace('*', '').replace('#', '').replace('`', '')
        clean_text = clean_text.replace('- ', '• ').replace('  ', ' ').strip()
        
        # Limit text length for optimal TTS quality
        if len(clean_text) > 3000:
            clean_text = clean_text[:3000] + "... I can provide more details if needed."
        
        url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/deployments/gpt-4o-mini-tts/audio/speech?api-version=2025-03-01-preview"  
      
        headers = {  
            "Content-Type": "application/json",  
            "Authorization": f"Bearer {os.environ['AZURE_OPENAI_KEY']}"  
        }  
        
        data = {  
            "model": "gpt-4o-mini-tts",  
            "input": clean_text,  
            "voice": "nova",  # Use consistent professional voice
            "response_format": "mp3",
            "speed": 0.9
        }  
        
        response = requests.post(url, headers=headers, json=data)  
        
        print(f"TTS API Response Status: {response.status_code}")
        
        if response.status_code == 200:  
            # Create a unique temporary file
            temp_file = os.path.join(tempfile.gettempdir(), f"response_{uuid.uuid4()}.mp3")
            
            with open(temp_file, "wb") as f:  
                f.write(response.content)  
            
            print(f"MP3 file saved successfully: {temp_file}")
            return temp_file
        else:  
            print(f"TTS API Error: {response.status_code}\n{response.text}")
            st.error(f"❌ Error generating audio: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error in generate_audio_response_gpt: {str(e)}")
        st.error(f"❌ Error generating audio response: {str(e)}")
        return None
    
@st.cache_resource
def get_mermaid_html(diagram):
    return f"""
    <div class="mermaid">
        {diagram}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    """

def brainstormmain():
    st.set_page_config(
        page_title="AI Brainstorming Hub",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional business UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 15px;
        border-radius: 10px;
        color: #000000;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border: 1px solid #f59e0b;
    }
    .main-header h1 {
        color: #000000 !important;
        margin-bottom: 5px;
        font-size: 1.8em;
    }
    .main-header p {
        color: #374151 !important;
        margin: 0;
        font-size: 0.9em;
    }
    .agent-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        height: 400px;
        overflow-y: auto;
    }
    .chat-container {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        height: 500px;
        overflow-y: auto;
    }
    .individual-agent {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .agent-title {
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-content {
        color: #374151;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .chat-message {
        margin: 15px 0;
        padding: 15px;
        border-radius: 12px;
        word-wrap: break-word;
    }
    .user-message {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        margin-right: 50px;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-left: 4px solid #6b7280;
        margin-left: 50px;
    }
    .voice-message {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
    }
    .message-header {
        font-weight: bold;
        color: #374151;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-container {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #10b981;
    }
    .input-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .scrollable-container::-webkit-scrollbar {
        width: 8px;
    }
    .scrollable-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    .scrollable-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 10px;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 5px;
        border: 1px solid #e2e8f0;
    }
    .audio-controls {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #3b82f6;
        text-align: center;
    }
    .agent-outputs-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        height: 500px;
        overflow-y: auto;
    }
    .accumulator-container {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #f59e0b;
        min-height: 400px;
    }
    .accumulator-textarea {
        width: 100%;
        min-height: 300px;
        padding: 15px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        line-height: 1.6;
        resize: vertical;
    }
    .selectable-content {
        cursor: text;
        user-select: text;
        -webkit-user-select: text;
        -moz-user-select: text;
        -ms-user-select: text;
    }
    .mermaid-container {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #0ea5e9;
        min-height: 400px;
    }
    .mermaid-chart {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #d1d5db;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 AI Brainstorming Hub</h1>
        <p>Multi-Agent Collaborative Intelligence for Strategic Innovation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = {}
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True
    if 'accumulator_content' not in st.session_state:
        st.session_state.accumulator_content = ""
    if 'selected_content' not in st.session_state:
        st.session_state.selected_content = ""
    if 'pending_copy_text' not in st.session_state:
        st.session_state.pending_copy_text = ""
    if 'token_usage' not in st.session_state:
        st.session_state.token_usage = {}
    if 'total_session_tokens' not in st.session_state:
        st.session_state.total_session_tokens = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
    if 'mermaid_diagrams' not in st.session_state:
        st.session_state.mermaid_diagrams = []
    
    # Create main layout
    main_col1, main_col2 = st.columns([3, 2])
    
    with main_col1:
        # Create tabs for the left column - Chat, Content Accumulator, and Mermaid Charts
        chat_tab, accumulator_tab, mermaid_tab = st.tabs(["💬 Brainstorming Chat", "📝 Content Accumulator", "📊 Mermaid Charts"])
        
        with chat_tab:
            # Chat Interface Section
            st.markdown("### 💬 Brainstorming Conversation")
            
            # Chat History Display
            chat_html = '<div class="chat-container scrollable-container">'
            
            if st.session_state.chat_history:
                for i, message in enumerate(st.session_state.chat_history):
                    message_class = "user-message" if message["role"] == "user" else "assistant-message"
                    if message.get("is_voice", False):
                        message_class += " voice-message"
                    
                    role_icon = "👤" if message["role"] == "user" else "🤖"
                    role_name = "You" if message["role"] == "user" else "AI Brainstorming Team"
                    
                    # Clean and escape content
                    content = message["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    content = content.replace("\n", "<br>")
                    
                    chat_html += f'''
                    <div class="chat-message {message_class}">
                        <div class="message-header">
                            {role_icon} {role_name}{" (Voice)" if message.get("is_voice", False) else ""}
                            <span style="font-size: 0.8em; color: #6b7280; margin-left: auto;">
                                {message.get("timestamp", "")}
                            </span>
                        </div>
                        <div class="agent-content selectable-content" id="chat-content-{i}">{content}</div>
                    </div>'''
            else:
                chat_html += '''
                <div style="text-align: center; color: #6b7280; padding: 100px 20px;">
                    <h3>🚀 Ready to Start Brainstorming!</h3>
                    <p>Ask a question or describe a challenge to engage our AI expert team.</p>
                </div>'''
            
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
            
            # Add simple copy buttons for chat messages
            if st.session_state.chat_history:
                st.markdown("#### 📋 Copy Chat Content")
                chat_col1, chat_col2 = st.columns(2)
                
                with chat_col1:
                    if st.button("📋 Copy Last Response", key="chat_copy_last"):
                        if st.session_state.chat_history:
                            # Get the last assistant response
                            last_response = None
                            for msg in reversed(st.session_state.chat_history):
                                if msg["role"] == "assistant":
                                    last_response = msg["content"]
                                    break
                            
                            if last_response:
                                if st.session_state.accumulator_content:
                                    st.session_state.accumulator_content += f"\n\n--- Last Chat Response ({datetime.now().strftime('%H:%M:%S')}) ---\n{last_response}"
                                else:
                                    st.session_state.accumulator_content = f"--- Last Chat Response ({datetime.now().strftime('%H:%M:%S')}) ---\n{last_response}"
                                st.success("✅ Copied to accumulator!")
                                st.rerun()
                
                with chat_col2:
                    if st.button("📋 Copy All Chat", key="chat_copy_all"):
                        if st.session_state.chat_history:
                            full_chat = f"--- Full Chat History ({datetime.now().strftime('%H:%M:%S')}) ---\n"
                            for msg in st.session_state.chat_history:
                                role = "User" if msg["role"] == "user" else "AI Team"
                                full_chat += f"\n{role} ({msg.get('timestamp', '')}):\n{msg['content']}\n"
                            
                            if st.session_state.accumulator_content:
                                st.session_state.accumulator_content += f"\n\n{full_chat}"
                            else:
                                st.session_state.accumulator_content = full_chat
                            st.success("✅ Copied to accumulator!")
                            st.rerun()
            
            # Audio Response Player
            if st.session_state.current_audio:
                st.markdown('<div class="audio-controls">', unsafe_allow_html=True)
                st.markdown("#### 🔊 AI Team Response Audio")
                st.audio(st.session_state.current_audio, format="audio/mp3")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Input Section
            st.markdown("### 💭 Your Input")
            
            # Create tabs for different input methods
            input_tab1, input_tab2 = st.tabs(["💬 Text Input", "🎤 Voice Input"])
            
            with input_tab1:
                # Text input using st.chat_input
                if prompt := st.chat_input("Describe your challenge or question for the AI brainstorming team..."):
                    if not st.session_state.processing:
                        process_brainstorm_request(prompt, is_voice=False)
                
                # Audio response option
                col_audio1, col_audio2 = st.columns([1, 1])
                with col_audio1:
                    st.session_state.audio_enabled = st.checkbox("🔊 Generate Audio Response", value=st.session_state.audio_enabled)
                with col_audio2:
                    if st.button("🔄 Clear Chat History"):
                        st.session_state.chat_history = []
                        st.session_state.agent_outputs = {}
                        st.session_state.current_audio = None
                        st.session_state.token_usage = {}
                        st.session_state.total_session_tokens = {
                            'prompt_tokens': 0,
                            'completion_tokens': 0,
                            'total_tokens': 0
                        }
                        st.session_state.mermaid_diagrams = []
                        st.rerun()
            
            with input_tab2:
                st.markdown('<div class="input-container">', unsafe_allow_html=True)
                st.markdown("#### 🎤 Voice Input")
                
                # Voice input
                audio_input = st.audio_input("Record your brainstorming question:")
                
                col_voice1, col_voice2 = st.columns([1, 1])
                with col_voice1:
                    if st.button("🎤 Process Voice Input", disabled=st.session_state.processing):
                        if audio_input and not st.session_state.processing:
                            # Transcribe audio first
                            with st.spinner("🎤 Transcribing your voice input...", show_time=True):
                                transcription = transcribe_audio(audio_input)
                                if transcription:
                                    st.success(f"📝 Transcribed: {transcription}")
                                    process_brainstorm_request(transcription, is_voice=True)
                                else:
                                    st.error("❌ Could not transcribe audio. Please try again.")
                
                with col_voice2:
                    voice_audio_enabled = st.checkbox("🔊 Voice Response", value=st.session_state.audio_enabled, key="voice_audio")
                    if voice_audio_enabled != st.session_state.audio_enabled:
                        st.session_state.audio_enabled = voice_audio_enabled
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with accumulator_tab:
            # Content Accumulator Tab - simplified and streamlined
            st.markdown("### 📝 Content Accumulator & Editor")
            st.markdown("*Collect, edit, and organize insights from conversations and agent outputs*")
            
            # Quick action buttons at the top
            col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)
            
            with col_quick1:
                if st.button("📋 Copy Last Response", key="acc_copy_last"):
                    if st.session_state.chat_history:
                        # Get the last assistant response
                        last_response = None
                        for msg in reversed(st.session_state.chat_history):
                            if msg["role"] == "assistant":
                                last_response = msg["content"]
                                break
                        
                        if last_response:
                            if st.session_state.accumulator_content:
                                st.session_state.accumulator_content += f"\n\n--- Last Chat Response ({datetime.now().strftime('%H:%M:%S')}) ---\n{last_response}"
                            else:
                                st.session_state.accumulator_content = f"--- Last Chat Response ({datetime.now().strftime('%H:%M:%S')}) ---\n{last_response}"
                            st.success("✅ Added to accumulator!")
                            st.rerun()
            
            with col_quick2:
                if st.button("📋 Copy Full Chat", key="acc_copy_full"):
                    if st.session_state.chat_history:
                        full_chat = f"--- Full Chat History ({datetime.now().strftime('%H:%M:%S')}) ---\n"
                        for msg in st.session_state.chat_history:
                            role = "User" if msg["role"] == "user" else "AI Team"
                            full_chat += f"\n{role} ({msg.get('timestamp', '')}):\n{msg['content']}\n"
                        
                        if st.session_state.accumulator_content:
                            st.session_state.accumulator_content += f"\n\n{full_chat}"
                        else:
                            st.session_state.accumulator_content = full_chat
                        st.success("✅ Added to accumulator!")
                        st.rerun()
            
            with col_quick3:
                if st.button("🗑️ Clear Accumulator", key="acc_clear"):
                    st.session_state.accumulator_content = ""
                    st.success("✅ Accumulator cleared!")
                    st.rerun()
            
            with col_quick4:
                if st.session_state.accumulator_content:
                    st.download_button(
                        label="💾 Download",
                        data=st.session_state.accumulator_content,
                        file_name=f"accumulated_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key="download_accumulator"
                    )
            
            st.divider()
            
            # Main content editor - larger and more prominent
            st.markdown("#### ✏️ Edit Your Accumulated Content")
            edited_content = st.text_area(
                "Your accumulated insights and notes:",
                value=st.session_state.accumulator_content,
                height=500,
                placeholder="Your collected insights will appear here. You can edit this content directly or use the copy buttons from chat and agent outputs to add content.",
                help="Edit this content directly, or use the copy buttons from chat messages and agent outputs to add content here."
            )
            
            # Update session state if content changed
            if edited_content != st.session_state.accumulator_content:
                st.session_state.accumulator_content = edited_content
            
            # Simple statistics
            if st.session_state.accumulator_content:
                word_count = len(st.session_state.accumulator_content.split())
                char_count = len(st.session_state.accumulator_content)
                st.caption(f"📊 **{word_count}** words • **{char_count}** characters")
            else:
                st.caption("📝 Start accumulating content using the copy buttons above")
            
            # Template suggestions
            st.markdown("#### 📋 Quick Templates")
            template_col1, template_col2 = st.columns(2)
            
            with template_col1:
                if st.button("📊 Analysis Template", key="template_analysis"):
                    template = """--- STRATEGIC ANALYSIS ---

## Executive Summary
[Key findings and recommendations]

## Market Opportunity
[Market size, trends, competitive landscape]

## Technical Feasibility
[Technology assessment and implementation approach]

## Business Model
[Revenue streams, cost structure, value proposition]

## Resource Requirements
[Team, budget, timeline]

## Success Metrics
[KPIs and measurement framework]

## Next Steps
[Action items and priorities]
"""
                    st.session_state.accumulator_content = template
                    st.rerun()
            
            with template_col2:
                if st.button("💡 Ideas Template", key="template_ideas"):
                    template = """--- BRAINSTORMING SESSION ---

## Challenge/Opportunity
[Define the problem or opportunity]

## Creative Ideas
- [Idea 1]
- [Idea 2]
- [Idea 3]

## Evaluation Criteria
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

## Selected Concepts
[Top ideas for further development]

## Implementation Plan
[Next steps and action items]
"""
                    st.session_state.accumulator_content = template
                    st.rerun()
            
            # Word count and statistics
            if st.session_state.accumulator_content:
                word_count = len(st.session_state.accumulator_content.split())
                char_count = len(st.session_state.accumulator_content)
                st.markdown(f"**Statistics:** {word_count} words, {char_count} characters")
        
        with mermaid_tab:
            # Mermaid Charts Tab
            st.markdown("### 📊 Mermaid Architecture Diagrams")
            st.markdown("*Visualize architecture and process diagrams from AI agent responses*")
            
            # Update diagrams when tab is accessed
            update_mermaid_diagrams()
            
            # Action buttons
            col_mermaid1, col_mermaid2, col_mermaid3 = st.columns(3)
            
            with col_mermaid1:
                if st.button("🔄 Refresh Diagrams", key="refresh_mermaid"):
                    update_mermaid_diagrams()
                    st.success("✅ Diagrams refreshed!")
                    st.rerun()
            
            with col_mermaid2:
                total_diagrams = len(st.session_state.mermaid_diagrams)
                st.metric("📊 Diagrams Found", total_diagrams)
            
            with col_mermaid3:
                if st.session_state.mermaid_diagrams:
                    # Create downloadable content
                    mermaid_export = ""
                    for i, diagram_info in enumerate(st.session_state.mermaid_diagrams):
                        mermaid_export += f"## Diagram {i+1} - {diagram_info['source']}\n"
                        mermaid_export += f"Generated: {diagram_info['timestamp']}\n\n"
                        mermaid_export += f"```mermaid\n{diagram_info['diagram']}\n```\n\n"
                    
                    st.download_button(
                        label="💾 Download",
                        data=mermaid_export,
                        file_name=f"mermaid_diagrams_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_mermaid"
                    )
            
            st.divider()
            
            # Display Mermaid diagrams
            if st.session_state.mermaid_diagrams:
                st.markdown("#### 🎨 Interactive Diagrams")
                # st.html(f"""
                #                     <script type="module">
                #                         import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
                #                         mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                #                         console.log("Mermaid initialized"); // Debugging
                #                     </script>
                #                     """)
                
                for i, diagram_info in enumerate(st.session_state.mermaid_diagrams):
                    with st.expander(f"📊 Diagram {i+1}: {diagram_info['source']} (Generated: {diagram_info['timestamp']})", expanded=True):
                        # Display source information
                        st.markdown(f"**Source:** {diagram_info['source']}")
                        st.markdown(f"**Generated:** {diagram_info['timestamp']}")
                        
                        # Display Mermaid diagram
                        try:
                            st.markdown("**Mermaid Diagram:**")
                            
                            # Clean the diagram code again to ensure it's properly formatted
                            clean_diagram = clean_mermaid_code(diagram_info['diagram'])
                            
                            # Use Streamlit's native markdown with mermaid support
                            st.markdown(f"""
                            ```mermaid
                            {clean_diagram}
                            ```
                            """)

                            # st.html(f"""
                            #         <div class="mermaid">
                            #             {clean_diagram}
                            #         </div>
                            #         """)
                            # st.html(f"""
                            #     <pre class="mermaid">
                            #         {clean_diagram}
                            #     </pre>
                            #     <script type="module">
                            #         import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                            #         mermaid.initialize({{ startOnLoad: true }});
                            #     </script>
                            # """)
                            st.markdown(get_mermaid_html(clean_diagram), unsafe_allow_html=True)

                            # Also provide a text area for editing/copying
                            st.markdown("**Mermaid Code (editable):**")
                            edited_diagram = st.text_area(
                                f"Edit Diagram {i+1}:",
                                value=clean_diagram,
                                height=200,
                                key=f"mermaid_edit_{i}",
                                help="You can copy this Mermaid code to use in other tools like Mermaid Live Editor"
                            )
                            
                            # Update diagram if edited
                            if edited_diagram != clean_diagram:
                                # Clean the edited diagram too
                                st.session_state.mermaid_diagrams[i]['diagram'] = clean_mermaid_code(edited_diagram)
                            
                            # Action buttons for individual diagrams
                            col_action1, col_action2, col_action3 = st.columns(3)
                            
                            with col_action1:
                                if st.button(f"📋 Copy to Accumulator", key=f"copy_mermaid_{i}"):
                                    mermaid_content = f"\n\n--- Mermaid Diagram from {diagram_info['source']} ---\n```mermaid\n{clean_diagram}\n```\n"
                                    if st.session_state.accumulator_content:
                                        st.session_state.accumulator_content += mermaid_content
                                    else:
                                        st.session_state.accumulator_content = mermaid_content
                                    st.success("✅ Copied to accumulator!")
                                    st.rerun()
                            
                            with col_action2:
                                # Use cleaned diagram for the live editor link
                                encoded_diagram = clean_diagram.replace(' ', '%20').replace('\n', '%0A').replace('#', '%23')
                                st.markdown(f"[🌐 Open in Mermaid Live](https://mermaid.live/edit#{encoded_diagram})")
                            
                            with col_action3:
                                if st.button(f"🗑️ Remove", key=f"remove_mermaid_{i}"):
                                    st.session_state.mermaid_diagrams.pop(i)
                                    st.success("✅ Diagram removed!")
                                    st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Error displaying diagram: {str(e)}")
                            st.code(diagram_info['diagram'], language="text")
            else:
                # No diagrams found
                st.markdown("""
                <div class="mermaid-container">
                    <div style="text-align: center; padding: 50px 20px;">
                        <h4>📊 No Mermaid Diagrams Found</h4>
                        <p>Mermaid diagrams will automatically appear here when generated by AI agents.</p>
                        <p><strong>The Technical Architect agent</strong> typically generates architecture diagrams in Mermaid format.</p>
                        <br>
                        <p style="font-size: 0.9em; color: #6b7280;">
                            💡 <strong>Tip:</strong> Ask questions about system architecture, technical design, or process flows to generate diagrams.
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Sample Mermaid diagram for demonstration
                st.markdown("#### 📝 Test Azure Architecture Diagram")
                with st.expander("🔧 Test Diagram Cleaning (Azure Architecture)", expanded=False):
                    # Test the problematic Azure diagram
                    oauth2_cleaned, problematic_cleaned = test_mermaid_cleaning()
                    
                    st.markdown("**Original diagram (had issues with text replacement):**")
                    st.code("""flowchart TD
WebUI[""Azure App Serviceless thanbr / greater thanWeb UI / Dashboard""]
AppAPI[""Azure App Serviceless thanbr / greater thanAPI Backend""]""", language="text")
                    
                    st.markdown("**Cleaned diagram (should render properly):**")
                    st.code(problematic_cleaned[:300] + "...", language="text")
                    
                    # Try to render the cleaned diagram
                    st.markdown("**Rendered diagram:**")
                    st.markdown(f"""
```mermaid
{problematic_cleaned}
```
""")
                
                st.markdown("#### 🔐 Test OAuth2 Edge Label Preservation")
                with st.expander("🔧 Test OAuth2 Edge Labels", expanded=False):
                    st.markdown("**Test case: OAuth2 in edge labels should be preserved**")
                    st.code('UI -->|Auth (OAuth2)|AAD["Azure AD"]', language="text")
                    
                    st.markdown("**Cleaned result:**")
                    st.code(oauth2_cleaned, language="text")
                    
                    # Check if OAuth2 is preserved
                    oauth2_preserved = "(OAuth2)" in oauth2_cleaned
                    if oauth2_preserved:
                        st.success("✅ OAuth2 content preserved in edge labels!")
                    else:
                        st.error("❌ OAuth2 content was removed from edge labels!")
                    
                    st.markdown("**Rendered OAuth2 test:**")
                    st.markdown(f"""
```mermaid
{oauth2_cleaned}
```
""")
    
    
    with main_col2:
        # Agent Insights Panel - simplified
        st.markdown("### 🤖 AI Agent Insights")
        
        # Status and Metrics
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #3b82f6; margin: 0;">{len(st.session_state.chat_history) // 2}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">Questions Asked</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_stat2:
            voice_count = len([msg for msg in st.session_state.chat_history if msg.get("is_voice", False)])
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #10b981; margin: 0;">{voice_count}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">Voice Interactions</p>
            </div>
            ''', unsafe_allow_html=True)
            
        with col_stat3:
            total_tokens = st.session_state.total_session_tokens.get('total_tokens', 0)
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #f59e0b; margin: 0;">{total_tokens:,}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">Total Tokens</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Processing Status
        if st.session_state.processing:
            st.markdown('''
            <div class="status-container">
                <h4>🔄 AI Team is Processing...</h4>
                <p>Multiple AI agents are collaborating on your request</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Token Usage Details
        if st.session_state.token_usage:
            st.markdown("#### 🔢 Current Request Token Usage")
            token_col1, token_col2, token_col3 = st.columns(3)
            
            with token_col1:
                st.markdown(f'''
                <div class="metric-card">
                    <h4 style="color: #6366f1; margin: 0;">{st.session_state.token_usage.get('prompt_tokens', 0):,}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em;">Prompt Tokens</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with token_col2:
                st.markdown(f'''
                <div class="metric-card">
                    <h4 style="color: #10b981; margin: 0;">{st.session_state.token_usage.get('completion_tokens', 0):,}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em;">Completion Tokens</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with token_col3:
                st.markdown(f'''
                <div class="metric-card">
                    <h4 style="color: #f59e0b; margin: 0;">{st.session_state.token_usage.get('total_tokens', 0):,}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em;">Total Tokens</p>
                </div>
                ''', unsafe_allow_html=True)
        
        # Session Token Summary
        if st.session_state.total_session_tokens.get('total_tokens', 0) > 0:
            st.markdown("#### 📈 Session Token Summary")
            st.markdown(f'''
            <div class="status-container">
                <p><strong>Total Session Tokens:</strong> {st.session_state.total_session_tokens.get('total_tokens', 0):,}</p>
                <p><strong>Prompt Tokens:</strong> {st.session_state.total_session_tokens.get('prompt_tokens', 0):,} | 
                   <strong>Completion Tokens:</strong> {st.session_state.total_session_tokens.get('completion_tokens', 0):,}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Individual Agent Outputs with scrollable container
        st.markdown("#### 📊 Individual Agent Outputs")
        
        if st.session_state.agent_outputs:
            agent_icons = {
                "ideationagent": "💡",
                "inquiryagent": "❓", 
                "businessanalyst": "💼",
                "techadvisor": "🚀",
                "strategicanalyst": "📊",
                "Sustainabilitypaperagent": "🌱",
                "ResourcePlanner": "📋",
                "SuccessMetricsAgent": "🎯",
                "TechArchMetricsAgent": "🏗️"
            }
            
            agent_names = {
                "ideationagent": "Ideation Catalyst",
                "inquiryagent": "Inquiry Specialist", 
                "businessanalyst": "Business Analyst",
                "techadvisor": "Technology Advisor",
                "strategicanalyst": "Strategic Analyst",
                "Sustainabilitypaperagent": "Sustainability Expert",
                "ResourcePlanner": "Resource Planner",
                "SuccessMetricsAgent": "Success Metrics Expert",
                "TechArchMetricsAgent": "Technical Architect"
            }
            
            # Sort agents to ensure consistent display order
            sorted_agents = sorted(st.session_state.agent_outputs.items())
            
            # Create a scrollable container using Streamlit's container
            with st.container(height=600):
                # Create expandable containers for each agent within the scrollable container
                for agent_id, output in sorted_agents:
                    icon = agent_icons.get(agent_id, "🤖")
                    name = agent_names.get(agent_id, agent_id)
                    
                    # Use streamlit expander for each agent
                    with st.expander(f"{icon} {name}", expanded=False):
                        # Clean and format output for display
                        clean_output = output.replace("**", "").replace("##", "").replace("###", "")
                        
                        # Display content in a text area for easy copying
                        st.text_area(
                            f"📄 {name} Output (Copy any part you need):",
                            value=clean_output,
                            height=150,
                            key=f"output_{agent_id}",
                            help="Select any text from this output and copy it to your clipboard"
                        )
                        
                        # Simple copy button
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"📋 Copy All to Accumulator", key=f"copy_all_{agent_id}"):
                                if st.session_state.accumulator_content:
                                    st.session_state.accumulator_content += f"\n\n--- {name} Insights ---\n{clean_output}"
                                else:
                                    st.session_state.accumulator_content = f"--- {name} Insights ---\n{clean_output}"
                                st.success(f"✅ Added {name} insights to accumulator!")
                                st.rerun()
                        
                        with col2:
                            # Show a small preview of what's in the accumulator
                            accumulator_preview = st.session_state.accumulator_content[-100:] + "..." if len(st.session_state.accumulator_content) > 100 else st.session_state.accumulator_content
                            st.caption(f"📝 Accumulator has {len(st.session_state.accumulator_content.split())} words")
        else:
            st.info("""
            🤖 **AI Agents Standing By**
            
            Individual agent insights will appear here after processing your request.
            
            **Our Expert Team:**
            - 💡 Ideation Catalyst
            - ❓ Inquiry Specialist  
            - 💼 Business Analyst
            - 🚀 Technology Advisor
            - 📊 Strategic Analyst
            - 🌱 Sustainability Expert
            - 📋 Resource Planner
            - 🎯 Success Metrics Expert
            - 🏗️ Technical Architect
            """)
        
        # Export Options
        st.markdown("#### 📤 Export Options")
        
        if st.session_state.chat_history or st.session_state.agent_outputs:
            export_data = {
                "chat_history": st.session_state.chat_history,
                "agent_outputs": st.session_state.agent_outputs,
                "mermaid_diagrams": st.session_state.mermaid_diagrams,
                "token_usage": {
                    "current_request": st.session_state.token_usage,
                    "session_total": st.session_state.total_session_tokens
                },
                "export_timestamp": datetime.now().isoformat()
            }
            
            st.download_button(
                label="📄 Download Session Report",
                data=json.dumps(export_data, indent=2),
                file_name=f"brainstorming_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

def process_brainstorm_request(user_input: str, is_voice: bool = False):
    """Process a brainstorming request through the multi-agent system."""
    
    # Set processing state
    st.session_state.processing = True
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "is_voice": is_voice,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Show processing indicator
    with st.spinner("🧠 AI Brainstorming Team is collaborating on your request...", show_time=True):
        try:
            # Call the multi-agent brainstorm function
            final_response, agent_outputs, token_usage = connected_agent_brainstorm(user_input)
            
            # Store agent outputs and token usage
            st.session_state.agent_outputs = agent_outputs
            st.session_state.token_usage = token_usage
            
            # Update Mermaid diagrams from new content
            update_mermaid_diagrams()
            
            # Update total session tokens
            st.session_state.total_session_tokens['prompt_tokens'] += token_usage.get('prompt_tokens', 0)
            st.session_state.total_session_tokens['completion_tokens'] += token_usage.get('completion_tokens', 0)
            st.session_state.total_session_tokens['total_tokens'] += token_usage.get('total_tokens', 0)
            
            # Add assistant response to chat history with token information
            response_with_tokens = f"{final_response}\n\n📊 **Token Usage**: {token_usage.get('total_tokens', 0):,} tokens (Prompt: {token_usage.get('prompt_tokens', 0):,}, Completion: {token_usage.get('completion_tokens', 0):,})"
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_with_tokens,
                "is_voice": False,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "token_usage": token_usage
            })
            
            # Generate audio response if enabled
            if st.session_state.audio_enabled:
                with st.spinner("🔊 Converting response to speech...", show_time=True):
                    # Create audio from the final summarized response
                    audio_file_path = generate_audio_response_gpt(final_response)
                    if audio_file_path and os.path.exists(audio_file_path):
                        # Read the audio file and store it in session state
                        with open(audio_file_path, 'rb') as f:
                            st.session_state.current_audio = f.read()
                        # Clean up the temporary file
                        try:
                            os.remove(audio_file_path)
                        except:
                            pass  # Ignore cleanup errors
            
            # Reset processing state
            st.session_state.processing = False
            
            # Rerun to update the UI
            st.rerun()
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ Error processing your request: {str(e)}")
            
            # Add error message to chat history with empty token usage
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ Sorry, I encountered an error while processing your request: {str(e)}",
                "is_voice": False,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            })
            st.rerun()

if __name__ == "__main__":
    with tracer.start_as_current_span("BrainStormingMultiAgent-tracing"):
        brainstormmain()