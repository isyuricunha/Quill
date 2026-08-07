"""Prompt template management for Bragi."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.app_paths import get_resource_dir, get_user_data_dir
from core.chatml_parser import ChatMLParser
from core.prompt_migrations import migrate_legacy_prompt_overrides


logger = logging.getLogger(__name__)


class PromptManager:
    """Load built-in prompts, user overrides and rendered messages."""

    def __init__(
        self,
        prompts_path: Optional[str] = None,
        user_prompts_path: Optional[str] = None,
    ):
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
        logger.debug("Default prompts: %s", self.prompts_path)
        logger.debug("User prompts: %s", self.user_prompts_path)

        self.load()

    def load(self) -> None:
        """Load defaults and user overrides, then migrate known legacy defaults."""
        if not self.prompts_path.exists():
            raise FileNotFoundError(
                f"Default prompts file not found: {self.prompts_path}"
            )

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
                logger.warning("Invalid user prompts JSON, ignoring: %s", exc)
            except Exception as exc:
                logger.warning("Error loading user prompts, ignoring: %s", exc)

        if migrate_legacy_prompt_overrides(
            self.default_prompts, self.user_prompts
        ):
            self.save()

        self._merge_prompts()

    def _merge_prompts(self) -> None:
        """Merge built-in and user prompts, preferring user overrides."""
        self.prompts = {
            key: value.copy() for key, value in self.default_prompts.items()
        }
        for key, value in self.user_prompts.items():
            if isinstance(value, dict):
                self.prompts[key] = value.copy()

        logger.debug("Merged prompts: %s total", len(self.prompts))

    def get_prompt_keys(self) -> List[str]:
        return list(self.prompts.keys())

    def get_prompt_info(self, prompt_key: str) -> Optional[Dict[str, Any]]:
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
            raise ValueError(f"Unknown prompt key: {prompt_key}")

        template = prompt_info["template"]
        messages = self.parser.parse_and_substitute(
            template,
            {"text": text, "instruction": instruction},
        )
        logger.debug(
            "Generated %s messages for prompt: %s",
            len(messages),
            prompt_key,
        )
        return messages

    def get_temperature(self, prompt_key: str) -> float:
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
        new_prompt: Dict[str, Any] = {
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
        """Update a prompt and store the result as a user override."""
        if prompt_key not in self.prompts:
            raise ValueError(f"Unknown prompt key: {prompt_key}")

        if prompt_key not in self.user_prompts:
            self.user_prompts[prompt_key] = self.prompts[prompt_key].copy()

        override = self.user_prompts[prompt_key]
        merged = self.prompts[prompt_key]

        if name is not None:
            override["name"] = name
            merged["name"] = name
        if template is not None:
            override["template"] = template
            merged["template"] = template
        if temperature is not None:
            override["temperature"] = temperature
            merged["temperature"] = temperature
        if model is not None:
            normalized_model = model.strip()
            if normalized_model:
                override["model"] = normalized_model
                merged["model"] = normalized_model
            else:
                override.pop("model", None)
                merged.pop("model", None)

        logger.info("Updated user prompt: %s", prompt_key)

    def save(self) -> None:
        """Persist user prompt overrides."""
        if not self.user_prompts:
            if self.user_prompts_path.exists():
                self.user_prompts_path.unlink()
                logger.info("Removed empty user prompt overrides file")
            return

        self.user_prompts_path.parent.mkdir(parents=True, exist_ok=True)
        with self.user_prompts_path.open("w", encoding="utf-8") as file:
            json.dump(self.user_prompts, file, indent=2, ensure_ascii=False)
        logger.info("User prompts saved to %s", self.user_prompts_path)

    def reset_prompt(self, prompt_key: str) -> None:
        """Reset a prompt to its current built-in default."""
        if prompt_key in self.user_prompts:
            del self.user_prompts[prompt_key]
            logger.info("Reset prompt to default: %s", prompt_key)

        if prompt_key in self.default_prompts:
            self.prompts[prompt_key] = self.default_prompts[prompt_key].copy()
        elif prompt_key in self.prompts:
            del self.prompts[prompt_key]

    def is_user_modified(self, prompt_key: str) -> bool:
        return prompt_key in self.user_prompts
