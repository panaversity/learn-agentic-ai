# Step 03: Multiple Cards 🌐

**Create an ecosystem of specialized agents using official A2A SDK - visual agent discovery**

> **Goal**: Run multiple specialized A2A agents simultaneously using official SDK and see how they advertise different capabilities.

## 🎯 What You'll Learn

- Agent specialization using official A2A SDK
- Multi-agent ecosystem patterns
- Comparative agent discovery
- Port management for multiple agents
- Visual ecosystem exploration
- Foundation for agent networks

## 📋 Prerequisites

- Completed [Step 02: Agent Skill](../02_agent_skill/)
- Understanding of AgentCard and AgentSkill types
- UV package manager installed
- Ability to run multiple terminals/processes

## 🚀 Implementation

We'll create 3 specialized agents using official A2A SDK, each focused on different capabilities:

### 1. Create UV Projects for Each Agent

```bash
# Create Math Agent
cd 03_multiple_cards
uv init math_agent_code
cd math_agent_code
uv add a2a-server

# Create Language Agent  
cd ../
uv init language_agent_code
cd language_agent_code
uv add a2a-server

# Create Utility Agent
cd ../
uv init utility_agent_code  
cd utility_agent_code
uv add a2a-server
```

### 2. Math Agent (Port 8002)

**File**: `math_agent_code/math_agent.py`

```python
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    AgentProvider,
)

class MathAgent:
    """Specialized agent for mathematical operations."""
    
    async def invoke(self, operation: str = "add") -> str:
        """Perform mathematical operations."""
        if operation == "add":
            return "I can add numbers: 5 + 3 = 8"
        elif operation == "statistics":
            return "I can calculate statistics: mean, median, mode"
        return "Math operations: addition, statistics, calculations"


class MathAgentExecutor(AgentExecutor):
    """Math specialist agent executor."""
    
    def __init__(self):
        self.agent = MathAgent()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute math operations."""
        result = await self.agent.invoke("add")
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel execution."""
        raise Exception('cancel not supported')


if __name__ == "__main__":
    # Define math-focused skills
    addition_skill = AgentSkill(
        id='add_numbers',
        name='Number Addition',
        description='Add two or more numbers together with detailed calculation',
        tags=['math', 'arithmetic', 'addition'],
        examples=['Add 5 and 3', 'Sum these numbers: 1,2,3,4'],
    )
    
    statistics_skill = AgentSkill(
        id='basic_statistics',
        name='Basic Statistics',
        description='Calculate mean, median, and other basic statistics for datasets',
        tags=['math', 'statistics', 'analysis'],
        examples=['Calculate mean of [1,2,3,4,5]', 'Find median of dataset'],
    )

    # Create math agent card
    math_agent_card = AgentCard(
        name='Math Specialist Agent',
        description='Specialized agent for mathematical operations and statistical analysis',
        url='http://localhost:8002/',
        version='1.0.0',
        provider=AgentProvider(
            organization='A2A Math Lab',
            url='http://localhost:8002/',
        ),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=False,
        ),
        skills=[addition_skill, statistics_skill],
    )

    # Create server
    request_handler = DefaultRequestHandler(
        agent_executor=MathAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=math_agent_card,
        http_handler=request_handler
    )

    print("🧮 Starting Math Specialist Agent on port 8002...")
    print(f"📊 Skills: {[skill.id for skill in math_agent_card.skills]}")
    uvicorn.run(server.build(), host="0.0.0.0", port=8002)
```

### 3. Language Agent (Port 8003)

**File**: `language_agent_code/language_agent.py`

