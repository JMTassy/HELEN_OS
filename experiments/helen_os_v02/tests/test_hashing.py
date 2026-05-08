from helen.hashing import sha256


def test_hash_determinism():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert sha256(a) == sha256(b)
