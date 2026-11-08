"""Installs the English language model the voice engine (Kokoro / misaki) needs: en_core_web_sm.

Without it, tts.py tries to download it itself from GitHub releases, and when GitHub's
download server times out (HTTP 504) the whole run fails. This script makes that impossible:
  1. already installed -> done
  2. a copy kept in the GitHub cache (~/.cache/voice-wheels) -> install it, no download at all
  3. download with retries from TWO places: Hugging Face (spacy/en_core_web_sm, the same
     servers the voice model comes from) and GitHub releases; the first that works wins,
     and the file is kept in the cache so the next runs never download it again
It exits with an error only if every source failed several times.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

CACHE = Path.home() / ".cache" / "voice-wheels"
SOURCES = [
    "https://huggingface.co/spacy/en_core_web_sm/resolve/main/en_core_web_sm-any-py3-none-any.whl",
    "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
]


def installed() -> bool:
    return importlib.util.find_spec("en_core_web_sm") is not None


def pip_install(wheel: Path) -> bool:
    return subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", str(wheel)]).returncode == 0


def proper_name(raw: Path) -> Path:
    """pip needs the real version in the file name; read it from the wheel's own metadata."""
    with zipfile.ZipFile(raw) as z:
        meta = next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))
        version = re.search(r"^Version:\s*(\S+)", z.read(meta).decode(), re.M).group(1)
    final = CACHE / f"en_core_web_sm-{version}-py3-none-any.whl"
    raw.replace(final)
    return final


def download(url: str) -> Path | None:
    tmp = CACHE / "download.tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nba-rumors-pipeline"})
        with urllib.request.urlopen(req, timeout=120) as r:
            tmp.write_bytes(r.read())
        return proper_name(tmp)
    except Exception as exc:
        print(f"[!] {url.split('/')[2]}: {exc}")
        return None


def main() -> None:
    if installed():
        print("[+] en_core_web_sm already installed")
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    for wheel in sorted(CACHE.glob("en_core_web_sm-*.whl")):
        if pip_install(wheel) and installed():
            print(f"[+] installed from cache: {wheel.name}")
            return
    for attempt in range(1, 5):
        for url in SOURCES:
            wheel = download(url)
            if wheel and pip_install(wheel) and installed():
                print(f"[+] installed {wheel.name} from {url.split('/')[2]} (kept in cache for next runs)")
                return
        wait = 20 * attempt
        print(f"[i] attempt {attempt} failed, retrying in {wait}s")
        time.sleep(wait)
    sys.exit("[!] the English voice model could not be downloaded from any source")


if __name__ == "__main__":
    main()
