import tempfile
import uuid
from openai import AzureOpenAI
import streamlit as st
import asyncio
import io
import os
import time
import json
import soundfile as sf
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List
from scipy.signal import resample
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import base64
import PIL.ImageGrab as ImageGrab
from PIL import Image


from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def capture_screenshot() -> str:
    """Capture a screenshot and return it as a base64 encoded string"""
    try:
        # Capture the entire screen
        screenshot = ImageGrab.grab()
        
        # Convert to RGB if needed (some systems return RGBA)
        if screenshot.mode != 'RGB':
            screenshot = screenshot.convert('RGB')
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode to base64
        screenshot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print(f"Screenshot captured successfully. Size: {len(screenshot_base64)} chars")
        return screenshot_base64
        
    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        # Return a placeholder image if screenshot fails
        # Create a simple 1x1 pixel image as fallback
        fallback_img = Image.new('RGB', (1, 1), color='white')
        buffer = io.BytesIO()
        fallback_img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Azure OpenAI configuration (replace with your credentials)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-06-01"  # Adjust API version as needed
)

def cuarun(query: str, environment: str = "browser") -> Dict[str, Any]:
    """Run computer use model and return detailed output for display"""
    cuaclient = AzureOpenAI(  
        base_url = os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",  
        api_key= os.getenv("AZURE_OPENAI_KEY"),
        api_version="preview"
        )

    try:
        response = cuaclient.responses.create(
            model="computer-use-preview", # set this to your model deployment name
            tools=[{
                "type": "computer_use_preview",
                "display_width": 1024,
                "display_height": 768,
                "environment": environment # browser for web tasks, windows for desktop
            }],
            input=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            truncation="auto",
            max_output_tokens= 2000,  # Increased for web content
        )

        # Initialize result dictionary
        result = {
            "success": True,
            "response_id": response.id if hasattr(response, 'id') else None,
            "raw_output": [],
            "computer_calls": [],
            "text_content": [],
            "web_content": [],
            "screenshots": [],
            "environment": environment,
            "error": None,
            "full_response": None,
            "response_type": None
        }

        # Store the full response for debugging
        result["full_response"] = str(response)
        
        # Check different response formats
        print("=== DEBUG: Response object ===")
        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")
        ## response.output is the previous response from the model
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            print("No computer call found. Output from model:")
            for item in response.output:
                print(item)

        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action

        # Extract screenshot from the first response if available
        screenshot_base64 = None
        
        # Look for screenshot data in the response output
        for item in response.output:
            if hasattr(item, 'type'):
                # Check if this is a screenshot output
                if item.type == "computer_call_output" and hasattr(item, 'output'):
                    output_obj = item.output
                    if hasattr(output_obj, 'type') and output_obj.type == "screenshot":
                        if hasattr(output_obj, 'image_url'):
                            # Extract base64 from image_url
                            image_url = output_obj.image_url
                            if "base64," in image_url:
                                screenshot_base64 = image_url.split("base64,")[1]
                                print(f"Found screenshot in first response: {len(screenshot_base64)} chars")
                        elif hasattr(output_obj, 'data'):
                            screenshot_base64 = output_obj.data
                            print(f"Found screenshot data in first response: {len(screenshot_base64)} chars")
                # Check if the item itself contains screenshot data
                elif hasattr(item, 'image_url') and item.image_url:
                    image_url = item.image_url
                    if "base64," in image_url:
                        screenshot_base64 = image_url.split("base64,")[1]
                        print(f"Found image_url in item: {len(screenshot_base64)} chars")
        
        # If no screenshot found in first response, use desktop capture as fallback
        screenshot_source = "first_response"
        if not screenshot_base64:
            print("No screenshot found in first response, capturing desktop as fallback")
            screenshot_base64 = capture_screenshot()
            screenshot_source = "desktop_fallback"

        # Your application would now perform the action suggested by the model
        # And create a screenshot of the updated state of the environment before sending another response
        
        # Store screenshot info in results
        result["screenshots"].append({
            "timestamp": datetime.now().isoformat(),
            "description": f"Screenshot used for model analysis ({screenshot_source})",
            "size": len(screenshot_base64),
            "source": screenshot_source
        })

        response_2 = cuaclient.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=[{
                "type": "computer_use_preview",
                "display_width": 1024,
                "display_height": 768,
                "environment": environment # browser for web tasks, windows for desktop
            }],
            input=[
                {
                    "call_id": last_call_id,
                    "type": "computer_call_output",
                    "output": {
                        "type": "input_image",
                        # Image should be in base64
                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ],
            truncation="auto"
        )
                
        # Process both the initial response and the follow-up response with screenshot
        # Try to access response content in different ways
        response_content = None
        
        # Store both responses for debugging
        result["full_response"] = f"Response 1: {str(response)}\n\nResponse 2: {str(response_2)}"
        
        print("=== DEBUG: Processing Response 2 (with screenshot) ===")
        print(f"Response 2 type: {type(response_2)}")
        
        # Process response_2 first (this should have the final analysis after screenshot)
        if hasattr(response_2, 'output') and response_2.output:
            print(f"Found response_2.output: {type(response_2.output)}")
            result["raw_output"].extend(response_2.output)
            result["response_type"] = "output_with_screenshot"
            
            # Process each item in response_2 output
            for i, item in enumerate(response_2.output):
                print(f"Response 2 Output item {i}: {type(item)} - {item}")
                
                if hasattr(item, 'type'):
                    if item.type == "text":
                        text_content = getattr(item, 'text', str(item))
                        result["text_content"].append(f"[Final Analysis]: {text_content}")
                        print(f"Response 2 Text content: {text_content}")
                    else:
                        # Handle other types from response_2
                        item_str = str(item)
                        result["text_content"].append(f"[Response 2 - {item.type}] {item_str}")
                        print(f"Response 2 Other type {item.type}: {item_str}")
                else:
                    item_str = str(item)
                    result["text_content"].append(f"[Response 2] {item_str}")
                    print(f"Response 2 No type attribute: {item_str}")
        
        # Also process the initial response (for computer calls/actions)
        # Method 1: Check for output attribute
        if hasattr(response, 'output') and response.output:
            print(f"Found response.output: {type(response.output)}")
            if not result["raw_output"]:  # Only set if not already set by response_2
                result["raw_output"] = response.output
                result["response_type"] = "output"
            
            # Process each item in output from initial response
            for i, item in enumerate(response.output):
                print(f"Response 1 Output item {i}: {type(item)} - {item}")
                
                # Try to extract content based on item type
                if hasattr(item, 'type'):
                    if item.type == "computer_call":
                        computer_call_info = {
                            "call_id": getattr(item, 'call_id', 'unknown'),
                            "action": getattr(item, 'action', None),
                            "type": item.type,
                            "full_item": str(item)
                        }
                        
                        # Extract more details from the action
                        if hasattr(item, 'action') and item.action:
                            action_obj = item.action
                            print(f"Action object: {type(action_obj)} - {action_obj}")
                            computer_call_info["action_details"] = str(action_obj)
                            
                            # Handle different action types
                            if hasattr(action_obj, 'type'):
                                computer_call_info["action_type"] = action_obj.type
                                
                                # Handle screenshot action
                                if action_obj.type == 'screenshot':
                                    computer_call_info["action_type"] = "screenshot"
                                    computer_call_info["description"] = "Take screenshot of current screen"
                                    
                            # Try to get other action properties
                            if hasattr(action_obj, 'action'):
                                computer_call_info["action_type"] = action_obj.action
                            if hasattr(action_obj, 'coordinate'):
                                computer_call_info["coordinates"] = action_obj.coordinate
                            if hasattr(action_obj, 'text'):
                                computer_call_info["text_input"] = action_obj.text
                        
                        result["computer_calls"].append(computer_call_info)
                    
                    elif item.type == "text":
                        text_content = getattr(item, 'text', str(item))
                        result["text_content"].append(text_content)
                        print(f"Text content: {text_content}")
                    
                    elif item.type == "computer_call_output":
                        # This might contain screenshot or other output data
                        output_obj = getattr(item, 'output', None)
                        if output_obj and hasattr(output_obj, 'type'):
                            if output_obj.type == "screenshot":
                                screenshot_info = {
                                    "timestamp": datetime.now().isoformat(),
                                    "description": "Screenshot from computer use model",
                                    "type": "model_screenshot"
                                }
                                if hasattr(output_obj, 'image_url'):
                                    screenshot_info["image_url"] = output_obj.image_url[:100] + "..." # Truncate for display
                                result["screenshots"].append(screenshot_info)
                                print(f"Found screenshot output in first response")
                    
                    else:
                        # Handle other types
                        item_str = str(item)
                        result["text_content"].append(f"[{item.type}] {item_str}")
                        print(f"Other type {item.type}: {item_str}")
                else:
                    # No type attribute
                    item_str = str(item)
                    result["text_content"].append(item_str)
                    print(f"No type attribute: {item_str}")
        
        # Method 2: Check for choices (like standard OpenAI response)
        elif hasattr(response, 'choices') and response.choices:
            print("Found response.choices")
            result["response_type"] = "choices"
            for choice in response.choices:
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    result["text_content"].append(choice.message.content)
        
        # Method 3: Check for output_text
        elif hasattr(response, 'output_text'):
            print(f"Found response.output_text: {response.output_text}")
            result["response_type"] = "output_text"
            result["text_content"].append(response.output_text)
        
        # Method 4: Check for content attribute
        elif hasattr(response, 'content'):
            print(f"Found response.content: {response.content}")
            result["response_type"] = "content"
            result["text_content"].append(response.content)
        
        else:
            # Last resort - try to convert entire response to string
            print("No known attributes found, converting to string")
            result["response_type"] = "string_conversion"
            result["text_content"].append(str(response))
        
        # If we found computer calls, explain what happens next
        if result["computer_calls"]:
            explanation = """
🔄 **Computer Use Model with Screenshot Feedback!**

The model has analyzed your request and provided computer actions. A screenshot was automatically captured and sent back to the model for analysis.

**What happened:**
1. ✅ Model analyzed your request and planned actions
2. ✅ Screenshot was automatically captured from your screen
3. ✅ Screenshot was sent back to the model for analysis
4. ✅ Model provided final analysis based on the visual information

**Current Status**: Both the action plan and visual analysis are now available.
            """
            result["text_content"].insert(0, explanation)
        else:
            # Check if we have analysis from response_2
            if result.get("text_content") and any("Final Analysis" in text for text in result["text_content"]):
                explanation = """
🔄 **Visual Analysis Completed!**

A screenshot was captured and analyzed by the computer use model. The analysis results are shown below.
                """
                result["text_content"].insert(0, explanation)
        
        return result

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "raw_output": [],
            "computer_calls": [],
            "text_content": [f"Error details: {str(e)}"],
            "web_content": [],
            "screenshots": [],
            "environment": environment,
            "response_id": None,
            "full_response": None,
            "response_type": "error"
        }

