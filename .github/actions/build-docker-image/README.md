# `build-docker-image`

Composite action that runs a single-architecture `docker build` against the supplied Dockerfile. Image name is sanitized to lowercase (Docker requires it). Does **not** push — used for CI build-verification only. For release/push, see [`publish-docker-image`](../publish-docker-image).

## Inputs

| Name              | Required | Default       | Description                                                                  |
|-------------------|----------|---------------|------------------------------------------------------------------------------|
| `image-name`      | yes      | —             | Docker image name. Sanitized to lowercase for Docker compatibility.          |
| `dockerfile-path` | yes      | —             | Path to the Dockerfile relative to `build-context`.                          |
| `build-context`   | no       | `.`           | Docker build context directory.                                              |

## Outputs

None.

## Required caller permissions

None beyond the defaults — the action does not push, log in, or read repository metadata.

## Usage

```yaml
- uses: actions/checkout@v6

- uses: yonatankarp/github-actions/.github/actions/build-docker-image@v2
  with:
    image-name: cat-fact-service
    dockerfile-path: ./Dockerfile
```

## Notes

- **Build-only.** Image is built as `<sanitized-name>:latest` on the runner and discarded when the job ends. Use [`publish-docker-image`](../publish-docker-image) to push to a registry.
- **Single arch.** Builds for the runner's native architecture only. No `buildx`, no QEMU. Add cross-arch builds via `publish-docker-image` instead.
