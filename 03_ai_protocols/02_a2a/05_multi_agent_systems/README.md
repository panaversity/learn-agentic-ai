# Step 5: A2A Powered Multi-Agent Systems Coordination ⭐

**Build a complete multi-agent Table Tennis scheduling system using OpenAI Agents SDK and A2A protocol** where a host agent coordinates with 3 specialized agents to schedule a Table Tennis game. 

## 🏓 The Table Tennis Scheduling Scenario

**User**: _"What time is everyone available tomorrow for Table Tennis?"_

**System Response**: _"Everyone is available tomorrow at 8 PM, and I've booked Court 1 for your game!"_

### 🏗️ Architecture Overview

```
┌─────────────────────┐    A2A     ┌──────────────────────┐
│   Host Agent        │◄───────────►│   Ameen Agent        │
│   (Orchestrator)    │            │   (Personal Calendar) │
│                     │            └──────────────────────┘
│ - Agent Discovery   │    A2A     ┌──────────────────────┐
│ - Parallel Messaging│◄───────────►│   Qasim Agent        │
│ - Response Analysis │            │   (Schedule Manager)  │
│ - Court Booking     │            └──────────────────────┘
│ - Decision Making   │    A2A     ┌──────────────────────┐
│                     │◄───────────►│   Ahmad Agent        │
└─────────────────────┘            │   (Availability Bot)  │
                                   └──────────────────────┘
```
### Multi-Agent Flow

1. **Host discovers** all remote agents via A2A agent cards
2. **Parallel messaging** to all 3 agents simultaneously
3. **Response aggregation** to find common availability
4. **Court booking** using host's local tools
5. **Final confirmation** sent to all participants

**🎯 Result**: Complete end-to-end Table Tennis scheduling with zero manual coordination!

## 🔧 Installation & Dependencies

### Project Setup

We will setup 3 different agents and the host agent

1. Host Agent
```bash
uv init friends_host
cd friends_host
# Main project dependencies
uv add openai-agents a2a-sdk uvicorn
```

2. Ameen Agent
```bash
uv init ameen_agent
cd ameen_agent
# Main project dependencies
uv add openai-agents a2a-sdk uvicorn
```

3. Qasim Agent
```bash
uv init qasim_agent
cd qasim_agent
# Main project dependencies
uv add openai-agents a2a-sdk uvicorn
```

4. Ahmad Agent
```bash
uv init ahmad_agent
cd ahmad_agent
# Main project dependencies
uv add openai-agents a2a-sdk uvicorn
```

### Environment Variables

Create .env and add `GEMINI_API_Key` in each project. Optionally you can add `OPENAI_API_KEY` to enable tracing.

## 🛠️ Build 1: Ameen's Personal Calendar Agent

Ameen's agent manages her personal schedule and availability.

#### Code: ameen_agent/main.py

## 🛠️ Build 2: Qasim's Schedule Manager Agent

Nate's agent focuses on schedule optimization and time management.

#### Code: qasim_agent/main.py

## 🛠️ Build 3: Ahmad's Availability Bot Agent

Caitlyn's agent specializes in rapid availability checking and conflict resolution.

#### Code: ahmad_agent/main.py

## ⚙️ Build 4: Host Agent (Multi-Agent Orchestrator)

The Host Agent uses OpenAI Agents SDK with custom A2A tools to coordinate other agents.

#### Code: 
1. Host Agent/UI Agent: friends_host/main.py
2. CLI Client: friends_host/cli_client.py

**🎯 Key Features**:

- **A2A Discovery**: Automatically discovers remote agents
- **Parallel Coordination**: Sends messages to all agents simultaneously
- **OpenAI Intelligence**: Uses GPT-4 for request analysis
- **Court Booking**: Simulates real court reservation system
- **Error Handling**: Graceful failure management

## 🧪 Testing the Multi-Agent System

### Start Individual Agents

```bash
# Terminal 1
cd ameen_agent && uv run python main.py

# Terminal 2  
cd qasim_agent && uv run python main.py

# Terminal 3
cd ahmad_agent && uv run python main.py
```

### Terminal 4 - Start coordinator:

```bash
cd friends_host && uv run python main.py
```

### Terminal 5 - Use Client CLI:

```bash
cd friends_host && uv run python cli_client.py
```

```bash
You: Check and if possible schedule Table Tennis for tomorrow evening with all
Coordinator: [discovers agents, sends personalized messages, books court]
```

The coordinator will dynamically discover agents and send personalized messages like:

Sample Chat

