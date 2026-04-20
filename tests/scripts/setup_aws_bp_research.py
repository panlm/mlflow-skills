#!/usr/bin/env python3
"""Setup script for aws-best-practice-research skill test.

Creates the project directory (no repo clone needed — the skill generates
output from AWS documentation searches, not from an existing codebase).
"""
from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    project_dir = Path(os.environ["PROJECT_DIR"])
    project_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
