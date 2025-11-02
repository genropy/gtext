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

    Supports modifiers (prefix with :modifier:):
    - expand: Recursively process the included content

    Syntax:
        protocol: content              # Basic
        :expand:protocol: content      # With expand modifier

    Examples:
        ```include
        static: header.md                      # Include file as-is
        :expand:static: template.md.gtext      # Include and expand recursively
        cli: python get_stats.py               # Execute command
        :expand:cli: python generate_doc.py    # Execute and expand output
        glob: sections/*.md                    # Include multiple files
        footer.md                              # Implicit static:
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

    # Supported modifiers
    MODIFIERS = {
        'expand',  # Recursively expand included content
    }

    def process(self, content: str, context: Dict) -> str:
        """Process all ```include blocks in the content.

        Args:
            content: The text content to process
            context: Context dict (should contain 'input_path' for relative path resolution)

        Returns:
            Content with all ```include blocks replaced by their resolved content
        """
        # Initialize depth tracking if not present
        if 'include_depth' not in context:
            context['include_depth'] = 0

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

    def _parse_line(self, line: str) -> tuple:
        """Parse line into (modifiers, protocol, content).

        Syntax: :modifier1:modifier2:protocol: content

        Args:
            line: Include directive line

        Returns:
            Tuple of (list of modifiers, protocol name, content)

        Examples:
            "static: file.md" → ([], 'static', 'file.md')
            ":expand:cli: date" → (['expand'], 'cli', 'date')
            ":expand:static: template.gtext" → (['expand'], 'static', 'template.gtext')
            "file.md" → ([], 'static', 'file.md')
        """
        modifiers = []
        content = line

        # Parse modifiers (lines starting with :)
        while content.startswith(':'):
            content = content[1:]  # Remove leading :

            if ':' not in content:
                # Malformed, treat as static
                return ([], 'static', line)

            parts = content.split(':', 1)
            potential_mod = parts[0].strip()

            if potential_mod in self.MODIFIERS:
                modifiers.append(potential_mod)
                content = parts[1]
            elif potential_mod in self.PROTOCOLS:
                # This is a protocol, not a modifier
                # Parse as protocol:content
                protocol = potential_mod
                actual_content = parts[1].strip()
                return (modifiers, protocol, actual_content)
            else:
                # Unknown modifier, stop parsing
                break

        # No more modifiers, parse protocol
        if ':' in content:
            parts = content.split(':', 1)
            protocol = parts[0].strip()
            actual_content = parts[1].strip()

            if protocol in self.PROTOCOLS:
                return (modifiers, protocol, actual_content)

        # No explicit protocol = static (backward compatibility)
        return (modifiers, 'static', content.strip())

    def _resolve_line(self, line: str, base_dir: Path, context: Dict) -> str:
        """Resolve a single include line using protocol handlers with modifiers support.

        Args:
            line: The include directive line
            base_dir: Base directory for path resolution
            context: Context dictionary

        Returns:
            Resolved content from the line
        """
        # Parse modifiers, protocol, content
        modifiers, protocol, content = self._parse_line(line)

        # Get handler
        if protocol not in self.PROTOCOLS:
            return f"<!-- ERROR: Unknown protocol '{protocol}' -->"

        handler_name = self.PROTOCOLS[protocol]
        handler = getattr(self, handler_name)

        # Execute handler
        result = handler(content, base_dir, context)

        # Apply modifiers
        if 'expand' in modifiers:
            # Recursively process the result
            result = self._expand_content(result, base_dir, context)

        return result

    def _expand_content(self, content: str, base_dir: Path, context: Dict) -> str:
        """Recursively expand content that may contain ```include blocks.

        Args:
            content: Content to expand
            base_dir: Base directory for resolution
            context: Context dict

        Returns:
            Expanded content with all ```include blocks resolved

        Note:
            Tracks recursion depth to prevent infinite loops.
            Maximum depth is 10 by default (configurable via context['max_include_depth']).
        """
        # Check if content has includes
        if '```include' not in content:
            return content

        # Check depth to prevent infinite recursion
        depth = context.get('include_depth', 0)
        max_depth = context.get('max_include_depth', 10)

        if depth >= max_depth:
            return f"<!-- ERROR: Max include depth {max_depth} exceeded -->\n{content}"

        # Increment depth
        context['include_depth'] = depth + 1

        # Process includes in this content
        def replace_include(match):
            include_block = match.group(1).strip()
            return self._resolve_include_block(include_block, context)

        expanded = self.INCLUDE_PATTERN.sub(replace_include, content)

        # Restore depth
        context['include_depth'] = depth

        return expanded

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
