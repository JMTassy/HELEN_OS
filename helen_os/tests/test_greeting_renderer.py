"""Test: greeting_renderer — reads only RuntimeBootContext, no improvisation."""
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting


def test_empty_context_returns_fresh_start():
    ctx = RuntimeBootContext()
    g = render_greeting(ctx)
    assert "No prior context" in g or "fresh" in g.lower()


def test_person_name_in_greeting():
    ctx = RuntimeBootContext(person_profile={"name": "JM"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert "JM" in g


def test_epoch_id_in_greeting():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E42"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert "E42" in g


def test_session_id_in_greeting():
    ctx = RuntimeBootContext(
        last_session={"session_id": "S99"},
        epoch_state={"epoch_id": "E1"},
        loaded_from="storage",
    )
    g = render_greeting(ctx)
    assert "S99" in g


def test_loaded_from_in_greeting():
    ctx = RuntimeBootContext(
        person_profile={"name": "X"}, loaded_from="storage"
    )
    g = render_greeting(ctx)
    assert "storage" in g


def test_missing_name_does_not_crash():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E1"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert isinstance(g, str) and len(g) > 0


def test_greeting_is_deterministic():
    ctx = RuntimeBootContext(
        person_profile={"name": "JM"},
        epoch_state={"epoch_id": "E3"},
        loaded_from="storage",
    )
    assert render_greeting(ctx) == render_greeting(ctx)
