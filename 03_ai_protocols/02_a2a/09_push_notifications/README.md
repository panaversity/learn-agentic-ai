# [Asynchronous Push Notifications](https://a2a-protocol.org/latest/topics/streaming-and-async/#2-push-notifications-for-disconnected-scenarios)

> **Goal**: Learn A2A push notifications for long-running tasks when clients can't maintain persistent connections.

For very long-running tasks (e.g., lasting minutes, hours, or even days) or when clients cannot or prefer not to maintain persistent connections (like mobile clients or serverless functions), A2A supports asynchronous updates via push notifications. This mechanism allows the A2A Server to actively notify a client-provided webhook when a significant task update occurs.

> **⚠️ Important Limitation (as of 13 August 2025):**
>
> The current A2A Python server implementations (including this example) do **not** guarantee webhook notifications for "completed" or terminal task states if the client disconnects before the task finishes.
>
> - If the client disconnects, the agent's event queue is closed and background work is cancelled, so only "submitted" and "working" webhooks may be sent.
> - True background/persistent task support (where webhooks are always sent regardless of client connection) is **not available out-of-the-box** at the time of writing.
> - There are **no official A2A Python examples** for this scenario as of this documentation.
>
> **Workaround:** To guarantee webhook delivery after disconnect, you must implement your own background task runner and webhook sender, decoupled from the client event queue.
>
> _If/when the A2A Python ecosystem adds first-class support for persistent background tasks and reliable webhooks, this step should be updated._

## Why Push Notifications?

In Step 4, you learned streaming with persistent connections. But what happens when:

- **Task takes 2 hours**
- **Client disconnects** (mobile app backgrounded, network issues)  
- **Server restarts** (deployment, maintenance)

**Solution**: Push notifications!

### A2A Push Notification Flow

```
1. Client starts long task with webhook config
2. Client disconnects (task keeps running)
3. Agent completes task asynchronously  
4. Agent POSTs to webhook with HMAC signature
5. Client validates signature & fetches results
```

## 🛠️ Build 1: Long-Running Task Agent with Webhooks

Let's build an agent that handles tasks lasting several minutes:

### View `long_running_agent.py`

### View Webhook Receiver `webhook_receiver.py`

### Test Long-Running Tasks with Webhooks

View `test_long_running.py`:

### Run the Complete Test

1. **Start webhook receiver**: `uv run python webhook_receiver.py` (port 9000)
2. **Start long-running agent**: `uv run python long_running_agent.py` (port 8001)  
3. **Run tests**: `uv run python test_long_running.py`
4. **Try the disconnect test** to see webhooks in action!

**🎯 Key Learning**: Webhooks enable truly asynchronous task completion - clients can disconnect and get notified when tasks finish!

## 🎯 What You've Mastered

Congratulations! You've now built A2A agents with:

### 📊 Complete Push Notification Capabilities

| Feature | Basic | Enterprise |
|---------|-------|------------|
| **Webhook Delivery** | ✅ HMAC signatures | ✅ JWT + HMAC |
| **Task Types** | ✅ Long-running | ✅ Secure + Batch + Files |
| **Error Handling** | ✅ Basic retry | ✅ Enterprise logging |
| **Authentication** | ✅ Simple secrets | ✅ JWT with claims |

### 🚀 Ready for Multi-Agent Systems

You now understand:
- **Asynchronous Task Completion**: Tasks that outlive connections
- **Multiple Artifact Delivery**: Complex result handling
- **Production Architecture**: Scalable, secure A2A implementations

**🎯 Next Step**: Multi-turn conversations!

- https://a2a-protocol.org/latest/topics/streaming-and-async/
- https://a2a-protocol.org/latest/topics/life-of-a-task/
- https://a2a-protocol.org/latest/tutorials/python/7-streaming-and-multiturn/