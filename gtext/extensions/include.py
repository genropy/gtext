"""Include extension for gtext - supports static files, CLI output, and glob patterns."""

import glob
import re
import subprocess
from pathlib import Path
from typing import Dict

from gtext.extensions.base import BaseExtension


class IncludeExtension(BaseExtension):
    """Extension that processes ```include blocks.

    Supports three types of includes:
    1. Static files: ```include path/to/file.md ```
    2. CLI commands: ```include cli: python script.py ```
    3. Glob patterns: ```include glob: docs/**/*.md ```

    All three can be mixed in a single block.

    Example:
        ```include
        header.md
        cli: python get_stats.py
        glob: sections/*.md
        footer.md
        ```
    """

    name = "include"

    # Regex to match ```include blocks
    INCLUDE_PATTERN = re.compile(
        r"```include\s*\n(.*?)```",
        re.DOTALL | re.MULTILINE
    )

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

            if line.startswith("cli:"):
                # CLI command
                cmd = line[4:].strip()
                results.append(self._execute_cli(cmd))
            elif line.startswith("glob:"):
                # Glob pattern
                pattern = line[5:].strip()
                results.append(self._resolve_glob(pattern, base_dir))
            else:
                # Static file path
                results.append(self._read_file(line, base_dir))

        return "\n".join(results)

    def _read_file(self, path: str, base_dir: Path) -> str:
        """Read a static file.

        Args:
            path: File path (relative or absolute)
            base_dir: Base directory for resolving relative paths

        Returns:
            File content

        Raises:
            FileNotFoundError: If file doesn't exist
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

    def _execute_cli(self, command: str) -> str:
        """Execute a CLI command and return its output.

        Args:
            command: Shell command to execute

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

    def _resolve_glob(self, pattern: str, base_dir: Path) -> str:
        """Resolve a glob pattern and include all matching files.

        Args:
            pattern: Glob pattern (e.g., "docs/**/*.md")
            base_dir: Base directory for resolving relative patterns

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
