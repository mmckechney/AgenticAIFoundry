import asyncio
from datetime import datetime
import streamlit as st
import os
import openai
from typing import List, Sequence

from dotenv import load_dotenv
load_dotenv()

model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = "model-router"
deployment = "model-router"

client = openai.AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key = os.getenv("AZURE_OPENAI_KEY"),
        api_version = "2024-12-01-preview",
        azure_deployment=model_name,
    )

def model_router(query: str) -> str:

    txtreturn = ""
    txtmodelused = ""
    starttime = datetime.now()
    txtmessages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": f"{query}",
        }
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=txtmessages,
        max_tokens=8192,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    endtime = datetime.now()
    
    txtreturn = response.choices[0].message.content.strip() + "\n"
    txtreturn += f"Response Time: {endtime - starttime}\n"
    # txtreturn += "Response Model Used: " + response.model + "\n"

    txtmodelused += "Response Model Used: " + response.model + "\n"

    return txtreturn, txtmodelused

def routermain():
    st.title("Model Router")
    st.write("This application routes queries to different models based on the content of the query.")
    
    query = st.text_input("Enter your query:")
    
    if st.button("Submit"):
        if query:
            with st.spinner("Processing..."):
                txtreturn, txtmodelused = model_router(query)
                st.success("Response received!")
                st.write(txtmodelused)
                st.text_area("Response", value=txtreturn, height=300)
        else:
            st.error("Please enter a query before submitting.")

if __name__ == "__main__":
    routermain()