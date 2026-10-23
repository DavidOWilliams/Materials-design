# WP1 architecture and extension review

WP1 establishes a validated, persistent foundation for a material-system design
loop. It does not implement inverse search, a manufacturing transformation,
coating physics, mechanics or measured ceramic validation. The enduring goal is
still general-purpose material-system discovery and optimisation; the executable
case is deliberately a planar thermal verification fixture.

This review uses the supplied Vision v3.0 (13 October 2026), Product Definition
v1.0 (14 October 2026), current WP1 instructions, Implementation Plan v2, the
recovered scientific reports and the implemented contracts/thermal adapter.
Source hashes are recorded in the completion evidence. Walkthroughs below are
architectural assessments, not demonstrations that future solvers run.

## Boundaries in the implemented foundation

`material_core/contracts.py` contains immutable, validated JSON contracts.
Composition preserves volume, mass or atomic basis; no conversion is inferred.
Material properties retain conditions, conventions, uncertainty and provenance.
Homogeneous composition, discrete layers and continuous piecewise-linear
composition gradients are distinct tagged architectures. Gradient control knots
are design parameters; `Discretisation` is a separate numerical setting.

There is no fixed maximum of two constituents, three objectives, eleven layers
or one named ceramic pair in these representations. The v1 coordinate model is
explicitly **one-dimensional planar normalized thickness**. It is not a generic
3D geometry language. Variable-length collections do not imply that every
represented design can be evaluated.

`thermal.py` is a replaceable adapter to the unchanged recovered Fourier fixture.
It supports homogeneous prescribed conductivity, exactly two equal discrete
layers with perfect interfaces, and a two-endpoint linear conductivity gradient.
It rejects other represented architectures as unsupported. It accepts only the
intended-state evaluation target; estimated or measured states cannot silently
fall back to the intended geometry. Conductivity is prescribed synthetic input,
not calculated from composition or from material names. The supported objective
is signed thermal transmission in W/m2. Missing mass/stress evaluations remain
unsupported; the complete D1 objective set is not implied.

`CandidateGenerator`, `ManufacturingTransformer` and `PerformanceEvaluator`
protocols establish the replacement boundaries. Their existence does not mean a
search generator or manufacturing transformer has been implemented. Evaluator
identity is carried in `RunInputs.solver` and in the result, including source and
dependency identity. Candidate generator and transformer protocols carry ID and
version; concrete implementations and qualification remain later work.

Design intent, commands, process scenario, estimated achieved state, measured
achieved state and evaluation are separately tagged objects. An estimated
state's optional geometry reuses `IntendedDesign` as a shape/composition payload;
its enclosing `estimated_achieved_state` tag and lineage retain its estimated
meaning. Callers must never export that nested geometry alone and call it a
measured design. A future shared geometry payload is preferable when multiple
achieved-state evaluators are introduced.

The run store writes canonical, hash-addressed JSON artifacts and SQLite run
metadata. It validates input/result identity, preserves parent runs and terminal
failures/incomplete results, and checks artifact integrity on reopening. This
is a local prototype store, not a managed multi-user execution platform. Neither
an immutable snapshot nor a valid checksum establishes physical validity.

## Future case one coating and substrate

Consider an insulating coating on a structural substrate, with a possible bond
layer, compared against an uncoated reference under the same service duty. This
case tests whether architecture and interface semantics can expand without
turning the recovered equal-layer fixture into an unjustified coating solver.

The material records, source provenance, composition basis, assumption versions,
objective directions/units, decision records and design lineage can be reused.
The existing layered representation could retain an ordered planar composition
stack for inspection. It cannot by itself express which region is the substrate,
which is a bond coat, where interface laws apply, or how repair/recoating changes
the system. Relabelling arbitrary layers as a qualified coating system would
lose consequential information.

Add a tagged coating/substrate architecture with explicit region roles,
thicknesses, orientation and interface identifiers. Add typed interface data
for the selected supported calculation: for example thermal contact resistance
and its source conditions. Define boundaries and the substrate restraint using
an applicable existing formulation. Permit perfect interfaces only as an
explicit idealisation. Do not infer adhesion or spallation resistance from
thermal conductivity or a successful conduction solve.

The first qualified evaluator could calculate thermal transmission through the
specified stack, while a separately qualified mechanics evaluator could assess
a defined tensile or interfacial mismatch quantity. Each must declare its
supported geometry, material-property mapping and required interface evidence.
Neither evaluator exists in WP1. A coating/substrate input must currently be
rejected rather than routed through the two equal-layer thermal fixture.

