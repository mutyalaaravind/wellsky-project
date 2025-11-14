"""
Demo MCP Server using FastMCP
"""

import asyncio
from typing import Any, Dict, List
from fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("Demo MCP Server")

@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """Get basic system information.
    
    Returns:
        Dictionary containing system information
    """
    import platform
    import os
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "current_directory": os.getcwd(),
        "environment_variables_count": len(os.environ)
    }

@mcp.tool()
def get_files() -> Dict[str, Any]:
    """List the contents of files in the data/files folder.
    
    Returns:
        Dictionary containing file names and their contents
    """
    import os
    import json
    
    files_dir = "data/files"
    result = {
        "directory": files_dir,
        "files": {},
        "file_count": 0
    }
    
    try:
        if not os.path.exists(files_dir):
            result["error"] = f"Directory {files_dir} does not exist"
            return result
            
        files = os.listdir(files_dir)
        result["file_count"] = len(files)
        
        for filename in files:
            file_path = os.path.join(files_dir, filename)
            
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Try to parse as JSON if it's a .json file
                    if filename.endswith('.json'):
                        try:
                            parsed_content = json.loads(content)
                            result["files"][filename] = {
                                "type": "json",
                                "content": parsed_content,
                                "raw_content": content
                            }
                        except json.JSONDecodeError:
                            result["files"][filename] = {
                                "type": "text",
                                "content": content,
                                "error": "Invalid JSON format"
                            }
                    else:
                        result["files"][filename] = {
                            "type": "text",
                            "content": content
                        }
                        
                except Exception as e:
                    result["files"][filename] = {
                        "error": f"Could not read file: {str(e)}"
                    }
                    
    except Exception as e:
        result["error"] = f"Could not access directory: {str(e)}"
        
    return result

@mcp.tool()
def add_allergy(name: str, notes: str, id: str = None) -> Dict[str, Any]:
    """Add an allergy to the repository.
    
    Args:
        name: Name of the allergen (required)
        notes: Additional notes related to the allergen (required)
        id: Optional UUID hex formatted value (will be generated if not provided)
        
    Returns:
        Dictionary containing the result of the operation
    """
    import os
    import json
    import uuid
    import re
    from datetime import datetime
    
    # Validate UUID format if provided
    if id is not None:
        uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        if not re.match(uuid_pattern, id):
            return {
                "success": False,
                "error": "Invalid UUID format. Must be hex formatted like: 550e8400-e29b-41d4-a716-446655440000"
            }
    
    # Generate UUID if not provided
    if id is None:
        id = str(uuid.uuid4())
    
    # Validate required fields
    if not name or not name.strip():
        return {
            "success": False,
            "error": "Name is required and cannot be empty"
        }
    
    if not notes or not notes.strip():
        return {
            "success": False,
            "error": "Notes are required and cannot be empty"
        }
    
    # Create allergy object conforming to schema
    allergy = {
        "id": id,
        "name": name.strip(),
        "notes": notes.strip()
    }
    
    # Create directory structure if it doesn't exist
    allergies_dir = "data/entities/allergies"
    try:
        os.makedirs(allergies_dir, exist_ok=True)
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not create directory structure: {str(e)}"
        }
    
    # Create filename using UUID
    filename = f"{id}.json"
    file_path = os.path.join(allergies_dir, filename)
    
    # Check if file already exists
    if os.path.exists(file_path):
        return {
            "success": False,
            "error": f"Allergy with ID {id} already exists"
        }
    
    # Save allergy to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(allergy, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Allergy added successfully",
            "allergy": allergy,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not save allergy file: {str(e)}"
        }

@mcp.resource("file://demo/info")
async def get_demo_info() -> str:
    """Get information about this demo MCP server."""
    return """
# Demo MCP Server

This is a demonstration MCP server built with FastMCP.

## Available Tools:
- add_allergy: Add an allergy to the repository
- get_files: List contents of files in the data/files folder
- get_system_info: Get basic system information

## Available Resources:
- file://demo/info: This information page
- file://demo/status: Server status information
- file://entity/definitions: Entity type definitions with JSON schemas

This server demonstrates basic MCP functionality including tools and resources.
"""

@mcp.resource("file://demo/status")
async def get_server_status() -> str:
    """Get current server status."""
    import datetime
    
    status = {
        "status": "running",
        "timestamp": datetime.datetime.now().isoformat(),
        "tools_count": 3,
        "resources_count": 3
    }
    
    return f"""
# Server Status

Status: {status['status']}
Timestamp: {status['timestamp']}
Available Tools: {status['tools_count']}
Available Resources: {status['resources_count']}

Server is operational and ready to handle requests.
"""

@mcp.resource("file://entity/definitions")
async def get_entity_type_definitions() -> str:
    """Get data definitions for entities."""
    import json
    
    entity_definitions = {
        "version": "1.0",
        "description": "Entity type definitions with JSON schemas",
        "entities": {
            "allergy": {
                "type": "object",
                "description": "Represents an allergy entity with allergen information",
                "properties": {
                    "id": {
                        "type": "string",
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                        "description": "Optional. UUID hex formatted value",
                        "optional": True
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the allergen",
                        "required": True
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes related to the allergen",
                        "required": True
                    }
                },
                "required": ["name", "notes"],
                "example": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Peanuts",
                    "notes": "Severe reaction, carry EpiPen at all times"
                }
            }
        }
    }
    
    return json.dumps(entity_definitions, indent=2)

if __name__ == "__main__":
    # For HTTP/SSE transport, we need to run with specific transport
    import uvicorn
    
    # Run with HTTP transport for remote MCP server
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
