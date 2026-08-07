# Configuration

Quill is configured from the tray icon. Right-click the tray icon and choose **Settings**.

The settings window contains four tabs: General, API, Hotkey, and Prompts.

## General

### Start Quill with Windows

Enables a per-user Windows startup entry.

Quill stores the startup command under:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

The value name is `Quill`.

No administrator privileges are required.

### Translation target language

The **Target language** field controls the built-in Translate action.

Quill provides several common choices, including:

- Portuguese (Brazil)
- English
- Spanish
- French
- German
- Italian
- Japanese
- Korean
- Chinese (Simplified)
- Chinese (Traditional)
- Russian

The field is editable, so any target language description can be entered manually.

When the setting is saved, Quill updates the Translate prompt's `Target language:` directive.

### Check for updates when Quill starts

When enabled, Quill checks this repository's latest GitHub Release once shortly after startup.

If Quill is already current, the startup check does not display a notification.

Manual update checks are always available from the tray menu.

## API

### Base URL

The base URL for an OpenAI-compatible API.

Examples:

```text
https://api.openai.com/v1
http://localhost:11434/v1
http://localhost:8080/v1
```

Quill sends requests to the compatible `/chat/completions` interface relative to this configured endpoint.

### API Key

The key used by the configured endpoint.

The value is encrypted before it is written to `config.json` using Windows DPAPI.

If the API Key field in Settings is left empty, Quill keeps the existing stored key.

Some local endpoints do not require a key.

### Model

The global default model name.

Quill does not use a fixed provider model list. Enter the identifier expected by your endpoint.

Each prompt can optionally override the global model from the Prompts tab.

### Additional Params

Additional request parameters can be supplied as a JSON object.

Example:

```json
{
  "reasoning_effort": "low",
  "top_p": 0.9
}
```

The value must be a JSON object.

Common use cases include provider-specific options, reasoning settings, sampling parameters, and compatible extensions.

Do not use Additional Params as the primary place to select a model. Quill applies the global or per-prompt model after Additional Params are merged into the request payload.

## Hotkey

### Main Hotkey

Default:

```text
<ctrl>+<space>
```

Opens the Quill popup after extracting the currently selected text.

### Quick Repeat

Default:

```text
<ctrl>+<shift>+<space>
```

Repeats the most recently used action on the current selection without opening the popup.

Leave the field empty to disable Quick Repeat.

### Direct Action Hotkeys

Direct actions bypass the popup.

Current defaults:

| Action | Default |
| --- | --- |
| Grammar Check | `<ctrl>+<alt>+g` |
| Rewrite | `<ctrl>+<alt>+r` |
| Professional | Disabled |
| Translate | `<ctrl>+<alt>+t` |

Leave any direct action field empty to disable it.

See [Hotkeys](hotkeys.md) for syntax, validation, and conflicts.

## Prompts

The Prompts tab exposes the effective prompt definitions used by Quill.

For each prompt you can configure:

- **Name**
- **Temperature** from `0.0` to `2.0`
- **Model override (optional)**
- **Template**

### Model override

Leave the field empty to use the global model configured in the API tab.

If a model is entered, only that prompt uses the override.

Example:

```text
Global model: fast-general-model
Grammar Check: empty, uses global model
Rewrite: stronger-writing-model
Translate: translation-model
```

The Base URL and API key remain global. The override changes only the model for that request.

### Reset to Default

**Reset to Default** removes the user override for the selected built-in prompt and restores the bundled version.

### Apply Changes

**Apply Changes** validates and writes the selected prompt to `user_prompts.json`.

Saving the Settings dialog also saves the currently selected prompt.

## Configuration files

### Installed build

```text
%LOCALAPPDATA%\Quill\config.json
%LOCALAPPDATA%\Quill\user_prompts.json
```

### Portable build

```text
<Quill folder>\data\config.json
<Quill folder>\data\user_prompts.json
```

`user_prompts.json` only exists when user prompt overrides need to be stored.

## Important configuration keys

A typical configuration contains values conceptually equivalent to:

```json
{
  "api": {
    "base_url": "https://api.example.com/v1",
    "api_key_encrypted": "...",
    "model": "model-name",
    "additional_params": {}
  },
  "hotkey": {
    "key": "<ctrl>+<space>",
    "quick_key": "<ctrl>+<shift>+<space>",
    "actions": {
      "grammar_check": "<ctrl>+<alt>+g",
      "rewrite": "<ctrl>+<alt>+r",
      "professional": "",
      "translate": "<ctrl>+<alt>+t"
    }
  },
  "translation": {
    "target_language": "English"
  },
  "startup": {
    "enabled": false
  },
  "updates": {
    "check_on_startup": true
  }
}
```

The encrypted API key is machine and Windows-user-context dependent because it uses DPAPI.

## Related documentation

- [Actions and Prompts](actions-and-prompts.md)
- [Hotkeys](hotkeys.md)
- [Updates and Data](updates-and-data.md)
- [Security and Privacy](security-and-privacy.md)
