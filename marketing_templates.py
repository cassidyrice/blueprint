"""
marketing_templates.py — Agent: The Closer
Specialized high-conversion script templates and hook generation logic
designed to move users from free content to paid reports.
"""

MARKETING_HOOKS = {
    "pain_point": [
        "You feel like you're working against a ghost. The {card} signature explains why.",
        "Most people with the {card} struggle with one specific shadow. Let's look at yours.",
        "Your {card} energy is being drained by a pattern you can't see yet."
    ],
    "power_play": [
        "The {card} isn't just a card. It's a blueprint for absolute material mastery.",
        "Stop guessing. Your {card} alignment is the key to your next major breakthrough.",
        "You were born under the {card}. It's time to start acting like it."
    ],
    "mystery": [
        "There is a hidden variable in your {card} spread that most people miss.",
        "Your birth card is the {card}, but your planetary ruler is where the real secret lies.",
        "Something major shifts for the {card} this year. Are you ready for it?"
    ]
}

CTA_VARIATIONS = {
    "soft": "Visit the link in my bio to see your full archetype.",
    "hard": "Get your custom 40-page Blueprint report at the link. Start your mastery today.",
    "urgent": "Your yearly cycle is shifting. Download your personalized report before the window closes."
}

def generate_marketing_script(card_data, strategy="pain_point", cta_type="hard"):
    """
    Combines core card data with high-conversion marketing psychology.
    """
    import random
    
    card = card_data.get('card', 'Unknown Card')
    identity = card_data.get('core_identity', 'a unique energetic pattern')
    hooks = MARKETING_HOOKS.get(strategy, MARKETING_HOOKS["mystery"])
    hook = random.choice(hooks).format(card=card)
    cta = CTA_VARIATIONS.get(cta_type, CTA_VARIATIONS["hard"])
    
    script = f"{hook} As a {card}, you are {identity}. But this is just the surface. {cta}"
    
    return script

if __name__ == "__main__":
    # Example usage for testing
    test_data = {
        "card": "8♦",
        "core_identity": "the material strategist who approaches resources as something to master and control"
    }
    print("--- Marketing Script Preview ---")
    print(generate_marketing_script(test_data, strategy="pain_point"))
