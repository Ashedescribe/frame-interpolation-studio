"""Model loading and weight resolution.

Resolves a model name to a network instance and loads weights from
`weights_dir`. Weights are expected as `.pth` state dicts with the
same key layout the reference RIFE release uses.
"""

from __future__ import annotations

from pathlib import Path

import structlog
import torch

from fis.models.base import InterpolationModel
from fis.models.registry import MODEL_REGISTRY

log = structlog.get_logger(__name__)


def load_model(name: str, *, device: str, weights_dir: Path) -> InterpolationModel:
    if name not in MODEL_REGISTRY:
        raise KeyError(f"unknown model '{name}', known: {sorted(MODEL_REGISTRY)}")
    factory = MODEL_REGISTRY[name]
    net = factory()
    weight_file = weights_dir / f"{name}.pth"
    if weight_file.exists():
        state = torch.load(weight_file, map_location="cpu", weights_only=True)
        net.load_state_dict(state, strict=False)
        log.info("model.loaded", name=name, path=str(weight_file))
    else:
        log.warning("model.weights_missing", name=name, expected=str(weight_file))
    net.to(device).eval()
    return net