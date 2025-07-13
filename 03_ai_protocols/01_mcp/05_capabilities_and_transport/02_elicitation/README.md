# 02: [Elicitation](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation) - Interactive Tool Experiences

The Model Context Protocol (MCP) provides a standardized way for servers to request additional information from users during tool execution. This enables tools to adapt and respond based on user input, creating interactive and dynamic experiences.

## 🎯 Learning Objectives
By the end of this lesson, you will be able to:
1. **Understand** why and when tools need to request user input
2. **Implement** a basic elicitation-enabled MCP server
3. **Handle** elicitation requests in an MCP client
4. **Design** user-friendly interactive tool experiences

## 🤔 Why Elicitation?

### The Problem: Static vs. Interactive Tools

**Traditional Tool (Static):**
```python
@mcp.tool()
def order_pizza(size: str, toppings: str) -> str:
    # User must provide ALL parameters upfront
    return f"Order: {size} pizza with {toppings}"
```

**Interactive Tool (With Elicitation):**
```python
@mcp.tool()
async def order_pizza(ctx: Context, size: str) -> str:
    # Ask for toppings only if user wants them
    result = await ctx.elicit(
        message="Would you like toppings?",
        schema=OrderPreferences
    )
    if result.data.want_toppings:
        return f"Order: {size} pizza with {result.data.toppings}"
    return f"Order: plain {size} pizza"
```

### Key Benefits
1. **Progressive Disclosure:** Ask for information only when needed
2. **Conditional Logic:** Adapt questions based on previous answers
3. **Better UX:** Guide users through complex decisions
4. **Validation:** Ensure correct input format and constraints

## 🏗️ Core Concepts

### 1. Stateful Connections
Elicitation requires back-and-forth communication during tool execution:
```
Client → Tool Request → Server
Client ← "Want toppings?" ← Server
Client → "Yes, mushrooms" → Server
Client ← Final Result ← Server
```

### 2. Elicitation Schema
Define the structure of requested data using Pydantic:
```python
class OrderPreferences(BaseModel):
    want_toppings: bool = Field(
        description="Would you like to add extra toppings?"
    )
    toppings: str = Field(
        default="mushrooms",
        description="What toppings would you like? (comma-separated)"
    )
```

### 3. Response Actions
Elicitation requests can have three outcomes:
- **Accept:** User provides the requested data
- **Decline:** User explicitly declines to provide data
- **Cancel:** User dismisses without making a choice

## 🛠️ Implementation Guide

### Server Setup
1. Create a stateful MCP server:
   ```python
   mcp = FastMCP(
       name="elicitation-server",
       stateless_http=False  # Required for elicitation
   )
   ```

2. Define your data schema:
   ```python
   class OrderPreferences(BaseModel):
       want_toppings: bool = Field(...)
       toppings: str = Field(...)
   ```

3. Create an elicitation-enabled tool:
   ```python
   @mcp.tool()
   async def order_pizza(ctx: Context, size: str) -> str:
       result = await ctx.elicit(
           message=f"Ordering a {size} pizza. Would you like to customize it?",
           schema=OrderPreferences
       )
       # Handle the response...
   ```

### Client Setup
1. Create an elicitation callback handler:
   ```python
   async def mock_elicitation(
       context: RequestContext["ClientSession", Any], 
       params: types.ElicitRequestParams
   ) -> types.ElicitResult | types.ErrorData:
       print(f"<- Client: Received 'elicitation' request from server.")
       print(f"<- Client Parameters '{params}'.")
       
       # Return mock response (in real app, would get from user)
       return types.ElicitResult(
           action="accept",
           content={"want_toppings": True, "toppings": "fajita"}
       )
   ```

2. Initialize session with callback:
   ```python
   async with ClientSession(
       read_stream, 
       write_stream, 
       elicitation_callback=mock_elicitation
   ) as session:
       await session.initialize()
   ```

## 🚀 Running the Demo

### Prerequisites
```bash
cd mcp_code
uv sync
```

### Start the Server
```bash
uvicorn server:mcp_app --port 8000
```

### Run the Client
```bash
python client.py
```

### Expected Output
```
🚀 Connecting to MCP server...
✅ Connected. Initializing session...

SCENARIO 1: Accepting the elicitation
----------------------------------------
<- Client: Received 'elicitation' request from server.
<- Client Parameters: [Schema and message details]
✅ Result: Order confirmed: large pizza with fajita

SCENARIO 2: Declining the elicitation
----------------------------------------
<- Client: Received 'elicitation' request from server.
<- Client Parameters: [Schema and message details]
✅ Result: Order confirmed: medium pizza with fajita
```

## 🎓 Best Practices

1. **Clear Messages:**
   - Provide descriptive prompts in the schema
   - Include helpful descriptions for each field
   - Show validation constraints in the schema

2. **Smart Validation:**
   - Use appropriate field types (bool, str, etc.)
   - Set reasonable defaults where appropriate
   - Add field descriptions for better UX

3. **Progressive Disclosure:**
   - Ask for information only when needed
   - Use conditional fields based on previous answers
   - Keep the schema flat and focused

4. **Error Handling:**
   - Handle all response actions (accept/decline/cancel)
   - Provide clear error messages
   - Include fallback behavior

## 🔄 Connection to Other Lessons

**Building on Previous:**
- **Sampling:** Tools that can think
- **This Lesson:** Tools that can ask questions

**Leading to Next:**
- **Roots:** Tools that understand project context

## 🎯 Practice Exercises

1. **Basic:** Add validation to the pizza toppings (e.g., max 3 toppings)
2. **Intermediate:** Add size recommendations based on party size
3. **Advanced:** Create a multi-step order wizard (size → toppings → drinks)

## 🏆 Success Criteria

You've mastered this lesson when you can:
- [ ] Explain when to use elicitation vs. upfront parameters
- [ ] Implement basic elicitation in your tools
- [ ] Handle all elicitation response types
- [ ] Design user-friendly interactive experiences

---

**🎓 Ready for Context?** Once you've mastered interactive tools, move on to [03_roots](../03_roots/) to learn how tools can discover and work with your project structure. 