```python
# Similar structure to Math Agent, but with language-focused skills
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, AgentProvider

class LanguageAgent:
    async def invoke(self) -> str:
        return "I can translate text and analyze language patterns!"

class LanguageAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = LanguageAgent()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception('cancel not supported')

if __name__ == "__main__":
    # Language-focused skills
    translation_skill = AgentSkill(
        id='translate_text',
        name='Text Translation',
        description='Translate text between different languages',
        tags=['language', 'translation', 'multilingual'],
        examples=['Translate "Hello" to Spanish', 'Convert English to French'],
    )
    
    analysis_skill = AgentSkill(
        id='analyze_text',
        name='Text Analysis',
        description='Analyze text for sentiment, language detection, and linguistic properties',
        tags=['language', 'analysis', 'nlp'],
        examples=['Analyze sentiment of text', 'Detect language of document'],
    )

    language_agent_card = AgentCard(
        name='Language Specialist Agent',
        description='Specialized agent for language processing, translation, and text analysis',
        url='http://localhost:8003/',
        version='1.0.0',
        provider=AgentProvider(organization='A2A Language Lab', url='http://localhost:8003/'),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[translation_skill, analysis_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LanguageAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(agent_card=language_agent_card, http_handler=request_handler)
    
    print("🗣️ Starting Language Specialist Agent on port 8003...")
    uvicorn.run(server.build(), host="0.0.0.0", port=8003)
```

### 4. Utility Agent (Port 8004)

**File**: `utility_agent_code/utility_agent.py`

```python
# Similar structure with utility-focused skills
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, AgentProvider
from datetime import datetime

class UtilityAgent:
    async def invoke(self) -> str:
        return f"Current time: {datetime.now().isoformat()}, I can help with utilities!"

class UtilityAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = UtilityAgent()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception('cancel not supported')

if __name__ == "__main__":
    # Utility-focused skills
    datetime_skill = AgentSkill(
        id='get_datetime_info',
        name='DateTime Information',
        description='Get current date/time information in various formats',
        tags=['utility', 'datetime', 'formatting'],
        examples=['Get current time', 'Format date as ISO'],
    )
    
    uuid_skill = AgentSkill(
        id='generate_uuid',
        name='UUID Generation',
        description='Generate unique identifiers in various formats',
        tags=['utility', 'uuid', 'generation'],
        examples=['Generate UUID', 'Create unique identifier'],
    )

    utility_agent_card = AgentCard(
        name='Utility Specialist Agent',
        description='Specialized agent for utility functions like datetime, UUIDs, and system operations',
        url='http://localhost:8004/',
        version='1.0.0',
        provider=AgentProvider(organization='A2A Utility Lab', url='http://localhost:8004/'),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[datetime_skill, uuid_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=UtilityAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(agent_card=utility_agent_card, http_handler=request_handler)
    
    print("🔧 Starting Utility Specialist Agent on port 8004...")
    uvicorn.run(server.build(), host="0.0.0.0", port=8004)
```



## 🧪 Testing

### 1. Start All Agents

Open 3 separate terminals and run:

```bash
# Terminal 1 - Math Agent
cd math_agent_code
python math_agent.py

# Terminal 2 - Language Agent  
cd language_agent_code
python language_agent.py

# Terminal 3 - Utility Agent
cd utility_agent_code
python utility_agent.py
```

### 2. Visual Agent Ecosystem Test

**Individual Agent Cards:**
1. Math Agent: http://localhost:8002/.well-known/agent.json
2. Language Agent: http://localhost:8003/.well-known/agent.json  
3. Utility Agent: http://localhost:8004/.well-known/agent.json

**Compare specializations** - Notice how each agent focuses on different capabilities using official A2A SDK!

### 3. Command Line Ecosystem Test

```bash
# Compare agent capabilities
curl http://localhost:8002/.well-known/agent.json | jq '.skills[].tags'
curl http://localhost:8003/.well-known/agent.json | jq '.skills[].tags'  
curl http://localhost:8004/.well-known/agent.json | jq '.skills[].tags'

# Compare skill counts
curl http://localhost:8002/.well-known/agent.json | jq '.skills | length'
curl http://localhost:8003/.well-known/agent.json | jq '.skills | length'
curl http://localhost:8004/.well-known/agent.json | jq '.skills | length'

# Test A2A messaging with each agent
curl -X POST http://localhost:8002/a2a \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "message/send", "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": "Hello Math Agent!"}], "messageId": "test-123"}}, "id": "req-456"}' | jq '.'
```

