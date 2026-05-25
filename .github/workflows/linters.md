# `linters.yml`

Reusable workflow that runs documentation and code-style linters in parallel-ish fashion:

1. `markdown-lint` over all `**/*.md` (when `docs/**` or `README.md` changed).
2. `./gradlew spotlessCheck` (when source-set files changed).

Each linter can be disabled independently via inputs. Both run inside the same job, gated by a [`dorny/paths-filter`](https://github.com/dorny/paths-filter) step to skip work when nothing relevant changed.

Markdown rules come from a bundled `config/markdown-lint/rules.json` (fetched at runtime from the `v2` tag of this repo) unless the caller overrides the path.

## Inputs

| Name                   | Required | Default     | Description                                                                                  |
|------------------------|----------|-------------|----------------------------------------------------------------------------------------------|
| `check_docs`           | no       | `true`      | Run `markdown-lint`.                                                                         |
| `check_style`          | no       | `true`      | Run `spotlessCheck`.                                                                         |
| `jvm-version`          | no       | `'25'`      | JDK version used to run `spotlessCheck`. Only matters when `check_style: true`.              |
| `jvm-distribution`     | no       | `'temurin'` | JDK distribution.                                                                            |
| `markdown-lint-config` | no       | `''`        | Path to a `rules.json` inside the consumer repo. Empty fetches the repo's bundled defaults.  |

## Secrets

None — uses the auto-provided `GITHUB_TOKEN`.

## Required caller permissions

```yaml
permissions:
  contents: read
```

## Usage

Minimal:

```yaml
jobs:
  lint:
    uses: yonatankarp/github-actions/.github/workflows/linters.yml@v2
```

Docs-only repo (skip spotless):

```yaml
    with:
      check_style: false
```

With a custom markdown-lint config:

```yaml
    with:
      markdown-lint-config: ./.markdownlint.json
```

## Notes

- **Input naming.** `check_docs` and `check_style` are snake_case (unlike most other inputs in this repo) for historical reasons; kebab-case breaks GH Actions matrix-key parsing in some contexts.
- **Dependabot checkout.** When the actor is `dependabot[bot]`, the workflow checks out `${{ github.event.pull_request.head.sha }}` instead of the default ref — necessary because Dependabot PRs run with a restricted `GITHUB_TOKEN` and the default checkout can fail.
- **Bundled rules are tag-pinned.** The default markdown-lint config is fetched from `raw.githubusercontent.com/yonatankarp/github-actions/v2/...`. If the floating `v2` tag is moved, the rules change. Pin via `markdown-lint-config` for stability.
