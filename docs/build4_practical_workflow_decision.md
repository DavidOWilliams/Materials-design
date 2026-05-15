# Build 4 Practical Workflow Decision

## Decision

For now, Build 4 will use the CLI/review-pack workflow as the official practical workflow.
Existing Streamlit `app.py` integration is deferred.
A separate Build 4 viewer may be considered later, but not before the CLI/review-pack workflow is stable.

## Context

- Build 4 now has application requirement fit, application limiting-factor analysis, controlled shortlist, validation plan generation, profile registry, default-profile CLI option, and review-output coverage.
- The current supported application profile is `hot_section_thermal_cycling_oxidation`.
- The current application-fit semantics are tailored to that hot-section profile.
- Adding more profiles before making assessment logic fully profile-aware could create misleading results.
- Integrating directly into `app.py` risks disturbing the preserved Build 3.1 metallic/alloy demonstrator.

## Guardrails

- Do not modify `app.py` unless explicitly approved later.
- Do not modify Build 3.1 runtime files.
- Do not add new profiles until profile-specific assessment semantics are defined and tested.
- Do not add ranking, Pareto optimisation, generated variants, certification approval, qualification approval, or final recommendation logic.
- Generated review outputs should remain untracked unless explicitly requested.

## Near-Term Workflow

1. Run Build 4 harness/exporter from CLI.
2. Use the review pack to inspect application fit, limiting factors, controlled shortlist buckets, and validation plan.
3. Treat outputs as decision-support artefacts, not final recommendations.
4. Use `--profile hot_section_thermal_cycling_oxidation` for explicit profile selection when desired.

## Future Options

- Improve review-pack readability.
- Add profile-specific assessment semantics.
- Add additional application profiles only after semantics are defined.
- Build a separate Build 4 viewer.
- Consider `app.py` integration only after explicit approval.
