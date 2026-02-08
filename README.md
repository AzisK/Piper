# readit

A CLI that reads text aloud using [piper-tts](https://github.com/rhasspy/piper). Uses the `en_US-kristin-medium` voice by default.

## Requirements

- Python 3.14+
- macOS (uses `afplay` for audio playback and `pbpaste` for clipboard)
- [uv](https://docs.astral.sh/uv/) (for dependency management)
- Rich library for beautiful terminal UI

## Setup

```bash
uv venv
uv pip install -e .
```

Download a voice model and place the `.onnx` and `.onnx.json` files in the project root.

### Available Voice Models

All voice models are hosted on Hugging Face: [https://huggingface.co/rhasspy/piper-voices/tree/main](https://huggingface.co/rhasspy/piper-voices/tree/main)

The file structure follows this pattern: `language/COUNTRY/voice_name/quality/`

**Examples:**

- `en_US-kristin-medium.onnx` (default)
- `en_US-amy-medium.onnx`
- `en_GB-northern_english_male-medium.onnx`
- `de_DE-eva_k-xlow.onnx`

To download a model:

1. Navigate to the model directory on Hugging Face
2. Download the `.onnx` and `.onnx.json` files
3. Place them in the project root

To use a different voice, specify the model path:

```bash
uv run readit -m en_US-amy-medium.onnx "Hello world"
```

## Usage

```bash
# Read text directly
uv run readit "Hello, I will read this for you"

# Read from a file
uv run readit -f article.txt

# Read from clipboard
uv run readit -c

# Read from clipboard (alternative)
pbpaste | uv run readit

# Interactive mode (launches automatically when no input is provided)
uv run readit

# Interactive mode (explicit)
uv run readit -i

# Read from a file (alternative)
cat article.txt | uv run readit

# Save to WAV file instead of playing
uv run readit -o output.wav "Save this"

# Play a saved WAV file
afplay output.wav

# Read text piped from other commands
ls -1 | uv run readit

# Read the output of a command
df -h | uv run readit

# Adjust speed (lower = slower) and volume
uv run readit -s 0.8 -v 1.5 "Slower and louder"
```

### Interactive mode

When launched with no arguments (or with `-i`), readit enters interactive mode. Type or paste text and press Enter to hear it read aloud.

#### Visual Enhancements

- **Beautiful banner** with colors and icons
- **Spinner animation** while generating speech
- **Enhanced status messages** with panels and success indicators

#### Commands

- Type text and press Enter to hear it
- Type `/quit` or `/exit` to stop
- Available commands in interactive mode: `/help`, `/clear`, `/replay`
- Press `Ctrl-D` for EOF to exit

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

### Other Use Cases

**Piped input detection:** When stdin is not a TTY (e.g., when used in a pipeline), the program reads from stdin instead of prompting interactively.

**Common patterns:**

```bash
# Read clipboard content
pbpaste | readit

# Read file content via cat
cat article.txt | readit

# Read command output
ls -1 | readit
df -h | readit

# Chain with other commands
echo "Done!" | readit && open .
find . -name "*.txt" | readit

# Save piped text to WAV and play it
echo "Notification" | readit -o /tmp/notify.wav && afplay /tmp/notify.wav
```

### Add to PATH

```bash
ln -s "$(pwd)/.venv/bin/readit" ~/.local/bin/readit
```
