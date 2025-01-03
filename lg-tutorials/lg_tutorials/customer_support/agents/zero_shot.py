from datetime import datetime
from typing import Annotated, Optional

from lang_examples_common.utils.langgraph_utils import SimpleState
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.message import AnyMessage, add_messages
from lg_tutorials.customer_support.tools.car_rental import (
    book_car_rental,
    cancel_car_rental,
    search_car_rentals,
    update_car_rental,
)
from lg_tutorials.customer_support.tools.excursions import (
    book_excursion,
    cancel_excursion,
    search_trip_recommendations,
    update_excursion,
)
from lg_tutorials.customer_support.tools.flights import (
    cancel_ticket,
    fetch_user_flight_information,
    search_flights,
    update_ticket_to_new_flight,
)
from lg_tutorials.customer_support.tools.hotels import (
    book_hotel,
    cancel_hotel,
    search_hotels,
    update_hotel,
)
from lg_tutorials.customer_support.tools.policies import lookup_policy


class Assistant:

    part_1_tools = [
        TavilySearchResults(max_results=1),
        fetch_user_flight_information,
        search_flights,
        update_ticket_to_new_flight,
        cancel_ticket,
        lookup_policy,
        search_car_rentals,
        book_car_rental,
        update_car_rental,
        cancel_car_rental,
        search_hotels,
        book_hotel,
        update_hotel,
        cancel_hotel,
        search_trip_recommendations,
        book_excursion,
        update_excursion,
        cancel_excursion,
    ]
    system_message = """You are a helpful customer support assistant for Swiss Airlines. 
                 Use the provided tools to search for flights, company policies, and other information to assist the user's queries. 
                 When searching, be persistent. Expand your query bounds if the first search returns no results. 
                 If a search comes up empty, expand your search before giving up.
                \n\nCurrent user:\n<User>\n{user_info}\n</User>
                \nCurrent time: {time}."""

    def __init__(self, llm, system_message: Optional[str] = None, invoke_config: Optional[str] = None):
        primary_assistant_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message or self.system_message),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now)
        self.runnable = primary_assistant_prompt | llm.bind_tools(self.part_1_tools)
        self.invoke_config = invoke_config or dict()

    def __call__(self, state: SimpleState, config: RunnableConfig):
        # Run a while True to re-run the assistant until it returns a non-empty response.
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id, "db": configuration["db"]}
            result = self.runnable.invoke(state, config=self.invoke_config)
            # import pdb; pdb.set_trace()
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
