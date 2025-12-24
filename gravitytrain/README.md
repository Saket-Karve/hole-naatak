# Gravity Train — Standalone Web Experience

This directory contains a fully standalone version of the Gravity Train website. It does not depend on any other files in the repository.

## Quick start (Python - preinstalled on macOS/Linux)

1. Open a terminal and navigate to this folder:
   ```bash
   cd gravitytrain
   ```
2. Start a local web server:
   ```bash
   python3 -m http.server 8080
   ```
3. Open the site in your browser:
   - `http://localhost:8080/` (loads `index.html`)

## Alternative: Node.js (if you have npm)

```bash
cd gravitytrain
npx --yes http-server -p 8080 -c-1
# or
npx --yes serve -l 8080
```

Then open `http://localhost:8080/`.

## Notes

- The page uses CesiumJS and imagery from public CDNs, so an internet connection is required.
- If you have a Cesium Ion token, open `index.html` and set the value of `ION_TOKEN` near the top of the script for world‑terrain and higher quality imagery.
- The experience auto‑runs a single progress simulation on load and shows a promotional banner at completion. Closing the banner resets the progress to the default 10%.


