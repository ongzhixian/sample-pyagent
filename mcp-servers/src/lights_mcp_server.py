import os
from fastmcp import FastMCP, Context
from services.office_lights import OfficeLightsService

lights_service = OfficeLightsService()

mcp = FastMCP('Light MCP Server')

@mcp.resource('resource://building/lights')
def building_lights() -> dict:
    return lights_service.get_office_lights()

@mcp.tool(name="get_lights", description="Gets the state of a particular light",
          tags=["lighting", "status"],
          meta={"version": "1.0", "author": "Light Team"})
async def get_lights(ctx: Context) -> list:
    resource = await ctx.read_resource('resource://building/lights')
    return resource

@mcp.tool(name="get_state", description="Gets the state of a particular light",
          tags=["lighting", "status"],
          meta={"version": "1.0", "author": "Light Team"})
async def get_state(location: str) -> bool:
    return lights_service.get_office_light(location)

@mcp.tool(name="change_state", description="Changes the state of the light",
          tags=["lighting", "status"],
          meta={"version": "1.0", "author": "Light Team"})
async def change_state(location: str) -> None:
    resource = lights_service.toggle_office_lights(location)
    return resource


@mcp.tool(name="read_file", 
          description="Read the contents of a file from local file system.",
          tags=["file", "read", "filesystem"],
          meta={"version": "1.0", "author": "Light Team"})
async def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError as e:
        return f"File not found: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool(name="list_files", 
          description="List files in a directory on the local file system.",
          tags=["file", "list", "filesystem"],
          meta={"version": "1.0", "author": "Light Team"})
async def list_files(directory_path: str) -> str:
    try:
        return os.listdir(directory_path)
    except FileNotFoundError as e:
        return f"Directory not found: {str(e)}"
    except Exception as e:
        return f"Error listing files: {str(e)}"




# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
