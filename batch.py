#!/usr/bin/env python3
"""
Automated batch pipeline — Card Blueprints SVG Video Generator
---------------------------------------------------------------
Each trigger advances to the next birthdate and cycles through
3 script contexts: profile → lens → spread → profile → ...

State is persisted in output/batch_state.json so every call picks
up exactly where the last one left off.

Commands:
    python batch.py trigger              # run next item in queue
    python batch.py trigger --dry-run    # preview what would run, no execution
    python batch.py status               # show queue progress
    python batch.py reset                # reset state to beginning
    python batch.py run-all              # process every item in the queue

Birthdates source:
    Edit birthdates.csv to add/remove people.
    Columns: name, month, day, birth_year
"""
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

import config
from generate_script import (
    script_profile,
    script_three_lens,
    script_spread_summary,
    card_from_birthday,
    CARD_DESCRIPTIONS,
)
from pipeline import run as run_pipeline


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BIRTHDATES_FILE = "birthdates.csv"
STATE_FILE = "output/batch_state.json"
VIDEOS_DIR = "output/videos"

# The 3 rotating script contexts
CONTEXTS = ["profile", "lens", "spread"]


# ---------------------------------------------------------------------------
# Birthdate helpers
# ---------------------------------------------------------------------------

def load_birthdates() -> list[dict]:
    with open(BIRTHDATES_FILE, newline="") as f:
        return list(csv.DictReader(f))


def current_spread_year(month: int, day: int, birth_year: int) -> int:
    """Calculate spread year (mapped directly to age) based on today's date."""
    today = date.today()
    birthday_this_year = date(today.year, month, day)
    age = today.year - birth_year
    if today < birthday_this_year:
        age -= 1
    return max(0, age)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"trigger_count": 0, "completed": []}


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Core trigger logic
# ---------------------------------------------------------------------------

def resolve_trigger(trigger_count: int, birthdates: list[dict]) -> dict:
    """
    For a given trigger number, return the birthdate + context to use.
    - Birthdate cycles through the full list
    - Context cycles through CONTEXTS (profile/lens/spread)
    """
    bd = birthdates[trigger_count % len(birthdates)]
    context = CONTEXTS[trigger_count % len(CONTEXTS)]
    return {
        "trigger": trigger_count,
        "name": bd["name"],
        "month": int(bd["month"]),
        "day": int(bd["day"]),
        "birth_year": int(bd["birth_year"]),
        "context": context,
        "legacy": bd.get("brand_association", "")
    }


def build_script(item: dict) -> tuple[str, str]:
    """
    Generate the narration script for a trigger item.
    Returns (script_text, output_video_path).
    """
    month, day, birth_year = item["month"], item["day"], item["birth_year"]
    context = item["context"]
    name = item["name"]

    card = card_from_birthday(month, day)
    card_safe = card.replace("♥","H").replace("♣","C").replace("♦","D").replace("♠","S")
    title = CARD_DESCRIPTIONS.get(card, {}).get("title", "").replace(" ", "_")

    output_path = os.path.join(
        VIDEOS_DIR,
        f"{name.lower()}_{card_safe}_{context}.mp4"
    )

    print(f"\n{'='*60}")
    print(f"Trigger #{item['trigger']} | {name} ({month}/{day}/{birth_year})")
    print(f"Birth card: {card} — {CARD_DESCRIPTIONS.get(card, {}).get('title', '')}")
    print(f"Context: {context.upper()}")
    print(f"Output: {output_path}")
    print(f"{'='*60}")

    if context == "profile":
        script = script_profile(card, name=name, legacy=item["legacy"])

    elif context == "lens":
        script = script_three_lens(card, name=name, legacy=item["legacy"])

    elif context == "spread":
        year_age = current_spread_year(month, day, birth_year)
        print(f"Spread year: {year_age} (Age {year_age})")
        script = script_spread_summary(month, day, year_age, name=name, legacy=item["legacy"])

    return script, output_path


def trigger_once(dry_run: bool = False) -> dict:
    """Run the next trigger in the queue. Returns the trigger item."""
    birthdates = load_birthdates()
    state = load_state()
    item = resolve_trigger(state["trigger_count"], birthdates)

    if dry_run:
        card = card_from_birthday(item["month"], item["day"])
        print(f"\nDRY RUN — Trigger #{item['trigger']}")
        print(f"  Person   : {item['name']} ({item['month']}/{item['day']}/{item['birth_year']})")
        print(f"  Birth card: {card} — {CARD_DESCRIPTIONS.get(card, {}).get('title', '')}")
        print(f"  Context  : {item['context'].upper()}")
        card_safe = card.replace("♥","H").replace("♣","C").replace("♦","D").replace("♠","S")
        print(f"  Output   : {VIDEOS_DIR}/{item['name'].lower()}_{card_safe}_{item['context']}.mp4")
        return item

    os.makedirs(VIDEOS_DIR, exist_ok=True)

    script, output_path = build_script(item)

    # Skip if already generated
    if os.path.exists(output_path):
        print(f"Video already exists, skipping: {output_path}")
    else:
        card = card_from_birthday(item["month"], item["day"])
    run_pipeline(script, card=card, output_path=output_path)

    # Persist state
    state["trigger_count"] += 1
    state["completed"].append({
        "trigger": item["trigger"],
        "name": item["name"],
        "context": item["context"],
        "output": output_path,
    })
    save_state(state)

    return item


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_status():
    birthdates = load_birthdates()
    state = load_state()
    total = state["trigger_count"]
    completed = state["completed"]

    print(f"\nBatch queue status")
    print(f"  Birthdates loaded : {len(birthdates)}")
    print(f"  Triggers fired    : {total}")
    print(f"  Videos created    : {len(completed)}")

    if completed:
        print(f"\nCompleted:")
        for c in completed[-10:]:
            exists = "✓" if os.path.exists(c["output"]) else "✗"
            print(f"  [{exists}] #{c['trigger']} {c['name']} / {c['context']} → {c['output']}")

    # Preview next 3
    print(f"\nNext 3 triggers:")
    for i in range(3):
        item = resolve_trigger(total + i, birthdates)
        card = card_from_birthday(item["month"], item["day"])
        print(f"  #{total + i}: {item['name']} ({item['month']}/{item['day']}) | {card} | {item['context'].upper()}")


def cmd_run_all():
    birthdates = load_birthdates()
    state = load_state()
    total_triggers = len(birthdates) * len(CONTEXTS)
    remaining = total_triggers - state["trigger_count"]

    if remaining <= 0:
        print("All triggers completed. Run `reset` to start over.")
        return

    print(f"Running {remaining} remaining triggers...")
    for _ in range(remaining):
        trigger_once()


def cmd_reset():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("State reset. Next trigger starts from #0.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Card Blueprints batch video pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("trigger", help="Run the next trigger in the queue")
    p.add_argument("--dry-run", action="store_true", help="Preview without executing")

    sub.add_parser("status", help="Show queue progress and next triggers")
    sub.add_parser("reset", help="Reset state back to trigger #0")
    sub.add_parser("run-all", help="Process all remaining triggers sequentially")

    args = parser.parse_args()

    if args.cmd == "trigger":
        trigger_once(dry_run=args.dry_run)
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "reset":
        cmd_reset()
    elif args.cmd == "run-all":
        cmd_run_all()


if __name__ == "__main__":
    main()
