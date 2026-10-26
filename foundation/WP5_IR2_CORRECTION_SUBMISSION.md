# WP5-IR2 — narrow correction submission for independent closure

Date: 26 October 2026. Draft PR #6. **Gate 3 remains OPEN; no independent acceptance of IR2 claimed.**

## Separate independent review findings

**Original WP5-R1:** independently verified and closed by the attached *WP5 Targeted Independent Review*, which tested **source SHA `ccbca12dc3ff049a27d53fa77caf0db21d10e4d5`** in a clean detached worktree, with 325 foundation/recovery tests, 34 focused WP5 tests, live Chromium acceptance, independently authored saved-brief cancellation/recovery and fresh-process replay. This review's results apply to that SHA only. Review archive (user-provided) SHA-256: `3990a70d970c5da5854d58a5f286af6fb77edbcc3da7213ce7904d4e97dcc898`. Preserve the review ZIP externally; this report references it rather than asserting it was committed.

**WP5-IR2:** independently reproduced pre-fix at `ccbca12...`: `execute_journal("invalid.jsonl", budget=0)` raised `ValueError: Positive evaluation budget required` **after** creating the empty journal and its manifest. A valid retry at that path then raised `FileExistsError`. The review archive contains `independent/invalid-zero-budget.jsonl`, its manifest and `independent-results.json` (field `zero_budget_side_effects`). This is the before-fix reproduction evidence. A separate old-SHA worktree regression rerun was not conducted for this submission.

## Narrow correction and new regression tests

- **Source correction commit:** `dd0bc5551cd630ff3ba1276564ab43f41fa4d81a`.
- **Test addition commit:** `42684f6de4db088126c944482bce94417e22761d`.
- **Verified implementation/workflow branch SHA:** `4078a83dc11e14703ff6cc03f5b62f4e48879d14`.
- **Actual successful PR merge checkout SHA:** `326598004be79f26184b43dcf2897b9af9b91bfd`, base `f3e6cfc7f7e9ed885ce681814c0927fc421163c8`.
- **Code:** `foundation/material_core/wp5_service.py`, at entry to `execute_journal` **before any filesystem operation**:
  `if type(budget) is not int or budget < 1: raise ValueError("Positive budget required")`.
- **Regression tests:** `foundation/tests/test_wp5_service.py`: eight parameterized invalid budgets `0,-1,True,False,1.0,1.5,"1",None`, asserting a validation error and no journal, manifest, attempts or parent directory; valid retry at the same path, one-candidate cancellation, real WP4 recovery and numerical replay, immutable journal protection; saved-brief mismatch leaves no journal/parent. All real services, no numerical mocks. Existing R1 tests unchanged.

## Actual CI results and exit status

**Primary successful run:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545 — job success, commands exit **0**:

- `bash foundation/setup.sh` — successful hash-locked foundation environment.
- `.venv-foundation/bin/python -m pip check` — success; no broken requirements (before and after UI install).
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp4_*.py -q` — **85 passed**.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp5_brief_editor.py foundation/tests/test_wp5_service.py foundation/tests/test_wp5_streamlit_interaction.py -q` — **44 passed**.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp5_service.py -k wp5_ir2 -vv --tb=long` — **10 passed**, 19 deselected; 8 parameter variants plus 2 lifecycle checks.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q` — **335 passed**.
- Live Chromium Streamlit acceptance, WP4 higher-resolution qualification/reopen/recompute, review evidence and regression workflow steps — success.
- WP3 compatibility: https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607599 — all four jobs success.

**Environment:** CI Python 3.12. Foundation hash-locked installation initially resolves `packaging==26.3`. Installing `streamlit==1.40.2` changes this to `packaging==24.2`; `playwright==1.56.0` is also installed for browser acceptance. The combined UI environment is **not** identical to the foundation lock. Actual `pip freeze` and `pip check` were archived. No combined lockfile is claimed.

## Raw artifacts and provenance

- **IR2 log, checkout SHA and actual combined dependency freeze:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545/artifacts/12653744082
- **Browser screenshot/dossier/log and freeze:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545/artifacts/12654498567
- **WP4 qualification dossiers, reviewer reproduction, actual checkout SHA:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545/artifacts/12654343765
- **Original R1 retained raw evidence:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545/artifacts/12653254584
- **Full raw CI log:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545 (WP4 qualification job).
- **Patch:** https://github.com/DavidOWilliams/Materials-design/commit/dd0bc5551cd630ff3ba1276564ab43f41fa4d81a

**Archive checksum:** GitHub artifacts expose server-side artifact IDs and sizes, but no verified ZIP SHA-256 was computed or claimed for these GitHub-hosted archives. The SHA-256 given above applies solely to the user-supplied independent-review ZIP.

## Independent reviewer handover

1. In a fresh isolated worktree at `4078a83dc11e14703ff6cc03f5b62f4e48879d14`, rerun the ten `-k wp5_ir2` tests and examine fresh-path no-mutation assertions.
2. Independently run the zero-budget reproduction, verify **no files or parent directory** exist, then retry the same path with a valid budget.
3. Verify journal immutability, cancellation, one-candidate reuse, numerical replay and saved-brief mismatch fail-closed.
4. Reconcile tested source SHA against actual PR merge checkout and artifact `checkout-sha.txt`.
5. Review original R1 separately as independently verified at `ccbca12...`; do not conflate that review with new IR2 acceptance.

**D1 restrictions:** Intended design and estimated achieved state remain separate; measured manufacturing evidence is unavailable/unknown, not passed. Duty-description edits are identity-propagation tests, not changed physical boundary conditions. Cancellation occurs at candidate boundaries; no asynchronous solver interruption or mid-kernel restart. D1 synthetic demonstration is not V1 physical validation. WP2/WP4 physics, accepted WP4 baselines, and numerical qualification were not modified. No PR merge or baseline movement. WP6 not started.
