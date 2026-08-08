import json
import tempfile
import unittest
from pathlib import Path

from core.prompt_manager import PromptManager


class CustomActionTests(unittest.TestCase):
    def _create_manager(self, root: Path) -> PromptManager:
        defaults = root / "default_prompts.json"
        user = root / "user_prompts.json"
        defaults.write_text(
            json.dumps(
                {
                    "rewrite": {
                        "name": "Rewrite",
                        "template": "<|im_start|>user\n{{text}}\n<|im_end|>",
                        "temperature": 0.5,
                    }
                }
            ),
            encoding="utf-8",
        )
        return PromptManager(str(defaults), str(user))

    def test_custom_action_round_trip_and_rendering(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manager = self._create_manager(root)

            action_key = manager.add_custom_action(
                "Discord Reply",
                template=(
                    "<|im_start|>system\nWrite a natural Discord reply.\n<|im_end|>\n"
                    "<|im_start|>user\n{{text}}\n<|im_end|>"
                ),
                temperature=0.4,
                model="fast-model",
                hotkey="<ctrl>+<alt>+d",
                show_in_popup=True,
            )
            manager.save()

            self.assertTrue(manager.is_custom_action(action_key))
            self.assertEqual(
                manager.get_custom_action_hotkeys()[action_key],
                "<ctrl>+<alt>+d",
            )
            self.assertEqual(manager.get_model(action_key), "fast-model")
            self.assertEqual(manager.get_temperature(action_key), 0.4)

            messages = manager.get_messages(action_key, "hello")
            self.assertEqual(messages[-1]["content"], "hello")

            reloaded = PromptManager(
                str(root / "default_prompts.json"),
                str(root / "user_prompts.json"),
            )
            actions = reloaded.get_custom_actions(visible_only=True)
            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0]["key"], action_key)
            self.assertEqual(actions[0]["name"], "Discord Reply")

    def test_custom_action_can_be_hidden_updated_and_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manager = self._create_manager(root)

            action_key = manager.add_custom_action("Casual")
            manager.update_custom_action(
                action_key,
                name="Very Casual",
                template=(
                    "<|im_start|>system\nMake it casual.\n<|im_end|>\n"
                    "<|im_start|>user\n{{text}}\n<|im_end|>"
                ),
                temperature=0.8,
                model="",
                hotkey="",
                show_in_popup=False,
            )

            self.assertEqual(manager.get_custom_actions(visible_only=True), [])
            self.assertEqual(
                manager.get_prompt_info(action_key)["name"],
                "Very Casual",
            )

            manager.save()
            manager.delete_custom_action(action_key)
            manager.save()

            reloaded = PromptManager(
                str(root / "default_prompts.json"),
                str(root / "user_prompts.json"),
            )
            self.assertIsNone(reloaded.get_prompt_info(action_key))

    def test_custom_action_validation_rejects_duplicate_names_and_missing_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manager = self._create_manager(root)

            manager.add_custom_action("Fix PT-BR")

            with self.assertRaises(ValueError):
                manager.add_custom_action("fix pt-br")

            with self.assertRaises(ValueError):
                manager.add_custom_action(
                    "Broken",
                    template=(
                        "<|im_start|>user\nNo selected text here.\n<|im_end|>"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
