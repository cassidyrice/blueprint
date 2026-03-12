# Cardology Media House — Core Product Suite

This repository contains the finalized production pipeline for high-fidelity Cardology blueprints, premium reports, and AI-driven video readings.

## 🚀 The Production Pipeline

To generate a complete customer package (JSON + PDF + MP4), use the master orchestrator:

```bash
python3 production.py "Subject Name" MM DD YYYY
```

Example:
```bash
python3 production.py "Albert Einstein" 3 14 1879
```

The output will be stored in `output/production/{name}_{date}/`.

---

## 🛠 Core Components

### 1. The Production Orchestrator (`production.py`)
The top-level script that coordinates the engine, the report generator, and the video pipeline. It ensures all assets are consistent and stored in a unified package.

### 2. The Blueprint Engine (`calculate_blueprint.py`)
High-fidelity calculation engine implementing the 1D flattened grid logic. It handles planetary periods, yearly spreads, karma pairs, and long-range patterns.

### 3. Premium Report Generator (`generate_birthcard_report.py`)
Produces a stunning, multi-page analysis of the subject's archetype and timing.
- **Aesthetic:** Deep Void / Gold / Wine Red / Cinzel.
- **Output:** PDF (via WeasyPrint) or HTML fallback.

### 4. Video production Pipeline (`pipeline.py`)
Generates 9:16 mobile-first video readings with:
- **Narration:** ElevenLabs AI (Voice ID: `HpOCVTxWELfaDqS1Pep5`).
- **Visuals:** High-contrast animated SVGs optimized for TikTok/Reels.
- **Sync:** Frame-perfect synchronization with a 2-second cinematic tail.

### 5. Context Engine (`context_engine.py`)
Manages AI personas (`mystic_architect`, `visual_designer`) to ensure brand consistency and the "WOW Factor" in every script and graphic.

---

## 🔧 Internal Tools

- **`batch.py`**: For high-volume production from a CSV.
- **`janitor.py`**: Maintenance and workspace cleaning.
- **`test_engine.py`**: Validation suite for calculation accuracy.

---

## 📦 Dependencies

Install via:
```bash
pip install -r requirements.txt
playwright install chromium
```
*Note: For PDF generation on Mac, `brew install weasyprint` is recommended to provide system dependencies like Pango.*
