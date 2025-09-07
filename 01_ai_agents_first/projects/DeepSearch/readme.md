# 🧠 Deep Research Multi-Agent System

A multi-agent research assistant powered by **LLMs (Gemini)** using the **OpenAI SDK**.  
This system takes a user’s query, clarifies it, plans research tasks, performs web searches, synthesizes results, validates sources, and generates a polished **professional research report with APA-style citations**.

---

## 📂 Project Structure

```
├── core.py                # Central configuration & shared context (merged config + shared)
├── deep_research_agent.py # Entry point (user interaction + pipeline execution)
├── planning_agent.py      # Breaks clarified query into specific research tasks
├── research_agents.py     # Web search, reflection, citations, source checking, orchestrator
├── synthesis_agent.py     # Synthesizes findings into a structured draft
├── report_writer.py       # Finalizes professional report and saves to file
├── reports/               # Auto-generated research reports
├── pyproject.toml         # Dependencies and project metadata
└── .env                   # API keys (OPENAI_API_KEY, GEMINI_API_KEY)
```

---

## ⚙️ Setup

### 1. Configure Environment

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_key_here   # optional, for tracing
GEMINI_API_KEY=your_gemini_key_here
```

### 2. Install Dependencies

Dependencies are defined in `pyproject.toml`. Install with:

```bash
uv sync
```

### 3. Run the System

```bash
uv run deep_research_agent.py
```

---

## 🔄 Workflow

1. **Requirement Gathering Agent**  
   Clarifies the user’s query (scope, depth).

2. **Planning Agent**  
   Breaks query into 2–3 specific research sub-tasks.

3. **Orchestrator Agent**  
   Coordinates the research process:
   - Web Search Agent → Reflective Agent → Synthesis Agent  
   - Citations Agent → Source Checker Agent → Report Writer Agent

4. **Report Writer Agent**  
   Produces a **final professional report** with inline citations and a validated APA-style reference list.  
   Saves the report in the `reports/` folder with a timestamped filename.

---

## 📄 Example Output

```
[Turn 1: Requirement Gathering Agent]
What is the impact of AI on higher education in the next 5 years?

Final Report:
---------------------------------
Title Page
Research Report: The Impact of AI on Higher Education
Date: 2025-09-07
Author: User (L'Aquila)

Executive Summary
...

Main Body
...

References
[1] Smith, J. (2023). *AI in Education*. Academic Press. https://example.com
...
```

Saved as:
```
reports/research_report_20250907_153210.txt
```

---

## 🧩 Agents Overview

- **Requirement Gathering Agent** → clarifies the initial query.  
- **Planning Agent** → breaks query into research tasks.  
- **Web Search Agent** → executes searches and stores results.  
- **Reflective Agent** → reviews results, identifies themes.  
- **Synthesis Agent** → creates a cohesive draft with inline citations.  
- **Citations Agent** → inserts citation markers `[1], [2]`.  
- **Source Checker Agent** → validates sources and formats APA references.  
- **Report Writer Agent** → compiles everything into the final professional report.  

---

## 📌 Notes

- The pipeline is **asynchronous** (`asyncio`) for efficiency.  
- All agents share state through `LocalContext`.  
- Reports are **timestamped** and saved in `reports/`.  
- Easily extendable with new agents (e.g., visualization, fact-checking, domain-specific research).  

---

## 🔮 Future Improvements

- Export final report as **Word (.docx)** or **PDF** automatically.  
- Add a **fact-checking agent** using retrieval-augmented generation.  
- Support **custom report templates** (academic, business, policy briefs).  

---

## 📜 License

MIT License © 2025 Muhammad Ahmed

