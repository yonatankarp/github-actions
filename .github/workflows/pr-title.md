# `pr-title.yml`

Reusable workflow that fails a pull request whose title doesn't start with its kind: `kind: text`, `kind(scope): text`, or `kind!: text` for a breaking change. The [`release-notes`](../actions/release-notes) action sorts pull requests by that kind, so this keeps every merged title readable by it.

The check is a bash pattern on the title; it doesn't check out the code or need a token.

## Inputs

| Name    | Required | Default                                     | Description                                    |
|---------|----------|---------------------------------------------|------------------------------------------------|
| `kinds` | no       | `feat,change,fix,docs,chore,ci,test,refactor` | Comma-separated kinds a title may start with. |

The scope is free text (`feat(Sessions): …`, `fix(cli): …`).

## Required caller permissions

None.

## Usage

```yaml
name: Pull request title

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

permissions: {}

jobs:
  title:
    uses: yonatankarp/github-actions/.github/workflows/pr-title.yml@v2
```

With other kinds:

```yaml
    with:
      kinds: feat,fix,chore
```

## Notes

- **`edited` matters.** Without it, fixing the title doesn't re-run the check.
- **Required check.** Make `title / title` a required status check in branch protection so a wrong title blocks the merge.
- **Dependabot.** Its titles (`Bump …`) fail the default kinds. Set a `commit-message` `prefix` (e.g. `chore`) in `dependabot.yml`, or skip the job with `if: github.actor != 'dependabot[bot]'`.
