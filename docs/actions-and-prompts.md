# Actions and Prompts

Bragi ships with focused writing actions and also supports user-created Custom Actions. Built-in prompts are intentionally compact and use separate system and user messages so permanent behavior is kept distinct from selected text.

## Built-in actions

### Grammar Check

Default temperature: `0.3`

Corrects clear grammar, spelling, punctuation and typographical errors while preserving the original language, tone, formatting and intentional informality whenever possible.

### Rewrite

Default temperature: `0.5`

Improves clarity, readability and flow while preserving the writer's voice and level of formality. It is not intended to automatically turn casual text into corporate prose.

### Professional

Default temperature: `0.4`

Actively restructures and polishes the text for professional contexts. It may remove unsuitable slang, improve organization and formalize phrasing, but it must preserve facts, intent, numbers, nuance and degree of certainty.

### Summarize

Default temperature: `0.3`

Produces concise continuous prose and preserves important names, numbers, dates, conditions, decisions and caveats without inventing missing information.

### Translate

Default temperature: `0.3`

Translates naturally into the target language configured in Settings. It preserves formatting, code, URLs, handles, placeholders and other content that should not be casually altered.

### Custom Instruction

Default temperature: `0.7`

Uses the one-off instruction typed in the popup. The selected text is treated as data rather than as instructions that can override the prompt hierarchy.

## Custom Actions

Custom Actions are reusable user-created actions. Each one has its own name, ChatML template, temperature, optional model override, optional global hotkey and popup visibility setting.

They use the same request path as built-in actions, so they also support direct execution and Quick Repeat.

See [Custom Actions](custom-actions.md) for the complete workflow.

## ChatML templates

Templates use ChatML-style message markers, for example:

```text
<|im_start|>system
You are a careful editor.
<|im_end|>
<|im_start|>user
<text>
{{text}}
</text>
<|im_end|>
```

Bragi parses message structure before substituting selected text. This prevents text containing strings that resemble ChatML control markers from becoming new prompt messages.

## Variables

`{{text}}` is replaced with the selected text.

`{{instruction}}` is replaced with the one-off Custom Instruction supplied in the popup.

Substitution is literal, not recursively interpreted.

Custom Actions must contain `{{text}}` so the selected text is always part of the action request.

## Model Override

Each built-in prompt and Custom Action can optionally specify its own model.

If the override is empty, the global model from the API tab is used. This makes it possible to use a fast model for Grammar Check or a lightweight Custom Action and a stronger model for Rewrite or Professional without changing the global configuration.

## User overrides

Editing a built-in prompt creates or updates an entry in `user_prompts.json`. Reset to Default removes that override and restores the built-in prompt.

Custom Actions are also stored in `user_prompts.json`, but they are user-owned objects rather than overrides of bundled defaults. They can be renamed, hidden from the popup or deleted.

Built-in prompts live in `resources/default_prompts.json` and should normally be changed through source control rather than by editing a packaged installation.

## Prompt migrations

Bragi carries forward compatible user prompt overrides from previous versions. Known old default prompts can be migrated to newer defaults while preserving user choices such as target language or Model Override when possible. A prompt that was genuinely customized by the user is not silently replaced with a new default.
