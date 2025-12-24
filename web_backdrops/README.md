# Web Backdrops (Python) — Renderer + Website Capture

This folder is a self‑contained project for creating dynamic backdrops:
- Render GLSL shaders to MP4 (GPU via moderngl + PyAV)
- Or capture HTML/CSS/JS pages to MP4 (Playwright/Chromium)

Default resolution: 1920×864 @ 30 fps.

## Prerequisites
- Python 3.10+
- FFmpeg installed (required by PyAV)
  - macOS: `brew install ffmpeg`
- Website capture (optional): install Chromium once:
  - `python -m playwright install chromium`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Shader → MP4 (moderngl + PyAV)

Render a 10‑second backdrop at 1920×864, 30 fps:

```bash
python -m backdrop --duration 10 --fps 30 --width 1920 --height 864 --output web_backdrops/outputs/plasma.mp4
```

Common options:
- `--duration` seconds (float), e.g. `10`
- `--fps` frames per second, e.g. `30`
- `--width --height` resolution, default `1920×864`
- `--crf` quality (lower = higher quality), default `18`
- `--preset` encoder speed/quality, e.g. `slow`, `medium`, `fast`
- `--bitrate` overrides CRF if provided
- `--shader` fragment shader in `backdrop/shaders/` (no extension), default `plasma`

## Website → MP4 (Playwright)

Create a backdrop web page under `web_backdrops/<name>/index.html`. Optionally implement:
- `window.__init({ width, height, fps })`
- `window.__render(t)` called each frame with time `t` (seconds)

Capture to MP4 (default output goes to `web_backdrops/outputs/webcap_output.mp4`):

```bash
python -m web_backdrops.webcap --html web_backdrops/backdrop_001/index.html --width 1920 --height 864 --fps 30 --duration 10
# or choose a custom output:
python -m web_backdrops.webcap --html web_backdrops/backdrop_001/index.html --output web_backdrops/outputs/my_backdrop.mp4
```

Notes:
- Captures `#stage` by default; use `<canvas id="stage" width="1920" height="864">` for best results, or pass `--selector`.
- The CLI creates the output directory if needed.

## Project Structure

```
backdrop/
  __init__.py
  __main__.py
  cli.py
  encoder.py
  glfw_context.py
  renderer.py
  shaders/
    fullscreen.vert
    plasma.frag
web_backdrops/
  backdrop_001/
    index.html
  backdrop_nasdaq/
    index.html
    assets/
      README.txt
  outputs/
  webcap/
    __init__.py
    __main__.py        # run with: python -m web_backdrops.webcap
    cli.py             # website → MP4 (Playwright)
```

## Notes
- On macOS, a hidden GLFW window is used to host the OpenGL context.
- If you author new shaders, ensure they declare `uniform float iTime;` and `uniform vec2 iResolution;` (or match the renderer’s expectations) and write to `fragColor`.
- For H.265/HEVC (`libx265`), change the CLI codec in the shader renderer and make sure your FFmpeg supports it.