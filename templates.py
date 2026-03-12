"""
Template library — wired to brand_config.py as single source of truth.
All colors, fonts, tone, and word counts come from brand_config.
Layout tuned for 9:16 vertical (1080x1920).
"""
from brand_config import COLORS, FONTS, DESIGN, TONE, get_suit_color

# ---------------------------------------------------------------------------
# Number → geometry mapping (card number drives the hero shape)
# ---------------------------------------------------------------------------

NUMBER_GEOMETRY = {
    1:  "a single perfect circle (r=320px) centered at canvas midpoint — unity, the origin",
    2:  "two vertical lines (2px wide, 480px tall) spaced 120px apart, mirrored from center — duality, opposition",
    3:  "an equilateral triangle (side 520px), apex up, centered — trinity, synthesis",
    4:  "a perfect square (420px sides) with both diagonals drawn — foundation, the four directions",
    5:  "a regular pentagon (circumradius 300px), one vertex up, centered — change, the five-pointed star inscribed inside",
    6:  "a regular hexagon (circumradius 300px), flat-top, centered — harmony, the honeycomb",
    7:  "a heptagram: two overlapping regular heptagons offset by 25.7deg, circumradius 280px — mystery, the unseen",
    8:  "a regular octagon (circumradius 300px) with a second octagon rotated 22.5deg inside it — power, the infinite loop",
    9:  "three concentric equilateral triangles rotated 40deg from each other, radii 300/200/100px — completion, the triple triad",
    10: "a circle (r=240px) divided into 10 equal sectors by fine gold lines — mastery, wholeness",
    11: "an 11-pointed star built from thin overlapping gold segments and a central white void — complexity, sovereignty",
    12: "a 12-segment clock-face circle (r=240px) with hairline-thin hour marks and no numerals — temporal cycles, cold wisdom",
    13: "a technical crown geometry: a 500px wide base bar supporting 5 precise triangular spires — supreme authority",
}


def get_geometry(card: str) -> str:
    face_map = {"A": 1, "J": 11, "Q": 12, "K": 13}
    num_str = card[:-1]
    num = face_map.get(num_str)
    if num is None:
        try:
            num = int(num_str)
        except ValueError:
            num = 1
    return NUMBER_GEOMETRY.get(num, NUMBER_GEOMETRY[1])


def estimate_duration(script: str) -> float:
    """Target a luxurious 35-second baseline for high-impact social media."""
    return 35.0


def get_suit_accent(card: str) -> str:
    """Brand-compliant suit color via brand_config."""
    color = get_suit_color(card)
    # Black suits return text color (#E8E4DF) — swap to gold for visual contrast on dark bg
    if color == COLORS["text"]:
        return COLORS["premium"]   # Metallic Gold for ♣ and ♠
    return color  # Wine Red for ♥ and ♦


# ---------------------------------------------------------------------------
# SVG SYSTEM PROMPT — 9:16 layout, brand palette
# Injects: {width} {height} {duration} {geometry} {suit_accent} {card}
# ---------------------------------------------------------------------------
SVG_SYSTEM_PROMPT = f"""You are a technical SVG architect. Your designs are built on structural integrity, 9:16 mobile optimization, and "Sacred Technicality."
Brand: Cardology Media House — Precision Engineering meets Modern Philosophy.

OUTPUT RULES — strictly enforced:
- Output ONLY raw SVG. No explanation.
- Root: <svg xmlns="http://www.w3.org/2000/svg" width="{{width}}" height="{{height}}" viewBox="0 0 {{width}} {{height}}">
- All animation durations = EXACTLY {{duration}}s
- Visual Density: High. Use layers of technical noise and geometric schematics.

═══════════════════════════════════════
STRUCTURAL LAYOUT (1080x1920)
═══════════════════════════════════════
Center Point: X=540, Y=960.
PERIMETER CUSHION: 120px (Strict empty border on all edges).

ELEMENT 1: THE MATTE DEPTH
- Static background: {COLORS["background"]}.

ELEMENT 2: ORBITAL SCHEMATICS
- Three concentric hairline rings (r=320, 360, 480) centered at 540,960. (Shrank to fit cushion)
- Stroke: {COLORS["premium"]}, opacity 0.15, stroke-width 0.5px.
- Animation: Each ring rotates slowly (linear) in opposite directions.

ELEMENT 3: THE HERO GEOMETRY
- {{geometry}} at canvas center. Maximum width: 780px.
- Stroke: {{suit_accent}}, stroke-width: 2.5px.
- Entry: 'Draw-in' (stroke-dashoffset) over 3s.

ELEMENT 4: STATUS TEXT (ENHANCED & CENTERED)
- Technical data (Card / Archetype Type) positioned at Y=320 (Centered).
- font-family 'Outfit', font-size 28px, tracking 8px.
- This text is now larger and centered within the upper cushion area.

ELEMENT 5: EDITORIAL HEADLINE
- Archetype Name: {{card}} [TITLE] centered at Y=1520.
- tracking 12px, font-family 'Cinzel', font-size 68px (Shrank from 84px for cushion).
- Reveal: Y-translation (slide up) + Opacity fade, starting t=3s.

ELEMENT 7: TECHNICAL HAIRLINES
- Four diagonal hairlines corner-to-center (opacity 0.1).
- Stroke: {COLORS["text"]}, stroke-width 0.5px.

ELEMENT 8: THE TEMPORAL CASCADE (NEW)
- Tasteful "Solitaire Win" echo effect: A series of 7 high-precision "ghost" layers of the Hero Geometry.
- Placement: Each ghost is offset by 4px vertically and 2px horizontally from the one before it, creating a slight "stacking" trail.
- Stroke: {{suit_accent}}, opacity trailing from 0.12 down to 0.01.
- Animation: Sequential fade-in (0.1s delay between layers) starting at t=4s.
- This represents the "cascade of outcomes"—infinite results from a single blueprint.

═══════════════════════════════════════
ANIMATION TIMING — the luxury beat
═══════════════════════════════════════
  t=0s    Void Deep black background enters
  t=1s    Minor technical elements appear (Corner symbols)
  t=2s    Hero Geometry begins slow-draw (stroke-dashoffset, duration 12s)
  t=4s    Title text begins its 2.5s slow fade
  t=6s    Gold pulse in background (opacity 0 → 0.1 → 0)
  t=0-end Continuous, almost imperceptible rotation of all geometry (0.5deg/sec)

The result must look like a high-end luxury brand reveal — cold, expensive, and technically perfect. Focus on the dynamic interaction of the moving lines.
"""


