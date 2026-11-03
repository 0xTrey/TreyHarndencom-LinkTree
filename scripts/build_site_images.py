#!/usr/bin/env python3
"""Build responsive portrait derivatives with macOS sips."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "static" / "images"
SOURCE = IMAGE_DIR / "headshot-professional-v1-web.jpg"
AVIF_SIZES = (720,)
JPEG_SIZES = (720, 960, 1280)


def run_sips(*args: str) -> None:
    subprocess.run(["sips", *args], check=True, stdout=subprocess.DEVNULL)


def build_derivative(width: int, image_format: str, extension: str) -> Path:
    destination = IMAGE_DIR / f"headshot-professional-v1-{width}.{extension}"
    options = [
        "--resampleWidth",
        str(width),
        "--setProperty",
        "format",
        image_format,
    ]
    if image_format == "jpeg":
        options.extend(["--setProperty", "formatOptions", "82"])
    elif image_format == "avif":
        options.extend(["--setProperty", "formatOptions", "68"])

    run_sips(*options, str(SOURCE), "--out", str(destination))
    return destination


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source portrait: {SOURCE.relative_to(ROOT)}")
    if shutil.which("sips") is None:
        raise SystemExit("This image build requires macOS sips.")

    outputs = [build_derivative(width, "avif", "avif") for width in AVIF_SIZES]
    outputs.extend(build_derivative(width, "jpeg", "jpg") for width in JPEG_SIZES)

    for output in outputs:
        print(f"{output.relative_to(ROOT)}\t{output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
