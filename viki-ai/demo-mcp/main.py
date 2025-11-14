"""
Main entry point for the Demo MCP Server
"""

import asyncio
import sys
from server import mcp

def main():
    """Main entry point for the MCP server."""
    try:
        print("Starting Demo MCP Server with HTTP/SSE transport...")
        print("Server Name: Demo MCP Server")
        print("Transport: HTTP/SSE")
        print("Host: 0.0.0.0")
        print("Port: 8000")
        print("Available Tools: add_allergy, get_files, get_system_info")
        print("Available Resources: file://demo/info, file://demo/status, file://entity/definitions")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the MCP server with HTTP/SSE transport
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
            
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
