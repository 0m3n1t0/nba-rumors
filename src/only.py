"""Stage 4e (his answers 2026-11-17): the fix after the final read redoes ONE Short's stages
(voice, yt-edit, pictures, final read). NBA_ONLY="short_1" limits a stage to that Short; unset,
every Short is done as before."""
from __future__ import annotations

import os


def wanted(name: str) -> bool:
    only = {x.strip() for x in os.environ.get("NBA_ONLY", "").split(",") if x.strip()}
    return not only or name in only


def active() -> bool:
    return bool(os.environ.get("NBA_ONLY", "").strip())
