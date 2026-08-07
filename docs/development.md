# Development

Bragi is a Python 3 / PySide6 Windows desktop utility.

## Local setup

From the repository root:

```powershell
python -m pip install -r requirements.txt
python main.py
```

For release-style builds, install PyInstaller as well:

```powershell
python -m pip install pyinstaller
```

## Tests

Compile all application sources first:

```powershell
python -m compileall -q core app ui main.py
```

Run unit tests:

```powershell
python -m unittest discover -s tests -v
```

The release workflow runs both commands before it attempts packaging.

## Build

Run:

```powershell
python build.py
```

The build script uses PyInstaller `--onedir` and produces:

```text
dist\Bragi\Bragi.exe
```

Runtime resources are bundled under the generated application directory, including:

- default prompts
- embedded version file
- Windows icon assets

Core, app and UI submodules are explicitly collected rather than relying only on PyInstaller import discovery.

## Smoke test

A packaged build supports:

```powershell
dist\Bragi\Bragi.exe --smoke-test
```

This imports critical packaged modules and exits. GitHub Actions runs this check before creating release artifacts.

## Installer

`installer.iss` is the Inno Setup definition. The published installer is per-user and requires no administrator privileges.

To compile manually, install Inno Setup and pass an application version:

```powershell
ISCC.exe /DAppVersion=2.0.0 installer.iss
```

The result is written under `installer-output` as:

```text
Bragi-v2.0.0-setup-windows-x64.exe
```

The Inno `AppId` intentionally remains the historical Quill value. Do not casually change it: it is what allows Bragi to upgrade an existing installed Quill copy instead of creating a second independent Windows installation.

## Project layout

```text
app/          application orchestration, hotkeys, selection and tray
core/         API, paths, prompts, crypto, updater and persistence
ui/           popup, onboarding, settings and theme
resources/    prompts, icons and embedded version
tests/        unit tests
docs/         maintained project documentation
```

## Branding compatibility

Current branding belongs in `core/brand.py` when it is needed by runtime compatibility code. Legacy `Quill` strings should remain only where they are intentionally required for migration, old repository redirects, historical installer identity or project lineage.

## Release changes

Use Conventional Commit messages. See [Release Process](release-process.md) before changing release automation or artifact naming.
