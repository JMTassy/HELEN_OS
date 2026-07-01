"""Transport Theory of Observations.

Standalone mathematical module. No HELEN, RH, or AI dependencies.

Core objects:
    ObservationMap  — R : S → L
    FiberSet        — [S]_R = { S' : R(S') = R(S) }
    GeneralizedKernel — Inv(R) = { T : R∘T = R }
    QuotientSpace   — S / ~_R
    Reconstructor   — faithfulness and injectivity checks
"""
from transport.observation import ObservationMap
from transport.fiber import FiberSet
from transport.kernel import GeneralizedKernel
from transport.quotient import QuotientSpace
from transport.reconstruction import Reconstructor
from transport.observer import ObserverClass, is_pathological
from transport.category import (
    ObservationMorphism,
    identity_morphism,
    compose,
)
from transport.bundle import ObservationBundle
from transport.factorization import Factorization, universal_factor
from transport.disintegration import FiniteDisintegration, shannon_entropy
from transport.statistical import (
    StatisticalState,
    StatisticalObservationModel,
    finite_probability_law,
    kl_divergence,
    hellinger_distance,
    total_variation_distance,
    fisher_information_1d,
)
from transport.drift import Drift, drift, guard_projection

__all__ = [
    "ObservationMap",
    "FiberSet",
    "GeneralizedKernel",
    "QuotientSpace",
    "Reconstructor",
    "ObserverClass",
    "is_pathological",
    "ObservationMorphism",
    "identity_morphism",
    "compose",
    "ObservationBundle",
    "Factorization",
    "universal_factor",
    "FiniteDisintegration",
    "shannon_entropy",
    "StatisticalState",
    "StatisticalObservationModel",
    "finite_probability_law",
    "kl_divergence",
    "hellinger_distance",
    "total_variation_distance",
    "fisher_information_1d",
    "Drift",
    "drift",
    "guard_projection",
]
