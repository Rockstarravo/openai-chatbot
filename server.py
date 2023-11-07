import openai
import pandas as pd
import streamlit as st
from io import StringIO
from st_files_connection import FilesConnection

#pulling the key from the streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]


def embedding_s3_file():
            conn = st.connection('s3', type=FilesConnection)
            dataframe_result = conn.read("bucketname/file", input_format="csv", ttl=500)
            return dataframe_result

st.title("Q/A Conversational Bot")


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Type Something here"):
    with st.chat_message("user"):
        st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
      
    if user_input in "upload s3 file":
        df2=embedding_s3_file()
        st.session_state.messages.append({"role": "user", "content": "kindly process my data "+ str(df2)})
        print(st.session_state.messages)
      
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
