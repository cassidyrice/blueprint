#!/usr/bin/env python3
"""
SVG Video Pipeline — Card Blueprints Edition
---------------------------------------------
Generates an MP4 video from Card Blueprints data:
  1. Claude → narration script from card data
  2. ElevenLabs → voiceover audio (MP3)
  3. Claude → animated SVG (CSS keyframes, duration matched to audio)
  4. Playwright → PNG frame sequence
  5. ffmpeg → final MP4

Usage examples:
    # Birth card profile
    python pipeline.py profile "A♣"

    # Three psychological lenses
    python pipeline.py lens "K♥"

    # Card in a planetary position
    python pipeline.py position "7♦" venus

    # Full spread reading
    python pipeline.py spread 3 15 27

    # Raw script (skip card lookup)
    python pipeline.py script "Your narration text here."
"""
import argparse
import os
import sys

import config
from generate_script import (
    script_profile,
    script_three_lens,
    script_position,
    script_spread_summary,
    script_marketing,
    card_from_birthday,
    PLANETARY_POSITIONS,
    CARD_DESCRIPTIONS,
)
from voiceover import generate_audio
from generate_svg import generate_svg, estimate_duration
from render_frames import render_frames_sync
from compose import compose_video


def run(script: str, card: str = "A♣", output_path: str = config.VIDEO_PATH) -> str:
    """Run the full pipeline for a given script and card. Returns the output video path."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    print(f"\nScript ({len(script.split())} words):\n{script}\n")

    print("=== Step 1: Generating voiceover ===")
    audio_duration = generate_audio(script, config.AUDIO_PATH)

    # Add a 2-second "handicap" (handshake) to the end for a contemplative tail
    visual_duration = audio_duration + 2.0

    print(f"\n=== Step 2: Generating animated SVG ({visual_duration:.2f}s) ===")
    svg_content = generate_svg(script, card=card, duration=visual_duration)

    svg_path = os.path.join(config.OUTPUT_DIR, "animation.svg")
    with open(svg_path, "w") as f:
        f.write(svg_content)
    print(f"SVG saved: {svg_path} ({len(svg_content)} chars)")

    print(f"\n=== Step 3: Rendering {int(visual_duration * config.FPS)} frames ===")
    render_frames_sync(svg_content, duration=visual_duration)

    print("\n=== Step 4: Composing final video ===")
    compose_video(
        frames_dir=config.FRAMES_DIR,
        audio_path=config.AUDIO_PATH,
        output_path=output_path,
    )

    print(f"\nDone! Video: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Card Blueprints SVG video pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--output", default=config.VIDEO_PATH, help="Output MP4 path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Raw script
    p = sub.add_parser("script", help="Use a raw narration script")
    p.add_argument("text", help="Narration text")

    # Birth card profile
    p = sub.add_parser("profile", help="Birth card identity profile")
    p.add_argument("card", help="Card notation e.g. A♣  K♥  7♦")

    # Three lenses
    p = sub.add_parser("lens", help="Three psychological lenses (under/sweet_spot/over)")
    p.add_argument("card")

    # Planetary position
    p = sub.add_parser("position", help="Card in a planetary position")
    p.add_argument("card")
    p.add_argument("position", choices=PLANETARY_POSITIONS)

    # Spread reading
    p = sub.add_parser("spread", help="Solar spread reading (month day year_age)")
    p.add_argument("month", type=int, help="Birth month (1-12)")
    p.add_argument("day", type=int, help="Birth day (1-31)")
    p.add_argument("year_age", type=int, help="Spread year number (age + 1)")

    # Marketing hook
    p = sub.add_parser("marketing", help="Generate a high-conversion marketing video")
    p.add_argument("card", help="Card notation e.g. A♣")
    p.add_argument("--strategy", choices=["pain_point", "power_play", "mystery"], default="pain_point")
    p.add_argument("--cta", choices=["soft", "hard", "urgent"], default="hard")

    args = parser.parse_args()

    print("=== Step 0: Generating script from card data ===")

    if args.cmd == "script":
        script = args.text

    elif args.cmd == "profile":
        print(f"Card: {args.card} — {CARD_DESCRIPTIONS.get(args.card, {}).get('title', '')}")
        script = script_profile(args.card)

    elif args.cmd == "lens":
        print(f"Card: {args.card} (three lenses)")
        script = script_three_lens(args.card)

    elif args.cmd == "position":
        print(f"Card: {args.card} in {args.position.upper()} position")
        script = script_position(args.card, args.position)

    elif args.cmd == "spread":
        bc = card_from_birthday(args.month, args.day)
        print(f"Birth date: {args.month}/{args.day} → {bc}, Year {args.year_age}")
        script = script_spread_summary(args.month, args.day, args.year_age)

    elif args.cmd == "marketing":
        print(f"Marketing Video: {args.card} (Strategy: {args.strategy}, CTA: {args.cta})")
        script = script_marketing(args.card, strategy=args.strategy, cta_type=args.cta)

    if not script:
        print("Error: empty script.", file=sys.stderr)
        sys.exit(1)

    run(script, output_path=args.output)


if __name__ == "__main__":
    main()
