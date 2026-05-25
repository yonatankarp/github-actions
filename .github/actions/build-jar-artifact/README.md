# `build-jar-artifact`

Composite action that checks out the repo (with submodules), installs the requested JDK, writes the release version into `gradle.properties`, and runs `./gradlew build` — optionally scoped to a single module. Used as the build step inside [`release-jar.yml`](../../workflows/release-jar.yml).

Steps it performs:

1. `actions/checkout@v6` with `submodules: recursive` (token-authenticated).
2. `actions/setup-java@v5` with Gradle caching.
3. Writes `version=<tag>` to `gradle.properties`.
4. Runs `./gradlew build` or `./gradlew :<module>:build`.

## Inputs

| Name               | Required | Default     | Description                                                                                  |
|--------------------|----------|-------------|----------------------------------------------------------------------------------------------|
| `tag`              | yes      | —           | Release tag (e.g. `1.2.3`). Written to `gradle.properties` as `version=<tag>`.               |
| `github-token`     | yes      | —           | Token used for submodule checkout. Pass `${{ secrets.GITHUB_TOKEN }}` or a PAT with the right scopes when private submodules are involved. |
| `module-name`      | no       | `''`        | Gradle module to build (e.g. `app`). Empty runs the root build.                              |
| `jvm-version`      | no       | `25`        | JDK major version.                                                                           |
| `jvm-distribution` | no       | `temurin`   | JDK distribution passed to `actions/setup-java`.                                             |

## Required caller permissions

None beyond what `actions/checkout` and `setup-java` need (typically `contents: read`).

## Usage

```yaml
- uses: yonatankarp/github-actions/.github/actions/build-jar-artifact@v2
  with:
    tag: ${{ github.event.release.tag_name }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

With a module and a non-default JDK:

```yaml
  with:
    tag: ${{ github.event.release.tag_name }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    module-name: app
    jvm-version: '21'
```

## Notes

- **Includes checkout.** Unlike most actions in this repo, this one runs `actions/checkout` itself with `submodules: recursive`. Don't double-check-out in the caller.
- **Submodule access.** If the repo has private submodules, pass a PAT with `repo` scope as `github-token`; the default `GITHUB_TOKEN` cannot read other private repos.
