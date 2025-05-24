import asyncio
import json
from typing import Any, Dict, Callable, Optional

class MCPServer:
    def __init__(self, host: str = "localhost", port: int = 9999):
        self.host = host
        self.port = port
        self.methods: Dict[str, Callable] = {}

    def register_method(self, name: str, handler: Callable):
        """Register a method handler."""
        self.methods[name] = handler

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connections."""
        peer = writer.get_extra_info('peername')
        print(f"New connection from {peer}")

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                try:
                    request = json.loads(data.decode())
                    method = request.get("method")
                    params = request.get("params", {})
                    request_id = request.get("id")

                    if method in self.methods:
                        result = await self.methods[method](**params)
                        response = {
                            "jsonrpc": "2.0",
                            "result": result,
                            "id": request_id
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "error": {"code": -32601, "message": f"Method {method} not found"},
                            "id": request_id
                        }

                except json.JSONDecodeError:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    }

                response_str = json.dumps(response) + "\n"
                writer.write(response_str.encode())
                await writer.drain()

        except Exception as e:
            print(f"Error handling client {peer}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"Connection closed for {peer}")

    async def start(self):
        """Start the MCP server."""
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        print(f"MCP Server running on {self.host}:{self.port}")
        
        async with server:
            await server.serve_forever()

# Example method handlers
async def echo(message: str) -> Dict[str, Any]:
    return {"message": message}

async def main():
    # Create and configure server
    server = MCPServer()
    
    # Register methods
    server.register_method("echo", echo)
    
    # Start server
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")

if __name__ == "__main__":
    asyncio.run(main()) 