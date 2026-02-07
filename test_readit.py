#!/usr/bin/env python3
"""Tests for readit interactive mode and core functions (TDD)."""

import io
import sys
import types
import argparse
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import importlib.util
import importlib.machinery
import pytest

_readit_path = str(Path(__file__).parent / "readit")
_loader = importlib.machinery.SourceFileLoader("readit", _readit_path)
_spec = importlib.util.spec_from_loader("readit", _loader, origin=_readit_path)
assert _spec
_readit = importlib.util.module_from_spec(_spec)
_readit.__file__ = _readit_path
_loader.exec_module(_readit)
sys.modules["readit"] = _readit


def _make_args(**overrides):
    defaults = dict(
        text=[],
        file=None,
        clipboard=False,
        model=Path(__file__).parent / "en_US-kristin-medium.onnx",
        speed=1.0,
        volume=1.0,
        output=None,
        silence=0.3,
        interactive=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


# ─── interactive_loop tests ───────────────────────────────────────────


class TestInteractiveLoop:
    def test_speaks_each_line_immediately(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO("hello\nworld\nquit\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == ["hello", "world"]
        assert result == 0

    def test_pasted_multiline_batched_together(self):
        from readit import interactive_loop

        spoken = []

        class FakeStdin:
            """Simulates pasting multiple lines at once."""
            def __init__(self, lines):
                self._lines = list(lines)
                self._pos = 0

            def readline(self):
                if self._pos >= len(self._lines):
                    return ""
                line = self._lines[self._pos]
                self._pos += 1
                return line

            def isatty(self):
                return False

        stdin = FakeStdin(["line one\n", "line two\n", "line three\n"])
        result = interactive_loop(
            speak_line=lambda t: spoken.append(t),
            stdin=stdin,
            has_more_input=lambda s: s._pos < len(s._lines),
        )
        assert len(spoken) == 1
        assert "line one" in spoken[0]
        assert "line two" in spoken[0]
        assert "line three" in spoken[0]
        assert result == 0

    def test_eof_exits_cleanly(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO("hello\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == ["hello"]
        assert result == 0

    def test_blank_lines_ignored(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO("\n  \nhello\nquit\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == ["hello"]
        assert result == 0

    def test_quit_commands_case_insensitive(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO("Hello\nEXIT\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == ["Hello"]
        assert result == 0

    def test_exit_command(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO("exit\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == []
        assert result == 0

    def test_colon_q_command(self):
        from readit import interactive_loop

        spoken = []
        stdin = io.StringIO(":q\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == []
        assert result == 0

    def test_bracketed_paste_batched_as_single_speak(self):
        from readit import interactive_loop, PASTE_START, PASTE_END

        spoken = []
        stdin = io.StringIO(
            f"{PASTE_START}line one\nline two\nline three{PASTE_END}\nquit\n"
        )
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert len(spoken) == 1
        assert "line one" in spoken[0]
        assert "line two" in spoken[0]
        assert "line three" in spoken[0]
        assert result == 0

    def test_bracketed_paste_strips_escape_sequences(self):
        from readit import interactive_loop, PASTE_START, PASTE_END

        spoken = []
        stdin = io.StringIO(f"{PASTE_START}hello world{PASTE_END}\nquit\n")
        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=stdin)
        assert spoken == ["hello world"]
        assert PASTE_START not in spoken[0]
        assert PASTE_END not in spoken[0]
        assert result == 0

    def test_bracketed_paste_mode_enabled_on_tty(self):
        from readit import interactive_loop, BRACKETED_PASTE_ON, BRACKETED_PASTE_OFF

        stderr = io.StringIO()

        class FakeTtyStdin:
            def isatty(self):
                return True
            def readline(self):
                return ""
            def fileno(self):
                raise io.UnsupportedOperation

        class FakeStdout:
            def __init__(self):
                self.written = []
            def write(self, s):
                self.written.append(s)
            def flush(self):
                pass

        fake_stdout = FakeStdout()
        interactive_loop(
            speak_line=lambda t: None,
            stdin=FakeTtyStdin(),
            stderr=stderr,
            tty_out=fake_stdout,
        )
        all_output = "".join(fake_stdout.written)
        assert BRACKETED_PASTE_ON in all_output
        assert BRACKETED_PASTE_OFF in all_output

    def test_ctrl_c_handled_gracefully(self):
        from readit import interactive_loop

        spoken = []
        call_count = 0

        class FakeStdin:
            def readline(self):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return "first\n"
                raise KeyboardInterrupt

            def isatty(self):
                return False

        result = interactive_loop(speak_line=lambda t: spoken.append(t), stdin=FakeStdin())
        assert spoken == ["first"]
        assert result == 0


# ─── build_piper_cmd tests ────────────────────────────────────────────


class TestBuildPiperCmd:
    def test_basic_command(self):
        from readit import build_piper_cmd

        cmd = build_piper_cmd(
            model=Path("/models/test.onnx"),
            speed=1.0,
            volume=1.0,
            silence=0.3,
            output=None,
        )
        assert cmd[1:3] == ["-m", "piper"]
        assert "--model" in cmd
        assert "/models/test.onnx" in cmd
        assert "--length-scale" in cmd
        assert "--volume" in cmd
        assert "--sentence-silence" in cmd

    def test_with_output_file(self):
        from readit import build_piper_cmd

        cmd = build_piper_cmd(
            model=Path("/models/test.onnx"),
            speed=1.0,
            volume=1.0,
            silence=0.3,
            output=Path("/out.wav"),
        )
        assert "--output-file" in cmd
        idx = cmd.index("--output-file")
        assert cmd[idx + 1] == "/out.wav"


# ─── speak_text tests ────────────────────────────────────────────────


class TestSpeakText:
    def test_play_path_calls_piper_then_afplay(self):
        from readit import speak_text

        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return types.SimpleNamespace(returncode=0, stderr="")

        args = _make_args()
        speak_text("hi", args, run=fake_run)

        assert len(calls) == 2
        assert calls[0][0][1:3] == ["-m", "piper"]
        assert calls[0][1].get("input") == "hi"
        assert calls[1][0][0] == "afplay"

    def test_output_path_no_afplay(self):
        from readit import speak_text

        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return types.SimpleNamespace(returncode=0, stderr="")

        stdout = io.StringIO()
        args = _make_args(output=Path("/tmp/out.wav"))
        speak_text("hi", args, run=fake_run, stdout=stdout)

        assert len(calls) == 1
        assert "Saved to" in stdout.getvalue()

    def test_piper_error_raises(self):
        from readit import speak_text

        def fake_run(cmd, **kwargs):
            return types.SimpleNamespace(returncode=1, stderr="boom")

        stderr = io.StringIO()
        args = _make_args()
        with pytest.raises(SystemExit):
            speak_text("hi", args, run=fake_run, stderr=stderr)
        assert "boom" in stderr.getvalue()


# ─── main integration tests ──────────────────────────────────────────


class TestMainInteractiveFlag:
    def test_interactive_flag_routes_to_loop(self):
        from readit import main

        loop_called = []

        def fake_loop(**kwargs):
            loop_called.append(True)
            return 0

        with pytest.raises(SystemExit) as exc_info:
            main(
                argv=["-i"],
                interactive_loop_fn=fake_loop,
                run=lambda *a, **k: types.SimpleNamespace(returncode=0, stderr=""),
            )
        assert loop_called
        assert exc_info.value.code == 0

    def test_no_input_defaults_to_interactive(self):
        from readit import main

        loop_called = []

        class FakeTtyStdin:
            def isatty(self):
                return True

            def readline(self):
                return ""

            def fileno(self):
                raise io.UnsupportedOperation("no fileno")

        def fake_loop(**kwargs):
            loop_called.append(True)
            return 0

        with pytest.raises(SystemExit) as exc_info:
            main(
                argv=[],
                interactive_loop_fn=fake_loop,
                run=lambda *a, **k: types.SimpleNamespace(returncode=0, stderr=""),
                stdin=FakeTtyStdin(),
            )
        assert loop_called
        assert exc_info.value.code == 0
