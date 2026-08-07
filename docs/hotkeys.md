# Hotkeys

Quill uses global Windows hotkeys through `pynput`.

Hotkeys are configured under **Settings > Hotkey**.

## Main Hotkey

Default:

```text
Ctrl+Space
```

Stored internally as:

```text
<ctrl>+<space>
```

The Main Hotkey:

1. captures the current text selection
2. opens the Quill popup
3. lets you choose an action or enter a custom instruction

## Quick Repeat

Default:

```text
Ctrl+Shift+Space
```

Quick Repeat reuses the most recently executed action and instruction on the current text selection without showing the popup.

Example workflow:

1. Select a sentence.
2. Open Quill and choose Rewrite.
3. Select another sentence.
4. Press Quick Repeat.
5. Quill runs Rewrite again immediately.

If there is no previous action, Quick Repeat falls back to the normal popup flow.

Leave the field empty to disable Quick Repeat.

## Direct Action Hotkeys

Direct hotkeys bypass the popup entirely.

Current defaults:

| Action | Default | Behavior |
| --- | --- | --- |
| Grammar Check | `Ctrl+Alt+G` | Captures selection and immediately runs Grammar Check |
| Rewrite | `Ctrl+Alt+R` | Captures selection and immediately runs Rewrite |
| Professional | Disabled | Optional slot available in Settings |
| Translate | `Ctrl+Alt+T` | Captures selection and immediately runs Translate |

Professional is intentionally unbound by default to avoid consuming another global Windows shortcut unless the user wants it.

Summarize currently remains a popup action and can also be reused through Quick Repeat.

## Hotkey syntax

The settings UI accepts the syntax used by `pynput`.

Examples:

```text
<ctrl>+<space>
<ctrl>+<alt>+g
<ctrl>+<shift>+a
<alt>+q
```

Regular letters and numbers do not require angle brackets.

Special keys and modifiers use angle brackets, for example:

```text
<ctrl>
<shift>
<alt>
<space>
<enter>
<f8>
```

## Validation rules

Quill validates configured hotkeys before saving.

### A modifier is required

Every configured hotkey must include at least one of:

- Ctrl
- Shift
- Alt

### Duplicate hotkeys are rejected

The Main Hotkey, Quick Repeat, and direct action hotkeys cannot use the same combination.

### Critical Windows hotkeys are rejected

Quill explicitly blocks these combinations:

```text
Alt+F4
Ctrl+Alt+Delete
Ctrl+Shift+Esc
```

## Hotkeys and text capture

Quill's text capture flow simulates `Ctrl+C` after the global hotkey fires.

Before doing so, Quill releases common modifier keys such as Ctrl, Alt, Shift, and Command to prevent a direct hotkey such as `Ctrl+Alt+G` from accidentally turning the simulated copy operation into `Ctrl+Alt+C`.

The previous clipboard text is restored after capture.

## Hotkeys while Quill is busy

Quill prevents overlapping AI requests and overlapping selection extraction operations.

If an AI request or capture is already in progress, another hotkey press can be ignored until the current operation finishes.

This avoids multiple responses racing to replace the same selected text.

## Pausing hotkeys

Right-click the tray icon and choose **Pause**.

While paused, Quill remains running but ignores global hotkey actions.

Choose **Resume** to reactivate them.

## Troubleshooting hotkeys

If a hotkey does not work:

1. Try another combination in Settings.
2. Check whether another application has registered the same global shortcut.
3. Make sure Quill is not paused.
4. Test in a basic editor such as Notepad to separate Quill behavior from target-application behavior.
5. If the target application is running elevated, Windows may block simulated input from a non-elevated Quill process. Running both applications at the same integrity level can help.

See [Troubleshooting](troubleshooting.md) for more cases.
