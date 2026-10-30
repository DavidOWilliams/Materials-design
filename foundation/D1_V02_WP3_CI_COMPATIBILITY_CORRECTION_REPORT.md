# D1 v0.2 — WP3 CI Compatibility Correction and Verification Report

**Date:** 30 October 2026  
**Finding:** V02-IR-F01 — implementation-team disposition **CORRECTED AND RETESTED; independent reviewer formal closure pending**  
**Exact tested correction SHA:** `d9e63ea468294eba4fc25493395ad68d60edf9a5`  
**Original tested implementation:** `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c`  
**Reviewed documentation-only predecessor:** `fdf6d8407ef21706b6ab60ed020f9512bdaaa06e`  
**PR:** https://github.com/DavidOWilliams/Materials-design/pull/22 — draft, unmerged.

## A. Root cause

The historical WP3 workflow [failed run 40957223034](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223034), job `123740320489` (`wp3-contract-and-vertical`), selected the entire `foundation/tests` tree using a scientific-only pinned foundation environment. This tree included two newly added Streamlit AppTest interaction tests in `foundation/tests/test_d1_v02_ui_collision.py`, but the WP3 job did not install Streamlit. Both imported `streamlit.testing.v1` and failed with `ModuleNotFoundError`. Original regression selection: **360 passed, 2 skipped, 2 failed**, with precisely these two failures; the other three WP3 jobs were successful. This was CI test-discovery portability, not a WP3 numerical defect. The same UI tests had passed in the separately provisioned Streamlit environment.

## B. Minimal correction — Option A, isolated test scope

Exactly these two paths were changed relative to the reviewed documentation-only head:

1. `foundation/tests/test_d1_v02_ui_collision.py` moved without modification to `foundation/ui_tests/test_d1_v02_ui_collision.py`, outside broad numerical foundation discovery.
2. `.github/workflows/d1-v02-ui-verification.yml` gained an explicit step executing `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/ui_tests/test_d1_v02_ui_collision.py -v`, with output written to `/tmp/d1-v02-verification/ui-collision.log`. This job installs **Streamlit 1.40.2**.

Option A was selected rather than adding a graphical/web runtime dependency to the historical pure-science WP3 qualification environment. This preserves all three collision tests as executed UI coverage, rather than silently skipping or deleting them. The test source content is identical. The dedicated v0.2 workflow continues to execute the full scientific suite separately.

## C. Actual corrected-source CI execution

All listed Actions run head SHAs are `d9e63ea468294eba4fc25493395ad68d60edf9a5`, Python 3.12. The relevant UI dependency is Streamlit `1.40.2` (installed by dedicated D1 v0.2 workflow).

| Workflow | Actual individual job results / tests | Final |
|---|---|---|
| [WP3 — run 41047548251](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548251) | `wp3-contract-and-vertical` **SUCCESS**, 359 passed / 2 skipped in broad scientific regression; `wp3-exact-branch-head` **SUCCESS**; `wp3-legacy-regression` **SUCCESS**; `wp3-original-review-reproduction` **SUCCESS**. Subsequent numerical/scenario steps in contract/vertical job also completed. | **PASS — 4/4 jobs** |
| [D1 v0.2 — run 41047548183](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548183) | `verify` **SUCCESS**; 7 display-transform unittest passes; foundation suite **339 passed / 1 warning**; relocated Streamlit collision suite **3 passed / 1 warning**, not skipped; WP3/WP4 accepted v0.1.0 numerical comparison **identical**; 4096-element examples **passed**; actual Chromium first-user journey and handoff/cancel/recovery **passed**. | **PASS** |
| [WP4 integration — run 41047548198](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548198) | `wp4-direct-branch` **SUCCESS** including focused, recovery, browser and integration stages. | **PASS** |
| [WP7 D1 exact-head — run 41047548148](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548148) | `qualify` **SUCCESS** including Streamlit, regressions, full-resolution examples, Chromium and handoff/recovery. | **PASS** |

The WP3 numerical and Pareto tests *ran*, they were not silently marked skipped. The previous failing run remains preserved; no history was overwritten or relabelled.

## D. Preservation

Repository comparison of the corrected SHA with the reviewed documentation-only head shows **one test-file relocation and one CI workflow update only**. Compared with original tested v0.2 application SHA, additional differences comprise previously committed Markdown documentation and those same test/CI-only changes. There are **no changed `foundation/material_core` files, numerical kernels, chart functions, UI application source, immutable dossiers or baseline release tags**. The corrected D1 workflow independently reran deterministic WP3 intended-state Pareto/proposals and WP4 manufacturing feedback/numerical objective comparison against `d1-v0.1.0` and reported **identical** outputs.

## E. Evidence and exact provenance

The complete workflow and individual job logs are available from the links above. GitHub evidence artifact ZIP digests (not individual dossier hashes; per-file SHA256SUMS are contained inside uploaded archives where applicable):

| Run | Artifact ID | SHA256 of artifact ZIP |
|---|---:|---|
| D1 v0.2 `41047548183` | `12972374769` | `bc6fc216e5d6bea985d5f7017f4635b85a08bc4f98f8fad15f366d0d500053a7` |
| WP3 contract/vertical `41047548251` | `12973362050` | `cf98876ecfd23251bb5091d5499576e00bc91721d1045c286b48366cafb084ad` |
| WP3 exact-head `41047548251` | `12973122244` | `db660f76d7e125c64d99087c5c209cbb8bbc0f7a27881f175b92e2cb4ed0f6dc` |
| WP4 `41047548198` | `12973137743` | `a4ebe304ac0cb2d2d5eaf42c28b7cf051833c6f1ab9d96622490b1cb6bf570b7` |
| WP7 `41047548148` | `12973192606` | `c856863ff193cc19070313a7ec082efc4a22d95d32dd7535bcb1b21a83158ce7` |

Additional WP4 evidence archives in run `41047548198` are retained under artifact IDs `12973840012`, `12973715590`, `12972494009`. Original failing WP3 run `40957223034`, previous development run `40957223174`, and independent reviewer run `41046147946` are deliberately unmodified.

## F. Finding disposition and independent-review request

**Implementation team assessment: V02-IR-F01 corrected and verified.** The exact previously failing WP3 job is green, historical science tests execute, relocated UI collision tests execute under pinned Streamlit, full v0.2 and WP4/WP7 checks are green, and baseline numerical results are unchanged. **Formal Gate 3 closure, any final bounded D1 v0.2 acceptance, merge or release decision belongs exclusively to the independent reviewer and programme owner.**

Reviewer should check the two-path diff and exact SHA above; inspect WP3 job `wp3-contract-and-vertical` and all three sibling job conclusions; verify `3 passed` in `ui-collision.log`, scientific test counts, exact baseline comparison, artifact digests and absence of science/UI application source changes. No new product feature or independent acceptance is asserted.
