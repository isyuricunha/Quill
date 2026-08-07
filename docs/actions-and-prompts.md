# Actions and Prompts

Quill's built-in actions are prompt templates rendered into OpenAI-compatible chat messages.

The bundled defaults live in:

```text
resources/default_prompts.json
```

User modifications are stored separately in `user_prompts.json`.

## Built-in actions

### Grammar Check

Default temperature: `0.3`

Purpose:

- correct grammar
- correct spelling
- correct punctuation
- correct clear typographical mistakes
- preserve the original meaning and style

The prompt is deliberately conservative. It tells the model to preserve intentional slang, dialect, abbreviations, capitalization, emojis, Markdown, URLs, commands, code, file paths, placeholders, and identifiers unless a correction is clearly required.

It is intended for cases where the text should remain recognizably yours.

### Rewrite

Default temperature: `0.5`

Purpose:

- improve clarity
- improve readability
- improve naturalness
- improve flow
- preserve the original voice and degree of formality

Rewrite is not intended to automatically make casual writing formal. It explicitly prefers natural, idiomatic language and avoids unnecessary corporate or ornate wording.

### Professional

Default temperature: `0.4`

Purpose:

- correct grammar and punctuation
- clean up awkward sentence structure
- replace overly casual wording when appropriate
- remove filler and unnecessary repetition
- reorganize sentences and paragraphs for coherence
- produce polished professional writing

Professional is intentionally stronger than Rewrite.

It may substantially restructure the text, but it is instructed to preserve facts, names, numbers, dates, requirements, intent, nuance, and degree of certainty. It should not invent information or make the author's position stronger than the source text.

### Summarize

Default temperature: `0.3`

Purpose:

- produce a concise summary
- preserve important facts and conditions
- preserve uncertainty and qualifications
- remove repetition and nonessential details

The default output is continuous prose rather than bullet points.

The prompt explicitly forbids inventing, inferring, or speculating beyond the source material.

### Translate

Default temperature: `0.3`

Purpose:

- translate into the target language configured under **Settings > General**
- preserve meaning, tone, intent, register, and formality
- produce natural target-language phrasing instead of mechanically literal output

The prompt tells the model to preserve or avoid translating technical elements such as URLs, handles, code, file paths, commands, placeholders, and identifiers.

The default target is `English`, but the user setting updates the prompt dynamically.

### Custom

Default temperature: `0.7`

Purpose:

- apply a user-written instruction to the selected text

The prompt treats `<instruction>` as the task and `<text>` as data to process.

This separation is intentional. Text that contains command-like phrases is not supposed to become a new instruction to the model.

## Prompt structure

Quill supports ChatML-style templates.

Example:

```text
<|im_start|>system
You are a careful editor.
Return only the processed text.
<|im_end|>
<|im_start|>user
<text>
{{text}}
</text>
<|im_end|>
```

The parser converts those blocks into standard message objects such as:

```json
[
  {
    "role": "system",
    "content": "You are a careful editor.\nReturn only the processed text."
  },
  {
    "role": "user",
    "content": "<text>\nSelected text here\n</text>"
  }
]
```

## Variables

Quill currently supports these template variables:

### `{{text}}`

The selected text captured from the active application.

### `{{instruction}}`

The instruction entered in the Custom Instruction field.

Variables are substituted after ChatML message parsing. This means selected text containing strings that look like ChatML control tokens remains ordinary message content instead of creating new roles.

Substitution is also single-pass. If selected text itself contains `{{instruction}}`, Quill keeps that sequence literal rather than recursively replacing it.

## Editing prompts

Open **Settings > Prompts**.

For a selected prompt you can edit:

- name
- temperature
- optional model override
- template

Built-in prompts can be restored with **Reset to Default**.

The Custom prompt name is intentionally fixed in the current UI.

## Per-prompt model override

Each prompt can optionally use a model different from the global API model.

Example:

```text
Global model: small-fast-model
Grammar Check: empty
Rewrite: writing-model
Professional: writing-model
Translate: multilingual-model
```

An empty override uses the global model.

The override affects only the `model` field of that request. Base URL, API key, and global Additional Params remain shared.

## Temperature guidance

Quill accepts temperatures from `0.0` through `2.0`.

Lower values are generally better for deterministic editing tasks such as Grammar Check and Translate. Higher values allow more variation, which can be useful for Custom instructions or more creative rewriting.

The bundled defaults are intentionally moderate:

| Action | Temperature |
| --- | ---: |
| Grammar Check | `0.3` |
| Rewrite | `0.5` |
| Professional | `0.4` |
| Summarize | `0.3` |
| Translate | `0.3` |
| Custom | `0.7` |

Different models interpret temperature differently, so treat these values as practical defaults rather than universal rules.

## Formatting preservation

The default editing prompts explicitly ask models to preserve technical and structural content where appropriate, including:

- paragraph breaks
- Markdown
- URLs
- email addresses
- `@handles`
- code
- file paths
- commands
- placeholders
- identifiers

A model can still make mistakes. For code-heavy or syntax-sensitive selections, review the result before relying on it.

## Prompt storage

Bundled defaults:

```text
resources/default_prompts.json
```

Installed user overrides:

```text
%LOCALAPPDATA%\Quill\user_prompts.json
```

Portable user overrides:

```text
<Quill folder>\data\user_prompts.json
```

User overrides are kept separate from bundled defaults so updates can replace application files without erasing customized prompts.

## Related documentation

- [Configuration](configuration.md)
- [Hotkeys](hotkeys.md)
- [Security and Privacy](security-and-privacy.md)
