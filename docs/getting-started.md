# Getting Started

Quill is a Windows tray utility that processes selected text with an OpenAI-compatible API and replaces the original selection with the result.

## Requirements

- Windows 10 or Windows 11
- 64-bit Windows for published releases
- An OpenAI-compatible API endpoint
- A model name accepted by that endpoint
- An API key if your endpoint requires one

## Choose a build

The latest release contains two Windows x64 packages.

### Installer

File pattern:

```text
Quill-vX.Y.Z-setup-windows-x64.exe
```

The installer:

- installs for the current Windows user
- does not require administrator privileges
- uses `%LOCALAPPDATA%\Programs\Quill`
- creates a Start Menu shortcut
- optionally creates a desktop shortcut
- supports the in-app installer update flow
- stores user configuration under `%LOCALAPPDATA%\Quill`

This is the recommended build for normal desktop use.

### Portable

File pattern:

```text
Quill-vX.Y.Z-portable-windows-x64.zip
```

Extract the entire archive and run `Quill.exe` from the extracted folder.

The portable build:

- does not require installation
- keeps `config.json` and `user_prompts.json` inside a local `data` folder beside `Quill.exe`
- can be moved as a folder
- opens the GitHub release page when a newer version is found instead of launching an installer automatically

Do not copy only `Quill.exe`. The published build is a PyInstaller `onedir` package and requires the files shipped beside the executable.

## First launch

On the first launch Quill opens its onboarding window.

Configure these values:

### Base URL

The root URL for an OpenAI-compatible API.

Examples:

```text
https://api.openai.com/v1
http://localhost:11434/v1
http://localhost:8080/v1
```

The exact URL depends on the provider or local server you use.

### API Key

Enter the API key required by the endpoint.

For local servers that do not require authentication, the field can be left empty.

Quill encrypts a stored API key with Windows DPAPI.

### Model

Enter the exact model identifier expected by your endpoint.

Examples vary by provider and server. Quill does not maintain a fixed model catalog, which means arbitrary OpenAI-compatible model names can be used.

## Your first action

1. Open an application with editable text.
2. Select a piece of text.
3. Press `Ctrl+Space`.
4. Choose one of the built-in actions.
5. Wait for the API response.
6. Quill replaces the selected text with the result.

The popup includes:

- Grammar Check
- Rewrite
- Professional
- Summarize
- Translate
- Custom Instruction

## Custom instructions

The popup also contains a Custom Instruction field.

Type an instruction such as:

```text
Make this friendlier without changing the meaning.
```

Then press `Enter` to send it.

Use `Shift+Enter` to insert a new line instead of sending.

## Direct action hotkeys

Some actions can skip the popup entirely.

Default direct hotkeys:

```text
Ctrl+Alt+G  Grammar Check
Ctrl+Alt+R  Rewrite
Ctrl+Alt+T  Translate
```

Professional has a direct hotkey slot but is disabled by default. You can assign one under **Settings > Hotkey**.

## Quick Repeat

`Ctrl+Shift+Space` repeats the last action on the currently selected text without reopening the popup.

This is useful when processing several separate pieces of text with the same action.

## Translate target language

Open **Settings > General > Translation** to choose the target language used by Translate.

The field is editable, so you can choose a common entry such as `Portuguese (Brazil)` or type any language description accepted by your model.

## Start Quill with Windows

Open **Settings > General** and enable **Start Quill with Windows**.

Quill registers itself under the current user's Windows Run key, so this does not require administrator privileges.

## Updates

Right-click the tray icon and choose **Check for Updates**.

By default Quill also performs one silent update check shortly after startup. It only notifies you when a newer release exists.

See [Updates and Data](updates-and-data.md) for the full behavior.

## Next steps

- [Configuration](configuration.md)
- [Actions and Prompts](actions-and-prompts.md)
- [Hotkeys](hotkeys.md)
- [Troubleshooting](troubleshooting.md)
