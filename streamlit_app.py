import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Get configuration settings 
load_dotenv()
azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
azure_oai_key = os.getenv("AZURE_OAI_KEY")
azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_search_key = os.getenv("AZURE_SEARCH_KEY")
azure_search_index = os.getenv("AZURE_SEARCH_INDEX")
azure_search_index_2 = os.getenv("AZURE_SEARCH_INDEX_2")

# Show title and description.
st.title("💬 POC - Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses."
)

# Create an OpenAI client.
client = AzureOpenAI(
        azure_endpoint = azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2024-08-01-preview"
        )

# Configure your data source
extension_config = dict(dataSources = [  
    { 
        "type": "AzureCognitiveSearch", 
        "parameters": { 
            "endpoint":azure_search_endpoint, 
            "key": azure_search_key, 
            "indexName": azure_search_index,
        }
    }
    ]
)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Generate a response using the OpenAI API.
    stream = client.chat.completions.create(
        model=azure_oai_deployment,
        messages=[
            {"role": "system", "content": "You are an assistant and you retrieve project names, users based on CV and you're capable on determining who worked on a project."},
            *[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        ],
        stream=True,
        extra_body={
            "data_sources":[
                
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": azure_search_endpoint,
                        "index_name": azure_search_index_2,
                        "authentication": {
                            "type": "api_key",
                            "key": azure_search_key,
                        }
                    }
                }
            ],
        }
    )

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response}) 

    #print("Citations:")
    #citations = stream.choices[0].message.context["messages"][0]["content"]
    #citation_json = json.loads(citations)
    #for c in citation_json["citations"]:
    #    print("  Title: " + c['title'] + "\n    URL: " + c['url'])
