# Agentic Rag Chatbot

## What is an LLM?

A Large Language Model (LLM) is an advanced artificial intelligence model trained on vast amounts of text data. LLMs, such as OpenAI's GPT series, are capable of understanding and generating human-like language, making them powerful tools for a wide range of natural language processing tasks, including chatbots, content generation, summarization, and more.

## What is RAG (Retrieval-Augmented Generation)?

Retrieval-Augmented Generation (RAG) is a technique that combines the generative capabilities of LLMs with information retrieval systems. In a RAG setup, the model retrieves relevant documents or knowledge from a database or external source and then uses this information to generate more accurate, context-aware, and up-to-date responses. This approach helps overcome the limitations of LLMs that may not have access to the latest or domain-specific information.

## What is Agentic RAG?

Agentic RAG extends the RAG paradigm by introducing agent-like behaviors and workflows. In Agentic RAG, autonomous agents can reason, plan, and interact with multiple tools or data sources to retrieve, synthesize, and present information. This makes the chatbot more dynamic, capable of handling complex queries, and able to orchestrate multi-step tasks.

## Why is Agentic RAG Important for Chatbots?

- **Enhanced Accuracy:** By retrieving relevant information in real-time, chatbots can provide more precise and up-to-date answers.
- **Context Awareness:** Agentic RAG enables chatbots to understand and use context from multiple sources, improving the quality of interactions.
- **Complex Task Handling:** Agentic agents can break down and solve multi-step problems, making chatbots more useful for advanced use cases.
- **Scalability:** The modular nature of agentic systems allows for easy integration of new tools and data sources.

## Project Description

The goal of this project is to build an Agentic RAG Chatbot that can answer questions based on information scraped from a specific website. The process involves several key steps:

1. **Web Scraping:** Automatically extract relevant content from a target website. This could include articles, FAQs, documentation, or any other useful text data.
2. **Data Storage in a Vector Database:** Process and store the scraped data in a vector database. This allows for efficient semantic search and retrieval of relevant information based on user queries.
3. **Integration with an LLM:** Connect the vector database to a Large Language Model (LLM). When a user asks a question, the system retrieves the most relevant information from the database and provides it as context to the LLM, enabling more accurate and context-aware responses.
4. **Running Chatbot:** Deploy a chatbot interface that users can interact with. The chatbot leverages the Agentic RAG approach to provide dynamic, up-to-date, and contextually rich answers by combining retrieval and generation capabilities.

By the end of this project, you will have a fully functional chatbot capable of answering questions using the latest information from your chosen website, demonstrating the power of Agentic RAG systems in real-world applications.

## Project Phases and Learning Goals

This project is structured into three progressive phases, each designed to build your skills step by step:

### 1. Basic Functionality

- **Scrape a Website:** Extract relevant content from a target website.
- **Create Embeddings & Store in Vector DB:** Convert the scraped data into embeddings and store them in a vector database for efficient retrieval.
- **Chainlit UI Integration:** Connect your retrieval-augmented system to a Chainlit UI and test chatbot interactions locally.

### 2. Intermediate Functionality

- **Build FastAPI Backend:** Develop REST APIs for your chatbot using FastAPI.
- **Streaming Responses:** Implement APIs that support streaming responses for real-time chat experiences.
- **API Documentation & Testing:** Use FastAPI's built-in API docs to test your endpoints.
- **Next.js Frontend:** Create a basic UI in Next.js and integrate it with your FastAPI backend, allowing users to interact with the chatbot from a web interface.

### 3. Advanced Functionality

- **Dockerize FastAPI App:** Build a Docker image for your FastAPI backend for easy deployment.
- **Cloud Deployment:** Deploy your FastAPI backend to a free cloud service (e.g., Render, Railway, or similar).
- **Deploy Next.js App:** Deploy your Next.js frontend to Vercel for public access.
- **Live Testing:** Test and interact with your live, production-ready Agentic RAG Chatbot.

By progressing through these phases, students will gain hands-on experience with web scraping, vector databases, LLM integration, API development, frontend-backend integration, and cloud deployment—covering the full stack of modern AI-powered chatbot development.

## Phase Guides

For detailed, step-by-step instructions for each phase, see the following guides:

- [Basic Functionality Guide](./basic/README.md)
- [Intermediate Functionality Guide](./intermediate/README.md)
- [Advanced Functionality Guide](./advanced/README.md)

---

## Step 1: Set Up Your Python Environment

1. **Install the Latest Version of Python**

   - Download and install the latest version of Python from the [official website](https://www.python.org/downloads/).
   - Verify the installation by running:
     ```bash
     python --version
     ```
     or
     ```bash
     python3 --version
     ```

2. **Install UV (Universal Virtualenv & Package Manager)**

   - UV is a fast Python package manager and environment tool. Install it using pip:
     ```bash
     pip install uv
     ```
     or, if you have pipx:
     ```bash
     pipx install uv
     ```
   - Verify the installation:
     ```bash
     uv --version
     ```

3. **Create a New Project with UV**
   - Initialize a new packaged Python project (replace `agentic_rag_chatbot` with your desired project name):
     ```bash
     uv init --package agentic_rag_chatbot
     ```
   - This will set up a new project directory with the necessary files for package management and development.

---

_Follow the steps below to build your own Agentic RAG Chatbot project._

---
