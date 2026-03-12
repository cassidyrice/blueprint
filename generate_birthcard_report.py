#!/usr/bin/env python3
"""
generate_birthcard_report.py — Generates a premium, multi-page PDF birthcard report.
Combines core archetype data, lifetime karma, and the current yearly spread.

Usage:
    python3 generate_birthcard_report.py <month> <day> <year> [--target-date YYYY-MM-DD] [--output filename.pdf]
"""

import json
import sys
import os
from datetime import date, datetime
from pathlib import Path

# Import the calculation engine
import calculate_blueprint
from calculate_blueprint import (
    calculate_blueprint as calc_blueprint, 
    init_data, 
    SOLAR_TO_CARD, 
    PLANET_NAMES,
    PLANET_DOMAINS,
    get_card_suit
)

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except Exception:
    HAS_WEASYPRINT = False

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

PLANET_COLORS = {
    "Mercury": "#6babde",
    "Venus": "#de6baa",
    "Mars": "#de6b6b",
    "Jupiter": "#a06bde",
    "Saturn": "#999999",
    "Uranus": "#4bbb7a",
    "Neptune": "#6baede",
    "Pluto": "#333333",
    "Result": "#cccc00"
}

# ---------------------------------------------------------------------------
from brand_config import COLORS, FONTS, DESIGN

# HTML Template Components
# ---------------------------------------------------------------------------

CSS_TEMPLATE = """
@page {
    size: letter;
    margin: 0;
}

:root {
    --primary: BACK_COLOR;
    --accent: GOLD_COLOR;
    --premium: PREM_COLOR;
    --text: TEXT_COLOR;
    --text-muted: #888;
    --bg-dark: BACK_COLOR;
    --border: #333;
    --card-red: RED_COLOR;
    --card-black: TEXT_COLOR;
}

* { box-sizing: border-box; }

body {
    font-family: 'Georgia', serif;
    color: var(--text);
    background: var(--bg-dark);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

.page {
    width: 8.5in;
    height: 11in;
    position: relative;
    page-break-after: always;
    background: var(--bg-dark);
    padding: 0.75in 0.85in;
    display: flex;
    flex-direction: column;
}

/* Header / Footer */
.header-rule {
    height: 1px;
    background: linear-gradient(to right, var(--accent), transparent);
    margin: 10px 0 30px;
}

.footer {
    position: absolute;
    bottom: 0.5in;
    left: 0.85in;
    right: 0.85in;
    display: flex;
    justify-content: space-between;
    font-family: 'Helvetica', sans-serif;
    font-size: 10px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 8px;
}

/* Typography - Text First */
h1 { 
    font-family: 'Helvetica', sans-serif;
    font-size: 38px; 
    font-weight: 800; 
    color: var(--premium); 
    margin: 0; 
    letter-spacing: -0.5px;
    text-transform: uppercase;
}

h2 { 
    font-family: 'Helvetica', sans-serif;
    font-size: 18px; 
    font-weight: 700; 
    color: var(--accent); 
    margin: 30px 0 10px; 
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 2px solid var(--border);
    display: inline-block;
}

h3 { 
    font-family: 'Helvetica', sans-serif;
    font-size: 15px; 
    font-weight: 700; 
    color: var(--text); 
    margin: 20px 0 5px;
}

.subtitle { 
    font-family: 'Helvetica', sans-serif;
    font-size: 11px; 
    color: var(--accent); 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-weight: 700;
}

/* The "Report" Look */
.lead-in {
    font-size: 18px;
    font-style: italic;
    color: var(--text-muted);
    border-left: 4px solid var(--accent);
    padding-left: 20px;
    margin: 20px 0;
}

.paragraph {
    margin-bottom: 15px;
    text-align: justify;
}

/* Compact Data Components - No overlapping */
.data-row {
    display: flex;
    gap: 20px;
    margin: 15px 0;
    align-items: flex-start;
}

.card-inline {
    width: 40px;
    height: 56px;
    border: 1px solid var(--border);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    background: #111;
    flex-shrink: 0;
    font-family: 'Helvetica', sans-serif;
}
.card-inline.red { color: var(--card-red); }
.card-inline.black { color: var(--card-black); }

/* Grid specific - ensuring it fits */
.spread-container {
    margin: 20px 0;
    display: flex;
    justify-content: space-between;
    gap: 30px;
}

.spread-table {
    border-collapse: collapse;
    font-family: 'Helvetica', sans-serif;
}

.mini-card {
    width: 44px;
    height: 60px;
    border: 1px solid #333;
    border-radius: 3px;
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #111;
    position: relative;
}
.mini-card.red { color: var(--card-red); }

.highlight-ring {
    position: absolute;
    top: -3px; right: -3px;
    width: 8px; height: 8px;
    border-radius: 50%;
    border: 1.5px solid #000;
    box-shadow: 0 0 2px rgba(0,0,0,0.5);
}

.col-label { font-size: 8px; color: #666; text-align: center; text-transform: uppercase; padding-bottom: 2px; }
.row-label { font-size: 8px; color: #666; text-align: right; padding-right: 5px; text-transform: uppercase; }

/* Interpretation Blocks - Clean text layout */
.interp-section {
    margin-top: 10px;
}

.interp-item {
    margin-bottom: 20px;
    break-inside: avoid;
}

.interp-head {
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 5px;
    margin-bottom: 8px;
}

.role-tag {
    font-family: 'Helvetica', sans-serif;
    font-size: 10px;
    font-weight: 800;
    color: white;
    background: var(--card-black);
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
}

.item-card-text {
    font-family: 'Helvetica', sans-serif;
    font-weight: 800;
    font-size: 16px;
}

.item-title {
    font-family: 'Helvetica', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--accent);
}
"""

