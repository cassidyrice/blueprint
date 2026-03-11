#!/usr/bin/env python3
"""
Card Blueprints — Core Calculation Engine

Takes a birthday (month, day, year) and a target date, and outputs:
  1. Archetype: Birth Card + Planetary Ruling Card
  2. Yearly Navigation: Spread year, 14 period cards (7 per anchor)
  3. Active Period: Which planetary period the target date falls in
  4. Orbital Map: 14 cards as people/experiential markers

Usage:
  python3 calculate_blueprint.py <birth_month> <birth_day> <birth_year> [--target-date YYYY-MM-DD]
"""

import json
import os
import sys
import textwrap
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Data Loading — Single file: card_blueprints_data.json
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'card_blueprints_data.json')
# Global data store
_DATA = None

def init_data():
    global _DATA
    if _DATA is not None:
        return
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        _DATA = json.load(f)

def get_data(section):
    """Access a section of the master data file."""
    init_data()
    return _DATA[section]

# Convenience accessors
def get_spreads():
    return get_data('yearly_spreads')

def get_prc_data():
    return get_data('planetary_ruling_cards')

def get_card_descriptions():
    return get_data('card_descriptions')

def get_three_lens():
    return get_data('three_lens')

def get_weekly_meanings():
    return get_data('weekly_card_meanings')

# ---------------------------------------------------------------------------
# Card Notation Helpers
# ---------------------------------------------------------------------------

SOLAR_TO_CARD = {
    0: "Joker",
    1: "A♥", 2: "2♥", 3: "3♥", 4: "4♥", 5: "5♥", 6: "6♥", 7: "7♥",
    8: "8♥", 9: "9♥", 10: "10♥", 11: "J♥", 12: "Q♥", 13: "K♥",
    14: "A♣", 15: "2♣", 16: "3♣", 17: "4♣", 18: "5♣", 19: "6♣", 20: "7♣",
    21: "8♣", 22: "9♣", 23: "10♣", 24: "J♣", 25: "Q♣", 26: "K♣",
    27: "A♦", 28: "2♦", 29: "3♦", 30: "4♦", 31: "5♦", 32: "6♦", 33: "7♦",
    34: "8♦", 35: "9♦", 36: "10♦", 37: "J♦", 38: "Q♦", 39: "K♦",
    40: "A♠", 41: "2♠", 42: "3♠", 43: "4♠", 44: "5♠", 45: "6♠", 46: "7♠",
    47: "8♠", 48: "9♠", 49: "10♠", 50: "J♠", 51: "Q♠", 52: "K♠"
}

CARD_TO_SOLAR = {v: k for k, v in SOLAR_TO_CARD.items()}

SUIT_DOMAINS = {
    "♥": "Emotional Patterns",
    "♣": "Behavioral/Intellectual Patterns",
    "♦": "Value/Resource Patterns",
    "♠": "Lifestyle/Transformation Patterns"
}

PLANET_NAMES = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

PLANET_DOMAINS = {
    "Mercury": "mind, communication, perception",
    "Venus": "relationships, values, love",
    "Mars": "action, drive, assertion, conflict",
    "Jupiter": "expansion, growth, opportunity, abundance",
    "Saturn": "structure, limits, discipline, karma",
    "Uranus": "disruption, innovation, sudden change",
    "Neptune": "dissolution, dreams, spirituality, surrender"
}

