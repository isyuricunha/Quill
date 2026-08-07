<div align="center">

# 🪶 Quill

**System-wide AI writing assistance for Windows, powered by your own OpenAI-compatible API.**

[![Latest Release](https://img.shields.io/github/v/release/isyuricunha/Quill?display_name=tag&sort=semver)](../../releases/latest)
[![Auto Release](https://github.com/isyuricunha/Quill/actions/workflows/release.yml/badge.svg)](../../actions/workflows/release.yml)
[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows&logoColor=white)](#requirements)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Select text anywhere, press a hotkey, choose an action, and Quill replaces the selection with the AI result.

[Download](../../releases/latest) · [Documentation](docs/README.md) · [Configuration](docs/configuration.md) · [Troubleshooting](docs/troubleshooting.md)

</div>

## Why Quill?

Quill is a small Windows tray utility focused on one job: making selected text better without forcing you into a full AI chat application.

It works across applications through standard copy and paste behavior, connects to the OpenAI-compatible endpoint you choose, and stays out of the way until you call it.

### Highlights

- **System-wide text actions** for selected text in Windows applications
- **Grammar Check** for conservative grammar, spelling, and punctuation fixes
- **Rewrite** for clearer, more natural writing while preserving your voice
- **Professional** for polished, well-structured professional writing
- **Summarize** for concise summaries that preserve important facts and caveats
- **Translate** with a configurable target language
- **Custom Instruction** for one-off transformations
- **Direct action hotkeys** for Grammar Check, Rewrite, Professional, and Translate
- **Quick Repeat** to reuse the last action without reopening the popup
- **Per-prompt model override** while keeping a global default model
- **Editable ChatML prompts** with `{{text}}` and `{{instruction}}` variables
- **OpenAI-compatible APIs** including hosted, local, and proxy endpoints
- **Windows DPAPI encryption** for the stored API key
- **Start with Windows** using a per-user startup entry
- **Built-in updater** backed by this repository's GitHub Releases
- **Installer and portable builds** with separate, well-defined data locations
- **Automatic releases** with unit tests and a packaged executable smoke test

## Download

Go to the [latest release](../../releases/latest) and choose one of the Windows x64 builds:

| Build | File | Best for |
| --- | --- | --- |
| Installer | `Quill-vX.Y.Z-setup-windows-x64.exe` | Normal desktop use, Start Menu integration, in-app installer updates |
| Portable | `Quill-vX.Y.Z-portable-windows-x64.zip` | Keeping Quill self-contained or moving it between folders |

The installer is per-user, installs under `%LOCALAPPDATA%\Programs\Quill`, and does not require administrator privileges.

## Quick start

1. Install Quill or extract the portable ZIP.
2. Run `Quill.exe`.
3. Enter your **Base URL**, **API Key** if required, and **Model**.
4. Select text in another application.
5. Press `Ctrl+Space`.
6. Choose an action.
7. Quill replaces the selected text with the result.

For custom instructions, type the instruction in the popup and press `Enter`. Use `Shift+Enter` for a new line.

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

Every prompt can be edited from **Settings > Prompts**, including its temperature, template, and optional model override.

More detail: [Actions and Prompts](docs/actions-and-prompts.md).

## Hotkeys

| Purpose | Default |
| --- | --- |
| Open Quill popup | `Ctrl+Space` |
| Quick Repeat | `Ctrl+Shift+Space` |
| Grammar Check directly | `Ctrl+Alt+G` |
| Rewrite directly | `Ctrl+Alt+R` |
| Professional directly | Disabled by default |
| Translate directly | `Ctrl+Alt+T` |

All direct action hotkeys are optional and configurable. A direct action processes the selected text immediately without showing the popup.

More detail: [Hotkeys](docs/hotkeys.md).

## Settings

Quill organizes configuration into four tabs:

- **General**: Start with Windows, translation target language, update checks
- **API**: Base URL, API key, global model, additional JSON parameters
- **Hotkey**: main hotkey, Quick Repeat, direct action hotkeys
- **Prompts**: name, temperature, optional model override, ChatML template, reset to default

The Translate target can be selected from common languages or typed manually.

More detail: [Configuration](docs/configuration.md).

## OpenAI-compatible API support

Quill sends requests to the `/chat/completions` interface exposed by the Base URL you configure. This makes it suitable for many hosted and local OpenAI-compatible services, such as OpenAI, compatible gateways, Ollama, llama.cpp, and other servers that implement the same request shape.

Example configuration:

```text
Base URL: http://localhost:11434/v1
API Key:  optional for local servers
Model:    your-model-name
```

You can also provide additional request parameters as JSON:

```json
{
  "reasoning_effort": "low",
  "top_p": 0.9
}
```

Use the dedicated global model field or per-prompt model override for `model`. Quill applies the selected model after Additional Params are merged.

## Installed vs portable data

Quill intentionally separates user data based on the build type:

| Build | User data location |
| --- | --- |
| Installed | `%LOCALAPPDATA%\Quill` |
| Portable | `data` beside `Quill.exe` |

The main user files are:

- `config.json`
- `user_prompts.json`

When upgrading from an older layout, Quill copies known legacy user files into the new location without deleting the originals and without overwriting an existing destination file.

More detail: [Updates and Data](docs/updates-and-data.md).

## Updates

The tray menu contains **Check for Updates**.

By default, Quill also checks GitHub Releases once shortly after startup. If the current version is already up to date, the automatic check stays quiet.

- **Installed build**: Quill can download the new setup executable, start it, and close the running instance.
- **Portable build**: Quill opens the release page so you can replace the portable files manually.

More detail: [Updates and Data](docs/updates-and-data.md).

## Security and privacy

- The API key is encrypted with Windows DPAPI and tied to the Windows user context.
- Selected text is sent only when you invoke an AI action, to the endpoint configured in Quill.
- Quill temporarily uses the clipboard to copy the selection and paste the result, then restores the previous clipboard text.
- Update checks contact GitHub Releases when performed manually or when startup checks are enabled.

More detail: [Security and Privacy](docs/security-and-privacy.md).

## Requirements

- Windows 10 or Windows 11
- 64-bit Windows for published builds
- An OpenAI-compatible API endpoint
- Internet access only if your configured endpoint or update checks require it

## Documentation

The full documentation lives in [`/docs`](docs/README.md):

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Actions and Prompts](docs/actions-and-prompts.md)
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

Run the test suite:

```powershell
python -m compileall -q core app ui main.py
python -m unittest discover -s tests -v
```

Build the Windows application:

```powershell
python build.py
```

See [Development](docs/development.md) for build, test, packaging, and source layout details.

## Independent maintenance

This repository is maintained as an **independent fork** with its own roadmap, releases, Windows packaging, updater endpoint, tests, and release automation. Published builds and update checks are produced from `isyuricunha/Quill` and do not depend on an upstream release cadence.

The original copyright notice and GPL terms remain preserved in [LICENSE](LICENSE).

## Credits

Quill builds on the original Quill project and retains its licensing notice. The original project also cited [WritingTools](https://github.com/theJayTea/WritingTools) as an inspiration.

Core technologies include [PySide6](https://doc.qt.io/qtforpython-6/), [pynput](https://github.com/moses-palmer/pynput), and [pyperclip](https://github.com/asweigart/pyperclip).

## License

Quill is distributed under the **GNU General Public License v3.0 or later**. See [LICENSE](LICENSE).

<div align="center">

**Quill** 🪶

Small, fast, system-wide AI writing assistance for Windows.

</div>
