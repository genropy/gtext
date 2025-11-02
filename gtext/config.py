"""Configuration management for gtext."""

import os
import stat
import yaml
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Manage gtext configuration stored in ~/.gtext/config.yaml."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".gtext"
        self.config_file = self.config_dir / "config.yaml"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists with proper permissions."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(mode=0o700, parents=True)
        else:
            # Ensure directory has secure permissions
            self.config_dir.chmod(0o700)

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                return config
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}

    def _save_config(self, config: Dict):
        """Save configuration to file with secure permissions."""
        # Write config
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        # Set secure permissions (owner read/write only)
        self.config_file.chmod(0o600)

    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider.

        Args:
            provider: Provider name ('openai', 'anthropic', etc.)
            api_key: API key string
        """
        config = self._load_config()

        if 'api_keys' not in config:
            config['api_keys'] = {}

        config['api_keys'][provider] = api_key
        self._save_config(config)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider.

        Args:
            provider: Provider name

        Returns:
            API key or None if not found
        """
        config = self._load_config()
        return config.get('api_keys', {}).get(provider)

    def delete_api_key(self, provider: str) -> bool:
        """Delete API key for a provider.

        Args:
            provider: Provider name

        Returns:
            True if key was deleted, False if not found
        """
        config = self._load_config()

        if 'api_keys' not in config:
            return False

        if provider in config['api_keys']:
            del config['api_keys'][provider]
            self._save_config(config)
            return True

        return False

    def list_providers(self) -> list:
        """List configured providers (without showing keys).

        Returns:
            List of provider names
        """
        config = self._load_config()
        return list(config.get('api_keys', {}).keys())

    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys.

        Returns:
            Dictionary of provider -> api_key
        """
        config = self._load_config()
        return config.get('api_keys', {})
