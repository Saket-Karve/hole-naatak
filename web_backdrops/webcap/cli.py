from __future__ import annotations

import argparse
import asyncio
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image
import numpy as np
from playwright.async_api import async_playwright

from backdrop.encoder import MP4Encoder, EncoderConfig

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "web_backdrops" / "outputs" / "webcap_output.mp4"

async def _capture_element_png(page, selector: str) -> bytes:
    el = page.locator(selector)
    return await el.screenshot(type="png")


async def _call_optional(page, fn_name: str, *args):
    exists = await page.evaluate("(name) => typeof window[name] === 'function'", fn_name)
    if exists:
        # Pass arguments via Playwright's arg channel; avoid polluting window globals
        await page.evaluate(
            "(data) => { const fn = window[data.fnName]; if (typeof fn === 'function') { return fn(...data.args); } }",
            {"fnName": fn_name, "args": list(args)},
        )


async def capture_html_to_mp4_async(
    html_path: Path,
    output: Path,
    width: int,
    height: int,
    fps: int,
    duration: float,
    selector: str = "#stage",
) -> None:
    num_frames = int(round(duration * fps))
    dt = 1.0 / float(fps)

    output.parent.mkdir(parents=True, exist_ok=True)
    cfg = EncoderConfig(width=width, height=height, fps=fps)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=1.0,
            color_scheme="dark",
        )
        page = await context.new_page()
        await page.goto(html_path.resolve().as_uri(), wait_until="load")

        # Initialize if provided
        await _call_optional(page, "__init", {"width": width, "height": height, "fps": fps})

        with MP4Encoder(str(output), cfg) as enc:
            t = 0.0
            for _ in range(num_frames):
                # Drive the page's render function if present
                await _call_optional(page, "__render", t)
                # Capture the canvas element (or page fallback)
                try:
                    png_bytes = await _capture_element_png(page, selector)
                except Exception:
                    png_bytes = await page.screenshot(full_page=False, type="png")

                img = Image.open(BytesIO(png_bytes)).convert("RGB")
                if img.size != (width, height):
                    img = img.resize((width, height), Image.BICUBIC)
                frame = np.array(img, dtype=np.uint8)
                enc.encode_frame(frame)
                t += dt

        await context.close()
        await browser.close()


def capture_html_to_mp4(
    html_path: Path,
    output: Path,
    width: int = 1920,
    height: int = 864,
    fps: int = 30,
    duration: float = 10.0,
    selector: str = "#stage",
) -> None:
    asyncio.run(
        capture_html_to_mp4_async(
            html_path=html_path,
            output=output,
            width=width,
            height=height,
            fps=fps,
            duration=duration,
            selector=selector,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capture a website backdrop to MP4 using headless Chromium.")
    p.add_argument("--html", type=Path, required=True, help="Path to local HTML file (e.g., web_backdrops/backdrop_001/index.html)")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output MP4 file path (default: {DEFAULT_OUTPUT})")
    p.add_argument("--width", type=int, default=1920, help="Video width")
    p.add_argument("--height", type=int, default=864, help="Video height")
    p.add_argument("--fps", type=int, default=30, help="Frames per second")
    p.add_argument("--duration", type=float, default=10.0, help="Duration in seconds")
    p.add_argument("--selector", type=str, default="#stage", help="CSS selector to capture (default: #stage)")
    return p


def main() -> None:
    args = build_parser().parse_args()
    capture_html_to_mp4(
        html_path=args.html,
        output=args.output,
        width=args.width,
        height=args.height,
        fps=args.fps,
        duration=args.duration,
        selector=args.selector,
    )


