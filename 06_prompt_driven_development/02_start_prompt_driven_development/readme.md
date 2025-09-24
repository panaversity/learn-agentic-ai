# Starting Prompt Driven Development (PDD)
This guide helps you choose and try AI coding tools based on your budget while maintaining the same Prompt-Driven Development (PDD) methodology across all tiers.

Choose the option that fits your budget; the disciplined loop remains the same: Spec → Plan → Prompt → Test/Evaluate → Refactor → Record → Review.

1. **$0/mo — Qwen Code (CLI) + Gemini CLI**: Start free with two terminal tools. Qwen Code offers strong repo exploration, git automation, and optional vision. Gemini CLI provides large‑context prompting, great for long prompts and scripts.
2. **$20/mo — Cursor Pro**: An AI‑native IDE with Agent Mode, multi‑file awareness, parallel agents, and fast tab completion.
3. **$40+/mo — GPT‑5 Codex + Cursor Pro**: Two Autonoumous AI Agents in Cursor AI Native IDE for parallel, repo‑wide work.
4. **Add‑On (Any budget) — Keep Gemini CLI + Qwen Code alongside anything above**: The free tier of both tools can be used in combination with Cursor Pro or GPT‑5 Codex for extra flexibility at no additional cost.
> Start free, then upgrade as your needs grow.

![Budget-based picks](./image.png)

## Tool Comparison

Below is a comparison of the four PDD tool options, tailored to different budgets, with consistent formatting and focus on their features, strengths, and use cases.


| Aspect              | Qwen Code (CLI) | Gemini CLI | Cursor Pro (AI-First IDE) | GPT-5 Codex (Cloud Agent) |
|---------------------|-----------------|------------|---------------------------|---------------------------|
| **Core Design**     | Terminal-based coding agent with strong repo analysis and optional vision support for multimodal prompts. | Terminal-native assistant with large context windows, ideal for long prompts and scripts. | AI-native IDE (VS Code fork) with seamless UI for inline edits, autocomplete, and multi-file awareness. | Cloud-based agent for agentic coding, focusing on parallel task execution and repo-wide automation. |
| **User Interaction**| CLI prompts for quick tasks, codebase queries, and git automation; runs locally with OAuth/API. | CLI prompts with simple Google auth; optimized for scripting and long, single-flow sessions. | Interactive, local IDE with inline suggestions, previews, and chat integrated with files/projects. | Conversational and autonomous; describe tasks via ChatGPT or CLI, executes with minimal supervision. |
| **Strengths**       | Free with 2K req/day, excels in codebase exploration, vision support, and git utilities. | Free, large context windows, fast setup, ideal for scripting and educational workflows. | Fast daily coding, multi-file edits, Agent Mode, parallel agents, and exclusive tab completion. | Handles complex, parallel, repo-wide tasks; generates PRs with tests/docs; strong automation. |
| **Use Cases**       | Learning, repo audits, architecture reviews, quick refactors via CLI. | Long prompts, scripting, terminal-based workflows, educational tasks. | Individual/team coding, prototyping, iterative development with rapid tab completion. | Large-scale automation, building from scratch, cross-repo tasks with minimal hands-on work. |
| **Pricing**         | Free ($0/mo). | Free ($0/mo). | Pro plan (~$20/mo), limited free tier. | Plus/Enterprise or API (~$40+/mo). |
| **Limitations**     | CLI-only UX; complex edits need editor integration; quotas apply. | CLI-only; fewer repo-wide automation features than Codex/Cursor. | Review needed for refactors; fewer autonomous long-running tasks than Codex. | Slower for simple edits; cloud latency; less interactive in-editor without extensions. |

## Getting Started
1. **Free Tier ($0/mo)**: Use **Qwen Code CLI** for codebase exploration and git automation, paired with **Gemini CLI** for long-context scripting. Ideal for beginners or lightweight projects.
2. **Pro Tier ($20/mo)**: Upgrade to **Cursor Pro** for an AI-native IDE with fast tab completion, Agent Mode, and multi-file editing, perfect for solo developers or small teams.
3. **Premium Tier ($40+/mo)**: Combine **GPT-5 Codex** with **Cursor Pro** for autonomous, repo-wide automation and PR generation, suited for complex projects or teams needing scalability.
4. Start with the free tier and upgrade as your workflow evolves, keeping the PDD method consistent.


## Latest SWE-bench Verified

* **Qwen Code** (Qwen3-Coder): **69.6%** on SWE-bench Verified in a 500-turn setting (repo tools + OpenHands harness). Some summaries also list **\~67%** under “standard” settings; scores vary with the agent/harness.
* **Gemini CLI** (uses **Gemini 2.5 Pro**): **63.8%** on SWE-bench Verified with Google’s custom agent setup.
* **Cursor Pro**: **N/A** — Cursor is an IDE; SWE-bench is reported for models/agents, not editors. Its performance depends on the model you run inside. (No official SWE-bench score for Cursor itself.)
* **GPT-5 Codex**: **\~74.9%** on SWE-bench Verified per OpenAI’s GPT-5 launch page; tech trade coverage reports **\~74.5%** for the Codex variant.
                                                          
## Practical performance (what you’ll feel day-to-day)

* **GPT-5 Codex** – shows the best *agentic coding* results on public leaderboards; Best at large, multi-file changes and autonomous bug-fix PRs; strongest *SWE-bench Verified* **74.5%**, showing among public numbers right now. Expect better planning + code review abilities.

* **Gemini CLI (2.5 Pro)** – Very capable agentic runs with generous free limits; excels in terminal-centric workflows, huge context, and easy pairing with Google’s Code Assist/MCP. **SWE-bench Verified** \~**63.8%** 

* **Qwen Code (Qwen2.5-Coder)** – Excellent free/open models for local/offline and repo-friendly code gen & repair; top open-source results on classic code benchmarks; for agentic repo-wide tasks you’ll likely pair it with a framework and careful tooling.
* **Cursor Pro** – Big productivity win (indexing, apply-diffs, background agents). Quality maps to the model you choose (GPT-5 Codex, Gemini, Claude, etc.). Pricing is transparent and reasonable for daily use.

---

Note for Gemini CLI: 

**Gemini CLI does have a VS Code plugin.** It’s the official **“Gemini CLI Companion”** extension that pairs directly with the Gemini CLI:

https://marketplace.visualstudio.com/items?itemName=Google.gemini-cli-vscode-ide-companion

You can also set it up:

**From VS Code (Marketplace)**

* Open VS Code → Extensions → search **“Gemini CLI Companion”** → Install. 

* The extension is meant to work *with* the CLI (you’ll run prompts in the integrated terminal; the companion adds editor-aware goodies like diffing and context):

https://developers.googleblog.com/en/gemini-cli-vs-code-native-diffing-context-aware-workflows/

* If you’re using **Gemini Code Assist** in VS Code, that’s a separate (but related) extension for completions/transformations—and Cloud Code will even install it for you. It’s not the same as the CLI companion, but many folks use both:

https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist

