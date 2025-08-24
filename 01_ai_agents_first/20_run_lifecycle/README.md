# Run Lifecycle Hooks - Complete Beginner's Guide

## What are Run Lifecycle Hooks? 🎯

Think of **Run Lifecycle Hooks** like a **security system for your entire building** (not just one room). While Agent hooks watch a single agent, Run hooks watch the **entire execution** - all agents working together.

### 🏢 Office Building Analogy
Imagine you have a **multi-story office building** with different departments (agents) on each floor:

- **Run Hooks** = **Building-wide security system** 📹🏢
- **Agent Hooks** = **Department-specific cameras** 📹🚪

Run hooks see **everything** that happens across all floors/agents, while agent hooks only see what happens in their specific department.

## RunHooksBase Class

This is your "master control room" that monitors the **entire agent execution run**. You can watch as different agents take turns, use tools, and hand off work to each other.

### Available Hooks (Global Event Listeners)

#### 1. `on_agent_start` - Any Agent Becomes Active 🌅
```python
async def on_agent_start(context, agent):
    print(f"🌅 SYSTEM: Agent {agent.name} is now active")
```

**🏢 Building Security Analogy**: Like the building-wide announcement system announcing when anyone clocks in for work.

**When this happens:**
- ANY agent in your system becomes the active/responsible agent
- This could be the first agent starting, or another agent taking over
- The system is tracking which agent is currently "in charge"
- This fires for EVERY agent that becomes active during the run

**Real Example:**
```
User starts conversation: "I need help with my order"
🌅 on_agent_start: CustomerService is now active
```

#### 2. `on_agent_end` - Any Agent Finishes ✅
```python
async def on_agent_end(context, agent, output):
    print(f"✅ SYSTEM: Agent {agent.name} completed work with output: {output}")
```

**🏢 Building Security Analogy**: Like the building-wide system logging when anyone completes their work and clocks out.

**When this happens:**
- ANY agent in your system finishes their work completely
- The agent has produced final output for their part of the task
- The agent is about to become inactive
- This tracks completion across all agents in the system

**Real Example:**
```
✅ on_agent_end: CustomerService completed with "I've escalated your issue to Technical Support"
```

#### 3. `on_llm_start` - Any Agent Asks AI Brain 📞
```python
async def on_llm_start(context, agent, system_prompt, input_items):
    print(f"📞 SYSTEM: {agent.name} is asking AI for help")
```

**🏢 Building Security Analogy**: Like monitoring when anyone in the building calls the expert consultation hotline.

**When this happens:**
- ANY agent in the system needs to "think" using the LLM
- This captures ALL LLM calls from ALL agents
- Helps track total "thinking" activity across the entire system
- Can happen multiple times per agent, multiple agents per run

**Real Example:**
```
📞 on_llm_start: CustomerService asking AI "How should I respond to this order inquiry?"
📞 on_llm_start: TechnicalSupport asking AI "How should I handle this technical issue?"
```

#### 4. `on_llm_end` - Any Agent Gets AI Response 🧠✨
```python
async def on_llm_end(context, agent, response):
    print(f"🧠✨ SYSTEM: {agent.name} got AI response")
```

**🏢 Building Security Analogy**: Like logging when anyone finishes their call with the expert consultation hotline.

**When this happens:**
- ANY agent receives a response from the LLM
- The AI has finished "thinking" for that specific request
- Always follows an `on_llm_start` from the same agent
- Tracks all AI thinking completion across the system

**Real Example:**
```
🧠✨ on_llm_end: CustomerService got AI guidance on handling the order
🧠✨ on_llm_end: TechnicalSupport got AI guidance on the technical solution
```

#### 5. `on_tool_start` - Any Agent Uses Any Tool 🔨
```python
async def on_tool_start(context, agent, tool):
    print(f"🔨 SYSTEM: {agent.name} using {tool.name}")
```

**🏢 Building Security Analogy**: Like a building-wide tool checkout system that logs whenever anyone uses any equipment.

**When this happens:**
- ANY agent in the system starts using a tool/function
- This tracks ALL tool usage across ALL agents
- Helps monitor what external actions are being taken system-wide
- Tools might be: database_lookup, send_email, web_search, calculator

**Real Example:**
```
🔨 on_tool_start: CustomerService using "order_lookup" tool
🔨 on_tool_start: TechnicalSupport using "diagnostic_check" tool
```

