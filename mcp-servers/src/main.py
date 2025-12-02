from fastmcp import FastMCP

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

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)