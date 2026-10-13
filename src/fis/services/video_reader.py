"""Decode-side wrapper around PyAV.

Yields float32 CHW tensors in [0, 1]. The reader is a context manager
and holds a single decoder; do not share instances across threads.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import av
import numpy as np
import torch


class VideoReader:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._container: av.container.InputContainer | None = None
        self._stream = None
        self._frame_count = 0
        self._fps = 0.0
        self._size: tuple[int, int] = (0, 0)

    def __enter__(self) -> "VideoReader":
        self._container = av.open(str(self._path))
        self._stream = self._container.streams.video[0]
        self._fps = float(self._stream.average_rate)
        self._size = (int(self._stream.codec_context.width), int(self._stream.codec_context.height))
        self._frame_count = int(self._stream.frames or 0)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._container is not None:
            self._container.close()

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @staticmethod
    def _to_tensor(frame: av.VideoFrame) -> torch.Tensor:
        arr = frame.to_ndarray(format="rgb24").astype(np.float32) / 255.0
        return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)

    def read_frame(self) -> torch.Tensor | None:
        assert self._container is not None
        try:
            frame = next(self._container.decode(video=0))
        except StopIteration:
            return None
        return self._to_tensor(frame)

    def iter_frames(self) -> Iterator[torch.Tensor]:
        while True:
            f = self.read_frame()
            if f is None:
                return
            yield f

    def read_frame_at(self, index: int) -> torch.Tensor | None:
        assert self._container is not None
        for i, frame in enumerate(self._container.decode(video=0)):
            if i == index:
                return self._to_tensor(frame)
        return None