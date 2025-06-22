# A2A Hands-On Steps 🛠️

**Learn A2A by building - step by step with working code**

> **Prerequisites**: Read the [A2A theory overview](../readme.md) first for context.

## 🎯 Learning Approach

**Active Learning Principles:**
- **Start from zero** - Build everything step by step
- **Immediate feedback** - Each step produces working code
- **Visual first** - Steps 1-3 use browser for immediate visual feedback
- **Official A2A sequence** - Steps 4-7 follow the [official A2A Python tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/)
- **Build incrementally** - Each step adds one focused concept

## 📋 Complete Step-by-Step Progression

```
01_agent_card/              # Serve basic agent card (visual in browser)
02_agent_skill/             # Add skills to agent card (visual in browser)  
03_multiple_cards/          # Multiple agent cards (visual in browser)
04_agent_executor/          # Agent executor pattern (official tutorial)
05_a2a_client/              # Basic A2A messaging (message/send)
06_message_streaming/       # Server-sent events streaming (message/stream)
07_multiturn_conversation/  # Multiturn conversations with task management
08_push_notifications/      # Push notifications for disconnected scenarios
09_agent_discovery/         # Agent discovery mechanisms and registry patterns
10_agent_to_agent/          # Direct agent-to-agent communication patterns
11_authentication/          # Authentication & security (OAuth2, JWT, API keys)
12_enterprise_features/     # Enterprise features & production deployment        
```

## 📚 Complete Step Learning Goals

| Step | Focus | Key Concepts | Official Reference | Testing Method |
|------|-------|--------------|-------------------|----------------|
| **01** | Agent Card | Basic agent discovery, JSON structure | [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/) | Browser + curl |
| **02** | Agent Skill | Skills definition, capabilities | [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/) | Browser + curl |
| **03** | Multiple Cards | Multiple agents, skill variations | Agent ecosystem patterns | Browser + curl |
| **04** | Agent Executor | AgentExecutor pattern, RequestContext | [Agent Executor](https://google-a2a.github.io/A2A/latest/tutorials/python/4-agent-executor/) | curl + test script |
| **05** | Hello A2A | A2A messaging, JSON-RPC 2.0 | [Interact with Server](https://google-a2a.github.io/A2A/latest/tutorials/python/6-interact-with-server/) | curl + test script |
| **06** | Streaming | Server-sent events, real-time | [Streaming & Multiturn](https://google-a2a.github.io/A2A/latest/tutorials/python/7-streaming-and-multiturn/) | curl + browser |
| **07** | Multiturn | Task management, conversation state | [Streaming & Multiturn](https://google-a2a.github.io/A2A/latest/tutorials/python/7-streaming-and-multiturn/) | Multi-request test |
| **08** | Push Notifications | Webhooks, disconnected scenarios | [Push Notifications](https://google-a2a.github.io/A2A/latest/topics/streaming-and-async/#2-push-notifications-for-disconnected-scenarios) | Webhook test |
| **09** | Agent Discovery | Agent discovery mechanisms, registry | [A2A Agent Discovery](https://google-a2a.github.io/A2A/specification/#agent-discovery) | Multi-agent setup |
| **10** | Agent-to-Agent | Direct agent communication patterns | [A2A Multi-Agent Communication](https://google-a2a.wiki/technical-documentation/#agent-collaboration) | Multi-agent test |
| **11** | Authentication | Security, OAuth2, JWT, API keys | [A2A Security Features](https://google-a2a.github.io/A2A/specification/#security) | Secure client test |
| **12** | Enterprise Features | Production deployment, monitoring | [A2A Production Considerations](https://google-a2a.github.io/A2A/specification/#production-considerations) | Production deploy |

## 🎯 Progressive Complexity

**Visual Steps (1-3)**: Start server → Open browser → See results
- Focus on understanding A2A agent cards and skills
- Immediate visual feedback in browser
- No complex protocol handling yet

**Official Tutorial Steps (4-7)**: Follow A2A Python tutorial
- **Step 4**: [Agent Executor](https://google-a2a.github.io/A2A/latest/tutorials/python/4-agent-executor/) - Core execution pattern
- **Step 5**: Basic A2A messaging with message/send
- **Step 6**: [Streaming](https://google-a2a.github.io/A2A/latest/tutorials/python/7-streaming-and-multiturn/) with Server-Sent Events
- **Step 7**: [Multiturn conversations](https://google-a2a.github.io/A2A/latest/tutorials/python/7-streaming-and-multiturn/) with task management

**Advanced A2A Steps (8-10)**: Real-world patterns
- **Step 8**: [Push Notifications](https://google-a2a.github.io/A2A/latest/topics/streaming-and-async/#2-push-notifications-for-disconnected-scenarios) for disconnected scenarios
- **Step 9**: [Agent Discovery](https://google-a2a.github.io/A2A/specification/#agent-discovery) mechanisms and registry patterns
- **Step 10**: [Agent-to-Agent Communication](https://google-a2a.wiki/technical-documentation/#agent-collaboration) patterns

**Production Steps (11-12)**: Real-world deployment
- **Step 11**: [Authentication & Security](https://google-a2a.github.io/A2A/specification/#security) (OAuth2, JWT, API keys)
- **Step 12**: [Enterprise Features](https://google-a2a.github.io/A2A/specification/#production-considerations) & production deployment

## 💡 Why This Structure Works

- **Complete A2A coverage** - All official tutorial concepts included
- **Missing concepts added** - Agent Executor, Streaming, Push Notifications
- **Proper progression** - Visual → Tutorial → Advanced → Production
- **Official reference alignment** - Links to official A2A documentation
- **No overwhelming complexity** - One concept per step
- **Immediate results** - Each step produces working code
- **Visual feedback first** - Browser testing for early steps
- **Progressive building** - Each step builds on previous ones

## 🎯 Expected Outcomes

After completing all 12 steps, you'll be able to:

- ✅ Build A2A-compliant agents from scratch
- ✅ Implement the Agent Executor pattern correctly
- ✅ Handle all core A2A protocol methods (message/send, message/stream, tasks/*)
- ✅ Create streaming and multiturn conversations
- ✅ Implement push notifications for disconnected scenarios
- ✅ Create multi-agent systems with proper discovery
- ✅ Handle authentication and security properly
- ✅ Deploy production-ready A2A agents

## 📖 Official A2A References

This hands-on guide directly implements concepts from:

- **[A2A Python Tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/)** - Steps 4-7 follow this exactly
- **[Streaming & Async Operations](https://google-a2a.github.io/A2A/latest/topics/streaming-and-async/)** - Steps 6-8 implement these patterns
- **[A2A Protocol Specification](https://google-a2a.github.io/A2A/latest/specification/)** - All steps follow this spec

---

**Ready to start building? Begin with [Step 01: Agent Card](./01_agent_card/) 🚀**

*Each step includes complete code, testing instructions, and references to official A2A documentation.* 