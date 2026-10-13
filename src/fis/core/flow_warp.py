"""Optical-flow warping helpers used by the model wrappers.

Kept separate from the models so the warping math can be unit tested
against a naive reference without loading any weights.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


def warp(frame: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
    """Backward-warp `frame` by `flow` (N, 2, H, W) in pixel units.

    Uses bilinear sampling with zero padding, matching the convention
    used by RIFE and IFRNet reference implementations.
    """
    n, _, h, w = frame.shape
    grid_y, grid_x = torch.meshgrid(
        torch.arange(h, dtype=frame.dtype, device=frame.device),
        torch.arange(w, dtype=frame.dtype, device=frame.device),
        indexing="ij",
    )
    grid_x = grid_x + flow[:, 0]
    grid_y = grid_y + flow[:, 1]
    norm_x = 2.0 * grid_x / max(w - 1, 1) - 1.0
    norm_y = 2.0 * grid_y / max(h - 1, 1) - 1.0
    grid = torch.stack([norm_x, norm_y], dim=-1)
    return F.grid_sample(frame, grid, mode="bilinear", padding_mode="border", align_corners=True)


def flow_scale(flow: torch.Tensor, factor: float) -> torch.Tensor:
    """Scale a flow field by `factor` (used for fractional timesteps)."""
    return flow * factor