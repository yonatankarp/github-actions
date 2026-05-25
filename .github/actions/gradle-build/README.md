# `gradle-build`

Composite action that runs `./gradlew build`, optionally scoped to a single Gradle module path.

Assumes the consumer has already checked out the repo and run [`prepare-jvm-build`](../prepare-jvm-build) (or equivalent JDK + Gradle setup).

## Inputs

| Name            | Required | Default | Description                                                              |
|-----------------|----------|---------|--------------------------------------------------------------------------|
| `gradle-module` | no       | `''`    | Gradle module (e.g. `:app`, `:nested:module`). Empty runs the root task. |

## Required caller permissions

None.

## Usage

```yaml
- uses: actions/checkout@v6
- uses: yonatankarp/github-actions/.github/actions/prepare-jvm-build@v2
- uses: yonatankarp/github-actions/.github/actions/gradle-build@v2
```

For a specific module:

```yaml
- uses: yonatankarp/github-actions/.github/actions/gradle-build@v2
  with:
    gradle-module: ':app'
```

## Notes

- **Module syntax.** Use Gradle's colon-prefixed path (e.g. `:app`, `:skeletons:spring`). Bare names without the leading `:` won't resolve.
