# Context Summarization

## Overview

**Context Summarization** uses an LLM to compress older conversation history into concise summaries, preserving key information while dramatically reducing token usage. This is more sophisticated than simple trimming.

## The Problem

In long conversations:

- **Token costs accumulate** with every turn sent to the LLM
- **Important context** from early conversation may be lost with simple trimming
- **Semantic coherence** is needed - can't just drop arbitrary messages

## The Solution

Context summarization:

1. **Keep recent turns** verbatim (e.g., last 5-10 messages)
2. **Summarize older turns** into a concise system message
3. **Preserve key facts** (user preferences, entity names, decisions made)
4. **Update summary incrementally** as conversation grows

### Example Flow

```
Original (20 turns, ~5000 tokens):
User: I'm planning a trip to Japan
Agent: Great! When are you planning to go?
User: Next spring, around April
Agent: Perfect timing for cherry blossoms...
[15 more turns discussing flights, hotels, budget]

Summarized (5 turns + summary, ~1500 tokens):
Summary: User is planning trip to Japan in April (cherry blossom season).
         Budget: $3000. Prefers boutique hotels. Interested in Kyoto temples.
[Last 5 turns verbatim]
```

## When to Use

✅ **Use summarization when:**

- Conversations regularly exceed 20-30 turns
- Early context has important facts that can't be lost
- You need semantic coherence (trimming would break flow)
- Token costs are a concern but quality can't be compromised

❌ **Don't use summarization when:**

- Conversations are naturally short (< 10 turns)
- Recent context is all that matters
- Summarization cost exceeds savings
- Real-time latency is critical (summarization adds delay)

## Pros & Cons

### Pros

- ✅ **Preserves important context** from entire conversation
- ✅ **Dramatic token savings** (60-80% reduction possible)
- ✅ **Maintains coherence** better than trimming
- ✅ **Configurable** (how much to keep verbatim vs. summarize)

### Cons

- ❌ **Adds latency** (extra LLM call for summarization)
- ❌ **Costs tokens** to generate summary
- ❌ **Information loss** (summarization is lossy)
- ❌ **Complexity** (needs good summarizer prompts)

## Implementation Pattern

### 1. LLM Summarizer

```python
from openai_agents import Agent, LLMSummarizer

summarizer = LLMSummarizer(
    model=llm_model,
    system_message="Summarize the conversation, preserving key facts and decisions.",
    max_tokens=500  # Limit summary length
)
```

### 2. Summarizing Session

```python
from openai_agents import SummarizingSession

session = SummarizingSession(
    summarizer=summarizer,
    keep_turns=5  # Keep last 5 turns verbatim
)
```

### 3. Agent Integration

```python
agent = Agent(
    name="LongConversationAgent",
    model=llm_model,
    session=session  # Use summarizing session
)
```

## Configuration Guide

### `keep_turns` Parameter

Controls how many recent turns to keep verbatim:

| Turns | Use Case                            | Token Impact      |
| ----- | ----------------------------------- | ----------------- |
| 3-5   | Short-term context (support)        | High compression  |
| 5-10  | Medium conversations (consultation) | Balanced          |
| 10-20 | Long discussions (therapy)          | Lower compression |

### Summarizer Prompt Design

**Good summarizer prompts:**

```
"Summarize the conversation, preserving:
 1. User's main goal and preferences
 2. Key decisions made
 3. Important entity names (people, places, products)
 4. Open questions or next steps
 Keep summary under 200 tokens."
```

**Bad summarizer prompts:**

```
"Summarize this."  ❌ Too vague
"Include everything."  ❌ Defeats purpose of summarization
```

## Evaluation Metrics

### Token Savings

```
savings = (original_tokens - summarized_tokens) / original_tokens * 100
```

### Information Retention

Use LLM-as-judge to evaluate:

1. **Fact preservation**: Are key facts from original present?
2. **Decision preservation**: Are decisions/commitments kept?
3. **Coherence**: Does conversation flow make sense?

### Cost Analysis

```
summarization_cost = summary_tokens * price_per_token
conversation_cost_savings = (original_tokens - summarized_tokens) * price_per_token
net_savings = conversation_cost_savings - summarization_cost
```

## Real-World Example

### Customer Support (25-turn conversation)

**Without summarization:**

- Total tokens: 6,000
- Cost per agent response: $0.012 (6000 tokens \* $0.002/1k)

**With summarization (keep_turns=5):**

- Summary: 300 tokens
- Recent turns: 1,200 tokens
- Total tokens: 1,500
- Cost per response: $0.003
- **Savings: 75%**

## Next Steps

1. **Start with `01_basic_summarization.py`** - See minimal implementation
2. **Explore `02_production_summarization.py`** - Production patterns
3. **Run `03_evaluate_summarization.py`** - Measure quality and savings

## Further Reading

- [OpenAI Cookbook: Summarization Strategies](https://cookbook.openai.com/)
- [Token Optimization Guide](https://platform.openai.com/docs/guides/optimization)
- [Agents SDK: SummarizingSession](https://github.com/openai/openai-agents-sdk)