# SCRIPT PROMPT TEMPLATES
# Brand tone: Robert Greene — strategic, philosophical, direct, no fluff
# Word count: Target 75-85 words for a 35-second reading.
# Forbidden: {TONE["forbidden_words"]}
# ---------------------------------------------------------------------------

_TONE_RULES = f"""
Tone: {TONE["style"]} — write like {TONE["voice"]}.
Word count: 75–85 words exactly (essential for 35s pacing).
Forbidden words: {", ".join(TONE["forbidden_words"])} — never use these.
- Second person. Direct. No hedging. No filler.
- Short declarative sentences. Each one lands.
- No names. No markdown. Pure spoken prose."""

SCRIPT_TEMPLATES = {

    "profile": """\
Write a 45-word spoken-word voiceover for the {card} — {title}.
{tone}

Card data:
- Who they are: {core_identity}
- Their gift: {gifts}
- Their challenge: {shadow}
- Their direction: {life_direction}

Structure — equal thirds:
1. GIFT: Open on the power and natural gift this archetype carries.
2. CHALLENGE: Name the one tension or pattern that holds them back — without dwelling.
3. REWARD: Close on the purpose and payoff when they step fully into it.

Each beat one sentence. End on possibility, not warning.
""",

    "lens": """\
Write a 45-word spoken-word voiceover for the {card} — {title}.
{tone}

Three states:
- Contracted: {under}
- Evolved: {sweet_spot}
- Inflated: {over}

Structure — equal thirds:
1. CHALLENGE: The contracted pattern — brief, precise, no judgment.
2. PURPOSE: The evolved center — where their real power lives.
3. REWARD: What becomes possible when they operate from the sweet spot.

Land hardest on the evolved state. End with forward momentum.
""",

    "spread": """\
Write a 45-word spoken-word solar spread reading voiceover.
{tone}

Birth card: {card} — {title}: {core_identity}
Planetary ruling card: {prc} — {prc_title}: {prc_identity}
This year's theme: {life_direction}

Structure — equal thirds:
1. GIFT: Who they are and what they carry into this year.
2. CHALLENGE: The one friction this year asks them to move through.
3. REWARD: What this year unlocks when they meet it fully.

Final line: the year's single invitation — forward-facing, not cautionary.
""",

    "marketing": """\
Write a 45-word spoken-word social media voiceover for the {card} archetype.
{tone}

Card: {card} — {title}
Identity: {core_identity}
Hook: {strategy}
CTA: {cta}

Structure:
1. HOOK: Intrigue them with who this archetype is at their best.
2. BRIDGE: Name the challenge that makes the gift meaningful.
3. CTA: The reward waiting on the other side — then the call to action.

Stop the scroll with possibility, not fear.
""",
}


def get_script_template(context: str) -> str:
    template = SCRIPT_TEMPLATES.get(context, SCRIPT_TEMPLATES["profile"])
    return template.replace("{tone}", _TONE_RULES)