The workflow would retain a baseline, propose a coating thickness or constituent
change, evaluate it, optionally transform it through a deposition scenario, and
reevaluate the appropriate achieved state. A missing bond property or unknown
achieved thickness would leave that requested assessment unresolved. A thermal
benefit alone would not establish a preferred architecture; common mass and
mechanical requirements still apply.

Migration: introduce the new architecture/settings variants under a new payload
schema, retaining v1 readers. Store old JSON bytes and hashes unchanged. New
coating evaluations get new input identities. Existing thermal runs remain
readable as thermal fixtures and are never retroactively labelled coatings.
The SQLite artifact-addressing and lineage approach can be reused; version-aware
payload dispatch must be added before mixed-version storage is supported.

## Future case two process energy and an alternative route

Consider the same planar design manufactured by two declared routes, comparing
process energy in joules per specified coupon as an additional objective. This
case tests a different performance quantity and a route that need not use
layer/feed-resolution controls. It is a software extension example, not a claim
that either route has a qualified energy model or available evidence.

The objective contract already carries arbitrary IDs, directions, applicability
and supported units; `energy`/`J` is in the unit registry. No three-objective
limit needs removal. Material/provenance records, assumptions, immutable runs,
results by objective ID, decision history and common-brief comparison checks
can be reused. A different route name is representable today, but a name and
nullable resolution fields do not implement its physics.

Add a typed route-specific scenario/settings variant for the chosen existing
energy calculation, with a defined functional unit, time history, relevant
process stages and material/waste accounting. Add missing dimensions explicitly
if the method needs them, such as power; do not place unvalidated numbers in
free-text descriptions. Inputs must be evidenced measurements or conspicuous
scenario assumptions. Unknown machine consumption, yield or process duration
cannot be replaced by zero. Joules per coupon is not a full lifecycle climate
impact: carbon factors, service life and system boundaries would require
separate evidence and contracts.

A versioned manufacturing adapter would return an estimated state only for the
transformations its supported method actually predicts. If the energy method
predicts no geometry or composition change, it must not invent shrinkage or
porosity. It may return energy plus unresolved achieved-state fields. A later
material proposal could choose a different design in response to a binding
energy or material budget, but the generator/search loop remains outside WP1.

Current restriction: `RunInputs.settings` accepts `ThermalSettings`, so a new
energy evaluator needs a discriminated settings union and a new schema reader.
For this thermal coupon case the existing brief's thermal fields retain their
meaning. A wholly nonthermal service problem additionally needs a typed brief
variant; dummy hot/cold temperatures are not an acceptable workaround. The
`Evaluation` metrics can describe the new objective, while a general field
payload should replace adding further solver-specific top-level arrays.

Migration: retain existing thermal settings, brief and result readers; add
route-specific contracts under a new schema version and version-aware store
loading. The content-hash rule continues to cover route, method, assumptions,
evidence and settings. A route change creates a new evaluation identity and
retains the earlier run; it never edits the historical snapshot.

## Extension map

| Current capability | Deliberate limitation | Extension mechanism | Migration needed |
|---|---|---|---|
| Variable-length constituent fractions with explicit basis | No implicit mass/volume/atomic conversion; no mixture physics | Qualified mapping adapter and evidence for conversion | New mapping settings/version; retain original basis and sources |
| Homogeneous, layered and piecewise-linear gradient design | One planar coordinate; no coating roles or 2D/3D geometry | New tagged architecture/geometry contracts with coordinate transforms | New schema variant and retained v1 reader |
| Separate mesh settings | Linear finite elements; recovered adapter requires even mesh | Solver-specific discretisation settings | New settings variant; new evaluation hash |
| Generic objective IDs, directions, supported units and applicability | Closed unit registry; only thermal transmission evaluated | Add reviewed dimensions and qualified evaluator | New schema/support version; existing objective meanings unchanged |
| Property conditions, conventions and provenance | Conditions partly textual; no property functions or tensor fields | Typed property-function/domain variants and applicability validation | New property schema; retain original measurement records |
| Process scenario plus commands | Layer/feed resolution fields only; no transform implemented | Route-specific settings and qualified manufacturing adapter | New process/settings variant; no reinterpretation of existing scenarios |
| Distinct estimated/measured state tags | Sparse observations; no measured spatial-field evaluator | Typed spatial observations, specimen joins and stage transforms | New state payload version; old unknowns remain unknown |
| RunInputs and Evaluation snapshots | Thermal settings and thermal field arrays embedded in v1 | Typed domain/settings/field unions; common run envelope | Version-aware readers required; do not rewrite old artifact bytes |
| Assumption snapshots and deterministic content hashes | Changes may conservatively invalidate more than strictly necessary | Explicit dependency subsets only after sound dependency tracking | New key-version policy if semantics change; retain old identities |
| SQLite metadata and JSON artifacts | Local single-operator prototype; no worker scheduler or multi-user controls | Add execution states/worker boundary, later database/object-store adapters | Explicit database migration; backup/restore and old-run readability tests |
| Generator/transformer/evaluator protocols | No inverse loop or process execution in WP1 | Implement qualified adapters behind these boundaries | Version concrete adapters and saved requests |
| Decision and provenance history | Not independent scientific acceptance or authenticity proof | Reviewer workflow, source rights checks, supported evidence ingestion | Add review records without altering original results |

