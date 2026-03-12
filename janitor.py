#!/usr/bin/env python3
"""
janitor.py — Agent 5: The Janitor (The Context Strategist)
Monitors the file tree, cleans up build artifacts, and improves context usage.
"""

import os
import shutil
import argparse
from pathlib import Path

def get_dir_size(path):
    total = 0
    for p in Path(path).rglob('*'):
        if p.is_file():
            total += p.stat().st_size
    return total

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def analyze_workspace():
    print("=== Agent 5: Workspace Analysis ===")
    root = Path(".")
    files = list(root.rglob('*'))
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    
    print(f"Total Workspace Size: {format_size(total_size)}")
    print(f"Total Files: {len(files)}")
    
    # Heavy hitters
    heavy = []
    for d in root.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            size = get_dir_size(d)
            heavy.append((d.name, size))
    
    heavy.sort(key=lambda x: x[1], reverse=True)
    print("\nDirectory Breakdown:")
    for name, size in heavy:
        print(f"  - {name:15}: {format_size(size)}")

    # Specific junk identification
    reports = list(root.glob("Birthcard_Report_*"))
    frames = list(Path("output/frames").glob("*.png"))
    
    print("\nCleanup Candidates:")
    if frames:
        print(f"  - Frames: {len(frames)} PNGs in output/frames ({format_size(get_dir_size('output/frames'))})")
    if reports:
        print(f"  - Reports: {len(reports)} temporary report files")

def clean_frames():
    path = Path("output/frames")
    if path.exists():
        print(f"Cleaning {path}...")
        count = 0
        for f in path.glob("*.png"):
            f.unlink()
            count += 1
        print(f"Removed {count} frames.")
    else:
        print("Frames directory not found.")

def clean_reports():
    print("Cleaning temporary reports...")
    count = 0
    for f in Path(".").glob("Birthcard_Report_*"):
        f.unlink()
        count += 1
    for f in Path(".").glob("test_report.html"):
        f.unlink()
        count += 1
    print(f"Removed {count} files.")

def summarize_production():
    """
    Agent: The Librarian
    Scans for final high-value output to show what actually exists.
    """
    print("\n" + "="*40)
    print("📋 CARDOLOGY PRODUCTION SUMMARY")
    print("="*40)
    
    video_dir = Path("output/videos")
    videos = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
    
    reports = list(Path(".").glob("*.pdf")) + list(Path(".").glob("*.md"))
    # Exclude manifest and plan from report counts
    reports = [r for r in reports if "Report" in r.name]

    if not videos and not reports:
        print("No final production assets found. Workspace is clean.")
    else:
        if videos:
            print(f"\n🎥 Final Videos ({len(videos)})")
            for v in videos:
                size = os.path.getsize(v) / (1024 * 1024)
                print(f"  - {v.name:30} | {size:.1f} MB")
        
        if reports:
            print(f"\n📄 Technical Reports ({len(reports)})")
            for r in reports:
                print(f"  - {r.name}")
    
    print("\n" + "="*40)
    print("Status: Context Optimized. Ready for next cycle.")
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 5: The Janitor")
    parser.add_argument("cmd", choices=["analyze", "clean", "purge"], help="Command to run")
    args = parser.parse_args()

    if args.cmd == "analyze":
        analyze_workspace()
    elif args.cmd == "clean":
        clean_frames()
        clean_reports()
        summarize_production()
    elif args.cmd == "purge":
        # More aggressive
        clean_frames()
        clean_reports()
        if os.path.exists("output/animation.svg"): os.unlink("output/animation.svg")
        if os.path.exists("output/voiceover.mp3"): os.unlink("output/voiceover.mp3")
        print("Workspace purged of all temporary media.")
        summarize_production()
