"""Re-evaluate observed CODE designs; never substitute missing achieved fields."""
import json
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).parent
d = json.loads((ROOT/'ceramic_evidence.json').read_text())
out = {'source_id': d['source']['id'], 'designs': {}}
for design in d['designs']:
    commands=design['commanded_zirconia_volume_fraction_by_layer']
    angles=design['curling_angle_deg']
    assert len(commands)==11 and all(0 <= x <= 1 for x in commands)
    changes=sum(a!=b for a,b in zip(commands,commands[1:]))
    measured=[a for a in angles if a is not None]
    complete=len(measured)==len(angles)
    out['designs'][design['id']]={
        'mean_curling_deg':mean(measured) if complete else None,
        'sample_sd_deg':stdev(measured) if complete else None,
        'observed_angles_deg':angles,
        'composition_changes':changes,
        'calculated_purge_ml':changes*d['process']['purge_per_composition_change_ml'],
        'nominal_equal_layer_mean_zirconia_fraction':mean(commands),
        'failure_status':design['failure_status'],
    }
a=out['designs']['type1']; b=out['designs']['type2']
out['comparison']={
    'scope':'Retrospective observed outcome comparison, not predictive physical model validation',
    'curling_mean_reduction_percent':100*(1-a['mean_curling_deg']/b['mean_curling_deg']),
    'purge_increase_ml':a['calculated_purge_ml']-b['calculated_purge_ml'],
    'paired_group_differences_deg':[y-x for x,y in zip(a['observed_angles_deg'],b['observed_angles_deg'])],
    'composition_budget_equal':False,
}
c=d['type1_composition']
out['rounded_label_composition_check']={
    'mean_absolute_difference_pp':mean(abs(a-b) for a,b in zip(c['nominal_Al_atomic_percent'],c['measured_Al_atomic_percent'])),
    'maximum_absolute_difference_pp':max(abs(a-b) for a,b in zip(c['nominal_Al_atomic_percent'],c['measured_Al_atomic_percent'])),
    'interpretation':'Descriptive check of rounded labels, not a measurement uncertainty estimate'
}
missing=[k for k in ('actual_gcode','timestamped_feed_rates','measured_extruded_volume_log','per_layer_achieved_geometry','specimen_specific_porosity') if d['process'][k] is None]
out['milestone_gate']={'passed':False,'missing_fields':missing,'additional_blockers':['measurement uncertainty','specimen-level joining of commands and all achieved fields','held-out predictive validation','original B4C-SiC revised specimen measurements']}
assert out['designs']['type3']['mean_curling_deg'] is None  # failures cannot disappear from ranking
assert a['calculated_purge_ml']==5 and b['calculated_purge_ml']==2.5
assert all(x>0 for x in out['comparison']['paired_group_differences_deg'])
assert not out['milestone_gate']['passed']
(ROOT/'ceramic_evaluation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
