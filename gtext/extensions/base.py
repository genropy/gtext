"""Base extension class for gtext."""

from abc import ABC, abstractmethod
from typing import Dict


class BaseExtension(ABC):
    """Abstract base class for gtext extensions.

    All extensions must inherit from this class and implement the process method.

    Attributes:
        name: Unique identifier for the extension

    Example:
        >>> class MyExtension(BaseExtension):
        ...     name = "my-extension"
        ...
        ...     def process(self, content: str, context: dict) -> str:
        ...         return content.upper()
    """

    name: str = "base"

    @abstractmethod
    def process(self, content: str, context: Dict) -> str:
        """Process content and return transformed result.

        Args:
            content: The text content to process
            context: Context dictionary with metadata (e.g., input_path)

        Returns:
            The transformed content

        Raises:
            Any extension-specific exceptions
        """
        pass
