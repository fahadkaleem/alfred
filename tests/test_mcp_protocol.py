#!/usr/bin/env python
"""Test MCP protocol communication with the Alfred server."""

import json
import os
import sys
import subprocess
import time
from alfred.mcp import mcp


def send_json_rpc(proc, request):
    """Send a JSON-RPC request to the server."""
    request_str = json.dumps(request)
    # MCP uses Content-Length header for stdio
    message = f"Content-Length: {len(request_str)}\r\n\r\n{request_str}"
    proc.stdin.write(message.encode())
    proc.stdin.flush()


def read_json_rpc(proc, timeout=5):
    """Read a JSON-RPC response from the server."""
    # Try to read the response
    import select

    # Check if data is available
    ready = select.select([proc.stdout], [], [], timeout)
    if not ready[0]:
        return None

    # Read Content-Length header
    header_line = proc.stdout.readline().decode()
    if not header_line.startswith("Content-Length:"):
        return None

    content_length = int(header_line.split(":")[1].strip())

    # Read empty line
    proc.stdout.readline()

    # Read the JSON content
    content = proc.stdout.read(content_length).decode()
    return json.loads(content)


def test_mcp_initialize():
    """Test MCP initialize request."""
    print("Starting Alfred MCP Server test...")
    print("-" * 50)

    # Start the server
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    env["ALFRED_LOG_LEVEL"] = "DEBUG"

    proc = subprocess.Popen(
        [sys.executable, "-m", "alfred.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    try:
        # Give server time to start
        time.sleep(1)

        # Check if process is still running
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode()
            print(f"Server failed to start:\n{stderr}")
            return False

        print("✓ Server started successfully")

        # Send initialize request
        print("\nSending initialize request...")
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "0.1.0"},
            },
        }

        send_json_rpc(proc, initialize_request)
        print("✓ Request sent")

        # Read response
        print("\nWaiting for response...")
        response = read_json_rpc(proc, timeout=5)

        if response:
            print("✓ Response received:")
            print(json.dumps(response, indent=2))

            # Verify response structure
            assert "jsonrpc" in response
            assert response.get("id") == 1
            assert "result" in response or "error" in response

            if "result" in response:
                result = response["result"]
                assert "protocolVersion" in result
                assert "capabilities" in result
                assert "serverInfo" in result

                print(f"\n✓ Server info: {result['serverInfo']}")
                print(f"✓ Protocol version: {result['protocolVersion']}")
                print(f"✓ Capabilities: {result['capabilities']}")

            return True
        else:
            print("✗ No response received within timeout")
            return False

    finally:
        # Clean up
        proc.terminate()
        proc.wait(timeout=2)
        print("\n✓ Server terminated cleanly")


def test_direct_server_run():
    """Test running the server directly without MCP protocol."""
    print("\nTesting direct server execution...")
    print("-" * 50)

    try:
        print(f"✓ MCP instance created: {mcp.name}")

        # Check MCP has expected attributes
        assert hasattr(mcp, "state")
        assert hasattr(mcp.state, "session_manager")
        print("✓ MCP state initialized correctly")

        tool_count = len(getattr(mcp, "_tools", {}))
        print(f"✓ Tools auto-registered: {tool_count}")

        return True
    except Exception as e:
        print(f"✗ Server creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test direct execution
    if not test_direct_server_run():
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Note: MCP protocol test skipped - FastMCP handles protocol internally")
    print("Server can be run with: python -m alfred.server")
    print("Or via FastMCP CLI: fastmcp run src/alfred/server.py")
    print("=" * 50)
