import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


if "httpx" not in sys.modules:
    fake_httpx = types.ModuleType("httpx")

    class _HttpxClient:
        pass

    class _HttpxResponse:
        pass

    class _HTTPStatusError(Exception):
        pass

    class _TimeoutException(Exception):
        pass

    class _RequestError(Exception):
        pass

    fake_httpx.Client = _HttpxClient
    fake_httpx.Response = _HttpxResponse
    fake_httpx.HTTPStatusError = _HTTPStatusError
    fake_httpx.TimeoutException = _TimeoutException
    fake_httpx.RequestError = _RequestError
    sys.modules["httpx"] = fake_httpx

from core.ai_provider import OAICompatibleProvider
from core.prompt_manager import PromptManager


class _FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": "ok"}}]}


class _FakeClient:
    def __init__(self):
        self.last_payload = None

    def post(self, path, json):
        self.last_payload = json
        return _FakeResponse()

    def close(self):
        pass


class ModelOverrideTests(unittest.TestCase):
    def _create_prompt_manager(self, root: Path) -> PromptManager:
        defaults = root / "default_prompts.json"
        user = root / "user_prompts.json"
        defaults.write_text(
            json.dumps(
                {
                    "rewrite": {
                        "name": "Rewrite",
                        "template": "<|im_start|>user\n{{text}}\n<|im_end|>",
                        "temperature": 0.7,
                    }
                }
            ),
            encoding="utf-8",
        )
        return PromptManager(str(defaults), str(user))

    def test_prompt_model_override_is_optional_and_persistent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manager = self._create_prompt_manager(root)

            self.assertIsNone(manager.get_model("rewrite"))

            manager.update_prompt("rewrite", model="fast-model")
            manager.save()
            self.assertEqual(manager.get_model("rewrite"), "fast-model")

            reloaded = PromptManager(
                str(root / "default_prompts.json"),
                str(root / "user_prompts.json"),
            )
            self.assertEqual(reloaded.get_model("rewrite"), "fast-model")

            reloaded.update_prompt("rewrite", model="")
            reloaded.save()
            self.assertIsNone(reloaded.get_model("rewrite"))

    def test_provider_uses_override_without_changing_global_model(self):
        provider = OAICompatibleProvider()
        fake_client = _FakeClient()
        provider.base_url = "https://example.invalid/v1"
        provider.model = "global-model"
        provider.client = fake_client

        result = provider.complete(
            [{"role": "user", "content": "hello"}],
            model="prompt-model",
        )

        self.assertEqual(result, "ok")
        self.assertEqual(fake_client.last_payload["model"], "prompt-model")
        self.assertEqual(provider.model, "global-model")

        provider.complete([{"role": "user", "content": "hello"}])
        self.assertEqual(fake_client.last_payload["model"], "global-model")


if __name__ == "__main__":
    unittest.main()
