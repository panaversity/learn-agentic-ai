# Step 8: Push Notifications

**Implement async webhooks for disconnected scenarios**

## 🎯 Goal

Add push notification support for long-running tasks that complete after the client disconnects, using webhooks with proper security validation.

## 🔍 What You'll Learn

- Push notification configuration via A2A
- Webhook security with challenge-response
- JWT/API-Key/HMAC authentication patterns
- Async task completion handling

## 🚀 Quick Start

```bash
# Start webhook receiver
python webhook_receiver.py
# → Runs on http://localhost:9000

# Start A2A agent with push support
python server.py

# Configure push notifications
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/pushNotificationConfig/set",
    "id": 1,
    "params": {
      "config": {
        "url": "http://localhost:9000/webhook",
        "authentication": {
          "type": "jwt",
          "token": "your-jwt-token"
        }
      }
    }
  }'
```

## 🔧 Webhook Flow

1. **Client configures webhook** with authentication
2. **Server validates webhook** with challenge-response  
3. **Long-running task starts** and client disconnects
4. **Task completes** asynchronously
5. **Server posts to webhook** with signed payload
6. **Client validates signature** and fetches final result

## 🛡️ Security Patterns

- **Challenge-Response**: Prevent SSRF attacks
- **JWT Validation**: Verify iss/aud/exp claims
- **HMAC Signatures**: Ensure webhook authenticity
- **Replay Protection**: Use iat/jti for freshness

## 🎯 Success Criteria

- ✅ Webhook configuration and validation works
- ✅ Long-running tasks trigger notifications
- ✅ Security verification prevents attacks
- ✅ Client can fetch final task results

**Next**: [Step 9: Authentication](../09_authentication/) - Secure the agent network
