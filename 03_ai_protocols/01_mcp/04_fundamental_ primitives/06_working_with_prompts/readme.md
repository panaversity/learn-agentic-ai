# 07. Working with Prompts

> **Build and use pre-crafted prompts for common workflows and AI interactions**

## Understanding MCP Prompts

Prompts in MCP are pre-crafted instructions for common workflows. They are **user-controlled**, meaning users decide when to apply them. Unlike tools and resources, prompts provide guidance and structure for AI interactions.

## Why Use Prompts?

Here's the key insight: users can already ask Claude to do most tasks directly. For example, a user could type "reformat the report.pdf in markdown" and get decent results. But they'll get much better results if you provide a thoroughly tested, specialized prompt that handles edge cases and follows best practices.

As the MCP server author, you can spend time crafting, testing, and evaluating prompts that work consistently across different scenarios. Users benefit from this expertise without having to become prompt engineering experts themselves.

### Key Characteristics of Prompts

- **User-controlled**: Users decide when to apply prompts
- **Instruction-focused**: Provide high-quality, reusable instructions
- **Context-aware**: Can include dynamic content and formatting
- **Reusable**: Can be applied across different scenarios
- **Structured**: Follow consistent patterns for effectiveness

## How Prompts Work?

Prompts define a set of user and assistant messages that clients can use. They should be high-quality, well-tested, and relevant to your MCP server's purpose. The workflow is:

- Write and evaluate a prompt relevant to your server's functionality
- Define the prompt in your MCP server using the @mcp.prompt decorator
- Clients can request the prompt at any time
- Arguments provided by the client become keyword arguments in your prompt function
- The function returns formatted messages ready for the AI model

This system creates reusable, parameterized prompts that maintain consistency while allowing customization through variables. It's particularly useful for complex workflows where you want to ensure the AI receives properly structured instructions every time.

### **Core MCP Prompts Concepts**
- **Prompt Discovery**: Using `prompts/list` to find available templates
- **Prompt Generation**: Using `prompts/get` to create customized prompts
- **Parameter Handling**: Dynamic prompt customization with type validation
- **2025-06-18 Features**: Title fields, enhanced metadata, and capabilities declaration

*Learn More:* [MCP Prompts Documentation](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts)

## Protocol Messages

### Listing Prompts

To retrieve available prompts, clients send a `prompts/list` request. This operation
supports [pagination](/specification/2025-06-18/server/utilities/pagination).

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prompts/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "prompts": [
      {
        "name": "code_review",
        "title": "Request Code Review",
        "description": "Asks the LLM to analyze code quality and suggest improvements",
        "arguments": [
          {
            "name": "code",
            "description": "The code to review",
            "required": true
          }
        ]
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```

### Getting a Prompt

To retrieve a specific prompt, clients send a `prompts/get` request. Arguments may be
auto-completed through [the completion API](/specification/2025-06-18/server/utilities/completion).

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def hello():\n    print('world')"
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "description": "Code review prompt",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Please review this Python code:\ndef hello():\n    print('world')"
        }
      }
    ]
  }
}
```


## ToDo Exercise Update your MCP Server to add Prompts

### Adding a Format Prompt

Define a prompt that reformats a document into Markdown. For example:

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """

    return [base.UserMessage(prompt)]
```

Add another prompt to summarize a doc
```python
@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of the document."
)
def summarize_document(doc_id: str = Field(description="Id of the document to summarize")) -> list:
    from mcp.types import PromptMessage, TextContent
    prompt_text = f"""
    Your goal is to summarize the contents of the document.
    Document ID: {doc_id}
    Include a concise summary of the document's main points.
    """
    return [PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))]
```

---

## Implementing Prompt Use in MCP Client

In your MCP client, implement the following methods to support prompts:

```python
async def list_prompts(self) -> types.ListPromptsResult:
    result = await self.session().list_prompts()
    return result.prompts

async def get_prompt(self, prompt_name, args: dict[str, str]):
    result = await self.session().get_prompt(prompt_name, args)
    return result.messages
```

These methods allow the client to fetch available prompts (using the `prompts/list` endpoint) and retrieve a specific prompt with variables interpolated (using the `prompts/get` endpoint).

---

## Testing Prompts

To test your prompt implementation:

- Use the MCP Inspector to view prompt templates and verify variable interpolation.
- In the CLI, type `/` to list available prompt commands. For example, typing `/format plan.md` will fetch the formatted prompt for document `plan.md`.
- Verify that the returned messages contain the structured markdown instructions.

These additions ensure that prompts are integrated end-to-end—defined on the server, used in the client, and tested thoroughly.

## Next Steps

Now that you understand prompts, you can:

1. **Create specialized prompts**: For your specific domain or use case
2. **Build prompt chains**: Combine multiple prompts for complex workflows
3. **Add prompt validation**: Ensure prompt arguments are valid
4. **Implement prompt caching**: For better performance

In the next lesson, we'll explore how to build comprehensive MCP applications that combine tools, resources, and prompts.

## Exercises

1. **Create domain-specific prompts**: Build prompts for your industry or domain
2. **Add prompt templates**: Create reusable prompt templates with variables
3. **Implement prompt validation**: Add argument validation for prompts
4. **Build prompt workflows**: Create chains of prompts for complex tasks

## Resources

- [MCP Prompt Specification](https://modelcontextprotocol.io/specification/2025-06-18#prompts)
- [Prompt Engineering Best Practices](https://www.anthropic.com/index/prompting-guide)
- [JSON Schema Validation](https://json-schema.org/learn/getting-started-step-by-step) 