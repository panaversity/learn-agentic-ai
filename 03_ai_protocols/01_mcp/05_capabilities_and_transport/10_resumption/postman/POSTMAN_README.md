# 🔄 MCP Resumption - Postman Testing Guide

> This collection demonstrates MCP resumption by simulating a client that disconnects and then seamlessly reconnects to a long-running task.

## 🎯 What This Collection Tests

-   **MCP Initialization**: Establishes a session and gets a `mcp-session-id`.
-   **Simulated Timeout**: Calls a long-running tool with a short timeout to simulate a network drop.
-   **Connection Resumption**: Uses a `GET` request with the `Last-Event-ID` and `mcp-session-id` headers to reconnect and receive the missed messages, as per the MCP specification.

## 🚀 How to Use

### 1. Start the Server

Make sure the example server is running. It has a 6-second delay built in.

```bash
# From the 10_resumption directory
uv run server.py
```

### 2. Run the Requests in Order

Execute the requests in the collection folder by folder. The flow is designed to be run sequentially.

-   **STEP 1: Initialize MCP Connection**: This folder establishes the connection.
    1.  `Initialize MCP Server`: Gets the `mcp-session-id` and the first `last_event_id`.
    2.  `Send Initialized Notification`: Completes the handshake.
-   **STEP 2: Tool Call Timeout**: This folder simulates the network drop.
    3.  `Tool Call with Timeout`: This request has a **2-second timeout**. The server takes 6 seconds, so this request is *guaranteed* to fail, which is what we want.
-   **STEP 3: MCP Resumption**: This folder shows the successful resumption.
    4.  `MCP Resumption with GET + Last-Event-ID`: This request will instantly retrieve the result from the server, which finished the work in the background.

## 🔍 What to Look For

-   In **Step 2**, the tool call will fail with a timeout. This is expected!
-   In **Step 3**, the resumption request will succeed immediately (response time will be very low).
-   Check the Postman Console to see the `mcp-session-id` and `last_event_id` being captured and used automatically by the test scripts.
-   The final response body will contain the text `(Retrieved via resumption)`, proving the cached result was delivered.

## 🔧 **Key Features**

### **Automatic Event ID Tracking**
The collection automatically extracts and stores event IDs:
```javascript
// Finds "id: 12345" in SSE response
if (line.startsWith('id: ')) {
    eventId = line.substring(4).trim();
    pm.collectionVariables.set('last_event_id', eventId);
}
```

### **Session Management**
Auto-captures session IDs:
```javascript
const sessionId = pm.response.headers.get('mcp-session-id');
pm.collectionVariables.set('mcp_session_id', sessionId);
```

### **MCP Resumption Header**
Test 4 uses the MCP specification header:
```json
{
  "key": "Last-Event-ID",
  "value": "{{last_event_id}}",
  "description": "MCP spec header for cross-stream event replay"
}
```

## 🔬 **Technical Learning**

### **Cross-Stream Event Correlation**
The key concept for students to understand:
- **Problem**: Events stored in different streams (`stream_id='1'` vs `stream_id='_GET_stream'`)
- **Solution**: Search ALL streams for events after the last event ID
- **Result**: MCP resumption works as specified!

### **MCP Server Log Evidence**
```bash
🏪 Stored event abc123 in stream 1          # Initialize response
🏪 Stored event def456 in stream _GET_stream # Tool result (different stream!)
🔄 Checking stream 1 with 1 events          # Same stream - no new events
🔄 Checking stream _GET_stream with 1 events # Different stream - found tool result!
🔄 Found event to replay: def456 in different stream _GET_stream
🔄 Sending event: def456 from stream _GET_stream
```

## 🎓 **Learning Outcomes**

After running these tests, students will understand:

- ✅ How MCP initialization establishes connections
- ✅ Why network timeouts happen in real systems
- ✅ How `Last-Event-ID` enables MCP resumption
- ✅ **Cross-stream event correlation** (the technical breakthrough!)
- ✅ How GET requests retrieve cached results
- ✅ The power of never losing progress with MCP

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Server Not Running**
   ```bash
   uv run server.py  # Start server first
   ```

2. **Test 3 Doesn't Timeout**
   - Check timeout is set to 2000ms (2 seconds)
   - Server delay is 6 seconds, so should definitely timeout
   - Look for "Connection timed out as expected" message

3. **Event IDs Not Tracking**
   - Check Test Results tab for console logs
   - Look for "Event ID captured" messages

4. **Test 4 Fails**
   - Ensure Tests 1-3 completed successfully first
   - Check `Last-Event-ID` header is present in Test 4
   - Verify the event ID variable was captured in Test 1

## 🔍 **How to Verify MCP Resumption**

### **Method 1: Server Log Analysis**
Look for these log patterns:
```bash
🔄 Replaying events after [event-id]
🔄 Found event to replay: [new-event-id] in different stream [stream-name]
🔄 Sending event: [new-event-id] from stream [stream-name]
```

### **Method 2: Response Indicator**
The tool result includes proof:
```json
{
  "result": "The weather in Tokyo will be warm and sunny! ☀️ (Retrieved via resumption)",
  "indicator_date": "2025-06-18T04:42:55.711075"
}
```

The **"Retrieved via resumption"** text proves the server replayed the cached result!

### **Method 3: Timing Analysis**
- **Fresh call**: 6+ seconds (server processing time)
- **Resumed call**: ~100ms (cached result retrieval)

## 💡 **The Big Picture**

This collection teaches students that:
- **Network problems happen** (Test 3 timeout)
- **Cross-stream events can be correlated** (the technical breakthrough)
- **MCP resumption works across streams** (Test 4 succeeds)
- **No work is lost** (Same tool call, instant cached result)
- **Last-Event-ID is the key** (The MCP spec header that enables cross-stream replay)

## 🎯 **Test Sequence Summary**

| Test | Purpose | Expected Result |
|------|---------|----------------|
| 1 | Initialize | ✅ Get session & event ID |
| 2 | Complete handshake | ✅ Connection established |
| 3 | Tool call (timeout) | ⏰ Times out (simulates network issues) |
| 4 | MCP resumption | ✅ Succeeds with GET + Last-Event-ID |

Perfect for learning **MCP Cross-Stream Resumption** fundamentals! 🚀

---

## 📋 **Summary**

**What this teaches**: MCP specification resumption in 4 simple steps
**Why it matters**: Real agents face network problems in production systems
**Technical concept**: Cross-stream event correlation enables reliable resumption
**Key learning**: GET + Last-Event-ID header follows MCP specification
**Result**: Students understand production-ready resilient AI agent communication! 🌍 