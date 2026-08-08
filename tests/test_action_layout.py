import json
import tempfile
import unittest
from pathlib import Path

from core.action_layout import (
    BUILTIN_POPUP_ACTION_ORDER,
    POPUP_ACTION_HIDDEN_KEY,
    POPUP_ACTION_ORDER_KEY,
    get_popup_action_layout,
    get_visible_popup_actions,
    normalize_popup_layout,
    restore_builtin_defaults,
)
from core.prompt_manager import PromptManager


class _Config:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)


class PopupActionLayoutTests(unittest.TestCase):
    def _create_manager(self, root: Path) -> PromptManager:
        defaults = root / "default_prompts.json"
        user = root / "user_prompts.json"
        prompts = {}
        for key in BUILTIN_POPUP_ACTION_ORDER:
            prompts[key] = {
                "name": key.replace("_", " ").title(),
                "template": "<|im_start|>user\n{{text}}\n<|im_end|>",
                "temperature": 0.5,
            }
        prompts["custom"] = {
            "name": "Custom",
            "template": "<|im_start|>user\n{{text}}\n<|im_end|>",
            "temperature": 0.7,
        }
        defaults.write_text(json.dumps(prompts), encoding="utf-8")
        return PromptManager(str(defaults), str(user))

    def test_saved_layout_can_reorder_and_hide_builtins(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_manager(Path(temp_dir))
            config = _Config(
                {
                    POPUP_ACTION_ORDER_KEY: [
                        "professional",
                        "grammar_check",
                        "rewrite",
                        "translate",
                        "summarize",
                    ],
                    POPUP_ACTION_HIDDEN_KEY: ["summarize"],
                }
            )

            visible = get_visible_popup_actions(config, manager)
            self.assertEqual(
                [action["key"] for action in visible],
                [
                    "professional",
                    "grammar_check",
                    "rewrite",
                    "translate",
                ],
            )

    def test_legacy_custom_visibility_is_migrated_when_no_layout_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_manager(Path(temp_dir))
            visible_key = manager.add_custom_action("Visible")
            hidden_key = manager.add_custom_action("Hidden", show_in_popup=False)

            order, hidden = get_popup_action_layout(_Config(), manager)

            self.assertEqual(order[:5], list(BUILTIN_POPUP_ACTION_ORDER))
            self.assertIn(visible_key, order)
            self.assertIn(hidden_key, order)
            self.assertNotIn(visible_key, hidden)
            self.assertIn(hidden_key, hidden)

    def test_new_actions_are_appended_and_stale_keys_are_removed(self):
        order, hidden = normalize_popup_layout(
            ["rewrite", "deleted", "rewrite"],
            ["deleted", "summarize"],
            ["grammar_check", "rewrite", "summarize", "custom_action_new"],
        )

        self.assertEqual(
            order,
            ["rewrite", "grammar_check", "summarize", "custom_action_new"],
        )
        self.assertEqual(hidden, ["summarize"])

    def test_restore_defaults_restores_builtins_but_preserves_custom_hidden_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_manager(Path(temp_dir))
            first_custom = manager.add_custom_action("First")
            second_custom = manager.add_custom_action("Second")

            order, hidden = restore_builtin_defaults(
                [
                    second_custom,
                    "professional",
                    "summarize",
                    first_custom,
                    "grammar_check",
                    "rewrite",
                    "translate",
                ],
                ["summarize", second_custom],
                manager,
            )

            self.assertEqual(order[:5], list(BUILTIN_POPUP_ACTION_ORDER))
            self.assertEqual(order[5:], [second_custom, first_custom])
            self.assertNotIn("summarize", hidden)
            self.assertEqual(hidden, [second_custom])


if __name__ == "__main__":
    unittest.main()
