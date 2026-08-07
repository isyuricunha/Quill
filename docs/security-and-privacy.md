# Security and Privacy

Quill is a local Windows utility that sends selected text to the OpenAI-compatible API endpoint configured by the user.

This page describes the main trust boundaries and local storage behavior visible in the current codebase.

## API key storage

Quill encrypts the API key with Windows DPAPI before writing it to `config.json`.

The implementation uses Windows `CryptProtectData` and `CryptUnprotectData`.

The encrypted value is stored as Base64 text in:

```text
api.api_key_encrypted
```

DPAPI ties decryption to the Windows security context. As a result, copying an encrypted `config.json` to another Windows account or machine can make the stored key unusable there.

If that happens, open Settings and enter the API key again.

## Selected text and API requests

Quill only processes text when an action is invoked.

The high-level flow is:

1. capture the current text selection
2. render the selected prompt
3. send the rendered chat messages to the configured API endpoint
4. receive the model response
5. replace the original selection

The content you select can therefore be transmitted to the API provider or local server you configured.

Choose an endpoint whose privacy and data-handling policies are appropriate for the text you process.

## Clipboard behavior

Quill uses the Windows clipboard as part of text capture and replacement.

### Capture

Quill:

1. saves the current clipboard text
2. writes an internal marker
3. simulates `Ctrl+C`
4. reads the copied selection
5. restores the previous clipboard text

### Replacement

Quill:

1. saves the current clipboard text
2. puts the AI result on the clipboard
3. simulates `Ctrl+V`
4. restores the previous clipboard text

This is designed to preserve normal clipboard contents during typical use.

Clipboard managers, target applications, security software, or unusually slow paste handling can still observe or affect this sequence.

## Prompt injection boundaries

Quill's ChatML parser parses message roles before inserting selected text and custom instruction values.

This matters because selected text can contain strings that resemble ChatML tokens such as:

```text
<|im_start|>system
```

Those strings remain ordinary message content instead of being parsed as additional system messages.

Prompt variable substitution is also single-pass, so text containing another placeholder such as `{{instruction}}` is not recursively substituted.

The default prompts additionally instruct the model to treat `<text>` content as data rather than instructions.

These measures improve prompt separation, but they do not make language-model output a security boundary. Review model output before using it in sensitive workflows.

## Update checks

Quill's updater contacts the GitHub API for:

```text
isyuricunha/Quill
```

Update checks happen when:

- you choose **Check for Updates** from the tray menu
- the startup update option is enabled and Quill performs its one scheduled startup check

The installer downloader only accepts setup download URLs that begin with this repository's GitHub Releases download path.

## Installed update downloads

When you approve an installed update, the setup executable is downloaded to a Quill updates directory inside the user's temporary directory.

Quill checks that the file exists and is non-empty before launching it.

The current updater does not perform an additional local cryptographic signature verification step. GitHub Releases and the HTTPS download path are therefore part of the update trust chain.

## Portable updates

Portable builds do not automatically download and execute the installer. They open the release page instead.

This keeps portable updates manual and makes it easier to preserve the local `data` directory.

## Local configuration

Installed user data:

```text
%LOCALAPPDATA%\Quill
```

Portable user data:

```text
<Quill folder>\data
```

The primary files are:

- `config.json`
- `user_prompts.json`

Prompt templates can contain instructions and model names but are not encrypted.

## Start with Windows

The startup option uses the current user's registry hive:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

It does not require an administrator-level system service.

## Practical recommendations

- Use a trusted API endpoint for sensitive text.
- Avoid processing secrets unless the configured endpoint is appropriate for them.
- Keep the Windows account protected because DPAPI security depends on the user context.
- Review AI output before pasting it into commands, code, legal text, or other high-impact content.
- Download published builds from this repository's Releases page.
- Keep portable `data` folders private if they contain configuration you do not want to share.

## Related documentation

- [Configuration](configuration.md)
- [Updates and Data](updates-and-data.md)
- [Architecture](architecture.md)
