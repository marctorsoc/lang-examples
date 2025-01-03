# lang-examples

Examples and good practices on langgraph, langfuse, and friends.

# Getting Started

For any example to your work, you'll need to install the common package:
```bash
cd lang-examples-common
uv pip install -r pyproject.toml
uv pip install -e .
```
I strongly recommend using `uv`, but if you don't have it installed, simply
remove it from the command. I also recommend using `conda` environments for
each example.

## (Optional) Set up ollama

If using ollama, we need to:

1. Install. Download for Mac, then leave it running
2. Run `ollama run llama3.2`

After the download, we can quit with Ctrl+D, and it will continue in the background.
Check models with `ollama ls` and those running with `ollama ps`. 
When done, use `ollama stop llama3.2`.


## (Optional) Create env.private file

If we use openAI, we need `.env.private` file with the following environment variables:
```
OPENAI_API_KEY=sk-...
ORGANIZATION_ID=org-...
ORGANIATION_NAME=...
```

## Starting langfuse

Open a a tmux session and run the following command:
```
docker compose up
```
Note that you will need to have Docker installed and enabled on your system for this to start. This should start langfuse. After this, you should go to http://localhost:3000/ to see the langfuse platform.

From here, you should create a project, create API keys, and paste them into the .env.private file
as `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`. Please follow langfuse docs for this.

## Starting the prompt playground

Now, start the playground by running the following command:
```
streamlit run prompt_playground.py --server.port 8504
```
This will open the playground on your browser, on port 8504.


- show how to track time and money spent on LLM calls


# FAQs

- what if you want to run langfuse and prompt playground in my EC2 instance?

Tunnel!

- what if you want to access the streamlit app from a device (e.g. your phone)
connected to the same local network?

In Mac, you can just disable the firewall (caution with this!), and then connect to the local IP address of the streamlit app, e.g. http://192.168.1.10:8504.

