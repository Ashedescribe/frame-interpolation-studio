"""Headless CLI entry point.

Usage:
    fis interpolate clip.mp4 --multiplier 4 --model rife-v4.6 -o out.mp4
    fis batch ./clips --multiplier 2 --recursive
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fis.config.settings import load_settings
from fis.handlers.batch_handler import BatchHandler
from fis.handlers.single_clip_handler import SingleClipHandler
from fis.services.logging_setup import configure_logging
from fis.utils.device_probe import pick_device


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fis", description="AI slow-motion / frame interpolation.")
    sub = p.add_subparsers(dest="cmd", required=True)

    single = sub.add_parser("interpolate", help="Interpolate a single clip.")
    single.add_argument("input", type=Path)
    single.add_argument("-o", "--output", type=Path, required=True)
    single.add_argument("-m", "--multiplier", type=int, default=2)
    single.add_argument("--model", default="rife-v4.6")
    single.add_argument("--device", default="auto")

    batch = sub.add_parser("batch", help="Interpolate every clip in a directory.")
    batch.add_argument("input_dir", type=Path)
    batch.add_argument("-o", "--output-dir", type=Path, required=True)
    batch.add_argument("-m", "--multiplier", type=int, default=2)
    batch.add_argument("--recursive", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = _build_parser().parse_args(argv)
    settings = load_settings()

    if args.cmd == "interpolate":
        handler = SingleClipHandler(settings=settings, device=pick_device(args.device))
        handler.run(args.input, args.output, multiplier=args.multiplier, model=args.model)
        return 0

    if args.cmd == "batch":
        handler = BatchHandler(settings=settings, device=pick_device("auto"))
        handler.run(args.input_dir, args.output_dir, multiplier=args.multiplier, recursive=args.recursive)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))