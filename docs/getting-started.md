# Getting Started

Bragi runs quietly in the Windows system tray and transforms text selected in other applications.

## Choose a build

### Installer

Download `Bragi-vX.Y.Z-setup-windows-x64.exe` for normal desktop use. The installer is per-user, requires no administrator privileges, creates Start Menu integration, and supports in-app installer updates.

New installations use:

```text
%LOCALAPPDATA%\Programs\Bragi
```

### Portable

Download `Bragi-vX.Y.Z-portable-windows-x64.zip`, extract the entire archive to a folder, and run `Bragi.exe`. Keep the whole extracted directory together.

Portable data stays inside a `data` folder beside the executable.

## First launch

On first launch Bragi asks for:

- **Base URL**: the OpenAI-compatible API root, usually ending in `/v1`
- **API Key**: optional for endpoints that do not require authentication
- **Model**: the model identifier accepted by your endpoint

Example for a local compatible server:

```text
Base URL: http://localhost:11434/v1
API Key:  (empty)
Model:    your-model-name
```

## First transformation

1. Select editable text in an application.
2. Press `Ctrl+Space`.
3. Choose Grammar Check, Rewrite, Professional, Summarize or Translate.
4. Bragi sends the selected text to the configured endpoint.
5. The selected text is replaced with the returned result.

The popup also accepts a custom instruction. Press `Enter` to send it or `Shift+Enter` for a new line.

## Direct actions

The default direct hotkeys skip the popup:

| Action | Default |
| --- | --- |
| Grammar Check | `Ctrl+Alt+G` |
| Rewrite | `Ctrl+Alt+R` |
| Translate | `Ctrl+Alt+T` |
| Professional | Disabled |

All are configurable and can be disabled.

## Quick Repeat

`Ctrl+Shift+Space` repeats the last action on the currently selected text without reopening the popup.

## Upgrading from Quill

Installed Bragi automatically looks for existing Quill configuration and prompt overrides in `%LOCALAPPDATA%\Quill`. If the corresponding Bragi files do not exist yet, they are copied into `%LOCALAPPDATA%\Bragi`.

The old files are not deleted. Existing Bragi files are never overwritten by migration.

See [Updates and Data](updates-and-data.md) for the complete migration behavior.
