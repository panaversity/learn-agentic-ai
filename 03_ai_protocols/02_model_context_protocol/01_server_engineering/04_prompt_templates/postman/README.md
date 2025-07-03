# 💬 MCP Prompt Templates - Postman Collection

This Postman collection demonstrates how to test an MCP server with **prompt templates**. You'll learn how to discover and generate structured prompts for AI interactions, understanding the difference between simple and complex prompt templates.

## 🎯 What You'll Learn

- **Prompt Template Discovery**: How to find available prompt templates on a server
- **Simple Prompts**: Single-message prompts that return formatted strings
- **Complex Prompts**: Multi-message prompts that create conversation structures
- **ChatML Format**: Understanding the message structure used by AI systems
- **Parameter Handling**: How to pass arguments to prompt templates
- **Error Handling**: What happens when prompt generation goes wrong

## 🚀 Quick Start

### 1. Start the Server
```bash
cd 03_ai_protocols/02_model_context_protocol/01_server_development/04_prompt_templates/my_prompts_server
uvicorn server:mcp_app --host 0.0.0.0 --port 8000
```

### 2. Import Collection
- Open Postman
- Click **Import** → **Upload Files**
- Select `MCP_Prompt_Templates.postman_collection.json`

### 3. Run the Requests
Start with **"01. Discover Available Prompts"** and work your way through!

## 🔍 Understanding the Requests

### 1. Prompt Discovery
**Purpose**: Find out what prompt templates the server provides

**What to expect**:
- Server returns list of available prompt templates
- Each template includes name, description, and parameter schema
- Should see `summarize` and `debug_error` templates

### 2. Simple Prompt Tests (`summarize`)
**Purpose**: Test prompts that return a single formatted message

**Template**: `summarize`
- **Input**: Text to be summarized
- **Output**: Single user message with summarization request
- **Use Cases**: Content summarization, text analysis, simple formatting

**Variations**:
- **Short Text**: Simple sentences and paragraphs
- **Long Text**: Complex technical content
- **Code Content**: Programming code and scripts

### 3. Complex Prompt Tests (`debug_error`)
**Purpose**: Test prompts that return multiple messages for conversations

**Template**: `debug_error`
- **Input**: Error message and code snippet
- **Output**: Multiple messages setting up a debugging conversation
- **Use Cases**: Technical support, troubleshooting, multi-turn conversations

**Variations**:
- **TypeError**: Null reference and type-related errors
- **IndexError**: Array bounds and indexing issues
- **ImportError**: Module and dependency problems
- **SyntaxError**: Code formatting and syntax issues

### 4. Error Scenarios
**Purpose**: Understand how the server handles invalid requests

**Error Types**:
- **Invalid Template Names**: Requesting non-existent prompts
- **Missing Parameters**: Forgetting required arguments
- **Partial Parameters**: Providing incomplete argument sets

## 📋 Request Details

| Request | Template | Input Type | Purpose | Expected Output |
|---------|----------|------------|---------|----------------|
| **01** | Discovery | - | List templates | 2 prompt templates |
| **02** | `summarize` | Short text | Basic summarization | Single user message |
| **03** | `summarize` | Long text | Complex summarization | Single user message |
| **04** | `summarize` | Code | Code summarization | Single user message |
| **05** | `debug_error` | TypeError | Debug conversation | Multiple messages |
| **06** | `debug_error` | IndexError | Debug conversation | Multiple messages |
| **07** | `debug_error` | ImportError | Debug conversation | Multiple messages |
| **08** | `debug_error` | SyntaxError | Debug conversation | Multiple messages |
| **09** | Error | Invalid name | Error handling | Error response |
| **10** | Error | Missing param | Error handling | Validation error |
| **11** | Error | Partial params | Error handling | Validation error |
| **12** | Edge case | Empty text | Edge case | Valid prompt structure |

## 🎓 Learning Path