```bash
🏓 Table Tennis Coordinator CLI
Type 'quit' to exit

You: Junaid here
Coordinator: Thinking...
Coordinator: Hello Junaid, I've discovered the following agents:

*   Ameen's Personal Calendar Agent (Port: 8001)
*   Qasim's Schedule Manager Agent (Port: 8002)
*   Ahmad's Availability Bot (Port: 8003)

How can I help you schedule a table tennis game with your friends? Please let me know who you'd like to play with and any preferred times.

You: Check and if possible schedule Table Tennis for tomorrow evening with all
Coordinator: Thinking...
Coordinator: It looks like I need a bit more information to finalize the schedule for tomorrow evening.

*   **Ameen** is available from 7:00 PM to 9:00 PM (high preference) and 8:00 PM to 10:00 PM (medium preference).
*   **Qasim** needs to know the specific date and who will be playing.
*   **Ahmad** needs tomorrow's date (including the year) and the specific time range you're considering for tomorrow evening.

Could you please provide tomorrow's date (e.g., "October 27th, 2023") and confirm the preferred time range for the game?

You: Tommorrow 13 August 2025 from 7:00 PM to 9:00 PM
Coordinator: Thinking...
Coordinator: Unfortunately, Ahmad is unavailable for table tennis on August 13th, 2025, from 7:00 PM to 9:00 PM due to a prior commitment.

However, Ameen is available at that time.

Ahmad has offered the following alternative times on August 14th, 2025:
*   7:30 PM to 9:30 PM
*   6:00 PM to 7:00 PM

Would you like me to check with Ameen and Qasim about their availability for these alternative times on August 14th, 2025, or would you like to propose a different time altogether?

You: let's schedule with ameen for now and just inform them so they can join if they want
Coordinator: Thinking...
Coordinator: Great! I've booked a table tennis court for you and Ameen.

**Booking Details:**
*   **Date:** August 13th, 2025
*   **Time:** 7:00 PM
*   **Duration:** 2 hours
*   **Court:** Court 1
*   **Booking ID:** TT-20250813-094005

I will now inform Qasim and Ahmad about this booking, so they can join if they wish.

You: so its done
Coordinator: Thinking...
Coordinator: Yes, it's done!

Here's a summary of what's been scheduled:

*   **Who:** Junaid and Ameen
*   **Activity:** Table Tennis
*   **Date:** August 13th, 2025
*   **Time:** 7:00 PM - 9:00 PM (2 hours)
*   **Court:** Court 1
*   **Booking ID:** TT-20250813-094005

I have also informed Qasim and Ahmad about this booking, so they are aware and can join if they wish.

```

## 🎯 What You'll Master

After building this multi-agent system, you'll have hands-on experience with:

### **🤖 OpenAI Agents SDK Integration**

- ✅ **GPT-4 Integration**: Using OpenAI models for intelligent agent behavior
- ✅ **Agent Personality**: Creating distinct agent personalities and response styles
- ✅ **Context Management**: Managing conversation context across multiple agents
- ✅ **Async Programming**: Building scalable async agent systems

### **🔗 A2A Protocol Mastery**

- ✅ **Agent Discovery**: Implementing agent card publishing and discovery
- ✅ **Message Formatting**: Converting between OpenAI and A2A message formats
- ✅ **Parallel Communication**: Coordinating multiple agents simultaneously
- ✅ **Error Handling**: Graceful failure management in distributed systems

### **🏗️ Multi-Agent Architecture**

- ✅ **Orchestration Patterns**: Host-coordinator pattern for multi-agent systems
- ✅ **Service Discovery**: Dynamic agent discovery and capability matching
- ✅ **Response Aggregation**: Collecting and synthesizing multiple agent responses
- ✅ **Decision Making**: Intelligent coordination based on agent feedback

### **⚡ Production Readiness**

- ✅ **Testing Strategy**: Comprehensive multi-agent system testing
- ✅ **Monitoring**: Health checks and status monitoring across agents
- ✅ **Scalability**: Adding new agents without code changes
- ✅ **Deployment**: Running multi-agent systems in production

## 🎉 Success Criteria

You've mastered multi-agent systems when:

### **✅ System Functionality**

- [ ] All 4 agents start and register successfully
- [ ] Host agent discovers all remote agents automatically
- [ ] Multi-agent coordination completes end-to-end
- [ ] System handles individual agent failures gracefully
- [ ] Comprehensive test suite passes completely

### **✅ Technical Understanding**

- [ ] Understand OpenAI Agents SDK integration patterns
- [ ] Can explain A2A protocol message flow
- [ ] Know how to add new agents to the system
- [ ] Understand multi-agent orchestration strategies
- [ ] Can debug distributed agent communication issues

### **✅ Production Readiness**

- [ ] System runs reliably under load
- [ ] Proper error handling and logging implemented
- [ ] Agent discovery works across network boundaries
- [ ] Performance metrics and monitoring in place
- [ ] Security considerations understood and implemented

## 📈 Next Learning Steps

After mastering this multi-agent system:

1. **Step 6: Push Notifications** - Add webhook support for long-running coordination
2. **Step 7: Multi-Turn Conversations** - Enable persistent context across agent interactions
3. **Step 8: Authentication** - Secure the multi-agent network
4. **Step 9: MCP-A2A Bridge** - Integrate with Model Context Protocol
5. **Step 10: gRPC Production** - High-performance agent communication

## 💡 Why This Architecture Matters

### **🚀 Industry Relevance**

- **Real Enterprise Pattern**: Multi-agent coordination is core to modern AI systems
- **Framework Agnostic**: A2A enables mixing different AI frameworks seamlessly
- **Scalable Design**: Patterns used by major AI platforms and companies
- **Future-Proof**: Architecture scales from prototype to production

### **🎯 Learning Value**

- **Practical Skills**: Build systems that solve real coordination problems
- **Technical Depth**: Master both AI frameworks and distributed systems
- **Problem Solving**: Experience with complex multi-agent interaction patterns
- **Career Ready**: Skills directly applicable to AI engineering roles

---

**🚀 Ready to build your multi-agent empire? Start with `./run_all_agents.sh` and experience the magic of OpenAI Agents SDK + A2A protocol!**

_This is where modern AI systems truly shine - intelligent agents working together seamlessly._ ⭐
