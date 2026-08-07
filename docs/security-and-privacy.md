# Security and Privacy

Bragi is a local Windows utility that sends selected text to the OpenAI-compatible endpoint configured by the user.

## API key storage

API keys are encrypted with Windows DPAPI before being written to `config.json`.

DPAPI binds protected data to the Windows user context. Bragi does not store the plaintext key in its configuration file.

The encrypted key can still be migrated from the previous Quill data folder because the protection is tied to the Windows account rather than the application name.

## Selected text

Bragi does not continuously read everything you type. Text is processed when you explicitly invoke an action.

The selected text, prompt instructions and configured request parameters are sent to the API endpoint you configured. The privacy policy and retention behavior of that endpoint are outside Bragi's control.

## Clipboard behavior

To work across many Windows applications, Bragi uses the standard clipboard workflow:

1. backs up the current clipboard text
2. simulates `Ctrl+C` to obtain the selection
3. restores the previous clipboard text
4. after receiving an AI response, temporarily places the response on the clipboard
5. simulates `Ctrl+V`
6. restores the previous clipboard text again

Applications that block clipboard access or standard copy/paste may not work with this mechanism.

## Prompt boundaries

Bragi parses the ChatML message structure before inserting selected text. The selected text is substituted into the already parsed message content rather than being allowed to create new ChatML messages.

This reduces the chance that literal control-marker text inside a selection alters the message hierarchy.

## Network requests

Bragi makes network requests in two situations:

- AI actions, to the configured OpenAI-compatible endpoint
- update checks, to the project's GitHub Releases endpoint

Startup update checks can be disabled in Settings.

## Update downloads

Installed updates are accepted only from expected GitHub Release download paths for the project. The installer is downloaded to a temporary Bragi update directory and launched only after the user confirms the update.

## Local files

Installed user data is stored under `%LOCALAPPDATA%\Bragi`. Portable user data is stored in `data` beside `Bragi.exe`.

During migration from Quill, Bragi copies known configuration files but intentionally does not delete the originals.

## Trust model

Bragi does not sandbox the remote model. A configured endpoint receives the content necessary to perform the requested writing action. Do not select sensitive text for processing unless you trust the endpoint receiving it.
