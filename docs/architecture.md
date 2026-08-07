# Architecture

Quill is a small PySide6 Windows tray application organized into three main code areas:

```text
app/    runtime application workflow
core/   reusable configuration, API, prompt, path, update, and security logic
ui/     Qt windows, dialogs, popup, and styling
```

The executable entry point is `main.py`.

## High-level flow

A typical Grammar Check, Rewrite, Professional, Summarize, or Translate request follows this path:

```text
Global hotkey
    |
    v
HotkeyManager
    |
    v
QuillApp
    |
    v
TextProcessor
    |
    | simulate Ctrl+C
    v
Selected text
    |
    v
Popup action or direct action
    |
    v
PromptManager
    |
    v
ChatMLParser
    |
    v
OAICompatibleProvider
    |
    | POST /chat/completions
    v
Configured API
    |
    v
Model response
    |
    v
TextProcessor
    |
    | simulate Ctrl+V
    v
Original selection replaced
```

## `main.py`

Responsibilities include:

- process startup
- single-instance handling
- logging initialization
- packaged smoke-test entry behavior
- creating `QuillApp`

The published executable is built from this entry point.

## `app/application.py`

`QuillApp` is the main orchestrator.

It owns the runtime managers and coordinates:

- onboarding
- settings
- API provider configuration
- global hotkeys
- selected-text extraction
- popup actions
- direct action hotkeys
- Quick Repeat
- AI request serialization
- text replacement
- cleanup on exit

### Request serialization

Quill guards AI requests with a lock and tracks whether a request is already in progress.

This prevents multiple overlapping model responses from racing to replace the same selection.

Text extraction also has its own in-progress state so multiple hotkeys do not start competing capture operations.

## `app/hotkey_manager.py`

Uses `pynput.keyboard.GlobalHotKeys`.

It manages three categories:

- Main Hotkey
- Quick Repeat
- direct action hotkeys

Direct hotkeys emit the prompt key together with the current mouse position.

Secondary hotkeys record a short suppression timestamp so overlapping combinations do not accidentally trigger the main hotkey as well.

## `app/text_processor.py`

Text capture and replacement use standard Windows-style copy and paste simulation.

### Capture

The worker:

1. releases common modifier keys
2. backs up the clipboard
3. writes a marker to the clipboard
4. simulates `Ctrl+C`
5. waits briefly for the target application
6. reads the selection
7. restores the previous clipboard text

The marker lets Quill distinguish a real selection copy from an unchanged clipboard.

### Replacement

The worker:

1. backs up the clipboard
2. copies the model response
3. simulates `Ctrl+V`
4. restores the previous clipboard text

Each operation uses a fresh Qt worker thread.

## `app/tray_manager.py`

Owns the Windows system tray icon and menu.

Current tray actions:

- Settings
- Check for Updates
- Pause or Resume
- Quit

It also manages background update checks and installed-update downloads.

## `core/config_manager.py`

Loads and saves JSON configuration.

Important responsibilities:

- dot-notation access such as `api.model`
- default configuration creation
- API key encryption and decryption through `CryptoManager`
- installed vs portable configuration path selection through `app_paths`

## `core/app_paths.py`

Centralizes runtime paths and build-mode detection.

It distinguishes:

### Installed

Application:

```text
%LOCALAPPDATA%\Programs\Quill
```

User data:

```text
%LOCALAPPDATA%\Quill
```

### Portable

User data:

```text
<Quill folder>\data
```

It also performs conservative migration of known legacy user-data files.

## `core/crypto_manager.py`

Wraps Windows DPAPI through `ctypes`.

It uses:

- `CryptProtectData`
- `CryptUnprotectData`

The encrypted bytes are Base64 encoded for JSON storage.

## `core/prompt_manager.py`

Combines:

- bundled prompt definitions
- user prompt overrides
- prompt metadata
- optional per-prompt model override
- temperature values
- ChatML rendering

Bundled prompts come from:

```text
resources/default_prompts.json
```

User changes come from:

```text
user_prompts.json
```

The effective prompt set is built by applying user overrides over bundled defaults.

## `core/chatml_parser.py`

Parses ChatML-style blocks into OpenAI-compatible message objects.

Important design detail: ChatML roles are parsed before selected text is substituted.

That means user-selected text containing ChatML-looking tokens remains content rather than modifying the request's message structure.

Variable substitution is single-pass.

## `core/ai_provider.py`

Implements the OpenAI-compatible request client.

A request contains:

- rendered messages
- temperature
- optional max tokens
- Additional Params
- selected model

The selected model is either:

1. the prompt's optional model override, if configured
2. the global API model otherwise

The provider applies the selected model after Additional Params are merged so an accidental `model` key in Additional Params does not override Quill's explicit model selection.

## `core/update_manager.py`

Implements semantic-version update checks against the latest public GitHub Release for `isyuricunha/Quill`.

Responsibilities:

- read the embedded build version
- query the latest release
- compare semantic versions
- find the setup asset
- distinguish installed and portable behavior
- download the installed setup to a temporary directory
- launch the installer

## `core/startup_manager.py`

Registers Quill under:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

The startup command uses the packaged executable when frozen and `main.py` when running from source.

## `ui/popup_window.py`

The popup presents quick actions and the Custom Instruction editor.

Built-in buttons currently include:

- Grammar Check
- Rewrite
- Professional
- Summarize
- Translate

The Custom Instruction field sends on `Enter` and inserts a line break on `Shift+Enter`.

## Settings UI

`ui/settings_window.py` contains the base settings dialog.

`ui/direct_hotkey_settings.py` extends it with independently maintained features such as:

- translation target language
- startup update preference
- direct action hotkeys
- per-prompt model override

The extension class is the Settings window imported by `QuillApp`.

## Resources

Important bundled files:

```text
resources/default_prompts.json
resources/version.txt
resources/icon.ico
resources/icon_alpha.ico
```

The release workflow rewrites `resources/version.txt` before packaging a release.

## Packaging

`build.py` produces a PyInstaller `onedir` build under:

```text
dist/Quill
```

The build explicitly collects Quill's internal packages and critical PySide6 modules instead of relying only on PyInstaller import discovery.

The published installer is created from `installer.iss` using Inno Setup.

## Release architecture

`.github/workflows/release.yml` handles:

1. source compilation checks
2. unit tests
3. semantic version calculation
4. version embedding
5. dependency installation
6. PyInstaller build
7. packaged executable smoke test
8. portable ZIP packaging
9. Inno Setup compilation
10. release notes
11. GitHub Release publication

See [Release Process](release-process.md).
