# Architecture

Bragi is a small PySide6 tray application. Its main workflow is intentionally simple: capture selected text, render a prompt, call an OpenAI-compatible endpoint, and paste the result back into the active application.

## Main components

### `main.py`

Application entry point. It performs the packaged smoke-test path, configures logging, acquires the single-instance lock and starts `BragiApp`.

### `app/application.py`

`BragiApp` coordinates managers and UI components. It owns application state such as the last action used by Quick Repeat and serializes AI requests so overlapping transformations are not started accidentally.

### `app/hotkey_manager.py`

Registers the main, Quick Repeat and direct-action global shortcuts through `pynput`.

### `app/text_processor.py`

Captures and replaces selected text using simulated copy/paste and temporary clipboard access. Modifier keys are released before synthetic clipboard shortcuts to reduce shortcut interference.

### `app/tray_manager.py`

Creates the tray icon and menu, manages Pause/Resume, Settings and update actions, and runs update network work outside the UI thread.

## Core services

### `core/config_manager.py`

Reads and writes `config.json`, including API settings, hotkeys and general preferences.

### `core/crypto_manager.py`

Encrypts and decrypts the API key through Windows DPAPI.

### `core/prompt_manager.py`

Loads built-in prompts, merges user overrides, applies prompt migrations and produces message arrays through the ChatML parser.

### `core/chatml_parser.py`

Parses ChatML structure before placeholder substitution. This keeps selected text inside the intended message rather than allowing it to create new message boundaries.

### `core/app_paths.py`

Centralizes installed/portable detection, resource paths, Bragi user-data paths and legacy Quill data migration.

### `core/startup_manager.py`

Manages the per-user Windows `Run` entry and migrates a legacy Quill startup entry to Bragi.

### `core/update_manager.py`

Reads the embedded version, queries GitHub Releases, locates the Windows installer asset, validates download origins, downloads updates and launches the setup executable.

### `core/single_instance.py`

Uses an OS-level file lock inside the active Bragi user-data directory to prevent duplicate running instances.

### `core/brand.py`

Contains product and compatibility constants. Keeping legacy identities centralized makes the Quill-to-Bragi transition explicit instead of scattering old names throughout the application.

## UI

- `ui/onboarding_window.py`: first-run API setup
- `ui/settings_window.py`: base settings implementation
- `ui/direct_hotkey_settings.py`: maintained Bragi settings layer for translation, updater, direct hotkeys and model overrides
- `ui/popup_window.py`: action popup shown near the cursor
- `ui/styles.py`: shared dark theme

## Request flow

```text
Global hotkey
    -> TextProcessor copies selected text
    -> BragiApp chooses popup / direct action / Quick Repeat
    -> PromptManager renders messages
    -> OAICompatibleProvider sends request
    -> BragiApp receives response
    -> TextProcessor pastes response
```

The AI request runs in a background thread so the Qt UI remains responsive.

## Persistence flow

Installed builds use `%LOCALAPPDATA%\Bragi`. Portable builds use `data` beside `Bragi.exe`.

When installed Bragi starts without a destination file, `app_paths` can copy the corresponding file from `%LOCALAPPDATA%\Quill`. Existing Bragi files are never replaced by migration.

## Build architecture

`build.py` creates a PyInstaller `onedir` package at:

```text
dist\Bragi\Bragi.exe
```

The release workflow then smoke-tests that executable, creates the portable ZIP, compiles the Inno Setup installer and publishes both artifacts.

The installer intentionally keeps the historical internal application ID from Quill so Windows recognizes Bragi as the same installed product during the rebrand upgrade.
