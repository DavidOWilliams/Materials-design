# Preserved accepted WP4 baseline and evidence

This directory preserves the exact downloaded GitHub Actions artifact and a source archive of the accepted implementation. These files are committed to Git rather than relying on Actions artifact retention.

## Identities

- **Tested and accepted implementation:** `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`; baseline branch `wp4-tested-2026-10-25`.
- **Documentation-only acceptance record:** `1805811acdafacd66ba3574e8cb45c59bebdd8e5`; baseline branch `wp4-acceptance-record-2026-10-25`.
- **Actual CI checkout:** `57c7d6134a6e9f4a1d30077d5d8575dd1a4c899c`, a temporary PR merge with the same source tree as the implementation.
- **This archive commit:** preservation only. It is neither the tested implementation nor a newly tested release.

The source tarball contains the tested implementation, not the later acceptance documentation. The exact evidence ZIP has SHA-256 `36eb05e5e69bc0af8a86c08fbada5b97fa6c9a5f6b8b64b3478020df588b831d` and 49 entries. It passed ZIP integrity validation. The source and acceptance commits remain reachable through separate baseline branches and this branch history. Branches are named references, not a claim of server-enforced immutability; do not move or delete them.

## Verification and restoration

Archives are stored as ordered binary parts to support reliable transfers. From this directory run `python3 restore.py` to verify every part and reconstruct the original ZIP and source tarball, then run `sha256sum -c SHA256SUMS`. No recompression or change to the original archive bytes is performed. `MANIFEST.json` records file digests and origin IDs; `EVIDENCE_CONTENTS.json` records each archived evidence file digest. Extract the source tarball separately or check out the tested commit/baseline branch. Use the environment instructions and dependency lockfile from that tested source.

The evidence ZIP's `wp4-tested-sha.txt` correctly contains the CI merge checkout, not the source commit. Source-tree equivalence is recorded in the manifest. The final workflows are:

- https://github.com/DavidOWilliams/Materials-design/actions/runs/40231063605
- https://github.com/DavidOWilliams/Materials-design/actions/runs/40231063596

The original Actions artifact expires on 23 January 2027. The Git copy is independent of that expiry. No claim is made that GitHub storage is an externally immutable or independently authenticated archive.

## Scope

Acceptance covers the bounded synthetic software/numerical demonstration only. Intended design, estimated achieved state and measured evidence remain distinct. There is no experimental ceramic validation, full D1 release or V1 completion claim. Prior test counts apply to the pinned implementation/source-equivalent CI checkout, not documentation or archive commits. This preservation action does not merge PR #4 or start WP5.
