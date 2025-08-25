#!/usr/bin/env python3
"""Dynamic prompt instruction appender based on YAML configuration."""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML not installed. Install with: pip install PyYAML", file=sys.stderr
    )
    sys.exit(1)


def load_config() -> Dict[str, str]:
    """Load prompt flags configuration from YAML file."""
    config_path = Path(__file__).parent / "prompt-config.yaml"

    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}", file=sys.stderr)
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        # Validate config structure
        if not isinstance(config, dict):
            print(
                "Error: Config must be a dictionary of flag: instruction pairs",
                file=sys.stderr,
            )
            return {}

        # Filter out non-string values and empty keys
        valid_config = {
            str(flag): str(instruction)
            for flag, instruction in config.items()
            if flag
            and instruction
            and isinstance(flag, (str, int, float))
            and isinstance(instruction, str)
        }

        return valid_config

    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return {}


def find_matching_flag(prompt: str, flags: Dict[str, str]) -> Optional[str]:
    """Find the matching flag in the prompt, checking longest flags first."""
    prompt = prompt.rstrip()

    # Sort flags by length (longest first) to handle overlapping flags correctly
    # e.g., -thh should be matched before -th
    sorted_flags = sorted(flags.keys(), key=len, reverse=True)

    for flag in sorted_flags:
        if prompt.endswith(f"-{flag}"):
            return flags[flag]

    return None


def main() -> None:
    """Main hook execution function."""
    try:
        # Load configuration
        config = load_config()
        if not config:
            # Silent exit if no config - hook becomes a no-op
            return

        # Read JSON payload from stdin
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)

        prompt = input_data.get("prompt", "")
        if not isinstance(prompt, str):
            print("Error: Prompt must be a string", file=sys.stderr)
            return

        # Find matching flag and append instruction
        instruction = find_matching_flag(prompt, config)
        if instruction:
            print(f"\n{instruction}")

    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Hook execution error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
