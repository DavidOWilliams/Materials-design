"""Presentation regression checks: no physics, search or eligibility changes."""
from __future__ import annotations
import unittest
from d1_visuals import _rows, _value, _valid, _pareto_ids, _estimated_design

def comp(a):
    return {"basis":"volume","fractions":[
        {"material_id":"scenario_A","fraction":a},
        {"material_id":"scenario_B","fraction":1-a}]}

class DisplayTransformTests(unittest.TestCase):
    def test_wp3_wp4_metric_names_not_conflated(self):
        wp3={"candidate":1,"thermal_transmission_W_m2":3.5,"qualified_for_numerical_pareto":True}
        wp4={"candidate":1,"thermal_transmission":2.4,"eligible":False}
        self.assertEqual(_value(wp3,"thermal_transmission","WP3"),3.5)
        self.assertEqual(_value(wp4,"thermal_transmission","WP4"),2.4)
        self.assertIsNone(_value(wp3,"thermal_transmission","WP4"))
        self.assertTrue(_valid(wp3,"WP3"))
        self.assertFalse(_valid(wp4,"WP4"))

    def test_gradient_only_original_knots(self):
        design={"architecture":{"kind":"gradient","interpolation":"piecewise_linear",
            "knots":[{"position":0.0,"composition":comp(.25)},
                     {"position":.35,"composition":comp(.40)},
                     {"position":1.0,"composition":comp(.05)}]}}
        kind, rows, entries=_rows(design)
        self.assertEqual(kind,"gradient")
        self.assertEqual([p for p,_ in entries],[0,.35,1])
        self.assertEqual(len(rows),6)
        self.assertEqual(rows[2]["fraction"],.4)

    def test_layered_steps_not_smoothed(self):
        design={"architecture":{"kind":"layered","layers":[
            {"start":0.0,"end":.4,"composition":comp(.8)},
            {"start":.4,"end":1.0,"composition":comp(.2)}]}}
        kind,rows,entries=_rows(design)
        self.assertEqual(kind,"layered")
        self.assertEqual([x[0] for x in entries],[0,.4,1])
        self.assertEqual(rows[2]["fraction"],.2)

    def test_no_manufacturing_geometry_no_fake_profile(self):
        self.assertIsNone(_estimated_design({"estimated_inputs":{"estimated_state":{"geometry":None}}}))
        self.assertIsNone(_estimated_design({"estimated_inputs":{}}))

    def test_pareto_source_only(self):
        self.assertEqual(_pareto_ids({"pareto_ids":["2"]}),{"2"})
        self.assertEqual(_pareto_ids(None),set())

if __name__=="__main__":
    unittest.main()
