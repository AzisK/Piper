# Reed Roadmap

## Phase 1 — Interactive Enhancements

### 1.1 Command Autocomplete (Tab Completion)
**Effort:** Small · **Priority:** High
**Status:** Partial — `prompt_toolkit` is already in use with `AutoSuggestFromHistory`.

- Add a custom `Completer` to `_make_prompt_session()` that completes `/quit`, `/exit`, `/help`, `/clear`, `/replay` (and future commands like `/pause`, `/stop`)
- Fuzzy-match support so `/h` → `/help`
- Extend to file paths for a future `/open` command

### 1.2 Non-blocking Playback Controller ✅
**Effort:** Medium · **Priority:** High
**Dependencies:** None
**Status:** Done

- ✅ Create `PlaybackController` class with background thread playback
- ✅ Pause/resume via `SIGSTOP`/`SIGCONT` (Unix)
- ✅ Stop via `proc.terminate()`
- ✅ Thread-safe state management with `threading.Lock`
- ✅ Integrated into interactive mode
- ✅ Zero new dependencies (stdlib `threading` + `signal`)

### 1.3 Playback Controls — Pause, Play, Stop
**Effort:** Small · **Priority:** High
**Dependencies:** 1.2 (non-blocking playback) ✅
**Status:** Ready to implement

- Add interactive commands: `/pause`, `/play` (resume), `/stop`
- Wire commands to `PlaybackController.pause()`, `.resume()`, `.stop()`
- Display playback state in prompt (e.g., `▶ Playing…`, `⏸ Paused`)
- Add to autocomplete and `/help` output

---

## Phase 2 — File Format Support

### 2.1 EPUB File Reading ✅
**Effort:** Medium · **Priority:** High
**Dependencies:** None
**Status:** Done

- ✅ Create `_iter_epub_chapters()` yielding `(chapter_number, total_chapters, text)` — mirrors `_iter_pdf_pages()`
- ✅ Wire into `main()` with `.epub` suffix detection alongside the existing `.pdf` path
- ✅ `--pages` flag selects chapters for EPUBs
- ✅ Strip HTML tags from EPUB XHTML content (stdlib `html.parser`)
- ✅ Navigation documents filtered out via spine ordering
- ✅ Zero external dependencies — uses stdlib `zipfile` + `xml.etree.ElementTree`

---

## Phase 3 — Reading Progress & Bookmarks

### 3.1 Save & Resume Reading Position
**Effort:** Medium · **Priority:** Medium
**Dependencies:** Phase 1.2 (stop controls) ✅, Phase 2.1 (epub support desirable) ✅
**Status:** Ready to implement

- Create a JSON bookmarks file at `_data_dir() / "bookmarks.json"`
- Schema:
  ```json
  {
    "/abs/path/to/book.pdf": {
      "page": 12,
      "char_offset": 340,
      "timestamp": "2026-02-18T10:00:00"
    }
  }
  ```
- On `/stop` or `Ctrl-C` during file reading, persist current page + character offset
- Add `--resume` / `-r` flag: `reed -f book.pdf --resume` picks up where it left off
- Add `reed bookmarks` subcommand to list/clear saved positions
- Interactive command: `/bookmarks` to list, `/resume` to continue last file

---

## Phase 4 — Streaming Audio

### 4.1 Streaming TTS Playback
**Effort:** Large · **Priority:** Medium
**Dependencies:** Phase 1.2 (playback controller) ✅
**Status:** Ready to implement

Currently reed generates the full WAV file before playing. Streaming removes that wait.

- Use `piper --output-raw` which streams raw PCM to stdout
- Pipe piper's stdout directly into the audio player's stdin (e.g., `aplay -f S16_LE -r 22050 -c 1` on Linux, `ffplay -f s16le -ar 22050 -ac 1 -` on macOS/Windows)
- On macOS: `afplay` doesn't support stdin; switch to `ffplay` or `sox play` for streaming, or use `python-sounddevice` to play raw PCM frames as they arrive
- Chunk-based playback loop:
  1. Start piper `Popen` with `stdout=PIPE`
  2. Start audio player `Popen` with `stdin=PIPE`
  3. Read chunks from piper → write to player
  4. Integrate with `PlaybackController` for pause/stop mid-stream
- Fallback: keep the current generate-then-play path when streaming isn't available

---

## Phase 5 — Language Expansion

### 5.1 Lithuanian Language Support — Voice Model Training
**Effort:** Large · **Priority:** Medium
**Dependencies:** None (can be started anytime, independent of reed code changes)

No Lithuanian piper voice model exists yet — this requires training one from scratch.

- **Dataset:** source or record a Lithuanian speech dataset (e.g., from Common Voice, M-AILABS, or custom recordings); needs ~2–10 hours of single-speaker audio with transcripts
- **Preprocessing:** segment audio, normalize text, generate phoneme alignments (espeak-ng has Lithuanian support: `lt`)
- **Training:** use [piper-recording-studio](https://github.com/rhasspy/piper-recording-studio) for data collection and [piper training pipeline](https://github.com/rhasspy/piper/blob/master/TRAINING.md) (VITS-based)
  - Train `low`, `medium`, and `high` quality variants
  - Export to `.onnx` format for piper runtime
- **Hosting:** publish the trained model to HuggingFace (or self-host) so `_model_url()` can resolve it
- **Reed integration:** once the model is hosted, add `lt_LT-<voice>-medium` as a downloadable voice; optionally add `--lang lt` shorthand
- **Validation:** native speaker review for pronunciation quality

---

## Summary Timeline

| Phase | Feature | Effort | Dependencies | Status |
|-------|---------|--------|--------------|--------|
| 1.1 | Command autocomplete | Small | — | Partial |
| 1.2 | Non-blocking playback controller | Medium | — | ✅ Done |
| 1.3 | Pause / play / stop commands | Small | 1.2 | Ready |
| 2.1 | EPUB reading | Medium | — | ✅ Done |
| 3.1 | Save & resume position | Medium | 1.2, 2.1 | Ready |
| 4.1 | Streaming audio | Large | 1.2 | Ready |
| 5.1 | Lithuanian voice model training | Large | — | — |

Phase 1.2 is complete ✅. Phases 1.3, 3.1, and 4.1 now have their dependencies satisfied and are ready to implement.
