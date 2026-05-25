# `move-major-tag.yml`

**This workflow is _not_ a reusable workflow.** It is an in-repo automation that re-points the floating `v2` tag at the current `main` HEAD after every push to `main`, so external consumers calling `@v2` always pick up the latest merged change.

Triggered on `push` to `main`. Internally runs [`bin/replace-tags.sh v2`](../../bin/replace-tags.sh), which force-deletes and re-creates the tag.

## Why this exists

Before this workflow, `v2` was only auto-moved by [`dependabot-auto-merge.yml`](./dependabot-auto-merge.md) (which runs the same script after a Dependabot merge). Human-authored PRs left `v2` stale — consumers wouldn't see changes until the next Dependabot bump. This workflow closes that gap by moving `v2` on **every** merge to `main`, regardless of who authored it.

## What it does

1. `actions/checkout@v6` with `fetch-tags: true` (the script needs the local `v2` tag to delete).
2. `./bin/replace-tags.sh v2` — force-deletes `v2` locally and on `origin`, then re-creates it at HEAD and pushes.

## Permissions

```yaml
permissions:
  contents: write
```

Needed for tag delete + push via `GITHUB_TOKEN`.

## Concurrency

```yaml
concurrency:
  group: move-major-tag
  cancel-in-progress: true
```

If two pushes to `main` happen in quick succession, the second cancels the first — last writer wins, which is exactly what we want (`v2` should track the latest `main`).

## Notes

- **Race with `dependabot-auto-merge`.** For Dependabot merges, _both_ this workflow and the legacy tag-move step in `dependabot-auto-merge.yml` will fire. They produce the same outcome, so the race is harmless, but the legacy step is now redundant and could be retired in a follow-up.
- **`GITHUB_TOKEN`-authored pushes don't trigger workflows.** Moving `v2` via this workflow won't recurse — GitHub deliberately skips workflow triggers for pushes made with the default token, which is exactly the behavior we want here. (Tag pushes don't match `branches: [main]` anyway.)
- **First-time setup on a fork.** `actions/checkout@v6` configures git push to use `GITHUB_TOKEN`. With `contents: write`, the token has tag delete + create rights — no PAT needed.
