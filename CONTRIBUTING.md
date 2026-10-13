# Contributing to frame-interpolation-studio

Thanks for wanting to push frames. This repo is a Windows-first desktop
tool for AI slow-motion and frame interpolation. It wraps RIFE / FILM /
IFRNet style networks behind a Qt desktop UI, with a CLI and a batch
pipeline for long clips.

## Ground rules

- Python 3.11+ is the target runtime. We ship a frozen build with
  PyInstaller on Windows 10/11 x64.
- Every PR must run `pytest tests/` clean and `ruff check src/` clean.
- Do not commit model weights. Weights live under `models/weights/`
  and are downloaded by `scripts/fetch_weights.py` from the release
  mirror. `.gitignore` blocks them on purpose.
- GPU code paths must degrade to CPU. If your change assumes CUDA,
  guard it.
- Keep the interpolation math in `src/fis/core/` pure. No Qt imports,
  no CLI imports, no file IO in the core engine.

## Layout

```
src/fis/bootstrap/    entry points (desktop, cli)
src/fis/core/         engine, tween math, flow warping
src/fis/handlers/     per-feature handlers (single clip, batch, preview)
src/fis/services/     model loading, video IO, cache, telemetry
src/fis/models/       network definitions (RIFE, FILM, IFRNet)
src/fis/utils/        logging, timing, frame utils, device probe
src/fis/config/       settings schema and defaults
```

## Adding a new interpolation model

1. Drop the network definition into `src/fis/models/`.
2. Register it in `src/fis/models/registry.py`.
3. Add a loader branch in `src/fis/services/model_loader.py`.
4. Add a smoke test in `tests/test_engine.py` that runs a 2-frame
   interpolation on a synthetic tensor and checks shape + finiteness.

## Coding style

- Type hints on every public function.
- `structlog` style key/value logging, not `print`.
- Prefer dataclasses over dicts for anything crossing a module
  boundary.
- No silent `except:` blocks. Catch specific exceptions.

## Commit messages

`area: short imperative summary` — e.g.
`core: fix chroma alignment on odd-height frames`

## Reporting bugs

Open an issue with: GPU model, driver version, input resolution,
target multiplier, and the first 40 lines of `logs/fis.log`.