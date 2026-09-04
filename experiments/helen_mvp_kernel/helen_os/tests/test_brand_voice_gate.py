"""brand_voice gate falsifiers. 🔵 OBSERVED.

Fail-closed UZIK-register linter over the extracted corpus. A voice check is authority-0:
render ⊬ admitted. Each falsifier forces one violation class; the clean cases must PASS.
"""
from helen_os.voice.brand_voice_gate import (
    Verdict, check, load_corpus, report,
)

CORPUS = load_corpus()


def _codes(text):
    return {v.code for v in check(text, CORPUS).violations}


# ---- BV-01: banned vocabulary → FAIL
def test_bv01_banned_vocab_fails():
    r = check("We drive innovation for iconic brands.", CORPUS)
    assert r.verdict == Verdict.FAIL and "BANNED_VOCAB" in {v.code for v in r.violations}


# ---- BV-02: banned production verb → FAIL
def test_bv02_banned_verb_fails():
    assert "BANNED_VOCAB" in _codes("We leverage the platform.")
    assert "BANNED_VOCAB" in _codes("Optimize and synergize the funnel.")


# ---- BV-03: negative parallelism (hard ban) → FAIL
def test_bv03_negative_parallelism_fails():
    assert "NEGATIVE_PARALLELISM" in _codes("This is not a campaign, but a movement.")
    assert "NEGATIVE_PARALLELISM" in _codes("We don't just make content but shape culture.")


# ---- BV-03b: French negative parallelism → FAIL
def test_bv03b_french_negative_parallelism_fails():
    assert "NEGATIVE_PARALLELISM" in _codes("Ce n'est pas une agence mais un studio.")
    assert "NEGATIVE_PARALLELISM" in _codes("Non pas du slop mais du craft.")


# ---- BV-04: unsourced metric → FAIL
def test_bv04_unsourced_metric_fails():
    assert "UNSOURCED_METRIC" in _codes("Onboarding time dropped 40% last quarter.")
    assert "UNSOURCED_METRIC" in _codes("Reach grew 3x.")


# ---- BV-05: clean UZIK-register copy → PASS
def test_bv05_clean_copy_passes():
    clean = "CLIENT: BRAND\nPHASE: PRODUCTION\nFORMAT: EVENT / CONTENT FACTORY\nSTATUS: V2\nNEXT: kick off"
    assert check(clean, CORPUS).verdict == Verdict.PASS


# ---- BV-06: metric WITH a source → PASS (obligation discharged)
def test_bv06_sourced_metric_passes():
    assert check("Onboarding time dropped 40% (source: analytics dashboard).", CORPUS).verdict == Verdict.PASS


# ---- BV-07: verbatim taglines pass (brand voice is admissible copy)
def test_bv07_verbatim_taglines_pass():
    for tagline in CORPUS["brand_voice"]["taglines_verbatim"]:
        assert check(tagline, CORPUS).verdict == Verdict.PASS, tagline


# ---- BV-08: multiple violations aggregate, not short-circuit
def test_bv08_violations_aggregate():
    r = check("We leverage innovation, not a tool but a revolution, up 50%.", CORPUS)
    codes = {v.code for v in r.violations}
    assert {"BANNED_VOCAB", "NEGATIVE_PARALLELISM", "UNSOURCED_METRIC"} <= codes


# ---- non-vacuity: the gate reports which checks actually ran (no silent empty pass)
def test_bv_non_vacuous_checks_run():
    r = check("CLIENT: BRAND", CORPUS)
    assert r.verdict == Verdict.PASS
    assert set(r.checks_run) == {"banned_vocab", "negative_parallelism", "unsourced_metric"}


# ---- authority is structurally 0; the report is projection-only
def test_bv_authority_zero_and_report_shape():
    r = check("We leverage synergy.", CORPUS)
    assert r.authority == 0
    rep = report(r)
    assert rep["authority"] == 0 and rep["canon"] is False
    assert rep["verdict"] == "FAIL" and rep["violation_count"] >= 1
    assert "BANNED_VOCAB" in rep["violations_by_code"]
