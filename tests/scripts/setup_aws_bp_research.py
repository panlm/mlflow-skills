#!/usr/bin/env python3
"""Setup script for aws-best-practice-research skill test.

Creates the project directory (no repo clone needed — the skill generates
output from AWS documentation searches, not from an existing codebase).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def main() -> None:
    project_dir = Path(os.environ["PROJECT_DIR"])
    project_dir.mkdir(parents=True, exist_ok=True)

    # Copy .mcp.json so Claude Code can access MCP servers in the test project
    repo_root = Path(__file__).resolve().parent.parent.parent
    mcp_json = repo_root / ".mcp.json"
    if mcp_json.exists():
        shutil.copy2(mcp_json, project_dir / ".mcp.json")


if __name__ == "__main__":
    main()
