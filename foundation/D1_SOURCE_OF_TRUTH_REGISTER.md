# D1 authoritative source register (provisional)

Date: 2026-10-27. Source identity is distinct from documentation acceptance, repository integration, and D1 release.

| Package | Tested source | Acceptance record | Documentation-only SHA | Integration status |
|---|---|---|---|---|
| WP1 | pending exact SHA audit | prior bounded acceptance (user-authorised premise) | pending | ancestor verification pending |
| WP2 | pending exact SHA audit | prior bounded acceptance | pending | ancestor verification pending |
| WP3 | pending exact SHA audit | prior bounded acceptance | pending | ancestor verification pending |
| WP4 | beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b | foundation/WP4_ACCEPTANCE_LEDGER.md | 1805811acdafacd66ba3574e8cb45c59bebdd8e5; preservation bb67e51029c5479361c59cea0b73b6bb722826f1 | tested source ancestor of WP6 (GitHub compare) |
| WP5 | 4078a83dc11e14703ff6cc03f5b62f4e48879d14 | foundation/WP5_INDEPENDENT_ACCEPTANCE.md | 5ade1e9650795427a8bb32de64dfce6c11cd0426 | tested source ancestor of WP6 (GitHub compare) |
| WP6 | 1f89c2d1bf64b669ca98b81f4305d20d08104e5c | foundation/WP6_INDEPENDENT_ACCEPTANCE.md (location supplied; not yet independently retrieved) | pending | D1 source starting point; not merged to main |
| P1 | 6eb62daec638185f5c5dc170182e9e0454b6e061; corrected 752752f880ed7c4b0c77d399ca7c99f9a9bb094e | Gate 3 pending | separate PR #10 | excluded from D1 |

Evidence and manifests: WP5 foundation/evidence/wp5-ir2-independent/SHA256SUMS.json; WP4 preservation branch wp4-evidence-archive-2026-10-26; WP6 exact evidence manifest to inventory. Dependencies: WP1 -> WP2 -> WP3 -> WP4 -> WP5 -> WP6. Outstanding limitations: D1 synthetic demonstration only; no measured ceramic V1 validation; independent WP7 review not performed. All pending fields must be resolved before release.
