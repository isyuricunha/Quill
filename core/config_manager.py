"""
Configuration file manager.

Handles loading/saving JSON settings and protects the API key through CryptoManager.
"""

import copy
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core.app_paths import get_user_data_dir
from core.crypto_manager import CryptoManager


logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration file manager."""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "api": {
            "base_url": "https://api.openai.com/v1",
            "api_key_encrypted": "",
            "model": "gpt-4",
            "additional_params": {},
        },
        "hotkey": {
            "key": "<ctrl>+<space>",
            "quick_key": "<ctrl>+<shift>+<space>",
            "enabled": True,
        },
        "ui": {
            "theme": "dark",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize ConfigManager.

        Args:
            config_path: Explicit config file path. When omitted, installed builds
                use %LOCALAPPDATA%/Bragi/config.json and portable builds use
                ./data/config.json beside Bragi.exe.
        """
        if config_path is None:
            config_path = get_user_data_dir() / "config.json"

        self.config_path = Path(config_path)
        self.crypto = CryptoManager()
        self._config: Dict[str, Any] = {}

        logger.debug("ConfigManager initialized with path: %s", self.config_path)

    def is_configured(self) -> bool:
        """Return whether a valid configuration file already exists."""
        if not self.config_path.exists():
            logger.debug("Config file does not exist")
            return False

        try:
            config = self.load()
            api_config = config.get("api", {})
            base_url = api_config.get("base_url", "")
            model = api_config.get("model", "")
            is_valid = bool(base_url and model)
            logger.debug(
                "Config file exists, configured: %s (base_url=%s, model=%s)",
                is_valid,
                bool(base_url),
                bool(model),
            )
            return is_valid
        except Exception as exc:
            logger.error("Error checking configuration: %s", exc)
            return False

    def load(self) -> Dict[str, Any]:
        """Load configuration from disk."""
        if not self.config_path.exists():
            logger.warning("Config file not found: %s", self.config_path)
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                self._config = json.load(file)
            logger.info("Configuration loaded successfully from %s", self.config_path)
            return self._config
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in config file: %s", exc)
            raise
        except Exception as exc:
            logger.error("Error loading config: %s", exc)
            raise

    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to disk."""
        if config is not None:
            self._config = config

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.config_path.open("w", encoding="utf-8") as file:
                json.dump(self._config, file, indent=2, ensure_ascii=False)
            logger.info("Configuration saved to %s", self.config_path)
        except Exception as exc:
            logger.error("Error saving config: %s", exc)
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self._config

        for part in keys:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                logger.debug("Key not found: %s, returning default: %s", key, default)
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        target = self._config

        for part in keys[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        target[keys[-1]] = value
        logger.debug("Set config: %s = %s", key, value)

    def get_api_key(self) -> str:
        """Decrypt and return the configured API key."""
        encrypted_key = self.get("api.api_key_encrypted", "")
        if not encrypted_key:
            logger.warning("No API key found in config")
            return ""

        try:
            decrypted = self.crypto.decrypt(encrypted_key)
            logger.debug("API key decrypted successfully")
            return decrypted
        except Exception as exc:
            logger.error("Failed to decrypt API key: %s", exc)
            raise RuntimeError("Failed to decrypt API key") from exc

    def set_api_key(self, api_key: str) -> None:
        """Encrypt and store an API key in the current configuration."""
        try:
            encrypted = self.crypto.encrypt(api_key)
            self.set("api.api_key_encrypted", encrypted)
            logger.debug("API key encrypted and set successfully")
        except Exception as exc:
            logger.error("Failed to encrypt API key: %s", exc)
            raise RuntimeError("Failed to encrypt API key") from exc

    def create_default_config(self) -> None:
        """Create and save a fresh default configuration."""
        logger.info("Creating default config")
        self._config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """Return a shallow copy of the full configuration."""
        return self._config.copy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_config_path = Path(__file__).parent.parent / "data" / "test_config.json"
    config = ConfigManager(test_config_path)

    print("\n=== Testing ConfigManager ===\n")

    print("1. Creating default config...")
    config.create_default_config()
    print(f"   Config file created at: {test_config_path}")

    print("\n2. Setting API key...")
    test_api_key = "sk-test-my-secret-api-key-1234567890"
    config.set_api_key(test_api_key)
    config.save()
    print(f"   API key set: {test_api_key[:15]}...")

    print("\n3. Loading config...")
    config.load()
    print(f"   Config version: {config.get('version')}")
    print(f"   Base URL: {config.get('api.base_url')}")
    print(f"   Model: {config.get('api.model')}")
    print(f"   Hotkey: {config.get('hotkey.key')}")

    print("\n4. Decrypting API key...")
    decrypted_key = config.get_api_key()
    print(f"   Decrypted: {decrypted_key[:15]}...")

    assert test_api_key == decrypted_key, "API key encryption/decryption test failed!"
    print("\n[OK] All tests passed!")
    print(f"\nTest config file saved at: {test_config_path}")
