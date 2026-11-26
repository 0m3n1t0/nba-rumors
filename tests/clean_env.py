"""D90d follow-up (his answer 2026-11-26, class R1: the tests run the same here and on GitHub).
The workflows set settings for the whole run (collect.yml: NBA_FORMATS "receipts" since D90d), and
the "Safety tests" step inherited them, so a test that assumed the format off failed on GitHub only
(run 45772374347). Every test file imports this module before any module of src/, so the tests see
the code's own defaults wherever they run; a test that needs a setting sets it itself."""
import os

WORKFLOW_SETTINGS = ("CHANNEL", "SHORTS_PER_RUN", "CLAUDE_MODEL", "CLAUDE_MODEL_LIGHT", "MUSIC_UNDER_DB",
                     "NBA_FORMATS")
for _name in WORKFLOW_SETTINGS:
    os.environ.pop(_name, None)
