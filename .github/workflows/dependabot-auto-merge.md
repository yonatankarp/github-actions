# `dependabot-auto-merge.yml`

Reusable workflow that auto-approves and auto-merges Dependabot PRs for **semver-minor and semver-patch** updates.

Behavior:

1. Fetch Dependabot metadata for the PR.
2. Approve the PR (only for minor/patch updates).
3. `gh pr merge --auto --rebase` — arms GitHub's **native auto-merge**, which merges once branch protection is satisfied (falls back to a direct merge when auto-merge can't be armed, e.g. no required checks).

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
- **No `needs:` required.** The merge is gated by GitHub's native auto-merge, which waits on whatever branch protection currently requires (required checks, up-to-date branch, conversation resolution). Adding a new required check in the consumer repo needs no workflow change. This also works identically for classic branch protection and rulesets, and is unaffected by `enforce_admins` — no bypass is attempted.
- **"Allow auto-merge" must be enabled** in the consumer repo settings (`Settings → General → Allow auto-merge`), otherwise arming fails.
- **Red checks leave the PR pending, not force-merged.** Unlike the previous `--admin` merge, a failing required check means the PR sits approved with auto-merge armed until checks go green. Failure visibility shifts from "CI job red" to "PR didn't merge".
- **Concurrency.** The workflow declares `concurrency: group: dependabot-auto-merge-<workflow>-<ref>`. The `dependabot-auto-merge-` prefix keeps this distinct from any group the caller may already hold on `<workflow>-<ref>` — without it, the caller and this reusable workflow self-deadlock on the same key and GitHub cancels the job. Repeated invocations on the same PR still replace the previous run.
- **Major bumps are skipped.** The `if:` condition only matches `version-update:semver-minor` and `version-update:semver-patch`. Other update types fall through without approval or merge.
