"""Executable witness for THEOREM_PHI_CONTRACTION_FLOOR_V1.

Verifies, with stdlib arithmetic only (independent of the torch scaffold in
helen_os/render/math_to_face.py), that the zero-noise phi-drift flow

    z' = -phi^(-t) (I - Pi) z

has a strictly positive memory floor — it does NOT contract to zero — and
that the constants stated in the theorem document are exact.

NON_SOVEREIGN. authority=false. Witness class: artifact receipt (executed test).
"""

import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LN_PHI = math.log(PHI)

# Constants asserted in THEOREM_PHI_CONTRACTION_FLOOR_V1.md §3
TOTAL_MASS_STATED = 2.078086921235          # 1/ln(phi)
C_PHI_STATED = 0.125169442295               # e^(-1/ln phi), continuous floor
C_DISC_T5_STATED = 0.136252952251           # Euler product, T=5, dt=0.1
C_DISC_INF_STATED = 0.112408840028          # Euler product limit, dt=0.1
C_CONT_T5_STATED = 0.150965198772           # continuous factor at T=5


def _euler_factor(T=None, dt=0.1, tail_eps=1e-18):
    """Product of (1 - dt*phi^(-k*dt)); full tail when T is None."""
    c, k = 1.0, 0
    while True:
        t = k * dt
        if T is not None and t >= T - 1e-12:
            break
        f = dt * PHI ** (-t)
        if T is None and f < tail_eps:
            break
        c *= (1.0 - f)
        k += 1
    return c


def test_total_drift_mass_is_finite_and_exact():
    mass = 1.0 / LN_PHI
    assert abs(mass - TOTAL_MASS_STATED) < 1e-12
    # Finiteness is the obstruction: quadrature agrees with the closed form.
    quad = sum(PHI ** (-(i + 0.5) * 1e-3) * 1e-3 for i in range(200_000))
    assert abs(quad - mass) < 1e-4


def test_continuous_floor_is_positive_and_exact():
    c_inf = math.exp(-1.0 / LN_PHI)
    assert abs(c_inf - C_PHI_STATED) < 1e-12
    assert c_inf > 0.125  # the flow keeps more than an eighth of off-anchor z0


def test_continuous_factor_at_T5():
    c5 = math.exp(-(1.0 - PHI ** -5.0) / LN_PHI)
    assert abs(c5 - C_CONT_T5_STATED) < 1e-12


def test_discrete_factor_T5_matches_theorem():
    assert abs(_euler_factor(T=5.0) - C_DISC_T5_STATED) < 1e-12


def test_discrete_infinite_product_has_positive_floor():
    c = _euler_factor(T=None)
    assert abs(c - C_DISC_INF_STATED) < 1e-12
    assert c > 0.11  # no annihilation in the implemented scheme either


def test_dt_halving_moves_toward_continuous_factor():
    """Falsifiable prediction from theorem §3(d): first-order in dt."""
    c5_cont = math.exp(-(1.0 - PHI ** -5.0) / LN_PHI)
    gap_dt10 = c5_cont - _euler_factor(T=5.0, dt=0.1)
    gap_dt05 = c5_cont - _euler_factor(T=5.0, dt=0.05)
    ratio = gap_dt05 / gap_dt10
    assert 0.4 < ratio < 0.6, f"first-order-in-dt prediction failed: {ratio}"


def test_anchor_component_is_conserved_exactly():
    """Theorem §3(a) in R^2: Pi = projection onto first axis. The Pi-component
    never moves; the complement contracts by the Euler factor exactly."""
    dt, n = 0.1, 50
    z = [3.0, 4.0]                      # z0 = (anchor=3, off-anchor=4)
    for k in range(n):
        f = dt * PHI ** (-(k * dt))
        # drift only on the (I-Pi) component (second coordinate)
        z = [z[0], z[1] * (1.0 - f)]
    assert z[0] == 3.0
    assert abs(z[1] - 4.0 * C_DISC_T5_STATED) < 1e-9
