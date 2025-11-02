"""Core text processing engine for gtext."""

import re
from pathlib import Path
from typing import Dict, List, Optional

from gtext.extensions.base import BaseExtension
from gtext.extensions.include import IncludeExtension


class TextProcessor:
    """Main processor for transforming text files with extensions.

    The TextProcessor reads .gtext files, applies registered extensions,
    and outputs the transformed content.

    Args:
        extensions: List of extension instances to use. If None, uses default extensions.

    Example:
        >>> processor = TextProcessor()
        >>> result = processor.process_file("document.md.gtext")
        >>> print(result)
    """

    def __init__(self, extensions: Optional[List[BaseExtension]] = None):
        """Initialize the processor with extensions."""
        if extensions is None:
            # Default extensions
            self.extensions = [IncludeExtension()]
        else:
            self.extensions = extensions

    def process_file(self, input_path: str | Path, output_path: Optional[str | Path] = None) -> str:
        """Process a .gtext file and optionally write output.

        Args:
            input_path: Path to the .gtext source file
            output_path: Optional output path. If None and input ends with .gtext,
                        auto-detects output by stripping .gtext extension.

        Returns:
            The processed content as a string

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Read source content
        content = input_path.read_text(encoding="utf-8")

        # Process with extensions
        processed = self.process_string(content, context={"input_path": input_path})

        # Write output if requested
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(processed, encoding="utf-8")
        elif str(input_path).endswith(".gtext"):
            # Auto-detect output path
            output_path = Path(str(input_path)[:-6])  # Strip .gtext
            output_path.write_text(processed, encoding="utf-8")

        return processed

    def process_string(self, content: str, context: Optional[Dict] = None) -> str:
        """Process a string with all registered extensions.

        Args:
            content: The text content to process
            context: Optional context dict passed to extensions

        Returns:
            The processed content
        """
        if context is None:
            context = {}

        # Remove gtext metadata comments before processing
        content = self._remove_metadata_comments(content)

        result = content
        for extension in self.extensions:
            result = extension.process(result, context)

        return result

    def _remove_metadata_comments(self, content: str) -> str:
        """Remove gtext metadata comments from content.

        Args:
            content: Content that may contain metadata comments

        Returns:
            Content with metadata comments removed
        """
        # Remove <!-- gtext:{...} --> comments
        pattern = r"<!--\s*gtext:\{.*?\}\s*-->\n?"
        return re.sub(pattern, "", content, flags=re.DOTALL)

    def add_extension(self, extension: BaseExtension) -> None:
        """Add an extension to the processor.

        Args:
            extension: Extension instance to add
        """
        self.extensions.append(extension)
