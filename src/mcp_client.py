import asyncio
import json
from typing import Any, Dict, Optional

class MCPClient:
    def __init__(self, host: str = "localhost", port: int = 9999):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def connect(self):
        """Connect to the MCP server."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        print(f"Connected to MCP server at {self.host}:{self.port}")

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP server and get the response."""
        if not self.writer or not self.reader:
            raise ConnectionError("Not connected to server")

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }

        # Send request
        request_str = json.dumps(request) + "\n"
        self.writer.write(request_str.encode())
        await self.writer.drain()

        # Get response
        response_data = await self.reader.readline()
        response = json.loads(response_data.decode())
        
        if "error" in response:
            raise Exception(f"MCP Error: {response['error']}")
        
        return response["result"]

    async def close(self):
        """Close the connection to the MCP server."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

async def main():
    # Example usage
    client = MCPClient()
    try:
        await client.connect()
        
        # Example request
        result = await client.send_request("echo", {"message": "Hello MCP!"})
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 