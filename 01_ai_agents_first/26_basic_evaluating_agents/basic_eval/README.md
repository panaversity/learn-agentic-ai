# Agent Evaluation: Step-by-Step with Gemini

Learn agent evaluation through **progressive, hands-on Python scripts**. Each script teaches one core concept, building your understanding systematically.

## 🎯 Learning Philosophy

This project follows **learning science principles**:

- ✅ **One concept at a time** - No overwhelming complexity
- ✅ **Progressive difficulty** - Each step builds on the previous
- ✅ **Hands-on practice** - Learn by running real code
- ✅ **Immediate feedback** - See results in Langfuse dashboard
- ✅ **Clear explanations** - Every script is heavily documented

## 📦 Prerequisites

- **Python 3.12+**
- **Gemini API key** - Free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **Langfuse account** - Free at [cloud.langfuse.com](https://cloud.langfuse.com)

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Your Keys

```bash
cp .env_backup .env
```

Then edit `.env` with your actual keys:

```env
GEMINI_API_KEY=your-gemini-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-key-here
```

## 📖 Step-by-Step Learning Path

Run these scripts **in order**. Each builds on the previous!

### Step 1: Basic Agent with Tracing 🌟

**File**: `01_basic_trace.py`

**What You'll Learn**:

- Set up Langfuse for observability
- Configure Gemini with OpenAI Agents SDK
- Run your first traced agent
- View traces in dashboard

**Run It**:

```bash
uv run python 01_basic_trace.py
```

**Expected Output**: Agent response + trace link

---

### Step 2: Agent with Tools 🔧

**File**: `02_tool_trace.py`

**What You'll Learn**:

- Add function tools to agents
- See tool calls in traces
- Monitor multi-step execution

**Run It**:

```bash
uv run python 02_tool_trace.py
```

**What to Notice**: Tool calls appear as separate spans

---

### Step 3: Custom Metadata 🏷️

**File**: `03_custom_metadata.py`

**What You'll Learn**:

- Add user_id and session_id
- Use tags for filtering
- Include domain-specific data

**Run It**:

```bash
uv run python 03_custom_metadata.py
```

**Why It Matters**: Track WHO uses the agent and HOW

---

### Step 4: User Feedback 👍👎

**File**: `04_user_feedback.py`

**What You'll Learn**:

- Collect user ratings
- Attach scores to traces
- Build feedback loops

**Run It**:

```bash
uv run python 04_user_feedback.py
```

**Real-World Use**: Identify what works and what doesn't

---

### Step 5: Dataset Evaluation 📊

**File**: `05_dataset_eval.py`

**What You'll Learn**:

- Create evaluation datasets
- Run systematic tests
- Compare configurations
- Make data-driven decisions

**Run It**:

```bash
uv run python 05_dataset_eval.py
```

**The Big Picture**: Test before deploying!

---

## 📊 What Gets Tracked

Each trace captures:

- **LLM calls** - Model, tokens, latency
- **Tool executions** - Inputs, outputs, timing
- **Costs** - Token usage per request
- **Custom data** - Your metadata, tags, scores

## 🎓 Learning Tips

1. **Run in order** - Each script builds on the previous
2. **Check Langfuse** - Always view the trace after running
3. **Experiment** - Modify code and see what changes
4. **Read comments** - Scripts are heavily documented
5. **Ask questions** - Understanding beats memorization

## 🔗 View Your Results

After running scripts, visit: [cloud.langfuse.com/traces](https://cloud.langfuse.com/traces)

## 📚 Learn More

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Langfuse Docs](https://langfuse.com/docs)
- [Evaluation Best Practices](https://langfuse.com/blog/2025-03-04-llm-evaluation-101-best-practices-and-challenges)

## 💡 Key Takeaways

✅ **Instrumentation is simple** - Just a few lines
✅ **Visibility is powerful** - See everything your agent does
✅ **Metrics guide improvement** - Track, analyze, optimize
✅ **Testing prevents problems** - Catch issues before production
✅ **Feedback drives quality** - User ratings are gold

---

**🎉 Ready to start? Run `01_basic_trace.py` now!**
