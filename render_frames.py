"""
Render an animated SVG to a sequence of PNG frames using Playwright.
Uses the Web Animations API to seek each animation to exact frame times,
ensuring frame-perfect capture regardless of machine speed.
"""
import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright
import config


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background: #000;
  }}
  svg {{
    display: block;
    width: {width}px;
    height: {height}px;
  }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""


SEEK_SCRIPT = """
(timeMs) => {
    const anims = document.getAnimations();
    anims.forEach(a => {
        try {
            a.pause();
            a.currentTime = timeMs;
        } catch(e) {}
    });
}
"""


async def render_frames(
    svg_content: str,
    duration: float,
    frames_dir: str = config.FRAMES_DIR,
) -> int:
    """
    Render the animated SVG to PNG frames.
    Returns the number of frames rendered.
    """
    frames_path = Path(frames_dir)
    if frames_path.exists():
        shutil.rmtree(frames_path)
    frames_path.mkdir(parents=True, exist_ok=True)

    html = HTML_TEMPLATE.format(
        width=config.WIDTH,
        height=config.HEIGHT,
        svg_content=svg_content,
    )

    total_frames = int(duration * config.FPS)
    print(f"Rendering {total_frames} frames at {config.FPS}fps ({duration:.2f}s)...")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(
            viewport={"width": config.WIDTH, "height": config.HEIGHT}
        )

        await page.set_content(html, wait_until="networkidle")

        # Extract animation handles once
        for frame_num in range(total_frames):
            time_ms = (frame_num / config.FPS) * 1000
            
            # Efficient seek and capture
            # We pause them in JS, but allow them in Playwright so the compositor updates
            count = await page.evaluate(f"""
                (t) => {{
                    const anims = document.getAnimations();
                    anims.forEach(a => {{
                        a.pause();
                        a.currentTime = t;
                    }});
                    return anims.length;
                }}
            """, time_ms)

            if frame_num == 0:
                print(f"  Debug: Found {count} animations in SVG.")

            frame_path = frames_path / f"{frame_num:05d}.png"
            # Set animations to 'allow' so the compositor actually renders our manual currentTime change
            await page.screenshot(path=str(frame_path), type="png", animations="allow")

            if frame_num % (config.FPS * 2) == 0:
                print(f"  Progress: {frame_num}/{total_frames} frames ({frame_num/total_frames*100:.1f}%)")

        await browser.close()

    print(f"Rendered {total_frames} frames to {frames_dir}/")
    return total_frames


def render_frames_sync(svg_content: str, duration: float, frames_dir: str = config.FRAMES_DIR) -> int:
    return asyncio.run(render_frames(svg_content, duration, frames_dir))


if __name__ == "__main__":
    with open("output/test.svg") as f:
        svg = f.read()
    count = render_frames_sync(svg, duration=5.0)
    print(f"Done: {count} frames")
