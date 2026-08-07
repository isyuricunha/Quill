# Development

This document covers local development, tests, Windows packaging, and the source layout for Quill.

## Environment

Published releases are built on GitHub Actions using:

```text
Windows latest
Python 3.12
```

Using Python 3.12 locally is recommended when reproducing release behavior.

## Clone

```powershell
git clone https://github.com/isyuricunha/Quill.git
cd Quill
```

## Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Main runtime dependencies include:

- PySide6
- pynput
- pyperclip
- cryptography
- httpx
- darkdetect

## Run from source

```powershell
python main.py
```

Development mode keeps user data in:

```text
<repository>\data
```

The Start with Windows feature, when used from source, stores a command that launches `main.py` through the current Python executable.

## Source compilation check

The release workflow first verifies that the Python source can compile:

```powershell
python -m compileall -q core app ui main.py
```

Treat any non-zero result as a release blocker.

## Unit tests

Run:

```powershell
python -m unittest discover -s tests -v
```

Current tests cover important behavior such as:

- installed and portable paths
- legacy data migration
- update-version behavior
- optional per-prompt model overrides
- prompt migration and safe ChatML substitution
- Professional prompt registration and optional hotkey behavior

New features should include focused tests whenever their logic can be exercised without driving the full GUI.

## Build the Windows application

Install runtime requirements first, then run:

```powershell
python build.py
```

`build.py` installs PyInstaller automatically if it is not already available.

The build output is:

```text
dist\Quill\
```

The executable is:

```text
dist\Quill\Quill.exe
```

Quill uses a PyInstaller `onedir` build, so the entire `dist\Quill` directory is required.

## PyInstaller configuration

The build script includes:

```text
--onedir
--windowed
--name=Quill
--clean
```

It bundles:

- default prompts
- embedded version file
- application icons

It explicitly collects internal packages:

```text
core
app
ui
```

It also explicitly includes `core.prompt_manager` and the required PySide6 modules.

This explicit collection exists to prevent a build from succeeding while silently omitting an internal module.

## Packaged executable smoke test

Published releases run:

```powershell
dist\Quill\Quill.exe --smoke-test
```

The release workflow waits for the process and rejects the release if the smoke test returns a non-zero exit code.

This is important because a source test can pass even when PyInstaller packaging is incomplete.

## Build the installer locally

The installer definition is:

```text
installer.iss
```

It requires Inno Setup.

The release workflow invokes `ISCC.exe` with an application version define equivalent to:

```powershell
ISCC.exe /DAppVersion=1.2.3 installer.iss
```

The resulting setup file is placed under:

```text
installer-output\Quill-v1.2.3-setup-windows-x64.exe
```

The installer is configured as:

- per-user
- no administrator privileges required
- x64-compatible
- installed under `%LOCALAPPDATA%\Programs\Quill`

## Portable package

The portable release is a ZIP of the complete `dist\Quill` directory contents.

Published filename:

```text
Quill-vX.Y.Z-portable-windows-x64.zip
```

## Project layout

```text
Quill/
├── .github/
│   └── workflows/
│       └── release.yml
├── app/
│   ├── application.py
│   ├── hotkey_manager.py
│   ├── text_processor.py
│   └── tray_manager.py
├── core/
│   ├── ai_provider.py
│   ├── app_paths.py
│   ├── chatml_parser.py
│   ├── config_manager.py
│   ├── crypto_manager.py
│   ├── hotkey_defaults.py
│   ├── prompt_manager.py
│   ├── startup_manager.py
│   └── update_manager.py
├── docs/
├── resources/
│   ├── default_prompts.json
│   ├── version.txt
│   ├── icon.ico
│   └── icon_alpha.ico
├── tests/
├── ui/
│   ├── direct_hotkey_settings.py
│   ├── onboarding_window.py
│   ├── popup_window.py
│   ├── settings_window.py
│   └── styles.py
├── build.py
├── installer.iss
├── main.py
└── requirements.txt
```

## User-data paths during development

Non-frozen development runs are treated like portable mode for user-data storage:

```text
<repository>\data\config.json
<repository>\data\user_prompts.json
```

The `data` directory is runtime data, not application source.

## Prompt development

Bundled prompts are defined in:

```text
resources/default_prompts.json
```

When editing a prompt, preserve the intended distinction between system instructions and user data.

The current parser supports:

```text
{{text}}
{{instruction}}
```

ChatML is parsed before those variables are inserted.

See [Actions and Prompts](actions-and-prompts.md).

## Release-safe commit strategy

The Auto Release workflow runs on every push to `main`.

Because `feat:`, `fix:`, `perf:`, and `refactor:` commits can create releases, multi-file features should preferably land as one atomic commit when possible.

Documentation-only work should use `docs:` so the workflow can validate the repository without publishing a new version.

See [Release Process](release-process.md).

## Before pushing a code change

Recommended minimum local checks:

```powershell
python -m compileall -q core app ui main.py
python -m unittest discover -s tests -v
```

For packaging changes also run:

```powershell
python build.py
dist\Quill\Quill.exe --smoke-test
```

## Coding direction

Quill is intentionally focused.

Prefer changes that improve selected-text writing workflows, reliability, configuration, prompts, packaging, or Windows integration without turning the application into a general-purpose AI chat client.
