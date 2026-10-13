"""Plugin host for community interpolation backends.

Plugins are Python modules exposing `register(registry)` that add
model factories. They run in-process with full privileges; only load
plugins you trust.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import structlog

from fis.models.registry import MODEL_REGISTRY

log = structlog.get_logger(__name__)


def load_plugin(path: Path) -> None:
    if not path.is_file() or path.suffix != ".py":
        raise ValueError(f"plugin must be a .py file: {path}")
    spec = importlib.util.spec_from_file_location(f"fis_plugin_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load plugin spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "register"):
        raise AttributeError(f"plugin {path.name} missing register(registry)")
    module.register(MODEL_REGISTRY)
    log.info("plugin.loaded", path=str(path))