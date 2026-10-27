# P1-IR correction evidence manifest — 27 October 2026

**Evidence-only metadata; not a new tested implementation.**
- New corrected tested implementation: `752752f880ed7c4b0c77d399ca7c99f9a9bb094e`.
- GitHub Actions exact-source run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40539883955
- Historical tested source: `6eb62daec638185f5c5dc170182e9e0454b6e061`.
- Frozen protocol SHA256: `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0`.
- Checkpoint-corrected historical source: `03cf5718da6b88c05c75ce492ea963507899f66b`.

## Github Actions artifact contents and independent SHA256 snapshots

Original CI artifact downloads were retained as unchanged ZIPs and hashed outside GitHub, yielding:

| Artifact | GitHub artifact ID | SHA256 of downloaded ZIP |
|---|---:|---|
| `p1-ir-corrected-verification.zip` | 12749493847 | `2d586048fa17239a1dba7f74009886b7dab3086789429dfa9b1dd2cdef61f334` |
| `p1-ir-original-rerun.zip` | 12749214412 | `4626fe867d4334ed49d86bc8df1ce50b79bc778aef7d8e0dce068c6713dbe0d4` |
| `p1-ir-integrity.zip` | 12749732785 | `bddd841abfcd028c645f2a1d0e134d086c785e5330cd52370b26e227e7466356` |

The separately packaged `provenance.json` has SHA256 `2f335a389426f0c8ecf4d6ce9589f3682c2bf6ce0bfc1c9e6741618092484bbb`. A combined ZIP containing the three exact unchanged CI ZIPs, provenance and a SHA256 manifest was constructed for the implementation handover, without replacing the original confirmatory archive.

## Verified exact execution outcomes

All **three jobs** in run 40539883955 completed successfully.

- Corrected P1 comparator / IR adversarial / numerical focused suite: **35 passed in 4.52 s**.
- Full foundation/recovery suite: **370 passed in 94.99 s**.
- Original source isolated checkout `6eb62da...`: **13 focused tests passed** and **348 full foundation/recovery tests passed**.
- Archive audit: original Actions archive **405 files**; repository preserved **412 files**; **zero missing**, **zero modified**; seven identified supplementary report/log/figure/manifest files.
- Strict supplementary CPU metrology: both arms had seven non-warm-up replications. Control mean **104.846398 ms**, SD **0.3079557 ms**; feedback mean **108.7202721 ms**, SD **5.2615943 ms**. At an 80ms prefix, control evaluated 3 candidates every time, whereas feedback evaluated 2 or 3. The benchmark is supplementary and **not new confirmatory data**.

## Reviewer requirement

These are developer-team executed CI and manifest findings, **NOT independently reviewed Gate 3 evidence**. Independently reproduce selected challenges, archive hashes, CPU thresholds and correction semantics, and decide all Gates separately. No numerical effects from original 80-pair frozen study were changed or retrospectively selected.
