"""Tests for Config class."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gtext.config import Config


def test_config_init():
    """Test Config initialization."""
    config = Config()
    assert config.config_dir == Path.home() / ".gtext"
    assert config.config_file == config.config_dir / "config.yaml"


def test_config_set_and_get_api_key():
    """Test setting and getting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-test-key-123')
            key = config.get_api_key('openai')
            assert key == 'sk-test-key-123'


def test_config_get_api_key_not_found():
    """Test getting non-existent API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            key = config.get_api_key('nonexistent')
            assert key is None


def test_config_delete_api_key():
    """Test deleting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('anthropic', 'sk-test')
            result = config.delete_api_key('anthropic')
            assert result is True
            key = config.get_api_key('anthropic')
            assert key is None


def test_config_delete_api_key_not_found():
    """Test deleting non-existent API key (no api_keys section)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            result = config.delete_api_key('nonexistent')
            assert result is False


def test_config_delete_api_key_not_in_list():
    """Test deleting non-existent API key (api_keys section exists)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            # Add one key
            config.set_api_key('openai', 'sk-test')
            # Try to delete a different key
            result = config.delete_api_key('anthropic')
            assert result is False


def test_config_list_providers():
    """Test listing configured providers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            providers = config.list_providers()
            assert providers == []
            
            config.set_api_key('openai', 'sk-test-1')
            config.set_api_key('anthropic', 'sk-test-2')
            
            providers = config.list_providers()
            assert set(providers) == {'openai', 'anthropic'}


def test_config_multiple_keys():
    """Test storing multiple API keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-openai-key')
            config.set_api_key('anthropic', 'sk-anthropic-key')

            assert config.get_api_key('openai') == 'sk-openai-key'
            assert config.get_api_key('anthropic') == 'sk-anthropic-key'


def test_config_get_all_api_keys():
    """Test getting all API keys at once."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-openai')
            config.set_api_key('anthropic', 'sk-anthropic')

            all_keys = config.get_all_api_keys()

            assert all_keys == {
                'openai': 'sk-openai',
                'anthropic': 'sk-anthropic'
            }


def test_config_load_error():
    """Test config load error handling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Create invalid YAML file
            config.config_file.parent.mkdir(parents=True, exist_ok=True)
            config.config_file.write_text("invalid: yaml: content: [[[")

            # Should return empty dict on load error
            result = config._load_config()
            assert result == {}
