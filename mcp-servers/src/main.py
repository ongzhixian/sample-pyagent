from fastmcp import FastMCP, Context
from services.office_lights import OfficeLightsService
from services.file_service import FileService

mcp = FastMCP("My MCP Server")
lights_service = OfficeLightsService()
file_service = FileService(root="C:/src/test-mcp-dir/data")  # Restrict all actions under ./data

# -----------------------------
# Resources
# -----------------------------
@mcp.resource("resource://building/lights")
def building_lights() -> str:
    return lights_service.get_office_lights()

# -----------------------------
# Tools: Lights
# -----------------------------

@mcp.tool(name="get_lights", description="Gets a list of lights and their current state.")
async def get_lights(ctx: Context) -> list[dict]:
    resource = await ctx.read_resource("resource://building/lights")
    return resource

@mcp.tool(name="get_state", description="Gets the state of a particular light")
async def get_state(location: str) -> bool:
    return lights_service.get_office_light(location)

@mcp.tool(name="change_state", description="Changes the state of the light")
async def change_state(location: str) -> None:
    resource = lights_service.toggle_office_lights(location)
    return resource

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
