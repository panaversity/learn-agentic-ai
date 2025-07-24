from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Prompt Server", stateless_http=True, json_response=True)


# Instruction-generating prompts (user-controlled)
@mcp.prompt()
def generate_code_review_instructions(
    focus: str = "general code quality", language: str = "python"
) -> str:
    """Generate agent instructions for code review tasks"""
    print(f"[debug-server] generate_code_review_instructions({focus}, {language})")

    return f"""You are a senior {language} code review specialist. Your role is to provide comprehensive code analysis with focus on {focus}.

INSTRUCTIONS:
- Analyze code for quality, security, performance, and best practices
- Provide specific, actionable feedback with examples
- Identify potential bugs, vulnerabilities, and optimization opportunities
- Suggest improvements with code examples when applicable
- Be constructive and educational in your feedback
- Focus particularly on {focus} aspects

RESPONSE FORMAT:
1. Overall Assessment
2. Specific Issues Found
3. Security Considerations
4. Performance Notes
5. Recommended Improvements
6. Best Practices Suggestions

Use the available tools to check current time if you need timestamps for your analysis."""

streamable_http_app = mcp.streamable_http_app()

if __name__ == "__main__":
    port = 8001
    import uvicorn
    uvicorn.run("server:streamable_http_app", host="0.0.0.0", port=port, reload=True)

