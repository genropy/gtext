"""Command-line interface for gtext."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from gtext import __version__
from gtext.config import Config
from gtext.metadata import add_output, get_outputs
from gtext.processor import TextProcessor


def render_command(args) -> int:
    """Execute the render command (intelligently handles single/multiple files).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import glob as glob_module

    try:
        processor = TextProcessor()

        # Separate inputs from potential output argument
        # Last arg might be output if it's not a .gtext file
        inputs_list = list(args.inputs)
        output_arg = None

        if len(inputs_list) > 1:
            last_arg = inputs_list[-1]
            # If last arg doesn't exist or is a directory, treat as output
            last_path = Path(last_arg)
            if not last_path.exists() or last_path.is_dir() or not last_arg.endswith(".gtext"):
                output_arg = inputs_list.pop()

        # Collect all input files (expand globs)
        input_files = []
        for pattern in inputs_list:
            if "*" in pattern:
                # Glob pattern
                matches = glob_module.glob(pattern, recursive=True)
                input_files.extend([Path(f) for f in matches if Path(f).is_file()])
            else:
                # Regular file
                input_files.append(Path(pattern))

        if not input_files:
            print("ERROR: No input files found", file=sys.stderr)
            return 1

        # Determine output mode
        output_dir = None
        if output_arg:
            output_path_obj = Path(output_arg)

            # If single file and output looks like a file, use it as-is
            if (
                len(input_files) == 1
                and "." in output_path_obj.name
                and not output_path_obj.is_dir()
            ):
                # Single file to single file
                pass
            else:
                # Output is a directory
                output_dir = output_path_obj
                output_dir.mkdir(parents=True, exist_ok=True)

        # Process files
        errors = 0
        for input_path in input_files:
            try:
                if args.dry_run or args.stdout:
                    # Print to stdout
                    result = processor.process_string(
                        input_path.read_text(encoding="utf-8"),
                        context={"input_path": input_path},
                    )
                    print(result)
                    if len(input_files) > 1:
                        print(f"\n{'='*60}\n")
                else:
                    # Determine output path for this file
                    if output_dir:
                        # Output to directory
                        output_name = (
                            input_path.stem if input_path.suffix == ".gtext" else input_path.name
                        )
                        output_path = output_dir / output_name
                    elif output_arg and len(input_files) == 1:
                        # Single file with explicit output file
                        output_path = Path(output_arg)
                    else:
                        # Auto-detect (same dir, strip .gtext)
                        output_path = None

                    processor.process_file(input_path, output_path)

                    # Determine the actual output path that was used
                    if output_path:
                        actual_output = output_path
                        print(f"Rendered {input_path} -> {output_path}")
                    else:
                        if str(input_path).endswith(".gtext"):
                            auto_output = str(input_path)[:-6]
                        else:
                            auto_output = str(input_path)
                        actual_output = Path(auto_output)
                        print(f"Rendered {input_path} -> {auto_output}")

                    # Save metadata (output path) in source file
                    if str(input_path).endswith(".gtext"):
                        add_output(input_path, actual_output)

            except Exception as e:
                print(f"ERROR processing {input_path}: {e}", file=sys.stderr)
                errors += 1

        if len(input_files) > 1:
            print(f"\nRendered {len(input_files) - errors} file(s), {errors} error(s)")

        return 1 if errors > 0 else 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def refresh_command(args) -> int:
    """Execute the refresh command (re-render using saved metadata).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import glob as glob_module

    try:
        processor = TextProcessor()

        # Collect input files
        input_files = []
        if hasattr(args, "sources") and args.sources:
            # Sources specified
            for pattern in args.sources:
                if "*" in pattern:
                    matches = glob_module.glob(pattern, recursive=True)
                    gtext_files = [
                        Path(f) for f in matches if Path(f).is_file() and f.endswith(".gtext")
                    ]
                    input_files.extend(gtext_files)
                else:
                    path = Path(pattern)
                    if path.is_file() and str(path).endswith(".gtext"):
                        input_files.append(path)
        else:
            # No sources: find all .gtext files in current directory with metadata
            for gtext_file in Path(".").glob("**/*.gtext"):
                if get_outputs(gtext_file):
                    input_files.append(gtext_file)

        if not input_files:
            print("No .gtext files with saved outputs found", file=sys.stderr)
            return 1

        errors = 0
        refreshed = 0

        for input_path in input_files:
            try:
                outputs = get_outputs(input_path)

                if not outputs:
                    print(f"- {input_path}: No saved outputs, skipping")
                    continue

                # Determine which output to use
                if len(outputs) == 1:
                    # Single output, use it
                    output_path = Path(outputs[0]["path"])
                    if not output_path.is_absolute():
                        output_path = input_path.parent / output_path
                elif hasattr(args, "all") and args.all:
                    # Refresh all outputs
                    for output_info in outputs:
                        output_path = Path(output_info["path"])
                        if not output_path.is_absolute():
                            output_path = input_path.parent / output_path

                        processor.process_file(input_path, output_path)
                        print(f"Refreshed {input_path} -> {output_path}")
                        refreshed += 1
                    continue
                else:
                    # Multiple outputs: interactive choice
                    print(f"\n{input_path} has {len(outputs)} outputs:")
                    for i, output_info in enumerate(outputs, 1):
                        timestamp = output_info.get("timestamp", "unknown")
                        print(f"  {i}. {output_info['path']} ({timestamp})")

                    choice = input("Refresh which? [1/all/skip] (default=1): ").strip().lower()

                    if choice == "skip" or choice == "s":
                        continue
                    elif choice == "all" or choice == "a":
                        # Refresh all
                        for output_info in outputs:
                            output_path = Path(output_info["path"])
                            if not output_path.is_absolute():
                                output_path = input_path.parent / output_path

                            processor.process_file(input_path, output_path)
                            print(f"Refreshed {input_path} -> {output_path}")
                            refreshed += 1
                        continue
                    else:
                        # Use number or default to 1
                        try:
                            idx = int(choice) if choice else 1
                            if 1 <= idx <= len(outputs):
                                output_info = outputs[idx - 1]
                                output_path = Path(output_info["path"])
                                if not output_path.is_absolute():
                                    output_path = input_path.parent / output_path
                            else:
                                print(f"Invalid choice: {choice}")
                                continue
                        except ValueError:
                            print(f"Invalid choice: {choice}")
                            continue

                # Single refresh
                processor.process_file(input_path, output_path)
                print(f"Refreshed {input_path} -> {output_path}")
                refreshed += 1

            except Exception as e:
                print(f"ERROR refreshing {input_path}: {e}", file=sys.stderr)
                errors += 1

        print(f"\nRefreshed {refreshed} file(s), {errors} error(s)")
        return 1 if errors > 0 else 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


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
        print(f"API key for '{args.provider}' saved to ~/.gtext/config.yaml")
        return 0

    # Subcommand: delete
    elif args.apikey_action == "delete":
        if not args.provider:
            print("ERROR: Provider name required", file=sys.stderr)
            print("Usage: gtext apikey delete <provider>")
            return 1

        if config.delete_api_key(args.provider):
            print(f"API key for '{args.provider}' deleted")
        else:
            print(f"ERROR: No API key found for '{args.provider}'", file=sys.stderr)
            return 1
        return 0

    # Interactive mode (no subcommand)
    else:
        print("gtext API Key Manager")
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
        print(f"API key for '{provider}' saved to ~/.gtext/config.yaml")
        print("  (file permissions set to 600 for security)")
        print()
        print("Test it with:")
        print(f"  GTEXT_TLDR_PROVIDER={provider} gtext cast your-file.gtext")

        return 0


def serve_command(args) -> int:
    """Execute the serve command (live preview server).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Check if watchdog is installed
        try:
            import watchdog  # noqa: F401
        except ImportError:
            print(
                "ERROR: The 'serve' command requires watchdog. Install with:",
                file=sys.stderr,
            )
            print("  pip install 'gtext[serve]'", file=sys.stderr)
            return 1

        from gtext.server import PreviewServer

        source_file = Path(args.source)

        if not source_file.exists():
            print(f"ERROR: File not found: {source_file}", file=sys.stderr)
            return 1

        if not str(source_file).endswith(".gtext"):
            print(f"ERROR: File must have .gtext extension: {source_file}", file=sys.stderr)
            return 1

        # Start server
        server = PreviewServer(source_file, port=args.port, host=args.host)
        server.start()
        server.serve_forever()

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


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

    # render command (new, handles single and multiple intelligently)
    render_parser = subparsers.add_parser(
        "render",
        help="Render .gtext template(s) - handles single files, patterns, and multiple inputs",
        epilog="Examples:\n"
        "  gtext render foo.md.gtext\n"
        "  gtext render foo.md.gtext output.md\n"
        "  gtext render foo.md.gtext finaldocs/\n"
        "  gtext render 'docs/**/*.gtext' finaldocs/\n"
        "  gtext render file1.gtext file2.gtext output/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    render_parser.add_argument(
        "inputs",
        nargs="+",
        help="Input .gtext file(s) or pattern(s), optionally followed by output file/directory. "
        "Last argument is treated as output if it doesn't end with .gtext",
    )
    render_parser.add_argument(
        "--stdout", action="store_true", help="Print output to stdout without writing files"
    )
    render_parser.add_argument("--dry-run", action="store_true", help="Alias for --stdout")
    render_parser.set_defaults(func=render_command)

    # refresh command
    refresh_parser = subparsers.add_parser(
        "refresh",
        help="Re-render .gtext files using saved output paths from metadata",
        epilog="Examples:\n"
        "  gtext refresh                  # Refresh all .gtext with metadata\n"
        "  gtext refresh foo.md.gtext      # Refresh specific file\n"
        "  gtext refresh 'docs/**/*.gtext' # Refresh pattern\n"
        "  gtext refresh --all             # Refresh all outputs for each file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    refresh_parser.add_argument(
        "sources",
        nargs="*",
        help="Source .gtext file(s) or pattern(s). If omitted, finds all .gtext with metadata",
    )
    refresh_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Refresh all saved outputs (skip interactive choice for multiple outputs)",
    )
    refresh_parser.set_defaults(func=refresh_command)

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

    # serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start live preview server for a .gtext file",
        epilog="Examples:\n"
        "  gtext serve document.md.gtext\n"
        "  gtext serve document.md.gtext --port 8000\n"
        "  gtext serve document.md.gtext --host 0.0.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    serve_parser.add_argument("source", help="Source .gtext file to serve")
    serve_parser.add_argument(
        "--port", "-p", type=int, default=8080, help="Port to serve on (default: 8080)"
    )
    serve_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.set_defaults(func=serve_command)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
