"""AI integration for gtext using LiteLLM.

This module provides a unified interface for AI operations (translation, summarization)
using LiteLLM which supports multiple providers (OpenAI, Anthropic, Azure, Ollama, etc.)
with a consistent API.
"""

import os
from typing import Dict, List, Optional


def is_ai_available() -> bool:
    """Check if LiteLLM is installed and configured."""
    try:
        import litellm  # noqa: F401
        return True
    except ImportError:
        return False


def get_configured_providers() -> Dict[str, bool]:
    """Detect which AI providers are configured via environment variables.

    Returns:
        Dictionary mapping provider names to configuration status
    """
    providers = {
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "Azure": bool(os.getenv("AZURE_API_KEY")),
        "Cohere": bool(os.getenv("COHERE_API_KEY")),
        "Ollama": True,  # Local, no key needed
    }
    return providers


def get_default_model() -> Optional[str]:
    """Get the default model from environment or config.

    Returns:
        Default model name or None if not configured
    """
    # Check environment variable first
    model = os.getenv("GTEXT_AI_MODEL")
    if model:
        return model

    # Check config file (future implementation)
    # config = load_config()
    # if config and 'default_model' in config:
    #     return config['default_model']

    # Auto-detect based on available API keys
    if os.getenv("OPENAI_API_KEY"):
        return "gpt-4o-mini"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "claude-3-haiku-20240307"

    return None


def get_ai_status() -> Dict[str, any]:
    """Get complete AI configuration status.

    Returns:
        Dictionary with AI availability, providers, and default model
    """
    available = is_ai_available()
    return {
        "available": available,
        "providers": get_configured_providers() if available else {},
        "default_model": get_default_model() if available else None,
    }


def call_ai(
    prompt: str,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 4000,
) -> str:
    """Call AI model via LiteLLM with unified interface.

    Args:
        prompt: The user prompt/message
        model: Model name (e.g., "gpt-4", "claude-3-sonnet", "ollama/mistral")
               If None, uses default from get_default_model()
        system: Optional system message
        max_tokens: Maximum tokens in response

    Returns:
        AI response text

    Raises:
        ImportError: If litellm not installed
        Exception: If AI call fails
    """
    try:
        import litellm
    except ImportError:
        raise ImportError(
            "LiteLLM not installed. Install with: pip install 'gtext[ai]'"
        )

    # Use default model if not specified
    if not model:
        model = get_default_model()
        if not model:
            raise ValueError(
                "No AI model configured. Set GTEXT_AI_MODEL environment variable "
                "or configure an API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)"
            )

    # Build messages
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Call via LiteLLM
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"AI call failed: {str(e)}")


def translate(text: str, target_language: str, model: Optional[str] = None) -> str:
    """Translate text to target language using AI.

    Args:
        text: Text to translate
        target_language: Target language code (e.g., "it", "fr", "es")
        model: Optional model override

    Returns:
        Translated text
    """
    prompt = f"""Translate the following text to {target_language}.
Preserve all formatting, markdown syntax, and code blocks.
Only return the translated text, nothing else.

Text to translate:
{text}"""

    return call_ai(prompt, model=model, max_tokens=8000)


def summarize(text: str, model: Optional[str] = None) -> str:
    """Generate a summary/TLDR of text using AI.

    Args:
        text: Text to summarize
        model: Optional model override

    Returns:
        Summary text
    """
    system = "You are a technical documentation assistant. Create concise summaries."

    prompt = f"""Create a brief summary (TL;DR) of the following text.
Focus on key points and main ideas.
Use 2-5 bullet points.

Text to summarize:
{text}"""

    return call_ai(prompt, model=model, system=system, max_tokens=2000)


def get_available_models() -> Dict[str, List[str]]:
    """Get list of commonly used models per provider.

    Returns:
        Dictionary mapping provider names to model lists
    """
    return {
        "OpenAI": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "Anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "Azure": [
            "azure/gpt-4",
            "azure/gpt-35-turbo",
        ],
        "Ollama": [
            "ollama/llama2",
            "ollama/mistral",
            "ollama/codellama",
        ],
    }
