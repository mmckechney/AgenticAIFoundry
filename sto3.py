import os
import base64
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()
      
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_WEST")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_WEST")
      
# Initialize Azure OpenAI client with Entra ID authentication
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2025-01-01-preview",
)


def o3_main(query: str) -> str:
    returntxt = ""
    chat_prompt = [
        {
            "role": "user",
            # "content": "Explain quantum particle and help me understand its implications in quantum computing."
            "content": query
        }
    ]

    # Include speech result if speech is enabled
    messages = chat_prompt

    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        #max_tokens=800,
        #temperature=0.7,
        #top_p=0.95,
        #frequency_penalty=0,
        #presence_penalty=0,
        #stop=None,
        #stream=False
    )

    # print(completion.to_json())
    print("Response:", completion.choices[0].message.content)
    returntxt = completion.choices[0].message.content

    return returntxt

def o3deep_chat():
    st.set_page_config(
        page_title="US Tariff AI Assistant",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🛠️ US Tariff AI Assistant")
    st.write("Ask questions about US tariffs and get detailed information from our comprehensive database.")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a scrollable container for chat history
    st.markdown("### 💬 Chat History")
    
    # Display chat history in a scrollable container with enhanced styling
    if st.session_state.messages:
        # Add custom CSS for better scrollbar styling
        st.markdown("""
        <style>
        .chat-container {
            max-height: 600px; 
            overflow-y: auto; 
            padding: 20px; 
            border: 2px solid #e0e0e0; 
            border-radius: 12px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        .user-message {
            background: linear-gradient(135deg, #007acc 0%, #005999 100%); 
            color: white; 
            padding: 15px 18px; 
            border-radius: 20px; 
            margin: 12px 0 12px 60px; 
            max-width: 75%;
            margin-left: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            word-wrap: break-word;
        }
        .assistant-message {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
            color: #1565c0; 
            padding: 15px 18px; 
            border-radius: 20px; 
            margin: 12px 60px 12px 0; 
            max-width: 75%;
            border-left: 4px solid #2196f3;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            word-wrap: break-word;
        }
        .message-content {
            white-space: pre-wrap; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.4;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 O3 Assistant:</strong><br>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("💡 Start a conversation by asking a question about US tariffs in the input box below.")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Explain quantum particle and help me understand its implications in quantum computing?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show loading spinner while processing
        with st.spinner("🔍 Processing using o3 Deep research..."):
            try:
                # Call the tariff agent function
                response = o3_main(prompt)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Rerun to display the new messages
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing your request: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I apologize, but I encountered an error while processing your request: {str(e)}"
                })
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Chat History", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()

if __name__ == "__main__":
    o3deep_chat()

