# Agent Evaluation: From Concepts to Production

This lesson teaches **agent evaluation** - the critical missing piece for production AI systems. We start with basic concepts and build toward production-ready evaluation systems.

## 🎯 **Two-Phase Learning Approach**

### **Phase 1: Basic Concepts** (`basic_eval/`)
Learn the fundamentals through simple, hands-on examples:
- Basic tracing and monitoring
- Simple evaluation techniques  
- Core evaluation concepts

### **Phase 2: Production Systems** (Future)
Build real production evaluation systems using [eval-driven development](https://cookbook.openai.com/examples/partners/eval_driven_system_design/receipt_inspection):
- Real business problems
- Comprehensive evaluation datasets
- Cost-benefit analysis
- Production monitoring

## 🚀 **The Real Goal: Production-Ready Evaluation**

**Before**: "My agent works!"
**After**: "My agent has 94% success rate, $0.05/request cost, 2.3s latency, and 4.6/5 user rating."

**This is the difference between demo and production.** 🎯

This lesson uses **Google's Gemini models** and follows the [OpenAI Cookbook's eval-driven development approach](https://cookbook.openai.com/examples/partners/eval_driven_system_design/receipt_inspection).

> 📖 **What You Already Know** (from lessons 1-25):
>
> - Building agents with tools, handoffs, guardrails
> - Session memory (lesson 21)
> - Vector memory with embeddings (lesson 22)
> - Basic tracing concepts (lesson 24)
>
> 🎯 **What's NEW in This Lesson**:
>
> - **Phase 1**: Basic evaluation concepts and tools
> - **Phase 2**: Production evaluation systems (future)
> - **Focus**: Learning to prove agents work, not just build them!

### Can you answer these about YOUR agent?

- ❓ How much does each interaction cost?
- ❓ How fast does it respond?
- ❓ Which tools are used most often?
- ❓ What's the failure rate?
- ❓ Are users satisfied?
- ❓ How does Config A compare to Config B?
- ❓ Did my last change improve performance?

**If you can't answer these** → You need lesson 26!

This lesson teaches you how to **EVALUATE** those agents through two phases:

### Phase 1: Basic Concepts (Current)

| Topic                    | What You'll Learn                                | Current Status |
| ------------------------ | ------------------------------------------------ | -------------- |
| **Basic Tracing**        | See what your agent is doing                     | ✅ Complete    |
| **Tool Monitoring**      | Track function calls and results                 | ✅ Complete    |
| **Custom Metadata**      | Add user_id, session_id to traces                | ✅ Complete    |
| **Simulated Feedback**   | Create scores programmatically                   | ✅ Complete    |
| **Simple Evaluation**    | Basic LLM-as-a-Judge implementation              | ✅ Complete    |

### Phase 2: Production Systems (Future)

| Topic                    | What You'll Learn                                | Why It's Different                           |
| ------------------------ | ------------------------------------------------ | -------------------------------------------- |
| **Real Cost Tracking**   | Actual token usage, pricing, optimization        | Production metrics, not demos                |
| **Performance Analysis** | Latency breakdowns, bottleneck identification    | Real optimization, not basic timing          |
| **Comprehensive Testing**| 100+ test cases with edge cases and failures     | Production-scale evaluation                  |
| **User Feedback Systems**| Actual UI for collecting real user feedback      | Real feedback loops, not simulated           |
| **A/B Testing Framework**| Scientific configuration comparison               | Data-driven optimization                     |
| **Production Debugging**| Real issue resolution and monitoring             | Production troubleshooting                    |


## 📚 Overview

Agent **evaluation** is the missing piece for production-ready AI systems. This lesson teaches evaluation through two phases:

### Phase 1: Basic Concepts (Current)
1. **Basic Tracing** - See what your agent is doing
2. **Tool Monitoring** - Track function calls and results  
3. **Custom Metadata** - Add context to your traces
4. **Simulated Feedback** - Create scores programmatically
5. **Simple Evaluation** - Basic LLM-as-a-Judge implementation

### Phase 2: Production Systems (Future)
1. **Real Cost Tracking** - Token usage, pricing, optimization
2. **Performance Analysis** - Latency breakdowns, bottlenecks
3. **Comprehensive Testing** - 100+ test cases with edge cases
4. **User Feedback Systems** - Actual UI for feedback collection
5. **Production Monitoring** - Real debugging and optimization

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

## 📖 Learning Path: Two Phases

### Phase 1: Basic Concepts (Current - `basic_eval/`)

Learn fundamentals through **progressive Python scripts**:

#### Step 1: Basic Agent with Tracing
**File**: `01_basic_trace.py`
- Run your first agent with Gemini
- See traces appear in Langfuse
- Understand the trace structure

#### Step 2: Agent with Tools
**File**: `02_tool_trace.py`
- Add function tools to your agent
- See how tool calls are traced
- Monitor multi-step execution

#### Step 3: Custom Metadata
**File**: `03_custom_metadata.py`
- Enrich traces with user_id, session_id
- Add tags for filtering
- Include custom domain data

#### Step 4: Simulated User Feedback
**File**: `04_user_feedback.py`
- Create scores programmatically (simulated feedback)
- Attach different score types to traces
- Use Langfuse scoring API

#### Step 5: Basic Dataset Evaluation
**File**: `05_dataset_eval.py`
- Create simple evaluation datasets (8 basic questions)
- Run LLM-as-a-Judge evaluation
- Compare two configurations

### Phase 2: Production Systems (Future - `production_eval/`)

Build real production evaluation systems following [eval-driven development](https://cookbook.openai.com/examples/partners/eval_driven_system_design/receipt_inspection):

- **Real business problems** - Like receipt processing, customer support
- **Comprehensive datasets** - 100+ test cases with edge cases
- **Cost-benefit analysis** - Connect evals to actual business value
- **Production monitoring** - Real debugging and optimization

## 🎓 Key Takeaways

### Phase 1: Basic Concepts (Current)
- **Basic instrumentation is simple** - Just a few lines of code
- **Traces show agent behavior** - See what your agent is doing
- **Scores provide feedback** - Attach ratings to traces
- **Simple testing is possible** - Basic evaluation concepts
- **Foundation for production** - Understanding the building blocks

### Phase 2: Production Systems (Future)
- **Eval-driven development** - Use evals to guide improvements
- **Business value connection** - Connect evals to actual costs/benefits
- **Production monitoring** - Real debugging and optimization
- **Comprehensive testing** - 100+ test cases with edge cases
- **Continuous improvement** - Use evals to iterate and optimize

## 📚 References

- [OpenAI Cookbook: Eval-Driven System Design](https://cookbook.openai.com/examples/partners/eval_driven_system_design/receipt_inspection) - **The gold standard for production evaluation**
- [OpenAI Cookbook: Evaluate Agents](https://cookbook.openai.com/examples/agents_sdk/evaluate_agents)
- [Langfuse Documentation](https://langfuse.com/docs)
- [LLM Evaluation Best Practices](https://langfuse.com/blog/2025-03-04-llm-evaluation-101-best-practices-and-challenges)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)


## 💡 Learning Tips

### Phase 1: Basic Concepts
1. **Run each script in order** - They build on each other
2. **Check Langfuse after each run** - See what gets tracked
3. **Experiment with modifications** - Change prompts, models, metadata
4. **Read the comments** - Each script is heavily documented
5. **Ask questions** - Understanding > memorization

### Phase 2: Production Systems (Future)
1. **Follow eval-driven development** - Use evals to guide improvements
2. **Connect to business value** - Measure actual costs and benefits
3. **Build comprehensive datasets** - 100+ test cases with edge cases
4. **Implement real monitoring** - Production debugging and optimization
5. **Iterate continuously** - Use evals to drive system improvements

---

**Next Steps**: 
- **Phase 1**: Go to `basic_eval/` and run `01_basic_trace.py`! 🚀
- **Phase 2**: Build production evaluation systems following [eval-driven development](https://cookbook.openai.com/examples/partners/eval_driven_system_design/receipt_inspection)
