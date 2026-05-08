from helen.mayor import mayor_verdict


def test_no_ship_default():
    assert mayor_verdict({}) == "NO_SHIP"


def test_no_ship_any_state():
    assert mayor_verdict({"admitted_receipts": ["R-1", "R-2"]}) == "NO_SHIP"
