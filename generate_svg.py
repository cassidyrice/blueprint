"""
Generate an animated SVG using Claude based on a narration script + card context.
Uses the minimalist matte palette and number-based geometry from templates.py.
"""
import anthropic
import config
from templates import SVG_SYSTEM_PROMPT, get_geometry, get_suit_accent
from context_engine import engine


def estimate_duration(script: str) -> float:
    """Estimate audio duration from word count (~120 wpm at 0.79 speed)."""
    words = len(script.split())
    duration = (words / 120) * 60
    return max(15.0, min(35.0, duration))


def generate_svg(script: str, card: str = "A♣", duration=None) -> str:
    """
    Call Claude to generate an animated SVG for the given script and card.
    Returns the raw SVG string.
    """
    if duration is None:
        duration = estimate_duration(script)

    geometry = get_geometry(card)
    suit_accent = get_suit_accent(card)

    system = SVG_SYSTEM_PROMPT.format(
        width=config.WIDTH,
        height=config.HEIGHT,
        duration=round(duration, 2),
        geometry=geometry,
        suit_accent=suit_accent,
        card=card,
    )

    prompt = (
        f"Create a precision high-luxury animated SVG for this card reading.\n\n"
        f"Card: {card}\n"
        f"Duration: exactly {round(duration, 2)} seconds\n"
        f"Hero geometry: {geometry}\n"
        f"Palette: matte black #0D0D0D / wine red {suit_accent} / matte white #E8E4DF / metallic gold #C5A059\n\n"
        f"Narration (use key phrases as animated text — concise, uppercase):\n{script}\n\n"
        f"Requirements:\n"
        f"- Strict 4-color palette only\n"
        f"- Elements never overlap — each in its own spatial zone\n"
        f"- Geometric precision — clean lines, exact positioning\n"
        f"- Slow deliberate animation timing\n"
        f"- Hero geometry must visually reference the card number\n\n"
        f"Start directly with <svg"
    )

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    system_persona = engine.get_persona("visual_designer")
    full_system = f"{system_persona}\n\nTECHNICAL REFERENCE:\n{system}"

    # Use modern Haiku for ultra-fast, high-token SVG generation
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=16000,
        system=full_system,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        final = stream.get_final_message()

    raw = "".join(b.text for b in final.content if b.type == "text").strip()

    if not raw:
        raise RuntimeError("SVG generation returned empty — check template formatting.")

    # Strip markdown fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # Find SVG start
    idx = raw.find("<svg")
    if idx == -1:
        raise RuntimeError(f"No <svg tag in output. Got: {raw[:300]}")

    return raw[idx:]


if __name__ == "__main__":
    import os
    test_script = "You are the mind that refuses to stay still. Your freedom is your gift. Your focus is your frontier."
    svg = generate_svg(test_script, card="5♣")
    os.makedirs("output", exist_ok=True)
    with open("output/test.svg", "w") as f:
        f.write(svg)
    print(f"SVG written ({len(svg)} chars)")
