"""D98 (his "კი" 2026-11-26, class R1 "tests are offline"): the tests NEVER call the real Claude.

Every test file imports this module first (test 141 checks that each tests/test_*.py does). On
import it:
  1. refuses to start any program named "claude" from this process, whatever way it is started
     (subprocess.run / Popen / call / check_output, os.system, os.posix_spawn(p)), by its bare name
     or its full path: the call raises RealClaudeCall at once (his answer 1: the guard sits in the
     tests, src/ is untouched, so the pipeline cannot change and a new module is covered too);
  2. puts a fake "claude" first on PATH for every process the tests start (his answer 3): it
     writes down the call and exits with an error at once, so a Python child (eval_run and
     fix_after_read start modules that way) cannot reach the real one either;
  3. fails, under its own name, every test during which a refused call happened, even when the
     code under test catches the error on purpose (evergreen.judge_about swallows everything; his
     answer 2: an error at the call AND the test that made it fails).
A test that needs Claude's answer replaces the call itself (his answer 4: the five tests that
called it before D98 stub it as "Claude did not answer", the case they always checked)."""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
import traceback
import unittest
from pathlib import Path


class RealClaudeCall(RuntimeError):
    """A test tried to start the real Claude CLI."""


CALLS: list[str] = []              # refused in-process calls (with where they came from)
_DIR = Path(tempfile.mkdtemp(prefix="nba_no_claude_"))
LOG = _DIR / "child_calls.log"     # the fake claude's record of calls from child processes
FAKE = _DIR / "bin" / "claude"
EXIT = 97                          # the fake's exit code


def _is_claude(args) -> bool:
    if isinstance(args, (bytes, os.PathLike)):
        args = os.fsdecode(args)
    if isinstance(args, str):
        try:
            words = shlex.split(args)
        except ValueError:
            words = args.split()
    else:
        words = [os.fsdecode(a) if isinstance(a, (bytes, os.PathLike)) else str(a) for a in (args or [])]
    return bool(words) and os.path.basename(words[0]) == "claude"


def _refuse(args) -> None:
    where = " > ".join(f"{Path(f.filename).name}:{f.lineno}" for f in traceback.extract_stack()[-8:-2])
    CALLS.append(f"{args!r} from {where}")
    raise RealClaudeCall(f"D98: a test tried to run the real Claude ({args!r}); stub the call instead")


def _child_calls() -> int:
    try:
        return len(LOG.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0


def mark() -> tuple[int, int]:
    """How many refused calls so far (in this process, in child processes)."""
    return len(CALLS), _child_calls()


def forget_since(m: tuple[int, int]) -> None:
    """Only for the guard's own tests: drop the calls they made on purpose."""
    del CALLS[m[0]:]
    if LOG.exists():
        lines = LOG.read_text(encoding="utf-8").splitlines(keepends=True)
        LOG.write_text("".join(lines[:m[1]]), encoding="utf-8")


def _install() -> None:
    # 2. the fake on PATH, for this process's children
    FAKE.parent.mkdir(parents=True, exist_ok=True)
    FAKE.write_text(f'#!/bin/sh\necho "claude $*" >> "{LOG}"\n'
                    f'echo "D98: tests never run the real Claude" >&2\nexit {EXIT}\n', encoding="utf-8")
    FAKE.chmod(0o755)
    os.environ["PATH"] = str(FAKE.parent) + os.pathsep + os.environ.get("PATH", "")

    # 1. this process: every way of starting a program
    popen_init = subprocess.Popen.__init__

    def guarded_init(self, args, *a, **k):
        if _is_claude(args):
            _refuse(args)
        return popen_init(self, args, *a, **k)
    subprocess.Popen.__init__ = guarded_init

    system = os.system

    def guarded_system(command):
        if _is_claude(command):
            _refuse(command)
        return system(command)
    os.system = guarded_system

    for name in ("posix_spawn", "posix_spawnp"):
        if hasattr(os, name):
            original = getattr(os, name)

            def guarded_spawn(path, argv, *a, _original=original, **k):
                if _is_claude([path]) or _is_claude(argv):
                    _refuse(argv)
                return _original(path, argv, *a, **k)
            setattr(os, name, guarded_spawn)

    # 3. the test that made a call fails, whatever the code did with the error
    run = unittest.TestCase.run

    def guarded_run(self, result=None):
        before = mark()
        result = run(self, result)
        after = mark()
        if result is not None and after != before:
            made = CALLS[before[0]:after[0]] + [f"child process: {x}" for x in
                                                 _child_lines()[before[1]:after[1]]]
            try:
                raise AssertionError("D98: this test called the real Claude:\n  " + "\n  ".join(made))
            except AssertionError:
                result.addFailure(self, sys.exc_info())
        return result
    unittest.TestCase.run = guarded_run


def _child_lines() -> list[str]:
    try:
        return LOG.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


if not getattr(unittest.TestCase.run, "_d98", False):
    _install()
    unittest.TestCase.run._d98 = True
