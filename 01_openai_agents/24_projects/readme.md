# OpenAI Agents SDK Projects

## Project 0: Building a Specialized Weather Assistant

https://www.datacamp.com/tutorial/openai-agents-sdk-tutorial

## Project 1: Email Automation Agent

https://aiablog.medium.com/complete-openai-agents-sdk-course-2025-a4dd68af0855

https://github.com/nnamu-cl/agents-sdk-course-2

## Project 2: Building a Research Assistant

https://www.datacamp.com/tutorial/openai-agents-sdk-tutorial

## Project 3: Automating Dispute Management with Agents SDK and Stripe API

https://cookbook.openai.com/examples/agents_sdk/dispute_agent


## Project 4: "Agento": A Modular AI Planning System

The "Agento" project showcases how the OpenAI Agents SDK can be used to turn broad goals into structured, actionable plans with iterative polish. Literally, you can start this sucker off with ANY goal or idea you can think of and it will go to work on it for you. Dive into the details and grab the starter code here, and improve this code:

https://github.com/dazzaji/agento6


# Projects to Submit

Below are some detailed project ideas for students to build AI agents using the OpenAI Agents SDK. These projects are designed to be educational, practical, and engaging, allowing students to explore the capabilities of AI agents while developing problem-solving and critical-thinking skills. Each project includes a description, objectives, and step-by-step directions for students to follow. We’ve avoided including code to encourage students to think through the implementation themselves, leveraging the OpenAI Agents SDK documentation and their creativity.

---

### Project 1: Personal Study Assistant
**Description:** Build an AI agent system that helps students manage their study schedules, find relevant resources, and summarize academic content. The system will consist of multiple agents working together: a scheduler, a web researcher, and a summarizer.

**Objectives:**
- Learn how to create and orchestrate multiple agents with distinct roles.
- Use the Responses API for web search and file processing.
- Implement handoffs between agents for seamless task delegation.

**Directions for Students:**
1. **Define the Agents:**
   - Create a "Scheduler Agent" to take user input (e.g., study topics and deadlines) and generate a study plan.
   - Create a "Research Agent" to search the web for articles, videos, or papers related to the study topics.
   - Create a "Summarizer Agent" to condense the research findings into concise notes.
2. **Set Up Inputs:**
   - Design a simple interface (e.g., command-line or text-based) where users can input their study goals and time constraints.
3. **Configure Tools:**
   - Use the built-in web search tool in the Responses API to enable the Research Agent to fetch real-time information.
   - Allow the Summarizer Agent to process text from web results or uploaded files (e.g., PDFs).
4. **Implement Handoffs:**
   - Ensure the Scheduler Agent passes the study topics to the Research Agent, which then hands off the collected data to the Summarizer Agent.
5. **Add Guardrails:**
   - Add checks to ensure the web search results are relevant (e.g., filter out non-academic sources) and the summaries are concise (e.g., limit word count).
6. **Test and Debug:**
   - Test the system with sample inputs like "Learn about machine learning by next week" and use the SDK’s tracing tools to monitor agent interactions.
7. **Enhance the Project:**
   - Add a feature to save the study plan and summaries to a file for later use.

---

### Project 2: AI-Powered Travel Planner
**Description:** Develop a multi-agent system that plans a trip based on user preferences (budget, destination, interests). Agents will handle destination research, itinerary planning, and budget tracking.

**Objectives:**
- Explore agent collaboration and task delegation.
- Integrate real-time web search and basic computation tools.
- Practice debugging and optimizing agent workflows.

**Directions for Students:**
1. **Define the Agents:**
   - Create a "Destination Agent" to research potential travel locations based on user interests (e.g., beaches, museums).
   - Create an "Itinerary Agent" to build a day-by-day plan using the researched destinations.
   - Create a "Budget Agent" to estimate costs and ensure the plan fits the user’s budget.
2. **Set Up Inputs:**
   - Allow users to input their preferences (e.g., "I want a 5-day trip to Europe under $2000, focused on history").
3. **Configure Tools:**
   - Use the web search tool to gather information on destinations, attractions, and travel costs.
   - Create a simple tool for the Budget Agent to calculate expenses (e.g., summing costs of flights, hotels, and activities).
4. **Implement Handoffs:**
   - Have the Destination Agent pass a shortlist of locations to the Itinerary Agent, which then collaborates with the Budget Agent to finalize the plan.
5. **Add Guardrails:**
   - Ensure the Destination Agent only selects safe, tourist-friendly locations and the Budget Agent flags plans exceeding the budget.
6. **Test and Debug:**
   - Test with different inputs (e.g., varying budgets or destinations) and use tracing to identify where agents might fail (e.g., incomplete itineraries).
7. **Enhance the Project:**
   - Add a feature to suggest alternative destinations if the budget is too low.

---

