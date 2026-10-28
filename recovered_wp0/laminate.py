"""Reconstructed Pelz benchmark from retained report, not recovered original code.

Seven symmetric alternating ideal bonded layers; constant biaxial stiffness;
stress-free joining then 1925 K cooling. Paper convention: negative=tension.
Not total process residual stress, bending, damage, or ceramic mixer response.
"""
import json
import math
from pathlib import Path

M1, M2 = 483e9 / (1-.17), 411e9 / (1-.16)
A1, A2 = 5.5e-6, 3.0e-6


def stress(l1, l2, cooling_K=1925.):
    if not all(math.isfinite(x) and x > 0 for x in (l1, l2, cooling_K)):
        raise ValueError('Positive finite thicknesses and cooling required')
    f = 4*l1/(4*l1+3*l2)
    factor = M1*M2*(A1-A2)*cooling_K/(M1*f+M2*(1-f))
    return {'B4C_fraction': f, 'B4C_stress_Pa': -factor*(1-f), 'SiC_stress_Pa': factor*f}


def compatible_strain(l1, l2, cooling_K=1925.):
    f = 4*l1/(4*l1+3*l2)
    strain = -(f*M1*A1+(1-f)*M2*A2)*cooling_K/(f*M1+(1-f)*M2)
    # Engineering positive tension is reversed to the paper's convention.
    return (-M1*(strain+A1*cooling_K), -M2*(strain+A2*cooling_K))


def results():
    return {'status': 'reconstructed_partial_reproduction_not_physical_validation',
            'source_doi': '10.1016/j.addma.2020.101647',
            'sign_convention': 'negative tension',
            'literal_549_526_um': stress(549e-6,526e-6),
            'diagnostic_reversed_526_549_um': stress(526e-6,549e-6),
            'thickness_ratio_sweep': {str(r):stress(r,1.) for r in (1,2,4,8)},
            'surrogate_purge': {'material':'Play-Doh, not ceramic calibration',
                'equivalent_trace_length_mm': 3200/(math.pi*.6**2),
                'equivalent_travel_time_s': 3200/(math.pi*.6**2)/5,
                'six_switch_volume_cm3': 19.2}}


if __name__ == '__main__':
    path = Path(__file__).with_name('laminate_results.json')
    path.write_text(json.dumps(results(),indent=2,allow_nan=False)+'\n')
    print(path)
