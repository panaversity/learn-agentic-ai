# MCP Servers to 10x Productivity
Model Context Protocol (MCP) servers plug powerful tools into your favorite coding agent. Add a few, and the agent can browse the web, control Playwright, talk to GitHub, recall team memory, and search deep documentation—all without leaving the chat.

This guide keeps things simple and practical. Use with the coding agent you prefer.

---

## Recommended Starter Servers

### Playwright MCP – Headless Browser & UI Tests
- **Why use it:** Script user journeys, capture screenshots, and verify pages after changes.
- **How to add:**
  ```json
  {
    "mcpServers": {
      "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
      }
    }
  }
  ```

- **Try this prompt:**
  > now setup a simple page that shows galaxy. Take the screenshot to ensure it's all perfect and review it. Continue iterating after reviewing to get perfect galaxy view.

### Tavily Browser Search – Web Search + Fetch
- **Why use it:** Rapid research, compare docs, gather references.
- **How to add:**
  ```json
  {
    "mcpServers": {
      "tavily-remote": {
        "command": "npx",
        "args": [
          "-y",
          "mcp-remote",
          "https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>"
        ]
      }
    }
  }
  ```
  Export `TAVILY_API_KEY` in your shell first. Reload the agent, then verify with `qwen mcp list` and `/mcp`.
- **Try this prompt:**
  > Check and research if gemini 3.0 and sonnet 4.5 are released.

### Context7 MCP – Up-to-Date Code Docs
- **Why use it:** Summaries with citations for frameworks, APIs, and changelogs.
- **How to add:**
  ```json
  {
    "mcpServers": {
      "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"]
      }
    }
  }
  ```
  Add your Context7 key as an env var. Confirm with `qwen mcp list` and `/mcp`.

### OpenMemory – Keep Team Facts Handy
- **Why use it:** Persist decisions, preferences, and reminders across sessions.
- **How to add:**
  ```json
    "openmemory": {
      "command": "npx",
      "args": ["-y", "openmemory"],
      "env": {
        "OPENMEMORY_API_KEY": "YOUR_API_KEY"
      }
    }
  ```
- **Try this prompt:**
  > Use add-memory tool and save that we prefer to use OpenAI Agents SDK, MCP, A2A, Kubernetes for Agentic AI.

---

## How to Choose Servers (Think Like a Technical Business Manager)

1. **Outcome first:** What workflow does this unblock? Example: “Verify login flow daily” or “Gather competitive notes in 5 minutes.”
2. **ROI quick check:** Setup under 15 minutes, saves 30+ minutes per week, reduces context switching.
3. **Security posture:** Use env vars for auth, avoid broad shell access, whitelist commands, no tokens in repositories.
4. **Maintenance:** Look for active repos, clean docs, simple install/uninstall commands, minimal dependencies.
5. **Integration fit:** Choose servers that complement your stack (browser automation, search, memory) without overlapping.
6. **Proof of value:** Run a 1-day pilot with a measurable goal (e.g., catch a flaky login, pull three curated sources with quotes, auto-generate a meeting brief).

---

With a handful of MCP servers, your coding agent turns into a full teammate: it can research, test, remember, and reason over code faster than a solo workflow. Build your stack gradually, and keep verifying each addition with the steps above.
