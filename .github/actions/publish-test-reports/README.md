# `publish-test-reports`

Composite action that publishes JUnit results as a GitHub Check and uploads HTML test reports + JaCoCo coverage as workflow artifacts. Both steps use `if: always()` so they run even when the build fails (so red builds still get reports).

Steps it performs:

1. `EnricoMi/publish-unit-test-result-action@v2` — turns JUnit XML into a Check.
2. `actions/upload-artifact@v7` — uploads `**/build/reports/tests/**` and `**/build/reports/jacoco/test/**`.

## Inputs

| Name             | Required | Default                                       | Description                                                                                  |
|------------------|----------|-----------------------------------------------|----------------------------------------------------------------------------------------------|
| `junit-pattern`  | no       | `**/build/test-results/test/TEST-*.xml`       | Glob for JUnit XML files.                                                                    |
| `artifact-name`  | no       | `test-reports`                                | Name of the uploaded artifact bundle.                                                        |
| `check-name`     | no       | `Test Results`                                | Name of the GitHub Check. Pass a unique value per matrix variant to avoid clobbering.        |

## Required caller permissions

The calling job **must** grant:

```yaml
permissions:
  pull-requests: write
  checks: write
```

Without these, `publish-unit-test-result-action` cannot create the Check.

## Usage

```yaml
- if: always()
  uses: yonatankarp/github-actions/.github/actions/publish-test-reports@v2
```

In a matrix build, give each variant a unique check name so they don't overwrite each other:

```yaml
- if: always()
  uses: yonatankarp/github-actions/.github/actions/publish-test-reports@v2
  with:
    check-name: Test Results (${{ matrix.variant }})
    artifact-name: test-reports-${{ matrix.variant }}
```

## Notes

- **Always-run.** Both inner steps use `if: always()`, but the action itself only runs if the caller's `if:` lets it. Wrap the caller step with `if: always()` to publish even on failure.
- **Unique names in matrices.** Duplicate `check-name` values across matrix legs cause the last-finishing leg to clobber the others' Check. Same for `artifact-name`.
- **`pull-requests: write` requirement** comes from `publish-unit-test-result-action`, which posts a PR comment with the summary in addition to the Check.
