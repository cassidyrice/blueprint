#!/usr/bin/env python3
"""
production.py — Master Product Orchestrator
------------------------------------------
Generates the complete 'Cardology Blueprint' package for a customer:
1. Core Engine JSON
2. Premium PDF Report
3. High-Fidelity Video Reading

Usage:
    python3 production.py "Names" MM DD YYYY
"""

import os
import sys
import shutil
from datetime import date
import json

import config
from calculate_blueprint import calculate_blueprint
from generate_birthcard_report import generate_report
from pipeline import run as run_video_pipeline
from generate_script import script_profile

def production_package(name: str, month: int, day: int, year: int):
    print("="*70)
    print(f"   CARDOLOGY MEDIA HOUSE | PRODUCTION PIPELINE")
    print(f"   Subject: {name} ({month}/{day}/{year})")
    print("="*70)

    # 1. Setup production directory
    safe_name = name.replace(" ", "_").lower()
    prod_dir = os.path.join("output", "production", f"{safe_name}_{date.today().isoformat()}")
    os.makedirs(prod_dir, exist_ok=True)
    
    # 2. Run Core Engine
    print(f"\n[1/3] Calculating Core Blueprint...")
    blueprint_data = calculate_blueprint(month, day, year)
    blueprint_path = os.path.join(prod_dir, f"{safe_name}_blueprint.json")
    with open(blueprint_path, "w") as f:
        json.dump(blueprint_data, f, indent=2, default=str)
    print(f"      ✓ Data crystallized: {blueprint_path}")

    # 3. Generate PDF Report
    print(f"\n[2/3] Crafting Premium PDF Report...")
    # generate_report returns the temp path, could be .pdf or .html
    temp_report = generate_report(month, day, year) 
    ext = os.path.splitext(temp_report)[1]
    report_path = os.path.join(prod_dir, f"{safe_name}_report{ext}")
    shutil.move(temp_report, report_path)
    print(f"      ✓ Report forged: {report_path}")

    # 4. Generate Video Reading
    print(f"\n[3/3] Rendering High-Fidelity Video...")
    video_path = os.path.join(prod_dir, f"{safe_name}_reading.mp4")
    # Get a high-impact profile script
    bc = blueprint_data['archetype']['birth_card']
    script = script_profile(bc, name=name, legacy="Relativity & The Cosmic Blueprint")
    run_video_pipeline(script, card=bc, output_path=video_path)
    print(f"      ✓ Video encoded: {video_path}")

    print("\n" + "="*70)
    print(f"   PRODUCTION COMPLETE")
    print(f"   Package: {prod_dir}")
    print("="*70)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 production.py <Name> <Month> <Day> <Year>")
        sys.exit(1)
    
    name = sys.argv[1]
    m = int(sys.argv[2])
    d = int(sys.argv[3])
    y = int(sys.argv[4])
    
    production_package(name, m, d, y)
