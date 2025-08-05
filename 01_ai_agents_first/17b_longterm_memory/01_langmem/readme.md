# LangMem

To effectively master Memory Layer you have to start thinking like an AI Researcher and here's the learning plan:

- Understand Memory Concepts, and the types of memory we have as humans.
- Choose a Memory Framework to implement your concepts. LangMem have implemented Memory conceptually similar to humans and their Core APIs are separate from Storage. Like our Brain and Memories are separate and interconnected.

[Course: Long-Term Agentic Memory with LangGraph](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/)

Note: We want to use this course to learn concept which we will use to implement the LangMem Core API to integrate with the OpenAI Agents SDK

[Official Docs](https://langchain-ai.github.io/langmem/)

Key features

🧩 **[Core memory API](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/#functional-core)** that works with any storage system and any Agentic Framework, we will work with these API
🧠 Memory management tools that agents can use to record and search information during active conversations "in the hot path"
⚙️ Background memory manager that automatically extracts, consolidates, and updates agent knowledge
⚡ Native integration with LangGraph's Long-term Memory Store, available by default in all LangGraph Platform deployments, at this stage we are not interested in these integrations.

### Learning GuideLine
- First take deep-learning course and cover 01-03 notebooks.
- Then review the 00_baseline_email_assistant/
- Now we will add semantic, episodic and procedural memories to our baseline email assistant.