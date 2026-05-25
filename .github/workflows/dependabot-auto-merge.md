# `dependabot-auto-merge.yml`

Reusable workflow that auto-approves and auto-merges Dependabot PRs for **semver-minor and semver-patch** updates, optionally moving a floating major tag (e.g. `v2`) to the post-merge SHA.

Behavior:

1. Fetch Dependabot metadata for the PR.
2. Approve the PR (only for minor/patch updates).
3. Wait for all required status checks to pass.
4. `gh pr merge --admin --rebase`.
5. _(optional)_ Run the tagging script to move `v2` to the new merge commit.

**Major-version bumps are intentionally _not_ auto-merged** — they need a human eye.

The `if: github.actor == 'dependabot[bot]'` guard means this job is a no-op on non-Dependabot PRs; safe to wire into a generic CI pipeline (see [`ouroboros.yml`](./ouroboros.md) for the in-repo example).

## Inputs

| Name                  | Required | Default                  | Description                                                                                  |
|-----------------------|----------|--------------------------|----------------------------------------------------------------------------------------------|
| `auto-update-tag`     | no       | `false`                  | When `true`, run `tagging-script-path` after a successful merge to move `v2` to the new SHA. |
| `tagging-script-path` | no       | `./bin/replace-tags.sh`  | Path to the tagging script inside the consumer repo.                                         |

## Secrets

| Name         | Required | Description                                                                                                       |
|--------------|----------|-------------------------------------------------------------------------------------------------------------------|
| `GITHUB_PAT` | yes      | PAT that can **approve** and **merge** PRs. The default `GITHUB_TOKEN` can't approve PRs created by `dependabot[bot]`. |

## Required caller permissions

```yaml
permissions:
  contents: write
  pull-requests: write
```

`contents: write` is needed for the tag-moving step. `pull-requests: write` lets `gh` operate on the PR.

## Usage

In the consumer repo's CI workflow:

```yaml
jobs:
  dependabot:
    if: ${{ github.actor == 'dependabot[bot]' }}
    permissions:
      contents: write
      pull-requests: write
    uses: yonatankarp/github-actions/.github/workflows/dependabot-auto-merge.yml@v2
    secrets:
      GITHUB_PAT: ${{ secrets.CI_PAT }}
```

With floating-tag updates enabled (used by the workflows-repo itself to keep `v2` current):

```yaml
    with:
      auto-update-tag: true
```

## Notes

- **PAT, not `GITHUB_TOKEN`.** Dependabot PRs can't be approved by the same user (the bot is the author), and the default `GITHUB_TOKEN` lacks the cross-actor approval permission. A PAT (or fine-grained token with `pull_requests: write` + `contents: write`) is required.
- **Status-check wait.** `gh pr checks --watch --required` polls until all required checks complete. If a required check hangs, this job will sit idle until the runner times out — set the calling job's `timeout-minutes` accordingly.
- **Concurrency.** The workflow declares `concurrency: group: <workflow>-<ref>`. Repeated invocations on the same PR replace the previous run.
- **Major bumps are skipped.** The `if:` condition only matches `version-update:semver-minor` and `version-update:semver-patch`. Other update types fall through without approval or merge.
