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

__all__ = [
    "ObservationMap",
    "FiberSet",
    "GeneralizedKernel",
    "QuotientSpace",
    "Reconstructor",
]
