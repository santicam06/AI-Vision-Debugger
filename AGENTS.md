# AI-Vision-Debugger — Agent Notes

## What this repo actually is
A single-file Python tool: `src/vis-fix.py` sends a screenshot to the Kimi K2.5 vision model (via OpenRouter) and lets it iteratively call a Tavily-backed `web_search` tool to diagnose error messages in the image. Output is plain text on stdout; diagnostic logs go to stderr.

> **Stale docs warning:** `README.md` (uncommitted) describes a TypeScript/Node code-reviewer (`npx tsx src/review.ts`, `system_prompts/INSTRUCTIONS1-3.md`, `reports/`, `npm install`). **None of that exists in the working tree** — README is aspirational/stale. `GEMINI.md` is the accurate current description of the code that actually runs.

## Entrypoints and ownership
- `src/vis-fix.py` — runnable script. `main()` is called at module import (no `if __name__ == "__main__":` guard), so importing this file executes it.
- `src/INSTRUCTIONS.md` — system prompt loaded at startup and sent as the first message. **Edit this file to change LLM behavior**; do not edit prompt strings in `vis-fix.py`.
- `image_tests/` — the **only** directory the script reads from. CLI arg resolves to `../image_tests/<filename>` relative to `src/`.

## Running it
From the repo root:
```bash
python src/vis-fix.py --error_1.jpeg
```
- Argv is parsed by hand at `vis-fix.py:74`. The first arg must start with `--` and is the **image filename** (e.g. `--error_2.jpeg`), not a flag value. Missing `--` prefix raises `ValueError`. Keep this convention or migration breaks.
- There is **no `requirements.txt`, `pyproject.toml`, `Pipfile`, or lockfile.** Install deps with: `pip install pillow openai python-dotenv tavily-python pydantic` (Python 3.10+).
- Required env vars in `.env` at repo root, loaded via `find_dotenv()`:
  - `OPENROUTER_API_KEY`
  - `TAVILY_API_KEY`
  - `.env` is gitignored and no `.env.example` ships — create manually.

## Quirk that will bite you
`pydantic_function_tool` is imported from the `openai` package (`vis-fix.py:8`), not from `pydantic`. The `openai` SDK must be >= 1.x. Older `openai` versions or pinning to `pydantic`'s own helper will break the tool registration.

## What is NOT set up
No tests, no linter, no formatter, no typechecker, no pre-commit config, no CI workflows. Don't propose `pytest`/`ruff`/`mypy` commands — there's nothing to run them against.

## Misc files
- `src/debug.txt` — diagnostic log file. `sys.stderr` is reassigned to this file at script startup (`vis-fix.py:21`), so every `print(..., file=sys.stderr)` (image processing, iteration traces, tool calls, errors) is captured here. Overwritten on each run.
- `sandbox_errors.txt` (repo root) — **manual scratchpad** for drafting error text to later screenshot. The script never reads it.
- `image_tests/error_{1,2,3}.jpeg` — sample inputs.

## Hardcoded values worth knowing before changing
- Model: `moonshotai/kimi-k2.5` (`vis-fix.py:104`).
- OpenAI client base URL: `https://openrouter.ai/api/v1`.
- Max tool-calling iterations: 5 (`vis-fix.py:99`).
- Image cap: 1024×1024 JPEG quality 85 (`vis-fix.py:31-33`).
- Tavily call: `search_depth="advanced"`, `max_results=8`, `include_answer=True` (`vis-fix.py:132-139`).

Any swap of model or base URL must keep OpenAI-compatible `chat.completions.parse` + `tools` + `image_url` support.
