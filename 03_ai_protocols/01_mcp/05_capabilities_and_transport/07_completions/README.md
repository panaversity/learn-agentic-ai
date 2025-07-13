# 07: MCP Completions - Intelligent Auto-Completion

**Learning Objective:** Master the MCP completions capability to provide intelligent, context-aware auto-completion suggestions that enhance user experience when working with parameterized prompts and resources.

## What Are MCP Completions?

MCP completions are a **utility feature** that enables servers to provide intelligent auto-completion suggestions to clients. Think of it like the autocomplete in your IDE, but for MCP prompt arguments and resource template parameters.

### Real-World Analogy
Imagine you're filling out a form online:
- When you start typing your country, the form suggests "United States" as you type "Un..."
- When you select "United States", the state field now shows relevant options like "California", "Texas", etc.
- This is exactly what MCP completions do for prompt arguments and resource parameters!

## Why Are Completions Important?

### Without Completions (Poor UX)
```
User: I want to review some code
System: Please provide the language parameter
User: Uh... what languages do you support?
System: [No help provided]
User: *guesses* "javascript"?
System: Error: Unsupported language. Try: python, rust, typescript, go...
```

### With Completions (Great UX)
```
User: I want to review some code
System: Please provide the language parameter
User: [starts typing "py"]
System: [suggests: "python", "pytorch"]
User: [selects "python"]
System: ✅ Perfect! Now analyzing Python code...
```

## Core Concepts (MCP 2025-06-18)

### 1. Completion Request (`completion/complete`)
The client asks the server: "What should I suggest for this parameter?"

```json
{
  "method": "completion/complete",
  "params": {
    "ref": {
      "type": "ref/prompt",
      "name": "review_code"
    },
    "argument": {
      "name": "language",
      "value": "py"
    }
  }
}
```

### 2. Completion Response
The server responds with intelligent suggestions:

```json
{
  "result": {
    "completion": {
      "values": [
        {
          "value": "python",
          "description": "Python programming language"
        },
        {
          "value": "pytorch", 
          "description": "PyTorch deep learning framework"
        }
      ],
      "total": 2,
      "hasMore": false
    }
  }
}
```

### 3. Context-Aware Completions
Completions can be smart about previously entered values:

```json
{
  "params": {
    "ref": {
      "type": "ref/prompt", 
      "name": "setup_project"
    },
    "argument": {
      "name": "framework",
      "value": "fast"
    },
    "context": {
      "language": "python"
    }
  }
}
```

**Result:** Since language="python", the server suggests Python frameworks like "fastapi", "flask", not JavaScript frameworks.

## Learning Path: From Simple to Advanced

### Level 1: Static Completions
Basic completions that don't change based on context.

**Example:** Programming languages
```python
@mcp.completion()
async def handle_completion(request):
    if request.argument.name == "language":
        return ["python", "javascript", "rust", "go"]
```

### Level 2: Filtered Completions  
Completions that filter based on what the user has typed.

**Example:** Filter languages starting with "py"
```python
@mcp.completion()
async def handle_completion(request):
    if request.argument.name == "language":
        all_languages = ["python", "javascript", "rust", "go"]
        typed = request.argument.value or ""
        return [lang for lang in all_languages if lang.startswith(typed)]
```

### Level 3: Context-Aware Completions
Completions that change based on other parameters.

**Example:** Framework suggestions based on language
```python
@mcp.completion()
async def handle_completion(request):
    if request.argument.name == "framework":
        language = request.context.get("language", "")
        if language == "python":
            return ["fastapi", "flask", "django"]
        elif language == "javascript":
            return ["express", "fastify", "koa"]
```

### Level 4: Hierarchical Completions
Multi-level completions that build on each other.

**Example:** GitHub owner → repository → branch
```python
@mcp.completion()
async def handle_completion(request):
    if request.argument.name == "owner":
        return ["microsoft", "google", "facebook"]
    elif request.argument.name == "repo":
        owner = request.context.get("owner", "")
        if owner == "microsoft":
            return ["vscode", "typescript", "playwright"]
```

