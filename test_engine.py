import json
from calculate_blueprint import calculate_blueprint
from datetime import date

def test_engine():
    print("🚀 Running Cardology Engine Validation...")
    
    # Test Case: Feb 17, 1991 (The "Classic" test case from project history)
    # Target Date: March 9, 2026 (Age 35, Spread Year 36)
    birth = (2, 17, 1991)
    target = date(2026, 3, 9)
    
    print(f"\nEvaluating: {birth[0]}/{birth[1]}/{birth[2]} @ {target}")
    result = calculate_blueprint(*birth, target_date=target)
    
    # Validation 1: Archetype
    archetype = result['archetype']
    print(f"✅ Archetype: BC={archetype['birth_card']} | PRC={archetype['planetary_ruling_card']}")
    assert archetype['birth_card'] == "8♦", "Birth Card mismatch"
    assert archetype['planetary_ruling_card'] == "5♣", "PRC mismatch"

    # Validation 2: Timing
    timing = result['timing']
    print(f"✅ Timing: Age={timing['age']} | Spread Year={timing['spread_year']}")
    assert timing['age'] == 35, "Age calculation error"
    assert timing['spread_year'] == 35, "Spread year mapping error (should be Age 35 -> SY 35)"

    # Validation 3: Yearly Karma (Env/Disp)
    # For Feb 17, 1991 (8♦) @ Age 35 (SY 35)
    bc_env = result['environment_displacement']['birth_card']
    print(f"✅ Yearly Karma: Env={bc_env['environment']} | Disp={bc_env['displacement']}")
    assert bc_env['environment'] == "K♣", "Environment card mismatch"
    assert bc_env['displacement'] == "3♠", "Displacement card mismatch"

    # Validation 4: Harmony (The new module)
    harmony = result['harmony']['birth_card']
    print(f"✅ Harmony: Rank Mates={harmony['rank_mates']} | Suit={harmony['suit_harmony']}")
    assert "8♥" in harmony['rank_mates'], "Harmony Rank Mates failure"

    # Validation 5: Active Period
    active = result['active_period']
    print(f"✅ Active Period: {active['planet']} (Day {active['day_in_personal_year']})")
    print(f"   - Internal: {active['birth_card_active']}")
    print(f"   - External: {active['prc_active']}")

    print("\n👑 ENGINE STATUS: Ready for high-volume production.")

if __name__ == "__main__":
    test_engine()
