from typing import Annotated, TypedDict

from IPython.display import Image, display
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph


def plot_langgraph(graph: CompiledStateGraph):
    display(Image(graph.get_graph().draw_mermaid_png()))


class SimpleState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def chatbot_node(llm, system_message=None, invoke_config=dict()):
    def chatbot_function(state):
        messages = state["messages"]
        if system_message:
            messages = [system_message] + messages
        return {"messages": [llm.invoke(messages, config=invoke_config)]}
    return chatbot_function
