"""Timestep schedules for frame interpolation.

A multiplier of N produces N-1 interior samples. We default to a linear
schedule; callers may pass a custom one for motion-blur style weighting.
"""

from __future__ import annotations

import numpy as np


def build_timesteps(multiplier: int, *, easing: str = "linear") -> list[float]:
    """Return interior timesteps in (0, 1) for a multiplier.

    `easing` selects the sample distribution:
      - "linear": uniform spacing (default, best for constant motion)
      - "center": denser near 0.5 (good for ease-in/out source pans)
    """
    if multiplier < 2:
        raise ValueError("multiplier must be >= 2")
    n = multiplier - 1
    if easing == "linear":
        return [i / multiplier for i in range(1, multiplier)]
    if easing == "center":
        x = np.linspace(-1.0, 1.0, n + 2)[1:-1]
        warped = 0.5 * (1.0 + np.tanh(x))
        return [float(v) for v in warped]
    raise ValueError(f"unknown easing: {easing}")