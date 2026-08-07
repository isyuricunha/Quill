# Release Process

Bragi publishes Windows releases through `.github/workflows/release.yml`.

## Trigger

The workflow runs on every push to `main` and can also be started manually. A workflow run does not automatically mean a release will be created.

Concurrency uses `cancel-in-progress: true` so a newer main push cancels an older in-progress release job.

## Versioning

The workflow reads Conventional Commit messages since the latest semantic-version tag.

| Change | Version bump |
| --- | --- |
| `feat!:` or `BREAKING CHANGE:` | Major |
| `feat:` | Minor |
| `fix:`, `perf:`, `refactor:` | Patch |
| docs/chore/test only | No release |

The Quill-to-Bragi product rebrand is intentionally a breaking major change and starts the Bragi identity at v2.0.0 while retaining the existing project history.

## Validation sequence

Before packaging, the workflow:

1. checks out the complete Git history
2. sets up Python 3.12
3. compiles Python sources with `compileall`
4. runs the unit test suite
5. determines the next semantic version

If no releasable Conventional Commit exists, later packaging steps are skipped.

## Build sequence

For a release, the workflow:

1. writes the resolved version to `resources/version.txt`
2. installs dependencies and PyInstaller
3. runs `python build.py`
4. runs `dist\Bragi\Bragi.exe --smoke-test`
5. creates the portable ZIP
6. installs Inno Setup
7. compiles `installer.iss`
8. generates release notes
9. publishes the GitHub Release

A release is not published if the packaged executable smoke test or installer build fails.

## Artifacts

Published Windows x64 artifacts are:

```text
Bragi-vX.Y.Z-portable-windows-x64.zip
Bragi-vX.Y.Z-setup-windows-x64.exe
```

The portable archive contains the entire PyInstaller `onedir` application. Users should extract all files and run `Bragi.exe`.

## Installed upgrades

The installer retains the historical internal Inno Setup AppId from Quill so an installed Quill copy can be upgraded to Bragi. User-facing names, executable, shortcuts, data namespace and release artifacts are Bragi.

Do not change this AppId without intentionally designing a new migration strategy.

## Repository rename transition

Bragi may be published from the historical repository path during the rename transition. GitHub redirects old repository URLs after a rename, and runtime updater validation accepts release download URLs from both the historical Quill path and the Bragi path.

This keeps existing installed clients updateable across the repository rename.

## Commit authorship

Commits made through the connected GitHub integration use the authenticated account metadata. Maintained project commits may include:

```text
Co-authored-by: Ella Mizuki <ella@yuricunha.com>
```

when appropriate.
