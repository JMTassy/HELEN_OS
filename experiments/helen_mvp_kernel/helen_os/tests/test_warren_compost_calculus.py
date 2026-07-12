"""Executable witness for WARREN_COMPOST_CALCULUS_V1.

Verifies the three laws of the Unforgetting Garden with stdlib arithmetic
only. Derives everything from the phi-contraction floor; introduces no new
axioms. NON_SOVEREIGN. authority=false.
"""

import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LN_PHI = math.log(PHI)
C_PHI = math.exp(-1.0 / LN_PHI)  # 0.125169442295... the floor


def detail_at(w0, t):
    """Closed-form detail mass at trace age t (continuous flow)."""
    return w0 * math.exp(-(1.0 - PHI ** (-t)) / LN_PHI)


def compost(lesson, w, kappa=1.0, rho=0.3):
    """COMPOST IT operator: transfer detail into lesson, shrink detail."""
    return lesson + kappa * w, rho * w


# ---------------------------------------------------------------- LAW 1

def test_law1_callback_guarantee():
    """Salience never falls below lesson + c_phi * w0: T9 satisfiable forever."""
    l0, w0 = 0.0, 1.0
    for t in (0.1, 1.0, 5.0, 50.0, 500.0):
        sal = l0 + detail_at(w0, t)
        assert sal >= l0 + C_PHI * w0 - 1e-12, f"floor pierced at t={t}"
    # eligibility formula: eligible <=> l0 >= theta - c_phi*w0
    theta = 0.15
    l0_needed = theta - C_PHI * w0            # ~0.0248
    sal_inf = l0_needed + C_PHI * w0
    assert abs(sal_inf - theta) < 1e-12


def test_law1_threshold_below_floor_always_eligible():
    """theta = 0.10*s0 < c_phi: every pure-detail trace stays eligible."""
    w0 = 1.0
    assert detail_at(w0, 1e6) > 0.10 * w0


# ---------------------------------------------------------------- LAW 2

def test_law2_compost_necessity():
    """Waiting caps at ~8x reduction; compost breaks the floor."""
    w0 = 1.0
    plateau = detail_at(w0, 1e6)
    assert abs(plateau - C_PHI * w0) < 1e-9          # passive cap
    _, w_after = compost(0.0, plateau, rho=0.3)
    assert w_after < C_PHI * w0                       # floor broken
    # k composts: residue <= rho^k * w0
    w = w0
    for _ in range(3):
        _, w = compost(0.0, w, rho=0.3)
    assert w <= 0.3 ** 3 * w0 + 1e-12


# ---------------------------------------------------------------- LAW 3

def test_law3_lesson_monotone_and_zol_backed():
    """Under the conservation condition kappa <= 1-rho, lesson only grows
    and ZOL minting is bounded by lambda * (total detail deposited)."""
    lam, kappa, rho = 10.0, 0.5, 0.5          # mass-conserving: kappa = 1-rho
    lesson, w = 0.0, 1.0
    zol, lessons_seen = 0.0, [lesson]
    for _ in range(50):
        w *= 0.9                               # some passive decay
        new_lesson, w = compost(lesson, w, kappa=kappa, rho=rho)
        zol += lam * (new_lesson - lesson)     # mint on transfer
        lesson = new_lesson
        lessons_seen.append(lesson)
        assert abs((lesson + w) - lessons_seen[0]) <= 1.0 + 1e-9  # never exceeds deposit
    assert all(b >= a for a, b in zip(lessons_seen, lessons_seen[1:]))
    assert zol <= lam * 1.0 + 1e-9             # backed by total deposit w0=1


def test_law3_condition_is_load_bearing():
    """NEGATIVE witness (kept per Law 5): with kappa > 1-rho the backing
    bound FAILS — the first draft of Law 3 was falsified by exactly this."""
    lam, kappa, rho = 10.0, 1.0, 0.5           # violates kappa <= 1-rho
    lesson, w, zol = 0.0, 1.0, 0.0
    for _ in range(50):
        w *= 0.9
        new_lesson, w = compost(lesson, w, kappa=kappa, rho=rho)
        zol += lam * (new_lesson - lesson)
        lesson = new_lesson
    assert zol > lam * 1.0                      # double-minting: bound broken


# ------------------------------------------------- closed form == scheme

def test_closed_form_matches_euler_product():
    """The lazy JS-style closed form agrees with the stepped Euler scheme
    that the Phase-0 kernel implements (first-order in dt)."""
    w0, T = 1.0, 5.0
    for dt, tol in ((0.1, 0.02), (0.01, 0.002)):
        w = w0
        k = 0
        while k * dt < T - 1e-12:
            w *= (1.0 - dt * PHI ** (-(k * dt)))
            k += 1
        assert abs(w - detail_at(w0, T)) < tol, (dt, w, detail_at(w0, T))


def test_constants_match_floor_theorem():
    assert abs(C_PHI - 0.125169442295) < 1e-12
    assert abs(1.0 / LN_PHI - 2.078086921235) < 1e-12
