# Memory Augmentation

This step is designed to take you from the fundamentals of agentic memory to hands-on implementation and a forward-looking research perspective.

## Step 1: Fundamentals of Agentic Memory

Goal: Understand the core concepts and vocabulary of memory in AI systems i.e: Short Term Memory, Long Term Memoery (different types i.e: semantic, procedural, episodic)



## Step 2: Get Hands on Memory Augmentation

Goal: Build and interact with a real, graph-based memory system using Graphiti.

1. First, review the current implementation options to understand the ecosystem.
    - Vector-based: Mem0, LangMem (open-source)
    - Graph-based: Zep, Cognee
    - Our Focus: We will use Graphiti to implement Graph-Based Agentic Memory. The concepts you learn here are transferable to other systems.

2. Understand "Why Graphiti?": Graphiti is the powerful open-source framework that powers Zep. It's a Python framework designed for building temporally-aware knowledge graphs that can be updated in real-time without batch recomputation, making it ideal for dynamic agentic systems.

3. Get hands on Graphiti MCP Server for Agentic Memory
- https://help.getzep.com/graphiti/getting-started/mcp-server 

4. BreakDown how Graphiti Works - Documentation
- https://help.getzep.com/graphiti/getting-started/welcome

5. Implement [OpenAI Agents SDK built-in session memory](https://openai.github.io/openai-agents-python/sessions/) and customize to manage tasks context.

6. Connect MCP server to OpenAI Agents sDK and [Implement Reflect Design Pattern](https://www.deeplearning.ai/the-batch/agentic-design-patterns-part-2-reflection/)

## Step 3: Adopt a Researcher's Mindset
Current Work on Memory is too early and will evolve a lot. 

- The Big Picture: Recognize that Long-Term Memory (LTM), Short-Term Memory (STM), and Retrieval-Augmented Generation (RAG) are not isolated concepts. They are converging into a single, cohesive architecture for intelligent AI. As an AI Engineer, developing research skills is crucial.
- Essential Reading:
    - [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956)
    - Read [Section 3 Methodolodgy](https://arxiv.org/html/2502.12110v10) about how it's derived from Zettelkasten method

## Broaden Your Perspective (Optional but Recommended)
Goal: Deepen your understanding by exploring alternative architectures and the original inspiration: human memory.

1. Explore Mem0: To understand the trade-offs, get hands-on with a vector-native approach ⁠https://docs.mem0.ai/openmemory/overview 
2. Study the Original Blueprint (Human Memory): To build truly empathetic and effective AI, it's invaluable to understand the complexities of human cognition. Watch this Podcast:[ Human Memory, Imagination, Deja Vu, and False Memories | Lex Fridman Podcast](https://www.youtube.com/watch?v=4iuepdI3wCU)