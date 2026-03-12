---
description: How to maintain and clean the Cardology workspace using Agent 5 (The Janitor)
---

This workflow helps optimize the AI's context window and local storage by removing build artifacts (image frames) and temporary reports.

1. **Analyze the Workspace**
Run this to see which files are consuming the most space/context.
// turbo
```bash
python3 janitor.py analyze
```

2. **Standard Cleanup**
Removes temporary image frames and duplicate reports. Ideal to run between video generations.
// turbo
```bash
python3 janitor.py clean
```

3. **Full Purge**
Wipes all generated media, audio, and reports to reset the output directory state.
// turbo
```bash
python3 janitor.py purge
```
