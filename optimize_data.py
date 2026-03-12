import json
import os

def optimize():
    source_path = "card_blueprints_data.json"
    target_path = "card_blueprints_data.min.json"
    
    with open(source_path, "r") as f:
        data = json.load(f)
    
    # 1. Remove _meta
    if "_meta" in data:
        del data["_meta"]
    
    # 2. Optimize solar_values
    if "card_to_solar" in data["solar_values"]:
        del data["solar_values"]["card_to_solar"]
        
    # 3. Compress planetary_ruling_cards
    # Convert ["K♣", "J♦"] to "K♣|J♦"
    prc = data["planetary_ruling_cards"]
    for date_key, val in prc.items():
        if isinstance(val, list):
            prc[date_key] = "|".join(val)
            
    # 4. Shorten keys in card_descriptions
    # title -> t, core_identity -> id, gifts -> g, shadow -> s, life_direction -> ld
    descriptions = {}
    key_map = {
        "title": "t",
        "core_identity": "id",
        "gifts": "g",
        "shadow": "s",
        "life_direction": "ld",
        "gateway": "gw"
    }
    for card, desc in data["card_descriptions"].items():
        new_desc = {key_map.get(k, k): v for k, v in desc.items()}
        descriptions[card] = new_desc
    data["card_descriptions"] = descriptions

    # 5. Compress yearly_spreads
    # Convert 7x7 grid into a single list of strings (49 items)
    for spread_id, content in data["yearly_spreads"].items():
        grid_2d = content["grid"]
        flat_grid = []
        for row in grid_2d:
            flat_grid.extend(row)
        content["grid"] = flat_grid

    # Save minified version (no indents for raw storage, but we'll use small indent for AI readability)
    with open(target_path, "w") as f:
        json.dump(data, f, separators=(',', ':'))
        
    print(f"Optimization complete.")
    print(f"Original size: {os.path.getsize(source_path) / 1024:.2f} KB")
    print(f"Compressed size: {os.path.getsize(target_path) / 1024:.2f} KB")

if __name__ == "__main__":
    optimize()
