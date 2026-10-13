"""Single-clip interpolation handler.

Owns the decode -> interpolate -> encode pipeline for one input file.
Progress is reported through an optional callback so both the CLI and
the Qt UI can render a bar.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import structlog

from fis.config.settings import Settings
from fis.core.engine import InterpolationRequest, interpolate_pair
from fis.services.model_loader import load_model
from fis.services.video_reader import VideoReader
from fis.services.video_writer import VideoWriter

log = structlog.get_logger(__name__)
ProgressFn = Callable[[int, int], None]


class SingleClipHandler:
    def __init__(self, settings: Settings, device: str) -> None:
        self._settings = settings
        self._device = device

    def run(
        self,
        input_path: Path,
        output_path: Path,
        *,
        multiplier: int,
        model: str,
        progress: ProgressFn | None = None,
    ) -> None:
        log.info("single_clip.start", input=str(input_path), multiplier=multiplier, model=model)
        net = load_model(model, device=self._device, weights_dir=self._settings.weights_dir)

        with VideoReader(input_path) as reader, VideoWriter(
            output_path,
            fps=reader.fps * multiplier,
            size=reader.size,
        ) as writer:
            prev = reader.read_frame()
            if prev is None:
                raise RuntimeError(f"no frames decoded from {input_path}")
            writer.write(prev)
            total = reader.frame_count
            idx = 1
            for cur in reader.iter_frames():
                mids = interpolate_pair(
                    net,
                    InterpolationRequest(first=prev, second=cur, multiplier=multiplier),
                )
                for m in mids:
                    writer.write(m)
                writer.write(cur)
                prev = cur
                idx += 1
                if progress is not None:
                    progress(idx, total)
        log.info("single_clip.done", output=str(output_path))