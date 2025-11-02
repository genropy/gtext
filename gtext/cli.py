"""Command-line interface for gtext."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from gtext import __version__
from gtext.config import Config
from gtext.processor import TextProcessor


def cast_command(args) -> int:
    """Execute the cast command (process single file).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        processor = TextProcessor()

        if args.dry_run:
            # Dry run: print to stdout
            result = processor.process_string(
                Path(args.input).read_text(encoding="utf-8"),
                context={"input_path": Path(args.input)},
            )
            print(result)
        else:
            # Normal processing
            processor.process_file(args.input, args.output)

            if args.output:
                print(f"✓ Processed {args.input} → {args.output}")
            else:
                # Auto-detected output
                output = str(args.input)[:-6] if args.input.endswith(".gtext") else args.input
                print(f"✓ Processed {args.input} → {output}")

        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cast_all_command(args) -> int:
    """Execute the cast-all command (process multiple files).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import glob

    processor = TextProcessor()
    errors = 0
    processed = 0

    for pattern in args.patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if Path(file_path).is_file():
                try:
                    processor.process_file(file_path)
                    output = str(file_path)[:-6] if file_path.endswith(".gtext") else file_path
                    print(f"✓ {file_path} → {output}")
                    processed += 1
                except Exception as e:
                    print(f"✗ ERROR processing {file_path}: {e}", file=sys.stderr)
                    errors += 1

    print(f"\nProcessed {processed} file(s), {errors} error(s)")
    return 1 if errors > 0 else 0


def apikey_command(args) -> int:
    """Execute the apikey command (manage API keys).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    config = Config()

    # Subcommand: list
    if args.apikey_action == "list":
        providers = config.list_providers()
        if not providers:
            print("No API keys configured.")
            print("\nTo add a key:")
            print("  gtext apikey set <provider> <key>")
            print("  gtext apikey  # Interactive mode")
        else:
            print("Configured providers:")
            for provider in providers:
                print(f"  • {provider}")
        return 0

    # Subcommand: set
    elif args.apikey_action == "set":
        if not args.provider or not args.api_key:
            print("ERROR: Both provider and api_key are required", file=sys.stderr)
            print("Usage: gtext apikey set <provider> <key>")
            return 1

        config.set_api_key(args.provider, args.api_key)
        print(f"✓ API key for '{args.provider}' saved to ~/.gtext/config.yaml")
        return 0

    # Subcommand: delete
    elif args.apikey_action == "delete":
        if not args.provider:
            print("ERROR: Provider name required", file=sys.stderr)
            print("Usage: gtext apikey delete <provider>")
            return 1

        if config.delete_api_key(args.provider):
            print(f"✓ API key for '{args.provider}' deleted")
        else:
            print(f"ERROR: No API key found for '{args.provider}'", file=sys.stderr)
            return 1
        return 0

    # Interactive mode (no subcommand)
    else:
        print("🤖 gtext API Key Manager")
        print()

        # Show currently configured providers
        providers = config.list_providers()
        if providers:
            print("Currently configured:")
            for p in providers:
                print(f"  • {p}")
            print()

        # Ask for provider
        print("Supported providers:")
        print("  1. openai    (GPT-4, GPT-3.5)")
        print("  2. anthropic (Claude)")
        print()

        provider_input = input("Enter provider name (or number): ").strip().lower()

        # Map number to provider
        provider_map = {"1": "openai", "2": "anthropic"}
        provider = provider_map.get(provider_input, provider_input)

        if provider not in ["openai", "anthropic"]:
            print(f"ERROR: Unknown provider '{provider}'", file=sys.stderr)
            print("Supported: openai, anthropic")
            return 1

        # Ask for API key
        print()
        if provider == "openai":
            print("Get your OpenAI API key from: https://platform.openai.com/api-keys")
        elif provider == "anthropic":
            print("Get your Anthropic API key from: https://console.anthropic.com/")

        print()
        api_key = input(f"Enter {provider} API key: ").strip()

        if not api_key:
            print("ERROR: API key cannot be empty", file=sys.stderr)
            return 1

        # Save it
        config.set_api_key(provider, api_key)
        print()
        print(f"✓ API key for '{provider}' saved to ~/.gtext/config.yaml")
        print("  (file permissions set to 600 for security)")
        print()
        print("Test it with:")
        print(f"  GTEXT_TLDR_PROVIDER={provider} gtext cast your-file.gtext")

        return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        prog="gtext",
        description="The text wizard - Transform text files with pluggable extensions",
        epilog="Documentation: https://gtext.readthedocs.io",
    )

    parser.add_argument("--version", action="version", version=f"gtext {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # cast command
    cast_parser = subparsers.add_parser("cast", help="Process a single .gtext file")
    cast_parser.add_argument("input", help="Input .gtext file")
    cast_parser.add_argument(
        "-o", "--output", help="Output file (default: auto-detect by stripping .gtext)"
    )
    cast_parser.add_argument(
        "--dry-run", action="store_true", help="Print output to stdout without writing files"
    )
    cast_parser.set_defaults(func=cast_command)

    # cast-all command
    cast_all_parser = subparsers.add_parser("cast-all", help="Process multiple .gtext files")
    cast_all_parser.add_argument(
        "patterns", nargs="+", help="File patterns to process (supports globs)"
    )
    cast_all_parser.set_defaults(func=cast_all_command)

    # apikey command
    apikey_parser = subparsers.add_parser("apikey", help="Manage API keys for AI providers")
    apikey_subparsers = apikey_parser.add_subparsers(dest="apikey_action")

    # apikey list
    apikey_subparsers.add_parser("list", help="List configured providers")

    # apikey set
    apikey_set_parser = apikey_subparsers.add_parser("set", help="Set API key for a provider")
    apikey_set_parser.add_argument("provider", help="Provider name (openai, anthropic)")
    apikey_set_parser.add_argument("api_key", help="API key")

    # apikey delete
    apikey_delete_parser = apikey_subparsers.add_parser(
        "delete", help="Delete API key for a provider"
    )
    apikey_delete_parser.add_argument("provider", help="Provider name")

    apikey_parser.set_defaults(func=apikey_command)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
