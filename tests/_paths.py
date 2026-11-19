"""Put the skill's scripts folder on sys.path. Every test module imports this first."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "research-paper-writing" / "scripts"
STUDY_SCRIPTS = ROOT / "research-study-design" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
for folder in (SCRIPTS, STUDY_SCRIPTS):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
