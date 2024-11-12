from langchain_core.messages import AIMessage, HumanMessage

PROMPT_CATEGORIZE_LINE_ITEMS = """
You are an expert analyst in the procurement sector. You will be given information describing a category \
and a list of dicts, describing each some properties about a line item being quoted by a provider for a \
client's project. Your task consists in mapping each item to one element in the category. In some exceptional \
cases, you might find that an item does not map to any element in the category. In that case, you can return \
the special value "Other".

The user will send you a message formatted as follows: \
```
{{
    "category_metadata": {{
        "name": <the name of the category>,
        "elements": <the values to categorize on for this category>,
        "source_columns": <the list of columns that are needed to map the elmenents of this category>
    }},
    "items": {{
        "0": {{<source_column_1> : <value_11>, "source_column2": <value12>, ...}},
        "1": {{<source_column_1> : <value_21>, "source_column2": <value22>, ...}},
        ...
    }}
}}
```
Please respond in the following json format:
{{
    "0": <element that maps to item 0>,
    "1": <element that maps to item 1>,
    ...
}}
"""


FEW_SHOT_EXAMPLES_CATEGORIZE_LINE_ITEMS: tuple = (
    HumanMessage(
        content="""
{{
    "category_metadata": {{
        "name": "Type of food",
        "elements": ["Fruit", "Vegetable", "Dairy"],
        "source_columns": ["Item Name", "Item Description"]
    }},
    "items": {{
        "0": {{"Item Name": "Apple", "Item Description": "Sweet"}},
        "1": {{"Item Name": "Milk", "Item Description": "Cows from England"}},
        "2": {{"Item Name": "V_34", "Item Description": "Broccoli"}},
        "3": {{"Item Name": "Apple", "Item Description": "Sour"}},
        "4": {{"Item Name": "DWQR_87", "Item Description": "Strawberries"}},
        "5": {{"Item Name": "Milk", "Item Description": "Soya based"}}
    }}
}}"""
    ),
    AIMessage(
        content="""
{{
    "0": "Fruit",
    "1": "Dairy",
    "2": "Vegetable",
    "3": "Fruit",
    "4": "Fruit",
    "5": "Other"
}}"""
    ),
)
