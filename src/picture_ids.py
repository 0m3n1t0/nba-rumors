"""One photo in two versions counts as ONE picture (owner's rule: nothing is shown twice in a
Short, zoomed or not).

Wikimedia Commons keeps a crop as a separate file: "Celtics at Wizards 2024-12-015.jpg" and
"Celtics at Wizards 2024-12-015 (cropped).jpg" (also "(cropped 2)", "_cropped"). They have
different pages and, being crops, different picture fingerprints, so both used to pass the
repeat check (run 43011651547 showed two photos twice). Here the crop marker is removed from the
file name, so the original and its crops share one identity.

A crop can also be named after the person cut out of it: "Celtics at Wizards 2024-12-036
(White).jpg" is Derrick White cut from "...-036.jpg" (run 43027675858 showed both). A trailing
"(words)" counts as a crop mark only when what is left is a numbered series file (ends in a
digit): "Doc Rivers (coach)" or "Jayson Tatum (2018)" stay their own pictures.

Only Commons photos take part, and only a crop matches: Flickr titles are not unique (many
different photos are simply called "Jaylen Brown"), and two different Commons files without a
crop marker never match by name.
"""

from __future__ import annotations

import re

COMMONS = "Wikimedia Commons"
EXTENSION = re.compile(r"\.(jpe?g|png|webp|tiff?|gif)$", re.I)
NAMED_CROP = re.compile(r"\s*\(\s*([^()\d]+?)\s*\)$")   # "(White)", "(Tatum and Brown)"
CROP_MARK = re.compile(r"[\s_\-]*[\(\[]\s*cropped(?:[\s_\-]*\d+)?\s*[\)\]]|[\s_\-]+cropped(?:[\s_\-]*\d+)?$", re.I)


def base_name(title: str) -> tuple[str, bool]:
    """("celtics at wizards 2024-12-015", True) for "...-015 (cropped).jpg"."""
    t = EXTENSION.sub("", re.sub(r"^File:", "", (title or "").strip(), flags=re.I))
    cropped = bool(CROP_MARK.search(t))
    t = CROP_MARK.sub("", t)
    named = NAMED_CROP.search(t)
    if named and re.search(r"\d$", t[:named.start()].strip()):
        t, cropped = t[:named.start()], True
    return re.sub(r"[\s_]+", " ", t).strip().lower(), cropped


def crop_keys(item: dict) -> tuple[set[str], set[str]]:
    """(what this picture marks as shown, what it must not meet). Empty for non-Commons photos
    and clips: their page / fingerprint checks stay exactly as before."""
    if item.get("kind") != "photo" or item.get("source") != COMMONS or not item.get("title"):
        return set(), set()
    name, cropped = base_name(item["title"])
    if not name:
        return set(), set()
    if cropped:
        return {f"crop:{name}"}, {f"base:{name}", f"crop:{name}"}
    return {f"base:{name}"}, {f"crop:{name}"}


def already_shown(item: dict, shown: set, key: str | None = None) -> bool:
    """The picture (its own key, or another version of the same photo) is already in the Short."""
    k = key if key is not None else (item.get("id") or item.get("page"))
    return (k is not None and k in shown) or bool(crop_keys(item)[1] & shown)


def mark_shown(item: dict, shown: set, key: str | None = None) -> None:
    k = key if key is not None else (item.get("id") or item.get("page"))
    if k is not None:
        shown.add(k)
    shown |= crop_keys(item)[0]
