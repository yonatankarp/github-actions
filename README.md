# GitHub Actions

[![Continuous Integration](https://github.com/yonatankarp/github-actions/actions/workflows/ouroboros.yml/badge.svg)](https://github.com/yonatankarp/github-actions/actions/workflows/ouroboros.yml)


Shared place for GitHub composable actions and workflows

---

## Available workflows

- [ci](.github/workflows/ci.yml) - Builds the project and if selected a docker image
- [linters](.github/workflows/linters.yml) - Runs the configured linters on the project
- [dependabot-auto-merge](.github/workflows/dependabot-auto-merge.yml) - Runs a pipeline that allows dependabot to automatically merge PRs that opened by it.
- [update-gradle-wrapper](.github/workflows/update-gradle-wrapper.yml) - A pipeline that allows upgrading gradle wrapper to its latest version. The pipeline can be executed nightly using GitHub action chron jobs.

---

## Replace Tag

Once a new change was added to the pipeline, you can move the tag to the current
commit by running the following script on the required branch:

```shell
$ sh ./bin/replace-tags.sh <TAG>
```

for example:

```shell
$ sh ./bin/replace-tags.sh v1
```
