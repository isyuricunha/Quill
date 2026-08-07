# Troubleshooting

## Bragi does not start

If a packaged build fails immediately, verify that the entire portable folder was extracted rather than copying only `Bragi.exe` out of it.

For an installed build, reinstall the latest setup package over the existing installation.

Release builds are smoke-tested by launching `Bragi.exe --smoke-test` before publication, but local antivirus or security software can still interfere with execution.

## "Bragi Already Running"

Only one Bragi instance is allowed at a time. Check the system tray for an existing instance before launching another copy.

The lock file is stored in the active user-data directory.

## Hotkey does not work

Check these common causes:

- Bragi is paused from the tray menu
- another application owns the same global shortcut
- the shortcut was changed in Settings
- the target application is running at a higher Windows integrity level

Try another shortcut if the combination is already in use.

## Bragi says no text is selected

Bragi relies on the target application supporting normal `Ctrl+C` behavior.

Confirm that:

1. the text is actually selected
2. copying it manually with `Ctrl+C` works
3. the selection is not inside a protected field such as a password input
4. clipboard access is not blocked by the target application

## Text is copied but not replaced

Replacement uses `Ctrl+V`. Verify that pasting manually works in the target field and that the field remains editable after the AI request completes.

## API request fails

Verify:

- Base URL is correct
- the endpoint implements an OpenAI-compatible chat-completions API
- API key is valid when required
- model name exists on that endpoint
- Additional Params contains valid JSON and parameters supported by the server

If only one action fails, check its optional Model Override in **Settings > Prompts**.

## Translation goes to the wrong language

Open **Settings > General** and verify Target language. Saving that setting updates the Translate prompt while preserving compatible prompt customizations.

## Direct hotkey conflict

Bragi prevents duplicate shortcuts inside its own configuration, but Windows or another application can still claim a combination externally. Assign another combination.

## Update check fails

Confirm that GitHub is reachable from the machine. Startup update checks can be disabled without affecting normal AI actions.

Portable builds open the release page instead of installing automatically.

## Upgrade from Quill did not import settings

For installed builds, check whether these files exist:

```text
%LOCALAPPDATA%\Quill\config.json
%LOCALAPPDATA%\Quill\user_prompts.json
```

and whether Bragi already has files at:

```text
%LOCALAPPDATA%\Bragi
```

Bragi never overwrites an existing Bragi destination during automatic migration. If a fresh Bragi config was created first, copy the desired legacy file manually after closing Bragi.

The old Quill files are intentionally not deleted, so they remain available for recovery.

## Start with Windows still shows Quill

A normal Bragi upgrade migrates the legacy startup registry value. If Windows still contains an old entry, open Bragi Settings, disable **Start Bragi with Windows**, save, then enable it again and save once more.

## Reset configuration

Close Bragi and back up the active data directory before removing files.

Installed:

```text
%LOCALAPPDATA%\Bragi
```

Portable:

```text
<Bragi folder>\data
```

Removing `config.json` causes Bragi to show first-run onboarding again. Removing `user_prompts.json` resets user prompt overrides to built-in defaults.
