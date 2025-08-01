# Agentic RAG

[Open Notebook in Google Colab](https://colab.research.google.com/drive/1QgAapf_z875sEev_O9COE7TPHIKEXx6r?usp=sharing)

# Code Explanation

This notebook demonstrates how to set up a Retrieval Augmented Generation (RAG) system using Google's Gemini models, ChromaDB for vector storage, and the OpenAI Agents SDK for orchestrating the process.

## Setup and Authentication

- **Imports:** Necessary libraries like `userdata`, `os`, `nest_asyncio`, `agents` (OpenAI Agents SDK), `chromadb`, `google.genai`, and `langchain_community.document_loaders` are imported.
- **Installations:** Key libraries are installed using `!pip install`.
- **API Key Setup:** The Gemini API key is fetched securely using `userdata.get('GEMINI_API_KEY')` and stored in `os.environ`. A check ensures the key is present.
- **Asyncio Patch:** `nest_asyncio.apply()` is used to make `asyncio` compatible with Jupyter/Colab environments.
- **Tracing:** `set_tracing_disabled(True)` is used to disable tracing for the Agents SDK, which can be helpful during development.

## Initializing Clients

- **ChromaDB Client:** `chromadb.Client()` initializes an in-memory ChromaDB instance for storing and searching vector embeddings.
- **Google GenAI Client:** `genai.Client(api_key=GEMINI_API_KEY)` initializes the Google GenAI client to interact with Gemini models for embedding and generation.
- **OpenAI-Compatible Client for Agents:** An `AsyncOpenAI` client is configured to point to the Gemini API endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`). This allows the Agents SDK, which is designed for OpenAI's API, to work with Gemini. `set_default_openai_client(external_client)` sets this up globally for the Agents SDK.

## Creating the Knowledge Base (Initial Data)

- **Documents:** A list of sample text documents (`documents`) and corresponding IDs (`doc_ids`) are defined.
- **Embedding Model:** The `gemini-embedding-exp-03-07` model is selected for generating embeddings.
- **Embedding Generation:** `client.models.embed_content` is used to generate embedding vectors for the documents. The `RETRIEVAL_DOCUMENT` task type is used for optimizing embeddings for retrieval.
- **ChromaDB Collection:** `chroma_client.get_or_create_collection(name="knowledge_base1")` creates or retrieves a collection in ChromaDB to store the documents and their embeddings.
- **Adding Data to Collection:** The documents, embeddings, and IDs are added to the ChromaDB collection using `collection.add()`. A try-except block is included to handle potential cases where the data already exists.

## Creating the RAG Tool

- **`answer_from_knowledge_base` function:** This Python function is decorated with `@function_tool` from the Agents SDK, making it available as a tool for the agent.
    - **Input:** Takes a `query` string as input.
    - **Embed Query:** The user query is embedded using the same Gemini embedding model, but with the `RETRIEVAL_QUERY` task type.
    - **Search ChromaDB:** `collection.query` is used to search the ChromaDB collection with the embedded query. It retrieves the top N most similar documents (set to `n_results=1` in this function).
    - **Retrieve Top Document:** The text content of the most relevant document is extracted from the query results.
    - **Construct Prompt:** A prompt is created combining the retrieved context and the user's question. This prompt instructs the language model to answer based *only* on the provided context.
    - **Generate Answer:** `client.models.generate_content` is used with the `gemini-1.5-flash` model to generate an answer based on the structured prompt.
    - **Return Answer:** The generated answer text is returned.

## Creating the Agent

- **`qa_agent`:** An `Agent` is created using the OpenAI Agents SDK.
    - **Name and Instructions:** The agent is given a name and instructions outlining its role (to use tools to find information in the knowledge base).
    - **Tools:** The `answer_from_knowledge_base` function is added to the agent's `tools` list, making it available for the agent to call.
    - **Model:** `OpenAIChatCompletionsModel` is used, configured with the `external_client` (the OpenAI-compatible client pointing to Gemini) and specifying the model name compatible with that endpoint (`gemini-1.5-flash-001`).

## Running the Agent

- **`main()` async function:**
    - **Agent Question:** A sample question is defined.
    - **Runner:** `Runner.run(qa_agent, agent_question)` executes the agent with the given question. The Agents SDK orchestrates the process, potentially deciding to call the `answer_from_knowledge_base` tool.
    - **Print Results:** The final output from the agent (the answer) is printed.
- **`if __name__ == "__main__": asyncio.run(main())`:** This ensures the `main()` async function is executed when the script is run.

## Adding PDF Data to the Knowledge Base

- **PDF Loading:**
    - `!pip install pypdf` installs the necessary library for handling PDFs.
    - `load_and_split_pdf(file_path)` function: Takes a PDF file path, uses `PyPDFLoader` to load it, and splits it into individual pages.
    - **File Upload:** `files.upload()` allows the user to upload a PDF file from their local machine to the Colab environment.
    - The uploaded file's path is obtained.
    - The PDF is loaded and split into pages using the `load_and_split_pdf` function.
- **Processing PDF Content:**
    - The text content is extracted from each PDF page.
    - Unique IDs are generated for each PDF page.
    - Embeddings are generated for the PDF page texts using the same Gemini embedding model and `RETRIEVAL_DOCUMENT` task type.
- **Adding PDF Data to ChromaDB:**
    - The `chroma_client.get_or_create_collection(name="knowledge_base1")` is used again to get the existing collection.
    - The PDF documents, embeddings, and IDs are added to the *same* collection. This merges the initial sample documents with the PDF content.
    - A try-except block handles potential duplicates.
- **Querying with PDF Content:**
    - The existing RAG tool (`answer_from_knowledge_base`) and agent (`qa_agent`) can now answer questions that might be found within the uploaded PDF, because the PDF content has been added to the knowledge base that the tool searches.
    - **`main_pdf_question()` async function:**
        - A sample question specifically related to the likely content of the uploaded PDF is defined.
        - The agent is run again with this new question.
        - The result and the agent's final answer are printed.