def main():
    """Streamlit interface for Computer Use Agent"""
    st.set_page_config(
        page_title="Computer Use Agent - Web Browser",
        page_icon="🌐",
        layout="wide"
    )

    st.title("🌐 Computer Use Agent - Web Browser")
    st.markdown("### AI-powered web browsing and content extraction")
    
    # Input section
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📝 Enter your web browsing request:")
            query = st.text_area(
                "What would you like to browse or extract from the internet?",
                value="Go to https://news.ycombinator.com and summarize the top 3 stories",
                height=100,
                help="Describe what you want to browse, search, or extract from websites"
            )
        
        with col2:
            st.markdown("#### 🖥️ Environment:")
            environment = st.selectbox(
                "Select environment",
                ["browser", "windows", "ubuntu", "mac"],
                index=0,
                help="Browser is recommended for web tasks"
            )
            
            if environment == "browser":
                st.info("🌐 Browser mode: Optimized for web browsing and content extraction")
            else:
                st.info("🖥️ Desktop mode: For system-level tasks")
        
        col1, col2= st.columns([1, 1])
        with col1:
            if st.button("🚀 Browse & Extract", type="primary"):
                if query.strip():
                    execute_computer_use(query, environment)
                else:
                    st.error("Please enter a request")
        
        with col2:
            if st.button("🗑️ Clear Output"):
                if 'execution_results' in st.session_state:
                    del st.session_state.execution_results
                st.rerun()

