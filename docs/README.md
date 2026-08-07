# Quill Documentation

This directory contains the complete documentation for the independently maintained `isyuricunha/Quill` codebase.

## User guide

| Document | What it covers |
| --- | --- |
| [Getting Started](getting-started.md) | Installer vs portable, first launch, first text transformation |
| [Configuration](configuration.md) | General, API, hotkey, translation, update, and prompt settings |
| [Actions and Prompts](actions-and-prompts.md) | Built-in actions, temperatures, ChatML, variables, model overrides |
| [Hotkeys](hotkeys.md) | Main hotkey, Quick Repeat, direct actions, validation and conflicts |
| [Updates and Data](updates-and-data.md) | In-app updates, installed vs portable storage, migration behavior |
| [Security and Privacy](security-and-privacy.md) | API key storage, clipboard behavior, network requests, trust boundaries |
| [Troubleshooting](troubleshooting.md) | Selection problems, hotkeys, API errors, updates, configuration recovery |

## Developer guide

| Document | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, request flow, text capture, prompt rendering, data flow |
| [Development](development.md) | Local setup, tests, build process, installer packaging, project layout |
| [Release Process](release-process.md) | Conventional Commit versioning, GitHub Actions, artifacts and smoke tests |

## Project status

This repository is maintained as an independent fork. It has its own releases, updater target, Windows installer, portable packaging, release workflow, tests, and roadmap.

The original copyright notice and GPL license remain in [`../LICENSE`](../LICENSE).

## Quick links

- [Main README](../README.md)
- [Latest release](../../releases/latest)
- [All releases](../../releases)
- [Auto Release workflow](../.github/workflows/release.yml)
- [Default prompts](../resources/default_prompts.json)
