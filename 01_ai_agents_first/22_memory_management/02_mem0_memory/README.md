# 🧠 Mem0 + AI Agents – Beginner’s Guide 

Give your AI assistant the power of **memory** using [Mem0](https://mem0.ai) + [OpenAI Agents SDK](https://github.com/openai/agents).
With memory, your assistant can **remember your name, preferences, and past conversations** across sessions.

---

## 🌟 Why Memory Matters

Without memory, every chat with AI is like meeting a stranger:

* ❌ You have to repeat your name every time
* ❌ It forgets your preferences instantly
* ❌ Conversations feel robotic

With **Mem0 memory**:

* ✅ AI remembers your name, hobbies, and favorite food
* ✅ Personalized responses based on your history
* ✅ Feels more natural and human-like

---

## 📦 Prerequisites (Before You Start)

1. **Python 3.10+** installed
2. **Basic Python knowledge** (variables, functions, imports)
3. API Keys:

   * [Mem0 API Key](https://mem0.ai) (memory storage)
   * [Gemini API Key](https://ai.google.dev/) (LLM brain)

---

## ⚙️ Installation

Open your terminal and run:

```bash
uv add openai-agents mem0ai python-dotenv
```

---

## 🔑 Setting Up API Keys

1. **Get Mem0 API Key**

   * Sign up at [Mem0](https://mem0.ai)
   * Copy your key from the dashboard

2. **Get Gemini API Key**

   * Go to [Google AI Studio](https://aistudio.google.com)
   * Create and copy a new API key

3. **Create `.env` File**
   In your project folder, create `.env`:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   MEM0_API_KEY=your_mem0_api_key
   ```

⚠️ Never share your API keys or upload them to GitHub.

---

## 📜 Code Overview

### 1. Connect to Gemini (AI Brain)

```python
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
```

### 2. Setup Mem0 (Memory Notebook)

```python
mem0 = MemoryClient()
```

### 3. Create Memory Tools (Save & Recall)

```python
@function_tool
def add_memory(query: str, user_id: str) -> str:
    return mem0.add([{"role": "user", "content": query}], user_id=user_id)

@function_tool
def search_memory(query: str, user_id: str) -> str:
    return mem0.search(query, user_id=user_id, limit=3)
```

### 4. Build the Agent (The Assistant)

```python
agent = Agent(
    name="Memory Assistant",
    instructions="""You are a helpful assistant with memory.
    Always check memory first before answering.
    Save new details about the user whenever possible.""",
    tools=[search_memory, add_memory],
    model=llm_model,
)
```

---

## 🧪 Running the Example

Save code as `main.py` and run:

```bash
uv run main.py
```

### Example Interaction

**First chat:**

```
User: My name is Wania and I like programming and my favourite dish is biryani `wania_123`
Agent: Got it! I’ll remember that.
```

**Second chat:**

```
User: What is my name and what I like to do and user_id is `wania_123`?
Agent: Your name is Wania, you like programming, and your favourite dish is biryani.
```

🎉 The agent remembered you!

---

## 🗂️ Key Concepts for Beginners

* **LLM (Large Language Model):** The “brain” of the AI (Gemini here).
* **Mem0:** The notebook where memories are stored.
* **Agent:** The assistant that uses tools + memory.
* **Tools:** Functions like `add_memory` and `search_memory`.
* **User ID:** Like a folder name — keeps memories separate for each user.

---

## 🛠️ Common Issues & Fixes

* ❌ **No memories found** → Make sure you use the **same `user_id`** for saving and searching.
* ❌ **API key error** → Check `.env` file and reload your terminal.
* ❌ **Module not found** → Run:

  ```bash
  uv add openai-agents mem0ai python-dotenv
  ```

---

## 🎯 Practice Exercise

Try this on your own:

1. Add a memory: “My favorite color is blue.”
2. Later, ask: “What’s my favorite color?”
3. See if the agent remembers!

---

## ✅ Best Practices

* Always use **unique user IDs** for each person.
* Don’t store **sensitive information** (like passwords).
* Start with **simple info** before complex data.
* Use **clear instructions** when talking to the agent.

---

## 🚀 Next Steps

* Create **multiple agents** (e.g., travel planner, health coach) sharing the same memory.
* Use **filters and metadata** for advanced memory search.
* Build a **chat web app** so users can interact with your memory-powered AI.

---

## 🎉 Conclusion

Congratulations! 
You just learned how to give an AI assistant **memory** using Mem0.
Now your agent can remember names, preferences, and more — making conversations smarter and more human-like.

Keep experimenting, and soon you’ll build AI assistants that feel like real companions. 
