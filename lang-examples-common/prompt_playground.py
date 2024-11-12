"""
Run the app with:
streamlit run prompt_playground.py --server.port 8504
"""

import streamlit as st
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langfuse import Langfuse
from langfuse.callback.langchain import LangchainCallbackHandler

from langfuse_tutorial.paths import ENV_PATH
from langfuse_tutorial.utils.llm_utils import get_chat_llm

assert load_dotenv(ENV_PATH, override=True), "Failed to load .env file"


def fetch_trace(trace_id):
    try:
        return langfuse.get_trace(trace_id)
    except Exception as e:
        st.error(f"Error fetching trace: {e}")
        return None


def get_generations(trace):
    return [
        observation
        for observation in trace.observations
        if observation.type == "GENERATION"
    ]


def read_updated_prompts(inputs):
    updated_input = []
    for role, message in inputs:
        schema = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}[role]
        updated_input.append(schema(content=message))
    return updated_input


def text_area(label, text, key, disabled=False):
    height = max(min(20 * int(len(text.split()) / 20), 400), 20)
    return st.text_area(
        label,
        value=text,
        key=key,
        height=height,
        disabled=disabled,
    )


def generation_output(label, content):
    if content.startswith("```") or content.startswith("{"):
        st.text(label)
        st.code(content, language="json", line_numbers=False)
    else:
        st.text_area(label, content, disabled=True)


langfuse = Langfuse()

st.title("Langfuse Trace Playground")

# Initialize or maintain LLM and temperature in session state
if "llm_name" not in st.session_state:
    st.session_state.llm_name = "gpt-4o"
# if 'temperature' not in st.session_state:
# st.session_state.temperature = 0.0

# Sidebar widgets
st.session_state.llm_name = st.sidebar.selectbox(
    "Select LLM:",
    ["gpt-4o-mini", "gpt-4o"],
    index=["gpt-4o-mini", "gpt-4o"].index(st.session_state.llm_name),
)
# st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
# llm = get_chat_llm(model_name=st.session_state.llm_name.upper(), temperature=st.session_state.temperature)
llm = get_chat_llm(model_name=st.session_state.llm_name.upper(), temperature=0)
trace_id = st.text_input("Enter Trace ID:")

# Only fetch the trace if a new trace_id is provided
if trace_id and trace_id != st.session_state.get("trace_id"):
    st.session_state.trace_id = trace_id
    trace = fetch_trace(trace_id)
    if trace:
        st.session_state.generations = get_generations(trace)
        st.session_state.generation_index = None
        st.session_state.updated_inputs = []

if generations := st.session_state.get("generations"):
    generation_labels = [
        f"Generation {i+1}: {gen.promptTokens} → {gen.completionTokens}"
        for i, gen in enumerate(st.session_state.generations)
    ]
    selected_generation = st.selectbox("Select a Generation:", generation_labels)
    selected_index = generation_labels.index(selected_generation)

    if selected_index != st.session_state.get("generation_index"):
        selected_generation_data = generations[selected_index]
        # if not st.session_state.updated_inputs:
        st.session_state.updated_inputs = [
            (input["role"], input["content"])
            for input in selected_generation_data.input
        ]

if st.session_state.get("updated_inputs"):
    with st.form("generation_form", clear_on_submit=False):
        inputs = []
        st.write("Generation Inputs:")
        for i, (role, message) in enumerate(st.session_state.updated_inputs):
            updated_message = text_area(role, message, key=f"input_{i}")
            inputs.append((role, updated_message))

        submitted = st.form_submit_button("Re-run")
        generation_output("Original Output", selected_generation_data.output["content"])

        if submitted:
            st.session_state.updated_inputs = inputs
            result = llm.invoke(
                read_updated_prompts(st.session_state.updated_inputs),
                config={
                    "callbacks": [
                        LangchainCallbackHandler(trace_name="playground", tags=[trace_id])
                    ]
                },
            )
            generation_output("New Output", result.content.strip())
