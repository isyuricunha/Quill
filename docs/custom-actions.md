# Custom Actions

Custom Actions let you turn recurring writing tasks into first-class Bragi actions without changing the application code.

Open **Settings > Custom Actions** to create and manage them.

## What a Custom Action contains

Each action has:

- a display name
- a ChatML prompt template
- a temperature from `0.0` to `2.0`
- an optional model override
- an optional global direct hotkey

The prompt must contain `{{text}}`. Bragi replaces that variable with the text selected in the active application.

Popup visibility and ordering are configured separately in **Settings > Popup Actions** so built-in and Custom Actions can be managed in one place.

## Example

An action named `Discord Reply` could use:

```text
<|im_start|>system
Rewrite the selected text as a concise, natural Discord message. Keep the same meaning and language. Return only the rewritten message.
<|im_end|>
<|im_start|>user
<text>
{{text}}
</text>
<|im_end|>
```

You could then expose it in the normal popup, assign a direct hotkey, or both.

## Popup behavior

New Custom Actions are added to the popup layout automatically and are visible by default.

Use **Settings > Popup Actions** to move a Custom Action above or below built-in actions, or hide it without deleting it. Hiding a Custom Action does not disable its direct hotkey or Quick Repeat behavior.

Bragi v2.1 stored popup visibility directly on each Custom Action. When upgrading, that old hidden/visible choice is preserved until the unified popup layout is saved.

See [Popup Actions](popup-actions.md).

## Direct hotkeys

A Custom Action hotkey behaves exactly like a built-in direct action: Bragi captures the current selection and immediately runs the action without opening the popup.

The hotkey is optional. Bragi validates it against:

- the main popup hotkey
- Quick Repeat
- built-in direct action hotkeys
- every other Custom Action hotkey
- critical Windows shortcuts blocked by Bragi

## Model override

Leaving the model field empty uses the global model from **Settings > API**.

Setting a model override affects only that Custom Action. The Base URL, API key and Additional Params continue to come from the global API configuration.

## Quick Repeat

Custom Actions participate in Quick Repeat. After running one, `Ctrl+Shift+Space` can apply the same action to a new selection.

If an action is deleted after being used, Bragi detects that the previous action no longer exists instead of trying to execute a stale prompt key.

## Storage

Custom Actions are stored in `user_prompts.json` alongside normal prompt overrides. Each action receives a stable internal key, so renaming the visible action does not break its persisted identity.

Popup ordering and visibility are stored separately in `config.json`.

Deleting a Custom Action removes it from `user_prompts.json`. Unlike built-in prompts, a deleted Custom Action has no Reset to Default operation.
