# Sub-Lesson 01: Context Trimming

## 📖 Overview

Learn how to implement **context trimming** - keeping only the last N turns and dropping older context. This is the simplest and most common context management pattern.

## 🎯 The Problem

As conversations grow longer:

- Context window fills up with old, irrelevant messages
- Costs increase (more tokens per request)
- Latency increases (longer prompts to process)
- Models may lose focus on recent context

## 💡 The Solution

**Context Trimming**: Keep only the last N "turns" of conversation.

- A **turn** = one user message + all responses (assistant, tool calls, tool results) until the next user message
- When turn count > `max_turns`, drop the oldest turns
- Keep turn boundaries intact (don't split mid-turn)

## ✅ When to Use Context Trimming

**Best for**:

- Short workflows (< 30 minutes)
- Tool-heavy operations (support agents, data analysis)
- Tasks where recent context matters more than distant context
- Need for deterministic, predictable behavior

**Avoid when**:

- Need to remember distant context (long research, multi-day projects)
- Tasks with dependencies across many turns
- Need to reference early conversation details

## 📊 Pros & Cons

| Pros                                         | Cons                              |
| -------------------------------------------- | --------------------------------- |
| ✅ Zero latency overhead                     | ❌ Hard cut-off loses old context |
| ✅ Deterministic (no summarization variance) | ❌ Can "forget" important details |
| ✅ Simple to implement and debug             | ❌ No long-range memory           |
| ✅ Predictable token usage                   | ❌ May repeat resolved issues     |

## 🏗️ How It Works

### Step 1: Define a Turn

```
Turn 1:
  - user: "My laptop won't start"
  - assistant: "Let's troubleshoot..."
  - tool_call: check_power_status()
  - tool_result: "Power cable connected"
  - assistant: "Try holding power button..."

Turn 2:
  - user: "Still not working"
  - assistant: "Let's check the battery..."
  ...
```

### Step 2: Count User Messages

- Walk through history
- Count messages where `role == "user"` and NOT synthetic
- Synthetic messages (summaries) don't count as real turns

### Step 3: Trim to Last N

- If user turns > `max_turns`, find the earliest of the last N user messages
- Keep everything from that point forward
- Drop everything before

## 📝 Files in This Sub-Lesson

- **`01_basic_trimming.py`** - Minimal TrimmingSession implementation
- **`02_production_trimming.py`** - Production version with logging, metadata
- **`03_evaluate_trimming.py`** - Evaluation framework with metrics
- **`.env_backup`** - Environment template

## 🚀 Getting Started

### 1. Set up environment

```bash
# Copy environment template
cp .env_backup .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_key_here
```

### 2. Run basic example

```bash
python 01_basic_trimming.py
```

### 3. Try production version

```bash
python 02_production_trimming.py
```

### 4. Run evaluation

```bash
python 03_evaluate_trimming.py
```

## 🔧 Key Parameter: `max_turns`

### How to Choose

1. **Estimate average turn complexity**:

   - Simple Q&A: 1 turn = ~200 tokens
   - Tool-heavy: 1 turn = ~1,500 tokens (user + tool calls + results)
   - Complex reasoning: 1 turn = ~3,000 tokens

2. **Calculate token budget**:

   - Target: Use 40-60% of context window
   - For Gemini 2.0 Flash (272k context): Target ~100k tokens
   - Example: 100k / 1,500 tokens per turn = ~66 turns max

3. **Start conservatively**:
   - Begin with `max_turns=5-8` for most use cases
   - Monitor: Are agents "forgetting" recent context? Increase
   - Monitor: Are costs too high? Decrease

### Examples by Use Case

| Use Case                      | Estimated Tokens/Turn | Recommended `max_turns` |
| ----------------------------- | --------------------- | ----------------------- |
| Simple chatbot                | 200                   | 20-30                   |
| Customer support (tool-heavy) | 1,500                 | 5-8                     |
| Code analysis                 | 3,000                 | 3-5                     |
| Research assistant            | 2,000                 | 8-12                    |

## 📊 Evaluation Metrics

Track these to measure effectiveness:

### Efficiency Metrics

- **Tokens per turn**: Should stabilize after trimming starts
- **Context window utilization**: Target 40-60%
- **Cost per conversation**: Lower with trimming

### Quality Metrics

- **Recent recall**: Can agent remember last 3-5 turns?
- **Coherence**: Do responses align with recent context?
- **Task completion**: Does agent still solve problems?

## 🎯 Real-World Scenario

**Customer Support Agent** (implemented in examples):

- User reports multiple issues over 30-minute conversation
- Each issue requires 3-5 tool calls (check logs, update system, verify)
- Without trimming: Context balloons to 50+ turns, costs spike
- With trimming (max_turns=5): Agent stays focused on current issue

## 🔍 Common Pitfalls

1. **Trimming too aggressively**: `max_turns=2` may lose critical recent context
2. **Not accounting for tool calls**: Each turn may have multiple tool results
3. **Forgetting turn boundaries**: Splitting mid-turn breaks coherence
4. **Not monitoring metrics**: Can't optimize without data

## 📚 Next Steps

After mastering context trimming:

1. Compare trimming effectiveness on your specific use case
2. Tune `max_turns` based on your token budget and task requirements
3. Move to **02_context_summarization** if you need long-range memory
4. Consider hybrid approaches (trimming + notes) for multi-hour tasks

---

**Ready to code?** Open `01_basic_trimming.py` to see the implementation!
