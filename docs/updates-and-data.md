# Updates and Data

Bragi supports both installed and portable distributions. The two modes intentionally use different storage locations.

## Data locations

### Installed build

```text
%LOCALAPPDATA%\Bragi\config.json
%LOCALAPPDATA%\Bragi\user_prompts.json
```

### Portable build

```text
<Bragi folder>\data\config.json
<Bragi folder>\data\user_prompts.json
```

Portable data moves with the extracted Bragi folder. Installed data stays independent of the program files so reinstalling or updating the application does not normally touch user settings.

## Migration from Quill

Bragi v2 is a product rebrand of the independently maintained Quill fork and includes an automatic compatibility path.

For an installed upgrade, Bragi checks the old location:

```text
%LOCALAPPDATA%\Quill
```

For each known user file, Bragi copies the old file into `%LOCALAPPDATA%\Bragi` only when the Bragi destination does not already exist.

Migration rules:

- `config.json` and `user_prompts.json` are supported
- existing Bragi files always win
- Quill source files are never deleted by the data migrator
- a failure to copy one file does not intentionally destroy either location
- older portable/runtime `data` layouts are also recognized when relevant

Because the API key was protected with Windows DPAPI rather than an application-specific encryption secret, a migrated encrypted API key remains decryptable for the same Windows user.

## Installed upgrade compatibility

The Bragi installer intentionally retains the historical Inno Setup application identity used by Quill. This is internal metadata and allows Windows to treat Bragi as an upgrade of the installed Quill application instead of creating an unrelated second product.

During an installed upgrade the installer:

- installs `Bragi.exe`
- removes a legacy `Quill.exe` from the active install directory
- removes obsolete Quill Start Menu and desktop shortcuts
- creates Bragi shortcuts
- migrates an enabled Windows startup entry from `Quill` to `Bragi`

New installations default to:

```text
%LOCALAPPDATA%\Programs\Bragi
```

An upgraded installation may retain a historical physical install directory selected by the previous installer. That does not affect the user-facing Bragi identity or the new `%LOCALAPPDATA%\Bragi` user-data namespace.

## Update checks

The tray menu contains **Check for Updates**.

When `Check for updates when Bragi starts` is enabled, Bragi performs one check shortly after startup. It remains silent when the installed version is current.

The updater reads the latest public GitHub Release and compares semantic versions.

## Installed update flow

When a newer release contains the expected Windows setup asset, Bragi can:

1. download the installer to the user's temporary directory
2. launch the installer
3. close the running Bragi instance

Downloads are restricted to the project's expected GitHub Release locations.

## Portable update flow

Portable builds do not overwrite themselves. Bragi offers to open the release page so the user can download and replace the portable files manually.

Keep the portable `data` folder when replacing the executable bundle.

## Repository rename compatibility

The updater is designed to survive the repository's Quill-to-Bragi rename transition. The historical GitHub repository URL is retained as a compatible endpoint because GitHub redirects renamed repositories, while installer download validation accepts both the historical and Bragi repository paths.