## Implementation Architecture

### Server Components (`server.py`)

```python
# 1. Declare completions capability
mcp = FastMCP(
    capabilities={"completions": {}}
)

# 2. Define prompts with parameters
@mcp.prompt()
async def review_code(language: str, code: str):
    """Review code with language-specific suggestions"""
    pass

# 3. Define resource templates with parameters  
@mcp.resource("github://repos/{owner}/{repo}")
async def github_repo(owner: str, repo: str):
    """Access GitHub repository"""
    pass

# 4. Implement completion handler
@mcp.completion()
async def handle_completion(request):
    """Provide intelligent completions"""
    # Smart completion logic here
    pass
```

### Client Components (`client.py`)

```python
# 1. Connect to server
client = Client(StdioServerParameters(command="python", args=["server.py"]))

# 2. Request completions
result = await client.complete(
    ref=PromptReference(type="ref/prompt", name="review_code"),
    argument={"name": "language", "value": "py"}
)

# 3. Display suggestions to user
for completion in result.completion.values:
    print(f"- {completion.value}: {completion.description}")
```

## Educational Examples

### Example 1: Programming Language Completion
**Scenario:** User wants to review code, starts typing "py"
**Server Response:** ["python", "pytorch"] 
**Learning:** Basic filtered completion

### Example 2: Framework Completion with Context
**Scenario:** User selected language="python", now typing "fast" for framework
**Server Response:** ["fastapi"] (not "fastify" which is JavaScript)
**Learning:** Context-aware completion

### Example 3: GitHub Repository Navigation
**Scenario:** User navigating GitHub resources
- Step 1: owner="model" → ["modelcontextprotocol", "microsoft"]
- Step 2: repo="mcp" (with owner="modelcontextprotocol") → ["specification", "servers"]
**Learning:** Hierarchical completion

## Common Patterns & Best Practices

### ✅ Do This
```python
# Provide helpful descriptions
{
    "value": "python",
    "description": "Python programming language - great for AI/ML"
}

# Filter based on user input
typed = request.argument.value or ""
return [item for item in items if item.startswith(typed.lower())]

# Use context wisely
language = request.context.get("language", "")
if language == "python":
    return python_frameworks
```

### ❌ Avoid This
```python
# No descriptions
{"value": "python"}

# No filtering - overwhelming user
return all_10000_programming_languages

# Ignoring context
return ["fastapi", "express", "rails"]  # Mixed languages
```

## Testing Your Understanding

### Quick Check Questions
1. What's the difference between a completion request and a regular MCP request?
2. How do context-aware completions improve user experience?
3. When would you use hierarchical completions?

### Hands-On Exercise
Try modifying the server to add completions for:
1. Database types: "postgresql", "mysql", "sqlite"
2. Make it context-aware: if language="python", suggest "sqlalchemy", "django-orm"

## Integration with DACA Framework

In the DACA (Dapr Agentic Cloud Ascent) framework, completions enhance the agentic experience by:

- **Reducing Cognitive Load:** Agents don't need to guess parameter values
- **Improving Accuracy:** Context-aware suggestions reduce errors
- **Enabling Discoverability:** Users learn what's possible through completions
- **Supporting Scalability:** Better UX means more confident users and broader adoption

## Next Steps

After mastering completions, you'll be ready for:
- **08: Progress Tracking** - Show users what's happening during long operations
- **09: Ping/Pong** - Keep connections alive and healthy

## Resources

- [MCP 2025-06-18 Completion Specification](https://spec.modelcontextprotocol.io/specification/2025-06-18/server/utilities/completion)
- [FastMCP Completion Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Real-World MCP Servers with Completions](https://github.com/modelcontextprotocol/servers)

---

**Remember:** Great completions feel like magic to users - they get exactly what they need, exactly when they need it. That's the power of intelligent auto-completion! 🎯 