
````markdown
# 🧠 AI Assistant with Session Memory (Using OpenAI Gemini)

This project shows how to build a **basic AI math assistant** that remembers conversations using **session memory**. It uses OpenAI's Gemini model and stores chat history in a local **SQLite database**.

---

## 💡 What is Session Memory?

Imagine you're talking to an AI, and it remembers what you said before. This is called **session memory**.

### 🔹 Example:

1. You say: “What is 2 + 2?”  
   AI says: “4”

2. You say: “Multiply the answer by 2.”  
   AI says: “4 × 2 = 8”

➡️ The AI remembered your last message. Without memory, it wouldn’t know what "the answer" means!

---

## 🎯 Why is Session Memory Important?

- ✅ Makes the AI smarter
- ✅ Conversations feel natural (just like talking to a human)
- ✅ Each user gets their own memory (separate sessions)
- ✅ Great for chatbots, virtual assistants, and teaching tools

---

## 📦 Requirements

Make sure you have:

- Python 3.8+
- OpenAI API key (Gemini API)
- Required Python packages

### Install packages:

```bash
pip install -r requirements.txt
````

Add a `.env` file with this line:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```



## 🧠 How the Code Works (Step-by-Step)

### 1. 🔐 Load API Key

We load your Gemini key using Python dotenv:

```python
from dotenv import load_dotenv
load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
```

---

### 2. 🔌 Connect to Gemini

We use Gemini API with OpenAI-compatible client:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

---

### 3. 🧠 Create the Agent

This is your smart assistant:

```python
agent = Agent(
    name="Assistant",
    instructions="You are a basic math assistant. Reply very concisely.",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=client
    ),
)
```

---

### 4. 💾 Setup Session Memory

We use SQLite database `maths_db.db` and set a session ID:

```python
session = SQLiteSession(
    session_id="user_123",
    db_path="maths_db.db"
)
```

---

### 5. 💬 Ask Questions

We run questions through the agent and keep memory:

```python
result1 = Runner.run_sync(agent, "what is 2+2?", session)
result2 = Runner.run_sync(agent, "Multiply whatever response you get by 2.", session)

print(result1.final_output)  # → 4
print(result2.final_output)  # → 8
```

---

## 👤 What if a New User Comes?

Every user gets their **own session ID** like this:

```python
session = SQLiteSession(session_id="user_456", db_path="maths_db.db")
```

This creates a **separate chat history** in the same database, so users don’t mix up messages.

---

## 🗃️ Where is Memory Stored?

We use a file called `maths_db.db`. This is a local database that stores all conversation history.

You can open it with any SQLite viewer and see user sessions and messages.

---

## 🔗 Useful Links

* [💾 SQLite Database](https://www.sqlite.org/index.html)
* [🌍 Openai SDK Sessions (Official Docs)](https://openai.github.io/openai-agents-python/sessions/)

---
