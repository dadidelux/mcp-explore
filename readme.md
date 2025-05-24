# Local MCP Project

This is a basic implementation of a Model Control Protocol (MCP) server and client in Python. The project demonstrates how to create a simple MCP server that can handle requests from clients using JSON-RPC 2.0 protocol.

## Project Structure

```
src/
├── mcp_server.py  - MCP server implementation
└── mcp_client.py  - MCP client implementation
```

## Getting Started

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Start the MCP server:
```bash
python src/mcp_server.py
```

3. In a separate terminal, run the client example:
```bash
python src/mcp_client.py
```

## Features

- JSON-RPC 2.0 protocol implementation
- Async/await based server and client
- Method registration system
- Error handling
- Example echo method implementation

## Example Usage

The current implementation includes an example "echo" method. The server will respond to client requests by echoing back the message sent.

### Adding New Methods

To add new methods to the server, define a handler function and register it with the server:

```python
async def my_method(param1: str, param2: int) -> Dict[str, Any]:
    # Implementation here
    return {"result": "some result"}

server = MCPServer()
server.register_method("my_method", my_method)
```

### Making Client Requests

```python
client = MCPClient()
await client.connect()
result = await client.send_request("my_method", {"param1": "value", "param2": 42})
```

## Configuration

Both server and client can be configured with custom host and port:

```python
server = MCPServer(host="0.0.0.0", port=8888)
client = MCPClient(host="localhost", port=8888)
```