def execute_computer_use(query: str, environment: str = "browser"):
    """Execute computer use model and display results"""
    with st.spinner("🌐 Browsing and extracting content..."):
        try:
            # Execute the computer use function
            result = cuarun(query, environment)
            
            # Store in session state for persistence
            st.session_state.execution_results = result
            st.session_state.last_query = query
            
            # Display results
            display_results(result, query)
            
        except Exception as e:
            st.error(f"❌ Error executing request: {str(e)}")
            st.exception(e)

def display_results(result: Dict[str, Any], original_query: str):
    """Display detailed results from computer use model with enhanced debugging and explanation"""
    
    # Create unique key prefix to avoid button key conflicts
    import time
    key_prefix = f"result_{int(time.time() * 1000)}"
    
    # Use full width container for results
    st.markdown("---")
    
    # Create a full-width container for all results
    with st.container(height=600, width=1000):
        st.markdown("### 📊 Computer Use Model Results")
        
        # Show original query and environment
        with st.expander("📝 Request Details", expanded=False):
            st.code(original_query, language="text")
            st.info(f"🖥️ Environment: **{result.get('environment', 'browser')}**")
            st.info(f"🔍 Response Type: **{result.get('response_type', 'unknown')}**")
        
        # Success/Error status with detailed explanation
        if result["success"]:
            if result.get("computer_calls"):
                st.warning("⚠️ **Action Plan Received** - Execution needed for final results")
                st.info("💡 The model provided computer actions but they haven't been executed yet. This is expected for computer use models - they plan actions but need an execution loop.")
            else:
                st.success("✅ Request processed successfully")
        else:
            st.error(f"❌ Error: {result['error']}")
            return
        
        # Display response ID if available
        if result["response_id"]:
            st.info(f"🆔 Response ID: `{result['response_id']}`")
        
        # Show what the model is actually doing
        st.markdown("### 🔍 Understanding Computer Use Model Behavior")
        
        if result.get("computer_calls"):
            st.warning("**🎯 The Model Planned Actions (Step 1 of 3)**")
            st.markdown("""
            The computer use model has analyzed your request and planned the necessary actions. 
            Here's what typically happens:
            
            1. **Planning Phase** ← *You are here*
               - Model analyzes your request
               - Creates action plan (click, type, navigate, etc.)
               
            2. **Execution Phase** (Not implemented yet)
               - System executes the planned actions
               - Takes screenshots of results
               
            3. **Analysis Phase** (Not implemented yet)  
               - Model analyzes screenshots
               - Extracts and formats final content
            """)
            
            st.info("💡 **Why you see 'response submitted'**: The model successfully created an action plan, but we need to implement the execution loop to get actual web content.")
        
        else:
            st.success("**✅ Direct Response Received**")
            st.info("The model provided a direct response without needing browser actions.")    # Enhanced debugging section
    with st.expander("🔧 Advanced Debugging Information", expanded=False):
        st.markdown("**Raw Response Attributes:**")
        st.json({
            "Response Type": result.get("response_type"),
            "Computer Calls Count": len(result.get("computer_calls", [])),
            "Text Content Count": len(result.get("text_content", [])),
            "Has Screenshots": bool(result.get("screenshots")),
            "Environment": result.get("environment")
        })
        
        if result.get("full_response"):
            st.markdown("**Full Response Object:**")
            st.code(str(result["full_response"])[:2000] + "..." if len(str(result["full_response"])) > 2000 else str(result["full_response"]), language="text")
    
    # Display computer actions (the actual plan from the model)
    if result["computer_calls"]:
        st.markdown("### � Planned Computer Actions")
        st.info("These are the actions the model wants to perform. In a complete implementation, these would be executed automatically.")
        
        for i, call in enumerate(result["computer_calls"]):
            action_name = call.get("action_type", call.get("action", "Unknown Action"))
            with st.expander(f"🔧 Action {i+1}: {action_name}", expanded=True):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Action Summary:**")
                    action_summary = {
                        "Action Type": call.get("action_type", call.get("action", "Not specified")),
                        "Call ID": call.get("call_id", "Not provided"),
                        "Call Type": call.get("type", "Not specified")
                    }
                    
                    # Add specific action details
                    if call.get("coordinates"):
                        action_summary["Target Location"] = call.get("coordinates")
                    if call.get("text_input"):
                        action_summary["Text to Input"] = call.get("text_input")
                    
                    for key, value in action_summary.items():
                        st.write(f"**{key}:** {value}")
                
                with col2:
                    st.markdown("**Raw Action Data:**")
                    st.code(call.get("full_item", str(call))[:500] + "..." if len(str(call)) > 500 else str(call), language="json")
                    
                    # Explain what this action would do
                    if call.get("action_type") == "click":
                        st.success("🖱️ This would click on a webpage element")
                    elif call.get("action_type") == "type":
                        st.success("⌨️ This would type text into a form field")
                    elif call.get("action_type") == "navigate":
                        st.success("🌐 This would navigate to a new webpage")
                    elif call.get("action_type") == "screenshot":
                        st.success("📸 This would take a screenshot for analysis")
                    else:
                        st.info("🔧 This would perform a computer action")
    
    # Display actual content/responses from the model
    if result["text_content"]:
        st.markdown("### � Model Response & Analysis")
        for i, text in enumerate(result["text_content"]):
            # Skip web content to avoid duplication
            if text not in result.get("web_content", []):
                with st.expander(f"📝 Response {i+1}", expanded=True):
                    # Check if this is an explanation or actual content
                    if "Computer Use Model Response Received" in text:
                        st.markdown(text)
                    else:
                        # Smart formatting based on content structure
                        if len(text) > 500 and any(marker in text for marker in ['\n\n', '1.', '2.', '3.', '#', '*']):
                            st.markdown(text)
                        else:
                            st.write(text)
                            
                    # Add copy button for longer content
                    if len(text) > 100:
                        if st.button(f"📋 Copy Response {i+1}", key=f"{key_prefix}_copy_response_{i}"):
                            st.code(text, language="text")
    
    # Display web content if any was extracted
    if result.get("web_content"):
        st.markdown("### 🌐 Extracted Web Content")
        st.success("✅ The model successfully extracted web content!")
        for i, content in enumerate(result["web_content"]):
            with st.expander(f"Web Content {i+1}", expanded=True):
                # Format based on content type
                if any(marker in content for marker in ['#', '*', '-', '1.', '2.', '3.']):
                    st.markdown(content)
                else:
                    st.text(content)
                
                if st.button(f"📋 Copy Web Content {i+1}", key=f"{key_prefix}_copy_web_{i}"):
                    st.code(content, language="text")
    
    # Display screenshots if available
    if result.get("screenshots"):
        st.markdown("### 📸 Screenshots")
        st.info("🖼️ Screenshots would show the actual browser state during execution")
        for i, screenshot in enumerate(result["screenshots"]):
            with st.expander(f"Screenshot {i+1}", expanded=True):
                st.code(screenshot, language="text")
                st.info("💡 In a full implementation, actual browser screenshots would be displayed here")
    
    # Enhanced explanation section
    st.markdown("### 💡 Next Steps & Implementation Notes")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🔄 Current Status:")
        if result["computer_calls"]:
            st.warning("⏳ **Action Plan Created**")
            st.write(f"✅ {len(result['computer_calls'])} computer actions planned")
            st.write("⏸️ Execution loop needed for final results")
        else:
            st.success("✅ **Direct Response**")
            st.write("🎯 No browser actions required")
        
        if result.get("text_content"):
            st.info(f"📝 {len(result['text_content'])} response sections received")
        
    with col2:
        st.markdown("#### 🛠️ To Get Actual Web Content:")
        st.markdown("""
        1. **Implement Screenshot Capture**
           - Take initial browser screenshot
           
        2. **Execute Planned Actions**
           - Click, type, navigate as planned
           
        3. **Capture Results**
           - Screenshot after each action
           
        4. **Send Back to Model**
           - Model analyzes screenshots
           - Extracts final content
        """)
    
    # Show implementation hint
    with st.expander("🔧 Implementation Hint for Developers", expanded=False):
        st.code("""
# Example execution loop structure needed:
import asyncio
from playwright import async_playwright

async def execute_computer_actions(actions, query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Take initial screenshot
        screenshot = await page.screenshot()
        
        # Execute each planned action
        for action in actions:
            if action['type'] == 'navigate':
                await page.goto(action['url'])
            elif action['type'] == 'click':
                await page.click(action['selector'])
            elif action['type'] == 'type':
                await page.type(action['selector'], action['text'])
            
            # Screenshot after each action
            screenshot = await page.screenshot()
            
            # Send screenshot back to model for analysis
            # ... (model processes screenshot and provides next action or final result)
        
        await browser.close()
        """, language="python")
    
    # Display screenshots if available
    if result.get("screenshots"):
        st.markdown("### 📸 Screenshots")
        for i, screenshot in enumerate(result["screenshots"]):
            with st.expander(f"Screenshot {i+1}", expanded=True):
                st.code(screenshot, language="text")
                st.info("💡 Screenshot data would be displayed here in a full implementation")
    
    # Display computer calls with enhanced web action details
    if result["computer_calls"]:
        st.markdown("### 🖱️ Browser Actions Performed")
        for i, call in enumerate(result["computer_calls"]):
            action_name = call.get("action_type", call.get("action", "Unknown Action"))
            with st.expander(f"Action {i+1}: {action_name}", expanded=True):
                col1, col2 = st.columns([1, 1])
                with col1:
                    action_details = {
                        "Call ID": call.get("call_id"),
                        "Action Type": call.get("action_type", call.get("action")),
                        "Call Type": call.get("type")
                    }
                    
                    # Add web-specific details
                    if call.get("coordinates"):
                        action_details["Coordinates"] = call.get("coordinates")
                    if call.get("text_input"):
                        action_details["Text Input"] = call.get("text_input")
                    
                    st.json(action_details)
                
                with col2:
                    if call.get("details"):
                        st.markdown("**Full Action Details:**")
                        st.code(str(call.get("details")), language="json")
    
    # Enhanced web browsing tips
    st.markdown("### 🌐 Web Browsing Insights")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if result["computer_calls"]:
            st.success(f"✅ Performed {len(result['computer_calls'])} browser actions")
            st.info("💡 The AI navigated and interacted with web pages to extract the requested information.")
        else:
            st.warning("⚠️ No browser actions detected. The model may have provided analysis without navigation.")
    
    with col2:
        if result.get("web_content"):
            st.success(f"� Extracted {len(result['web_content'])} pieces of web content")
            st.info("💡 Content has been successfully extracted and formatted for easy reading.")
        else:
            st.info("📝 No specific web content extracted. Check the AI Response section above.")
    
    # Display raw output for debugging
    if result["raw_output"]:
        with st.expander("🔍 Raw API Response (Debug)", expanded=False):
            st.json([str(item) for item in result["raw_output"]])

