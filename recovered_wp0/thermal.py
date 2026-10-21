"""Reconstructed 2026-10-21 from the retained WP0 report.

Steady 1D Fourier conduction: prescribed synthetic spatial conductivity,
perfect interfaces, no sources or lateral loss. Not a composition mixture law.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from skfem import Basis, BilinearForm, ElementLineP1, MeshLine, asm, condense, solve
from skfem.helpers import dot, grad


@dataclass(frozen=True)
class ThermalDesign:
    architecture: str
    length_m: float
    hot_K: float
    cold_K: float
    conductivity_W_mK: tuple
    units: str

    def __post_init__(self):
        object.__setattr__(self, 'conductivity_W_mK', tuple(self.conductivity_W_mK))
        if self.architecture not in ('homogeneous', 'layered', 'graded'):
            raise ValueError('Unsupported architecture')
        if self.units != 'SI':
            raise ValueError('Explicit SI units required')
        vals = (self.length_m, self.hot_K, self.cold_K, *self.conductivity_W_mK)
        if not all(math.isfinite(x) and x > 0 for x in vals):
            raise ValueError('Finite positive dimensions, kelvin temperatures and conductivity required')
        expected = 1 if self.architecture == 'homogeneous' else 2
        if len(self.conductivity_W_mK) != expected:
            raise ValueError('Conductivity count inconsistent with architecture')

    def conductivity(self, x):
        k = self.conductivity_W_mK
        if self.architecture == 'homogeneous':
            return np.full_like(x, k[0])
        if self.architecture == 'layered':
            return np.where(x < self.length_m / 2, k[0], k[1])
        return k[0] + (k[1] - k[0]) * x / self.length_m

    def analytic_flux(self):
        k = self.conductivity_W_mK
        if self.architecture == 'homogeneous':
            resistance = self.length_m / k[0]
        elif self.architecture == 'layered':
            resistance = self.length_m / 2 * (1 / k[0] + 1 / k[1])
        elif k[0] == k[1]:
            resistance = self.length_m / k[0]
        else:
            resistance = self.length_m * math.log(k[1] / k[0]) / (k[1] - k[0])
        return (self.hot_K - self.cold_K) / resistance


def from_legacy(candidate):
    # Deliberately no inference from names, keyword scores or incomplete evidence.
    return ThermalDesign(**candidate['wp0_thermal_fixture'])


def input_hash(design, elements):
    raw = json.dumps({'design': asdict(design), 'elements': elements,
                      'solver': 'wp0r-skfem-fourier-v1'}, sort_keys=True, allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def evaluate(design, elements=128):
    if isinstance(elements, bool) or not isinstance(elements, int) or elements < 2 or elements % 2:
        raise ValueError('Even integer mesh count >=2 required; interface must align')
    mesh = MeshLine(np.linspace(0, design.length_m, elements + 1))
    basis = Basis(mesh, ElementLineP1())

    @BilinearForm
    def conduction(u, v, w):
        return design.conductivity(w.x[0]) * dot(grad(u), grad(v))

    matrix = asm(conduction, basis)
    boundary = np.array([0, elements])
    prescribed = np.zeros(elements + 1)
    prescribed[boundary] = [design.hot_K, design.cold_K]
    temperature = solve(*condense(matrix, np.zeros(elements + 1), x=prescribed, D=boundary))
    midpoints = (mesh.p[0, :-1] + mesh.p[0, 1:]) / 2
    flux = -design.conductivity(midpoints) * np.diff(temperature) / np.diff(mesh.p[0])
    q = float(np.mean(flux))
    exact = design.analytic_flux()
    return {'input_hash': input_hash(design, elements), 'elements': elements,
            'flux_W_m2': q, 'analytic_flux_W_m2': exact,
            'absolute_error_W_m2': abs(q - exact),
            'relative_error': abs(q - exact) / abs(exact) if exact else None,
            'flux_spread_W_m2': float(np.ptp(flux)),
            'temperature_K': temperature.tolist()}


def fixtures():
    return [ThermalDesign(a, .01, 400., 300., k, 'SI') for a, k in
            [('homogeneous', (2.,)), ('layered', (2., 10.)), ('graded', (2., 10.))]]


def dominates(left, right, directions):
    if not directions or set(left) != set(directions) or set(right) != set(directions):
        raise ValueError('Complete identical objective schema required')
    if any(d not in ('min', 'max') for d in directions.values()):
        raise ValueError('Unknown direction')
    if not all(math.isfinite(v) for obj in (left, right) for v in obj.values()):
        raise ValueError('Nonfinite objective')
    differences = [(left[k]-right[k])*(1 if directions[k]=='min' else -1) for k in directions]
    return all(d <= 0 for d in differences) and any(d < 0 for d in differences)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    results = {d.architecture: {'input': asdict(d), 'meshes': [evaluate(d, n) for n in (8,16,32,64,128)]}
               for d in fixtures()}
    if args.replay:
        saved = json.loads(args.output.read_text())
        for key in results:
            assert saved[key]['input'] == json.loads(json.dumps(results[key]['input']))
            for old, new in zip(saved[key]['meshes'], results[key]['meshes'], strict=True):
                assert old['input_hash'] == new['input_hash']
                np.testing.assert_allclose(old['temperature_K'], new['temperature_K'], rtol=1e-10, atol=1e-8)
                assert math.isclose(old['flux_W_m2'], new['flux_W_m2'], rel_tol=1e-10, abs_tol=1e-7)
        print('Separate-process replay passed')
    else:
        args.output.write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
        print({k: v['meshes'][-1]['flux_W_m2'] for k,v in results.items()})


if __name__ == '__main__':
    main()