#### 6. `on_tool_end` - Any Agent Finishes Using Any Tool ✅🔨
```python
async def on_tool_end(context, agent, tool, result):
    print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
```

**🏢 Building Security Analogy**: Like the building system logging when anyone returns equipment to the checkout.

**When this happens:**
- ANY agent completes using a tool and gets the result
- Always follows an `on_tool_start` from the same agent
- The system can see what results tools are providing
- Tracks completion of all external actions system-wide

**Real Example:**
```
✅🔨 on_tool_end: CustomerService finished "order_lookup" - found order #12345
✅🔨 on_tool_end: TechnicalSupport finished "diagnostic_check" - issue identified
```

#### 7. `on_handoff` - Work Passes Between Any Agents 🏃‍♂️➡️🏃‍♀️
```python
async def on_handoff(context, from_agent, to_agent):
    print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF: {from_agent.name} → {to_agent.name}")
```

**🏢 Building Security Analogy**: Like the building's workflow system tracking when work gets transferred between departments.

**When this happens:**
- ANY agent decides another agent should handle the task
- Work is being transferred from one agent to another
- This tracks the "relay race" of work between agents
- Shows the collaboration flow in your multi-agent system

**Real Example:**
```
🏃‍♂️➡️🏃‍♀️ HANDOFF: CustomerService → TechnicalSupport
(Customer issue was too technical for general support)
```

## Complete Multi-Agent Flow Example 🔄

Here's what a complex conversation looks like with ALL run hooks:

```
User: "My premium account isn't working and I need a refund"

🌅 on_agent_start: CustomerService becomes active
📞 on_llm_start: CustomerService asks AI how to handle account issues
🧠✨ on_llm_end: AI suggests checking account status first
🔨 on_tool_start: CustomerService uses "account_lookup" tool
✅🔨 on_tool_end: Found premium account with technical issues
📞 on_llm_start: CustomerService asks AI about escalation
🧠✨ on_llm_end: AI suggests escalating to TechnicalSupport
🏃‍♂️➡️🏃‍♀️ on_handoff: CustomerService → TechnicalSupport
✅ on_agent_end: CustomerService finished with "Escalating to tech support"

🌅 on_agent_start: TechnicalSupport becomes active  
📞 on_llm_start: TechnicalSupport asks AI about account issues
🧠✨ on_llm_end: AI suggests running diagnostics
🔨 on_tool_start: TechnicalSupport uses "system_diagnostic" tool
✅🔨 on_tool_end: Found server issue affecting premium features
📞 on_llm_start: TechnicalSupport asks AI about refunds
🧠✨ on_llm_end: AI suggests escalating to BillingManager
🏃‍♂️➡️🏃‍♀️ on_handoff: TechnicalSupport → BillingManager
✅ on_agent_end: TechnicalSupport finished with "Issue confirmed, escalating"

🌅 on_agent_start: BillingManager becomes active
📞 on_llm_start: BillingManager asks AI about refund process
🧠✨ on_llm_end: AI provides refund procedure
🔨 on_tool_start: BillingManager uses "process_refund" tool
✅🔨 on_tool_end: Refund processed successfully
✅ on_agent_end: BillingManager finished with "Refund processed"
```

## Understanding Run vs Agent Hooks 🤔

This is crucial for beginners to understand:

**🏢 Run Hooks - Building Security System**
- Monitors **ALL agents** in the system
- Sees **everything** that happens during execution
- Tracks the **big picture** of how agents collaborate
- Set up once for the entire run: `run_hooks=YourHooksClass()`

**🏠 Agent Hooks - Individual Room Cameras**  
- Monitors **ONE specific agent** only
- Sees only what **that agent** does
- Tracks **individual agent** behavior
- Set up per agent: `agent.hooks = YourHooksClass()`

**Visual Comparison:**
```
Run Hooks See:                    Agent Hooks See:
                          
🏢 Building Level                 🏠 Room Level
├─ CustomerService activity       ├─ Only CustomerService
├─ TechnicalSupport activity      OR
├─ BillingManager activity        ├─ Only TechnicalSupport  
└─ All handoffs between them      OR
                                 └─ Only BillingManager
```

## Simple Example

