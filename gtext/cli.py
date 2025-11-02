"""Command-line interface for gtext."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from gtext import __version__
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
                context={"input_path": Path(args.input)}
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


def watch_command(args) -> int:
    """Execute the watch command (watch for changes).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    print("ERROR: Watch mode not yet implemented", file=sys.stderr)
    print("Suggestion: Use a file watcher like 'watchexec' or 'entr' with gtext cast-all")
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
        epilog="Documentation: https://gtext.readthedocs.io"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"gtext {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # cast command
    cast_parser = subparsers.add_parser(
        "cast",
        help="Process a single .gtext file"
    )
    cast_parser.add_argument(
        "input",
        help="Input .gtext file"
    )
    cast_parser.add_argument(
        "-o", "--output",
        help="Output file (default: auto-detect by stripping .gtext)"
    )
    cast_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output to stdout without writing files"
    )
    cast_parser.set_defaults(func=cast_command)

    # cast-all command
    cast_all_parser = subparsers.add_parser(
        "cast-all",
        help="Process multiple .gtext files"
    )
    cast_all_parser.add_argument(
        "patterns",
        nargs="+",
        help="File patterns to process (supports globs)"
    )
    cast_all_parser.set_defaults(func=cast_all_command)

    # watch command (not yet implemented)
    watch_parser = subparsers.add_parser(
        "watch",
        help="Watch files and auto-regenerate on changes"
    )
    watch_parser.add_argument(
        "patterns",
        nargs="+",
        help="File patterns to watch"
    )
    watch_parser.set_defaults(func=watch_command)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
