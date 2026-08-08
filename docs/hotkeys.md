# Hotkeys

Bragi listens for global shortcuts through `pynput`.

## Defaults

| Purpose | Default |
| --- | --- |
| Main popup | `Ctrl+Space` |
| Quick Repeat | `Ctrl+Shift+Space` |
| Grammar Check | `Ctrl+Alt+G` |
| Rewrite | `Ctrl+Alt+R` |
| Professional | Disabled |
| Translate | `Ctrl+Alt+T` |

## Main hotkey

The main hotkey copies the current selection, opens the Bragi popup near the cursor and lets you choose a built-in action, a visible Custom Action, or enter a custom instruction.

## Quick Repeat

Quick Repeat reuses the last action and instruction on the current selection without reopening the popup. Custom Actions participate in Quick Repeat too.

If no previous action exists, Bragi falls back to the normal popup flow.

## Direct action hotkeys

A direct action immediately processes the selected text with its assigned prompt. No popup is shown.

Built-in direct action shortcuts are configured in **Settings > Hotkey**. Custom Action shortcuts are configured on the individual action in **Settings > Custom Actions**.

Every direct action shortcut is optional. Leave its field empty to disable it.

Professional intentionally ships without a default shortcut so Bragi does not consume more global combinations than necessary.

## Validation

Bragi requires configured shortcuts to include at least one modifier: Ctrl, Shift or Alt.

It also rejects:

- duplicate shortcuts across the main hotkey, Quick Repeat, built-in actions and Custom Actions
- `Alt+F4`
- `Ctrl+Alt+Delete`
- `Ctrl+Shift+Esc`

## Modifier handling

Before Bragi simulates copy or paste operations, modifier keys are released to reduce interference between the activation shortcut and the generated `Ctrl+C` / `Ctrl+V` events.

## Conflicts with other applications

A shortcut may still be claimed globally by another application. If a Bragi shortcut does not fire, choose another combination in Settings and test again.

Some elevated applications can prevent a normally launched process from interacting with them because of Windows integrity-level boundaries. This is a Windows behavior rather than a Bragi-specific shortcut rule.

## Pausing

Choose **Pause** from the tray menu to temporarily disable Bragi's hotkey listener. Choose **Resume** to enable it again.
