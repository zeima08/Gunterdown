#!/usr/bin/env python3
"""Run Gunterdown directly from a source checkout."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gunterdown.tui import main

raise SystemExit(main())
