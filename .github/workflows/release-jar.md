# `release-jar.yml`

Reusable workflow that builds a JAR artifact and publishes it to **GitHub Packages** (Maven). The caller wires its own trigger (typically `release: types: [published]` or a tag-push).

Internally delegates to the [`build-jar-artifact`](../actions/build-jar-artifact) composite action and then runs `./gradlew publishMavenPublicationToGitHubPackagesRepository`.

## Inputs

| Name           | Required | Default | Description                                                                                  |
|----------------|----------|---------|----------------------------------------------------------------------------------------------|
| `tag`          | yes      | —       | Release tag (e.g. `1.2.3`). Used as the published artifact version.                          |
| `module-name`  | no       | `''`    | Gradle module to build/publish. Empty assumes a single-module (non-modular) project.         |

## Secrets

| Name           | Required | Description                                                                                  |
|----------------|----------|----------------------------------------------------------------------------------------------|
| `github-token` | yes      | PAT with `write:packages` (and `repo` for private repos) — used for submodule checkout _and_ as the credential the Gradle plugin uses to publish to GitHub Packages. |

## Required caller permissions

The reusable workflow handles its own auth via the passed-in secret, so the caller's `permissions:` block needs no extras beyond the default `contents: read`.

## Usage

```yaml
name: Release
on:
  release:
    types: [published]

jobs:
  jar:
    uses: yonatankarp/github-actions/.github/workflows/release-jar.yml@v2
    with:
      tag: ${{ github.event.release.tag_name }}
    secrets:
      github-token: ${{ secrets.PUBLISH_PACKAGES_PAT }}
```

Multi-module project:

```yaml
    with:
      tag: ${{ github.event.release.tag_name }}
      module-name: app
```

## Notes

- **`GITHUB_TOKEN` is _not_ sufficient.** GitHub Packages publishing across repos requires a PAT (or fine-grained token) with `write:packages`. The default `GITHUB_TOKEN` works only for publishing into the same repo — and not at all for submodule checkout into private repos.
- **Version comes from the input.** `build-jar-artifact` writes `version=<tag>` into `gradle.properties` before the build; the Gradle publish plugin picks that up. Don't override `version` in your `build.gradle.kts` if you want this to work.
- **Submodules supported.** `build-jar-artifact` checks out with `submodules: recursive` using the same `github-token`. Make sure that token can read the submodule repos.
