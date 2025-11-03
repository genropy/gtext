"""Configuration management for gtext.

Manages two types of configuration:
1. API keys: ~/.config/gtext/apikeys.yaml (sensitive, not shared)
2. Security policies: ~/.config/gtext/config.json + .gtext/config.json (shared via git)
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, List
import json
import fnmatch

import yaml


class Config:
    """Manage gtext configuration.

    API keys are stored in ~/.config/gtext/apikeys.yaml (sensitive)
    Security policies are stored in:
    - ~/.config/gtext/config.json (global)
    - .gtext/config.json (per-project)
    """

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "gtext"
        self.apikeys_file = self.config_dir / "apikeys.yaml"
        self.security_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists with proper permissions."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(mode=0o700, parents=True)
        else:
            # Ensure directory has secure permissions
            self.config_dir.chmod(0o700)

    # ==================== API Keys Management ====================

    def _load_apikeys(self) -> Dict:
        """Load API keys from YAML file."""
        if not self.apikeys_file.exists():
            return {}

        try:
            with open(self.apikeys_file, "r") as f:
                config = yaml.safe_load(f) or {}
                return config
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
            return {}

    def _save_apikeys(self, config: Dict):
        """Save API keys to YAML file with secure permissions."""
        with open(self.apikeys_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        self.apikeys_file.chmod(0o600)

    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider.

        Args:
            provider: Provider name ('openai', 'anthropic', etc.)
            api_key: API key string
        """
        config = self._load_apikeys()

        if "api_keys" not in config:
            config["api_keys"] = {}

        config["api_keys"][provider] = api_key
        self._save_apikeys(config)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider.

        Args:
            provider: Provider name

        Returns:
            API key or None if not found
        """
        config = self._load_apikeys()
        return config.get("api_keys", {}).get(provider)

    def delete_api_key(self, provider: str) -> bool:
        """Delete API key for a provider.

        Args:
            provider: Provider name

        Returns:
            True if key was deleted, False if not found
        """
        config = self._load_apikeys()

        if "api_keys" not in config:
            return False

        if provider in config["api_keys"]:
            del config["api_keys"][provider]
            self._save_apikeys(config)
            return True

        return False

    def list_providers(self) -> list:
        """List configured providers (without showing keys).

        Returns:
            List of provider names
        """
        config = self._load_apikeys()
        return list(config.get("api_keys", {}).keys())

    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys.

        Returns:
            Dictionary of provider -> api_key
        """
        config = self._load_apikeys()
        return config.get("api_keys", {})

    # ==================== Security Policies Management ====================

    def _get_security_path(self, project_dir: Optional[Path] = None, use_global: bool = False) -> Path:
        """Get security config file path."""
        if use_global or not project_dir:
            return self.security_file
        return project_dir / ".gtext" / "config.json"

    def _load_security(self, project_dir: Optional[Path] = None, use_global: bool = False) -> Dict:
        """Load security configuration from JSON file."""
        config_path = self._get_security_path(project_dir, use_global)

        if not config_path.exists():
            return {}

        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load security config from {config_path}: {e}")
            return {}

    def _save_security(self, config: Dict, project_dir: Optional[Path] = None, use_global: bool = False):
        """Save security configuration to JSON file."""
        config_path = self._get_security_path(project_dir, use_global)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_merged_security(self, project_dir: Optional[Path] = None) -> Dict:
        """Get merged security configuration (global + project).

        Merge rules:
        - Global rules come first
        - Project rules come after
        - First-match wins during evaluation

        Args:
            project_dir: Project directory

        Returns:
            Merged configuration with ordered rules
        """
        global_cfg = self._load_security(use_global=True)
        project_cfg = self._load_security(project_dir)

        merged = {}
        all_protocols = set(global_cfg.keys()) | set(project_cfg.keys())

        for protocol in all_protocols:
            # Merge rules: global first, then project
            global_rules = global_cfg.get(protocol, {}).get("rules", [])
            project_rules = project_cfg.get(protocol, {}).get("rules", [])
            merged[protocol] = {"rules": global_rules + project_rules}

        return merged

    def add_rule(
        self,
        protocol: str,
        pattern: str,
        action: str,
        name: Optional[str] = None,
        project_dir: Optional[Path] = None,
        use_global: bool = False
    ) -> bool:
        """Add security rule.

        Args:
            protocol: Protocol name (e.g., "cli")
            pattern: Pattern to match (e.g., "date", "git *")
            action: "allow" or "deny"
            name: Optional rule name
            project_dir: Project directory
            use_global: Add to global config

        Returns:
            True if added

        Raises:
            ValueError: If pattern contains dangerous characters or action is invalid
        """
        # Validate action
        if action not in ["allow", "deny"]:
            raise ValueError(f"Invalid action: {action}. Must be 'allow' or 'deny'")

        # Validate pattern (no shell metacharacters except wildcards)
        DANGEROUS = [";", "|", "&", "$", "`", "\n", "\r", "&&", "||", ">", "<"]
        if any(c in pattern for c in DANGEROUS):
            raise ValueError(f"Pattern contains dangerous characters: {pattern}")

        config = self._load_security(project_dir, use_global)

        if protocol not in config:
            config[protocol] = {"rules": []}
        if "rules" not in config[protocol]:
            config[protocol]["rules"] = []

        # Create rule
        rule = {"pattern": pattern, "action": action}
        if name:
            rule["name"] = name

        config[protocol]["rules"].append(rule)
        self._save_security(config, project_dir, use_global)
        return True

    def remove_rule(
        self,
        protocol: str,
        identifier: str,
        project_dir: Optional[Path] = None,
        use_global: bool = False
    ) -> bool:
        """Remove security rule by index or name.

        Args:
            protocol: Protocol name
            identifier: Rule index (as string) or rule name
            project_dir: Project directory
            use_global: Remove from global config

        Returns:
            True if removed, False if not found
        """
        config = self._load_security(project_dir, use_global)
        rules = config.get(protocol, {}).get("rules", [])

        if not rules:
            return False

        # Try as index first
        try:
            index = int(identifier)
            if 0 <= index < len(rules):
                rules.pop(index)
                self._save_security(config, project_dir, use_global)
                return True
            return False
        except ValueError:
            # Not an index, try as name
            for i, rule in enumerate(rules):
                if rule.get("name") == identifier:
                    rules.pop(i)
                    self._save_security(config, project_dir, use_global)
                    return True
            return False

    def move_rule(
        self,
        protocol: str,
        identifier: str,
        direction: str,
        project_dir: Optional[Path] = None,
        use_global: bool = False
    ) -> Tuple[bool, str]:
        """Move security rule up/down/top/bottom.

        Args:
            protocol: Protocol name
            identifier: Rule index (as string) or rule name
            direction: "up", "down", "top", or "bottom"
            project_dir: Project directory
            use_global: Move in global config

        Returns:
            Tuple of (success: bool, message: str)
        """
        if direction not in ["up", "down", "top", "bottom"]:
            return (False, f"Invalid direction: {direction}")

        config = self._load_security(project_dir, use_global)
        rules = config.get(protocol, {}).get("rules", [])

        if not rules:
            return (False, "No rules found")

        # Find index
        index = None
        try:
            index = int(identifier)
            if not (0 <= index < len(rules)):
                return (False, f"Invalid index: {index}")
        except ValueError:
            # Try as name
            for i, rule in enumerate(rules):
                if rule.get("name") == identifier:
                    index = i
                    break
            if index is None:
                return (False, f"Rule not found: {identifier}")

        # Move rule
        rule = rules[index]

        if direction == "up":
            if index == 0:
                return (False, "Cannot move up (already at top)")
            rules.pop(index)
            rules.insert(index - 1, rule)
        elif direction == "down":
            if index == len(rules) - 1:
                return (False, "Cannot move down (already at bottom)")
            rules.pop(index)
            rules.insert(index + 1, rule)
        elif direction == "top":
            if index == 0:
                return (False, "Already at top")
            rules.pop(index)
            rules.insert(0, rule)
        elif direction == "bottom":
            if index == len(rules) - 1:
                return (False, "Already at bottom")
            rules.pop(index)
            rules.append(rule)

        self._save_security(config, project_dir, use_global)
        return (True, f"Moved rule {identifier} {direction}")

    def list_rules(
        self,
        protocol: str,
        project_dir: Optional[Path] = None,
        use_global: bool = False
    ) -> List[Dict]:
        """List security rules for protocol.

        Args:
            protocol: Protocol name
            project_dir: Project directory
            use_global: List from global config

        Returns:
            List of rules with index added
        """
        config = self._load_security(project_dir, use_global)
        rules = config.get(protocol, {}).get("rules", [])
        return rules

    def clear_rules(
        self,
        protocol: str,
        project_dir: Optional[Path] = None,
        use_global: bool = False
    ) -> bool:
        """Clear all security rules for protocol.

        Args:
            protocol: Protocol name
            project_dir: Project directory
            use_global: Clear from global config

        Returns:
            True if cleared, False if no rules found
        """
        config = self._load_security(project_dir, use_global)

        if protocol not in config or not config[protocol].get("rules"):
            return False

        config[protocol]["rules"] = []
        self._save_security(config, project_dir, use_global)
        return True

    def is_command_allowed(
        self,
        protocol: str,
        command: str,
        base_dir: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Check if command is allowed by security rules.

        Logic: First-match wins
        - Check each rule in order (global first, then project)
        - If pattern matches:
          - action=allow → ALLOW (return True)
          - action=deny → DENY (return False)
        - If no match → DENY (secure by default)

        Args:
            protocol: Protocol name (e.g., "cli")
            command: Command to check
            base_dir: Base directory for project config

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check shell metacharacters (always blocked)
        DANGEROUS = [";", "|", "&", "$", "`", "\n", "\r", "&&", "||", ">", "<"]
        if any(c in command for c in DANGEROUS):
            return (False, "Contains dangerous shell metacharacters")

        config = self.get_merged_security(base_dir)
        rules = config.get(protocol, {}).get("rules", [])

        if not rules:
            return (False, "No rules configured (secure by default)")

        # Check each rule in order (first-match wins)
        for i, rule in enumerate(rules):
            pattern = rule["pattern"]
            action = rule["action"]
            name = rule.get("name", "")

            # Check exact match first
            if command == pattern:
                if action == "allow":
                    reason = f"Rule #{i}"
                    if name:
                        reason += f" ({name})"
                    reason += f": exact match '{pattern}' → allow"
                    return (True, reason)
                else:  # deny
                    reason = f"Rule #{i}"
                    if name:
                        reason += f" ({name})"
                    reason += f": exact match '{pattern}' → deny"
                    return (False, reason)

            # Check pattern match (with wildcards)
            if any(c in pattern for c in ['*', '?', '[']):
                if fnmatch.fnmatch(command, pattern):
                    if action == "allow":
                        reason = f"Rule #{i}"
                        if name:
                            reason += f" ({name})"
                        reason += f": pattern '{pattern}' → allow"
                        return (True, reason)
                    else:  # deny
                        reason = f"Rule #{i}"
                        if name:
                            reason += f" ({name})"
                        reason += f": pattern '{pattern}' → deny"
                        return (False, reason)

        # No match
        return (False, "No matching rule (secure by default)")
