"""Explicit, fail-closed WP4 transform registry.

A process route is a declared capability, not proof of a machine's performance.
Two scenarios may use the same transform implementation with different
resolutions. Registry identity is separate from numerical solver identity.
"""
from __future__ import annotations
from .wp4_resolution import transform, TRANSFORM_ID, TRANSFORM_VERSION
from .wp4_uniform import transform as uniform_transform, ID as UNIFORM_ID, VERSION as UNIFORM_VERSION, ROUTE as UNIFORM_ROUTE

REGISTRY_VERSION=1
ROUTES={"synthetic_ideal_planar_deposition":(TRANSFORM_ID,TRANSFORM_VERSION,transform),
        UNIFORM_ROUTE:(UNIFORM_ID,UNIFORM_VERSION,uniform_transform)}

def resolve(process):
    try:
        name,version,delegate=ROUTES[process.route]
    except KeyError as e:
        raise ValueError("Unregistered WP4 process capability: "+process.route) from e
    if process.status=="unresolved":
        raise ValueError("Unresolved process scenario")
    return dict(registry_version=REGISTRY_VERSION,route=process.route,
                transformer=name,transformer_version=version),delegate

def apply(design,process):
    identity,delegate=resolve(process)
    commands,state=delegate(design,process)
    if state.estimator_id!=identity["transformer"] or state.estimator_version!=identity["transformer_version"]:
        raise ValueError("Transform delegate identity mismatch")
    return identity,commands,state
