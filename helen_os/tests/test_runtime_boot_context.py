"""Test: RuntimeBootContext — boot continuity object law."""
from helen_os.boot.runtime_boot_context import RuntimeBootContext


def test_empty_context_is_empty():
    ctx = RuntimeBootContext()
    assert ctx.is_empty()
    assert ctx.loaded_from == "empty"


def test_context_with_person_not_empty():
    ctx = RuntimeBootContext(person_profile={"name": "JM"})
    assert not ctx.is_empty()
    assert ctx.person_name() == "JM"


def test_missing_person_name_returns_none():
    ctx = RuntimeBootContext(person_profile={"role": "operator"})
    assert ctx.person_name() is None


def test_epoch_id_from_epoch_state():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E42"})
    assert ctx.last_epoch_id() == "E42"


def test_missing_epoch_state_returns_none():
    ctx = RuntimeBootContext()
    assert ctx.last_epoch_id() is None


def test_to_dict_has_schema():
    ctx = RuntimeBootContext()
    d = ctx.to_dict()
    assert d["schema"] == "RUNTIME_BOOT_CONTEXT_V1"
    assert "person_profile" in d


def test_to_dict_preserves_loaded_from():
    ctx = RuntimeBootContext(loaded_from="storage", person_profile={"name": "X"})
    assert ctx.to_dict()["loaded_from"] == "storage"


def test_all_fields_none_is_empty():
    ctx = RuntimeBootContext(
        person_profile=None, last_session=None,
        epoch_state=None, companion_state=None, live_context=None,
    )
    assert ctx.is_empty()
