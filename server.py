#dowload teh packages
import openai
import pandas as pd
import streamlit as st
import boto3
from io import StringIO
from st_files_connection import FilesConnection

#pulling the key from the streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# define when we intent the pull the file and feed to the bot
def embedding_s3_file(bucketname,folder_path,filename):
            conn = st.connection('s3', type=FilesConnection)
            dataframe_result = conn.read("bucketname/file", input_format="csv", ttl=500)
            return dataframe_result

def get_all_s3_files(bucketname,folder_prefix):
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        file_list = [content['Key'] for content in response.get('Contents', [])]
        return file_list

    except Exception as e:
        st.error(f"Error: {e}")

# Setting up the title
st.title("Q/A Conversational Bot")

# bumping up the session state and holding the values
# declare the openai_model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Addign messages to carry out the messages on conversations 
# On Each phase of the chat, we need to ensure responses should be appending to messages, On failure case Chatbot couldnt provide accurate data on loosen history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Below loop responsible to populate the messages on existance
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input will be validated here and chats published as an array to llm model which evetually responds by processing the orior conversations
if user_input := st.chat_input("Type Something here"):
    with st.chat_message("user"):
        st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

# During file read, below one will be invoked (user_input="upload s3 file")            
    if user_input in "upload s3 file":
        filenames=get_all_s3_files("bucket_name","folder_name")
        for j in filenames:
            content = embedding_s3_file("bucket_name","folder_name",j)
            st.session_state.messages.append({"role": "user", "content": "kindly process my data "+ str(content)})
        print(st.session_state.messages)

# Here we go bot side processing which begins up the empty value and holds the response from gpt model
# Condtion openai.ChatCompletion.create() works on executing the user intent and reverts with suitable answer
    with st.chat_message("bot"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "bot", "content": full_response})
