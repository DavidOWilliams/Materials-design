"""WP2 bounded 1D thermal / equibiaxial thermoelastic numerical kernel.

This is a numerical kernel, NOT a physical property-map endorsement.
The caller must supply coherent, supported *cellwise* physical fields,
including conductivity, density, biaxial modulus and expansion. It never
fills missing properties by interpolation or by fallback to intended state.

Theory: Fourier resistance and classical laminate A/B/D thermal resultants;
see NASA/TM-2001-210656 section 2.3, equations (2.35)-(2.39).
Thermal-mismatch stress is NOT manufacturing residual stress.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Literal


@dataclass(frozen=True)
class Cell:
    """Constant-property physical cell, oriented from hot face to cold face."""
    thickness_m: float
    conductivity_W_mK: float
    density_kg_m3: float
    biaxial_modulus_Pa: float  # E/(1-nu) for isotropic equibiaxial plane stress
    expansion_per_K: float


@dataclass(frozen=True)
class BoundedResult:
    areal_mass_kg_m2: float
    hot_to_cold_flux_W_m2: float  # Signed, positive if hot face hotter
    transmitted_flux_magnitude_W_m2: float
    tensile_mismatch_Pa: float
    coordinates_m: tuple[float, ...]
    temperature_K: tuple[float, ...]
    signed_equibiaxial_stress_Pa: tuple[float, ...]
    midplane_strain: float
    curvature_per_m: float
    force_residual_N_m: float
    moment_residual_N: float
    limitations: tuple[str, ...]


def evaluate_cells(cells: tuple[Cell, ...], hot_K: float, cold_K: float,
                   stress_free_K: float,
                   restraint: Literal['free','flat_restrained']='free') -> BoundedResult:
    """Evaluate thin planar coupons with perfect interfaces and no body sources.

    Uses exact series resistance for piecewise constant conductivity.
    The cellwise stress is evaluated at centres; jump discontinuities are not
    averaged across interfaces. The free case admits axial strain and bending
    curvature by balancing force and moment, using an A/B/D reduction.
    """
    if not cells:
        raise ValueError("At least one physical cell is required")
    if any(not isfinite(v) or v<=0 for v in (hot_K,cold_K,stress_free_K)):
        raise ValueError("Temperature must be positive finite Kelvin")
    if restraint not in ('free','flat_restrained'):
        raise ValueError("Unsupported mechanical restraint")
    for c in cells:
        if any(not isfinite(v) for v in vars(c).values()):
            raise ValueError("Nonfinite cell property")
        if min(c.thickness_m,c.conductivity_W_mK,c.density_kg_m3,c.biaxial_modulus_Pa)<=0:
            raise ValueError("Nonpositive geometry or property")
        if abs(c.expansion_per_K)>1e-2:
            raise ValueError("Expansion outside bounded small-strain input guard")
    total=sum(c.thickness_m for c in cells)
    resistances=[c.thickness_m/c.conductivity_W_mK for c in cells]
    flux=(hot_K-cold_K)/sum(resistances)
    z_edges=[0.]
    t_edges=[hot_K]
    for c,r in zip(cells,resistances):
        z_edges.append(z_edges[-1]+c.thickness_m)
        t_edges.append(t_edges[-1]-flux*r)
    # Explicitly preserve signed flux and require positive magnitude for objective.
    zmid=[(a+b)/2-total/2 for a,b in zip(z_edges,z_edges[1:])]
    tmid=[(a+b)/2 for a,b in zip(t_edges,t_edges[1:])]
    stiffness=[c.biaxial_modulus_Pa*c.thickness_m for c in cells]
    eigen=[c.expansion_per_K*(T-stress_free_K)
           for c,T in zip(cells,tmid)]
    A=sum(stiffness)
    B=sum(q*z for q,z in zip(stiffness,zmid))
    D=sum(c.biaxial_modulus_Pa*(c.thickness_m*z*z+c.thickness_m**3/12)
          for c,z in zip(cells,zmid))
    NT=sum(q*e for q,e in zip(stiffness,eigen))
    # T(z) is exactly linear inside each constant-k cell. The eigenstrain
    # moment therefore includes Q*alpha*T'(z)*h**3/12 in addition to
    # its centroid contribution. Omitting this term creates spurious
    # homogeneous free-plate stress and incorrect curvature.
    thermal_slopes=[(tb-ta)/c.thickness_m for c,ta,tb in
                    zip(cells,t_edges,t_edges[1:])]
    MT=sum(q*e*z + c.biaxial_modulus_Pa*c.expansion_per_K*slope*c.thickness_m**3/12
           for q,e,z,c,slope in zip(stiffness,eigen,zmid,cells,thermal_slopes))
    if restraint=='free':
        denominator=A*D-B*B
        if denominator<=0 or not isfinite(denominator):
            raise ValueError("Ill-conditioned laminate stiffness")
        strain=(NT*D-B*MT)/denominator
        curvature=(A*MT-B*NT)/denominator
    else:
        strain=curvature=0.
    stresses=tuple(c.biaxial_modulus_Pa*(strain+curvature*z-e)
                   for c,z,e in zip(cells,zmid,eigen))
    force=sum(q*(strain+curvature*z-e)
              for q,z,e in zip(stiffness,zmid,eigen))
    moment=sum(q*(strain+curvature*z-e)*z
               for q,z,e in zip(stiffness,zmid,eigen))
    moment+=sum(c.biaxial_modulus_Pa*c.thickness_m**3/12*
                (curvature-c.expansion_per_K*slope)
                for c,slope in zip(cells,thermal_slopes))
    return BoundedResult(
        areal_mass_kg_m2=sum(c.density_kg_m3*c.thickness_m for c in cells),
        hot_to_cold_flux_W_m2=flux,
        transmitted_flux_magnitude_W_m2=abs(flux),
        tensile_mismatch_Pa=max(0.,*stresses),
        coordinates_m=tuple(zmid),
        temperature_K=tuple(tmid),
        signed_equibiaxial_stress_Pa=stresses,
        midplane_strain=strain,curvature_per_m=curvature,
        force_residual_N_m=force,moment_residual_N=moment,
        limitations=(
            "Cellwise constant properties; thin equibiaxial plane-stress plate.",
            "Perfect bonding and contact; no interface fracture or edge effects.",
            "Elastic, small-strain response from a prescribed stress-free state.",
            "Centroid stress maximum: not a layer-interface stress peak.",
            "Exact linear within-cell thermal force/moment; sampled stress at cell centres.",
            "No drying, sintering, creep, relaxation, cracking or total residual stress.",
            "No property mapping or ceramic validation provided by this numerical kernel.",
        ),
    )