CSS = (CSS_TEMPLATE.replace("BACK_COLOR", COLORS["background"])
                  .replace("GOLD_COLOR", COLORS["secondary"])
                  .replace("PREM_COLOR", COLORS["premium"])
                  .replace("TEXT_COLOR", COLORS["text"])
                  .replace("RED_COLOR", COLORS["accent_warm"]))

def get_card_html(card, role_color=None, is_mini=False):
    if not card: return ""
    color_class = "red" if "♥" in card or "♦" in card else "black"
    ring = f'<div class="highlight-ring" style="background: {role_color};"></div>' if role_color else ""
    tag_class = "mini-card" if is_mini else "card-inline"
    return f'<div class="{tag_class} {color_class}">{ring}{card}</div>'

def generate_report_html(result):
    archetype = result["archetype"]
    timing = result["timing"]
    bc_spread = result["birth_card_spread"]
    active = result["active_period"]
    karma = result["lifetime_karma"]
    lr = result["long_range"]
    env_disp = result["environment_displacement"]

    init_data()
    descriptions = calculate_blueprint._DATA.get("card_descriptions", {})
    meanings = calculate_blueprint._DATA.get("weekly_card_meanings", {})
    
    bc_desc = descriptions.get(archetype["birth_card"], {})
    prc_desc = descriptions.get(archetype["planetary_ruling_card"], {})
    
    # Grid Highlights
    hmap = {}
    for planet in reversed(PLANET_NAMES):
        card = bc_spread["period_cards"].get(planet)
        if card: hmap[card] = PLANET_COLORS[planet]
    
    if env_disp["birth_card"]:
        hmap[env_disp["birth_card"]["environment"]] = "#1dd1a1" # Environment
        hmap[env_disp["birth_card"]["displacement"]] = "#ff9f43" # Displacement
    
    if lr["birth_card"]:
        hmap[lr["birth_card"]["card"]] = "#ff9f43" # Long Range
        
    hmap[bc_spread["pluto"]] = PLANET_COLORS["Pluto"]
    hmap[bc_spread["result"]] = PLANET_COLORS["Result"]
    hmap[archetype["planetary_ruling_card"]] = "#54a0ff" # PRC
    hmap[archetype["birth_card"]] = "#feca57" # Birth Card

    def build_grid_html(grid):
        col_labels = ["Nept", "Uran", "Satn", "Jupt", "Mars", "Venu", "Merc"]
        row_labels = ["Merc", "Venu", "Mars", "Jupt", "Satn", "Uran", "Nept"]
        html = '<table class="spread-table">'
        html += '<thead><tr><th></th>'
        for col in col_labels:
            html += f'<th class="col-label">{col}</th>'
        html += '</tr></thead><tbody>'
        for r in range(7):
            row = grid[r*7 : (r+1)*7]
            html += f'<tr><td class="row-label">{row_labels[r]}</td>'
            for card in row:
                color = hmap.get(card)
                html += f'<td>{get_card_html(card, role_color=color, is_mini=True)}</td>'
            html += '</tr>'
        html += '</tbody></table>'
        return html

    now_str = datetime.now().strftime("%B %d, %Y")
    pages = []
    
    # --- PAGE 1: Identity & Archetype ---
    p1 = []
    p1.append('<div class="page">')
    p1.append('    <div class="subtitle">The Blueprint Report</div>')
    p1.append(f'    <h1>Birth Archetype: {archetype["birth_card"]}</h1>')
    p1.append('    <div class="header-rule"></div>')
    p1.append('    <div class="lead-in">')
    p1.append(f'        "Your soul chose the signature of the {archetype["birth_card"]} to navigate this lifetime—a pattern of {archetype["birth_card_suit_domain"].lower()}."')
    p1.append('    </div>')
    p1.append('    <h2>I. Core Identity</h2>')
    p1.append('    <div class="data-row">')
    p1.append(f'        {get_card_html(archetype["birth_card"])}')
    p1.append('        <div class="paragraph">')
    p1.append(f'            <strong>{bc_desc.get("t", "Archetype")}</strong><br>')
    p1.append(f'            {bc_desc.get("id", "")}')
    p1.append('        </div>')
    p1.append('    </div>')
    p1.append('    <div class="data-row">')
    p1.append(f'        {get_card_html(archetype["planetary_ruling_card"])}')
    p1.append('        <div class="paragraph">')
    p1.append(f'            <strong>Perception: {prc_desc.get("t", "Planetary Ruler")}</strong><br>')
    p1.append(f'            While the {archetype["birth_card"]} is your internal engine, others experience you through the lens of the {archetype["planetary_ruling_card"]}. ')
    p1.append('            This is your professional and social "ruling" presence.')
    p1.append('        </div>')
    p1.append('    </div>')
    p1.append('    <h2>II. The Karma Pair</h2>')
    p1.append('    <p class="paragraph">')
    p1.append('        Every lifetime has a specific tension—a challenge card and a supporting strength. This is your permanent "Soul Blueprint."')
    p1.append('    </p>')
    p1.append('    <div class="data-row">')
    p1.append('        <div style="display:flex; gap:10px;">')
    p1.append('            <div style="text-align:center;">')
    p1.append(f'                {get_card_html(karma["birth_card"]["challenge"])}')
    p1.append('                <div style="font-size:9px; font-weight:700; margin-top:4px;">CHALLENGE</div>')
    p1.append('            </div>')
    p1.append('            <div style="text-align:center;">')
    p1.append(f'                {get_card_html(karma["birth_card"]["supporting"])}')
    p1.append('                <div style="font-size:9px; font-weight:700; margin-top:4px;">SUPPORT</div>')
    p1.append('            </div>')
    p1.append('        </div>')
    p1.append('        <div class="paragraph">')
    p1.append(f'            Your growth edge lies in mastering the <strong>{karma["birth_card"]["challenge"]}</strong>. ')
    p1.append(f'            The <strong>{karma["birth_card"]["supporting"]}</strong> represents a natural talent you can lean on.')
    p1.append('        </div>')
    p1.append('    </div>')
    p1.append('    <h2>III. The Life Path</h2>')
    p1.append('    <p class="paragraph">')
    p1.append(f'        <strong>The Gateway:</strong> {bc_desc.get("gw", "Your path is unique.")}')
    p1.append('    </p>')
    p1.append('    <div class="footer">')
    p1.append(f'        <span>Report for {timing["birth_date"]}</span>')
    p1.append(f'        <span>Created {now_str} — Page 1</span>')
    p1.append('    </div>')
    p1.append('</div>')
    pages.append("\n".join(p1))

    # --- PAGE 2: Current Year ---
    p2 = []
    p2.append('<div class="page">')
    p2.append('    <div class="subtitle">The Temporal Report</div>')
    p2.append(f'    <h1>Yearly Cycle: Age {timing["age"]}</h1>')
    p2.append('    <div class="header-rule"></div>')
    p2.append('    <p class="paragraph">')
    p2.append(f'        You are currently in Spread Year {timing["spread_year"]}. This defines the psychological environment from your last birthday to your next.')
    p2.append('    </p>')
    p2.append('    <div class="spread-container">')
    p2.append('        <div style="flex:1;">')
    p2.append('            <h3>The Yearly Spread</h3>')
    grid_json = calculate_blueprint._DATA["yearly_spreads"][str(timing["spread_year"])]["grid"]
    p2.append(f'            {build_grid_html(grid_json)}')
    p2.append('            <div style="margin-top:15px; font-size:11px; color:var(--text-muted);">')
    p2.append(f'                <strong>Crown Line:</strong> {", ".join(timing["crown_line"])}')
    p2.append('            </div>')
    p2.append('        </div>')
    p2.append('        <div style="flex:1; padding-left:20px; border-left: 1px solid var(--border);">')
    p2.append('            <h3>Active Influence</h3>')
    p2.append(f'            <p class="paragraph" style="font-size:13px;">Currently in your <strong>{active["planet"]}</strong> period.</p>')
    p2.append('            <div class="data-row" style="margin-bottom:10px;">')
    p2.append(f'                {get_card_html(active["birth_card_active"])}')
    p2.append(f'                <div style="font-size:12px;"><strong>Internal: {active["birth_card_active"]}</strong></div>')
    p2.append('            </div>')
    p2.append('            <div class="data-row">')
    p2.append(f'                {get_card_html(active["prc_active"])}')
    p2.append(f'                <div style="font-size:12px;"><strong>External: {active["prc_active"]}</strong></div>')
    p2.append('            </div>')
    p2.append('            <h3>Key Locations</h3>')
    p2.append('            <ul style="font-size:12px; padding-left:15px;">')
    p2.append(f'                <li><strong>Environment:</strong> {env_disp["birth_card"]["environment"]}</li>')
    p2.append(f'                <li><strong>Displacement:</strong> {env_disp["birth_card"]["displacement"]}</li>')
    p2.append(f'                <li><strong>Long Range:</strong> {lr["birth_card"]["card"]}</li>')
    p2.append('            </ul>')
    p2.append('        </div>')
    p2.append('    </div>')
    p2.append('    <h2>Yearly Summary</h2>')
    p2.append('    <p class="paragraph">')
    p2.append(f'        This year is defined by the <strong>{lr["birth_card"]["card"]}</strong> theme. ')
    p2.append(f'        Displacing the <strong>{env_disp["birth_card"]["displacement"]}</strong> brings lessons of ')
    p2.append(f'        {descriptions.get(env_disp["birth_card"]["displacement"], {}).get("t", "experience")}.')
    p2.append('    </p>')
    p2.append('    <div class="footer">')
    p2.append('        <span>Cycle Valid through Birthday</span>')
    p2.append(f'        <span>Created {now_str} — Page 2</span>')
    p2.append('    </div>')
    p2.append('</div>')
    pages.append("\n".join(p2))

    # --- PAGE 3+: Interpretations ---
    interp_items = [
        ("Birth Card", archetype["birth_card"], "birth_card", "#feca57"),
        ("Planetary Ruler", archetype["planetary_ruling_card"], "prc", "#54a0ff"),
        ("Long Range", lr["birth_card"]["card"] if lr["birth_card"] else None, "long_range", "#ff9f43"),
        ("Environment", env_disp["birth_card"]["environment"] if env_disp["birth_card"] else None, "environment", "#1dd1a1"),
        ("Displacement", env_disp["birth_card"]["displacement"] if env_disp["birth_card"] else None, "displacement", "#ff9f43"),
        ("Mercury", bc_spread["period_cards"].get("Mercury"), "mercury", PLANET_COLORS["Mercury"]),
        ("Venus", bc_spread["period_cards"].get("Venus"), "venus", PLANET_COLORS["Venus"]),
        ("Mars", bc_spread["period_cards"].get("Mars"), "mars", PLANET_COLORS["Mars"]),
        ("Jupiter", bc_spread["period_cards"].get("Jupiter"), "jupiter", PLANET_COLORS["Jupiter"]),
        ("Saturn", bc_spread["period_cards"].get("Saturn"), "saturn", PLANET_COLORS["Saturn"]),
        ("Uranus", bc_spread["period_cards"].get("Uranus"), "uranus", PLANET_COLORS["Uranus"]),
        ("Neptune", bc_spread["period_cards"].get("Neptune"), "neptune", PLANET_COLORS["Neptune"]),
        ("Pluto", bc_spread["pluto"], "pluto", PLANET_COLORS["Pluto"]),
        ("Result", bc_spread["result"], "result", PLANET_COLORS["Result"]),
    ]

    interp_html = []
    interp_html.append('<div class="page">')
    interp_html.append('    <div class="subtitle">The Interpretations</div>')
    interp_html.append('    <h1>Analysis & Meanings</h1>')
    interp_html.append('    <div class="header-rule"></div>')
    interp_html.append('    <div class="interp-section">')

    for i, (label, card, role_key, color) in enumerate(interp_items):
        if not card: continue
        desc = descriptions.get(card, {})
        m = meanings.get(card, {}).get(role_key, "")
        
        if i > 0 and i % 7 == 0:
            interp_html.append('    </div>')
            interp_html.append('</div>')
            interp_html.append('<div class="page">')
            interp_html.append('    <div class="subtitle">The Interpretations</div>')
            interp_html.append('    <h1>Analysis Continued</h1>')
            interp_html.append('    <div class="header-rule"></div>')
            interp_html.append('    <div class="interp-section">')

        interp_html.append('        <div class="interp-item">')
        interp_html.append('            <div class="interp-head">')
        interp_html.append(f'                <span class="role-tag" style="background: {color};">{label}</span>')
        suit = get_card_suit(card)
        c_class = 'var(--card-red)' if suit in '♥♦' else 'var(--card-black)'
        interp_html.append(f'                <span class="item-card-text" style="color: {c_class}">{card}</span>')
        interp_html.append(f'                <span class="item-title">{desc.get("t", "")}</span>')
        interp_html.append('            </div>')
        interp_html.append(f'            <div class="paragraph" style="font-size:13px; margin-bottom:5px;"><strong>Meaning:</strong> {m}</div>')
        interp_html.append(f'            <div style="font-size:11px; color:var(--text-muted); font-style:italic;">Archetype: {desc.get("id", "")}</div>')
        interp_html.append('        </div>')

    interp_html.append('    </div>')
    interp_html.append('    <div class="footer">')
    interp_html.append('        <span>Archetypal Breakdown</span>')
    interp_html.append(f'        <span>Created {now_str} — Page 3+</span>')
    interp_html.append('    </div>')
    interp_html.append('</div>')
    
    pages.append("\n".join(interp_html))

    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"

