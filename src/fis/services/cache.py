"""Disk cache for interpolated frame sequences.

Keyed by (clip hash, start index, multiplier, model). Lets the desktop
preview reuse frames the batch job already produced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch


class FrameCache:
    def __init__(self, root: Path, max_bytes: int = 8 * 1024**3) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)
        self._max_bytes = max_bytes

    @staticmethod
    def key(clip: Path, start: int, multiplier: int, model: str) -> str:
        h = hashlib.blake2b(digest_size=16)
        h.update(clip.name.encode())
        h.update(f"{start}:{multiplier}:{model}".encode())
        return h.hexdigest()

    def get(self, key: str) -> list[torch.Tensor] | None:
        p = self._root / f"{key}.pt"
        if not p.exists():
            return None
        data = torch.load(p, map_location="cpu", weights_only=True)
        return list(data)

    def put(self, key: str, frames: list[torch.Tensor]) -> None:
        torch.save(frames, self._root / f"{key}.pt")
        self._evict()

    def _evict(self) -> None:
        entries = sorted(self._root.glob("*.pt"), key=lambda p: p.stat().st_mtime)
        total = sum(p.stat().st_size for p in entries)
        for p in entries:
            if total <= self._max_bytes:
                break
            total -= p.stat().st_size
            p.unlink(missing_ok=True)

    def manifest(self) -> dict[str, object]:
        return {"root": str(self._root), "entries": len(list(self._root.glob("*.pt")))}

    def dump_manifest(self, path: Path) -> None:
        path.write_text(json.dumps(self.manifest(), indent=2), encoding="utf-8")