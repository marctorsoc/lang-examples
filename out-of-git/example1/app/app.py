from uuid import uuid4

import openai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig

from langfuse_tutorial.app.tools import DataProcessingToolWithMath, create_agent_prompt
from langfuse_tutorial.example1.data_extraction.utils import read_excel
from langfuse_tutorial.io import read_consolidated_summary_sheet
from langfuse_tutorial.llm import create_chat_model
from langfuse_tutorial.paths import ENV_PATH

assert load_dotenv(ENV_PATH), "Failed to load .env file"


# Setup memory for contextual conversation
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs, return_messages=True)


def create_agent(dfs):
    chat_llm = create_chat_model(temperature=0.8, streaming=True)
    prompt = create_agent_prompt()
    tool_llm = create_chat_model(temperature=0.5, streaming=True, deployment_id="ai-gpt-4")
    tools = [
        DataProcessingToolWithMath(
            dfs=dfs,
            llm=tool_llm,
            budget=0,
        )
    ]
    # tools = [DataProcessingToolWithMath(dfs=dfs, llm=tool_llm)]
    agent = create_openai_tools_agent(chat_llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
    )


# Streamlit app layout
st.set_page_config(
    page_title="Pricing proposals extractor",
    page_icon="🦜",
    layout="wide",
)

st.title("Pricing proposals extractor")

st.text(f'Keys in state: {list(st.session_state.keys())}')

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = str(uuid4())
uploaded_files = st.sidebar.file_uploader(
    label="Upload Excel submission files",
    type=["xlsx"],
    key=st.session_state.uploader_key,
    accept_multiple_files=True,
    help="Some hints on what to do",
)
st.text(f'Uploaded files: {uploaded_files}')
if uploaded_files:
    files_content = list(map(read_excel,uploaded_files))
    file_content_widgets = []
    for uploaded_file, file_content in zip(uploaded_files, files_content):
        st.subheader(f"File Content for {uploaded_file.name}")
        for table_name, df in file_content.items():
            with st.expander(table_name.replace("_", " ").title()):
                widget = st.dataframe(df)
                file_content_widgets.append(widget)
        if st.button("Analyze"):
            with st.spinner("Analyzing"):
                prompt = f"The following is the content of a file:\n{file_content}\n\nWhat insights can you provide?"
                # response = get_llm_response(prompt)
                response = "lalala"
                st.subheader("Agent Thoughts and Answers")
                st.text(response)

if st.sidebar.button("Clear State"):
    st.session_state.clear()
    st.session_state.uploader_key = str(uuid4())
    st.experimental_rerun()
