# Basic Agent Evaluation: Learning the Fundamentals

Learn the **core concepts** of agent evaluation through simple, hands-on Python scripts. This is a **learning-focused project** that demonstrates basic evaluation techniques using Gemini and Langfuse.

> ⚠️ **Important**: This is a **learning project**, not a production system. The examples are simplified to teach concepts clearly.

## 🎯 What This Project Actually Teaches

**Core Concepts** (what you'll learn):

- ✅ **Basic Tracing** - How to see what your agent is doing
- ✅ **Tool Monitoring** - Tracking function calls and results  
- ✅ **Metadata Addition** - Adding context to traces
- ✅ **Score Creation** - Attaching ratings to traces
- ✅ **Simple Evaluation** - Basic LLM-as-a-Judge implementation

**What This Project Does NOT Cover** (production-level):

- ❌ **Real Cost Tracking** - Actual token usage and pricing
- ❌ **Performance Analysis** - Latency breakdowns and optimization
- ❌ **Production Debugging** - Real issue resolution
- ❌ **Comprehensive Testing** - Large-scale evaluation datasets
- ❌ **Real User Feedback** - Actual user interface for feedback

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

### Step 4: Simulated User Feedback 👍👎

**File**: `04_user_feedback.py`

**What You'll Learn**:

- Create scores programmatically (simulated feedback)
- Attach different score types to traces
- Use Langfuse scoring API

**Run It**:

```bash
uv run python 04_user_feedback.py
```

**Note**: This simulates user feedback - real production would collect from actual users

---

### Step 5: Basic Dataset Evaluation 📊

**File**: `05_dataset_eval.py`

**What You'll Learn**:

- Create simple evaluation datasets (8 basic questions)
- Run LLM-as-a-Judge evaluation
- Compare two configurations
- Understand evaluation concepts

**Run It**:

```bash
uv run python 05_dataset_eval.py
```

**Note**: This uses 8 simple Q&A questions - production would use 100s of complex test cases

---

## 📊 What Gets Tracked (Basic Level)

Each trace captures:

- **LLM calls** - Model used, basic timing
- **Tool executions** - Inputs, outputs, basic timing
- **Custom metadata** - user_id, session_id, tags
- **Scores** - Basic ratings attached to traces

**Note**: This is basic tracking - production systems would include detailed cost analysis, performance metrics, and comprehensive monitoring.

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

## 💡 Key Takeaways (Learning Level)

✅ **Basic instrumentation is simple** - Just a few lines of code
✅ **Traces show agent behavior** - See what your agent is doing
✅ **Scores provide feedback** - Attach ratings to traces
✅ **Simple testing is possible** - Basic evaluation concepts
✅ **Foundation for production** - Understanding the building blocks

## 🚀 Next Steps for Production

To build **real production evaluation systems**, you'd need to add:

- **Comprehensive datasets** - 100+ complex test cases
- **Real cost tracking** - Token usage, pricing, optimization
- **Performance analysis** - Latency breakdowns, bottlenecks
- **Production debugging** - Real issue resolution tools
- **User feedback systems** - Actual UI for collecting feedback
- **A/B testing frameworks** - Scientific configuration comparison

---

**🎉 Ready to start? Run `01_basic_trace.py` now!**
