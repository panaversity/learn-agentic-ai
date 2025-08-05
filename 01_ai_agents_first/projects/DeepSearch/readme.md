### **Assignment Guide — Build a Web Search Agent with OpenAI Agents SDK**

> **Goal:** Create a Web Search Agent that takes a user’s query, calls a search-API, and returns **personalized**, concise answers.
> You’ll leverage the **first 10 folders (01 → 10)** from our GitHub track.

---

## 1 ↠ 01\_uv – *Project setup*

| Why it matters                                                          | What you must do                                                                                            |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `uv` lets you install & run dependencies fast without global pollution. | • Clone the repo<br>• Verify you can run a “Hello, Agent” script. |

---

## 2 ↠ 02\_what\_is\_api – *Talking to the outside world*

| Why                                                                  | Task                                                                                                                      |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| A web-search agent is basically an **API client** wrapped in an LLM. | Pick a search API (Bing, Google CustomSearch, DuckDuckGo, etc.). Read its docs, note required query params & auth header. | You can use tavily for web-search

---

## 3 ↠ 03\_get\_api\_key – *Security 101*

| Why                                                               | Task                                                                                     |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Never hard-code keys. You’ll break security and rate-limit rules. | • Create `.env` with `SEARCH_API_KEY=...`<br>• Load it via `os.getenv` inside your tool. |

---

## 4 ↠ 04\_hello\_agent – *Your first runnable agent*

| Why                                                                   | Task                                                                                                                  |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Gives you a minimal skeleton: model + Agent + run cycle. | Copy `hello_agent.py` → `web_search_agent.py`. Replace greeting logic with a placeholder “search API called” message or with proper system prompt. |

---

## 5 ↠ 05\_model\_configuration – *Tuning the brain*

| Why                                                                  | Task                                                                                              |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Temperature, max-tokens, model choice dictate response style & cost. | • Set `temperature=xxx` (experiment with temp and select your desire temperature).<br>• Limit `max_tokens` so summaries stay crisp. |

---

## 6 ↠ 06\_basic\_tools – *Giving the agent ToolBox*

| Why                                               | Task                                                                                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Tools let the LLM reach beyond its training data. | Implement a `search_web` tool that:<br>1. Accepts `{query:str}`<br>2. Calls chosen API<br>3. Returns top N results (title + URL + snippet). |

---

## 7 ↠ 07\_model\_settings – *Refining behaviour*

| Why                                                              | Task                                                                                                  |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| You can pin the model to summarise, cite, or reason differently. | Add an instruction like: “When responding, give a **three-sentence answer** with bullet-point links.” |

---

## 8 ↠ 08\_local\_context – *Personalisation layer*  **⬅ NEW FOCUS**

| Why                                                                                                                                                                          | Task                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local context** lets the agent remember rich user-specific data between turns. We’ll use it to **fetch user-profile info** and tailor answers. | • During the first user turn, store a `user_profile` object in `context` (you can fake it or read from a mock DB).<br>• Each subsequent turn, prepend dynamic instructions such as:<br>  “You’re helping **{name}** from **{city}** who likes **{topic}.** Personalise examples accordingly.” |

---

## 9 ↠ 09\_dynamic\_instructions – *Adapting on the fly*

| Why                                                                                                  | Task                                                                                                                     |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Users say “search deeper” or “give me just links.” | • Detect keywords like “deeper” / “summarise” or understand user query what user asked for.<br>• Mutate instructions (e.g., increase result count or shorten answer). |

---

## 10 ↠ 10\_streaming – *Real-time UX bonus*

| Why                                                        | Task                                                                                                           |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Streaming partial replies feels faster and shows progress. | Use the SDK’s streaming wrapper so results trickle to the console as soon as they arrive. |

---

### **Deliverables**

| Item                     | Details                                                           |
| ------------------------ | ----------------------------------------------------------------- |
| `web_search_agent.py`    | Complete, well-commented agent code                               |
| `README.md`              | • Setup steps<br>• How personalisation works<br>• How to run demo |
| **Demo (optional +10%)** | Short screen-capture or gif of agent in action                    |

---

### **Marking Rubric (100 pts)**

| Criterion                           | Pts |
| ----------------------------------- | --- |
| Dependency & environment setup (uv) | 5   |
| Secure API-key handling             | 10  |
| Search tool implementation          | 20  |
| Model configuration (05 + 07)       | 10  |
| **Local context personalisation**   | 20  |
| Dynamic instructions                | 15  |
| Streaming output                    | 10  |
| Code quality & README               | 10  |

---

### **Hints**

1. **Mock user data**: If you don’t have a real user DB, create a simple `user_profile = {"name":"Ali","city":"Lahore","topic":"AI"}` and store it on first run.
2. **Rate-limits**(Optional): Search APIs often cap requests—cache results in local context to avoid repeat calls.
3. **Testing** (Optional): Write a few unit tests for the tool function to ensure it gracefully handles empty results or API errors.

---

**Challenge yourself, have fun, and remember — a personalised answer is always more valuable than a generic one. Good luck building your Web Search Agent!**
