SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PYTHONPATH := /Users/jean-marietassy/Desktop/JMT\ CONSULTING\ -\ Releve\ 24

.PHONY: test membrane-test anti-regression ghost-check

# Run all tests
test:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q helen_os/tests/

# Run core membrane tests (batch + validator + anti-regression + ghost-check)
membrane-test:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q \
	  helen_os/tests/test_ledger_validator_accepts_valid_and_rejects_invalid.py \
	  helen_os/tests/test_autoresearch_batch_is_bounded_and_ordered.py \
	  helen_os/tests/test_autoresearch_batch_is_deterministic.py \
	  helen_os/tests/test_no_local_replay_shadowing.py \
	  helen_os/tests/test_no_ghost_closures.py

# Check for replay divergence (single source of truth)
anti-regression:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q \
	  helen_os/tests/test_no_local_replay_shadowing.py -v

# Ghost closure attestation gate — every CLOSED receipt must be receipt-backed
ghost-check:
	source $(VENV)/bin/activate && PYTHONPATH=$(PYTHONPATH) $(PYTEST) -q \
	  helen_os/tests/test_no_ghost_closures.py -v