### Project 3: Customer Support Automation System
**Description:** Build an AI agent system to automate customer support for a fictional online store. The system will handle inquiries, process returns, and escalate complex issues to a human-like agent.

**Objectives:**
- Understand how to design agents for real-world applications.
- Use file search and external tool integration.
- Implement safety mechanisms to avoid inappropriate responses.

**Directions for Students:**
1. **Define the Agents:**
   - Create an "Inquiry Agent" to answer basic questions (e.g., shipping times, product availability).
   - Create a "Returns Agent" to guide users through the return process based on store policies.
   - Create an "Escalation Agent" to recognize complex queries and draft a response for a human to review.
2. **Set Up Inputs:**
   - Design a text-based input where users can ask questions like "How long does shipping take?" or "I want to return my order."
3. **Configure Tools:**
   - Use the file search tool to let the Inquiry Agent access a FAQ document or product catalog.
   - Allow the Returns Agent to retrieve a return policy file and process user requests.
4. **Implement Handoffs:**
   - Enable the Inquiry Agent to pass unresolved questions to the Escalation Agent, and the Returns Agent to confirm details with the Inquiry Agent if needed.
5. **Add Guardrails:**
   - Add checks to prevent the agents from giving incorrect information (e.g., validating against the FAQ) or escalating unnecessarily.
6. **Test and Debug:**
   - Test with common customer queries and edge cases (e.g., vague questions) and use tracing to ensure smooth handoffs.
7. **Enhance the Project:**
   - Add a feature to log interactions for future analysis or training.

---

### Project 4: News Digest Generator
**Description:** Create an AI agent system that compiles a daily news digest based on user-specified topics (e.g., technology, sports). Agents will search the web, filter content, and summarize articles.

**Objectives:**
- Leverage web search for real-time data.
- Practice multi-step reasoning and content filtering.
- Explore observability tools for performance tuning.

**Directions for Students:**
1. **Define the Agents:**
   - Create a "Search Agent" to find recent news articles based on user topics.
   - Create a "Filter Agent" to remove irrelevant or low-quality sources.
   - Create a "Digest Agent" to summarize the filtered articles into a short digest.
2. **Set Up Inputs:**
   - Allow users to input topics of interest (e.g., "Latest AI developments").
3. **Configure Tools:**
   - Use the web search tool to fetch articles and ensure citations are included.
   - Design a simple filtering mechanism (e.g., checking source credibility or recency).
4. **Implement Handoffs:**
   - Have the Search Agent pass articles to the Filter Agent, which then hands off the curated list to the Digest Agent.
5. **Add Guardrails:**
   - Ensure the Filter Agent excludes outdated or unreliable sources, and the Digest Agent keeps summaries brief.
6. **Test and Debug:**
   - Test with different topics and review the digest for accuracy and relevance, using tracing to spot inefficiencies.
7. **Enhance the Project:**
   - Add a feature to email the digest or format it as a PDF.

---

### Project 5: Code Review Assistant
**Description:** Develop an AI agent system to assist with code reviews by analyzing code files, suggesting improvements, and generating documentation. This is ideal for students with some programming experience.

**Objectives:**
- Integrate file processing and external tool use.
- Learn to handle multi-step tasks with agents.
- Explore debugging complex workflows.

**Directions for Students:**
1. **Define the Agents:**
   - Create a "Analyzer Agent" to read code files and identify potential issues (e.g., syntax, style).
   - Create a "Suggestion Agent" to propose fixes or optimizations.
   - Create a "Documentation Agent" to generate comments or a README based on the code.
2. **Set Up Inputs:**
   - Allow users to upload a code file (e.g., Python script) or input a GitHub repository link.
3. **Configure Tools:**
   - Use the file search tool to process uploaded code files.
   - Optionally integrate a web search to find best practices or documentation templates.
4. **Implement Handoffs:**
   - Have the Analyzer Agent pass identified issues to the Suggestion Agent, which then collaborates with the Documentation Agent for final output.
5. **Add Guardrails:**
   - Ensure the Analyzer Agent only flags relevant issues and the Suggestion Agent avoids impractical fixes.
6. **Test and Debug:**
   - Test with sample code (e.g., a buggy script) and use tracing to ensure all agents contribute effectively.
7. **Enhance the Project:**
   - Add a feature to support multiple programming languages or integrate with a GitHub API for pull request comments.

---

### General Tips for Students
- **Start Simple:** Begin with one agent and a single task, then scale up to multi-agent systems.
- **Read the Docs:** Refer to the OpenAI Agents SDK documentation (available online) for setup instructions and tool details.
- **Experiment:** Try different configurations (e.g., agent instructions, tool combinations) to see what works best.
- **Collaborate:** Work in teams to brainstorm agent roles and test each other’s systems.
- **Showcase:** Present your project with a demo and explain how the agents collaborate to solve the problem.


