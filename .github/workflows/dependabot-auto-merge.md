# `dependabot-auto-merge.yml`

Reusable workflow that auto-approves and auto-merges Dependabot PRs for **semver-minor and semver-patch** updates.

Behavior:

1. Fetch Dependabot metadata for the PR.
2. Approve the PR (only for minor/patch updates).
3. Wait for all required status checks to pass.
4. `gh pr merge --admin --rebase`.

**Major-version bumps are intentionally _not_ auto-merged** — they need a human eye.

The `if: github.actor == 'dependabot[bot]'` guard means this job is a no-op on non-Dependabot PRs; safe to wire into a generic CI pipeline (see [`ouroboros.yml`](./ouroboros.md) for the in-repo example).

Floating-tag moves (e.g. advancing `v2` after a merge) are handled separately by [`move-major-tag.yml`](./move-major-tag.md), which runs on every push to `main` regardless of author.

## Inputs

None.

## Secrets

| Name         | Required | Description                                                                                                       |
|--------------|----------|-------------------------------------------------------------------------------------------------------------------|
| `GITHUB_PAT` | yes      | PAT that can **approve** and **merge** PRs. The default `GITHUB_TOKEN` can't approve PRs created by `dependabot[bot]`. |

## Required caller permissions

```yaml
permissions:
  contents: read
  pull-requests: write
```

`pull-requests: write` lets `gh` operate on the PR via the PAT.

## Usage

In the consumer repo's CI workflow:

```yaml
jobs:
  dependabot:
    if: ${{ github.actor == 'dependabot[bot]' }}
    permissions:
      contents: read
      pull-requests: write
    uses: yonatankarp/github-actions/.github/workflows/dependabot-auto-merge.yml@v2
    secrets:
      GITHUB_PAT: ${{ secrets.CI_PAT }}
```

## Notes

- **PAT, not `GITHUB_TOKEN`.** Dependabot PRs can't be approved by the same user (the bot is the author), and the default `GITHUB_TOKEN` lacks the cross-actor approval permission. A PAT (or fine-grained token with `pull_requests: write` + `contents: write`) is required.
- **Status-check wait.** `gh pr checks --watch --required` polls until all required checks complete. If a required check hangs, this job will sit idle until the runner times out — set the calling job's `timeout-minutes` accordingly.
- **Concurrency.** The workflow declares `concurrency: group: dependabot-auto-merge-<workflow>-<ref>`. The `dependabot-auto-merge-` prefix keeps this distinct from any group the caller may already hold on `<workflow>-<ref>` — without it, the caller and this reusable workflow self-deadlock on the same key and GitHub cancels the job. Repeated invocations on the same PR still replace the previous run.
- **Major bumps are skipped.** The `if:` condition only matches `version-update:semver-minor` and `version-update:semver-patch`. Other update types fall through without approval or merge.
