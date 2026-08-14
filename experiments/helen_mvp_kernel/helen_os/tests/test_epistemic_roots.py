"""Claim-level epistemic root accounting — the four rules, as falsifiers. 🔵 OBSERVED.

1. different documents ⊬ different roots
2. different authors ⊬ independent witnesses
3. independence is computed per CLAIM, not per source
4. representation multiplicity ⊬ warrant
"""
from helen_os.audit.epistemic_roots import (
    Representation, dependency_uncertainty, lambda_proxy, n_epi, n_representations,
    n_unresolved, proxy_laundering, warrant_root_count, warrant_supported,
)


def R(id, root, kind=""):
    return Representation(id, root, kind)


# ─────────────── Rule 1 — different documents ⊬ different roots ───────────────
def test_ten_newspapers_one_interview_is_one_root():
    reps = [R(f"paper_{i}", root="interview_X", kind="newspaper") for i in range(10)]
    assert n_representations(reps) == 10
    assert n_epi(reps) == 1                       # ten publications, one witness
    assert lambda_proxy(reps) == 10.0
    assert proxy_laundering(reps) is True         # "10 sources corroborate" is FALSE


# ─────────────── Rule 2 — different authors ⊬ independent witnesses ───────────────
def test_subject_biographer_proxy_is_one_root():
    # Sanders' hereditary-initiation claim: Subject → Johns (biographer) → book → derivative quote.
    # Different author (Johns) does NOT mint a second root — the support traces to the subject.
    reps = [
        R("sanders_statement", root="sanders_claim", kind="interview"),
        R("johns_book", root="sanders_claim", kind="biography"),
        R("later_quote", root="sanders_claim", kind="derivative"),
    ]
    assert n_epi(reps) == 1                        # Author(x) ≠ EpistemicRoot(x)
    assert warrant_root_count(reps) == 1
    assert proxy_laundering(reps) is True


# ─────────────── Rule 3 — independence is per CLAIM, not per source ───────────────
def test_same_book_is_proxy_for_one_claim_and_root_for_another():
    # The SAME book (Johns) is a proxy for the origin myth but an independent root for
    # something she personally witnessed. Root accounting is claim-local.
    origin_myth = [
        R("sanders_statement", root="sanders_claim"),
        R("johns_retelling", root="sanders_claim"),      # descends from the subject
    ]
    coven_meeting = [
        R("johns_direct_obs", root="johns_eyewitness"),  # Johns saw it herself → her own root
        R("attendee_account", root="attendee_eyewitness"),
    ]
    assert n_epi(origin_myth) == 1                 # proxy for the myth
    assert n_epi(coven_meeting) == 2               # independent for what she witnessed
    # the source is identical; only the CLAIM differs → different root counts


# ─────────────── Rule 4 — representation multiplicity ⊬ warrant ───────────────
def test_warrant_tracks_roots_not_representations():
    one = [R("a", root="src")]
    thirtyseven = [R(f"r{i}", root="src") for i in range(37)]      # 37 restatements of one root
    assert warrant_root_count(one) == warrant_root_count(thirtyseven) == 1
    assert lambda_proxy(thirtyseven) == 37.0       # Λ_proxy=37: amplification, not corroboration


# ─────────────── Positive control — genuine independence is NOT laundering ───────────────
def test_genuinely_independent_roots_are_not_flagged():
    # civil registry + contemporaneous eyewitness + independent photograph = three real roots.
    reps = [
        R("civil_registry", root="registry", kind="record"),
        R("eyewitness", root="witness_A", kind="testimony"),
        R("photo", root="photo_archive", kind="image"),
    ]
    assert n_epi(reps) == 3
    assert lambda_proxy(reps) == 1.0               # every representation is its own root
    assert proxy_laundering(reps) is False         # NOT laundering — non-vacuity guard
    assert warrant_root_count(reps) == 3


def test_single_representation_is_not_laundering():
    reps = [R("only", root="r")]
    assert proxy_laundering(reps) is False         # one doc, one root — nothing amplified


# ─────────────── THE STRESS TEST — hidden common dependency (~dep collapse) ───────────────
def test_hidden_common_dependency_collapses_apparent_roots():
    # Two reports with DIFFERENT root ids — naive dedup by document/root sees two witnesses.
    # But both analysts quoted the SAME spokesperson: a hidden upstream dependency.
    reps = [R("report_a", root="analyst_A", kind="analysis"),
            R("report_b", root="analyst_B", kind="analysis")]
    assert n_epi(reps) == 2                                  # naive: two apparent roots
    deps = [("analyst_A", "analyst_B")]                      # ~dep,c : shared upstream source
    assert n_epi(reps, deps) == 1                            # collapses to ONE witness
    assert lambda_proxy(reps, deps) == 2.0
    assert proxy_laundering(reps, deps) is True              # amplification exposed
    assert warrant_root_count(reps, deps) == 1              # warrant sees one root, not two


def test_transitive_dependency_chain_collapses():
    # a↔b and b↔c share upstreams → all three collapse to one component (union-find transitivity)
    reps = [R("r_a", root="a"), R("r_b", root="b"), R("r_c", root="c")]
    assert n_epi(reps) == 3
    assert n_epi(reps, [("a", "b"), ("b", "c")]) == 1       # transitive collapse


# ─────────────── FIXTURE 6 — mixed dependency (N_repr=5, N_epi=2) ───────────────
def test_mixed_dependency_is_neither_one_nor_five():
    # A and B independently observe; C, D, E all derive from A. Expected N_epi = 2 (not 1, not 5).
    reps = [R("A", "A"), R("B", "B"), R("C", "C"), R("D", "D"), R("E", "E")]
    deps = [("C", "A"), ("D", "A"), ("E", "A")]             # C,D,E collapse into A's component
    assert n_representations(reps) == 5
    assert n_epi(reps, deps) == 2                           # {A,C,D,E} and {B}


# ─────────────── FIXTURE 5 — independent-but-weak (N_epi ⊬ W) ───────────────
def test_ten_independent_rumors_do_not_warrant():
    # Ten genuinely independent roots, but all low quality (rumors / poor measurements).
    reps = [R(f"rumor_{i}", root=f"src_{i}") for i in range(10)]
    assert n_epi(reps) == 10                                # structurally independent
    q = {f"src_{i}": 0.1 for i in range(10)}                # all weak
    assert warrant_supported(reps, root_quality=q) is False  # N_epi=10 ⊬ warrant
    # positive control: three STRONG independent roots do warrant
    strong = [R("a", "a"), R("b", "b"), R("c", "c")]
    assert warrant_supported(strong, root_quality={"a": 0.9, "b": 0.9, "c": 0.9}) is True


# ─────────────── UNRESOLVED ≠ INDEPENDENT and ≠ DEPENDENT ───────────────
def test_unresolved_dependency_is_flagged_not_assumed_independent():
    # Two roots whose dependence is UNKNOWN: do NOT collapse (not proven dependent),
    # but do NOT report clean independence either — n_unresolved surfaces the doubt.
    reps = [R("x", "r1"), R("y", "r2")]
    unresolved = [("r1", "r2")]
    assert n_epi(reps) == 2                                 # not collapsed (not proven dependent)
    assert n_unresolved(reps, unresolved) == 2             # but flagged as unresolved
    assert dependency_uncertainty(reps, unresolved) == 1.0  # 2/2 roots uncertain → n_epi is optimistic
