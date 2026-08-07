# Release Process

Quill publishes Windows releases automatically through GitHub Actions.

Workflow:

```text
.github/workflows/release.yml
```

## Trigger

The workflow runs on:

- every push to `main`
- manual `workflow_dispatch`

Only one Auto Release run is intended to remain active at a time.

The workflow uses:

```yaml
concurrency:
  group: auto-release
  cancel-in-progress: true
```

A newer push cancels an older in-progress run in the same concurrency group.

## Release versioning

Quill uses Conventional Commit messages to decide whether a release should be created.

### Major

A major release is created for a breaking commit such as:

```text
feat!: change configuration format
```

or a commit body containing:

```text
BREAKING CHANGE:
```

### Minor

A `feat:` commit produces a minor version bump.

Example:

```text
feat: add professional writing mode
```

### Patch

These commit types produce a patch bump:

```text
fix:
perf:
refactor:
```

### No release

Other commit types do not create a version bump by themselves.

Examples:

```text
docs:
test:
chore:
ci:
```

The workflow still starts and runs the early validation steps on a push to `main`, but it stops release packaging after determining that no releasable Conventional Commit exists.

## Base version

The workflow finds the highest semantic version tag matching:

```text
v[0-9]*
```

It calculates the next version from commits since that tag.

The repository includes a historical fallback to upstream `v1.0.8` for cases where no local release tag exists.

Normal current development should always have local release tags, so the fallback is primarily historical bootstrap logic.

## Validation stages

Before packaging a releasable commit, the workflow runs source validation.

### Python compile check

```powershell
python -m compileall -q core app ui main.py
```

A non-zero exit code fails the job.

### Unit tests

```powershell
python -m unittest discover -s tests -v
```

A non-zero exit code fails the job.

## Version embedding

For a releasable commit, the calculated version is written to:

```text
resources/version.txt
```

The packaged application reads this file for updater version comparison and tray version display.

The workflow changes this file in the Actions workspace for the build. It does not need a separate version-bump commit on `main`.

## Dependency installation

The release job uses Python 3.12 and installs:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
```

## Application build

The workflow runs:

```powershell
python build.py
```

This produces:

```text
dist\Quill\Quill.exe
```

and the rest of the PyInstaller `onedir` application folder.

## Packaged smoke test

After building, Actions executes the packaged binary:

```powershell
dist\Quill\Quill.exe --smoke-test
```

The release is blocked if the executable returns a non-zero exit code.

This catches packaging failures that source-level tests cannot detect, such as a Python module missing from the PyInstaller bundle.

## Portable package

The workflow compresses the complete `dist\Quill` folder contents.

Output pattern:

```text
Quill-vX.Y.Z-portable-windows-x64.zip
```

## Installer package

Actions installs Inno Setup with Chocolatey, locates `ISCC.exe`, and compiles:

```text
installer.iss
```

Output pattern:

```text
Quill-vX.Y.Z-setup-windows-x64.exe
```

The installer is per-user and targets:

```text
%LOCALAPPDATA%\Programs\Quill
```

## Release notes

Release notes are generated from commit subjects since the previous release tag.

They also identify the two downloadable packages:

- Installer
- Portable

## Publishing

The final publication step uses GitHub CLI with the workflow token:

```text
gh release create
```

The release:

- creates the semantic version tag
- targets the current GitHub Actions commit
- uploads the portable ZIP
- uploads the setup executable
- uses the generated release notes

## Updater relationship

`core/update_manager.py` queries this repository's latest GitHub Release.

That means the Auto Release workflow is also the production source for Quill's in-app update channel.

Installed updates expect a release asset ending in:

```text
-setup-windows-x64.exe
```

Changing release filenames or repository ownership requires coordinating the updater code.

## Commit authorship

Commits made through connected GitHub automation can be attributed to the authenticated repository identity. Project automation commits may also include:

```text
Co-authored-by: Ella Mizuki <ella@yuricunha.com>
```

when appropriate.

## Recommended release discipline

For a feature touching several files, prefer one atomic `feat:` commit when practical.

This avoids triggering intermediate versions while the feature is only partially integrated.

For follow-up corrections before a release is published, a `fix:` commit can be used, but the best outcome is to keep `main` releasable at every pushed code commit.

For documentation-only changes, use `docs:`.

## Related documentation

- [Development](development.md)
- [Architecture](architecture.md)
- [Updates and Data](updates-and-data.md)
