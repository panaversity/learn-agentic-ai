# Graph Databases

## Introduction

This tutorial will guide you through the process of integrating Neo4j, a powerful graph database, with the OpenAI Agents SDK. We'll also explore the Model Context Protocol (MCP) and its role in the evolving landscape of AI development. While a direct integration between the OpenAI Agents SDK and Neo4j's MCP servers is not yet available, we will demonstrate a practical approach to connect your OpenAI agent to a Neo4j database, enabling it to query and retrieve information from a knowledge graph.

### What is Neo4j?

Neo4j is a native graph database that stores and manages data in the form of nodes, relationships, and properties. It is designed to efficiently handle highly connected data and complex queries, making it an excellent choice for applications such as recommendation engines, fraud detection, and knowledge graphs.

### What is MCP?

The Model Context Protocol (MCP) is an open-source protocol designed to standardize how language models (LLMs) interact with external tools, APIs, and data sources. It provides a modular and extensible framework for building AI agents that can seamlessly connect to a wide range of services. Neo4j offers MCP servers for memory and database access, which can be used with compatible agent development frameworks.

### What is the OpenAI Agents SDK?

The OpenAI Agents SDK is a Python library that simplifies the development of AI agents powered by OpenAI's language models. It provides a structured and intuitive way to create agents, define their capabilities, and orchestrate their interactions with users and tools.

## Prerequisites

Before we begin, you will need to set up the following:

  * **A Neo4j Instance:** We recommend using [Neo4j AuraDB](https://neo4j.com/cloud/aura-free), a fully managed cloud database that offers a free tier for getting started.
  * **Python:** Make sure you have Python 3.7 or later installed on your system.
  * **OpenAI API Key:** You will need an API key from OpenAI to use their language models. You can obtain one from the [OpenAI Platform](https://platform.openai.com/).

Once you have these prerequisites, you can install the necessary Python libraries using pip:

```bash
pip install neo4j openai-agents
```

## Core Concepts

Let's briefly review the core concepts of each technology before we dive into the implementation.

### Neo4j

  * **Nodes:** Represent entities in your data, such as people, products, or concepts.
  * **Relationships:** Define the connections between nodes, indicating how they are related to each other.
  * **Properties:** Key-value pairs that store data on nodes and relationships.
  * **Cypher:** Neo4j's declarative query language, designed for expressing complex graph patterns.

### MCP

  * **MCP Host:** The environment where the AI agent runs.
  * **MCP Client:** A component within the host that communicates with MCP servers.
  * **MCP Server:** An adapter that exposes a tool or service to the agent in a standardized way.

### OpenAI Agents SDK

  * **Agent:** A customizable entity that can perform tasks, interact with users, and use tools.
  * **Tool:** A function or service that an agent can use to perform actions, such as searching the web or querying a database.
  * **Runner:** A component that executes an agent and manages its interactions.

## Tutorial: Integrating Neo4j with an OpenAI Agent

In this tutorial, we will create a simple knowledge graph of movies and actors in Neo4j and then build an OpenAI agent that can query this graph to answer questions.

### Step 1: Set Up the Neo4j Database

First, let's populate our Neo4j database with some data. You can use the Neo4j Browser or a Python script to execute the following Cypher query:

```cypher
CREATE (theMatrix:Movie {title: 'The Matrix', released: 1999})
CREATE (keanu:Actor {name: 'Keanu Reeves'})
CREATE (carrie:Actor {name: 'Carrie-Anne Moss'})
CREATE (keanu)-[:ACTED_IN]->(theMatrix)
CREATE (carrie)-[:ACTED_IN]->(theMatrix)
```

This query creates two `Actor` nodes and one `Movie` node, and then creates `ACTED_IN` relationships between them.

### Step 2: Create a Neo4j Tool for the OpenAI Agent

Next, we'll create a Python function that connects to our Neo4j database and executes a Cypher query. This function will serve as a tool for our OpenAI agent.

```python
from neo4j import GraphDatabase
from agents import Tool

# Database credentials
URI = "neo4j+s://<your-aura-db-uri>"
AUTH = ("neo4j", "<your-aura-db-password>")

def query_neo4j(query: str) -> str:
    """
    Executes a Cypher query against the Neo4j database and returns the result.
    """
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        records, _, _ = driver.execute_query(query)
        return str([dict(record) for record in records])

# Create a tool for the agent
neo4j_tool = Tool(
    name="query_neo4j",
    description="Query the Neo4j database to find information about movies and actors.",
    func=query_neo4j,
)
```

Replace `<your-aura-db-uri>` and `<your-aura-db-password>` with your Neo4j AuraDB credentials.

### Step 3: Create the OpenAI Agent

Now, let's create an OpenAI agent and give it access to our Neo4j tool. We'll also provide instructions on how to use the tool to answer questions.

```python
from agents import Agent

agent = Agent(
    name="Movie Buff",
    instructions="You are a movie expert with access to a knowledge graph. Use the query_neo4j tool to answer questions about movies and actors. Formulate your queries in Cypher.",
    tools=[neo4j_tool],
)
```

### Step 4: Run the Agent

Finally, we can use the `Runner` to execute our agent and ask it a question.

```python
from agents import Runner

result = Runner.run(agent, "Who acted in The Matrix?")
print(result.final_output)
```

The agent will use the `query_neo4j` tool to execute a Cypher query like `MATCH (a:Actor)-[:ACTED_IN]->(:Movie {title: 'The Matrix'}) RETURN a.name` and then use the result to answer your question.

## The Role of MCP

As mentioned earlier, the OpenAI Agents SDK does not have a native MCP client at this time. However, the approach we've demonstrated—creating a custom tool to interact with Neo4j—achieves a similar goal to what MCP aims to standardize. By creating a well-defined interface for our agent to access the Neo4j database, we are essentially creating a custom "connector" that serves the same purpose as an MCP server.

As MCP continues to gain traction in the AI community, we can expect to see more direct integrations with popular agent development frameworks like the OpenAI Agents SDK. This will further simplify the process of building sophisticated AI agents that can leverage a wide range of tools and services.

## Conclusion

In this tutorial, we have learned how to integrate Neo4j with the OpenAI Agents SDK to create an AI agent that can query a knowledge graph. We have also discussed the role of MCP in the broader context of AI agent development. By combining the power of graph databases with the flexibility of large language models, you can build intelligent applications that can reason about and interact with complex, real-world data.

For further exploration, you can refer to the official documentation for [Neo4j](https://neo4j.com/docs/), [MCP](https://www.google.com/search?q=https://www.modelcontext.dev/), [Everything a Developer Needs to Know About MCP with Neo4j](https://www.wearedevelopers.com/en/magazine/604/)everything-a-developer-needs-to-know-about-mcp-with-neo4j-604  and the [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents-sdk).

