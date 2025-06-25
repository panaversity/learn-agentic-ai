# MCP Cancellation Postman Tests 🧪

This Postman collection provides comprehensive testing for MCP request cancellation functionality.

## 🚀 **Quick Setup**

### **1. Import the Collection**
1. Open Postman
2. Click "Import"
3. Select `MCP_Cancellation_Tests.postman_collection.json`
4. The collection will appear in your workspace

### **2. Start the MCP Server**
```bash
cd ../mcp_code
python server.py
```

Server will start on `http://localhost:8000`

### **3. Run the Tests**
You can run tests individually or as a complete collection.

## 🧪 **Test Scenarios**

### **1. Initialize MCP Connection**
- ✅ Establishes MCP session
- 📋 Extracts session ID for subsequent requests
- 🔐 Sets up authentication headers

### **2. Send Initialized Notification**
- 📡 Completes MCP handshake
- ✅ Verifies notification acceptance

### **3. Start Long-Running Task**
- 🚀 Begins 10-second file processing
- 📋 Stores request ID for cancellation
- ⏰ Simulates real long-running operation

### **4. Cancel Long-Running Task**
- ⏹️ Sends cancellation notification
- 📝 Includes cancellation reason
- ✅ Verifies server accepts cancellation

### **5. Check Active Tasks**
- 🔍 Queries server for active tasks
- 🧹 Verifies cleanup after cancellation
- 📊 Shows task status management

### **6. Quick Task (Race Condition Test)**
- ⚡ Starts task that completes immediately
- 🏁 Tests edge case handling
- 📋 Prepares for race condition test

### **7. Cancel Quick Task (Race Condition)**
- 🏁 Attempts to cancel completed task
- ⚠️ Tests server's race condition handling
- ✅ Verifies graceful handling of late cancellation

### **8. Final Active Tasks Check**
- 🧹 Confirms all tasks cleaned up
- ✅ Verifies no resource leaks
- 📊 Shows final system state

## 🎯 **How to Use**

### **Option 1: Run Individual Tests**
1. Click on any test request
2. Click "Send"
3. Review response and test results
4. Check server logs for detailed output

### **Option 2: Run Complete Collection**
1. Right-click on collection name
2. Select "Run collection"
3. Configure run settings (delay between requests)
4. Click "Run MCP Cancellation Tests"
5. Review test results summary

### **Option 3: Manual Cancellation Test**
1. Send "3. Start Long-Running Task"
2. **Immediately** send "4. Cancel Long-Running Task"
3. Watch server logs for real-time cancellation
4. Verify task stops mid-processing

## 📊 **Expected Results**

### **Successful Cancellation**
```
Server logs should show:
🚀 Starting file processing: postman_test_file.csv
📋 Request ID: 2
⏰ Estimated time: 10 seconds
📊 Processing postman_test_file.csv... 1/10 seconds
📊 Processing postman_test_file.csv... 2/10 seconds
⏹️ Cancellation received for request: 2
✅ Cancelled active task: 2
🧹 Cleaned up resources for: 2
```

### **Race Condition Handling**
```
Server logs should show:
⚡ Quick task started: 4
✅ Quick task completed: 4
⏹️ Cancellation received for request: 4
⚠️ Request 4 not found in active tasks (race condition)
   This is normal - request may have completed before cancellation arrived
```

## 🔧 **Troubleshooting**

### **Server Not Responding**
- ✅ Ensure server is running: `python server.py`
- 🌐 Check URL: `http://localhost:8000`
- 🔌 Verify port 8000 is available

### **Session ID Issues**
- 🔄 Re-run "1. Initialize MCP Connection"
- 📋 Check collection variables for session ID
- 🔐 Ensure session ID is properly set

### **Cancellation Not Working**
- ⏰ Send cancellation quickly after starting task
- 📋 Verify request ID matches between start/cancel
- 🔍 Check server logs for cancellation messages

## 💡 **Learning Objectives**

After running these tests, you'll understand:

1. **🔄 MCP Session Management**
   - How session IDs work
   - Proper initialization sequence

2. **⏹️ Cancellation Protocol**
   - `notifications/cancelled` message format
   - Request ID tracking

3. **🏁 Race Condition Handling**
   - What happens when cancelling completed tasks
   - Graceful error handling

4. **🧹 Resource Management**
   - How servers clean up cancelled tasks
   - Active task tracking

## 🚀 **Next Steps**

- Try modifying processing times in requests
- Test with multiple concurrent tasks
- Experiment with different cancellation reasons
- Build your own cancellable MCP tools

---

**💡 Pro Tip**: Watch the server logs while running tests - they show the complete cancellation flow in real-time! 