### For Beginners
1. **Start with Discovery**: Run request #01 to see available templates
2. **Try Simple Prompts**: Run requests #02-#04 to understand basic prompt generation
3. **Explore Complex Prompts**: Run requests #05-#08 to see multi-message structures
4. **Learn from Errors**: Run requests #09-#12 to understand error handling

### For Advanced Users
1. **Analyze Message Structures**: Study the ChatML format in responses
2. **Compare Template Types**: Notice differences between simple and complex prompts
3. **Test Edge Cases**: Try unusual inputs and parameter combinations
4. **Create Custom Tests**: Modify parameters to test your own scenarios

## 🔧 Key Concepts Explained

### Prompt Templates vs Direct Prompting
- **Templates**: Reusable, parameterized prompt structures
- **Direct**: One-off, manually crafted prompts
- **Benefits**: Consistency, maintainability, standardization

### ChatML Message Format
```json
{
  "role": "user|assistant|system",
  "content": [
    {
      "type": "text",
      "text": "The actual message content"
    }
  ]
}
```

### Template Types
- **Simple**: Return string → Single user message
- **Complex**: Return message list → Multi-message conversation

### Message Roles
- **System**: Sets AI persona and behavior
- **User**: Human input and requests
- **Assistant**: AI responses and clarifications

## 🔧 Customization Tips

### Testing Different Content Types
**For Summarize Template**:
- Try different text lengths and complexities
- Test with various content types (articles, code, data)
- Experiment with different languages or formats

**For Debug Error Template**:
- Use real error messages from your development work
- Try different programming languages and error types
- Test with various code complexity levels

### Creating New Test Cases
1. Duplicate an existing request
2. Modify the arguments in the request body
3. Update the description to match your test
4. Run and analyze the results

### Analyzing Responses
- **Simple Prompts**: Look at the formatted text structure
- **Complex Prompts**: Count messages and analyze conversation flow
- **Error Cases**: Study error codes and validation messages

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Connection refused** | Make sure server is running on port 8000 |
| **404 Not Found** | Check the URL path is `/mcp` |
| **Template not found** | Verify template name matches exactly |
| **Invalid JSON** | Check request body syntax |
| **Parameter errors** | Ensure all required parameters are provided |

### Expected Error Responses
- **Invalid template**: `{"error": {"code": -32601, "message": "Method not found"}}`
- **Missing parameter**: Validation error with parameter details
- **Partial parameters**: Error indicating which parameters are missing

## 🎯 Success Criteria

You've mastered this collection when you can:
- ✅ Discover all available prompt templates and understand their schemas
- ✅ Successfully generate simple prompts with various text inputs
- ✅ Successfully generate complex prompts with multiple parameters
- ✅ Understand the ChatML message format and structure
- ✅ Handle and interpret error responses
- ✅ Explain when to use simple vs complex prompt templates

## 💡 Real-World Applications

### Simple Prompt Templates
- **Content Summarization**: Articles, reports, documentation
- **Text Analysis**: Sentiment analysis, keyword extraction
- **Format Conversion**: Markdown to HTML, data transformation
- **Translation**: Language conversion with context

### Complex Prompt Templates
- **Technical Support**: Multi-step troubleshooting conversations
- **Educational Tutoring**: Step-by-step learning interactions
- **Code Review**: Structured feedback and improvement suggestions
- **Interview Preparation**: Question-answer conversation flows

## 🔗 Next Steps

After completing this collection:
1. **Combine Features**: Try servers with tools, resources, AND prompts
2. **Build Your Own**: Create custom prompt templates for your use cases
3. **Advanced Patterns**: Learn about prompt chaining and composition
4. **AI Integration**: Use generated prompts with actual AI models

## 📚 Additional Resources

- [MCP Specification - Prompts](https://spec.modelcontextprotocol.io/specification/basic/prompts/)
- [ChatML Format Documentation](https://github.com/openai/openai-python/blob/main/chatml.md)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering) 