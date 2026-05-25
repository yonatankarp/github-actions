# `ouroboros.yml`

**This workflow is _not_ a reusable workflow.** It is the in-repo CI that tests this repo's own reusable workflows and composite actions against the bundled skeleton projects under `skeletons/`. Named after [Ouroboros](https://en.wikipedia.org/wiki/Ouroboros) — the serpent eating its tail — because it uses the workflows-repo to test the workflows-repo.

Triggered on `pull_request` (`opened`, `synchronize`, `reopened`, `ready_for_review`).

## What it runs

| Job                  | Purpose                                                                                                              |
|----------------------|----------------------------------------------------------------------------------------------------------------------|
| `pipeline`           | Matrix call to [`ci.yml`](./ci.md) across 4 variants (spring/ktor skeletons, with/without Docker, with submodule).   |
| `dependabot_auto_merge` | Calls [`dependabot-auto-merge.yml`](./dependabot-auto-merge.md) when the PR author is `dependabot[bot]`.          |
| `linters`            | Calls [`linters.yml`](./linters.md).                                                                                 |
| `actions-linter`     | Runs `devops-actions/actionlint` against the workflow YAMLs.                                                         |
| `all-green`          | Aggregates `pipeline`, `linters`, `actions-linter` into a single required check via `re-actors/alls-green`.          |

## Matrix variants tested by `pipeline`

| Variant                       | `image_name`     | `dockerfile_path`              | `gradle_module`     | Why                                          |
|-------------------------------|------------------|--------------------------------|---------------------|----------------------------------------------|
| `spring-skeleton`             | `spring-skeleton`| `skeletons/spring/Dockerfile`  | _(root)_            | Baseline Spring build.                       |
| `ktor-skeleton-uppercase`     | `KTOR-SKELETON`  | `skeletons/ktor/Dockerfile`    | _(root)_            | Exercises the lowercase-sanitization path.   |
| `spring-skeleton-no-docker`   | `spring-skeleton`| _(empty)_                      | _(root)_            | Confirms the Docker step is skipped.         |
| `spring-skeleton-submodule`   | `spring-skeleton`| `skeletons/spring/Dockerfile`  | `:skeletons:spring` | Confirms module-scoped builds work.          |

## Permissions

Top-level grants `contents: write` (needed by `dependabot_auto_merge` for tag-moving). Each job tightens the scope further as needed.

## Secrets used

- `CI_PAT` — passed to `dependabot_auto_merge` as `GITHUB_PAT`. Set this in repo secrets.

## Notes

- **Not callable.** This workflow has no `workflow_call` trigger; do not try to `uses:` it from another repo.
- **Local `uses: ./...`.** Sub-jobs reference `./.github/workflows/ci.yml` etc. — the local files, not the published `@v2` tag. That's intentional: the point is to test the in-progress branch, not the released version.
- **`all-green` is the only required check.** Set repo branch-protection to require `all-green` and skip the individual sub-jobs.
- **Concurrency.** `<workflow>-<job>-<ref>` with `cancel-in-progress: true` — pushing a new commit to a PR cancels the previous run.