```python
from openai_agents import Agent, RunHooksBase
from openai_agents.orchestration import run

# Create a system-wide monitoring class
class SystemMonitor(RunHooksBase):
    def __init__(self):
        self.active_agents = []
        self.tool_usage = {}
        self.handoffs = 0
    
    async def on_agent_start(self, context, agent):
        self.active_agents.append(agent.name)
        print(f"🌅 SYSTEM: {agent.name} is now working")
        print(f"   Active agents so far: {self.active_agents}")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print(f"📞 SYSTEM: {agent.name} is thinking...")
    
    async def on_llm_end(self, context, agent, response):
        print(f"🧠✨ SYSTEM: {agent.name} finished thinking")
    
    async def on_tool_start(self, context, agent, tool):
        tool_name = tool.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        print(f"🔨 SYSTEM: {tool_name} used {self.tool_usage[tool_name]} times")
    
    async def on_tool_end(self, context, agent, tool, result):
        print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
    
    async def on_handoff(self, context, from_agent, to_agent):
        self.handoffs += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.handoffs}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context, agent, output):
        print(f"✅ SYSTEM: {agent.name} completed their work")
        print(f"📊 STATS: {len(self.active_agents)} agents used, {self.handoffs} handoffs")

# Create your agents
customer_service = Agent(name="CustomerService")
tech_support = Agent(name="TechnicalSupport")
billing_manager = Agent(name="BillingManager")

# Create the system monitor
system_monitor = SystemMonitor()

# Run with system-wide monitoring
result = await run(
    agents=customer_service,
    input="I need help with my account",
    run_hooks=system_monitor,  # This monitors EVERYTHING
)
```

## Advanced Example - Multi-Agent Analytics

```python
import time
from datetime import datetime

class MultiAgentAnalytics(RunHooksBase):
    def __init__(self):
        self.start_time = None
        self.agent_stats = {}
        self.system_stats = {
            'total_llm_calls': 0,
            'total_tool_calls': 0,
            'total_handoffs': 0
        }
    
    def _init_agent_stats(self, agent_name):
        if agent_name not in self.agent_stats:
            self.agent_stats[agent_name] = {
                'start_time': None,
                'total_time': 0,
                'llm_calls': 0,
                'tool_calls': 0
            }
    
    async def on_agent_start(self, context, agent):
        if self.start_time is None:
            self.start_time = time.time()
        
        self._init_agent_stats(agent.name)
        self.agent_stats[agent.name]['start_time'] = time.time()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"🌅 [{timestamp}] SYSTEM: {agent.name} started working")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self._init_agent_stats(agent.name)
        self.agent_stats[agent.name]['llm_calls'] += 1
        self.system_stats['total_llm_calls'] += 1
        
        print(f"📞 SYSTEM: {agent.name} LLM call #{self.agent_stats[agent.name]['llm_calls']}")
    
    async def on_llm_end(self, context, agent, response):
        print(f"🧠✨ SYSTEM: {agent.name} got LLM response")
    
    async def on_tool_start(self, context, agent, tool):
        self._init_agent_stats(agent.name)
        self.agent_stats[agent.name]['tool_calls'] += 1
        self.system_stats['total_tool_calls'] += 1
        
        print(f"🔨 SYSTEM: {agent.name} tool call #{self.agent_stats[agent.name]['tool_calls']} ({tool.name})")
    
    async def on_tool_end(self, context, agent, tool, result):
        print(f"✅🔨 SYSTEM: {agent.name} finished {tool.name}")
        print(f"   Result length: {len(str(result))} characters")
    
    async def on_handoff(self, context, from_agent, to_agent):
        self.system_stats['total_handoffs'] += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.system_stats['total_handoffs']}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context, agent, output):
        if agent.name in self.agent_stats and self.agent_stats[agent.name]['start_time']:
            duration = time.time() - self.agent_stats[agent.name]['start_time']
            self.agent_stats[agent.name]['total_time'] = duration
        
        print(f"✅ SYSTEM: {agent.name} finished")
        print(f"   Duration: {duration:.2f}s")
        print(f"   LLM calls: {self.agent_stats[agent.name]['llm_calls']}")
        print(f"   Tool calls: {self.agent_stats[agent.name]['tool_calls']}")
        
        # Print system summary
        total_time = time.time() - self.start_time if self.start_time else 0
        print(f"\n📊 SYSTEM STATS:")
        print(f"   Total runtime: {total_time:.2f}s")
        print(f"   Total LLM calls: {self.system_stats['total_llm_calls']}")
        print(f"   Total tool calls: {self.system_stats['total_tool_calls']}")
        print(f"   Total handoffs: {self.system_stats['total_handoffs']}")
        print(f"   Agents used: {list(self.agent_stats.keys())}")
```

## Hook Execution Order in Multi-Agent Systems 📋

