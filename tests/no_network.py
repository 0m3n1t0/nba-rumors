"""D99 (his "კი" to all five recommendations 2026-11-26 01:33 Tbilisi, class R1 "tests are offline"):
the tests NEVER reach the network.

Every test file imports this module first, right after no_real_claude (test 142 checks that each
tests/test_*.py does). On import it:
  1. refuses, in this process, every name lookup (getaddrinfo, gethostbyname(_ex), gethostbyaddr)
     and every connection or send (socket connect / connect_ex / sendto / sendmsg, so also
     create_connection, urllib, http.client, ssl) to ANY address, 127.0.0.1 included (his answer 2:
     here the internet goes through a proxy on 127.0.0.1); the call raises NetworkCall at once
     (his answer 1: the guard sits in the tests, src/ is untouched);
  2. fails, under its own name, every test during which a refused call happened, even when the
     code under test swallows the error (his answer 3: media.commons_videos catches everything);
  3. points every proxy variable of the processes the tests start at a closed local port, so a
     child (git, curl, a python urllib) that tries the internet fails at once (his answer 4).
A test whose code would search the network replaces the search itself (his answer 5: test 104's
Commons search answers "nothing found")."""
from __future__ import annotations

import os
import socket
import sys
import traceback
import unittest
from pathlib import Path


class NetworkCall(OSError):
    """A test tried to reach the network."""


CALLS: list[str] = []          # refused calls (what, and where they came from)
DEAD_PROXY = "http://127.0.0.1:9"     # a closed local port: a child's internet call fails at once
PROXY_VARS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")


def _refuse(what: str, target) -> None:
    where = " > ".join(f"{Path(f.filename).name}:{f.lineno}" for f in traceback.extract_stack()[-8:-2])
    CALLS.append(f"{what} {target!r} from {where}")
    raise NetworkCall(f"D99: a test tried to reach the network ({what} {target!r}); stub the call instead")


def mark() -> int:
    """How many refused calls so far."""
    return len(CALLS)


def forget_since(m: int) -> None:
    """Only for the guard's own tests: drop the calls they made on purpose."""
    del CALLS[m:]


def _install() -> None:
    # 3. the processes the tests start: every proxy variable at a closed port, no exceptions
    for name in PROXY_VARS:
        os.environ[name] = DEAD_PROXY
    for name in ("NO_PROXY", "no_proxy"):
        os.environ.pop(name, None)

    # 1. this process: name lookups
    for name in ("getaddrinfo", "gethostbyname", "gethostbyname_ex", "gethostbyaddr"):
        def guarded_lookup(host, *a, _name=name, **k):
            _refuse(_name, host)
        setattr(socket, name, guarded_lookup)

    # 1. this process: connections and sends, any address
    for name in ("connect", "connect_ex"):
        def guarded_connect(self, address, _name=name):
            _refuse(_name, address)
        setattr(socket.socket, name, guarded_connect)

    def guarded_sendto(self, data, *args):
        _refuse("sendto", args[-1] if args else None)
    socket.socket.sendto = guarded_sendto

    def guarded_sendmsg(self, buffers, ancdata=(), flags=0, address=None):
        _refuse("sendmsg", address)
    socket.socket.sendmsg = guarded_sendmsg

    # 2. the test that made a call fails, whatever the code did with the error
    run = unittest.TestCase.run

    def guarded_run(self, result=None):
        before = mark()
        result = run(self, result)
        after = mark()
        if result is not None and after != before:
            try:
                raise AssertionError("D99: this test reached the network:\n  " + "\n  ".join(CALLS[before:after]))
            except AssertionError:
                result.addFailure(self, sys.exc_info())
        return result
    guarded_run._d99 = True
    unittest.TestCase.run = guarded_run


if not getattr(socket.getaddrinfo, "_d99", False):
    _install()
    socket.getaddrinfo._d99 = True
