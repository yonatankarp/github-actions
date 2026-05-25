# `publish-docker-image`

Composite action that builds a multi-arch Docker image with `buildx` and pushes it to the specified container registry. Registry-agnostic: the caller supplies the registry hostname and credentials. Used internally by the `release-docker-ghcr.yml` reusable workflow; will also back the future `release-docker-dockerhub.yml`.

Steps it performs:

1. `actions/checkout@v6`
2. `docker/setup-qemu-action@v3` (for cross-arch emulation)
3. `docker/setup-buildx-action@v3`
4. `docker/login-action@v3` against `inputs.registry`
5. `docker/metadata-action@v5` to compute tags (`<tag>`, optionally `latest`) and OCI labels
6. `docker/build-push-action@v6` with provenance attestation

## Inputs

| Name            | Required | Default                     | Description                                                                                  |
|-----------------|----------|-----------------------------|----------------------------------------------------------------------------------------------|
| `registry`      | yes      | —                           | Container registry hostname (e.g. `ghcr.io`, `docker.io`).                                   |
| `image-name`    | yes      | —                           | Image name under the registry (e.g. `yonatankarp/cat-fact-service`).                         |
| `tag`           | yes      | —                           | Primary image tag (e.g. `1.2.3`).                                                            |
| `username`      | yes      | —                           | Registry username.                                                                           |
| `password`      | yes      | —                           | Registry password or access token. See "Secrets" note below.                                 |
| `dockerfile`    | no       | `./Dockerfile`              | Path to the Dockerfile.                                                                      |
| `build-context` | no       | `.`                         | Docker build context directory.                                                              |
| `platforms`     | no       | `linux/amd64,linux/arm64`   | Comma-separated buildx target platforms.                                                     |
| `latest`        | no       | `true`                      | Also tag the image as `:latest`. Pass `"true"` or `"false"`.                                 |
| `provenance`    | no       | `mode=min`                  | Provenance attestation setting (`mode=min`, `mode=max`, `false`).                            |

## Secrets

Composite actions cannot accept GitHub Actions `secrets` directly — only `inputs`. The caller must pass the secret **value** to `password`, e.g.:

```yaml
with:
  password: ${{ secrets.GITHUB_TOKEN }}        # GHCR
  # or
  password: ${{ secrets.DOCKERHUB_TOKEN }}     # Docker Hub
```

## Required caller permissions

For GHCR pushes, the calling job needs:

```yaml
permissions:
  contents: read
  packages: write
  attestations: write
  id-token: write
```

For Docker Hub, only `contents: read` is needed (auth is via Docker Hub credentials, not the GitHub token).

## Usage

Direct call from a job (rare — most callers should use the higher-level reusable workflows instead):

```yaml
- name: Publish to GHCR
  uses: yonatankarp/github-actions/.github/actions/publish-docker-image@v2
  with:
    registry: ghcr.io
    image-name: ${{ github.repository }}
    tag: ${{ github.event.release.tag_name }}
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

## Notes

- **Multi-arch build time:** `linux/arm64` is emulated via QEMU on `ubuntu-latest` runners, which is 3–5× slower than native amd64.
- **Provenance:** `mode=min` attaches signed metadata linking the image to the workflow run. Set `provenance: false` to disable, or `mode=max` for fuller build-step details.
