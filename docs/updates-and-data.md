# Updates and Data

Quill supports both installed and portable Windows builds. The application intentionally keeps their user-data behavior separate.

## Installed build

The installer uses:

```text
%LOCALAPPDATA%\Programs\Quill
```

Application files are stored there, while writable user data is stored separately under:

```text
%LOCALAPPDATA%\Quill
```

Current user-data files:

```text
%LOCALAPPDATA%\Quill\config.json
%LOCALAPPDATA%\Quill\user_prompts.json
```

This separation means replacing or reinstalling application files does not require storing user configuration inside the installation directory.

## Portable build

Portable Quill stores user data beside the executable:

```text
<Quill folder>\data\config.json
<Quill folder>\data\user_prompts.json
```

This makes the folder self-contained for portable use.

If you move the entire portable Quill folder, its local configuration moves with it.

## Legacy data migration

Older Quill layouts could place `config.json` and `user_prompts.json` in application-relative `data` directories, including PyInstaller runtime locations.

Current builds check known legacy locations when determining the user-data directory.

Migration rules:

- only `config.json` and `user_prompts.json` are migrated
- files are copied, not moved
- legacy originals are left in place
- an existing destination file is never overwritten
- the first matching legacy source is used for a missing destination file

This design supports upgrades while leaving a recovery copy in the older location.

## Manual update check

Right-click the tray icon and choose:

```text
Check for Updates
```

Quill queries the latest public release from:

```text
https://github.com/isyuricunha/Quill/releases
```

If the installed version is current, a manual check displays an up-to-date message.

If a newer version exists, behavior depends on the build type.

## Installed update flow

For an installed build with a setup asset available:

1. Quill shows the available version.
2. You confirm the update.
3. Quill downloads the release setup executable into the user's temporary directory.
4. Quill validates that the installer URL belongs to this repository's GitHub release download path.
5. Quill launches the installer.
6. The running Quill instance exits.
7. The installer updates the per-user installation.

The downloaded installer filename follows this pattern:

```text
Quill-vX.Y.Z-setup-windows-x64.exe
```

## Portable update flow

For a portable build:

1. Quill reports the newer version.
2. You can open the GitHub release page.
3. Download the new portable ZIP.
4. Replace the application files manually.

Your portable data lives in the local `data` directory, so preserve that directory when replacing files.

A safe manual portable update is:

1. Close Quill.
2. Back up the existing folder if desired.
3. Extract the new release to a temporary folder.
4. Copy the new application files over the old application files while keeping your existing `data` folder.
5. Start `Quill.exe`.

## Automatic startup check

The option **Settings > General > Check for updates when Quill starts** is enabled by default for configured installations.

When enabled:

- Quill schedules one check shortly after startup
- the check runs in a background thread
- if no update exists, no notification is shown
- if an update exists, Quill shows a tray notification
- the notification tells you to use **Check for Updates** to continue

The startup check does not automatically download or install anything.

## Version detection

Published builds contain:

```text
resources/version.txt
```

The Auto Release workflow writes the release version into that file before building.

Quill compares the embedded semantic version with the latest GitHub release tag.

If the version file cannot be read, the updater falls back to `0.0.0`, which makes a public release appear newer.

## Start with Windows and updates

Windows startup and application updates are independent settings.

**Start Quill with Windows** registers the current executable under the current user's Windows Run key.

The installer uses a stable install path, so installed updates continue to launch from the same location.

For portable builds, moving the Quill folder after enabling Start with Windows changes the executable path. Disable and re-enable the startup option after moving the folder so the Windows Run entry points to the new path.

## Uninstalling the installed build

The installer creates a normal per-user uninstall entry.

Application files are removed by the uninstaller. User data under `%LOCALAPPDATA%\Quill` is intentionally separate from the install directory and should be treated as personal configuration.

If you want a completely clean reset, close Quill and manually remove `%LOCALAPPDATA%\Quill` after uninstalling.

## Backing up configuration

For the installed build, back up:

```text
%LOCALAPPDATA%\Quill
```

For portable, back up:

```text
<Quill folder>\data
```

Because the API key is protected with Windows DPAPI, copying `config.json` to another Windows account or machine may not make the encrypted key decryptable there. Re-enter the API key after migration if necessary.

## Related documentation

- [Configuration](configuration.md)
- [Security and Privacy](security-and-privacy.md)
- [Troubleshooting](troubleshooting.md)
- [Release Process](release-process.md)
