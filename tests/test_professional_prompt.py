import json
import unittest
from pathlib import Path

from core.chatml_parser import ChatMLParser
from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS, DIRECT_ACTION_LABELS


ROOT = Path(__file__).resolve().parents[1]


class ProfessionalPromptTests(unittest.TestCase):
    def setUp(self):
        prompts_path = ROOT / "resources" / "default_prompts.json"
        with prompts_path.open("r", encoding="utf-8") as file:
            self.prompts = json.load(file)

    def test_professional_prompt_is_available(self):
        prompt = self.prompts["professional"]
        self.assertEqual(prompt["name"], "Professional")
        self.assertEqual(prompt["temperature"], 0.4)

    def test_professional_prompt_uses_system_and_user_messages(self):
        prompt = self.prompts["professional"]
        source = "mano vou ver isso amanha pq hoje n vai dar"
        messages = ChatMLParser.parse_and_substitute(
            prompt["template"],
            {"text": source, "instruction": ""},
        )

        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        self.assertIn(source, messages[1]["content"])
        self.assertIn("professional", messages[0]["content"].lower())

    def test_professional_direct_hotkey_is_optional(self):
        self.assertIn("professional", DIRECT_ACTION_HOTKEYS)
        self.assertEqual(DIRECT_ACTION_HOTKEYS["professional"], "")
        self.assertEqual(DIRECT_ACTION_LABELS["professional"], "Professional")


if __name__ == "__main__":
    unittest.main()
