# Learn Agentic AI using Dapr Agentic Cloud Ascent (DACA) Design Pattern: From Start to Scale

This repo is part of the [Panaversity Certified Agentic & Robotic AI Engineer](https://docs.google.com/document/d/15usu1hkrrRLRjcq_3nCTT-0ljEcgiC44iSdvdqrCprk/edit?usp=sharing) program. It covers AI-201, AI-202 and AI-301 courses.

We have Two Hunches, the future of Pakistan depends on it, let's make sure that we are not wrong:

It is very important for Pakistan that we bet on the right horses for the upcoming age of Agentic AI. We will be training millions of Agentic AI Developers all over Pakistan and online around the world and building startups, we cant afford to be wrong.

Hunch #1: Dapr
We feel Dapr, Dapr Actors, Dapr Workflows, and Dapr Agents will be the core technology in building the next generation multi ai agentic systems, is my hunch correct?

Hunch #2: OpenAI Agents SDK
We also have a hunch that OpenAI Agents SDK will be the go to framework for beginners to start learning Agentic AI?

Let us see what the best AI has to say about our hunches:

https://chatgpt.com/share/6811b893-82cc-8001-9037-e45bcd91cc64

https://g.co/gemini/share/1f31c876520b

https://grok.com/share/bGVnYWN5_4343d342-c7df-4b06-9174-487a64f59d53



## This Panaversity Initiative Tackles the Critical Challenge: 

**“How do we design AI Agents that can handle 10 million concurrent AI Agents without failing?”**

Note: The challenge is intensified as we must guide our students to solve this issue with minimal financial resources available during training.

<p align="center">
<img src="./img/cover.png" width="600">
</p>

Kubernetes with Dapr can theoretically handle 10 million concurrent agents in an agentic AI system without failing, but achieving this requires extensive optimization, significant infrastructure, and careful engineering. While direct evidence at this scale is limited, logical extrapolation from existing benchmarks, Kubernetes’ scalability, and Dapr’s actor model supports feasibility, especially with rigorous tuning and resource allocation.

**Condensed Argument with Proof and Logic**:

1. **Kubernetes Scalability**:
   - **Evidence**: Kubernetes supports up to 5,000 nodes and 150,000 pods per cluster (Kubernetes docs), with real-world examples like PayPal scaling to 4,000 nodes and 200,000 pods (InfoQ, 2023) and KubeEdge managing 100,000 edge nodes and 1 million pods (KubeEdge case studies). OpenAI’s 2,500-node cluster for AI workloads (OpenAI blog, 2022) shows Kubernetes can handle compute-intensive tasks.
   - **Logic**: For 10 million users, a cluster of 5,000–10,000 nodes (e.g., AWS g5 instances with GPUs) can distribute workloads. Each node can run hundreds of pods, and Kubernetes’ horizontal pod autoscaling (HPA) dynamically adjusts to demand. Bottlenecks (e.g., API server, networking) can be mitigated by tuning etcd, using high-performance CNIs like Cilium, and optimizing DNS.

2. **Dapr’s Efficiency for Agentic AI**:
   - **Evidence**: Dapr’s actor model supports thousands of virtual actors per CPU core with double-digit millisecond latency (Dapr docs, 2024). Case studies show Dapr handling millions of events, e.g., Tempestive’s IoT platform processing billions of messages (Dapr blog, 2023) and DeFacto’s system managing 3,700 events/second (320 million daily) on Kubernetes with Kafka (Microsoft case study, 2022).
   - **Logic**: Agentic AI relies on stateful, low-latency agents. Dapr Agents, built on the actor model, can represent 10 million users as actors, distributed across a Kubernetes cluster. Dapr’s state management (e.g., Redis) and pub/sub messaging (e.g., Kafka) ensure efficient coordination and resilience, with automatic retries preventing failures. Sharding state stores and message brokers scales to millions of operations/second.

3. **Handling AI Workloads**:
   - **Evidence**: LLM inference frameworks like vLLM and TGI serve thousands of requests/second per GPU (vLLM benchmarks, 2024). Kubernetes orchestrates GPU workloads effectively, as seen  Kubernetes manages GPU workloads, as seen in NVIDIA’s AI platform scaling to thousands of GPUs (NVIDIA case study, 2023).
   - **Logic**: Assuming each user generates 1 request/second requiring 0.01 GPU, 10 million users need ~100,000 GPUs. Batching, caching, and model parallelism reduce this to a feasible ~10,000–20,000 GPUs, achievable in hyperscale clouds (e.g., AWS). Kubernetes’ resource scheduling ensures optimal GPU utilization.

4. **Networking and Storage**:
   - **Evidence**: EMQX on Kubernetes handled 1 million concurrent connections with tuning (EMQX blog, 2024). C10M benchmarks (2013) achieved 10 million connections using optimized stacks. Dapr’s state stores (e.g., Redis) support millions of operations/second (Redis benchmarks, 2024).
   - **Logic**: 10 million connections require ~100–1,000 Gbps bandwidth, supported by modern clouds. High-throughput databases (e.g., CockroachDB) and caching (e.g., Redis Cluster) handle 10 TB of state data for 10 million users (1 KB/user). Kernel bypass (e.g., DPDK) and eBPF-based CNIs (e.g., Cilium) minimize networking latency.

5. **Resilience and Monitoring**:
   - **Evidence**: Dapr’s resiliency policies (retries, circuit breakers) and Kubernetes’ self-healing (pod restarts) ensure reliability (Dapr docs, 2024). Dapr’s OpenTelemetry integration scales monitoring for millions of agents (Prometheus case studies, 2023).
   - **Logic**: Real-time metrics (e.g., latency, error rates) and distributed tracing prevent cascading failures. Kubernetes’ liveness probes and Dapr’s workflow engine recover from crashes, ensuring 99.999% uptime.

**Feasibility with Constraints**:
- **Challenge**: No direct benchmark exists for 10 million concurrent users with Dapr/Kubernetes in an agentic AI context. Infrastructure costs (e.g., $10M–$100M for 10,000 nodes) are prohibitive for low-budget scenarios.
- **Solution**: Use open-source tools (e.g., Minikube, kind) for local testing and cloud credits (e.g., AWS Educate) for students. Simulate 10 million users with tools like Locust on smaller clusters (e.g., 100 nodes), extrapolating results. Optimize Dapr’s actor placement and Kubernetes’ resource quotas to maximize efficiency on limited hardware. Leverage free-tier databases (e.g., MongoDB Atlas) and message brokers (e.g., RabbitMQ).

**Conclusion**: Kubernetes with Dapr can handle 10 million concurrent users in an agentic AI system, supported by their proven scalability, real-world case studies, and logical extrapolation. For students with minimal budgets, small-scale simulations, open-source tools, and cloud credits make the problem tractable, though production-scale deployment requires hyperscale resources and expertise.


**Agentic AI Top Trend of 2025**

<p align="center">
<img src="./img/toptrend.webp" width="200">
</p>


## The Dapr Agentic Cloud Ascent (DACA) Design Pattern Addresses 10 Million AI Agents Challenge 

Let's understand and learn about "Dapr Agentic Cloud Ascent (DACA)", our winning design pattern for developing and deploying planet scale multi-agent systems.

### Executive Summary: Dapr Agentic Cloud Ascent (DACA)

The Dapr Agentic Cloud Ascent (DACA) guide introduces a strategic design pattern for building and deploying sophisticated, scalable, and resilient agentic AI systems. Addressing the complexities of modern AI development, DACA integrates the OpenAI Agents SDK for core agent logic with the Model Context Protocol (MCP) for standardized tool use and the Agent2Agent (A2A) protocol for seamless inter-agent communication, all underpinned by the distributed capabilities of Dapr. **Grounded in AI-first and cloud-first principles**, DACA promotes the use of stateless, containerized applications deployed on platforms like Azure Container Apps (Serverless Containers) or Kubernetes, enabling efficient scaling from local development to planetary-scale production, potentially leveraging free-tier cloud services and self-hosted LLMs for cost optimization. The pattern emphasizes modularity, context-awareness, and standardized communication, envisioning an **Agentia World** where diverse AI agents collaborate intelligently. Ultimately, DACA offers a robust, flexible, and cost-effective framework for developers and architects aiming to create complex, cloud-native agentic AI applications that are built for scalability and resilience from the ground up.


**[Comprehensive Guide to Dapr Agentic Cloud Ascent (DACA) Design Pattern](https://github.com/panaversity/learn-agentic-ai/blob/main/comprehensive_guide_daca.md)**

<p align="center">
<img src="./img/ascent.png" width="500">
</p>

<p align="center">
<img src="./img/architecture1.png" width="400">
</p>




### Target User
- **Agentic AI Developer and AgentOps Professionals**

### Why OpenAI Agents SDK should be the main framework for agentic development for most use cases?

**Table 1: Comparison of Abstraction Levels in AI Agent Frameworks**

| **Framework**         | **Abstraction Level** | **Key Characteristics**                                                                 | **Learning Curve** | **Control Level** | **Simplicity** |
|-----------------------|-----------------------|-----------------------------------------------------------------------------------------|--------------------|-------------------|----------------|
| **OpenAI Agents SDK** | Minimal              | Python-first, core primitives (Agents, Handoffs, Guardrails), direct control           | Low               | High             | High           |
| **CrewAI**            | Moderate             | Role-based agents, crews, tasks, focus on collaboration                                | Low-Medium        | Medium           | Medium         |
| **AutoGen**           | High                 | Conversational agents, flexible conversation patterns, human-in-the-loop support       | Medium            | Medium           | Medium         |
| **Google ADK**        | Moderate             | Multi-agent hierarchies, Google Cloud integration (Gemini, Vertex AI), rich tool ecosystem, bidirectional streaming | Medium            | Medium-High      | Medium         |
| **LangGraph**         | Low-Moderate         | Graph-based workflows, nodes, edges, explicit state management                        | Very High         | Very High        | Low            |
| **Dapr Agents**       | Moderate             | Stateful virtual actors, event-driven multi-agent workflows, Kubernetes integration, 50+ data connectors, built-in resiliency | Medium            | Medium-High      | Medium         |


The table clearly identifies why OpenAI Agents SDK should be the main framework for agentic development for most use cases:
- It excels in **simplicity** and **ease of use**, making it the best choice for rapid development and broad accessibility.
- It offers **high control** with **minimal abstraction**, providing the flexibility needed for agentic development without the complexity of frameworks like LangGraph.
- It outperforms most alternatives (CrewAI, AutoGen, Google ADK, Dapr Agents) in balancing usability and power, and while LangGraph offers more control, its complexity makes it less practical for general use.

If your priority is ease of use, flexibility, and quick iteration in agentic development, OpenAI Agents SDK is the clear winner based on the table. However, if your project requires enterprise-scale features (e.g., Dapr Agents) or maximum control for complex workflows (e.g., LangGraph), you might consider those alternatives despite their added complexity. 

## Core DACA Agentic AI Courses:

### AI-201:  Fundamentals of Agentic AI and DACA AI-First Development (14 weeks)

- ⁠Agentic & DACA Theory - 1 week
- UV & ⁠OpenAI Agents SDK - 5 weeks
- ⁠Agentic Design Patterns - 2 weeks 
- ⁠Memory [LangMem & mem0] 1 week
- Postgres/Redis (Managed Cloud) - 1 week
- FastAPI (Basic)  - 2 weeks
- ⁠Containerization (Rancher Desktop) - 1 week
- Hugging Face Docker Spaces - 1 week


**[AI-201 Video Playlist](https://www.youtube.com/playlist?list=PL0vKVrkG4hWovpr0FX6Gs-06hfsPDEUe6)**

Note: These videos are for additional learning, and do not cover all the material taught in the onsite classes.

Prerequisite: Successful completion of [AI-101: Modern AI Python Programming - Your Launchpad into Intelligent Systems](https://github.com/panaversity/learn-modern-ai-python)

### AI-202: DACA Cloud-First Agentic AI Development (14 weeks)
- Rancher Desktop with Local Kubernetes - 4 weeks
- Advanced FastAPI with Kubernetes - 2 weeks
- Dapr [workflows, state, pubsub, secrets] - 3 Week
- CockRoachdb & RabbitMQ Managed Services - 2 weeks
- ⁠Model Context Protocol -  2 weeks
- ⁠Serverless Containers Deployment (ACA) - 2 weeks

Prerequisite: Successful completion of AI-201

### AI-301 DACA Planet-Scale Distributed AI Agents (14 Weeks)
- ⁠Certified Kubernetes Application Developer (CKAD) - 4 weeks
- ⁠A2A Protocol - 2 weeks
- ⁠Voice Agents - 2 weeks
- ⁠Dapr Agents/Google ADK - 2 weeks
- ⁠Self-LLMs Hosting - 1 week
- Finetuning LLMs - 3 weeks

Prerequisite: Successful completion of AI-201 & AI-202

## Evaluations

Quizzes + Hackathons (Everything is Onsite)

1. Advanced Modern Python (including asyncio) [Q1]
2. OpenAI Agents SDK (45 MCQ in 1 hour) [01_ai_agents_first]
3. Protocols (A2A and MCP) [05_ai_protocols]
4. Hackathon1 - 8 Hours (Using Above Quiz Stack)
5. Containerization + FastAPI [04_daca_agent_native_dev = 01 + 02 ]
6. Kubernetes (Rancher Desktop) [Stimulations] [04_daca_agent_native_dev = 02 ]
7. Dapr1 - State, PubSub, Bindings, Invocation [04_daca_agent_native_dev = 03 ]
8. Dapr2 - Workflows, Virtual Actors [04_agent_native = 04, 05, 06]
9. Hackathon2 - 8 Hours (Agent Native Startup) 
10. CKAD + DAPR + ArgoCD (Stimulatinos) [06_daca_deployment_guide + 07_ckad]