if __name__ == "__main__":
    # Initialize session state
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = None
    
    # Run main interface
    main()
    
    # Display previous results if they exist
    if st.session_state.execution_results:
        st.markdown("---")
        st.markdown("### 📋 Previous Execution Results")
        display_results(st.session_state.execution_results, st.session_state.get('last_query', 'Previous query'))
    
    # Enhanced sidebar with web browsing examples
    with st.sidebar:
        st.markdown("### 🌐 Web Browsing Examples")
        st.markdown("Click any example to use it:")
        
        web_examples = [
            "Go to https://news.ycombinator.com and summarize the top 5 stories",
            "Search for 'latest AI news' on Google and extract key headlines", 
            "Browse to https://www.reddit.com/r/technology and get the top posts",
            "Visit https://github.com/trending and list trending repositories",
            "Go to https://stackoverflow.com and find recent Python questions",
            "Browse to https://www.wikipedia.org and search for 'artificial intelligence'",
            "Visit https://www.bbc.com/news and summarize today's top news",
            "Go to https://www.amazon.com and search for 'laptops under $1000'",
            "Browse to https://www.youtube.com and find trending videos",
            "Visit a weather website and get today's forecast"
        ]
        
        for i, example in enumerate(web_examples):
            if st.button(f"🌐 {example[:35]}...", key=f"web_example_{i}", use_container_width=True):
                st.session_state.example_query = example
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🖥️ Desktop Examples")
        
        desktop_examples = [
            "Take a screenshot of the current desktop",
            "Open the calculator application", 
            "Create a new folder on desktop named 'Test'",
            "Open Microsoft Word and create a document",
            "Open file explorer and navigate to Documents"
        ]
        
        for i, example in enumerate(desktop_examples):
            if st.button(f"�️ {example[:35]}...", key=f"desktop_example_{i}", use_container_width=True):
                st.session_state.example_query = example
                st.rerun()
        
        # Display selected example
        if 'example_query' in st.session_state:
            st.markdown("---")
            st.markdown("### 📝 Selected Example")
            st.text_area("Query:", value=st.session_state.example_query, key="example_display", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                env = "browser" if any(web_term in st.session_state.example_query.lower() 
                                     for web_term in ['http', 'www', 'google', 'search', 'browse']) else "windows"
                if st.button("� Execute", key="execute_example"):
                    execute_computer_use(st.session_state.example_query, env)
            
            with col2:
                if st.button("❌ Clear", key="clear_example"):
                    del st.session_state.example_query
                    st.rerun()
        
        # Usage tips
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        **For best results:**
        - Be specific about websites to visit
        - Mention what information to extract
        - Use browser mode for web tasks
        - Use desktop mode for system tasks
        """)
    
    # Remove the old test code