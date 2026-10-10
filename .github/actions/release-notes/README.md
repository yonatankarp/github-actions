# `release-notes`

Composite action that writes a version's release notes from the pull requests merged since the previous `v*` tag. Each pull request's title picks its heading, so pair it with the [`pr-title.yml`](../../workflows/pr-title.md) check. The script is plain Python 3 (standard library only) and runs locally too, for a preview before tagging.

What goes in:

- **The title's kind picks the heading:** `feat:` under **✨ New features**, `change:` under **🔧 Improvements**, `fix:` under **🐞 Bug fixes**. `docs`, `chore`, `ci`, `test` and `refactor` are left out.
- **Dependency upgrades** (`chore(deps): …`, Dependabot's default) get a section of their own, last, when `dependencies` names its heading. Libraries usually want this, since their users inherit those versions. Without it they're left out like any chore.
- **A scope is only a label** (`feat(Sessions): …` stays under New features), unless it's listed in `scope-sections`, which gives it a heading of its own (`cli=⌨️ In Terminal` puts `fix(cli): …` there).
- **The entry** is the first paragraph under a `## Release note` heading in the pull request's description, or the title when there is none. `none` leaves the pull request out. A paragraph becomes one bullet; a list stays a list.
- **Links and HTML are taken out**, since anyone can edit a description: a link keeps its text, tags and comments go, and a bare URL loses its `https://` so nothing autolinks.
- **A count line goes on top:** "This update has 7 improvements and 1 bug fix." Dependency upgrades count as "dependency updates". A scope section adds ", plus more in Terminal." (its heading, without the emoji, after "more").
- **It fails** when the version has no `feat`, `fix` or `change` pull request (or dependency upgrade, with `dependencies` set), so an empty release never goes out.

The pull requests are found on the first-parent history between the two tags: merge commits (`Merge pull request #12 from …`) and squash merges (`Title (#12)`) both work. A commit with neither is left out with a warning.

The descriptions are read when the action runs, not when the pull requests were merged, so an edit to a merged pull request's `## Release note` still changes the notes.

## Inputs

| Name             | Required | Default            | Description                                                                                                         |
|------------------|----------|--------------------|---------------------------------------------------------------------------------------------------------------------|
| `version`        | yes      | —                  | The version, with or without its `v` (`v0.8.0` or `0.8.0`).                                                         |
| `ref`            | no       | `''`               | Where the notes end. Empty means the `v<version>` tag; `origin/main` gives a preview before tagging.                |
| `override`       | no       | `''`               | A path pattern such as `release-notes/{version}.md` (`{version}` without its `v`). When that file exists, it's published word for word instead. |
| `footer`         | no       | `''`               | A file appended after the generated notes, such as install instructions. Not appended to an override file.          |
| `scope-sections` | no       | `''`               | One `scope=heading` per line, e.g. `cli=⌨️ In Terminal`. Only listed scopes get their own section.                  |
| `dependencies`   | no       | `''`               | A heading for dependency upgrades (`chore(deps)` pull requests), e.g. `📦 Dependencies`. Empty leaves them out.      |
| `output`         | no       | `release-notes.md` | Where to write the notes.                                                                                           |

## Outputs

| Name   | Description                 |
|--------|-----------------------------|
| `path` | The path of the notes file. |

## Required caller permissions

```yaml
permissions:
  contents: read
  pull-requests: read
```

`gh` reads the pull requests with `GH_TOKEN` when the job sets one, or `github.token` otherwise. The runner needs `python3`, `git` and `gh`, which GitHub's Ubuntu and macOS runners have.

## Usage

Check out with the whole history and the tags first (`fetch-depth: 0`): the action looks for the previous tag.

```yaml
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: read
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0

      - id: notes
        uses: yonatankarp/github-actions/.github/actions/release-notes@v2
        with:
          version: ${{ github.ref_name }}
          override: release-notes/{version}.md
          scope-sections: |
            cli=⌨️ In Terminal

      - env:
          GH_TOKEN: ${{ github.token }}
          NOTES: ${{ steps.notes.outputs.path }}
        run: gh release create "$GITHUB_REF_NAME" --draft --notes-file "$NOTES"
```

## Preview locally

From the project's checkout, with `gh` signed in:

```bash
python3 path/to/github-actions/.github/actions/release-notes/release_notes.py 0.8.0 origin/main \
  --override 'release-notes/{version}.md' --scope-section 'cli=⌨️ In Terminal'
```

Without a `ref` it ends at the `v0.8.0` tag. `--footer FILE` and `--dependencies HEADING` work as the inputs do.

## Notes

- **Older versions.** A version whose notes live somewhere else (a `CHANGELOG.md` section, say) gets an `override` file.
- **Tests.** `python3 -m unittest discover -s .github/actions/release-notes` runs in [`ouroboros.yml`](../../workflows/ouroboros.md).
