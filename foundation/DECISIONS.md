# WP1 decisions and contradiction log

Recorded 22–23 October 2026. Scope authority: the supplied consolidated WP1
instructions, then Vision v3 for enduring direction, Implementation Plan v2 for
delivery, and verified recovery evidence for existing implementation/science.

| ID | Issue | Decision and consequence |
|---|---|---|
| D01 | Implementation plan says recovery is outstanding; recovery report says publication needs approval | Both statements are stale. Verified recovery branch and commit `2655d64f2d5a02dfeaf2a3c4c1e553cda218a89f` exist. Start there, preserve main and recovery, publish a separate WP1 branch. |
| D02 | Product v1 uses earlier 8–12 week plan and early scientific gates | Current D1 delivery plan supersedes that sequence. WP1 builds foundations; measured V1 remains separate and unresolved. No expert contact is required before D1. |
| D03 | Legacy phase guardrails prohibit some new numerical work | Treat them as historical constraints on the existing route. Isolate the new core in `foundation/`; do not reinterpret legacy keyword scores as physical objectives. |
| D04 | Requested phase 6 roadmap file is empty | Record its zero-byte state; do not infer a roadmap from the filename. The current implementation plan governs sequencing. |
| D05 | Product mentions heavy solver environments | Use existing recovered Fourier calculation for WP1 with a minimal Python 3.12 hash lock. MOOSE/OpenFOAM, GPU and external LLM services are not WP1 dependencies. |
| D06 | Thermal fixtures could be mistaken for ceramic property laws | Preserve prescribed synthetic conductivity as explicit settings/provenance. Constituent composition does not imply a verified mixture law. Unsupported objectives/targets remain unresolved. |
| D07 | Flexible schemas could imply unimplemented physics | Permit variable-length constituents/layers/objectives but declare v1 planar geometry and the narrower thermal fixture domain. Document typed extensions and schema migration in ARCHITECTURE.md. |
| D08 | Unknown measurements could become favourable defaults | Require explicit missing reasons; keep estimated and measured identities distinct. No automatic zero porosity, perfect fidelity or demonstrated feasibility. |
| D09 | Assumption edits could silently alter old runs | Preserve exact A01–A15 text, append versions and hash full snapshots. Changed records miss old cache keys; old runs retain original evidence. |
| D10 | Persistent inputs and failure recovery | SQLite metadata plus immutable content-addressed JSON. Revalidate at boundaries, atomically install artifacts before metadata, retain interrupted/failed/incomplete executions and immutable decisions. |
| D11 | Pelz references differ between documents | The recovered laminate benchmark is the 2021 active-mixing paper, DOI `10.1016/j.addma.2020.101647`. Do not substitute the separately mentioned 2024 paper or silently reverse its thickness assignments. |
| D12 | CODE data might be conflated with Pelz validation | Keep distinct material systems and source bases. Atomic EDS values are not volume fractions; group subtraction is not a paired study. Neither closes achieved-state validation. |
| D13 | Broad product scope could overexpand WP1 | Implement no inverse search, manufacturing physics, mechanics solver or full UI here. Preserve replaceable boundaries and describe the concrete WP2 integration path. |
| D14 | Another domain could require dummy thermal fields | Do not use dummy fields. Introduce typed brief/settings/result variants at the first extension, retain v1 decoders, and preserve old artifact bytes/hashes. Current limitations are explicit, not a permanent product boundary. |

The two architectural walkthroughs were reviewed before this contract revision
was finalized. No decision narrows the enduring discovery/inverse-design vision.
Later scientific review must resolve assumptions using evidence; software
verification and agent review do not provide that acceptance.
