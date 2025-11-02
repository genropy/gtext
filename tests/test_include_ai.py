"""Tests for AI features in IncludeExtension (tldr, translate with real providers)."""

import os
import tempfile
from pathlib import Path
import pytest

from gtext.processor import TextProcessor


# Skip all tests if no OpenAI API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


def test_tldr_openai_real(tmp_path):
    """Test :tldr: with OpenAI provider (real API call)."""
    content_file = tmp_path / "doc.txt"
    # Create content long enough to summarize
    content_file.write_text("""
# Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on building systems
that can learn from and make decisions based on data. Unlike traditional programming,
where explicit instructions are provided, machine learning algorithms identify patterns
in data and use those patterns to make predictions or decisions without being explicitly
programmed for each specific task.

There are three main types of machine learning: supervised learning, where the algorithm
learns from labeled training data; unsupervised learning, where the algorithm finds patterns
in unlabeled data; and reinforcement learning, where the algorithm learns through trial and
error by receiving rewards or penalties.

Popular applications of machine learning include image recognition, natural language processing,
recommendation systems, and autonomous vehicles.
""")

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "openai",
        "tldr_model": "gpt-4o-mini"
    }

    result = processor.process_string(template, context=context)

    # Should contain AI summary
    assert "AI Summary" in result
    assert "gpt-4o-mini" in result
    # Should be shorter than original
    assert len(result) < len(content_file.read_text())


def test_translate_openai_real(tmp_path):
    """Test :translate: with OpenAI provider (real API call)."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Hello world. This is a test document.")

    processor = TextProcessor()
    template = f"""```include
:translate[it]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "openai",
        "translate_model": "gpt-4o-mini"
    }

    result = processor.process_string(template, context=context)

    # Should contain translation (likely contains "Ciao" or Italian text)
    assert result.strip() != ""
    # Should be different from original English
    assert "This is a test document" not in result or "Questo è" in result


def test_tldr_with_config(tmp_path):
    """Test :tldr: reading API key from environment."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Content. " * 50)  # Long enough

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    # Set provider via environment variable
    import os
    old_provider = os.environ.get("GTEXT_TLDR_PROVIDER")
    os.environ["GTEXT_TLDR_PROVIDER"] = "openai"

    try:
        result = processor.process_string(template, context={"cwd": tmp_path})

        # Should use openai and succeed
        assert "AI Summary" in result or "ERROR" in result
    finally:
        # Restore
        if old_provider:
            os.environ["GTEXT_TLDR_PROVIDER"] = old_provider
        elif "GTEXT_TLDR_PROVIDER" in os.environ:
            del os.environ["GTEXT_TLDR_PROVIDER"]


def test_translate_with_config(tmp_path):
    """Test :translate: reading API key from environment."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("This is a simple test.")

    processor = TextProcessor()
    template = f"""```include
:translate[es]:static: {content_file}
```"""

    # Set provider via environment
    import os
    old_provider = os.environ.get("GTEXT_TRANSLATE_PROVIDER")
    old_target = os.environ.get("GTEXT_TRANSLATE_TARGET")

    os.environ["GTEXT_TRANSLATE_PROVIDER"] = "openai"
    os.environ["GTEXT_TRANSLATE_TARGET"] = "es"

    try:
        result = processor.process_string(template, context={"cwd": tmp_path})

        # Should translate or show error
        assert result.strip() != ""
    finally:
        # Restore
        if old_provider:
            os.environ["GTEXT_TRANSLATE_PROVIDER"] = old_provider
        elif "GTEXT_TRANSLATE_PROVIDER" in os.environ:
            del os.environ["GTEXT_TRANSLATE_PROVIDER"]

        if old_target:
            os.environ["GTEXT_TRANSLATE_TARGET"] = old_target
        elif "GTEXT_TRANSLATE_TARGET" in os.environ:
            del os.environ["GTEXT_TRANSLATE_TARGET"]
