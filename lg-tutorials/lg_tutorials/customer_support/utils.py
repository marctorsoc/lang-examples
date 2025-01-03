import json
import logging

from lang_examples_common.utils.display_utils import wrap_text
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

logging.basicConfig(format="%(asctime)s - %(message)s")
log = logging.getLogger("lang-examples")
log.setLevel(logging.INFO)


def handle_tool_error(state) -> dict:
    # this "error" key is the one we specify below as "exception_key"
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)],
        exception_key="error",
    )


# def _print_event(event: dict, _printed: set, max_length=1500):
#     # Original from the tutorial, for streaming
#     current_state = event.get("dialog_state")
#     if current_state:
#         print("Currently in: ", current_state[-1])
#     message = event.get("messages")
#     if message:
#         if isinstance(message, list):
#             message = message[-1]
#         if message.id not in _printed:
#             msg_repr = message.pretty_repr(html=True)
#             if len(msg_repr) > max_length:
#                 msg_repr = msg_repr[:max_length] + " ... (truncated)"
#             print(msg_repr)
#             _printed.add(message.id)


def print_message(message, max_length=1500):
    """
    Used for invoke (not streaming), adding emojis and print_wrapped
    """
    # print(type(message))
    tool_name = None
    if message.type == "human":
        emoji = "👨"
    elif message.type == "ai":
        emoji = "🤖"
    elif message.type == "tool":
        emoji = "🛠️"
        tool_name = message.name
    else:
        import pdb

        pdb.set_trace()

    content = ""
    if message.content:
        try:
            content = "\n" + json.dumps(json.loads(message.content), indent=4)
        except:
            content = wrap_text(message.content, max_length)
        
        if tool_name:
            content = tool_name + content

    if getattr(message, "tool_calls", None):
        content += "Using tools:\n" + json.dumps(message.tool_calls, indent=4)
    
    content = f"{emoji} - {content}"
    # import pdb; pdb.set_trace()
    print(content, flush=True)
