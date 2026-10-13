"""Short-window preview handler used by the desktop scrubber.

Interpolates only the two frames bracketing the playhead so the UI can
show a fluid preview without re-encoding the whole clip.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from fis.core.engine import InterpolationRequest, interpolate_pair
from fis.services.model_loader import load_model
from fis.services.video_reader import VideoReader


class PreviewHandler:
    def __init__(self, device: str, weights_dir: Path) -> None:
        self._device = device
        self._weights_dir = weights_dir

    def frame_at(self, clip: Path, index: int, *, model: str = "rife-v4.6", t: float = 0.5) -> np.ndarray:
        net = load_model(model, device=self._device, weights_dir=self._weights_dir)
        with VideoReader(clip) as reader:
            a = reader.read_frame_at(index)
            b = reader.read_frame_at(index + 1)
        if a is None or b is None:
            raise IndexError(f"frame {index} out of range for {clip}")
        mids = interpolate_pair(net, InterpolationRequest(first=a, second=b, multiplier=2))
        if not mids:
            return a.squeeze(0).permute(1, 2, 0).cpu().numpy()
        return mids[0].squeeze(0).permute(1, 2, 0).cpu().numpy()