def generate_report_markdown(result):
    archetype = result["archetype"]
    timing = result["timing"]
    bc_spread = result["birth_card_spread"]
    active = result["active_period"]
    karma = result["lifetime_karma"]
    lr = result["long_range"]
    env_disp = result["environment_displacement"]

    init_data()
    descriptions = calculate_blueprint._DATA.get("card_descriptions", {})
    meanings = calculate_blueprint._DATA.get("weekly_card_meanings", {})
    
    bc_desc = descriptions.get(archetype["birth_card"], {})
    prc_desc = descriptions.get(archetype["planetary_ruling_card"], {})

    now_str = datetime.now().strftime("%B %d, %Y")

    md = []
    md.append(f"# The Blueprint Report: {archetype['birth_card']}")
    md.append(f"**Report for {timing['birth_date']}** | *Created {now_str}*")
    md.append("\n---\n")
    md.append(f"> \"Your soul chose the signature of the {archetype['birth_card']} to navigate this lifetime—a pattern of {archetype['birth_card_suit_domain'].lower()}.\"")
    md.append("\n")

    md.append("## I. Core Identity")
    md.append(f"### **Birth Card: {archetype['birth_card']}**")
    md.append(f"**{bc_desc.get('t', 'Archetype')}**")
    md.append(f"{bc_desc.get('id', '')}")
    md.append("\n")
    md.append(f"### **Planetary Ruler: {archetype['planetary_ruling_card']}**")
    md.append(f"**{prc_desc.get('t', 'Planetary Ruler')}**")
    md.append(f"While the {archetype['birth_card']} is your internal engine, others experience you through the lens of the {archetype['planetary_ruling_card']}. This is your professional and social \"ruling\" presence.")
    md.append("\n")

    md.append("## II. The Karma Pair")
    md.append("Every lifetime has a specific tension—a challenge card and a supporting strength. This is your permanent \"Soul Blueprint.\"")
    md.append("\n")
    md.append(f"| Position | Card | Function |")
    md.append(f"| :--- | :--- | :--- |")
    md.append(f"| **Challenge** | {karma['birth_card']['challenge']} | Where you encounter friction and growth. |")
    md.append(f"| **Support** | {karma['birth_card']['supporting']} | Natural talent you can lean on. |")
    md.append("\n")

    md.append("## III. The Life Path")
    md.append(f"**The Gateway:** {bc_desc.get('gw', 'Your path is unique.')}")
    md.append("\n")

    md.append("---")
    md.append(f"## IV. Yearly Cycle: Age {timing['age']}")
    md.append(f"You are currently in **Spread Year {timing['spread_year']}**. This cycle defines the people, events, and psychological environment from your last birthday to your next.")
    md.append("\n")
    
    md.append("### The Yearly Spread Grid")
    grid = calculate_blueprint._DATA['yearly_spreads'][str(timing['spread_year'])]['grid']
    col_labels = ["Neptune", "Uranus", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"]
    row_labels = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    
    header = "| | " + " | ".join(col_labels) + " |"
    sep = "| :--- | " + " | ".join([":---:"] * len(col_labels)) + " |"
    md.append(header)
    md.append(sep)
    for r in range(7):
        row = grid[r*7 : (r+1)*7]
        line = f"| **{row_labels[r]}** | " + " | ".join(row) + " |"
        md.append(line)
    md.append("\n")
    
    md.append(f"**Crown Line:** {', '.join(timing['crown_line'])}")
    md.append("\n")

    md.append("### Current Temporal Influence")
    md.append(f"You are currently in your **{active['planet']}** period.")
    md.append(f"- **Internal Influence ({active['planet']}):** {active['birth_card_active']} (How you feel)")
    md.append(f"- **External Influence ({active['planet']}):** {active['prc_active']} (How events show up)")
    md.append("\n")

    md.append("### Key Yearly Locations")
    md.append(f"- **Environment (Home Base):** {env_disp['birth_card']['environment']}")
    md.append(f"- **Displacement (Where you moved):** {env_disp['birth_card']['displacement']}")
    md.append(f"- **Long Range (Yearly Theme):** {lr['birth_card']['card']}")
    md.append("\n")

    md.append("---")
    md.append("## V. Analysis & Meanings")
    
    interp_items = [
        ("Birth Card", archetype["birth_card"], "birth_card"),
        ("Planetary Ruler", archetype["planetary_ruling_card"], "prc"),
        ("Long Range", lr["birth_card"]["card"] if lr["birth_card"] else None, "long_range"),
        ("Environment", env_disp["birth_card"]["environment"] if env_disp["birth_card"] else None, "environment"),
        ("Displacement", env_disp["birth_card"]["displacement"] if env_disp["birth_card"] else None, "displacement"),
        ("Mercury", bc_spread["period_cards"].get("Mercury"), "mercury"),
        ("Venus", bc_spread["period_cards"].get("Venus"), "venus"),
        ("Mars", bc_spread["period_cards"].get("Mars"), "mars"),
        ("Jupiter", bc_spread["period_cards"].get("Jupiter"), "jupiter"),
        ("Saturn", bc_spread["period_cards"].get("Saturn"), "saturn"),
        ("Uranus", bc_spread["period_cards"].get("Uranus"), "uranus"),
        ("Neptune", bc_spread["period_cards"].get("Neptune"), "neptune"),
        ("Pluto", bc_spread["pluto"], "pluto"),
        ("Result", bc_spread["result"], "result"),
    ]

    for label, card, role_key in interp_items:
        if not card: continue
        desc = descriptions.get(card, {})
        m = meanings.get(card, {}).get(role_key, "Meaning not available for this position.")
        
        md.append(f"### {label}: {card}")
        md.append(f"**{desc.get('title', '')}**")
        md.append(f"**Meaning in Position:** {m}")
        md.append("\n")
        md.append(f"*Archetype Focus: {desc.get('core_identity', '')}*")
        md.append("\n")

    md.append("---\n*End of Report*")
    return "\n".join(md)

# ---------------------------------------------------------------------------
# API Function
# ---------------------------------------------------------------------------

def generate_report(bm, bd, by, td=None):
    if td is None:
        td = date.today()
    
    result = calc_blueprint(bm, bd, by, td)
    report_html = generate_report_html(result)
    
    if HAS_WEASYPRINT:
        output_name = f"Birthcard_Report_{bm}_{bd}_{by}.pdf"
        HTML(string=report_html).write_pdf(output_name)
    else:
        output_name = f"Birthcard_Report_{bm}_{bd}_{by}.html"
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(report_html)
    
    return output_name

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 generate_birthcard_report.py <month> <day> <year> [--target-date YYYY-MM-DD] [--output filename] [--md]")
        sys.exit(1)
    
    bm = int(sys.argv[1])
    bd = int(sys.argv[2])
    by = int(sys.argv[3])
    
    td = date.today()
    md_output = "--md" in sys.argv
    ext = ".md" if md_output else ".pdf"
    output_name = f"Birthcard_Report_{bm}_{bd}_{by}{ext}"
    
    if "--target-date" in sys.argv:
        idx = sys.argv.index("--target-date")
        td = date.fromisoformat(sys.argv[idx + 1])
    
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_name = sys.argv[idx + 1]
    
    print(f"Calculating blueprint for {bm}/{bd}/{by} (Target: {td})...")
    result = calc_blueprint(bm, bd, by, td)
    
    if md_output:
        print("Generating Markdown report...")
        report_md = generate_report_markdown(result)
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"Success! Markdown report saved to {output_name}")
    else:
        print("Generating HTML report...")
        report_html = generate_report_html(result)
        
        if HAS_WEASYPRINT:
            print(f"Converting to PDF: {output_name}...")
            HTML(string=report_html).write_pdf(output_name)
            print(f"Success! Report saved to {output_name}")
        else:
            html_output = output_name.replace(".pdf", ".html")
            with open(html_output, "w", encoding="utf-8") as f:
                f.write(report_html)
            print(f"WeasyPrint not found. Saved as HTML instead: {html_output}")
            print("Tip: Open the HTML in Chrome and 'Print to PDF' for the best result.")

if __name__ == "__main__":
    main()
