# D1 v0.2.0 — draft GitHub release notes and reproducible demonstration

**DRAFT ONLY — NOT PUBLISHED; NOT TAGGED.** Intended classification: **bounded internal synthetic demonstration**, no production engineering claim. Proposed immutable annotated tag `d1-v0.2.0` → `280e21e3df62a6e2fcbf5bf4668b6b235ccd8384` (tree `60d0ef541dfe9d2dd38860308d1524206f09c5f5`).

## Release notes — changes versus D1 v0.1.0

This demonstration makes validated *synthetic numerical data* easier to inspect, without adding new physical validation. It adds source-preserving schematic architecture and composition plots for homogeneous/layered/gradient WP3 candidates; measured-coordinate-free numerical objective scatter/trade-off views; source-linked tables, numerical qualification and unknown-state presentation; WP4 conditional estimated-achieved presentation and deviations only when supported by provenance; unused output filename suggestions and dossier-overwrite prevention; browser recovery confirmation that is stable across Streamlit rerenders and correctly invalidates green success on corrupted evidence. Original scientific algorithms and WP3/WP4 numerical outcomes compare identically with v0.1.0.

## Installation (qualifying Linux / compatible Codespaces environment)

Start from a clean checkout of the **approved tag target**, not a later documentation or workflow-only commit:

```bash
git fetch origin --tags
git checkout --detach 280e21e3df62a6e2fcbf5bf4668b6b235ccd8384
git rev-parse HEAD
python3.12 -V
PYTHON=python3.12 bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
.venv-foundation/bin/python -m pip check
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py --server.address 0.0.0.0 --server.port 8501
```

Install Chromium/playwright only for independent browser verification, not for typical use: `.venv-foundation/bin/python -m pip install playwright==1.56.0` and `.venv-foundation/bin/python -m playwright install --with-deps chromium`. The numerical foundation is hash-locked by `foundation/requirements.lock.txt`; Streamlit is pinned at 1.40.2, but the full UI transitive dependency closure is in the saved CI `pip freeze` and is not declared universally hash-locked. Install uses Linux/Ubuntu CI evidence; **no first-user Windows/Edge or independent Codespaces qualification**. Avoid reusing an environment from a different commit.

## Guided first-use demonstration

1. Open the D1 guided UI at localhost:8501 or forwarded Codespaces port. Use a new empty workspace directory and accept only unused output filenames. Never overwrite prior run stores, dossiers, journals or manifests.
2. In WP3, select a synthetic scenario, full **4096 elements** and deterministic budget/seed. Generate and persist proposals for homogeneous, layered and gradient architectures. Compare source-linked composition shape, mass/transmission/thermal-mismatch objectives, eligibility and numerical-qualification status. Source records, not graph interpolation, are authoritative.
3. Inspect the **WP3-only** intended-state Pareto; select a completed **compatible A/B gradient**. Homogeneous, layered, unsupported composition and incompatible source/mesh do not qualify for WP4 handoff.
4. In WP4, preserve original WP3 campaign ledger/store, run the selected design in an unused immutable dossier. Inspect the separate *estimated-achieved-state* feedback and WP4-only Pareto. Unsupported achieved-state overlays are unavailable rather than claimed.
5. Exercise cooperative cancellation at a candidate boundary and recovery into a new dossier. Observe verified success, trigger an ordinary rerender, reopen in a fresh browser and verify source lineage. The previously accepted integrity check rejects missing or corrupted `*.handoff.json`, clears green recovery success and displays warning; byte restoration alone does not revive stale green confirmation.
6. Preserve the **WP4 dossier and companion** together with the underlying **WP3 campaign ledger/run-store/verified full ZIP**. The WP4 JSON plus companion are **not a self-contained relocatable package**. Verify SHA256 and replay in a separate Python process after moving to a clean destination.

For reproducible sample artifacts without overwriting historic evidence:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py d1-v02-examples --elements 4096 --budget 9
```

Confirm generation manifest and three separate-process replays. See `foundation/D1_V02_RELEASE_INSTALL_FIRST_USE.md` for full instructions and `foundation/D1_V02_PUBLICATION_APPROVAL_PACKAGE.md` for exact evidence.

## Reproducibility and independent review

- Independent scientific UI review [PR #23](https://github.com/DavidOWilliams/Materials-design/pull/23) PASS bounded; recovery correction [PR #28](https://github.com/DavidOWilliams/Materials-design/pull/28) all R1–R5 PASS, D1-V02-IR25-01 CLOSED.
- Exact merged commit [post-merge Actions 41099626877](https://github.com/DavidOWilliams/Materials-design/actions/runs/41099626877), evidence **artifact 12998706707**, ZIP SHA256 **`eb0d47e5509dd1d0be637fe30ada6fe3f3cc7eed9a38a3f3045bb53d85722fec`**, 169/169 verified.
- Original corrected implementation [41082638967](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967), artifact 12991415168, ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c` (161/161). Independent [41089182257](https://github.com/DavidOWilliams/Materials-design/actions/runs/41089182257), artifact 12993441777 ZIP SHA256 `3edfd431602a3bb8aecd130cbba541d095ce02a572000577f5e4f9c5aeb4b635` (39/39).
- Do not replace tested SHA with documentation/CI HEAD, PR merge checkout or annotation object SHA. Retain copies before GitHub Actions artifact retention expiry.

## Known limitations and warnings

**Synthetic only.** No measured ceramics property/manufacturability data, real sintering/porosity/CFD/uncertainty qualification, airworthiness certification, production suitability or validated general inverse-design superiority. WP3 intended state and WP4 estimated achieved are distinct numerical contexts, with distinct Pareto sets that cannot be pooled. Qualification is numerical under assumptions, not an experimental engineering claim. Cooperative cancellation at candidate boundaries only. P1/P2/P3/E1/E2 and V1 are outside this release.

**Distribution readiness:** human new-user walkthroughs, accessibility/screen reader/keyboard/contrast, Windows/Edge and Codespaces remain unqualified (F02). Internal bounded technical demonstration only until separately accepted. Obsolete v0.1 CI workflow issue #29 must be resolved before claiming all main CI green; historical failure preserved.

**No permission to create the proposed tag, publish a GitHub Release or deploy is implied by this draft.**
