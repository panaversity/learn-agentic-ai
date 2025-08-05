# Master [Graphiti: Temporal Knowledge Graphs Engine](https://help.getzep.com/v3/graphiti/getting-started/welcome)

Learn **Graphiti** - the temporal knowledge graph framework that powers Zep's memory architecture. This path takes you from beginner to expert through hands-on examples and real projects.

> [How to pronounce Graphiti?](https://www.youtube.com/watch?v=sygRBjILDn8)

## 🎯 What You'll Learn

- **Build knowledge graphs** from any text, conversations, or data
- **Search and retrieve** information using semantic queries  
- **Create custom types** for your specific domain
- **Deploy production agentic memory systems** with MCP integration
- **Master temporal patterns** for AI agent memory

## 📚 Learning Path

We follow proven learning principles:
- **Start simple** with working examples
- **Build complexity** step by step
- **Practice immediately** with real code
- **Connect concepts** across steps

## 📖 Step-by-Step Learning

### **Phase 1: Core Concepts (Steps 01-04)**
*Learn the fundamentals through hands-on practice*

**Step 01: [Hello World](01_hello_world/)** - Your first knowledge graph  
*Get Graphiti running and see how text becomes structured knowledge*

**Step 02: [Adding Episodes](02_adding_episodes/)** - Different data types  
*Learn text, message, and JSON episodes with real examples*

**Step 03: [Custom Types](03_custom_types/)** - Domain-specific modeling  
*Create custom entities and relationships for your domain*

**Step 04: [Communities](04_communities/)** - Finding patterns  
*Discover how Graphiti groups related information automatically*

### **Phase 2: Advanced Features (Steps 05-08)**
*Build production-ready systems*

**Step 05: [Graph Namespacing](05_graph_namespacing/)** - Multi-tenant isolation  
*Separate data for different users or organizations*

**Step 06: [Searching](06_searching/)** - Advanced retrieval  
*Master semantic search, filtering, and optimization*

**Step 07: [CRUD Operations](07_crud_operations/)** - Direct manipulation  
*Work directly with nodes and edges when needed*

**Step 08: [Fact Triples](08_fact_triples/)** - Precise knowledge  
*Add structured facts for maximum precision*

### **Phase 3: Production Systems (Steps 09-12)**
*Deploy and scale your knowledge graphs*

**Step 09: [MCP Server](09_mcp_server/)** - AI assistant integration  
*Connect Graphiti to Claude, Cursor, and other AI tools*

**Step 10: [Configuration](10_configuration/)** - Performance optimization  
*Configure LLMs, databases, and performance settings*

**Step 11: [Zep Integration](11_zep_memory/)** - Production memory  
*Understand how Graphiti powers production AI systems*

**Step 12: [TutorsGPT Project](12_tutorsgpt_implementation/)** - Complete system  
*Build a full educational AI system using everything you've learned*

## 🛠️ How to Use This Path

### **Each Step Includes**
1. **Clear explanation** of the concept
2. **Working code examples** you can run immediately  
3. **Hands-on exercises** to practice
4. **Real-world applications** and use cases
5. **Common issues** and how to solve them

### **Learning Approach**
- **Start with Step 01** and work through in order
- **Run all the code examples** - don't just read them
- **Try the exercises** before moving to the next step
- **Build on previous knowledge** as you progress
- **Ask questions** and experiment with variations

## 🚀 Prerequisites

### **Knowledge Prerequisites**
- Python 3.10+ programming
- Basic understanding of graphs (nodes/edges)
- Familiarity with AI/LLM concepts
- Experience with APIs and databases

### **Learning Environment**
- **Neo4j Database**: [Neo4j Desktop](https://neo4j.com/download/) or [AuraDB](https://neo4j.com/cloud/aura/)
- **Code Editor**: VS Code or Cursor with Python extension recommended

1. **Start with [01_hello_world](01_hello_world/)** 

By completing this pathway, you won't just know Graphiti - you'll **think** with temporal knowledge graphs. 

---

## Graphiti vs Other Options Comparison Table

| **Platform/Framework**  | **Architecture & Design**                                                                                               | **Agentic Memory Support**                                          | **Graph RAG Support**                                                   | **Benchmarks (DMR/LongMemEval/LOCOMO)**                                                                                | **Source**                                                  | **Deployment**                                               | **Ecosystem & Integrations**                                                                                                                  | **Enterprise Features**                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Zep (Graphiti)**      | Dynamic temporal KG; incremental LLM+indexing pipeline; contextual prompt assembly.                                     | Yes – full conversational memory via KG.                            | Yes – “Graph RAG” for dynamic data.                                     | 94.8% vs 93.4% (MemGPT) on DMR; \~90% reduction in response latency and up to +18.5% accuracy on LongMemEval.          | Closed-source (SaaS); Graphiti engine is open (Apache 2.0). | Hosted SaaS; can self-host Graphiti core.                    | Built on Neo4j/FalkorDB; integrates with LangGraph, LangChain tools, vector DBs; MCP server for LLMs.                                         | Auth/RBAC via cloud service; enterprise contracts available; HIPAA-compliance likely for managed version. |
| **Letta (MemGPT)**      | MemGPT-style “agent OS”: in-context *memory blocks* + external vector memory + tools.                                   | Yes – built-in persistent memory across sessions (memory blocks).   | Indirect – agents can call external tools/RAG pipelines as needed.      | MemGPT (base) reported \~94% accuracy on DMR (Zep comparison) (full-context baseline \~98%). Latency depends on model. | Open-source (Apache 2.0).                                   | Self-host (Docker or pip); also offered via Letta Cloud.     | Framework-agnostic; works with any LLM (OpenAI, Anthropic, vLLM, Ollama, etc.) and LangChain; has Python/TS SDKs and ADE GUI.                 | Auth, logging in Letta server; versioned agents; no vendor lock-in. Compliance left to host.              |
| **Mem0**                | Hybrid memory store: vector DB + graph DB + KV for facts. LLM-driven extract→store; multi-level (user, session, agent). | Yes – persists user/agent info for personalization.                 | Yes – graph DB captures relationships for RAG-like queries.             | +26% accuracy vs OpenAI Memory on LOCOMO; 91% lower latency vs full-context; \~90% fewer tokens.                       | Open-source (Apache 2.0) with optional SaaS.                | Hosted platform (Mem0 Cloud) or self-host via API/SDK.       | SDKs for Python/Node; supports multiple LLM providers (OpenAI, Gemini, Claude, Ollama); integrates with common AI frameworks and data stores. | Enterprise SaaS includes analytics, encryption, auth; on-prem option for sensitive data.                  |
| **LangMem (LangChain)** | Memory SDK with typed memory (semantic/episodic/procedural); abstracts storage layer.                                   | Yes – agents can learn and store long-term facts from conversation. | Yes – via LangGraph integration, supports graph-based memory retrieval. | No public benchmarks yet. Latency depends on storage backend.                                                          | Open-source (Apache, part of LangChain).                    | Library (PyPI); also free managed API for memory extraction. | Native integration with LangGraph (LangChain’s KG); works with any vector DB or database; agent frameworks.                                   | Open, user-managed; privacy via namespacing per user; no built-in enterprise features.                    |

| **Framework**      | **Architecture & Design**                                                                                       | **Agentic Memory Support**                                     | **Graph RAG Support**                                                  | **Benchmarks / Performance**                                                                                 | **Source**                | **Deployment**                                                       | **Ecosystem & Integrations**                                                                                                     | **Enterprise Features**                                                                                            |
| ------------------ | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Graphiti (Zep)** | Real-time temporal KG engine: continuous episode ingestion, bi-temporal graph, hybrid search.                   | Yes – core of agent memory (Zep).                              | Yes – designed for Graph RAG on dynamic data.                          | Sub-second query latency; scales to large data (benchmarks: Zep shows high accuracy with low context usage). | Open-source (Apache 2.0). | Python library, Docker; requires a graph backend (Neo4j/FalkorDB).   | Integrates with Neo4j/FalkorDB, LangChain/Graph connectors, vector stores; LLMs via OpenAI/Gemini/Anthropic.                     | Leverages graph DB’s security (RBAC, encryption); MCP server adds auth on API.                                     |
| **GraphRAG (MS)**  | Static pipeline: LLM-based triple extraction → Leiden clustering → community summaries → RAG with graph search. | No (static index only).                                        | Yes – exactly (KG-enhanced RAG for static documents).                  | Improved QA vs flat RAG (no public latency data; queries take seconds).                                      | Open-source (MIT).        | Python code (PyTorch/NetworkX); can be run on local machines.        | Works on any text corpus; outputs KG that can be stored in any graph DB.                                                         | No built-in security; externalize via infrastructure.                                                              |
| **LlamaIndex KG**  | Builds a knowledge graph from text (LLM triple extraction) and supports Cypher or NL querying.                  | No (used for document memory, not chat memory).                | Yes – used for KG-augmented RAG (Graph RAG).                           | No dedicated benchmarks; RAG performance depends on LLM and KG completeness.                                 | Open-source (MIT).        | Python library; supports various graph stores (NebulaGraph, Neo4j).  | Integrates with LangChain, supports Llama Hub data sources, any embedding model.                                                 | Relies on graph DB’s features; no extra guarantees.                                                                |
| **LightRAG**       | Multi-level RAG: graph-index + embedding-index; incremental graph updates; hybrid retriever.                    | No (focused on RAG tasks).                                     | Yes – knowledge-graph-enhanced RAG.                                    | Demonstrated higher recall/answer quality than GraphRAG (e.g. +8–12% across metrics).                        | Open-source (MIT).        | Python/Docker; includes a Streamlit UI and Ollama-compatible server. | Supports many vector DBs; can plug into Neo4j, Memgraph, PostgreSQL (AGE), etc..                                                 | No built enterprise layer; Secured by hosting environment.                                                         |
| **Cognee**         | ECL pipeline: ontology-driven ingestion → graph + vector indexing → neuro-symbolic reasoning【47†】.              | Yes – explicitly an AI memory engine (persistent KG per user). | Yes – its KG is a complete RAGable knowledge base (it “replaces RAG”). | Claims \~90% answer accuracy on benchmarks vs \~5% for unaugmented ChatGPT (internal data).                  | Open-source (Apache 2.0). | Python library; also a SaaS platform (“Cogwit Beta”).                | Many connectors: 30+ data types (PDF, DB, audio, code), vector stores (Qdrant, Milvus, etc.), graph DBs (Neo4j, Kuzu, NetworkX). | Designed for on-prem use; includes auth, namespace isolation, and supports real reasoning (ontologies, reasoners). |

Each of the above platforms combines memory and graph concepts in different ways.  Zep/Graphiti and Cognee build *dynamic, temporal knowledge graphs* specifically for agent memory, excelling at cases where data evolves over time.  GraphRAG, LlamaIndex KG, and LightRAG focus on *static KG-based retrieval* for RAG tasks.  Letta and LangMem emphasize agent **memory management**, with Letta’s approach most closely matching the traditional MemGPT research and LangMem providing modular memory APIs.  Mem0 and Cognee occupy a hybrid space: Mem0’s hybrid store and Cognee’s ontological pipeline both support persistent agent memory plus knowledge graph querying.

In summary, Zep (Graphiti) and Cognee represent the leading *temporal memory graph* platforms (with high retrieval accuracy and low latency on modern benchmarks). Letta and Mem0 offer mature agent-memory layers (open-source) with strong context-handling, while LangMem is an emerging SDK geared for LangChain developers.  On the KG frameworks side, GraphRAG and LightRAG push the envelope on KG+LLM RAG techniques, whereas LlamaIndex and Graphiti focus on integrated knowledge graphs (Graphiti for live agents, LlamaIndex for document graphs).  All these systems are extensible (integrating with vector DBs, Neo4j/other graph DBs, LangChain, etc.) and most are open-source – except Zep (commercial).  Enterprise needs (HIPAA, auth, multi-tenancy) are largely addressed by hosted offerings or underlying database features rather than built into the core open frameworks.

---

## Why Graphiti is the strongest open-source core

1. **True Bi-Temporal Store**

   * Every fact you ingest carries both its “valid from” timestamp and its ingestion timestamp. Agents can ask “What did I know about X as of last week?” or “What beliefs were retracted yesterday?”—and Graphiti answers that directly, without hacks.
2. **Read-Write Knowledge Graph**

   * Agents aren’t just readers. They can insert new beliefs, update relationships, record events, and even retract or supersede prior assertions. That makes it ideal for multi-step planning and evolving world models.
3. **Hybrid Retrieval Engine**

   * Under the hood you get embeddings + BM25 + Cypher-style graph traversals, so your RAG pipeline can pick the right retrieval mode per query (e.g. semantic lookup vs. graph-path reasoning).
4. **Real-Time Incremental Updates**

   * No batch re-indexing. As your agent interacts, facts flow immediately into the graph, and subsequent queries see the new state within milliseconds.

---

## When you might layer on something else

* **Context-Assembly & UX**
  Graphiti is the engine—but if you want turn-key session management, multi-tenant namespaces, RBAC, rate limiting, prebuilt dashboards or turnkey SaaS hosting, you’ll either build on top of Graphiti yourself or use **Zep Cloud** (which packages Graphiti + all of that).
* **Higher-Level Agent Framework**
  If you prefer an LLM-first with built-in tool registries, memory-eviction policies, and UI for orchestrating complex agents, consider **Letta** or **Mem0**. 
* **Ontology-Driven Reasoning**
  For domains that need formal ontologies and symbolic inference (e.g. healthcare, finance), you might look at **Cognee** or extend Graphiti with your own reasoning modules.

---

## Quick decision guide

| Criterion                     | Pure Graphiti                    | Graphiti + Zep Cloud         | Alternative options              |
| ----------------------------- | -------------------------------- | ---------------------------- | -------------------------------- |
| **Fully open-source**         | ✅                                | ❌ (SaaS)                     | Letta, Mem0, LangMem             |
| **Temporal, read/write KG**   | ✅                                | ✅                            | Cognee (with ontology), LightRAG |
| **Turn-key memory service**   | ❌ (you build)                    | ✅                            | Mem0 Cloud                       |
| **Agentic RAG orchestration** | ✅ (via Cypher & embeddings)      | ✅ (built-in)                 | GraphRAG (static), LightRAG      |
| **Enterprise & compliance**   | Leverage Neo4j/FalkorDB features | Built-in RBAC, SLAs, HIPAA ? | Cognee (on-prem), Mem0 Cloud     |

---

### Bottom Line

* If **you want** the **absolute most flexible**, **open-source**, **temporal**, **read/write** memory + RAG engine to embed in your own agent stack, **Graphiti** is by far the best bet.
* If you need **enterprise-grade orchestration**, **multi-tenant context management**, and a **hosted** solution on day one, consider **Zep Cloud** (it’s Graphiti under the hood).

*"Intelligence is not about memorizing facts, but about developing reasoning capabilities that can be applied to any domain. True mastery comes from building the cognitive architecture to think with the tools, not just use them."* - Intelligence Development Science
