"""
Prompt template manager.

Loads built-in/user prompts and handles ChatML parsing and variable substitution.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.app_paths import get_resource_dir, get_user_data_dir
from core.chatml_parser import ChatMLParser


logger = logging.getLogger(__name__)


class PromptManager:
    """Prompt template manager."""

    def __init__(self, prompts_path: Optional[str] = None, user_prompts_path: Optional[str] = None):
        """Initialize PromptManager.

        Args:
            prompts_path: Built-in prompts file. Defaults to the bundled
                resources/default_prompts.json.
            user_prompts_path: User prompt overrides. Installed builds use
                %LOCALAPPDATA%/Quill/user_prompts.json, while portable builds use
                ./data/user_prompts.json beside Quill.exe.
        """
        if prompts_path is None:
            prompts_path = get_resource_dir() / "default_prompts.json"
        if user_prompts_path is None:
            user_prompts_path = get_user_data_dir() / "user_prompts.json"

        self.prompts_path = Path(prompts_path)
        self.user_prompts_path = Path(user_prompts_path)

        self.default_prompts: Dict[str, Dict[str, Any]] = {}
        self.user_prompts: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.parser = ChatMLParser()

        logger.debug("PromptManager initialized")
        logger.debug("  Default prompts: %s", self.prompts_path)
        logger.debug("  User prompts: %s", self.user_prompts_path)

        self.load()

    def load(self) -> None:
        """Load built-in prompts and optional user overrides."""
        if not self.prompts_path.exists():
            logger.error("Default prompts file not found: %s", self.prompts_path)
            raise FileNotFoundError(f"Default prompts file not found: {self.prompts_path}")

        try:
            with self.prompts_path.open("r", encoding="utf-8") as file:
                self.default_prompts = json.load(file)
            logger.info("Loaded %s default prompts", len(self.default_prompts))
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in default prompts file: %s", exc)
            raise

        self.user_prompts = {}
        if self.user_prompts_path.exists():
            try:
                with self.user_prompts_path.open("r", encoding="utf-8") as file:
                    self.user_prompts = json.load(file)
                logger.info("Loaded %s user prompts", len(self.user_prompts))
            except json.JSONDecodeError as exc:
                logger.warning("Invalid JSON in user prompts file, ignoring: %s", exc)
            except Exception as exc:
                logger.warning("Error loading user prompts, ignoring: %s", exc)

        self._merge_prompts()

    def _merge_prompts(self) -> None:
        """Merge built-in and user prompts, preferring user overrides."""
        self.prompts = {}

        for key, value in self.default_prompts.items():
            self.prompts[key] = value.copy()

        for key, value in self.user_prompts.items():
            self.prompts[key] = value.copy()

        logger.debug("Merged prompts: %s total", len(self.prompts))

    def get_prompt_keys(self) -> List[str]:
        """Return all available prompt keys."""
        return list(self.prompts.keys())

    def get_prompt_info(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """Return prompt metadata for a key."""
        return self.prompts.get(prompt_key)

    def get_messages(
        self,
        prompt_key: str,
        text: str,
        instruction: str = "",
    ) -> List[Dict[str, str]]:
        """Render a prompt into OpenAI-compatible messages."""
        prompt_info = self.get_prompt_info(prompt_key)
        if not prompt_info:
            logger.error("Unknown prompt key: %s", prompt_key)
            raise ValueError(f"Unknown prompt key: {prompt_key}")

        template = prompt_info["template"]
        variables = {
            "text": text,
            "instruction": instruction,
        }

        messages = self.parser.parse_and_substitute(template, variables)
        logger.debug("Generated %s messages for prompt: %s", len(messages), prompt_key)
        return messages

    def get_temperature(self, prompt_key: str) -> float:
        """Return the configured temperature for a prompt."""
        prompt_info = self.get_prompt_info(prompt_key)
        if not prompt_info:
            return 0.7
        return prompt_info.get("temperature", 0.7)

    def get_model(self, prompt_key: str) -> Optional[str]:
        """Return an optional model override for a prompt."""
        prompt_info = self.get_prompt_info(prompt_key)
        if not prompt_info:
            return None

        model = prompt_info.get("model", "")
        if not isinstance(model, str):
            return None

        model = model.strip()
        return model or None

    def add_prompt(
        self,
        prompt_key: str,
        name: str,
        template: str,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> None:
        """Add a new user prompt."""
        new_prompt = {
            "name": name,
            "template": template,
            "temperature": temperature,
        }
        if model and model.strip():
            new_prompt["model"] = model.strip()

        self.user_prompts[prompt_key] = new_prompt
        self.prompts[prompt_key] = new_prompt.copy()
        logger.info("Added user prompt: %s", prompt_key)

    def update_prompt(
        self,
        prompt_key: str,
        name: Optional[str] = None,
        template: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
    ) -> None:
        """Update an existing prompt and store the changes as a user override."""
        if prompt_key not in self.prompts:
            raise ValueError(f"Unknown prompt key: {prompt_key}")

        if prompt_key not in self.user_prompts:
            self.user_prompts[prompt_key] = self.prompts[prompt_key].copy()

        if name is not None:
            self.user_prompts[prompt_key]["name"] = name
            self.prompts[prompt_key]["name"] = name
        if template is not None:
            self.user_prompts[prompt_key]["template"] = template
            self.prompts[prompt_key]["template"] = template
        if temperature is not None:
            self.user_prompts[prompt_key]["temperature"] = temperature
            self.prompts[prompt_key]["temperature"] = temperature
        if model is not None:
            normalized_model = model.strip()
            if normalized_model:
                self.user_prompts[prompt_key]["model"] = normalized_model
                self.prompts[prompt_key]["model"] = normalized_model
            else:
                self.user_prompts[prompt_key].pop("model", None)
                self.prompts[prompt_key].pop("model", None)

        logger.info("Updated user prompt: %s", prompt_key)

    def save(self) -> None:
        """Save user prompt overrides to disk."""
        if not self.user_prompts:
            if self.user_prompts_path.exists():
                self.user_prompts_path.unlink()
                logger.info("Removed empty user prompt overrides file")
            else:
                logger.debug("No user prompts to save")
            return

        self.user_prompts_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.user_prompts_path.open("w", encoding="utf-8") as file:
                json.dump(self.user_prompts, file, indent=2, ensure_ascii=False)
            logger.info("User prompts saved to %s", self.user_prompts_path)
        except Exception as exc:
            logger.error("Error saving user prompts: %s", exc)
            raise

    def reset_prompt(self, prompt_key: str) -> None:
        """Reset a prompt to its built-in value."""
        if prompt_key in self.user_prompts:
            del self.user_prompts[prompt_key]
            logger.info("Reset prompt to default: %s", prompt_key)

        if prompt_key in self.default_prompts:
            self.prompts[prompt_key] = self.default_prompts[prompt_key].copy()
        elif prompt_key in self.prompts:
            del self.prompts[prompt_key]

    def is_user_modified(self, prompt_key: str) -> bool:
        """Return whether a prompt has a user override."""
        return prompt_key in self.user_prompts


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("\n=== Testing PromptManager ===\n")
    pm = PromptManager()

    print("1. Available prompts:")
    for key in pm.get_prompt_keys():
        info = pm.get_prompt_info(key)
        print(f"   - {key}: {info['name']} (temp={info['temperature']})")

    print("\n2. Testing grammar_check prompt...")
    text = "I are student and you is teacher."
    messages = pm.get_messages("grammar_check", text)
    print(f"   Generated {len(messages)} messages:")
    for message in messages:
        print(f"   [{message['role']}]: {message['content'][:50]}...")

    print("\n3. Testing rewrite prompt with instruction...")
    text = "The cat sat on the mat."
    instruction = "Make it more dramatic and exciting"
    messages = pm.get_messages("rewrite", text, instruction)
    print(f"   Generated {len(messages)} messages")
    user_content = messages[0]["content"] if messages else ""
    print(f"   User message includes text: {text in user_content}")

    print("\n4. Testing temperature values...")
    print(f"   grammar_check: {pm.get_temperature('grammar_check')}")
    print(f"   rewrite: {pm.get_temperature('rewrite')}")
    print(f"   summarize: {pm.get_temperature('summarize')}")

    print("\n5. Testing custom prompt addition...")
    pm.add_prompt(
        "test_custom",
        "Test Custom",
        "<|im_start|>system\nTest system message\n<|im_end|>\n<|im_start|>user\n{{text}}\n<|im_end|>",
        temperature=0.5,
    )
    assert "test_custom" in pm.get_prompt_keys()
    print("   [OK] Custom prompt added")

    print("\n[OK] All PromptManager tests passed!")
