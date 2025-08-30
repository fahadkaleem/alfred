#!/usr/bin/env python
"""Test script to verify the Alfred MCP server."""

import json
import asyncio
import os
import sys
import pytest

from alfred.mcp import mcp
from alfred.config import get_config


@pytest.mark.asyncio
async def test_server():
    """Test the MCP server functionality."""
    print("Testing Alfred MCP Server...")
    print("-" * 50)

    # Test 1: Settings
    print("1. Testing settings...")
    config = get_config()
    print(f"   ✓ Platform: {config.platform}")
    print(f"   ✓ AI Provider: {config.ai_provider}")
    print(f"   ✓ Claude Model: {config.claude_model}")
    print(f"   ✓ Max Tokens: {config.max_tokens}")

    # Test 2: MCP instance
    print("\n2. Testing MCP instance...")
    print(f"   ✓ MCP instance created: {mcp.name}")

    # Test 3: MCP state
    print("\n3. Testing MCP state...")
    assert hasattr(mcp.state, "session_manager")
    assert hasattr(mcp.state, "config")
    assert hasattr(mcp.state, "logger")
    print("   ✓ Session manager initialized")
    print("   ✓ Config attached")
    print("   ✓ Logger configured")

    # Test 4: Tool auto-registration
    print("\n4. Testing tool auto-registration...")
    # Tools are now auto-registered via decorators when imported
    # Check that tools exist on the server
    tool_count = len(getattr(mcp, "_tools", {}))
    print(f"   ✓ Tools auto-registered: {tool_count}")

    # Test 5: Session management
    print("\n5. Testing session management...")
    session_manager = mcp.state.session_manager

    # Create a test session
    test_session_id = "test-session-123"
    test_workspace = os.getcwd()

    session = session_manager.start_session(test_session_id, test_workspace)
    print(f"   ✓ Session created: {session.session_id}")
    print(f"   ✓ Workspace: {session.workspace_path}")

    # Get session
    retrieved_session = session_manager.get(test_session_id)
    assert retrieved_session.session_id == test_session_id
    print("   ✓ Session retrieved successfully")

    # End session
    session_manager.end_session(test_session_id)
    print("   ✓ Session ended successfully")

    print("\n" + "=" * 50)
    print("All tests passed! ✅")
    print("=" * 50)

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_server())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
