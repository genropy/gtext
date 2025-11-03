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
    INCLUDE_PATTERN = re.compile(r"```include\s*\n(.*?)```", re.DOTALL | re.MULTILINE)

    # Protocol handlers
    PROTOCOLS = {
        "static": "_handle_static",
        "cli": "_handle_cli",
        "glob": "_handle_glob",
    }

    # Supported modifiers
    MODIFIERS = {
        "expand",  # Recursively expand included content
        "tldr",  # AI-powered summarization
        "translate",  # AI-powered translation
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
        if "include_depth" not in context:
            context["include_depth"] = 0

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

        Syntax: :modifier1[params]:modifier2:protocol: content

        Args:
            line: Include directive line

        Returns:
            Tuple of (list of modifier_specs, protocol name, content)
            where modifier_specs can be:
            - string: modifier name without parameters
            - tuple: (modifier_name, params_dict) with parameters

        Examples:
            "static: file.md" → ([], 'static', 'file.md')
            ":expand:cli: date" → (['expand'], 'cli', 'date')
            ":translate[it]:static: file.md" → ([('translate', {'lang': 'it'}], 'static', 'file.md')
            "file.md" → ([], 'static', 'file.md')
        """
        modifiers = []
        content = line

        # Parse modifiers (lines starting with :)
        while content.startswith(":"):
            content = content[1:]  # Remove leading :

            if ":" not in content:
                # Malformed, treat as static
                return ([], "static", line)

            parts = content.split(":", 1)
            potential_mod = parts[0].strip()

            # Check for parameters in square brackets
            mod_name = potential_mod
            mod_params = {}
            if "[" in potential_mod and "]" in potential_mod:
                # Extract modifier name and parameters
                bracket_start = potential_mod.index("[")
                bracket_end = potential_mod.index("]")
                mod_name = potential_mod[:bracket_start]
                params_str = potential_mod[bracket_start + 1 : bracket_end]
                # For now, simple format: single parameter is the target language
                mod_params = {"lang": params_str.strip()}

            if mod_name in self.MODIFIERS:
                if mod_params:
                    modifiers.append((mod_name, mod_params))
                else:
                    modifiers.append(mod_name)
                content = parts[1]
            elif mod_name in self.PROTOCOLS:
                # This is a protocol, not a modifier
                # Parse as protocol:content
                protocol = mod_name
                actual_content = parts[1].strip()
                return (modifiers, protocol, actual_content)
            else:
                # Unknown modifier, stop parsing
                break

        # No more modifiers, parse protocol
        if ":" in content:
            parts = content.split(":", 1)
            protocol = parts[0].strip()
            actual_content = parts[1].strip()

            if protocol in self.PROTOCOLS:
                return (modifiers, protocol, actual_content)

        # No explicit protocol = static (backward compatibility)
        return (modifiers, "static", content.strip())

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
        for modifier in modifiers:
            # Handle both string modifiers and (name, params) tuples
            if isinstance(modifier, tuple):
                mod_name, mod_params = modifier
            else:
                mod_name = modifier
                mod_params = {}

            if mod_name == "expand":
                # Recursively process the result
                result = self._expand_content(result, base_dir, context)
            elif mod_name == "tldr":
                # AI-powered summarization
                result = self._tldr_content(result, context)
            elif mod_name == "translate":
                # AI-powered translation
                # Merge modifier params into context
                translate_context = context.copy()
                if "lang" in mod_params:
                    translate_context["translate_target"] = mod_params["lang"]
                result = self._translate_content(result, translate_context)

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
        if "```include" not in content:
            return content

        # Check depth to prevent infinite recursion
        depth = context.get("include_depth", 0)
        max_depth = context.get("max_include_depth", 10)

        if depth >= max_depth:
            return f"<!-- ERROR: Max include depth {max_depth} exceeded -->\n{content}"

        # Increment depth
        context["include_depth"] = depth + 1

        # Process includes in this content
        def replace_include(match):
            include_block = match.group(1).strip()
            return self._resolve_include_block(include_block, context)

        expanded = self.INCLUDE_PATTERN.sub(replace_include, content)

        # Restore depth
        context["include_depth"] = depth

        return expanded

    def _tldr_content(self, content: str, context: Dict) -> str:
        """Generate AI-powered summary of content.

        Args:
            content: Content to summarize
            context: Context dict (may contain 'tldr_model', 'tldr_mock')

        Returns:
            Summarized content or error message

        Configuration via context or environment variables:
            - GTEXT_AI_MODEL: Model name (e.g., "gpt-4", "claude-3-sonnet", "ollama/mistral")
            - OPENAI_API_KEY, ANTHROPIC_API_KEY, etc: Provider API keys
            - Set tldr_mock=True in context for mock mode (testing)
        """
        import os
        from gtext import ai

        # Check for mock mode
        if context.get("tldr_mock") or os.getenv("GTEXT_TLDR_MOCK"):
            return self._tldr_mock(content)

        # Check content length
        if len(content.strip()) < 100:
            return content  # Too short to summarize

        # Check if AI is available
        if not ai.is_ai_available():
            return (
                "<!-- ERROR: LiteLLM not installed. "
                "Install with: pip install 'gtext[ai]' -->\n" + content
            )

        # Get model from context or use default
        model = context.get("tldr_model") or os.getenv("GTEXT_AI_MODEL")

        try:
            summary = ai.summarize(content, model=model)
            model_used = model or ai.get_default_model() or "unknown"
            return f"**AI Summary ({model_used}):**\n\n{summary}\n"
        except ImportError as e:
            return f"<!-- ERROR: {e} -->\n{content}"
        except ValueError as e:
            return f"<!-- ERROR: {e} -->\n{content}"
        except Exception as e:
            return f"<!-- ERROR in AI summarization: {e} -->\n{content}"

    def _tldr_mock(self, content: str) -> str:
        """Mock summarization for testing (no API required)."""
        lines = content.strip().split("\n")
        word_count = len(content.split())
        char_count = len(content)

        # Create a simple summary
        first_lines = "\n".join(lines[:3])
        if len(lines) > 3:
            first_lines += f"\n\n[...{len(lines) - 3} more lines...]"

        return f"""**Mock Summary:**

- Document contains {word_count} words, {char_count} characters
- {len(lines)} lines total
- First few lines:

{first_lines}

*This is a mock summary. For AI summaries: install 'gtext[ai]' and set GTEXT_AI_MODEL (e.g., gpt-4, claude-3-sonnet) with appropriate API key.*
"""

    def _translate_content(self, content: str, context: Dict) -> str:
        """Generate AI-powered translation of content.

        Args:
            content: Content to translate
            context: Context dict (may contain 'translate_model', 'translate_target', 'translate_mock')

        Returns:
            Translated content or error message

        Configuration via context or environment variables:
            - GTEXT_AI_MODEL: Model name (e.g., "gpt-4", "claude-3-sonnet")
            - GTEXT_TRANSLATE_TARGET: Target language code (e.g., "it", "fr", "es")
            - OPENAI_API_KEY, ANTHROPIC_API_KEY, etc: Provider API keys
            - Set translate_mock=True in context for mock mode (testing)
        """
        import os
        from gtext import ai

        # Get target language
        target_lang = context.get("translate_target") or os.getenv("GTEXT_TRANSLATE_TARGET", "en")

        # Check for mock mode
        if context.get("translate_mock") or os.getenv("GTEXT_TRANSLATE_MOCK"):
            return self._translate_mock(content, target_lang)

        # Check content length
        if len(content.strip()) < 10:
            return content  # Too short to translate

        # Check if AI is available
        if not ai.is_ai_available():
            return (
                "<!-- ERROR: LiteLLM not installed. "
                "Install with: pip install 'gtext[ai]' -->\n" + content
            )

        # Get model from context or use default
        model = context.get("translate_model") or os.getenv("GTEXT_AI_MODEL")

        try:
            return ai.translate(content, target_lang, model=model)
        except ImportError as e:
            return f"<!-- ERROR: {e} -->\n{content}"
        except ValueError as e:
            return f"<!-- ERROR: {e} -->\n{content}"
        except Exception as e:
            return f"<!-- ERROR in AI translation: {e} -->\n{content}"

    def _translate_mock(self, content: str, target_lang: str) -> str:
        """Mock translation for testing (no API required)."""
        return f"""<!-- Mock Translation to {target_lang} -->

{content}

<!-- This is a mock translation (original text preserved). -->
<!-- For AI translation: install 'gtext[ai]' and set GTEXT_AI_MODEL with appropriate API key. -->"""

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
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
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
