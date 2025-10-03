# Evaluating AI Agents: Step-by-Step with Gemini

Learn how to monitor, trace, debug, and [evaluate your AI agents using the OpenAI Agents SDK integrated with Langfuse](https://cookbook.openai.com/examples/agents_sdk/evaluate_agents) for comprehensive observability.

This lesson uses **Google's Gemini models** and focuses on hands-on Python scripts that teach **one concept at a time**.

> 📖 **What You Already Know** (from lessons 1-25):
>
> - Building agents with tools, handoffs, guardrails
> - Session memory (lesson 21)
> - Vector memory with embeddings (lesson 22)
> - Basic tracing concepts (lesson 24)
>
> 🎯 **What's NEW in This Lesson**:
>
> - **Evaluation & observability** - Monitor, test, and improve agents
> - **Not** memory management - focus is on proving agents work!
>
> 🔍 **[What Makes This Different? →](WHAT_IS_NEW.md)**

> 🎓 **[See Complete Learning Outcomes →](LEARNING_OUTCOMES.md)**

## 📚 Overview

Agent **evaluation** is the missing piece for production-ready AI systems. This lesson progressively teaches:

1. **Basic Tracing** - See what your agent is doing
2. **Tool Monitoring** - Track function calls and results
3. **Custom Metadata** - Add context to your traces
4. **User Feedback** - Collect ratings on responses
5. **Dataset Evaluation** - Test systematically

## 🎯 Why Evaluate AI Agents?

1. **Debugging** - Identify when and why tasks fail
2. **Cost Management** - Track token usage and optimize expenses
3. **Performance Monitoring** - Measure latency and response times
4. **Quality Assurance** - Ensure reliable and safe outputs
5. **Continuous Improvement** - Use feedback to enhance agent capabilities

## 🔑 Key Concepts

### Online Evaluation (Production Monitoring)

Monitor agents in real-time with actual users:

- **Cost tracking** - Token usage and API costs per request
- **Latency monitoring** - Response time for each step
- **User feedback** - Thumbs up/down ratings from users
- **LLM-as-a-Judge** - Automated quality scoring

### Offline Evaluation (Pre-deployment Testing)

Test agents systematically before releasing:

- **Dataset benchmarking** - Run on known test cases
- **A/B testing** - Compare different model/prompt configurations
- **Regression testing** - Ensure changes don't break existing features

## � Tools Used

- **OpenAI Agents SDK** - Framework for building AI agents
- **Google Gemini** - LLM provider (via OpenAI-compatible API)
- **Langfuse** - Observability and evaluation platform
- **Pydantic Logfire** - OpenTelemetry instrumentation
- **Hugging Face Datasets** - Benchmark data sources

## 🚀 Getting Started

### Prerequisites

## 🚀 Getting Started

### Prerequisites

You'll need API keys for:

- **Gemini** - Get free key at [Google AI Studio](https://aistudio.google.com/apikey)
- **Langfuse** - Create free account at [cloud.langfuse.com](https://cloud.langfuse.com)

### Setup

1. Navigate to the `basic_eval/` directory
2. Copy `.env_backup` to `.env` and add your keys
3. Run `uv sync` to install dependencies
4. Follow the step-by-step scripts below

## 📖 Learning Path: One Step at a Time

We teach evaluation through **progressive Python scripts**, each building on the last:

### Step 1: Basic Agent with Tracing

**File**: `01_basic_trace.py`

- Run your first agent with Gemini
- See traces appear in Langfuse
- Understand the trace structure

### Step 2: Agent with Tools

**File**: `02_tool_trace.py`

- Add function tools to your agent
- See how tool calls are traced
- Monitor multi-step execution

### Step 3: Custom Metadata

**File**: `03_custom_metadata.py`

- Enrich traces with user_id, session_id
- Add tags for filtering
- Include custom domain data

### Step 4: User Feedback

**File**: `04_user_feedback.py`

- Collect user ratings (thumbs up/down)
- Attach scores to traces
- Build feedback loops

### Step 5: Dataset Evaluation

**File**: `05_dataset_eval.py`

- Create evaluation datasets
- Run systematic tests
- Compare configurations

## 🎓 Key Takeaways

- **Instrumentation is simple** - Just a few lines of code
- **Traces show everything** - See each step your agent takes
- **Metrics guide optimization** - Track costs, speed, and quality
- **Feedback drives improvement** - User ratings are invaluable
- **Testing prevents bugs** - Evaluate before deploying

## 📚 References

- [OpenAI Cookbook: Evaluate Agents](https://cookbook.openai.com/examples/agents_sdk/evaluate_agents)
- [Langfuse Documentation](https://langfuse.com/docs)
- [LLM Evaluation Best Practices](https://langfuse.com/blog/2025-03-04-llm-evaluation-101-best-practices-and-challenges)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)

## 📁 Project Structure

```
26_basic_evaluating_agents/
├── readme.md              # This file
└── basic_eval/            # Step-by-step evaluation project
    ├── .env_backup        # Environment template
    ├── pyproject.toml     # Dependencies
    ├── 01_basic_trace.py  # Step 1: First traced agent
    ├── 02_tool_trace.py   # Step 2: Tools and tracing
    ├── 03_custom_metadata.py  # Step 3: Enrich traces
    ├── 04_user_feedback.py    # Step 4: Collect ratings
    └── 05_dataset_eval.py     # Step 5: Systematic testing
```

## 💡 Learning Tips

1. **Run each script in order** - They build on each other
2. **Check Langfuse after each run** - See what gets tracked
3. **Experiment with modifications** - Change prompts, models, metadata
4. **Read the comments** - Each script is heavily documented
5. **Ask questions** - Understanding > memorization

---

**Next Steps**: Go to `basic_eval/` and run `01_basic_trace.py`! 🚀