# Grid layout constants
ROW_NAMES = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
COL_NAMES = ["Neptune", "Uranus", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"]

# ---------------------------------------------------------------------------
# Step 1: Calculate Birth Card
# ---------------------------------------------------------------------------

def calculate_solar_value(month, day):
    """Formula: 55 - (2 * month + day). Wraps via +52 if <= 0."""
    sv = 55 - (2 * month + day)
    if sv < 0:
        sv += 52
    # sv == 0 → Joker (Dec 31 only), left as 0
    return sv

def get_birth_card(month, day):
    """Returns (card_notation, solar_value)"""
    sv = calculate_solar_value(month, day)
    card = SOLAR_TO_CARD.get(sv, "Unknown")
    return card, sv

def get_card_suit(card):
    """Extract suit symbol from card notation."""
    for suit in ["♥", "♣", "♦", "♠"]:
        if suit in card:
            return suit
    return None

# ---------------------------------------------------------------------------
# Step 2: Get Planetary Ruling Card
# ---------------------------------------------------------------------------

def get_planetary_ruling_card(month, day):
    """Lookup from the date-based reference. Returns string or list for dual-PRC dates."""
    init_data()
    key = f"{month}/{day}"
    prc = get_prc_data().get(key)
    if prc is None:
        return None
    return prc  # string or list

# ---------------------------------------------------------------------------
# Step 3: Calculate Spread Year & Load Grid
# ---------------------------------------------------------------------------

def calculate_age(birth_month, birth_day, birth_year, target_date):
    """Calculate age as of target date. Birthday-to-birthday rule."""
    birthday_this_year = date(target_date.year, birth_month, birth_day)
    if target_date >= birthday_this_year:
        age = target_date.year - birth_year
    else:
        age = target_date.year - birth_year - 1
    return age

def calculate_spread_year(age):
    """Spread Year = age + 1, clamped to 0-90."""
    sy = age + 1
    return max(0, min(90, sy))

def load_spread(spread_year):
    """Load the 7x7 grid + crown line for a given spread year."""
    init_data()
    key = str(spread_year)
    if key not in get_spreads():
        raise ValueError(f"Spread year {spread_year} not found (valid: 0-90)")
    return get_spreads()[key]

# ---------------------------------------------------------------------------
# Step 4: Find Card in Grid & Extract 7 Period Cards
# ---------------------------------------------------------------------------

def find_card_in_grid(card, grid):
    """
    Find card position in the 7x7 grid.
    Returns (row, col) or None if not found.
    Row 0=Mercury ... Row 6=Neptune
    Col 0=Neptune ... Col 6=Mercury
    """
    for r in range(7):
        for c in range(7):
            if grid[r][c] == card:
                return (r, c)
    return None

def extract_cards(card, spread, count=9):
    """
    Extract cards by moving LEFT from the card's position in the grid.
    
    Rules:
    - Start at cell immediately LEFT of the card
    - Move left along the row
    - At left edge (col 0): drop down one row, restart at col 6
    - If on Neptune row (row 6) bottom-left: wrap to Crown Line
    - Crown Line traversal: Mars (index 2) → Jupiter (index 1) → Saturn (index 0)
    
    Default count=9 yields:
      Cards 1-7: Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune
      Card 8: Pluto
      Card 9: Result
    
    Returns list of card notations.
    """
    grid = spread["grid"]
    crown = spread["crown"]  # [Saturn, Jupiter, Mars] — indices 0, 1, 2
    
    pos = find_card_in_grid(card, grid)
    if pos is None:
        # Card might be in the Crown Line
        for ci, cc in enumerate(crown):
            if cc == card:
                return _extract_from_crown_start(ci, crown, grid, count)
        return None
    
    row, col = pos
    collected = []
    
    cur_row = row
    cur_col = col
    in_crown = False
    crown_index = None
    
    for _ in range(count):
        if not in_crown:
            cur_col -= 1
            if cur_col < 0:
                cur_row += 1
                cur_col = 6
                if cur_row > 6:
                    in_crown = True
                    crown_index = 2
                    collected.append(crown[crown_index])
                    continue
            collected.append(grid[cur_row][cur_col])
        else:
            crown_index -= 1
            if crown_index < 0:
                # Exhausted Crown Line — wrap to grid top-right
                in_crown = False
                cur_row = 0
                cur_col = 6
                collected.append(grid[cur_row][cur_col])
                continue
            collected.append(crown[crown_index])
    
    return collected

def extract_7_cards(card, spread):
    """Extract 7 planetary period cards (Mercury-Neptune). Convenience wrapper."""
    return extract_cards(card, spread, count=7)

def _extract_from_crown_start(crown_pos, crown, grid, count=9):
    """Extract cards when the anchor card is IN the Crown Line."""
    collected = []
    ci = crown_pos
    in_crown = True
    cur_row = 0
    cur_col = 7  # placeholder, set when entering grid
    
    for _ in range(count):
        if in_crown:
            ci -= 1
            if ci < 0:
                in_crown = False
                cur_row, cur_col = 0, 6
                collected.append(grid[cur_row][cur_col])
                continue
            collected.append(crown[ci])
        else:
            cur_col -= 1
            if cur_col < 0:
                cur_row += 1
                cur_col = 6
                if cur_row > 6:
                    # Re-enter crown from right
                    in_crown = True
                    ci = 2
                    collected.append(crown[ci])
                    continue
            collected.append(grid[cur_row][cur_col])
    
    return collected

# ---------------------------------------------------------------------------
# Step 5: Determine Active Planetary Period
# ---------------------------------------------------------------------------

def get_active_period(birth_month, birth_day, target_date):
    """
    Determine which planetary period the target date falls in.
    Each period = 52 days from birthday.
    
    Mercury: Days 1-52
    Venus: Days 53-104
    Mars: Days 105-156
    Jupiter: Days 157-208
    Saturn: Days 209-260
    Uranus: Days 261-312
    Neptune: Days 313-365/366
    
    Returns (planet_name, period_index_0based, day_in_year)
    """
    # Find most recent birthday before target date
    birthday_this_year = date(target_date.year, birth_month, birth_day)
    if target_date >= birthday_this_year:
        last_birthday = birthday_this_year
    else:
        last_birthday = date(target_date.year - 1, birth_month, birth_day)
    
    days_since_birthday = (target_date - last_birthday).days
    if days_since_birthday == 0:
        days_since_birthday = 1  # Birthday itself = day 1
    
    period_ranges = [
        ("Mercury", 1, 52),
        ("Venus", 53, 104),
        ("Mars", 105, 156),
        ("Jupiter", 157, 208),
        ("Saturn", 209, 260),
        ("Uranus", 261, 312),
        ("Neptune", 313, 366),
    ]
    
    for planet, start, end in period_ranges:
        if start <= days_since_birthday <= end:
            idx = PLANET_NAMES.index(planet)
            return planet, idx, days_since_birthday
    
    # Fallback (shouldn't reach)
    return "Neptune", 6, days_since_birthday

# ---------------------------------------------------------------------------
# Step 6: Long Range Card Calculation
# ---------------------------------------------------------------------------

def get_long_range_card(card, age):
    """
    Calculate the Long Range card for a given card at a given age.
    
    The Long Range system uses 7-year cycles:
    - Cycle 0 (ages 0-6): Extract 7 cards from Spread 1 (skip spirit spread at index 0)
    - Cycle 1 (ages 7-13): Extract 7 cards from Spread 2
    - Cycle N (ages N*7 to N*7+6): Extract 7 cards from Spread N+1
    
    The position within the cycle maps to the planetary period:
    - Position 0 = Mercury card, Position 1 = Venus, ... Position 6 = Neptune
    
    The spirit spread (JSON Year 0 / natural order) is skipped entirely.
    "Year 0" in Card Blueprints = Spread 1 in the data.
    
    Returns dict with {card, planet, cycle, spread_year, position} or None.
    """
    init_data()
    
    cycle = age // 7
    position = age % 7
    spread_key = str(cycle + 1)  # +1 to skip spirit spread
    
    if spread_key not in get_spreads():
        return None
    
    spread = get_spreads()[spread_key]
    cards_7 = extract_7_cards(card, spread)
    
    if cards_7 is None or position >= len(cards_7):
        return None
    
    lr_card = cards_7[position]
    planet = PLANET_NAMES[position]
    
    return {
        "card": lr_card,
        "planet": planet,
        "cycle": cycle,
        "spread_used": int(spread_key),
        "position_in_cycle": position,
        "all_7_in_cycle": cards_7
    }

# ---------------------------------------------------------------------------
# Step 7: Environment & Displacement Cards
# ---------------------------------------------------------------------------

def get_environment_displacement(card, spread_year):
    """
    Calculate Environment and Displacement cards for a given card at a given spread year.
    
    Environment: The card sitting at the birth card's SPIRIT SPREAD position 
    in the current year's spread. (Who moved into your permanent house.)
    
    Displacement: The card that normally sits (in the spirit spread) at 
    the birth card's CURRENT YEAR position. (The landlord where you moved to.)
    
    Returns dict with {environment, displacement} or None.
    """
    init_data()
    
    spirit = get_spreads()["0"]  # Spirit spread = Year 0 in JSON
    current = get_spreads().get(str(spread_year))
    if current is None:
        return None
    
    # Find card's spirit position
    spirit_pos = _find_card_position(card, spirit)
    if spirit_pos is None:
        return None
    
    # Find card's current year position
    current_pos = _find_card_position(card, current)
    if current_pos is None:
        return None
    
    # Environment: card at spirit position in current spread
    environment = _get_card_at_position(spirit_pos, current)
    
    # Displacement: card at current position in spirit spread
    displacement = _get_card_at_position(current_pos, spirit)
    
    return {
        "environment": environment,
        "displacement": displacement,
        "spirit_position": _format_position(spirit_pos),
        "current_position": _format_position(current_pos)
    }

def get_lifetime_karma(card):
    """
    Lifetime challenge and supporting karma cards.
    These are the Environment and Displacement from Year 1 (first spread 
    after the spirit spread). They define the permanent karma pair.
    
    Supporting Karma = Year 1 Environment (card at spirit position in Year 1)
    Challenge Karma = Year 1 Displacement (spirit card at Year 1 position)
    
    Returns dict with {challenge, supporting}.
    """
    init_data()
    
    result = get_environment_displacement(card, 1)
    if result is None:
        return None
    
    return {
        "challenge": result["displacement"],
        "supporting": result["environment"]
    }

def _find_card_position(card, spread):
    """Find a card's position in a spread. Returns ('grid', row, col) or ('crown', index)."""
    grid = spread["grid"]
    crown = spread["crown"]
    
    for r in range(7):
        for c in range(7):
            if grid[r][c] == card:
                return ("grid", r, c)
    
    for ci, cc in enumerate(crown):
        if cc == card:
            return ("crown", ci)
    
    return None

def _get_card_at_position(pos, spread):
    """Get the card at a given position in a spread."""
    if pos[0] == "grid":
        return spread["grid"][pos[1]][pos[2]]
    else:
        return spread["crown"][pos[1]]

def _format_position(pos):
    """Format a position for display."""
    if pos[0] == "grid":
        return {"type": "grid", "row": ROW_NAMES[pos[1]], "col": COL_NAMES[pos[2]]}
    else:
        labels = ["Saturn", "Jupiter", "Mars"]
        return {"type": "crown", "position": labels[pos[1]]}

# ---------------------------------------------------------------------------
# Step 8: Full Blueprint Calculation
# ---------------------------------------------------------------------------

def calculate_blueprint(birth_month, birth_day, birth_year, target_date=None):
    """
    Full Card Blueprint calculation.
    
    Returns a dict with:
      - archetype: {birth_card, planetary_ruling_card, solar_value}
      - spread_year, age
      - birth_card_periods: 7 cards with planet assignments
      - prc_periods: 7 cards with planet assignments  
      - active_period: {planet, index, day_in_year}
      - active_cards: {birth_card_active, prc_active}
    """
    if target_date is None:
        target_date = date.today()
    
    # Birth Card
    birth_card, solar_value = get_birth_card(birth_month, birth_day)
    
    # Planetary Ruling Card
    prc = get_planetary_ruling_card(birth_month, birth_day)
    # Handle dual-PRC dates: use first card as primary
    prc_primary = prc[0] if isinstance(prc, list) else prc
    prc_secondary = prc[1] if isinstance(prc, list) and len(prc) > 1 else None
    
    # Age & Spread Year
    age = calculate_age(birth_month, birth_day, birth_year, target_date)
    spread_year = calculate_spread_year(age)
    
    # Load spread
    spread = load_spread(spread_year)
    
    # Extract 9 cards for Birth Card (7 planets + Pluto + Result)
    bc_position = find_card_in_grid(birth_card, spread["grid"])
    bc_9cards = extract_cards(birth_card, spread, count=9)
    bc_7cards = bc_9cards[:7] if bc_9cards else None
    
    # Extract 9 cards for Planetary Ruling Card
    prc_position = find_card_in_grid(prc_primary, spread["grid"])
    prc_9cards = extract_cards(prc_primary, spread, count=9)
    prc_7cards = prc_9cards[:7] if prc_9cards else None
    
    # Active period
    active_planet, active_idx, day_in_year = get_active_period(birth_month, birth_day, target_date)
    
    # Build period card assignments
    bc_periods = {}
    prc_periods = {}
    for i, planet in enumerate(PLANET_NAMES):
        if bc_7cards and i < len(bc_7cards):
            bc_periods[planet] = bc_7cards[i]
        if prc_7cards and i < len(prc_7cards):
            prc_periods[planet] = prc_7cards[i]
    
    # Active cards
    bc_active = bc_periods.get(active_planet)
    prc_active = prc_periods.get(active_planet)
    
    # Grid positions (for debugging/display)
    bc_grid_pos = None
    if bc_position:
        bc_grid_pos = {"row": ROW_NAMES[bc_position[0]], "col": COL_NAMES[bc_position[1]]}
    
    prc_grid_pos = None
    if prc_position:
        prc_grid_pos = {"row": ROW_NAMES[prc_position[0]], "col": COL_NAMES[prc_position[1]]}
    
    # Long Range cards (for both BC and PRC)
    bc_long_range = get_long_range_card(birth_card, age)
    prc_long_range = get_long_range_card(prc_primary, age)
    
    # Environment & Displacement (yearly karma)
    bc_env_disp = get_environment_displacement(birth_card, spread_year)
    prc_env_disp = get_environment_displacement(prc_primary, spread_year)
    
    # Lifetime Karma
    bc_karma = get_lifetime_karma(birth_card)
    prc_karma = get_lifetime_karma(prc_primary)
    
    return {
        "archetype": {
            "birth_card": birth_card,
            "birth_card_solar_value": solar_value,
            "birth_card_suit_domain": SUIT_DOMAINS.get(get_card_suit(birth_card), "Unknown"),
            "planetary_ruling_card": prc_primary,
            "prc_secondary": prc_secondary,
            "purpose_statement": f"Emits {birth_card} energy, perceived by others as {prc_primary}"
        },
        "timing": {
            "birth_date": f"{birth_month}/{birth_day}/{birth_year}",
            "target_date": target_date.isoformat(),
            "age": age,
            "spread_year": spread_year,
            "crown_line": spread["crown"]
        },
        "birth_card_spread": {
            "anchor": birth_card,
            "grid_position": bc_grid_pos,
            "period_cards": bc_periods,
            "pluto": bc_9cards[7] if bc_9cards and len(bc_9cards) > 7 else None,
            "result": bc_9cards[8] if bc_9cards and len(bc_9cards) > 8 else None,
            "all_9": bc_9cards
        },
        "prc_spread": {
            "anchor": prc_primary,
            "grid_position": prc_grid_pos,
            "period_cards": prc_periods,
            "pluto": prc_9cards[7] if prc_9cards and len(prc_9cards) > 7 else None,
            "result": prc_9cards[8] if prc_9cards and len(prc_9cards) > 8 else None,
            "all_9": prc_9cards
        },
        "long_range": {
            "birth_card": bc_long_range,
            "planetary_ruling_card": prc_long_range
        },
        "environment_displacement": {
            "birth_card": bc_env_disp,
            "planetary_ruling_card": prc_env_disp
        },
        "lifetime_karma": {
            "birth_card": bc_karma,
            "planetary_ruling_card": prc_karma
        },
        "active_period": {
            "planet": active_planet,
            "planet_domain": PLANET_DOMAINS[active_planet],
            "period_index": active_idx,
            "day_in_personal_year": day_in_year,
            "birth_card_active": bc_active,
            "prc_active": prc_active
        },
        "navigation_summary": {
            "all_14_cards": list(set((bc_7cards or []) + (prc_7cards or []))),
            "bc_formula": f"{birth_card} + {bc_active} + {active_planet}" if bc_active else None,
            "prc_formula": f"{prc_primary} + {prc_active} + {active_planet}" if prc_active else None
        }
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_output(result):
    """Pretty-print the blueprint result."""
    a = result["archetype"]
    t = result["timing"]
    bc = result["birth_card_spread"]
    prc = result["prc_spread"]
    ap = result["active_period"]
    nav = result["navigation_summary"]
    
    desc = get_card_descriptions()
    weekly = get_weekly_meanings()
    
    print("=" * 70)
    print("CARD BLUEPRINT")
    print("=" * 70)
    
    print(f"\n--- ARCHETYPE ---")
    print(f"Birth Card:              {a['birth_card']} (Solar Value: {a['birth_card_solar_value']})")
    bc_desc = desc.get(a['birth_card'], {})
    if bc_desc:
        print(f"                         {bc_desc.get('title', '')}")
        print(textwrap.fill(bc_desc.get('core_identity', ''), width=70, initial_indent="                         ", subsequent_indent="                         "))
    print(f"                         Domain: {a['birth_card_suit_domain']}")
    
    print(f"Planetary Ruling Card:   {a['planetary_ruling_card']}")
    prc_desc = desc.get(a['planetary_ruling_card'], {})
    if prc_desc:
        print(f"                         {prc_desc.get('title', '')}")
        print(textwrap.fill(prc_desc.get('core_identity', ''), width=70, initial_indent="                         ", subsequent_indent="                         "))
    if a['prc_secondary']:
        print(f"  (Secondary PRC):       {a['prc_secondary']}")
    print(f"Purpose:                 {a['purpose_statement']}")
    
    print(f"\n--- TIMING ---")
    print(f"Birth Date:    {t['birth_date']}")
    print(f"Target Date:   {t['target_date']}")
    print(f"Age:           {t['age']}")
    print(f"Spread Year:   {t['spread_year']}")
    print(f"Crown Line:    {' | '.join(t['crown_line'])}")
    
    print(f"\n--- BIRTH CARD SPREAD ({bc['anchor']}) ---")
    if bc['grid_position']:
        print(f"Grid Position: Row={bc['grid_position']['row']}, Col={bc['grid_position']['col']}")
    print(f"7 Period Cards:")
    for planet in PLANET_NAMES:
        card = bc['period_cards'].get(planet, '?')
        marker = " ◄ ACTIVE" if planet == ap['planet'] else ""
        print(f"  {planet:10s} → {card}{marker}")
        if card in weekly and planet.lower() in weekly[card]:
            print(textwrap.fill(weekly[card][planet.lower()], width=70, initial_indent="               ", subsequent_indent="               "))
    
    p_card = bc.get('pluto', '?')
    print(f"  {'Pluto':10s} → {p_card}")
    if p_card in weekly and 'pluto' in weekly[p_card]:
        print(textwrap.fill(weekly[p_card]['pluto'], width=70, initial_indent="               ", subsequent_indent="               "))
        
    r_card = bc.get('result', '?')
    print(f"  {'Result':10s} → {r_card}")
    if r_card in weekly and 'result' in weekly[r_card]:
        print(textwrap.fill(weekly[r_card]['result'], width=70, initial_indent="               ", subsequent_indent="               "))
    
    print(f"\n--- PRC SPREAD ({prc['anchor']}) ---")
    if prc['grid_position']:
        print(f"Grid Position: Row={prc['grid_position']['row']}, Col={prc['grid_position']['col']}")
    print(f"7 Period Cards:")
    for planet in PLANET_NAMES:
        card = prc['period_cards'].get(planet, '?')
        marker = " ◄ ACTIVE" if planet == ap['planet'] else ""
        print(f"  {planet:10s} → {card}{marker}")
        if card in weekly and planet.lower() in weekly[card]:
            print(textwrap.fill(weekly[card][planet.lower()], width=70, initial_indent="               ", subsequent_indent="               "))
            
    p_card_prc = prc.get('pluto', '?')
    print(f"  {'Pluto':10s} → {p_card_prc}")
    if p_card_prc in weekly and 'pluto' in weekly[p_card_prc]:
        print(textwrap.fill(weekly[p_card_prc]['pluto'], width=70, initial_indent="               ", subsequent_indent="               "))
        
    r_card_prc = prc.get('result', '?')
    print(f"  {'Result':10s} → {r_card_prc}")
    if r_card_prc in weekly and 'result' in weekly[r_card_prc]:
        print(textwrap.fill(weekly[r_card_prc]['result'], width=70, initial_indent="               ", subsequent_indent="               "))
    
    print(f"\n--- ACTIVE PERIOD ---")
    print(f"Planet:        {ap['planet']} ({ap['planet_domain']})")
    print(f"Day in Year:   {ap['day_in_personal_year']}")
    print(f"BC Active:     {ap['birth_card_active']}")
    print(f"PRC Active:    {ap['prc_active']}")
    
    lr = result["long_range"]
    print(f"\n--- LONG RANGE ---")
    if lr["birth_card"]:
        bc_lr = lr["birth_card"]
        card = bc_lr['card']
        print(f"BC Long Range:   {card} (Cycle {bc_lr['cycle']}, Spread {bc_lr['spread_used']}, {bc_lr['planet']})")
        if card in weekly and 'long_range' in weekly[card]:
            print(textwrap.fill(weekly[card]['long_range'], width=70, initial_indent="                 ", subsequent_indent="                 "))
    if lr["planetary_ruling_card"]:
        prc_lr = lr["planetary_ruling_card"]
        card = prc_lr['card']
        print(f"PRC Long Range:  {card} (Cycle {prc_lr['cycle']}, Spread {prc_lr['spread_used']}, {prc_lr['planet']})")
        if card in weekly and 'long_range' in weekly[card]:
            print(textwrap.fill(weekly[card]['long_range'], width=70, initial_indent="                 ", subsequent_indent="                 "))
    
    ed = result["environment_displacement"]
    print(f"\n--- ENVIRONMENT & DISPLACEMENT ---")
    if ed["birth_card"]:
        env_card = ed['birth_card']['environment']
        print(f"BC Environment:  {env_card} (who moved into your house)")
        if env_card in weekly and 'environment' in weekly[env_card]:
             print(textwrap.fill(weekly[env_card]['environment'], width=70, initial_indent="                 ", subsequent_indent="                 "))
        print(f"BC Displacement: {ed['birth_card']['displacement']} (landlord where you moved)")
    if ed["planetary_ruling_card"]:
        env_card = ed['planetary_ruling_card']['environment']
        print(f"PRC Environment: {env_card}")
        if env_card in weekly and 'environment' in weekly[env_card]:
             print(textwrap.fill(weekly[env_card]['environment'], width=70, initial_indent="                 ", subsequent_indent="                 "))
        print(f"PRC Displacement:{ed['planetary_ruling_card']['displacement']}")
    
    karma = result["lifetime_karma"]
    print(f"\n--- LIFETIME KARMA ---")
    if karma["birth_card"]:
        print(f"BC Challenge:    {karma['birth_card']['challenge']}")
        print(f"BC Supporting:   {karma['birth_card']['supporting']}")
    if karma["planetary_ruling_card"]:
        print(f"PRC Challenge:   {karma['planetary_ruling_card']['challenge']}")
        print(f"PRC Supporting:  {karma['planetary_ruling_card']['supporting']}")
    
    print(f"\n--- NAVIGATION ---")
    print(f"BC Formula:    {nav['bc_formula']}")
    print(f"PRC Formula:   {nav['prc_formula']}")
    print(f"All 14 Cards:  {', '.join(sorted(nav['all_14_cards']))}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 calculate_blueprint.py <month> <day> <year> [--target-date YYYY-MM-DD]")
        sys.exit(1)
    
    bm = int(sys.argv[1])
    bd = int(sys.argv[2])
    by = int(sys.argv[3])
    
    td = date.today()
    if "--target-date" in sys.argv:
        idx = sys.argv.index("--target-date")
        td = date.fromisoformat(sys.argv[idx + 1])
    
    result = calculate_blueprint(bm, bd, by, td)
    format_output(result)
    
    # Also output JSON for programmatic use
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
