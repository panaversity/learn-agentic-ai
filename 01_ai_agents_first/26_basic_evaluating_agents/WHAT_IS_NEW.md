# What's Different: Lesson 26 vs Previous Lessons

This document clarifies what makes lesson 26 unique and what you've already learned.

## 📚 Previous Lessons (1-25) - Agent Building

You've already learned how to **BUILD** agents:

| Lesson | What You Learned                                      | Status  |
| ------ | ----------------------------------------------------- | ------- |
| 01-10  | Basic agents, tools, configuration                    | ✅ Done |
| 11-18  | Handoffs, structured outputs, guardrails              | ✅ Done |
| 19-20  | Agent lifecycle, run lifecycle                        | ✅ Done |
| **21** | **Session memory** - Managing conversation state      | ✅ Done |
| **22** | **Vector memory** - Embeddings, mem0, semantic search | ✅ Done |
| 23-25  | Custom runners, tracing basics, Chainlit UI           | ✅ Done |

**Key Point**: You know how to build sophisticated agents with memory, tools, and handoffs.

---

## 🎯 Lesson 26 - Agent Evaluation (NEW!)

This lesson teaches you how to **EVALUATE** those agents:

### What's NEW:

| Topic                    | What You'll Learn                                | Why It's Different                           |
| ------------------------ | ------------------------------------------------ | -------------------------------------------- |
| **Langfuse Integration** | Production-grade observability platform          | Not basic tracing - full evaluation platform |
| **Trace Analysis**       | Debug by inspecting detailed traces              | Beyond print statements                      |
| **Custom Metadata**      | Add user_id, session_id for **filtering traces** | NOT session memory - just trace metadata!    |
| **User Feedback**        | Collect ratings, attach to traces                | Systematic feedback loops                    |
| **Dataset Evaluation**   | Create benchmarks, run tests, compare configs    | Offline evaluation methodology               |
| **Cost & Performance**   | Track tokens, latency, optimize                  | Production metrics                           |
| **A/B Testing**          | Scientific comparison of configurations          | Data-driven optimization                     |

---

## 🔍 Important Distinctions

### Session ID: Two Different Uses

**Lesson 21 (Session Memory)**:

```python
# Managing conversation state/memory
session.add_message(...)
session.get_history()
```

- **Purpose**: Store and retrieve conversation history
- **Focus**: Memory management

**Lesson 26 (Evaluation)**:

```python
# Adding metadata to traces for filtering
span.update_trace(
    session_id="eval-session-123",  # Just a label for filtering!
    user_id="user_42"
)
```

- **Purpose**: Filter and search traces by session
- **Focus**: Observability, not memory

---

## 📊 The Complete Picture

```
Lessons 1-25: BUILD agents
    ↓
    You have: Working agent with tools, memory, handoffs
    ↓
Lesson 26: EVALUATE agents
    ↓
    You can: Prove it works, monitor it, improve it
    ↓
    PRODUCTION READY! 🚀
```

---

## ✅ Quick Check: Do You Need This Lesson?

### Can you answer these about YOUR agent?

- ❓ How much does each interaction cost?
- ❓ How fast does it respond?
- ❓ Which tools are used most often?
- ❓ What's the failure rate?
- ❓ Are users satisfied?
- ❓ How does Config A compare to Config B?
- ❓ Did my last change improve performance?

**If you can't answer these** → You need lesson 26!

**If you CAN answer these** → You already know evaluation! 🎉

---

## 🎯 Summary

### You Already Know:

- ✅ Building agents (lessons 1-20)
- ✅ Session memory management (lesson 21)
- ✅ Vector memory with embeddings (lesson 22)
- ✅ Basic tracing concepts (lesson 24)

### You'll Learn in Lesson 26:

- 🆕 Production observability with Langfuse
- 🆕 Systematic evaluation methodology
- 🆕 User feedback systems
- 🆕 Dataset-based testing
- 🆕 Cost and performance monitoring
- 🆕 A/B testing and optimization

### The Result:

**Before**: "I built an agent with memory and tools"
**After**: "I built an agent that costs $0.05/request, responds in 2.3s, has 94% success rate, and users rate it 4.6/5"

**That's production-ready.** 💪

---

**Ready to start? Go to `basic_eval/` and run `01_basic_trace.py`!**
