"""
Generate narration scripts from Card Blueprints data using Claude.

Script types:
  - profile      : birth card identity, gifts, shadow, life direction
  - three_lens   : under / sweet_spot / over for a card
  - position     : card meaning in a specific planetary position (mercury, venus, etc.)
  - spread       : full solar spread reading for a birthday + target date
"""
import json
import os
import anthropic
import config
from templates import get_script_template
from calculate_blueprint import get_harmonic_relationships
from context_engine import engine

# Load blueprint data once at import time
_DATA_PATH = os.path.join(os.path.dirname(__file__), "card_blueprints_data.min.json")
with open(_DATA_PATH) as f:
    BLUEPRINT = json.load(f)

CARD_DESCRIPTIONS = BLUEPRINT["card_descriptions"]
THREE_LENS = BLUEPRINT["three_lens"]
WEEKLY_MEANINGS = BLUEPRINT["weekly_card_meanings"]
PLANETARY_RULING = BLUEPRINT["planetary_ruling_cards"]
SOLAR_VALUES = BLUEPRINT["solar_values"]

from marketing_templates import MARKETING_HOOKS, CTA_VARIATIONS
import random

PLANETARY_POSITIONS = [
    "mercury", "venus", "mars", "jupiter",
    "saturn", "uranus", "neptune",
    "environment", "long_range", "pluto", "result"
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def card_from_birthday(month: int, day: int) -> str:
    """Return the birth card notation for a given month/day."""
    solar_val = 55 - (2 * month + day)
    if solar_val < 0:
        solar_val += 52
    if solar_val == 0:
        return "Joker"
    return SOLAR_VALUES["solar_to_card"][str(solar_val)]


def prc_from_birthday(month: int, day: int):
    """Return the planetary ruling card(s) for a given month/day."""
    key = f"{month}/{day}"
    val = PLANETARY_RULING.get(key, "Unknown")
    if isinstance(val, str) and "|" in val:
        return val.split("|")
    return [val] if isinstance(val, str) else val


def get_card_data(card: str) -> dict:
    """Pull all available data for a card into a single dict."""
    data = {}
    if card in CARD_DESCRIPTIONS:
        data["description"] = CARD_DESCRIPTIONS[card]
    if card in THREE_LENS:
        data["three_lens"] = THREE_LENS[card]
    if card in WEEKLY_MEANINGS:
        data["weekly_meanings"] = WEEKLY_MEANINGS[card]
    return data


# ---------------------------------------------------------------------------
# Script generation with Claude
# ---------------------------------------------------------------------------

def _call_claude(prompt: str, persona: str = "mystic_architect") -> str:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    system_prompt = engine.get_persona(persona)
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def script_profile(card: str, name: str = None, legacy: str = None) -> str:
    data = CARD_DESCRIPTIONS.get(card)
    if not data:
        raise ValueError(f"No description found for card: {card}")
    
    # Fetch harmonic data
    harmony = get_harmonic_relationships(card)
    resonance = harmony.get("resonance_type", "Evolving")
    mates = ", ".join(harmony.get("rank_mates", []))

    template = get_script_template("profile")
    context_str = f"Name: {name}\nLegacy: {legacy}\n" if name else ""
    prompt = context_str + template.format(
        card=card,
        title=data["t"],
        core_identity=data["id"],
        gifts=data["g"],
        shadow=data["s"],
        life_direction=data["ld"]
    )
    return _call_claude(prompt)


def script_three_lens(card: str, name: str = None, legacy: str = None) -> str:
    data = THREE_LENS.get(card)
    if not data:
        raise ValueError(f"No three_lens data for card: {card}")
    title = CARD_DESCRIPTIONS.get(card, {}).get("t", card)
    template = get_script_template("lens")
    context_str = f"Name: {name}\nLegacy: {legacy}\n" if name else ""
    prompt = context_str + template.format(
        card=card,
        title=title,
        under=data["under"],
        sweet_spot=data["sweet_spot"],
        over=data["over"],
        duration="15–20s",
    )
    return _call_claude(prompt)


def script_position(card: str, position: str) -> str:
    if position not in PLANETARY_POSITIONS:
        raise ValueError(f"Unknown position: {position}. Choose from: {PLANETARY_POSITIONS}")
    meanings = WEEKLY_MEANINGS.get(card)
    if not meanings:
        raise ValueError(f"No weekly meanings for card: {card}")
    meaning = meanings.get(position, "")
    title = CARD_DESCRIPTIONS.get(card, {}).get("t", card)
    prompt = (
        f"Write a punchy 35–50 word voiceover for {card} — {title} in the {position.upper()} position.\n\n"
        f"Meaning: {meaning}\n\n"
        f"Direct. Second person. No names. Short sentences. End on a clear statement."
    )
    return _call_claude(prompt)


def script_spread_summary(month: int, day: int, year_age: int, name: str = None, legacy: str = None) -> str:
    birth_card = card_from_birthday(month, day)
    prc = prc_from_birthday(month, day)
    prc_str = "/".join(prc) if isinstance(prc, list) else prc

    bc_data = CARD_DESCRIPTIONS.get(birth_card, {})
    prc_data = CARD_DESCRIPTIONS.get(prc_str.split("/")[0], {})

    template = get_script_template("spread")
    context_str = f"Name: {name}\nLegacy: {legacy}\n" if name else ""
    prompt = context_str + template.format(
        card=birth_card,
        title=bc_data.get("t", birth_card),
        core_identity=bc_data.get("id", ""),
        prc=prc_str,
        prc_title=prc_data.get("t", "Planetary Ruler"),
        prc_identity=prc_data.get("id", ""),
        life_direction=bc_data.get("ld", "")
    )
    return _call_claude(prompt)


def script_marketing(card: str, strategy: str = "pain_point", cta_type: str = "hard") -> str:
    data = CARD_DESCRIPTIONS.get(card)
    if not data:
        raise ValueError(f"No description found for card: {card}")
    
    template = get_script_template("marketing")
    
    # Select specific hook and CTA text
    hook_options = MARKETING_HOOKS.get(strategy, MARKETING_HOOKS["mystery"])
    hook_text = random.choice(hook_options).format(card=card)
    cta_text = CTA_VARIATIONS.get(cta_type, CTA_VARIATIONS["hard"])

    prompt = template.format(
        card=card,
        title=data.get("t", card),
        core_identity=data.get("id", ""),
        strategy=strategy,
        hook=hook_text,
        cta=cta_text
    )
    return _call_claude(prompt)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Card Blueprints narration scripts")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("profile", help="Birth card profile")
    p.add_argument("card", help="Card notation e.g. 'A♣' or 'K♥'")

    p = sub.add_parser("lens", help="Three psychological lenses")
    p.add_argument("card")

    p = sub.add_parser("position", help="Card in a planetary position")
    p.add_argument("card")
    p.add_argument("position", choices=PLANETARY_POSITIONS)

    p = sub.add_parser("spread", help="Full spread reading")
    p.add_argument("month", type=int)
    p.add_argument("day", type=int)
    p.add_argument("year_age", type=int, help="Spread year (age+1)")

    p = sub.add_parser("birthday", help="Lookup birth card from birthday")
    p.add_argument("month", type=int)
    p.add_argument("day", type=int)

    args = parser.parse_args()

    if args.cmd == "birthday":
        bc = card_from_birthday(args.month, args.day)
        prc = prc_from_birthday(args.month, args.day)
        print(f"Birth card: {bc} — {CARD_DESCRIPTIONS.get(bc, {}).get('title', '')}")
        print(f"PRC: {prc}")
    elif args.cmd == "profile":
        print(script_profile(args.card))
    elif args.cmd == "lens":
        print(script_three_lens(args.card))
    elif args.cmd == "position":
        print(script_position(args.card, args.position))
    elif args.cmd == "spread":
        print(script_spread_summary(args.month, args.day, args.year_age))
