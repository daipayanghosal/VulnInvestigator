"""
scripts/deploy_ghpages.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Builds the Apple UI frontend and deploys the static dist bundle
directly to the `gh-pages` branch on GitHub.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_FRONTEND = _ROOT / "frontend"
_DIST = _FRONTEND / "dist"

def main() -> int:
    print("[1/3] Building Apple-design static frontend...")
    res = subprocess.run(["npm", "run", "build"], cwd=str(_FRONTEND), shell=True)
    if res.returncode != 0:
        print("Build failed.")
        return res.returncode

    if not (_DIST / "index.html").exists():
        print(f"Error: {_DIST / 'index.html'} does not exist.")
        return 1

    print("[2/3] Initialising git repository in dist...")
    git_dir = _DIST / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    def run_git(args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(["git"] + args, cwd=str(_DIST), check=True, capture_output=True, text=True)

    try:
        run_git(["init"])
        run_git(["checkout", "-b", "gh-pages"])
        run_git(["add", "-A"])
        run_git(["commit", "-m", "deploy: update GitHub Pages build"])

        # Fetch remote url from parent repository
        parent_remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(_ROOT),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        print(f"[3/3] Pushing to origin/gh-pages...")
        run_git(["push", "-f", parent_remote, "gh-pages"])
        print("\nSuccessfully deployed static bundle to GitHub Pages branch (gh-pages)!")
        print("Live URL: https://daipayanghosal.github.io/VulnInvestigator/")
    finally:
        if git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
