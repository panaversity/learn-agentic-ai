# Tools
Check out the OpenAI Agents Python tools documentation:
https://openai.github.io/openai-agents-python/tools/

The three main tool types are:
- Function tools: Tools that execute Python functions
- Code tools: Tools that execute arbitrary code
- Retrieval tools: Tools that retrieve information from external sources

`uv add openai-agents python-dotenv chainlit`

Give these commands to run the project:

    cd chatbot

    uv venv

On Mac:

    source .venv/bin/activate

Using uv to run the project

    uv run chainlit run main.py -w