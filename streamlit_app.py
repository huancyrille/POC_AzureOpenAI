import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import logging
import requests

logging.basicConfig(level=logging.DEBUG)

# Get configuration settings 
load_dotenv()


# Show title and description.
st.title("💬 POC - Chatbot")
st.write(
    "Chatbot assistant, retrieval of resume/profile informations."
)

url = "http://ovsearch.h9cnf8chdegwacgr.westeurope.azurecontainer.io:5200/answer"
headers = {
    "Content-Type": "application/json"
}


# Create an OpenAI client.
# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

data = dict()

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("Posez votre question:"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    data = dict(query = prompt)
    response = requests.post(url, headers=headers, json=data)

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response}) 

    #print("Citations:")
    #citations = stream.choices[0].message.context["messages"][0]["content"]
    #citation_json = json.loads(citations)
    #for c in citation_json["citations"]:
    #    print("  Title: " + c['title'] + "\n    URL: " + c['url'])
