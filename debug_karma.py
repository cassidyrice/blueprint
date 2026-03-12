from calculate_blueprint import init_data, _DATA, _find_card_position, _get_card_at_position

def debug_karma(card, ages):
    from calculate_blueprint import get_spreads
    init_data()
    spreads = get_spreads()
    spirit = spreads['0']
    spirit_pos = _find_card_position(card, spirit)
    print(f"Card: {card} | Spirit Pos: {spirit_pos}")
    
    for age in ages:
        sy = age + 1
        current = spreads.get(str(sy))
        if not current: continue
        
        current_pos = _find_card_position(card, current)
        env = _get_card_at_position(spirit_pos, current)
        disp = _get_card_at_position(current_pos, spirit)
        print(f"Age {age} (Spread {sy}): Pos={current_pos} | Env={env} | Disp={disp}")

if __name__ == "__main__":
    debug_karma("8♦", [34, 35, 36])
