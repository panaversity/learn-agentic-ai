# client/http_client.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Define the MCP server endpoint URL
SERVER_MCP_ENDPOINT_URL = "http://localhost:8000/mcp"

# WELCOME_MSG_URI for client-side checks, must match server definition
WELCOME_MSG_URI = "app:///messages/welcome"


async def run_http_client():
    print(
        f"Starting MCP HTTP client to connect to {SERVER_MCP_ENDPOINT_URL}...")
    try:
        async with streamablehttp_client(SERVER_MCP_ENDPOINT_URL) as (read_stream, write_stream, _):
            print("Streamable HTTP client connected to server.")
            async with ClientSession(read_stream, write_stream, sampling_callback=None) as session:
                print("ClientSession created. Initializing...")
                init_response = await session.initialize()
                print(
                    f"Initialization successful. Server: {init_response.serverInfo.name} v{init_response.serverInfo.version}")
                print(f"Server Capabilities: {init_response.capabilities}")
                print("-" * 30)

                # 1. List and Call a Tool
                print("Listing tools...")
                tools = await session.list_tools()
                if not tools.tools:
                    print("No tools found on server.")
                else:
                    print(
                        f"Available tools: {[tool.name for tool in tools.tools]}")
                    greet_tool_info = next(
                        (t for t in tools.tools if t.name == "greet"), None)
                    if greet_tool_info:
                        print("\nCalling 'greet' tool with default param...")
                        result_default = await session.call_tool("greet")
                        print(f"Tool 'greet' (default) responded: {result_default.content[0].text}")

                        print("\nCalling 'greet' tool with param 'User'...")
                        result_user = await session.call_tool("greet", arguments={"name": "User"})
                        print(
                            f"Tool 'greet' ('User') responded: {result_user.content[0].text}")
                    else:
                        print("Tool 'greet' not found.")
                print("-" * 30)

                # 2. List and Read a Resource
                print("Listing resources...")
                resources_list = await session.list_resources()
                if not resources_list.resources:
                    print("No resources found on server.")
                else:
                    print(
                        f"Available resources (names only): {[res.name for res in resources_list.resources if res.name]}")

                    # Find the resource by its URI, ensuring URI is treated as a string for comparison
                    welcome_res_info = next(
                        (r for r in resources_list.resources if r.uri and str(
                            r.uri) == WELCOME_MSG_URI),
                        None
                    )

                    if welcome_res_info:
                        # Ensure URI is treated as string for display/use if it's an AnyUrl object
                        display_uri = str(
                            welcome_res_info.uri) if welcome_res_info.uri else "N/A"
                        print(
                            f"\nReading resource: {welcome_res_info.name} ({display_uri})...")

                        # Use the client-side WELCOME_MSG_URI for reading, as it's a confirmed string.
                        # Alternatively, could use str(welcome_res_info.uri) if confident it's always populated.
                        resource_data = await session.read_resource(WELCOME_MSG_URI)

                        if resource_data.contents and hasattr(resource_data.contents[0], 'text'):
                            print(
                                f"Resource content: {resource_data.contents[0].text}")
                            print(
                                f"Resource MIME type: {resource_data.contents[0].mimeType}")
                        else:
                            print(
                                f"Could not read or parse text content from {WELCOME_MSG_URI}")
                    else:
                        print(
                            f"Resource with URI '{WELCOME_MSG_URI}' not found in the listed resources.")
                print("-" * 30)

                # 3. List and Get a Prompt
                print("Listing prompts...")
                prompts_list = await session.list_prompts()
                if not prompts_list.prompts:
                    print("No prompts found on server.")
                else:
                    print(
                        f"Available prompts: {[p.name for p in prompts_list.prompts]}")
                    simple_question_prompt_info = next(
                        (p for p in prompts_list.prompts if p.name == "simple_question"), None)

                    if simple_question_prompt_info:
                        print(
                            "\nGetting 'simple_question' prompt with default param...")
                        prompt_response_default = await session.get_prompt("simple_question")
                        print(
                            f"Prompt 'simple_question' (default) messages: {prompt_response_default.messages}")

                        print(
                            "\nGetting 'simple_question' prompt with entity 'the moon'...")
                        prompt_response_moon = await session.get_prompt("simple_question", arguments={"entity": "the moon"})
                        print(
                            f"Prompt 'simple_question' ('the moon') messages: {prompt_response_moon.messages}")
                    else:
                        print("Prompt 'simple_question' not found.")

                print("-" * 30)
                print("HTTP Client operations complete.")

    except ConnectionRefusedError:
        print(
            f"Error: Connection refused. Ensure the MCP server is running at {SERVER_MCP_ENDPOINT_URL}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_http_client())
