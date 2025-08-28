#!/usr/bin/env python3
"""Test the refactored workflow state discovery with proper architecture."""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alfred.clients.linear import LinearClient
from alfred.config import get_config
from alfred.adapters.linear_adapter import LinearAdapter


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print("=" * 60)


def test_workflow_manager():
    """Test the WorkflowStateManager through LinearClient."""
    print_section("Testing WorkflowStateManager")

    config = get_config()
    if not config.linear_api_key:
        print("❌ LINEAR_API_KEY not found")
        return

    try:
        # Initialize Linear client directly
        client = LinearClient(api_key=config.linear_api_key)
        print("✅ LinearClient initialized")

        # Get team ID
        team_id = config.team_id
        if not team_id:
            teams = client.teams.get_all()
            if teams:
                team_id = list(teams.keys())[0]
                print(f"ℹ️ Using first available team: {team_id}")
            else:
                print("❌ No teams found")
                return
        else:
            print(f"✅ Using configured team: {team_id}")

        # Test workflow state discovery
        print("\nDiscovering workflow states...")
        team_states = client.workflow_states.discover_team_states(team_id)

        print(f"\nTeam: {team_states.team_name} (ID: {team_states.team_id})")
        print(f"States found: {len(team_states.states)}")
        print(f"Discovered at: {team_states.discovered_at}")

        print("\nStates by type:")
        for state_type, states in team_states.states_by_type.items():
            state_names = [s.name for s in states]
            print(f"  {state_type}: {', '.join(state_names)}")

        print("\nAlfred Status Mappings:")
        for alfred_status, linear_states in team_states.alfred_mappings.items():
            print(
                f"  {alfred_status} → {', '.join(linear_states) if linear_states else '(none)'}"
            )

        # Test status mapping
        print("\nTesting status mapping:")
        test_statuses = ["pending", "in_progress", "done", "cancelled"]
        for status in test_statuses:
            linear_state = team_states.get_linear_state_for_alfred(status)
            print(f"  Alfred '{status}' → Linear '{linear_state}'")

        # Test reverse mapping
        print("\nTesting reverse mapping:")
        test_linear = ["Backlog", "In Progress", "Done", "Canceled"]
        for linear_name in test_linear:
            alfred_status = team_states.get_alfred_status_for_linear(linear_name)
            print(f"  Linear '{linear_name}' → Alfred '{alfred_status}'")

        return team_states

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def test_adapter_integration():
    """Test that LinearAdapter still works with the refactored code."""
    print_section("Testing LinearAdapter Integration")

    config = get_config()
    if not config.linear_api_key:
        print("❌ LINEAR_API_KEY not found")
        return

    try:
        # Initialize adapter
        adapter = LinearAdapter(api_token=config.linear_api_key)
        print("✅ LinearAdapter initialized")

        # Test the get_workflow_states method
        print("\nTesting adapter.get_workflow_states()...")
        result = adapter.get_workflow_states(team_id=config.team_id)

        print(f"Team: {result['team_name']}")
        print(f"States: {len(result['states'])}")
        print(f"State names: {', '.join(result['state_names'][:5])}...")

        if "alfred_mappings" in result:
            print("\n✅ Alfred mappings included in adapter response")
        else:
            print("\n⚠️ Alfred mappings not included in adapter response")

        return result

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def test_caching():
    """Test that caching works properly."""
    print_section("Testing Cache Functionality")

    config = get_config()
    if not config.linear_api_key:
        print("❌ LINEAR_API_KEY not found")
        return

    try:
        client = LinearClient(api_key=config.linear_api_key)
        team_id = config.team_id or list(client.teams.get_all().keys())[0]

        # First call - should hit API
        print("First call (should hit API)...")
        start = datetime.now()
        result1 = client.workflow_states.discover_team_states(team_id)
        time1 = (datetime.now() - start).total_seconds()
        print(f"  Time: {time1:.2f}s")

        # Second call - should use cache
        print("Second call (should use cache)...")
        start = datetime.now()
        result2 = client.workflow_states.discover_team_states(team_id)
        time2 = (datetime.now() - start).total_seconds()
        print(f"  Time: {time2:.2f}s")

        if time2 < time1 / 2:
            print("✅ Cache appears to be working (second call was faster)")
        else:
            print("⚠️ Cache may not be working (similar times)")

        # Force refresh
        print("Third call with force_refresh=True...")
        start = datetime.now()
        result3 = client.workflow_states.discover_team_states(
            team_id, force_refresh=True
        )
        time3 = (datetime.now() - start).total_seconds()
        print(f"  Time: {time3:.2f}s")

        if time3 > time2:
            print("✅ Force refresh working (took longer than cached call)")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print(" REFACTORED WORKFLOW STATE DISCOVERY TEST")
    print("=" * 60)

    # Test the workflow manager
    workflow_result = test_workflow_manager()

    # Test adapter integration
    adapter_result = test_adapter_integration()

    # Test caching
    test_caching()

    # Save results
    if workflow_result or adapter_result:
        print_section("Saving Test Results")

        output_dir = Path(__file__).parent / "test_results"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if workflow_result:
            workflow_file = output_dir / f"refactored_workflow_{timestamp}.json"
            with open(workflow_file, "w") as f:
                json.dump(workflow_result.model_dump(), f, indent=2, default=str)
            print(f"✅ Workflow results saved to: {workflow_file}")

        if adapter_result:
            adapter_file = output_dir / f"refactored_adapter_{timestamp}.json"
            with open(adapter_file, "w") as f:
                json.dump(adapter_result, f, indent=2, default=str)
            print(f"✅ Adapter results saved to: {adapter_file}")

    print("\n" + "=" * 60)
    print(" TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
