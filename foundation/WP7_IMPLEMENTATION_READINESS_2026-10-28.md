# WP7 implementation readiness assessment — 28 October 2026

Starting source: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`; inspected against original WP5 interface, WP5 service, WP4 persistence and WP6 evaluator. Draft governance PR #12 at `6fdfce29c29f5b4ad26b974315adb0d4cd000c9f` remains separate; no source-of-truth documents replaced.

| User journey | Status at accepted baseline | WP7 minimum intervention |
|---|---|---|
| Setup/start | Implemented but needs fresh D1 clean-install qualification | Reuse `foundation/setup.sh`; add D1 instructions |
| Define/load representative brief | Already working within bounded fixture; scientifically arbitrary brief edits unsupported | Visible built-in fixture and selected mass scenario |
| Generate candidate designs | WP4 sequential gradient revision already working and verified as part of prior integration; full WP3 multi-architecture generator not integrated into WP5 | Expose WP4 as truthful bounded example; three-architecture D1 acceptance item still open |
| Evaluate numerically | Already working and verified in WP6 integration | Reuse unchanged WP4/WP2 |
| Feasibility/constraints | Already present in records, hard to interpret | Read-only explanations |
| Trade-offs/Pareto | WP3 strict routine exists but WP5 did not display Pareto | Read-only strict Pareto computed from WP4 recorded results |
| Select/inspect design | Inspect returned raw dossier, not guided | Candidate selection and provenance details |
| Save dossier | Already working; immutable and integrity checked | Guided save/download |
| Restart/restore | Already working service; UI lacked guided demonstration | Restore and recompute controls |
| Understand scientific limits | WP5 warning, historical governance | Persistent D1 warnings and explicit omissions |

**Minimality:** WP7 only adds `wp7_view.py`, `wp7_app.py`, tests and documentation. No numerical, scientific, process-mapping or WP4 feasibility formulas changed. Pareto uses existing WP3 strict routine and the WP4 `feasible` flag. An eligible record is only *conditionally* scenario feasible; never measured validation.

**Important residual acceptance gap:** The original Implementation Plan v2 requires three architecture classes including a homogeneous reference and at least one beyond-initial-list generated design. The WP4 campaign shown by WP7 is a gradient-only sequential design demonstration. Historical WP2 homogeneous/layered numerical verification does not by itself prove the integrated WP7 application can edit, generate and compare those classes. Do NOT mark WP7 complete until this checklist item is implemented and verified or explicitly dispositioned by an independent reviewer. Likewise no physical achieved-state data or generalised search superiority.
