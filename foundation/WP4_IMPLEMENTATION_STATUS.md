# WP4 implementation status (not accepted)

Source baseline: accepted WP3 record 71933c733340d4b7c33777488a428bc56e34f57f (accepted implementation 790c3521f09e3f61615702de3b149c9f315e9e74).

First increment: `material_core/wp4_resolution.py` provides an isolated synthetic planar layer/feed transformer for volume-basis, one/two constituent designs. It integrates piecewise-linear gradients and discontinuous layers over process intervals, quantises feed fractions and returns separate commands and estimated geometry. Non-divisible thicknesses and unsupported routes/bases fail explicitly. Absolute command volumes are not asserted on the unit-area coupon.

**Not yet verified:** no WP4 test execution, fresh environment verification, WP2 estimated-target integration, feedback-driven revision, persistence/replay, budgeted comparisons, challenge gates or independent review. Do not claim F01-F12/C01-C12 pass. This is an untested first increment only.

**Known limitations requiring correction before acceptance:** transformer source hash is a placeholder; estimated geometry representation uses the existing IntendedDesign container; quantisation tie policy and floating tolerances require independent reference tests; command unit-area quantities need a versioned schema extension; material balances and fidelity need durable records; support for a one-layer estimated architecture requires appropriate representation; zero-length or invalid process inputs must be rejected by contracts. Existing repository interfaces and independent scientific checks must be respected.

WP4 implementation, gates 1-2 and gate 3 remain OPEN. No merge authorised.
