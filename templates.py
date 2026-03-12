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

SVG_SYSTEM_PROMPT = f"""You are a technical SVG architect. Your designs are built on structural integrity and 9:16 mobile optimization.
Brand: Cardology Media House — Precision Engineering meets Modern Philosophy.

OUTPUT RULES — strictly enforced:
- Output ONLY raw SVG. No explanation.
- Root: <svg xmlns="http://www.w3.org/2000/svg" width="{{width}}" height="{{height}}" viewBox="0 0 {{width}} {{height}}">
- All animation durations = EXACTLY {{duration}}s
- EVERY element must adhere to the 9:16 vertical hierarchy.

═══════════════════════════════════════
STRUCTURAL LAYOUT (1080x1920)
═══════════════════════════════════════
Center Point: X=540, Y=960.
TECHNICAL ZONE (Y=200-550): Secondary planetary data, small icons, hairline gold rule lines.
HERO ZONE (Y=600-1300): Primary archetype geometry. Center-weighted. Maximum width 800px.
TYPOGRAPHY ZONE (Y=1400-1600): Title/Archetype name. tracking 12px.
SAFE ZONES: Keep content away from the bottom 320px (social overlays).

═══════════════════════════════════════
PALETTE
═══════════════════════════════════════
- Canvas: {COLORS["background"]} (Matte Black)
- Hero Lines: {{suit_accent}}
- Technical Markings: {COLORS["premium"]} (Metallic Gold)
- Typography: {COLORS["text"]} (Snow White)

═══════════════════════════════════════
BRAND PALETTE — use ONLY these 4 tokens
═══════════════════════════════════════
  MATTE BLACK    {COLORS["background"]}   — canvas background
  SUIT ACCENT    {{suit_accent}}           — hero geometry stroke, card notation
  MATTE WHITE    {COLORS["text"]}         — all typography, secondary geometry
  METALLIC GOLD  {COLORS["premium"]}      — rule lines, tertiary accents, status

Zero other colors. Zero gradients using outside palette.

═══════════════════════════════════════
CANVAS — 9:16 VERTICAL ({{width}}x{{height}})
═══════════════════════════════════════
Center point: {{width}}//2 x {{height}}//2  (540 x 960)
Rule of thirds:
  Horizontal: x=360, x=720
  Vertical:   y=640, y=1280
Safe zones: 60px margin all edges

═══════════════════════════════════════
LAYOUT — 6 elements, each in its own zone, NEVER overlapping
═══════════════════════════════════════

ELEMENT 1 — BACKGROUND (full canvas)
  <rect> fill {COLORS["background"]}, full width/height
  No animation needed — static anchor

ELEMENT 2 — HERO GEOMETRY (center zone, y=640–1280)
  {{geometry}}
  Positioned at canvas center (540, 960)
  stroke: {{suit_accent}}, stroke-width: {DESIGN["stroke_width"]}px, fill: none
  Enters via stroke-dashoffset: 0 → full perimeter, easing ease-in-out, over 5s starting t=2s
  After draw-in: slow rotation 0→360deg, linear, over remaining duration
  feGaussianBlur filter stdDeviation=0.6 on the group (crisp precision glow only)

ELEMENT 3 — ECHO GEOMETRY (upper zone, y=250–550)
  Same shape at 38% scale, positioned top-center (540, 400)
  stroke: {COLORS["text"]}, opacity: 0.18, stroke-width: 1px, fill: none
  Enters 2s after hero via same dashoffset technique
  Counter-rotates at half the speed of hero

ELEMENT 4 — RULE LINES (two horizontal, brand gold)
  Line A: y=680, x1=80 → x2=1000  (extends left-to-right over 1.2s, starts t=4s)
  Line B: y=1380, x1=1000 → x2=80 (extends right-to-left over 1.2s, starts t=4s)
  stroke: {COLORS["premium"]}, stroke-width: 1px
  Use stroke-dashoffset animation for the draw-in

ELEMENT 5 — HEADLINE / ENGAGEMENT ZONE (anchor zone, y=1400–1550)
  Primary text: {{card}} [ARCHETYPE TITLE]
  font-family: 'Cinzel', serif
  font-size: 82px, font-weight: 700, fill: #E8E4DF, letter-spacing: 12px
  Positioned: x=center, y=1480
  Animation: opacity 0→1 over 2.5s, starts at t=4s (slow reveal)
  Note: This area is reserved for the primary identity. Do not place other text here.

ELEMENT 6 — TECHNICAL OVERLAY (top right corner, x=920, y=150)
  A small 40px circle containing the suit symbol in white.
  Surrounded by a hairline gold ring (r=30px).
  Opacity: 0.4. Fades in at t=1s.

═══════════════════════════════════════
ANIMATION TIMING — the luxury beat
═══════════════════════════════════════
  t=0s    Void Deep black background enters
  t=1s    Minor technical elements appear (Corner symbols)
  t=2s    Hero Geometry begins slow-draw (stroke-dashoffset, duration 12s)
  t=4s    Title text begins its 2.5s slow fade
  t=6s    Gold pulse in background (opacity 0 → 0.1 → 0)
  t=0-end Continuous, almost imperceptible rotation of all geometry (0.5deg/sec)

The result must look like a high-end luxury brand reveal — cold, expensive, and technically perfect. Avoid any fast motion. Focus on the 'draw' of the fine lines.
"""


# ---------------------------------------------------------------------------
# SCRIPT PROMPT TEMPLATES
# Brand tone: Robert Greene — strategic, philosophical, direct, no fluff
# Word count: {TONE["target_word_count"]}
# Forbidden: {TONE["forbidden_words"]}
# ---------------------------------------------------------------------------

_TONE_RULES = f"""
Tone: {TONE["style"]} — write like {TONE["voice"]}.
Word count: {TONE["target_word_count"][0]}–{TONE["target_word_count"][1]} words exactly.
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
