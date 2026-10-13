"""Frame interpolation engine.

Takes a decoded frame pair as float32 tensors in [0, 1] with shape
(N, 3, H, W) and produces `multiplier - 1` intermediate frames per gap.
All work is batched through the model's `infer` callable so the caller
can swap RIFE / FILM / IFRNet behind the same interface.

Concurrency: the engine is stateless and safe to call from multiple
threads as long as the underlying model is not mutated concurrently.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch

from fis.core.tween import build_timesteps
from fis.models.base import InterpolationModel


@dataclass(frozen=True, slots=True)
class InterpolationRequest:
    first: torch.Tensor
    second: torch.Tensor
    multiplier: int = 2
    scene_cut_guard: float = 0.35


def interpolate_pair(
    model: InterpolationModel,
    request: InterpolationRequest,
) -> list[torch.Tensor]:
    """Return intermediate frames between `first` and `second`.

    Raises ValueError if `multiplier` < 2. Returns `multiplier - 1`
    frames in temporal order. If the mean absolute difference between
    `first` and `second` exceeds `scene_cut_guard`, an empty list is
    returned and the caller should not synthesize frames across the cut.
    """
    if request.multiplier < 2:
        raise ValueError(f"multiplier must be >= 2, got {request.multiplier}")

    mad = (request.first - request.second).abs().mean().item()
    if mad > request.scene_cut_guard:
        return []

    timesteps = build_timesteps(request.multiplier)
    frames: list[torch.Tensor] = []
    with torch.inference_mode():
        for t in timesteps:
            mid = model.infer(request.first, request.second, t)
            frames.append(mid.clamp_(0.0, 1.0))
    return frames