# Project Manifest: Cardology Media House

This document serves as the primary context anchor for all agents interacting with this repository.

## 🎯 Project Mission
Our goal is to automate the production of high-fidelity "Cardology" (Science of the Cards) content. We take date-based metaphysical data and transform it into cinematic videos and structured reports.

## 🏗️ Technical Architecture

### 1. The Engine (`calculate_blueprint.py`)
*   **Role:** The single source of truth for all mathematical and metaphysical calculations.
*   **Data:** Powered by `card_blueprints_data.json` (Spreads, Archetypes, Meanings).
*   **Key Function:** `calculate_blueprint()` returns a comprehensive JSON object for a birthdate.

### 2. The Video Swarm (`pipeline.py`)
*   **Orchestrator:** `pipeline.py` coordinates the following specialized scripts:
    *   `generate_script.py`: Narrative creation via Claude (High-impact storytelling).
    *   `voiceover.py`: Audio generation via ElevenLabs API.
    *   `generate_svg.py`: Dynamic SVG visual generation matching audio duration.
    *   `render_frames.py`: Playwright-based capture of SVG frames to PNG.
    *   `compose.py`: FFmpeg assembly of frames + audio to MP4.

### 3. The Report Wing (`generate_birthcard_report.py`)
*   **Role:** Generates multi-page technical analysis in PDF, HTML, or Markdown.
*   **Usage:** `python3 generate_birthcard_report.py <M> <D> <Y> --md`

### 4. The Context Wing (`.prompts/`)
*   **The Brain:** Modular persona and template management.
*   **Context Engine:** `context_engine.py` assembles high-fidelity prompts.
*   **Personas:** 
    *   `mystic_architect`: Robert Greene Brand Voice.
    *   `visual_designer`: High-end Luxury SVG standards.

### 5. Maintenance & Operations
*   **Janitor:** `janitor.py` handles workspace cleanup (`/janitor` workflow).
*   **Batch:** `batch.py` processes multiple birthdates from `birthdates.csv`.
*   **Config:** `config.py` manages API keys and video constants (FPS, Resolution).

## 📂 Directory Map
*   `/output/`: Generated media storage.
    *   `/frames/`: (Temporary) Storage for PNG frames during video render.
    *   `/videos/`: Final MP4 output destination.
*   `/.prompts/`: Primary source of truth for AI tone, style, and instructions.
*   `/.agent/workflows/`: Specialized protocol files (e.g., `janitor.md`).

---
*Last Updated: March 11, 2026*
