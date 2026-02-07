# readit

A CLI that reads text aloud using [piper-tts](https://github.com/rhasspy/piper). Uses the `en_US-kristin-medium` voice by default.

## Requirements

- Python 3.14+
- macOS (uses `afplay` for audio playback and `pbpaste` for clipboard)
- [uv](https://docs.astral.sh/uv/) (for dependency management)

## Setup

```bash
uv venv
uv pip install piper-tts
```

Download a voice model (e.g., [kristin](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/kristin/medium)) and place the `.onnx` and `.onnx.json` files in the project root.

## Usage

```bash
# Read text directly
uv run python readit "Hello, I will read this for you"

# Pipe from stdin
echo "Some long text" | uv run python readit

# Read from a file
uv run python readit -f article.txt

# Read from clipboard
uv run python readit -c

# Interactive mode (launches automatically when no input is provided)
uv run python readit

# Interactive mode (explicit)
uv run python readit -i

# Save to WAV file instead of playing
uv run python readit -o output.wav "Save this"

# Play a saved WAV file
afplay output.wav

# Adjust speed (lower = slower) and volume
uv run python readit -s 0.8 -v 1.5 "Slower and louder"
```

### Interactive mode

When launched with no arguments (or with `-i`), readit enters interactive mode. Type or paste text and press Enter to hear it read aloud.

- **Pasted multi-line text** is batched and read as a single block (bracketed paste mode is enabled automatically)
- Type `quit`, `exit`, or `:q` to stop
- Ctrl-D (EOF) also exits

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-f`, `--file` | Read text from a file | — |
| `-c`, `--clipboard` | Read text from clipboard | — |
| `-m`, `--model` | Path to voice model | `en_US-kristin-medium.onnx` |
| `-s`, `--speed` | Speech speed (lower = slower) | `1.0` |
| `-v`, `--volume` | Volume multiplier | `1.0` |
| `-i`, `--interactive` | Interactive mode: type/paste text to read | — |
| `-o`, `--output` | Save to WAV file instead of playing | — |
| `--silence` | Seconds of silence between sentences | `0.3` |

### Add to PATH

```bash
ln -s "$(pwd)/readit" ~/.local/bin/readit
```
