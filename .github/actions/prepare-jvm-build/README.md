# `prepare-jvm-build`

Composite action that validates the Gradle wrapper, installs the requested JDK, and sets up Gradle with shared caching. The standard pre-build step for any JVM workflow in this repo.

Steps it performs:

1. `gradle/actions/wrapper-validation@v6` — verifies `gradle-wrapper.jar` against the Gradle wrapper checksum database.
2. `actions/setup-java@v5` with the requested distribution + version.
3. `gradle/actions/setup-gradle@v6` with the build cache. Read-only cache off `main`; read-write on `main`.

**Assumes the consumer has already checked out the repo.**

## Inputs

| Name               | Required | Default     | Description                                                                                  |
|--------------------|----------|-------------|----------------------------------------------------------------------------------------------|
| `jvm-version`      | no       | `25`        | JDK major version (e.g. `21`, `25`).                                                         |
| `jvm-distribution` | no       | `temurin`   | JDK distribution: `temurin`, `zulu`, `microsoft`, `corretto`, `semeru`, `graalvm`.           |

## Required caller permissions

None.

## Usage

```yaml
- uses: actions/checkout@v6

- uses: yonatankarp/github-actions/.github/actions/prepare-jvm-build@v2
```

With overrides:

```yaml
- uses: yonatankarp/github-actions/.github/actions/prepare-jvm-build@v2
  with:
    jvm-version: '21'
    jvm-distribution: zulu
```

## Notes

- **Cache scope.** Build cache is read-write only on `refs/heads/main`. Feature branches read the cache but cannot poison it.
- **Caller must check out first.** Wrapper validation needs `gradle/wrapper/gradle-wrapper.jar` to exist on disk.
