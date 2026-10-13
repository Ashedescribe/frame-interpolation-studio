"""RIFE-style multi-scale flow network (trimmed for the studio build).

Follows the reference RIFE v4 topology: a small feature encoder, a
coarse-to-fine IFNet, and a synthesis head that warps the two inputs
by the predicted flow and blends them at timestep `t`.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from fis.core.flow_warp import warp


def _conv(in_c: int, out_c: int, k: int = 3, s: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_c, out_c, k, s, padding=k // 2)


class IFBlock(nn.Module):
    def