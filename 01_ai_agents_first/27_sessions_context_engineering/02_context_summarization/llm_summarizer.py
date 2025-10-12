import asyncio
from typing import List, Tuple
from agents import Runner, TResponseInputItem, RunConfig, ModelSettings

from llm_config import base_agent

SUMMARY_PROMPT = """
You are a senior customer-support assistant for tech devices, setup, and software issues.
Compress the earlier conversation into a precise, reusable snapshot for future turns.

Before you write (do this silently):
- Contradiction check: compare user claims with system instructions and tool definitions/logs; note any conflicts or reversals.
- Temporal ordering: sort key events by time; the most recent update wins. If timestamps exist, keep them.
- Hallucination control: if any fact is uncertain/not stated, mark it as UNVERIFIED rather than guessing.

Write a structured, factual summary ≤ 200 words using the sections below (use the exact headings):

• Product & Environment:
  - Device/model, OS/app versions, network/context if mentioned.

• Reported Issue:
  - Single-sentence problem statement (latest state).

• Steps Tried & Results:
  - Chronological bullets (include tool calls + outcomes, errors, codes).

• Identifiers:
  - Ticket #, device serial/model, account/email (only if provided).

• Timeline Milestones:
  - Key events with timestamps or relative order (e.g., 10:32 install → 10:41 error).

• Tool Performance Insights:
  - What tool calls worked/failed and why (if evident).

• Current Status & Blockers:
  - What’s resolved vs pending; explicit blockers preventing progress.

• Next Recommended Step:
  - One concrete action (or two alternatives) aligned with policies/tools.

Rules:
- Be concise, no fluff; use short bullets, verbs first.
- Do not invent new facts; quote error strings/codes exactly when available.
- If previous info was superseded, note “Superseded:” and omit details unless critical.
"""

class LLMSummarizer:
    def __init__(self, client = base_agent, model="gemini-2.5-flash-lite", max_tokens=400, tool_trim_limit=600):
        self.client = base_agent.clone(instructions=SUMMARY_PROMPT)
        self.model = model
        self.max_tokens = max_tokens
        self.tool_trim_limit = tool_trim_limit

    async def summarize(self, messages: List[TResponseInputItem]) -> Tuple[str, str]:
        """
        Create a compact summary from `messages`.

        Returns:
            Tuple[str, str]: The shadow user line to keep dialog natural,
            and the model-generated summary text.
        """
        user_shadow = "Summarize the conversation we had so far."
        TOOL_ROLES = {"tool", "tool_result"}

        def to_snippet(m: TResponseInputItem) -> str | None:
            role = (m.get("role") or "assistant").lower()
            content = (m.get("content") or "").strip()
            if not content:
                return None
            # Trim verbose tool outputs to keep prompt compact    
            if role in TOOL_ROLES and len(content) > self.tool_trim_limit:
                content = content[: self.tool_trim_limit] + " …"
            return f"{role.upper()}: {content}"

        # Build compact, trimmed history
        history_snippets = [s for m in messages if (s := to_snippet(m))]

        # Build the user message with conversation history
        user_message = "\n".join(history_snippets)

        # Use Runner.run with the agent (which has instructions set)
        resp = await Runner.run(
            self.client,
            user_message,  # Just pass the string, agent already has instructions
            run_config=RunConfig(
                model_settings=ModelSettings(
                    max_output_tokens=self.max_tokens
                )
            )
        )

        summary = resp.final_output
        await asyncio.sleep(0)  # yield control
        return user_shadow, summary
