# Configuration

Open **Settings** from the Bragi tray menu.

## General

### Start Bragi with Windows

Creates a per-user entry under the Windows `Run` registry key. Administrator privileges are not required.

When upgrading from Quill, an existing enabled `Quill` startup entry is migrated to `Bragi`.

### Translation target language

The Translate action uses a configurable target language. Bragi includes common choices such as Portuguese (Brazil), English, Spanish, French, German, Italian, Japanese, Korean, Chinese and Russian, but the field is editable and accepts any target language description.

### Update checks

`Check for updates when Bragi starts` performs one lightweight GitHub Releases check after launch. If no update exists, the automatic check is silent.

## API

### Base URL

Enter the root of an OpenAI-compatible API. Bragi appends the chat-completions route internally.

Examples:

```text
https://api.openai.com/v1
http://localhost:11434/v1
http://localhost:8080/v1
```

### API key

The API key is stored encrypted with Windows DPAPI. Leaving the API-key field empty while editing settings keeps the currently stored key.

### Global model

The model field is the default model used by all prompts and Custom Actions that do not have a Model Override.

### Additional Params

Extra request parameters can be supplied as a JSON object:

```json
{
  "reasoning_effort": "low",
  "top_p": 0.9
}
```

Do not use Additional Params as the primary way to choose a model. Bragi applies its global or per-action model after these parameters are merged.

## Hotkey

The Hotkey tab contains:

- Main Hotkey
- Quick Repeat
- built-in Direct Action Hotkeys

Custom Action hotkeys are configured with each action under **Custom Actions**.

Shortcuts must include Ctrl, Shift or Alt. Bragi rejects duplicate shortcuts across the main hotkey, Quick Repeat, built-in direct actions and Custom Actions, as well as critical Windows combinations.

See [Hotkeys](hotkeys.md).

## Custom Actions

The Custom Actions tab lets you create reusable actions with:

- name
- temperature
- optional model override
- optional direct hotkey
- popup visibility
- ChatML prompt template

Every Custom Action prompt must contain `{{text}}`.

See [Custom Actions](custom-actions.md).

## Prompts

Every built-in prompt exposes:

- display name
- temperature
- optional model override
- ChatML template
- reset to default

Leaving the model override empty uses the global API model.

User prompt changes and Custom Actions are written to `user_prompts.json`; built-in defaults remain in `resources/default_prompts.json`.

See [Actions and Prompts](actions-and-prompts.md).

## Configuration files

Installed builds:

```text
%LOCALAPPDATA%\Bragi\config.json
%LOCALAPPDATA%\Bragi\user_prompts.json
```

Portable builds:

```text
<Bragi folder>\data\config.json
<Bragi folder>\data\user_prompts.json
```

See [Updates and Data](updates-and-data.md) for migration details.
