# `release-docker-ghcr.yml`

Reusable workflow that builds a multi-arch Docker image and pushes it to GitHub Container Registry (GHCR), tagged with the supplied release tag (and optionally `:latest`).

Mirrors the shape of [`release-jar.yml`](./release-jar.yml) — the caller wires up its own trigger (typically on release/tag).

Internally delegates to the [`publish-docker-image`](../actions/publish-docker-image) composite action, which is registry-agnostic and shared with the upcoming Docker Hub release workflow.

## Inputs

| Name            | Required | Default                     | Description                                                                                  |
|-----------------|----------|-----------------------------|----------------------------------------------------------------------------------------------|
| `tag`           | yes      | —                           | Release tag (e.g. `1.2.3`). Used as the primary image tag.                                   |
| `image-name`    | no       | `${{ github.repository }}`  | Image name without registry. Final image is `ghcr.io/<image-name>`.                          |
| `dockerfile`    | no       | `./Dockerfile`              | Path to the Dockerfile.                                                                      |
| `build-context` | no       | `.`                         | Docker build context directory.                                                              |
| `platforms`     | no       | `linux/amd64,linux/arm64`   | Comma-separated target platforms for `buildx`.                                               |
| `latest`        | no       | `true`                      | Also tag the image as `:latest`. Set to `false` for pre-releases / RCs.                      |

## Secrets

None. Authentication uses the automatically-provided `GITHUB_TOKEN`.

## Required caller permissions

The calling job **must** grant at least these permissions — the reusable workflow declaring them is not enough on its own:

```yaml
permissions:
  contents: read
  packages: write
  attestations: write
  id-token: write
```

## Usage

```yaml
name: Release
on:
  release:
    types: [published]

jobs:
  docker:
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write
    uses: yonatankarp/github-actions/.github/workflows/release-docker-ghcr.yml@v2
    with:
      tag: ${{ github.event.release.tag_name }}
```

With overrides:

```yaml
    with:
      tag: ${{ github.event.release.tag_name }}
      image-name: yonatankarp/cat-fact-service
      dockerfile: ./docker/Dockerfile
      platforms: linux/amd64
      latest: false
```

## Notes

- **Package visibility:** GHCR creates packages as **private** on first push. Flip to public in the package settings on GitHub if you want unauthenticated pulls.
- **Multi-arch build time:** `linux/arm64` is built via QEMU emulation on `ubuntu-latest`, which is 3–5× slower than native. Drop to `linux/amd64` if build time matters more than ARM support.
- **Provenance:** Build provenance attestation is enabled (`mode=min`) — signed metadata is attached to the image linking it back to the workflow run that built it. SBOM and full `mode=max` provenance are intentionally not enabled.
