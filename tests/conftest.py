"""
Test suite partitioning for helen-conquest root tests/.

Three classes:
  core          - constitutional invariants; always run; no external deps
  requires_ocaml - kernel_cli binary (OCaml); skip when binary absent
  integration   - full runtime env (daemon, numpy, nacl, etc.); optional
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import kernel_cli_available


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_ocaml: skip when kernel_cli binary is not built")
    config.addinivalue_line("markers", "integration: requires full runtime environment")


def _nacl_available() -> bool:
    try:
        import nacl.signing  # noqa: F401
        return True
    except ImportError:
        return False


def pytest_collection_modifyitems(config, items):
    skip_ocaml = pytest.mark.skip(reason="kernel_cli binary not built (OCaml required)")
    skip_integration = pytest.mark.skip(reason="integration env not available (nacl/daemon required)")
    ocaml_ok = kernel_cli_available()
    nacl_ok = _nacl_available()
    for item in items:
        if "requires_ocaml" in item.keywords and not ocaml_ok:
            item.add_marker(skip_ocaml)
        if "integration" in item.keywords and not nacl_ok:
            item.add_marker(skip_integration)
