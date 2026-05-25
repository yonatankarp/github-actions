# `detect-source-changes`

Composite action that wraps [`dorny/paths-filter`](https://github.com/dorny/paths-filter) with a curated filter for the standard JVM/Gradle source set plus an optional Dockerfile. Emits a single boolean output `source_code` so downstream steps can short-circuit when nothing build-relevant changed.

Files that count as a source change:

- `.github/workflows/**`
- `.github/actions/**`
- `**/src/**`
- `**/build.gradle.kts`
- `gradle/libs.versions.toml`
- `gradle/wrapper/gradle-wrapper.properties`
- `gradlew`, `gradlew.bat`, `settings.gradle.kts`
- The supplied `dockerfile-path`, if any.

## Inputs

| Name              | Required | Default | Description                                                                                  |
|-------------------|----------|---------|----------------------------------------------------------------------------------------------|
| `dockerfile-path` | no       | `''`    | Optional Dockerfile path to include in the filter. Leave empty if the repo has no Dockerfile.|

## Outputs

| Name          | Description                                                            |
|---------------|------------------------------------------------------------------------|
| `source_code` | `'true'` if any path matched the filter, `'false'` otherwise.          |

## Required caller permissions

None.

## Usage

```yaml
- uses: actions/checkout@v6

- id: changes
  uses: yonatankarp/github-actions/.github/actions/detect-source-changes@v2
  with:
    dockerfile-path: ./Dockerfile

- if: steps.changes.outputs.source_code == 'true'
  run: ./gradlew build
```

## Notes

- **Output is a string.** GitHub Actions outputs are always strings — compare against `'true'` (with quotes), not the boolean `true`.
- **Caller must check out first.** `paths-filter` runs against the working tree; check out the repo before this step.
