"""Include extension for gtext - supports static files, CLI output, and glob patterns."""

import glob
import re
import subprocess
from pathlib import Path
from typing import Dict

from gtext.extensions.base import BaseExtension


class IncludeExtension(BaseExtension):
    """Extension that processes ```include blocks.

    Supports multiple protocols:
    - static: Static files (default if no protocol specified)
    - cli: Execute shell commands
    - glob: Multiple files via glob patterns

    All protocols can be mixed in a single block.

    Example:
        ```include
        static: header.md
        cli: python get_stats.py
        glob: sections/*.md
        footer.md
        ```

    Backward compatibility: Lines without protocol are treated as static: paths.
    """

    name = "include"

    # Regex to match ```include blocks
    INCLUDE_PATTERN = re.compile(
        r"```include\s*\n(.*?)```",
        re.DOTALL | re.MULTILINE
    )

    # Protocol handlers
    PROTOCOLS = {
        'static': '_handle_static',
        'cli': '_handle_cli',
        'glob': '_handle_glob',
    }

    def process(self, content: str, context: Dict) -> str:
        """Process all ```include blocks in the content.

        Args:
            content: The text content to process
            context: Context dict (should contain 'input_path' for relative path resolution)

        Returns:
            Content with all ```include blocks replaced by their resolved content
        """
        def replace_include(match):
            include_block = match.group(1).strip()
            return self._resolve_include_block(include_block, context)

        return self.INCLUDE_PATTERN.sub(replace_include, content)

    def _resolve_include_block(self, block: str, context: Dict) -> str:
        """Resolve a single ```include block.

        Args:
            block: The content inside the ```include block
            context: Context dict for path resolution

        Returns:
            The resolved content from all include directives
        """
        lines = block.split("\n")
        results = []

        input_path = context.get("input_path")
        base_dir = Path(input_path).parent if input_path else Path.cwd()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            result = self._resolve_line(line, base_dir, context)
            results.append(result)

        return "\n".join(results)

    def _resolve_line(self, line: str, base_dir: Path, context: Dict) -> str:
        """Resolve a single include line using protocol handlers.

        Args:
            line: The include directive line
            base_dir: Base directory for path resolution
            context: Context dictionary

        Returns:
            Resolved content from the line
        """
        # Check for protocol prefix
        if ':' in line:
            # Try to split protocol:content
            parts = line.split(':', 1)
            protocol = parts[0].strip()

            # Check if this is a known protocol
            if protocol in self.PROTOCOLS:
                content = parts[1].strip()
                handler_name = self.PROTOCOLS[protocol]
                handler = getattr(self, handler_name)
                return handler(content, base_dir, context)

            # Not a known protocol, treat as path (e.g., C:\path or url:// etc)
            # Fall through to static handler

        # No protocol or unknown protocol = static file (backward compatibility)
        return self._handle_static(line, base_dir, context)

    def _handle_static(self, path: str, base_dir: Path, context: Dict) -> str:
        """Handle static file includes.

        Args:
            path: File path (relative or absolute)
            base_dir: Base directory for resolving relative paths
            context: Context dictionary

        Returns:
            File content
        """
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = base_dir / file_path

        if not file_path.exists():
            return f"<!-- ERROR: File not found: {path} -->"

        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            return f"<!-- ERROR reading {path}: {e} -->"

    def _handle_cli(self, command: str, base_dir: Path, context: Dict) -> str:
        """Handle CLI command execution.

        Args:
            command: Shell command to execute
            base_dir: Base directory (for context, not used)
            context: Context dictionary

        Returns:
            Command output (stdout)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return f"<!-- ERROR executing '{command}': {result.stderr} -->"
            return result.stdout
        except subprocess.TimeoutExpired:
            return f"<!-- ERROR: Command timed out: {command} -->"
        except Exception as e:
            return f"<!-- ERROR executing '{command}': {e} -->"

    def _handle_glob(self, pattern: str, base_dir: Path, context: Dict) -> str:
        """Handle glob pattern matching.

        Args:
            pattern: Glob pattern (e.g., "docs/**/*.md")
            base_dir: Base directory for resolving relative patterns
            context: Context dictionary

        Returns:
            Combined content from all matching files
        """
        # Resolve pattern relative to base_dir
        full_pattern = str(base_dir / pattern)

        try:
            matching_files = sorted(glob.glob(full_pattern, recursive=True))

            if not matching_files:
                return f"<!-- WARNING: No files matched pattern: {pattern} -->"

            results = []
            for file_path in matching_files:
                path = Path(file_path)
                if path.is_file():
                    try:
                        content = path.read_text(encoding="utf-8")
                        results.append(content)
                    except Exception as e:
                        results.append(f"<!-- ERROR reading {file_path}: {e} -->")

            return "\n\n".join(results)
        except Exception as e:
            return f"<!-- ERROR resolving glob '{pattern}': {e} -->"
