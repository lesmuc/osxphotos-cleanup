# osxphotos-cleanup

A macOS tool that scans your iCloud Photos library and suggests photos to clean up. It uses rule-based filters and optionally [Ollama](https://ollama.com/) Vision AI to identify candidates for deletion or review.

Photos are **never deleted directly** -- instead, results are organized into albums in Photos.app so you can review them manually.

## How it works

1. **Scan** -- Reads your Photos library metadata via [osxphotos](https://github.com/RhetTbull/osxphotos)
2. **Rules** -- Applies cleanup rules to find candidates:
   - **BurstCleanupRule** -- Non-favorite burst photos
   - **DrinkRule** -- Photos labeled as drinks (glasses, bottles) without recognized people
   - **FoodRule** -- Photos labeled as food without recognized people
   - **LargeFileRule** -- Unusually large photos (>50 MB) or videos (>500 MB)
3. **AI Analysis** (optional) -- Sends `REVIEW` candidates to Ollama Vision (llama3.2-vision) for a second opinion
4. **Albums** -- Creates albums in Photos.app (`AI: To Delete`, `AI: To Review`, `AI: To Archive`)

## Requirements

- macOS with Photos.app
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) with `llama3.2-vision:11b` (only for AI analysis)

## Installation

```bash
git clone https://github.com/lesmuc/osxphotos-cleanup.git
cd osxphotos-cleanup
uv sync
```

## Usage

```bash
# Scan entire library, run AI analysis, create albums
cleanup

# Scan only the first 100 photos
cleanup --limit 100

# Preview suggestions without creating albums
cleanup --dry-run

# Skip AI analysis (rules only)
cleanup --no-ai

# Combine options
cleanup --limit 100 --dry-run --no-ai
```

## Options

| Option | Description |
|---|---|
| `--limit N` | Scan only the first N photos (0 = all) |
| `--dry-run` | Show suggestions without creating albums |
| `--no-ai` | Skip Ollama Vision analysis |
