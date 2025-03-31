# Three-Tier Full-Stack Chatbots

In the [05_chatbot](https://github.com/panaversity/learn-agentic-ai/tree/main/01_openai_agents/05_chatbot/chatbot) section, we created a basic monolithic chatbot. Now, in this section, we will construct three-tier, full-stack chatbots. These will be developed using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and designed to support multiple tenants with user authentication. They will feature both long-term memory ([LangMem](https://langchain-ai.github.io/langmem/)) and short-term memory, with state persistence handled by a relational database ([CockroachDB Serverless](https://www.cockroachlabs.com/lp/serverless/)). The front-end user interface (UI) will be crafted with [Chainlit](https://chainlit.io/), while the middle tier will leverage [FastAPI](https://fastapi.tiangolo.com/) to define REST APIs. We will use [SQLModel](https://sqlmodel.tiangolo.com/) to integrate with [CockroachDB Serverless](https://www.cockroachlabs.com/lp/serverless/). The Agents API will adhere to standards outlined in LangChain's [Agent Protocol](https://github.com/langchain-ai/agent-protocol). Both the front-end and middle-tier components will be deployed in separate [Docker Containers](https://www.docker.com/resources/what-container/), hosted on [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker). The middle-tier REST API will be stateless. These chatbots will serve as foundational templates for future product development.

### What is a Three-Tier Architecture?

A **three-tier architecture** is a software design pattern that organizes an application into three distinct layers, each with a specific responsibility:

- **Presentation Tier**: This is the user interface layer, responsible for displaying information and handling user interactions. Examples include web pages, mobile app interfaces, or desktop application frontends.
- **Application Tier** (or Logic Tier): This layer contains the business logic of the application. It processes inputs from the presentation tier, applies rules, performs calculations, and manages the application's core functionality.
- **Data Tier**: This tier handles data storage and retrieval, typically using databases or file systems. It ensures data persistence and provides access to the information needed by the application tier.

Each tier is separate, meaning they can be developed, deployed, and maintained independently while communicating with each other through defined interfaces.

### What is a Monolithic Architecture?

In contrast, a **monolithic architecture** is a design where all components of an application—user interface, business logic, and data access—are combined into a single, tightly coupled unit. Everything is bundled together and deployed as one entity, with no clear separation between the different functionalities.

### How is Three-Tier Architecture Better than a Monolith?

The three-tier architecture offers several advantages over a monolithic approach, making it more suitable for complex or growing applications. Here’s how it stands out:

1. **Scalability**  
   - **Three-Tier**: Each tier can be scaled independently based on its specific needs. For example, if the presentation tier experiences high traffic, you can add more servers to that layer alone without touching the application or data tiers.  
   - **Monolith**: The entire application must be scaled as a whole, even if only one part (e.g., the user interface) needs more resources. This can waste computing power and increase costs.

2. **Maintainability**  
   - **Three-Tier**: Changes to one tier, like upgrading the database in the data tier, don’t require modifying the other tiers, as long as their interfaces remain compatible. This reduces the risk and effort of updates.  
   - **Monolith**: A change in one area (e.g., tweaking the business logic) can affect the entire system, requiring extensive testing and increasing the chance of unintended side effects.

3. **Flexibility**  
   - **Three-Tier**: Each tier can use the most suitable technology for its role. For instance, you might use a fast, lightweight framework for the presentation tier and a specialized database for the data tier.  
   - **Monolith**: The application is typically built with a single technology stack, limiting the ability to adopt new or specialized tools for different functions.

4. **Fault Isolation**  
   - **Three-Tier**: A failure in one tier (e.g., a database crash in the data tier) is less likely to bring down the entire system. The other tiers might still function partially, using cached data or fallback mechanisms.  
   - **Monolith**: A bug or crash in any component can take down the whole application, creating a single point of failure.

5. **Team Collaboration**  
   - **Three-Tier**: Different teams can work on separate tiers simultaneously—e.g., one team on the user interface, another on business logic, and a third on the database—without interfering with each other. This speeds up development.  
   - **Monolith**: Tight coupling makes it harder for multiple teams to work in parallel, as changes in one area can conflict with others, slowing down progress.

### Conclusion

While a monolithic architecture might be simpler for small, straightforward applications, the **three-tier architecture** excels in most modern scenarios due to its modularity, scalability, and maintainability. By separating concerns into distinct tiers, it provides the flexibility to grow, adapt, and handle complexity more effectively than a monolith, where everything is locked into a single unit.

## What does Stateless API mean?

When it's stated that the middle-tier REST API will be "stateless," it means that each request from the front-end to the middle-tier API is treated as an independent transaction. The middle-tier API does not retain any information or "state" from previous requests.

Here's a breakdown of what that implies:

* **No Session Data:**
    * The API doesn't store session data or maintain any ongoing connection with the client.
    * Each request must contain all the necessary information for the API to process it.
* **Independence of Requests:**
    * Each request is processed in isolation.
    * The API doesn't rely on or assume any prior interactions.
* **Scalability and Reliability:**
    * Statelessness makes the API highly scalable because any server can handle any request.
    * It also improves reliability because if one server fails, other servers can continue processing requests without interruption.
* **Simplicity:**
    * Stateless APIs are generally simpler to design and implement because they don't need to manage complex session states.

In the context of the chatbot application described in the paragraph:

* The front-end (Chainlit) will send requests to the middle-tier (FastAPI) containing all the necessary data, such as user input, authentication tokens, and any relevant context.
* The middle-tier will process the request, interact with the database (CockroachDB Serverless) and the Agents SDK, and return a response.
* The middle tier will not store any information about the conversation between requests. all needed information will be passed with each request.
* The persistence of the chat history and user information will be handled by the relational database (CockroachDB), not in the middle tier API itself.

Essentially, each request to the API is a fresh transaction, and the API relies on external storage (the database) for persistent data.

