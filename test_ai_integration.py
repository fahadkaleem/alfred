#!/usr/bin/env python3
"""Integration test for AI services with actual Anthropic API."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from alfred.ai_services import (
    AIService,
    AIProvider,
    get_config,
    get_provider,
    AuthenticationError,
)


async def test_anthropic_integration():
    """Test AI services with actual Anthropic API."""

    # Load environment variables
    load_dotenv()

    # Check if API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False

    print(f"✅ Found ANTHROPIC_API_KEY: {api_key[:10]}...")

    try:
        # Test 1: Provider initialization
        print("\n🧪 Test 1: Initializing Anthropic provider...")
        provider = get_provider(AIProvider.ANTHROPIC)
        print(f"✅ Provider initialized: {provider.provider_name.value}")
        print(f"   Model: {provider.model}")

        # Test 2: Initialize AI Service
        print("\n🧪 Test 2: Initializing AI service...")
        ai_service = AIService(provider=AIProvider.ANTHROPIC)
        print("✅ AI service initialized")

        # Test 3: Simple completion
        print("\n🧪 Test 3: Testing simple completion...")
        response = await provider.complete(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, Alfred AI is working!' and nothing else.",
                }
            ],
            max_tokens=50,
            temperature=0.1,
        )
        print(f"✅ Response: {response.text}")
        print(f"   Tokens used: {response.usage.total_tokens}")

        # Test 4: Create tasks from spec
        print("\n🧪 Test 4: Creating tasks from specification...")
        spec = """
        Build a simple todo list web application with the following features:
        - User can add new todos
        - User can mark todos as complete
        - User can delete todos
        - Data persists in local storage
        """

        tasks = await ai_service.create_tasks_from_spec(spec_content=spec, num_tasks=3)

        print(f"✅ Generated {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"\n   Task {i}: {task.get('title', 'Untitled')}")
            print(f"   Priority: {task.get('priority', 'N/A')}")
            print(f"   Complexity: {task.get('complexity', 'N/A')}")

        # Test 5: Decompose a task
        print("\n🧪 Test 5: Decomposing a task...")
        if tasks:
            first_task = tasks[0]
            subtasks = await ai_service.decompose_task(task=first_task, num_subtasks=2)

            print(
                f"✅ Generated {len(subtasks)} subtasks for '{first_task.get('title', 'Task')}':"
            )
            for i, subtask in enumerate(subtasks, 1):
                print(f"   Subtask {i}: {subtask.get('title', 'Untitled')}")

        # Test 6: Assess complexity
        print("\n🧪 Test 6: Assessing task complexity...")
        complexity = await ai_service.assess_complexity(
            task="Implement OAuth 2.0 authentication with Google and GitHub providers"
        )

        print(f"✅ Complexity assessment:")
        print(f"   Score: {complexity.get('complexity_score', 'N/A')}/10")
        print(f"   Risk level: {complexity.get('risk_level', 'N/A')}")
        print(f"   Estimated hours: {complexity.get('estimated_hours', 'N/A')}")
        print(f"   Should decompose: {complexity.get('should_decompose', 'N/A')}")

        # Test 7: Research query
        print("\n🧪 Test 7: Testing research functionality...")
        research = await ai_service.research(
            query="What are the best practices for implementing rate limiting in a REST API?",
            detail_level="low",
        )

        if isinstance(research, dict):
            print(f"✅ Research completed:")
            print(f"   Summary: {research.get('summary', 'N/A')[:100]}...")
            insights = research.get("key_insights", [])
            if insights:
                print(f"   Found {len(insights)} key insights")
        else:
            print(f"✅ Research response: {research[:200]}...")

        # Test 8: Streaming (basic test)
        print("\n🧪 Test 8: Testing streaming response...")
        messages = [{"role": "user", "content": "Count from 1 to 5 slowly."}]

        print("✅ Streaming response: ", end="", flush=True)
        full_text = []
        async for event in provider.stream_complete(messages, max_tokens=100):
            if event.type == "text" and event.data:
                print(event.data, end="", flush=True)
                full_text.append(event.data)
            elif event.type == "message_end":
                print(
                    f"\n   Stream completed. Tokens: {event.usage.total_tokens if event.usage else 'N/A'}"
                )

        # Test 9: Token counting
        print("\n🧪 Test 9: Testing token counting...")
        test_text = "This is a test sentence to count tokens. It should be roughly 10-15 tokens."
        token_count = provider.count_tokens(test_text)
        print(f"✅ Token count for test text: {token_count}")

        # Test 10: Usage summary
        print("\n🧪 Test 10: Getting usage summary...")
        usage = ai_service.get_usage_summary()
        print(f"✅ Total usage across all requests:")
        print(f"   Input tokens: {usage['total_input_tokens']}")
        print(f"   Output tokens: {usage['total_output_tokens']}")
        print(f"   Total tokens: {usage['total_tokens']}")
        print(f"   Estimated cost: ${usage['estimated_cost']}")

        print("\n" + "=" * 60)
        print("🎉 All tests passed successfully!")
        print("=" * 60)
        return True

    except AuthenticationError as e:
        print(f"\n❌ Authentication error: {e}")
        print("   Please check your ANTHROPIC_API_KEY in .env")
        return False
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🚀 Alfred AI Services Integration Test")
    print("=" * 60)

    success = await test_anthropic_integration()

    if success:
        print("\n✅ Integration test completed successfully!")
        print("   The AI services are working correctly with the Anthropic API.")
    else:
        print("\n❌ Integration test failed.")
        print("   Please check the error messages above.")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
