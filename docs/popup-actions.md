# Popup Actions

Bragi lets you choose which actions appear in the main popup and the order in which they are shown.

Open **Settings > Popup Actions**.

## Reordering actions

Select an action and use **Move Up** or **Move Down**. The popup follows the saved order exactly, including Custom Actions.

For example, if Professional is your most-used action, move it to the first position and it will become the first button in the popup.

## Hiding actions

Each action has a checkbox in the Popup Actions list.

Uncheck an action to remove it from the popup. Hiding an action does not delete it, reset its prompt, or disable an assigned direct hotkey.

This applies to both built-in actions and Custom Actions.

## Built-in actions are never deleted

Grammar Check, Rewrite, Professional, Summarize and Translate remain available internally even when hidden from the popup.

Their prompts can still be edited in **Settings > Prompts**, and configured direct hotkeys continue to work while the popup button is hidden.

## Restore Defaults

**Restore Defaults** restores every built-in action to the original built-in order and makes all built-ins visible again.

Custom Actions are not deleted or reset. They remain after the built-in actions in their current relative order, and a Custom Action that was hidden remains hidden.

## Custom Actions

New Custom Actions are appended to the popup layout automatically and are visible by default. Deleting a Custom Action automatically removes stale layout state the next time the layout is normalized.

Bragi v2.1 stored Custom Action popup visibility inside the Custom Action itself. When upgrading to the unified Popup Actions layout, that existing visibility choice is preserved if no newer popup layout has been saved yet.

## Storage

The unified popup layout is stored in `config.json` under the popup action order and hidden-action settings. Custom Action definitions themselves remain stored in `user_prompts.json`.
