from fastmcp import FastMCP, Context

from services.office_lights import OfficeLightsService

mcp = FastMCP("My MCP Server")
lights_service = OfficeLightsService()

@mcp.resource("resource://building/lights")
def building_lights() -> str:
    """Provides a simple greeting message."""
    return lights_service.get_office_lights()
    # return "Hello from FastMCP Resources!"

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool(
    name="get_lights",
    description="Get lights.", # Custom description
    tags={"catalog", "search"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "product-team"}  # Custom metadata
)
async def get_lights(ctx: Context) -> list[dict]:
    resource = await ctx.read_resource("resource://building/lights")
    return resource
    # print(f"Searching for '{query}' in category '{category}'")
    # return [{"id": 2, "name": "Another Product"}]

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)