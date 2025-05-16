from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP(name="my-tools-server", stateless_http=True)


class AddParameters(BaseModel):
    a: int = Field(description="The first number to add")
    b: int = Field(description="The second number to add")


class AddResponse(BaseModel):
    result: int = Field(description="The sum of the two numbers")


@mcp.tool(name="calculator/add", description="Add two numbers together")
def add(parameters: AddParameters) -> AddResponse:
    """Add two numbers together.

    Args:
        a(int): The first number to add
        b(int): The second number to add

    Returns:
        AddResponse: The sum of the two numbers
    """
    return AddResponse(result=parameters.a + parameters.b)


@mcp.tool(name="forecast", description="Get weather forecast for a city")
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    return f"The weather in {city} will be warm and sunny"

# --- Tool 3: Dummy Data Manager - Delete Item (Demonstrates ToolAnnotations) ---
class DeleteItemParameters(BaseModel):
    item_id: str = Field(description="The ID of the dummy item to delete.")
    confirm: bool = Field(
        default=False, description="Confirmation flag to proceed with deletion.")


class DeleteItemResponse(BaseModel):
    status: str = Field(description="The status of the delete operation.")
    message: str = Field(description="A message detailing the outcome.")


@mcp.tool(
    name="dummy_data_manager/delete_item",
    description="Simulates deleting a dummy item by its ID. This tool demonstrates various annotations.",
    annotations=ToolAnnotations(
        title="Delete Dummy Item",
        readOnlyHint=False,  # This tool modifies (simulated) state
        destructiveHint=True,  # This tool simulates a destructive action
        # Calling it again for the same ID after success would be different (e.g., item not found)
        idempotentHint=False,
        openWorldHint=False,  # Operates on a known, internal dummy dataset
        # Example of a custom annotation if your ToolAnnotations model supports 'extra="allow"'
        # and your client/host knows how to interpret it:
        # custom_RequiresPrivilegeLevel="admin"
    )
)
async def delete_dummy_item(params: DeleteItemParameters) -> DeleteItemResponse:
    """
    Simulates deleting a dummy item.

    This tool is intended to showcase how ToolAnnotations can describe
    a tool's behavior, such as being non-read-only and destructive.
    It requires confirmation to proceed.
    """
    if not params.confirm:
        return DeleteItemResponse(
            status="aborted",
            message="Deletion aborted. Confirmation not provided."
        )

    # In a real scenario, you would interact with a database or state store here.
    # For this example, we'll just simulate success.
    print(f"[Server Log] Simulating deletion of item: {params.item_id}")

    return DeleteItemResponse(
        status="success",
        message=f"Successfully simulated deletion of item '{params.item_id}'. (This is a simulation)"
    )