## 📊 Expected Output

When you visit each agent card, you should see distinct specializations:

**Math Agent** (http://localhost:8002/.well-known/agent.json):
```json
{
  "name": "Math Specialist Agent",
  "description": "Specialized agent for mathematical operations and statistical analysis",
  "provider": {"organization": "A2A Math Lab"},
  "skills": [
    {
      "id": "add_numbers",
      "name": "Number Addition",
      "tags": ["math", "arithmetic", "addition"]
    },
    {
      "id": "basic_statistics", 
      "name": "Basic Statistics",
      "tags": ["math", "statistics", "analysis"]
    }
  ]
}
```

**Language Agent** (http://localhost:8003/.well-known/agent.json):
```json
{
  "name": "Language Specialist Agent",
  "provider": {"organization": "A2A Language Lab"},
  "skills": [
    {
      "id": "translate_text",
      "tags": ["language", "translation", "multilingual"]
    },
    {
      "id": "analyze_text",
      "tags": ["language", "analysis", "nlp"]
    }
  ]
}
```

## 🔍 Key A2A Concepts

### Agent Specialization
- **Focused capabilities**: Each agent excels in specific domains
- **Clear boundaries**: Math, language, utilities - distinct responsibilities  
- **Efficient discovery**: Other agents know exactly what each agent offers
- **Composition potential**: Agents can work together on complex tasks

### Multi-Agent Ecosystems
- **Distributed capabilities**: No single agent needs to do everything
- **Service discovery**: Agents can find and use each other's services
- **Scalability**: Add new specialized agents without changing existing ones
- **Fault tolerance**: If one agent fails, others continue working

### Discovery Patterns
- **Standard endpoints**: All agents use `/.well-known/agent.json`
- **Automated discovery**: Discovery hubs can catalog available agents
- **Real-time status**: Check which agents are online/offline
- **Capability mapping**: Understand the full ecosystem's capabilities

### Why Multiple Agents Matter
- **Separation of concerns**: Each agent has a clear, focused purpose
- **Independent scaling**: Scale math-heavy vs language-heavy workloads separately
- **Independent deployment**: Update agents independently
- **Expertise modeling**: Different agents can embody different types of expertise

## ✅ Success Criteria

- ✅ All 3 UV projects created with a2a-server dependencies
- ✅ All 3 servers start without port conflicts using official A2A SDK
- ✅ Each specialized agent serves a unique agent card with proper AgentSkill types
- ✅ Each agent shows different specializations via tags and skill categories
- ✅ Browser testing reveals ecosystem structure using official A2A format
- ✅ Command line tests show agent diversity and A2A protocol compliance

## 🎯 Next Step

**Ready for Step 04?** → [04_agent_executor](../04_agent_executor/) - Implement the official Agent Executor pattern

---

## 💡 Key Insights

1. **Specialization enables expertise** - Focused agents are more effective than generalist agents
2. **Discovery enables composition** - Agents can find and use each other's capabilities
3. **Ecosystems are powerful** - Multiple agents can solve complex problems together
4. **Standards enable interoperability** - Consistent agent card format allows ecosystem growth
5. **Visual testing reveals patterns** - Browser testing makes ecosystem structure clear

## 🏗️ Ecosystem Design Patterns

1. **Domain specialization**: Agents focus on specific knowledge domains
2. **Function specialization**: Agents focus on specific types of operations
3. **Discovery hubs**: Central services that catalog available agents
4. **Service meshes**: Networks of interconnected specialized agents
5. **Capability advertising**: Agents clearly communicate what they can do

## 📖 Official Reference

This step demonstrates ecosystem concepts from: [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

**🎉 Congratulations! You've created your first A2A agent ecosystem with specialized, discoverable agents!** 