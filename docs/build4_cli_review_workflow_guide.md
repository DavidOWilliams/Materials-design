# Build 4 CLI and Review-Pack Workflow Guide

## 1. Purpose

Build 4 currently uses a CLI/review-pack workflow for deterministic inspection of the ceramics-first material-system slice. It is not integrated into the Streamlit `app.py` runtime at this stage.

Use the CLI tools to generate local review artifacts, then inspect the review pack for application fit, limiting factors, controlled shortlist buckets, and validation planning. Build 3.1 `app.py` integration remains deferred.

## 2. Current supported profile

The current supported application profile is:

```text
hot_section_thermal_cycling_oxidation
```

The default CLI behavior resolves to this profile. Passing it explicitly is recommended when documenting or reproducing a review run.

## 3. Recommended commands

Run the full test suite before changes:

```bash
pytest
```

Run the Build 4 ceramics-first harness with its default output directory, `outputs/`:

```bash
python tools/build4_ceramics_first_harness.py
```

Run the Build 4 ceramics-first harness with the supported profile selected explicitly:

```bash
python tools/build4_ceramics_first_harness.py --profile hot_section_thermal_cycling_oxidation
```

Optionally choose a review output directory for harness artifacts:

```bash
python tools/build4_ceramics_first_harness.py --output-dir outputs/build4_ceramics_first
```

Run the Build 4 review pack exporter with its default output directory, `outputs/build4_review_pack/`:

```bash
python tools/build4_review_pack_exporter.py
```

Run the Build 4 review pack exporter with the supported profile selected explicitly:

```bash
python tools/build4_review_pack_exporter.py --profile hot_section_thermal_cycling_oxidation
```

Optionally choose a review pack directory and clean old files inside that directory first:

```bash
python tools/build4_review_pack_exporter.py --output-dir outputs/build4_review_pack --clean
```

Run the full test suite after changes:

```bash
pytest
```

## 4. What the review pack contains

The review pack should include package-level and candidate-level Build 4 review data, including:

- `application_profile`
- `application_requirement_fit_summary`
- `application_limiting_factor_summary`
- `controlled_shortlist_summary`
- `validation_plan_summary`
- candidate-level `application_requirement_fit`
- candidate-level `application_limiting_factor_analysis`

The exporter also writes a review-pack index, summary JSON, package JSON, view-model JSON, full markdown report, and split markdown sections under the selected output directory.

## 5. How to interpret the outputs

Application requirement fit describes how each candidate maps to the supported hot-section thermal-cycling and oxidation profile. Treat it as structured fit evidence for review, not as a scorecard that selects a winner.

Application limiting factors identify profile-specific concerns that constrain candidate use, such as architecture path issues, evidence gaps, lifecycle burdens, coating or gradient concerns, and other application-facing risks.

Controlled shortlist buckets group candidates into review-oriented categories such as near-term comparison references, validation-needed options, exploratory context, research-only context, poor-fit-for-profile candidates, and insufficient-information cases. These buckets support discussion and triage; they are not rankings.

Validation plan categories summarize the kinds of follow-up validation work implied by the candidate set and profile, such as baseline reference validation, validation required before engineering use, exploratory validation only, research validation only, parked/no validation for this profile, and insufficient-information follow-up. They help frame next evidence needs and do not grant qualification or certification approval.

## 6. Important boundaries

Build 4 CLI/review-pack outputs are:

- not a ranking
- not a final recommendation
- not Pareto optimisation
- not generated candidate variants
- not qualification approval
- not certification approval
- no live model calls
- Build 3.1 `app.py` integration is deferred

## 7. Git hygiene

Generated review outputs should normally remain untracked. Do not commit `outputs/` unless explicitly requested.

Do not commit `__pycache__` directories or `.pyc` files.

Before committing, run:

```bash
git status --short --untracked-files=all
```

Confirm that the intended documentation change is the only tracked change unless the commit scope explicitly says otherwise.

## 8. Next likely workflow improvements

Likely future workflow improvements include:

- additional application profiles only after profile-specific semantics are defined
- a separate Build 4 viewer
- `app.py` integration only after explicit approval
