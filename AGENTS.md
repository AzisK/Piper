# Agents

## Project

This is `readit`, a Python CLI wrapper around piper-tts for text-to-speech on macOS.

## Stack

- Python 3.14+
- piper-tts (installed via `uv pip install piper-tts`)
- macOS `afplay` for audio playback, `pbpaste` for clipboard access
- Voice model: `en_US-kristin-medium.onnx` in project root

## Structure

- `readit` — single-file CLI script (no package structure)

## Commands

- Run: `uv run python readit "text"`
- Interactive mode: `uv run python readit` (launches automatically when no input provided)
- Interactive mode (explicit): `uv run python readit -i`
- Typecheck: `uv run python -m mypy readit --ignore-missing-imports`
- Test (unit): `uv run python -m pytest test_readit.py -v`
- Test (smoke): `echo "test" | uv run python readit -o /dev/null`

## Testing

- **Always write tests first (TDD)** — create failing tests before implementing features
- Test file: `test_readit.py` using `pytest`
- Tests use dependency injection (fake `run`, `stdin`, `stdout`, `stderr`) to avoid real subprocess calls
- The `readit` script (no `.py` extension) is imported via `importlib.machinery.SourceFileLoader`
- Run full test suite before and after every change: `uv run python -m pytest test_readit.py -v`

## Conventions

- Single-file script, no package or module structure
- Use `argparse` for CLI argument parsing
- Use `subprocess` to invoke piper and afplay
- Default model path is resolved relative to the script location
