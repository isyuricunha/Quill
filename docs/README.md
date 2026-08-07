# Bragi Documentation

This directory contains the maintained documentation for Bragi, a system-wide AI writing assistant for Windows.

## User guide

| Document | Covers |
| --- | --- |
| [Getting Started](getting-started.md) | Installer vs portable, first launch, first transformation |
| [Configuration](configuration.md) | API, general settings, translation, updates and prompts |
| [Actions and Prompts](actions-and-prompts.md) | Built-in actions, ChatML, temperatures and model overrides |
| [Hotkeys](hotkeys.md) | Main hotkey, Quick Repeat, direct actions and conflicts |
| [Updates and Data](updates-and-data.md) | Updates, storage locations and Quill-to-Bragi migration |
| [Security and Privacy](security-and-privacy.md) | API key storage, clipboard behavior and network requests |
| [Troubleshooting](troubleshooting.md) | Selection, hotkeys, API, updater and migration problems |

## Developer guide

| Document | Covers |
| --- | --- |
| [Architecture](architecture.md) | Components, request flow, persistence and update flow |
| [Development](development.md) | Source setup, tests, build and installer packaging |
| [Release Process](release-process.md) | Conventional Commits, semantic versioning and artifacts |

## Project lineage

Bragi evolved from the Quill codebase and is maintained independently with its own product identity, releases, updater, Windows packaging, tests, documentation and roadmap.

The original copyright notice and GPL terms remain preserved in [`../LICENSE`](../LICENSE).

## Quick links

- [Main README](../README.md)
- [Latest release](../../releases/latest)
- [All releases](../../releases)
- [Auto Release workflow](../.github/workflows/release.yml)
- [Default prompts](../resources/default_prompts.json)
