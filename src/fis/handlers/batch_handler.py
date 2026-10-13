"""Batch handler: walk a directory and interpolate every matching clip."""

from __future__ import annotations

from pathlib import Path

import structlog

from fis.config.settings import Settings
from fis.handlers.single_clip_handler import SingleClipHandler
from fis.utils.frame_utils import VIDEO_EXTS

log = structlog.get_logger(__name__)


class BatchHandler:
    def __init__(self, settings: Settings, device: str) -> None:
        self._settings = settings
        self._device = device

    def _discover(self, root: Path, recursive: bool) -> list[Path]:
        it = root.rglob("*") if recursive else root.glob("*")
        return sorted(p for p in it if p.is_file() and p.suffix.lower() in VIDEO_EXTS)

    def run(
        self,
        input_dir: Path,
        output_dir: Path,
        *,
        multiplier: int,
        recursive: bool,
    ) -> None:
        clips = self._discover(input_dir, recursive)
        log.info("batch.start", count=len(clips), input_dir=str(input_dir))
        handler = SingleClipHandler(settings=self._settings, device=self._device)
        for clip in clips:
            rel = clip.relative_to(input_dir)
            out = output_dir / rel.with_suffix(".mp4")
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                handler.run(clip, out, multiplier=multiplier, model=self._settings.default_model)
            except Exception as exc:  # noqa: BLE001 - batch must not die on one clip
                log.error("batch.clip_failed", clip=str(clip), error=str(exc))
                continue
        log.info("batch.done", count=len(clips))