from dataclasses import dataclass
from typing import Any, Dict, List
import numpy as np
from PIL import Image

Array = np.ndarray


@dataclass(frozen=True)
class MathObject:
    payload: Dict[str, Any]


@dataclass(frozen=True)
class ImageOut:
    pil: Image.Image


@dataclass(frozen=True)
class GateReport:
    passed: bool
    metrics: Dict[str, float]
    reasons: List[str]
