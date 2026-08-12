# Cloudflare Pages public-artifact recovery

This directory is an immutable, public-only recovery of production deployment
`cccdee7a-2286-4a95-b514-5b36ab2bf45a`. It is deliberately separate from
`dist-cloudflare`: the original ad-hoc deployment was marked dirty and its
public bytes do not match the later generated export.

The files in `site/` were fetched only from the deployment's public Pages
origin. `manifest.json` pins their SHA-256 digests and records Cloudflare's
per-file identifiers. Verify the checkout without network access:

```sh
python3 scripts/verify_pages_public_artifact.py
```

This is a preservation artifact, not a deploy instruction. A later deployment
workflow must explicitly select this directory and separately verify redirects,
headers, and domain routing before any cutover.
