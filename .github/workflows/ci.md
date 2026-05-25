# `ci.yml`

Reusable JVM CI workflow. Chains the repo's composite actions into the standard build pipeline:

1. `actions/checkout@v6` (optionally with submodules).
2. [`prepare-jvm-build`](../actions/prepare-jvm-build) — wrapper validation, JDK install, Gradle setup.
3. [`detect-source-changes`](../actions/detect-source-changes) — short-circuit when nothing build-relevant changed.
4. [`gradle-build`](../actions/gradle-build) — runs `./gradlew build` (or scoped to a module). **Skipped when no source changes.**
5. [`publish-test-reports`](../actions/publish-test-reports) — JUnit Check + HTML/JaCoCo artifacts. Runs with `if: always()` to publish on red builds. **Disable via `publish-test-reports: false`.**
6. [`build-docker-image`](../actions/build-docker-image) — only runs when `dockerfile-path` is set _and_ source changed.

## Inputs

| Name                   | Required | Default                              | Description                                                                                  |
|------------------------|----------|--------------------------------------|----------------------------------------------------------------------------------------------|
| `jvm-version`          | no       | `'25'`                               | JDK major version.                                                                           |
| `jvm-distribution`     | no       | `'temurin'`                          | JDK distribution passed to `actions/setup-java`.                                             |
| `gradle-module`        | no       | `''`                                 | Gradle module path (e.g. `:app`). Empty runs the root build.                                 |
| `dockerfile-path`      | no       | `''`                                 | Path to the Dockerfile. Empty disables the docker build step.                                |
| `image-name`           | no       | `${{ github.event.repository.name }}`| Docker image name (sanitized to lowercase by `build-docker-image`).                          |
| `publish-test-reports` | no       | `true`                               | Publish the JUnit Check + upload test/coverage artifacts.                                    |
| `submodules`           | no       | `'false'`                            | Forwarded to `actions/checkout`. Accepts `'false'`, `'true'`, or `'recursive'` (as string).  |

## Secrets

None — uses the auto-provided `GITHUB_TOKEN`.

## Required caller permissions

The reusable workflow declares these on its inner job, but the calling workflow must allow at least:

```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

`pull-requests: write` + `checks: write` are only needed when `publish-test-reports: true` (the default).

## Usage

Minimal:

```yaml
name: CI
on:
  pull_request:

jobs:
  build:
    uses: yonatankarp/github-actions/.github/workflows/ci.yml@v2
```

With a Dockerfile and a specific module:

```yaml
jobs:
  build:
    uses: yonatankarp/github-actions/.github/workflows/ci.yml@v2
    with:
      gradle-module: ':app'
      dockerfile-path: ./Dockerfile
      image-name: cat-fact-service
```

## Notes

- **Build skipped without source changes.** `detect-source-changes` decides whether `gradle-build` and `build-docker-image` run. Doc-only changes therefore skip the build path but still publish (empty) test reports.
- **`submodules` is a string, not a boolean.** `actions/checkout` accepts `false` / `true` / `recursive`; we pass it through unchanged. Type is `string` for that reason.
- **Image name is sanitized.** `build-docker-image` lowercases the image name before tagging, so `image-name: KTOR-SKELETON` builds `ktor-skeleton:latest`.
