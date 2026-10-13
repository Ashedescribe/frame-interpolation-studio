"""Encode-side wrapper around PyAV. Consumes float32 CHW tensors."""

from __future__ import annotations

from pathlib import Path

import av
import numpy as np
import torch


class VideoWriter:
    def __init__(self, path: Path, *, fps: float, size: tuple[int, int], crf: int = 17) -> None:
        self._path = path
        self._fps = fps
        self._size = size
        self._crf = crf
        self._container: av.container.OutputContainer | None = None
        self._stream = None

    def __enter__(self) -> "VideoWriter":
        self._container = av.open(str(self._path), mode="w")
        self._stream = self._container.add_stream("libx264", rate=int(round(self._fps)))
        self._stream.width, self._stream.height = self._size
        self._stream.pix_fmt = "yuv420p"
        self._stream.options = {"crf": str(self._crf), "preset": "slow"}
        return self

    def __exit__(self, *exc: object) -> None:
        if self._container is not None:
            self._container.close()

    def write(self, frame: torch.Tensor) -> None:
        assert self._container is not None
        arr = (frame.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
        vf = av.VideoFrame.from_ndarray(arr, format="rgb24")
        for pkt in self._stream.encode(vf):
            self._container.mux(pkt)