"""python -m helen_kernel.constitution — run the deployed gate."""
from __future__ import annotations

import json
import sys

from . import verify_constitution

if __name__ == "__main__":
    receipt = verify_constitution()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    sys.exit(0 if receipt["verdict"] == "CONSTITUTION_HELD" else 1)
