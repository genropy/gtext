#!/usr/bin/env python3
"""Example CLI tool with comprehensive help documentation."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="my_tool",
        description="A powerful data processing tool for batch operations",
        epilog="For more info visit: https://github.com/myorg/my-tool",
    )

    parser.add_argument(
        "input_file",
        help="Input file to process (supports .csv, .json, .xml)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv", "xml", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Operation timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.2.3",
    )

    args = parser.parse_args()

    # Actual processing would go here
    print(f"Processing {args.input_file}...")
    if args.output:
        print(f"Output will be written to {args.output}")
    print(f"Format: {args.format}")


if __name__ == "__main__":
    main()
