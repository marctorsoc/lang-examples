import json
import os
import re
from typing import Callable

import tiktoken
from dotenv import load_dotenv
from lang_examples_common.paths import ENV_PATH
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from pydantic import BaseModel

assert load_dotenv(ENV_PATH, override=True), "Failed to load .env file"

def get_family(model):
    if "llama" in model:
        return "llama"
    elif "gpt" in model:
        return "openai"
    else:
        raise NotImplementedError(f"Unknown model: {model}")

def get_chat_llm(
    model="llama3-groq-tool-use:latest",  # "gpt-4o-mini", "llama3-groq-tool-use:latest", "llama3"
    family=None,  # openai, llama
    temperature: float = 0.0,
    max_retries: int = 3,
    **llm_kwargs,
):
    if family is None:
        family = get_family(model)
        
    if family != "llama":
        env_name = f"{family.upper()}_API_KEY"
        llm_kwargs["api_key"] = os.getenv(env_name)

    match family:
        case "openai":
            constructor = ChatOpenAI
        case "llama":
            constructor = ChatOllama

    llm = constructor(
        model=model,
        temperature=temperature,
        max_retries=max_retries,
        request_timeout=60,
        **llm_kwargs,
    )
    return llm


def create_chain(
    prompt_message,
    pydantic_object: BaseModel | None = None,
    partial_kwargs: dict = {},
    model_name="llama3.2",
    family="llama",
    temperature=0,
    few_shot_examples: tuple = (),
    **llm_kwargs,
):
    """
    Create a simple chain `prompt | llm | parser`.
    If pydantic_object is passed, then use it to
        - add `format_instructions` to the prompt
        - add a PydanticOutputParser to the chain
    else:
        - add a SimpleJsonOutputParser to the chain
    """
    llm = get_chat_llm(model=model_name, family=family, temperature=temperature, **llm_kwargs)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_message),
            *few_shot_examples,
            ("human", "{query}"),
        ]
    ).partial(**partial_kwargs)

    if pydantic_object is not None:
        parser = PydanticOutputParser(pydantic_object=pydantic_object)  # type: ignore
        prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    else:
        parser = SimpleJsonOutputParser()

    return prompt | llm | RunnableLambda(postprocess_llm_output) | parser


def postprocess_llm_output(llm_output):
    new_output = (
        llm_output.content.replace("{{", "{").replace("}}", "}").replace("\\/", "/")
    )
    try:
        json.loads(new_output)
        json_decodable = True
    except:
        json_decodable = False

    if json_decodable:
        return new_output

    # remove trailing commas
    return re.sub(r",\s*([\]}])", r"\1", new_output)


def invoke_with_retries(
    chain,
    query,
    validator: Callable | None = None,
    name: str = "",
    session_id: str = "",
    tags: list[str] = [],
    visualizer: Callable | None = None,
    max_retries: int = 5,
    logger: Callable = print,
):
    """
    Run invoke a max of `max_retries` times, using a `validator` and potentially
    showing failures via the `visualizer`. It logs everything to langfuse, as long
    as it is enabled.

    Returns the response, or None if the chain failed to complete.
    """
    name = name if name else "chain"
    session_id = session_id if session_id else "session"

    # it seems like host needs to be passed and does not get read from env vars.
    # Tried without it and was getting errors
    langfuse_handler = CallbackHandler(
        trace_name=name,
        host=os.environ["LANGFUSE_HOST"],
        tags=list(tags),  # avoid modifying the original list
        session_id=session_id,
    )

    response = None
    for i in range(max_retries):
        try:
            response = chain.invoke(
                dict(query=query), config=dict(callbacks=[langfuse_handler])
            )
            if validator is not None:
                validator(response)
            if i > 0:
                logger(f"Success on `{name}` after {i} retries")
            return response
        except Exception as e:
            logger(str(e))
            if response and visualizer is not None:
                visualizer(response)

            logger(f"Retrying `{name}` ({i + 1}/{max_retries})")
            langfuse_handler.trace_name = f"{name} (retry {i + 1})"
            if "retry" not in langfuse_handler.tags:
                langfuse_handler.tags.append("retry")

    logger("Failed to get response from LLM")
    return None


def num_tokens_from_string(string: str, encoding_name: str = "ada") -> int:
    """
    Returns the number of tokens in a text string.
    "ada" uses "cl100k_base", which works for text-embedding-ada-002, gpt-3.5-turbo and gpt-4
    See https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
