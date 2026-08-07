"""Migrations for prompt overrides created from older Quill defaults."""

import logging
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


LEGACY_DEFAULT_TEMPLATES = {
    "grammar_check": "<|im_start|>user\nYou are a grammar correction assistant.\n\nCorrect all grammatical errors, spelling mistakes, and punctuation issues in the text within <text> tags.\n\nRules:\n- Preserve the original meaning, tone, and structure\n- Do not add, remove, or rephrase content beyond corrections\n- If no errors exist, return the text unchanged\n- Respond in the same language as <text>\n- Return ONLY the corrected text, without any prefixes or meta-commentary\n\n<text>\n{{text}}\n</text>\n<|im_end|>",
    "rewrite": "<|im_start|>user\nYou are a professional editor.\n\nRewrite the text within <text> tags to improve clarity, readability, and flow while preserving the core meaning.\n\nRules:\n- Maintain the original intent and key information\n- Keep similar length\n- Respond in the same language as <text>\n- Return ONLY the rewritten text, without any prefixes or meta-commentary\n\n<text>\n{{text}}\n</text>\n<|im_end|>",
    "summarize": "<|im_start|>user\nYou are a summarization specialist.\n\nSummarize the text within <text> tags, capturing only the essential points.\n\nRules:\n- Be concise while including all key information\n- Write in continuous prose, not bullet points\n- Respond in the same language as <text>\n- Return ONLY the summary, without any prefixes or meta-commentary\n\n<text>\n{{text}}\n</text>\n<|im_end|>",
    "custom": "<|im_start|>user\nYou are a text processing assistant.\n\nApply the instruction within <instruction> tags to the text within <text> tags.\n\n<instruction>\n{{instruction}}\n</instruction>\n\nRules:\n- Apply the instruction ONLY to the content within <text> tags\n- Return ONLY the result, without any prefixes or meta-commentary\n\n<text>\n{{text}}\n</text>\n<|im_end|>",
}

LEGACY_TEMPERATURES = {
    "grammar_check": 0.3,
    "rewrite": 0.7,
    "summarize": 0.5,
    "translate": 0.3,
    "custom": 0.7,
}

LEGACY_TRANSLATE_PREFIX = (
    "<|im_start|>user\n"
    "You are a professional translator.\n\n"
    "Target language: "
)

LEGACY_TRANSLATE_SUFFIX = (
    "\n\nTranslate the text within <text> tags into the target language specified above.\n\n"
    "Rules:\n"
    "- Preserve the original meaning, tone, and structure\n"
    "- Keep proper nouns unchanged unless they have standard translations\n"
    "- Adapt idioms naturally for the target language\n"
    "- Return ONLY the translation, without any prefixes or meta-commentary\n\n"
    "<text>\n{{text}}\n</text>\n"
    "<|im_end|>"
)


def _legacy_translate_language(template: str) -> Optional[str]:
    """Return the target language when template is an untouched legacy Translate prompt."""
    if not template.startswith(LEGACY_TRANSLATE_PREFIX):
        return None
    if not template.endswith(LEGACY_TRANSLATE_SUFFIX):
        return None

    language = template[
        len(LEGACY_TRANSLATE_PREFIX): -len(LEGACY_TRANSLATE_SUFFIX)
    ].strip()

    if not language or "\n" in language or "\r" in language:
        return None
    return language


def migrate_legacy_prompt_overrides(
    default_prompts: Dict[str, Dict[str, Any]],
    user_prompts: Dict[str, Dict[str, Any]],
) -> bool:
    """Upgrade untouched legacy prompt templates while preserving user choices.

    Model overrides and user-adjusted temperatures are preserved. Templates that
    differ from the known old defaults are treated as intentional customizations
    and are never replaced.
    """
    changed = False

    for prompt_key, override in user_prompts.items():
        if not isinstance(override, dict):
            continue

        current_template = override.get("template")
        if not isinstance(current_template, str):
            continue

        new_default = default_prompts.get(prompt_key)
        if not isinstance(new_default, dict):
            continue

        new_template = new_default.get("template")
        if not isinstance(new_template, str):
            continue

        target_language = None
        if prompt_key == "translate":
            target_language = _legacy_translate_language(current_template)
            if target_language is None:
                continue
        elif current_template != LEGACY_DEFAULT_TEMPLATES.get(prompt_key):
            continue

        if target_language:
            new_template = new_template.replace(
                "Target language: English",
                f"Target language: {target_language}",
                1,
            )

        override["template"] = new_template

        old_temperature = LEGACY_TEMPERATURES.get(prompt_key)
        new_temperature = new_default.get("temperature")
        if (
            old_temperature is not None
            and new_temperature is not None
            and override.get("temperature") == old_temperature
        ):
            override["temperature"] = new_temperature

        changed = True
        logger.info("Migrated legacy prompt override: %s", prompt_key)

    return changed
