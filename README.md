<div align="center">

# Bragi

**System-wide AI writing assistance for Windows, powered by your own OpenAI-compatible API.**

[![Latest Release](https://img.shields.io/github/v/release/isyuricunha/bragi?display_name=tag&sort=semver)](../../releases/latest)
[![Auto Release](https://github.com/isyuricunha/bragi/actions/workflows/release.yml/badge.svg)](../../actions/workflows/release.yml)
[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows&logoColor=white)](#requirements)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Select text anywhere, press a hotkey, choose an action, and Bragi replaces the selection with the AI result.

[Download](../../releases/latest) · [Documentation](docs/README.md) · [Configuration](docs/configuration.md) · [Troubleshooting](docs/troubleshooting.md)

</div>

## What is Bragi?

Bragi is a small Windows tray utility focused on one job: improving selected text without turning into another full AI chat client.

It works across applications through standard copy and paste behavior, connects to the OpenAI-compatible endpoint you choose, and stays out of the way until you invoke it.

The name comes from **Bragi**, the Norse god associated with poetry and eloquence.

Bragi evolved from the Quill codebase and is now maintained as an independent project with its own releases, Windows packaging, updater, tests, documentation, and roadmap.

## Highlights

- **System-wide text actions** for selected text in Windows applications
- **Grammar Check** for conservative grammar, spelling, and punctuation fixes
- **Rewrite** for clearer, more natural writing while preserving your voice
- **Professional** for polished, well-structured professional writing
- **Summarize** for concise summaries that preserve important facts and caveats
- **Translate** with a configurable target language
- **Custom Instruction** for one-off transformations
- **Custom Actions** with their own prompt, temperature, model override and optional hotkey
- **Configurable popup actions** with ordering, visibility and built-in restore
- **Direct action hotkeys** for built-in and user-created actions
- **Quick Repeat** to reuse the last action without reopening the popup
- **Per-prompt model override** while keeping a global default model
- **Editable ChatML prompts** with `{{text}}` and `{{instruction}}` variables
- **OpenAI-compatible APIs** including hosted, local, and proxy endpoints
- **Windows DPAPI encryption** for the stored API key
- **Start with Windows** using a per-user startup entry
- **Built-in updater** backed by GitHub Releases
- **Installer and portable builds** with separate user-data locations
- **Automatic releases** with unit tests and a packaged executable smoke test

## Download

Go to the [latest release](../../releases/latest) and choose one of the Windows x64 builds:

| Build | File | Best for |
| --- | --- | --- |
| Installer | `Bragi-vX.Y.Z-setup-windows-x64.exe` | Normal desktop use, Start Menu integration, in-app installer updates |
| Portable | `Bragi-vX.Y.Z-portable-windows-x64.zip` | Keeping Bragi self-contained or moving it between folders |

The installer is per-user and does not require administrator privileges. New installations use `%LOCALAPPDATA%\Programs\Bragi`.

## Quick start

1. Install Bragi or extract the portable ZIP.
2. Run `Bragi.exe`.
3. Enter your **Base URL**, **API Key** if required, and **Model**.
4. Select text in another application.
5. Press `Ctrl+Space`.
6. Choose an action.
7. Bragi replaces the selected text with the result.

For a custom transformation, type an instruction in the popup and press `Enter`. Use `Shift+Enter` for a new line.

See [Getting Started](docs/getting-started.md) for the full walkthrough.

## Built-in actions

| Action | Default temperature | Behavior |
| --- | ---: | --- |
| Grammar Check | `0.3` | Corrects clear grammar, spelling, punctuation, and typographical errors while preserving tone and style |
| Rewrite | `0.5` | Improves clarity, readability, naturalness, and flow without unnecessarily formalizing the text |
| Professional | `0.4` | Reworks text into polished professional writing while preserving facts, intent, nuance, and certainty |
| Summarize | `0.3` | Produces concise continuous prose without inventing or inferring missing information |
| Translate | `0.3` | Produces a natural translation into the configured target language |
| Custom | `0.7` | Applies the instruction you provide to the selected text |

Every built-in prompt can be edited from **Settings > Prompts**, including its temperature, template, and optional model override.

More detail: [Actions and Prompts](docs/actions-and-prompts.md).

## Custom Actions

Open **Settings > Custom Actions** to create reusable actions for tasks you do repeatedly.

Each Custom Action has a name, ChatML prompt, temperature, optional model override and optional global hotkey. Custom Actions use the same processing pipeline as built-in actions, so they work with direct execution and Quick Repeat too.

The prompt must contain `{{text}}`, which is replaced with the current selection.

More detail: [Custom Actions](docs/custom-actions.md).

## Popup Actions

Open **Settings > Popup Actions** to control the button layout without changing prompts or hotkeys.

Built-in and Custom Actions share one ordered list. Use **Move Up** and **Move Down** to choose the order, and uncheck an action to hide it from the popup. Hidden actions are not deleted, and any configured direct hotkey keeps working.

**Restore Defaults** makes all built-in actions visible again and restores their original order while preserving Custom Actions and their hidden state.

More detail: [Popup Actions](docs/popup-actions.md).

## Hotkeys

| Purpose | Default |
| --- | --- |
| Open Bragi popup | `Ctrl+Space` |
| Quick Repeat | `Ctrl+Shift+Space` |
| Grammar Check directly | `Ctrl+Alt+G` |
| Rewrite directly | `Ctrl+Alt+R` |
| Professional directly | Disabled by default |
| Translate directly | `Ctrl+Alt+T` |

All direct action hotkeys are optional and configurable. Custom Actions can define their own optional direct hotkey. A direct action processes the selected text immediately without showing the popup.

More detail: [Hotkeys](docs/hotkeys.md).

## Settings

Bragi organizes configuration into six tabs:

- **General**: Start with Windows, translation target language, update checks
- **API**: Base URL, API key, global model, additional JSON parameters
- **Hotkey**: main hotkey, Quick Repeat, built-in direct action hotkeys
- **Popup Actions**: action order, popup visibility and built-in restore
- **Custom Actions**: user-created actions, hotkeys, temperature and model overrides
- **Prompts**: built-in prompt name, temperature, optional model override, ChatML template, reset to default

The Translate target can be selected from common languages or typed manually.

More detail: [Configuration](docs/configuration.md).

## OpenAI-compatible API support

Bragi sends requests to the `/chat/completions` interface exposed by the Base URL you configure. It can therefore work with many hosted and local services that implement the OpenAI-compatible request shape.

Example:

```text
Base URL: http://localhost:11434/v1
API Key:  optional for local servers
Model:    your-model-name
```

Additional request parameters can be supplied as JSON:

```json
{
  "reasoning_effort": "low",
  "top_p": 0.9
}
```

Use the dedicated global model field or a per-prompt/model override for `model`.

## Installed vs portable data

Bragi separates user data based on build type:

| Build | User data location |
| --- | --- |
| Installed | `%LOCALAPPDATA%\Bragi` |
| Portable | `data` beside `Bragi.exe` |

The primary user files are `config.json` and `user_prompts.json`. Custom Actions are stored in `user_prompts.json` alongside prompt overrides, while popup ordering and hidden-action state are stored in `config.json`.

### Upgrading from Quill

Bragi v2 is designed as an upgrade path from Quill. On first use, an installed Bragi build looks for the previous `%LOCALAPPDATA%\Quill` configuration and prompt overrides. Missing Bragi files are copied automatically.

Existing Bragi files always win. The old Quill files are left untouched for recovery, and the migration never overwrites an existing destination file.

The Windows installer also migrates an enabled `Quill` startup entry to `Bragi` and removes obsolete Quill shortcuts and the old executable when upgrading an installed copy.

More detail: [Updates and Data](docs/updates-and-data.md).

## Updates

The tray menu contains **Check for Updates**. By default, Bragi also checks GitHub Releases once shortly after startup and stays silent when no update exists.

- **Installed build**: Bragi can download the new setup executable, start it, and close the running application.
- **Portable build**: Bragi opens the release page so the portable files can be replaced manually.

More detail: [Updates and Data](docs/updates-and-data.md).

## Security and privacy

- The API key is encrypted with Windows DPAPI and tied to the Windows user context.
- Selected text is sent only when you invoke an AI action, to the endpoint configured in Bragi.
- Bragi temporarily uses the clipboard to copy the selection and paste the result, then restores the previous clipboard text.
- Update checks contact GitHub Releases when performed manually or when startup checks are enabled.

More detail: [Security and Privacy](docs/security-and-privacy.md).

## Requirements

- Windows 10 or Windows 11
- 64-bit Windows for published builds
- An OpenAI-compatible API endpoint
- Internet access only if your endpoint or update checks require it

## Documentation

The full documentation lives in [`/docs`](docs/README.md):

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Actions and Prompts](docs/actions-and-prompts.md)
- [Popup Actions](docs/popup-actions.md)
- [Custom Actions](docs/custom-actions.md)
- [Hotkeys](docs/hotkeys.md)
- [Updates and Data](docs/updates-and-data.md)
- [Security and Privacy](docs/security-and-privacy.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [Release Process](docs/release-process.md)

## Development

```powershell
python -m pip install -r requirements.txt
python main.py
```

Run the tests:

```powershell
python -m compileall -q core app ui main.py
python -m unittest discover -s tests -v
```

Build the Windows application:

```powershell
python build.py
```

The packaged executable is produced as `dist\Bragi\Bragi.exe`.

## Project lineage

Bragi is independently maintained and has its own roadmap and distribution pipeline. It evolved from the Quill project, whose original copyright notice remains preserved in the license and project history. Quill also cited [WritingTools](https://github.com/theJayTea/WritingTools) as an inspiration.

Core technologies include [PySide6](https://doc.qt.io/qtforpython-6/), [pynput](https://github.com/moses-palmer/pynput), and [pyperclip](https://github.com/asweigart/pyperclip).

## License

Bragi is distributed under the **GNU General Public License v3.0 or later**. See [LICENSE](LICENSE).

<div align="center">

**Bragi**

Small, fast, system-wide AI writing assistance for Windows.

</div>