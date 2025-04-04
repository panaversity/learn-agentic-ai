# Development will use a Combination of Stateless Computing, and Event-Driven and Three-Tier Architecture

In the [05_chatbot](https://github.com/panaversity/learn-agentic-ai/tree/main/01_openai_agents/05_chatbot/chatbot) section, we created a basic monolithic chatbot. Now, in this section, we will construct three-tier, full-stack chatbots. These will be developed using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and designed to support multiple tenants with user authentication. They will feature both long-term memory ([LangMem](https://langchain-ai.github.io/langmem/)) and short-term memory, with state persistence handled by a relational database ([CockroachDB Serverless](https://www.cockroachlabs.com/lp/serverless/)). The front-end user interface (UI) will be crafted with [Chainlit](https://chainlit.io/), while the middle tier will leverage [FastAPI](https://fastapi.tiangolo.com/) to define REST APIs. We will use [SQLModel](https://sqlmodel.tiangolo.com/) to integrate with [CockroachDB Serverless](https://www.cockroachlabs.com/lp/serverless/). The Agents API will adhere to standards outlined in LangChain's [Agent Protocol](https://github.com/langchain-ai/agent-protocol). Both the front-end and middle-tier components will be deployed in separate [Docker Containers](https://www.docker.com/resources/what-container/), hosted on [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker). The middle-tier REST API will be stateless. These chatbots will serve as foundational templates for future product development.

## AgentiaCloud Architecture for Agentic AI

A combination of **event-driven architecture (EDA)**, **three-tier architecture**, **stateless computing**, and **scheduled computing (CronJobs)** is used by AgentiaCloud for agentic AI development to meet the requirements of AI agents—such as their autonomy, real-time needs, scalability, and complexity. This mix can indeed be a powerful and practical approach for many agentic AI systems. Let’s break it down and evaluate how these paradigms align with agentic AI, which typically involves autonomous, goal-driven entities that perceive, decide, and act in an environment.

---

### What is Agentic AI?
Agentic AI refers to systems where AI "agents" operate with some degree of autonomy, making decisions and taking actions to achieve goals. These agents might:
- React to environmental changes (e.g., user inputs, sensor data).
- Perform scheduled tasks (e.g., periodic analysis).
- Coordinate with other agents or systems.
- Scale dynamically based on workload.

Examples include multi-agent systems, autonomous chatbots, or robotic process automation (RPA).

---

### Analyzing the Components

#### 1. Event-Driven Architecture (EDA)
- **Why It Fits Agentic AI**:
  - Agents often need to **react to events**—like a user command, a sensor trigger, or a state change in another agent. EDA’s asynchronous, reactive nature aligns perfectly with this.
  - Loose coupling allows agents to operate independently, publishing events (e.g., "TaskCompleted") and subscribing to others (e.g., "NewDataAvailable") without tight dependencies.
  - Supports real-time decision-making, critical for agents in dynamic environments.
- **Use Case**: An agent monitoring stock prices reacts to a "PriceDrop" event by executing a trade, while another agent logs the action—all triggered via an event bus.

#### 2. Three-Tier Architecture
- **Why It Fits Agentic AI**:
  - Provides a **structured foundation**:
    - **Presentation Layer**: Interfaces for human-agent interaction (e.g., a UI for configuring agents).
    - **Business Logic Layer**: Houses the agent’s decision-making logic (e.g., rules, models, or reinforcement learning policies).
    - **Data Layer**: Stores agent states, historical data, or shared knowledge bases.
  - Simplifies development by separating concerns, making it easier to manage complex agent logic.
  - Can integrate with EDA by embedding event-driven mechanisms in the business logic layer.
- **Use Case**: A customer support agent uses the presentation layer to interact with users, the business logic layer to process queries (possibly via events), and the data layer to retrieve customer history.

#### 3. Stateless Computing
- **Why It Fits Agentic AI**:
  - Statelessness (where each request or event is handled independently, without relying on prior state stored in memory) enhances **scalability** and **resilience**.
  - Agents can be deployed as stateless microservices or serverless functions (e.g., AWS Lambda), spinning up to handle events and shutting down when idle—ideal for unpredictable workloads.
  - Simplifies horizontal scaling: add more agent instances without worrying about shared state.
  - Caveat: Agents often need some state (e.g., memory of past actions). This can be offloaded to an external store (e.g., Postgres, a database) in the data layer, keeping the compute layer stateless.
- **Use Case**: An agent handling incoming customer requests runs as a stateless function, fetching its context (e.g., conversation history) from a database per event.

#### 4. Scheduled Computing (CronJobs)
- **Why It Fits Agentic AI**:
  - Agents may need to perform **periodic tasks**, like data aggregation, model retraining, or status checks, which CronJobs handle efficiently.
  - Complements EDA by addressing proactive (time-based) rather than reactive (event-based) behavior.
  - Useful for maintenance or long-term planning in agentic systems (e.g., an agent that optimizes a schedule daily).
- **Use Case**: An agent retrains its machine learning model every night at 2 AM via a CronJob, then uses the updated model for event-driven decisions during the day.

---

### How They Work Together for Agentic AI
Here’s a cohesive architecture:
- **Three-Tier Structure**:
  - **Presentation**: User or external system interfaces to interact with agents.
  - **Business Logic**: Hosts the agent logic, split into stateless event handlers (for real-time reactions) and scheduled tasks (for periodic actions).
  - **Data**: Stores agent states, event logs, and shared resources (e.g., a knowledge graph).
- **EDA**: Drives real-time agent behavior. Agents publish and subscribe to events via an event bus (e.g., Kafka), enabling autonomy and coordination.
- **Stateless Computing**: Agent logic runs as stateless functions or containers, scaling dynamically with event load and fetching state from the data layer as needed.
- **CronJobs**: Handle time-based tasks, triggering events or directly updating the system (e.g., "ModelUpdated" event after retraining).

#### Example Workflow
Imagine a fleet of delivery drones (agentic AI):
- **Event-Driven**: A "PackageAssigned" event triggers a drone agent to plan its route. It publishes "RoutePlanned" for a tracking agent to monitor.
- **Three-Tier**: The drone’s logic (business layer) computes routes, pulling map data (data layer) and reporting status via a dashboard (presentation layer).
- **Stateless**: Each drone’s route planner runs as a stateless service, scaling with the number of packages, with flight state stored in a database.
- **CronJobs**: A nightly job recalibrates drone battery models based on usage data, updating their decision-making parameters.

---

### Is This the "Best" Approach?
#### Advantages
- **Scalability**: Stateless computing and EDA allow agents to handle variable workloads efficiently.
- **Flexibility**: EDA supports reactive agents, while CronJobs cover proactive tasks, all within a clear three-tier structure.
- **Modularity**: Separates agent logic, data, and interfaces, easing development and maintenance.
- **Resilience**: Loose coupling and statelessness reduce single points of failure.

#### Potential Downsides
- **Complexity**: Managing events, stateless services, and scheduled tasks adds overhead—overkill for simple agents.
- **State Management**: Statelessness requires external state storage, which can introduce latency or consistency challenges.
- **Resource Use**: CronJobs and event buses might be unnecessary if agents only need simple, synchronous interactions.

#### When It’s Best
This combo excels for:
- **Distributed, autonomous agents**: Multi-agent systems needing real-time coordination (e.g., robotics, simulations).
- **Scalable AI services**: Cloud-based agents handling unpredictable demand (e.g., chatbots, recommendation engines).
- **Hybrid behavior**: Agents requiring both reactive (event-driven) and proactive (scheduled) actions.

For simpler agentic AI (e.g., a single rule-based bot), a lighter setup—like a monolithic three-tier app without EDA or statelessness—might suffice.

---

### Conclusion
Yes, combining EDA, three-tier architecture, stateless computing, and CronJobs can be an excellent fit for agentic AI development, especially for complex, scalable, and autonomous systems. It balances structure (three-tier), reactivity (EDA), efficiency (stateless), and proactivity (CronJobs). Tailor it to your use case: lean on EDA for real-time autonomy, statelessness for scale, and CronJobs for periodic tasks, all anchored by a three-tier framework. If your agents are less dynamic or resource-constrained, simplify by dropping components like EDA or stateless computing. 

### What is Event-Driven Architecure?

Event-Driven Architecture (EDA) is a design paradigm where the flow of a system is driven by the production, detection, and consumption of **events**. An event is a record of something that has happened—think of it as a notification of a state change or an action, like "user clicked a button," "payment processed," or "sensor detected motion." Instead of components directly calling each other (like in traditional request-response models), they communicate indirectly by generating and reacting to these events, often through an intermediary like an event bus or message queue.

### Core Components
1. **Event Producers**: These are the sources that generate events. It could be a user action (e.g., submitting a form), a system process (e.g., a file upload completing), or an external trigger (e.g., a stock price change).
   
2. **Events**: Lightweight messages or data packets that describe what happened. They typically include details like a timestamp, event type, and relevant payload (e.g., "OrderPlaced: {orderId: 123, amount: $50}").

3. **Event Bus/Channel**: The infrastructure that routes events from producers to consumers. Examples include message queues (RabbitMQ, Apache Kafka), pub/sub systems (Google Pub/Sub), or even simple in-memory brokers.

4. **Event Consumers**: Components or services that listen for specific events and react accordingly. A consumer might send an email, update a database, or trigger another process.

### How It Works
- An event occurs (e.g., a customer places an order).
- The producer publishes the event to the event bus.
- The bus delivers the event to all subscribed consumers.
- Each consumer processes the event independently, often asynchronously (i.e., not waiting for a response).

This creates a **loosely coupled** system—producers don’t need to know who’s listening or what they’ll do with the event, and consumers don’t need to know where the event came from.

### Key Characteristics
- **Asynchronous**: Events are processed when they’re received, not necessarily in real-time or in sequence, decoupling the timing of actions.
- **Reactive**: The system responds to events as they happen, making it ideal for dynamic, real-time applications.
- **Scalable**: You can add more consumers to handle events without changing the producer, supporting high-throughput scenarios.
- **Distributed**: EDA fits naturally in distributed systems (e.g., microservices), where components run independently.

### Common Patterns
1. **Publish/Subscribe (Pub/Sub)**: Producers publish events to a channel, and multiple consumers subscribe to receive them. Each consumer gets its own copy of the event.
2. **Message Queues**: Events are placed in a queue, and consumers pull them one at a time, ensuring ordered processing.
3. **Event Sourcing**: Instead of storing just the current state, the system records all events that led to it, reconstructing state by replaying them.
4. **CQRS (Command Query Responsibility Segregation)**: Often paired with EDA, separating read and write operations, with events driving updates.

### Examples
- **E-commerce**: An "OrderPlaced" event triggers inventory updates, payment processing, and customer notifications—all handled by separate services.
- **IoT**: A sensor sends a "TemperatureExceeded" event, prompting a cooling system to activate.
- **Social Media**: A "NewPost" event updates feeds, sends notifications, and logs analytics.

### Benefits
- **Flexibility**: Add or remove consumers without altering the producer.
- **Resilience**: If one consumer fails, others can still process events.
- **Real-Time Processing**: Great for applications needing immediate reactions (e.g., fraud detection).
- **Scalability**: Distribute workload across multiple consumers or nodes.

### Drawbacks
- **Complexity**: Tracking event flows and ensuring consistency can be tricky.
- **Eventual Consistency**: Asynchronous processing might mean delays in state updates.
- **Debugging**: Harder to trace a sequence of events compared to a linear call stack.

### When to Use It
EDA shines in systems that need to handle high volumes of asynchronous tasks, react to real-time changes, or scale across distributed components—like microservices, IoT, or large-scale web apps. It’s less suited for simple, linear workflows where a traditional request-response model (e.g., a basic CRUD app) is enough.

In essence, EDA is about building systems that thrive on change, letting events steer the action rather than rigid, predefined flows. It’s a mindset shift from "do this, then that" to "something happened—now what?"

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
* The persistence of the chat history and user information will be handled by the relational database (Redis and CockroachDB), not in the middle tier API itself.

Essentially, each request to the API is a fresh transaction, and the API relies on external storage (the database) for persistent data.


## Development Stack (Local): Open Source

The development, prototype and production stacks are identical in terms of the tools and technologies used. The only difference lies in how they are deployed. This unified development approach ensures developers can build and test locally or in a cloud environment using the same stack, transitioning seamlessly to either prototyping or production deployment.  
- **LLM APIs**: OpenAI Chat Completion (Google Gemini - Free Tier), Responses API 
- **Lightweight Agents**: OpenAI Agents SDK (Open Source)
- **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)** Server in stateless containers for standardizing agentic tool calling (Open Source).  
- **REST APIs**: FastAPI (Open Source)
- **Stateless Serverless Docker Containers**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) and [Docker Compose](https://docs.docker.com/compose/) (Free Tier and Open Source)
- **Asynchronous Message Passing**: [RabbitMQ Docker Image](https://hub.docker.com/_/rabbitmq/) (Open Source) 
- **Scheduled Container Invocation**: [For development we use [python-crontab](https://pypi.org/project/python-crontab/) on Linux and Mac. [APSchedule](https://pypi.org/project/APScheduler/) for Windows. Or [Schedule](https://pypi.org/project/schedule/) for inprocess scheduling on any system.
- **Relational Database**: [Postgres Docker Image](https://hub.docker.com/_/postgres) (Open Source). Implement abstraction layers (e.g., ORMs for databases) to ease provider switches, we will use SQLModel (Open Source). 
- **Inmemory Datastore**: [Redis Docker Image](https://hub.docker.com/_/redis) (Open Source). In Python use [redis-py](https://pypi.org/project/redis/) or higher level [Redis OM Python](https://github.com/redis/redis-om-python) (Open Source). 
- **Developing inside a Container** [Visual Studio Code Dev Containers Extension](https://code.visualstudio.com/docs/devcontainers/containers)
- **Run Darp Locally** [Run using Docker-Compose](https://docs.dapr.io/getting-started/install-dapr-selfhost/) (Open Source) Optionally, you can use [Dapr Agents](https://dapr.github.io/dapr-agents/) and [Dapr Workflows](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)