## Evolution rules and costly choices

V1 is a deliberately concrete schema. The implementation currently rejects
unknown schema versions and unexpected fields. It does **not yet implement**
mixed-version dispatch or automated migrations. Before the first new domain,
move the v1 decoder into a retained version namespace and dispatch using the
payload schema version. Preserve exact old artifacts and their content hashes.
A migrated interpretation must be a new artifact with explicit lineage to its
source; no in-place rewrite of a historical accepted run is permitted.

SQLite metadata has its own version. Payload evolution and database evolution
are separate: a new domain may reuse existing metadata fields, but the loader
still needs schema dispatch. Any database migration must be transactional,
backed up and tested against stored v1 runs. A future reader should open v1
snapshots with the retained v1 contract. Re-execution additionally requires the
old numerical source/settings/environment or an explicit new evaluation; mere
readability does not guarantee replay with a replacement solver.

Three decisions would become expensive if allowed to spread. First, mandatory
thermal boundaries in every brief must not become requirements of a nonthermal
application. Second, the normalized-thickness geometry must not be stretched
into an undocumented 3D coordinate convention. Third, each new solver must not
add private fields directly to the common result object. Introduce typed domain
variants at the first extension, before UI/search code proliferates around the
v1 shapes. This is a contained migration cost today, not a justification for
building a speculative universal platform in WP1.

Other boundaries should be retained: never infer properties from legacy keyword
scores; never collapse estimated and measured state identity; never silently
renormalise changed manufacturing material budgets; never convert unknowns to
zero or successful feasibility. Keep adapter applicability narrower than the
representational schema whenever scientific support is narrower.

## Authority conflicts and scientific distinctions

The current WP1 instructions and Implementation Plan v2 govern delivery. The
older product's 8–12 week schedule, early scientific-review dependency and
heavier MOOSE/OpenFOAM environment proposal do not override the later bounded,
CPU-first D1 path. D1 functional demonstration and V1 measured validation remain
separate. WP1 does not complete either milestone.

The historical Build 4 and Phase 5 documents describe hot-section-only flows,
no arbitrary generated gradients, no live specialist calls and no integration
into the legacy app. They remain useful descriptions of those legacy phases;
they do not prohibit the later authorised numerical core. Their useful
principles—baseline preservation, visible trade-offs and no qualification
claims—remain applicable. The requested
`docs/phase6_to_full_optimisation_thin_slice_roadmap.md` is zero bytes in the
verified recovery tree, so no contents are inferred from its filename.

The product references Pelz's 2024 work, while the recovered laminate benchmark
explicitly reproduces the separate 2021 active-mixing paper,
DOI `10.1016/j.addma.2020.101647`. The vision mentions both. These are distinct
references, not interchangeable benchmark provenance. The recovered benchmark
retains literal and reversed thickness assignments; matching the reported
rounding after reversal does not prove the source assignment should be changed.

The CODE alumina/zirconia records are a different case from Pelz B4C–SiC. They
retain atomic-versus-command-volume basis, missing specimen-linked geometry,
porosity and uncertainty, failed specimens and unequal composition budgets.
The retained `paired_group_differences_deg` is index subtraction, not evidence
of a paired experimental design. Neither record supplies complete achieved-state
validation. No new mechanism, calibration, author communication or scientific
acceptance is created by this architecture review.
