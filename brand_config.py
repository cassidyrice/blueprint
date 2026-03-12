"""
brand_config.py — Centralized Brand Tokens
Ensures visual and narrative consistency across all agents.
"""

# Visual Tokens
COLORS = {
    "background": "#0D0D0D",      # Matte Black
    "secondary": "#C5A059",       # Muted Gold (Secondary accent)
    "text": "#E8E4DF",            # Matte White
    "accent_warm": "#8B1A2A",     # Wine Red
    "premium": "#D4AF37",         # Metallic Gold (Highlight)
}

FONTS = {
    "serif": "Georgia, 'Playfair Display', serif",
    "sans": "Helvetica, Inter, sans-serif"
}

# Design Principles
DESIGN = {
    "stroke_width": 1.7,
    "letter_spacing_titles": "12px",
    "letter_spacing_body": "1px",
    "aspect_ratio": "9:16"
}

# Narrative Guardrails
TONE = {
    "style": "Modern Philosopher / Strategic",
    "voice": "Robert Greene-esque",
    "forbidden_words": ["manifest", "spirit animal", "vibes"],
    "target_word_count": (35, 55)
}

def get_suit_color(card):
    """Returns the official brand color for a card suit."""
    if any(s in card for s in "♥♦"):
        return COLORS["accent_warm"]
    return COLORS["text"] # Black cards use the white text color for contrast
