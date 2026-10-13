"""Common interface every interpolation network implements."""

from __future__ import annotations

from typing import Protocol

import torch


class InterpolationModel(Protocol):
    def infer(self, first: torch.Tensor, second: torch.Tensor, t: float) -> torch.Tensor:
        """Return the frame at fractional time `t` between the two inputs.

        Inputs are (1, 3, H, W) float32 in [0, 1]. Output has the same
        shape and dtype. Implementations must not mutate their inputs.
        """
        ...

    def to(self, device: str) -> "InterpolationModel": ...

    def eval(self) -> "InterpolationModel": ...

    def load_state_dict(self, state: dict[str, torch.Tensor], strict: bool = False) -> object: ...