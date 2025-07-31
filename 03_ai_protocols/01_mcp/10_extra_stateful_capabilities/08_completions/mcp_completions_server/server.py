from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
    TextContent,
)

# === COMPLETION DATA ===
LANGUAGES = ["python", "javascript", "typescript", "java", "go", "rust"]
FRAMEWORKS = {
    "python": ["fastapi", "flask", "django"],
    "javascript": ["express", "react", "vue"],
    "typescript": ["nestjs", "angular", "next"]
}
GITHUB_OWNERS = ["microsoft", "google", "facebook", "openai", "anthropic"]
GITHUB_REPOS = {
    "microsoft": ["vscode", "typescript", "playwright"],
    "google": ["angular", "tensorflow", "protobuf"],
    "openai": ["openai-python", "gpt-4", "whisper"]
}

# === SERVER SETUP ===
mcp = FastMCP(
    name="mcp-completions-demo",
    description="Simple MCP completions server for learning",
)


@mcp.prompt(description="Code review with completable language")
def review_code(language: str, focus: str = "all") -> str:
    """Review code with language and focus completions."""
    return f"Please review this {language} code focusing on {focus} aspects."


@mcp.prompt(description="Project setup with context-aware framework")
def setup_project(language: str, framework: str) -> str:
    """Setup project with language and framework completions."""
    return f"Create a {language} project using {framework} framework."

# === RESOURCES ===


@mcp.resource("github://repos/{owner}/{repo}")
def github_repo(owner: str, repo: str) -> str:
    """GitHub repository with owner and repo completions."""
    return f"GitHub Repository: {owner}/{repo}\nURL: https://github.com/{owner}/{repo}"

# === COMPLETION HANDLER ===


@mcp.completion()
async def handle_completion(
    ref: PromptReference | ResourceTemplateReference,
    argument: CompletionArgument,
    context: CompletionContext | None,
) -> Completion | None:
    """Handle completion requests."""

    # === PROMPT COMPLETIONS ===
    if isinstance(ref, PromptReference):
        if ref.name == "review_code":
            if argument.name == "language":
                matches = [
                    lang for lang in LANGUAGES if lang.startswith(argument.value)]
                return Completion(values=matches, hasMore=False)
            elif argument.name == "focus":
                focuses = ["all", "security", "performance", "style"]
                matches = [f for f in focuses if f.startswith(argument.value)]
                return Completion(values=matches, hasMore=False)

        elif ref.name == "setup_project":
            if argument.name == "language":
                matches = [
                    lang for lang in LANGUAGES if lang.startswith(argument.value)]
                return Completion(values=matches, hasMore=False)
            elif argument.name == "framework":
                # Context-aware completion based on language
                if context and context.arguments:
                    language = context.arguments.get("language", "").lower()
                    if language in FRAMEWORKS:
                        frameworks = FRAMEWORKS[language]
                        matches = [
                            fw for fw in frameworks if fw.startswith(argument.value)]
                        return Completion(values=matches, hasMore=False)

    # === RESOURCE COMPLETIONS ===
    elif isinstance(ref, ResourceTemplateReference):
        if ref.uri == "github://repos/{owner}/{repo}":
            if argument.name == "owner":
                matches = [
                    owner for owner in GITHUB_OWNERS if owner.startswith(argument.value)]
                return Completion(values=matches, hasMore=False)
            elif argument.name == "repo":
                # Context-aware completion based on owner
                if context and context.arguments:
                    owner = context.arguments.get("owner", "").lower()
                    if owner in GITHUB_REPOS:
                        repos = GITHUB_REPOS[owner]
                        matches = [
                            repo for repo in repos if repo.startswith(argument.value)]
                        return Completion(values=matches, hasMore=False)

    return None

# === DEMO TOOLS ===


@mcp.tool()
def list_completion_examples() -> list[TextContent]:
    """Show completion examples for testing."""
    return [
        TextContent(
            type="text",
            text="""# MCP Completions Examples

## Prompt Completions
1. review_code.language: "py" → ["python"]
2. review_code.focus: "sec" → ["security"]
3. setup_project.language: "java" → ["javascript", "java"]
4. setup_project.framework: "fast" (with language="python") → ["fastapi"]

## Resource Completions
5. github://repos/{owner}/{repo}.owner: "micro" → ["microsoft"]
6. github://repos/{owner}/{repo}.repo: "type" (with owner="microsoft") → ["typescript"]

## Test with Postman
Use the provided collection to test these completions via HTTP endpoints.
"""
        )
    ]


# === STREAMABLE HTTP APP ===
mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
