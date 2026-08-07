# Troubleshooting

This guide covers the most common problems with Quill's hotkeys, selection capture, API configuration, prompts, updates, and stored data.

## Quill says no text is selected

Quill captures selected text by temporarily using the clipboard and simulating `Ctrl+C`.

Try these checks:

1. Make sure text is actually highlighted before pressing the hotkey.
2. Test in Windows Notepad.
3. Confirm the target application supports normal `Ctrl+C` copy behavior.
4. Try a different Quill hotkey in case the target application intercepts the current combination.
5. Make sure Quill is not paused from the tray menu.

Some protected applications, password fields, remote desktop environments, games, terminals, or custom editors can block or alter clipboard behavior.

## The hotkey does nothing

Possible causes:

### Another application owns the shortcut

Change the shortcut under **Settings > Hotkey**.

### Quill is paused

Right-click the tray icon. If the menu shows **Resume**, Quill is currently paused.

### The target application is elevated

Windows can restrict simulated input between processes running at different integrity levels.

If the target application is running as administrator and Quill is not, test with both running at the same level.

### The shortcut is invalid

Configured hotkeys must contain at least one modifier key:

- Ctrl
- Shift
- Alt

Quill also rejects duplicate shortcuts and several critical Windows combinations.

See [Hotkeys](hotkeys.md).

## The popup opens but text is not replaced

Quill replaces text by putting the result on the clipboard and simulating `Ctrl+V`.

Check whether the target application normally accepts `Ctrl+V`.

If paste is blocked or delayed by the application, Quill may not be able to replace the selection reliably.

Try the same action in Notepad to determine whether the issue is application-specific.

## My clipboard changed unexpectedly

Quill normally backs up and restores the clipboard during capture and replacement.

Clipboard managers, synchronization tools, security software, and applications with delayed paste behavior can interact with this timing.

If the issue happens only in one application, test in Notepad and temporarily disable clipboard-history tools to isolate the cause.

## API request failed

Check **Settings > API**.

### Base URL

Make sure the endpoint exposes an OpenAI-compatible chat completion interface.

Common local examples use a `/v1` base path, but the exact URL depends on your server.

### API Key

Confirm the key is valid for the endpoint.

If you moved `config.json` from another Windows user or machine, DPAPI may no longer be able to decrypt the stored key. Enter the key again in Settings.

### Model

The model identifier must match what the endpoint expects.

If the global model works but one action fails, check whether that prompt has a **Model override** configured.

### Additional Params

Invalid or unsupported JSON fields can cause provider errors.

Temporarily clear Additional Params and retry.

## Additional Params cannot be saved

The field must contain a valid JSON object.

Valid:

```json
{
  "top_p": 0.9
}
```

Invalid:

```json
[
  "top_p",
  0.9
]
```

The top-level value must be an object, not an array or scalar.

## Translate uses the wrong language

Open:

```text
Settings > General > Translation
```

Check **Target language** and save Settings again.

If you manually customized the Translate prompt, inspect it under **Settings > Prompts** and confirm it still contains the intended `Target language:` directive.

Use **Reset to Default** if you want to discard custom prompt changes and return to the bundled Translate prompt.

## A prompt uses the wrong model

Open **Settings > Prompts**, choose the prompt, and inspect **Model override (optional)**.

- Empty means use the global model from the API tab.
- A value means that prompt uses the specified model instead.

Clear the field and apply/save if you want the prompt to return to the global model.

## Prompt changes keep coming back

User prompt overrides are stored in `user_prompts.json`.

Use **Reset to Default** for a built-in prompt rather than only editing the visible text back manually.

Locations:

Installed:

```text
%LOCALAPPDATA%\Quill\user_prompts.json
```

Portable:

```text
<Quill folder>\data\user_prompts.json
```

## Quill starts with onboarding again

Quill shows onboarding when it cannot find a usable configuration containing a Base URL and model.

Check the expected data location.

Installed:

```text
%LOCALAPPDATA%\Quill\config.json
```

Portable:

```text
<Quill folder>\data\config.json
```

If you moved only `Quill.exe` out of a portable package, restore the complete published folder. Quill uses a PyInstaller `onedir` layout and requires its bundled files.

## API key decryption failed

The encrypted key is protected with Windows DPAPI.

This can happen after moving configuration to a different Windows account or machine.

Fix:

1. Open Settings.
2. Enter the API key again.
3. Save.

If the settings window cannot load because of a damaged configuration, back up the data directory, remove `config.json`, restart Quill, and complete onboarding again.

## Quill does not start after an update

Published releases run a packaged executable smoke test before the release is created, but local security tools or incomplete manual copying can still cause problems.

### Portable

Make sure the entire new ZIP was extracted. Do not replace only `Quill.exe`.

### Installed

Run the current setup executable again over the existing installation.

The user configuration is stored separately under `%LOCALAPPDATA%\Quill`.

## Check for Updates fails

Update checks require access to GitHub's API and Releases endpoints.

Check:

- internet connectivity
- firewall or proxy rules
- GitHub availability
- whether security software blocks Quill network access

A failed manual check displays an error. A failed automatic startup check is intentionally less intrusive.

## Installed updater does not offer automatic installation

Automatic installer updates are only offered when Quill detects that it is running from its per-user installed location and the latest release contains the expected setup asset.

Expected install path:

```text
%LOCALAPPDATA%\Programs\Quill
```

Expected installer suffix:

```text
-setup-windows-x64.exe
```

If Quill is running as portable, it opens the release page instead.

## Start with Windows stopped working after moving portable Quill

The startup registry entry stores the executable path.

After moving the portable folder:

1. Open Settings.
2. Disable **Start Quill with Windows** and save.
3. Reopen Settings.
4. Enable it again and save.

This rewrites the startup entry using the new executable path.

## Reset Quill completely

### Installed build

1. Quit Quill.
2. Back up `%LOCALAPPDATA%\Quill` if desired.
3. Remove `%LOCALAPPDATA%\Quill`.
4. Start Quill again.

### Portable build

1. Quit Quill.
2. Back up the local `data` directory if desired.
3. Remove the `data` directory.
4. Start Quill again.

Quill will return to onboarding.

## Still broken?

When reporting a problem, include:

- Quill version
- installed or portable build
- Windows version
- target application
- action used
- whether the same action works in Notepad
- API type or server name, without exposing your API key
- exact error message or traceback

This information usually separates text-capture issues from API, prompt, packaging, or application-specific problems quickly.
