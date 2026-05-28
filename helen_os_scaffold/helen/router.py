"""
Compatibility shim.

Tests and bridge code import:
  from helen.router import route_input, set_helen_instance

Real implementation lives in:
  helen_os.router
"""
from helen_os.router import *  # noqa: F401,F403