Understanding the order across multiple agents:

```
Multi-Agent Flow:

Agent A:
1. 🌅 on_agent_start (Agent A becomes active)
2. 📞 on_llm_start (Agent A asks AI)
3. 🧠✨ on_llm_end (Agent A gets response)
4. 🔨 on_tool_start (Agent A uses tool)
5. ✅🔨 on_tool_end (Agent A tool completes)
6. 🏃‍♂️➡️🏃‍♀️ on_handoff (A → B)
7. ✅ on_agent_end (Agent A finishes)

Agent B:
8. 🌅 on_agent_start (Agent B becomes active)
9. 📞 on_llm_start (Agent B asks AI)
10. 🧠✨ on_llm_end (Agent B gets response)
11. ✅ on_agent_end (Agent B finishes)
```

## Real-World Use Cases 🌍

### 1. System Performance Monitoring 📈
```python
class PerformanceMonitor(RunHooksBase):
    async def on_agent_start(self, context, agent):
        print(f"⚡ Performance: {agent.name} started")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print(f"🧠 Performance: LLM call initiated by {agent.name}")
    
    async def on_tool_start(self, context, agent, tool):
        print(f"🔧 Performance: {tool.name} tool started by {agent.name}")
```

### 2. Audit Trail & Compliance 📝
```python
class AuditTrail(RunHooksBase):
    def __init__(self):
        self.audit_log = []
    
    async def on_agent_start(self, context, agent):
        self.audit_log.append(f"AGENT_START: {agent.name} at {datetime.now()}")
    
    async def on_handoff(self, context, from_agent, to_agent):
        self.audit_log.append(f"HANDOFF: {from_agent.name} → {to_agent.name} at {datetime.now()}")
    
    async def on_tool_start(self, context, agent, tool):
        self.audit_log.append(f"TOOL_USE: {agent.name} used {tool.name} at {datetime.now()}")
```

### 3. User Experience Updates 👥
```python
class UserExperienceTracker(RunHooksBase):
    async def on_agent_start(self, context, agent):
        if agent.name == "CustomerService":
            print("👋 Our customer service team is helping you...")
        elif agent.name == "TechnicalSupport":
            print("🔧 Connecting you with technical support...")
        elif agent.name == "BillingManager":  
            print("💰 Our billing specialist is handling your request...")
    
    async def on_handoff(self, context, from_agent, to_agent):
        print(f"🔄 Transferring you from {from_agent.name} to {to_agent.name}")
    
    async def on_tool_start(self, context, agent, tool):
        if tool.name == "database_lookup":
            print("🔍 Looking up your account information...")
        elif tool.name == "process_refund":
            print("💳 Processing your refund...")
```

## Key Points for Beginners 📚

1. **System-Wide**: Run hooks monitor **ALL agents** in the execution
2. **Global View**: See the **big picture** of how agents collaborate
3. **Setup**: Use `run_hooks=YourHooksClass()` in the `run()` function
4. **Coordination**: Track handoffs and collaboration between agents
5. **Analytics**: Perfect for system-wide performance and usage analytics
6. **Async**: All hook methods must be `async` functions

## Common Mistakes ❌

### ❌ Don't Do This:
```python
# Confusing run hooks with agent hooks
agent.hooks = RunHooksBase()  # Wrong! Use AgentHooksBase for agents

# Forgetting to pass run_hooks to run()
result = run(agents=agent1)  # No monitoring!
```

### ✅ Do This Instead:
```python
# Correct setup for run hooks
system_monitor = MyRunHooks()
result = await run(
    agents=agent1 
    run_hooks=system_monitor  # Correct!
)

# Agent hooks are separate
agent1.hooks = MyAgentHooks()  # Individual agent monitoring
```

## When to Use Run Hooks vs Agent Hooks

| Use Run Hooks When | Use Agent Hooks When |
|-------------------|---------------------|
| 🏢 Monitor entire system | 🏠 Monitor specific agent |
| 📊 System-wide analytics | 🔍 Debug one agent |
| 🤝 Track agent collaboration | 🎯 Agent-specific logic |
| 📈 Performance across all agents | 📝 Individual agent logs |
| 🔄 Understand handoff patterns | 🚨 Agent-specific alerts |

Think of Run hooks as your **air traffic control tower** 🛩️📡 - you can see all the planes (agents) and how they coordinate, while Agent hooks are like **individual airplane instruments** ✈️📊 - focused on one specific plane!