SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PYTHONPATH := $(CURDIR)

.PHONY: test membrane-test anti-regression demo-helen demo-boot demo-coupling demo-autoresearch demo-airlock

# Run all tests
test:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q helen_os/tests/

# Run core membrane tests (batch + validator + anti-regression)
membrane-test:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q \
	  helen_os/tests/test_ledger_validator_accepts_valid_and_rejects_invalid.py \
	  helen_os/tests/test_autoresearch_batch_is_bounded_and_ordered.py \
	  helen_os/tests/test_autoresearch_batch_is_deterministic.py \
	  helen_os/tests/test_no_local_replay_shadowing.py

# Power demos — NON_SOVEREIGN, authority=NONE, no ledger writes
demo-boot:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/demos/demo_boot_ritual.py

demo-coupling:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/demos/demo_reality_coupling.py

demo-autoresearch:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/demos/demo_bounded_autoresearch.py

demo-airlock:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/demos/demo_init_airlock.py

demo-helen: demo-boot demo-coupling demo-autoresearch demo-airlock

# Check for replay divergence (single source of truth)
anti-regression:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q \
	  helen_os/tests/test_no_local_replay_shadowing.py -v
