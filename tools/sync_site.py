#!/usr/bin/env python3
"""
Sync the working site source to the two places it needs to go.

  DELAY/site/  ->  the git repo at ~/Desktop/aarondelaycounseling-site
               ->  the local preview server root

Working source of truth is always DELAY/site/. Nothing should be edited
directly in the repo folder, or the next sync will overwrite it.

Usage:
  python3 tools/sync_site.py            sync only
  python3 tools/sync_site.py --status   sync, then show git status and branch
"""

import os, re, shutil, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "DELAY", "site")
REPO = os.path.expanduser("~/Desktop/aarondelaycounseling-site")

# The sandboxed preview server cannot read ~/Desktop, so it serves a copy.
# Read the served path out of the running server's own script rather than
# guessing: there are dozens of stale scratchpad dirs from past sessions and
# picking one by glob order silently syncs into the wrong place.
PREVIEW = None
_newest = None
for script in glob.glob("/private/tmp/claude-501/*/*/scratchpad/serve.py"):
    mtime = os.path.getmtime(script)
    if _newest is None or mtime > _newest:
        m = re.search(r'ROOT\s*=\s*["\'](.+?)["\']', open(script, encoding="utf-8").read())
        if m:
            PREVIEW, _newest = m.group(1), mtime

SKIP = {".git", ".DS_Store"}


def copy_tree(src, dst):
    os.makedirs(dst, exist_ok=True)
    # remove files in dst that no longer exist in src, but never touch .git
    for name in os.listdir(dst):
        if name in SKIP:
            continue
        target = os.path.join(dst, name)
        if not os.path.exists(os.path.join(src, name)):
            shutil.rmtree(target) if os.path.isdir(target) else os.remove(target)
    for name in os.listdir(src):
        if name in SKIP:
            continue
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(s):
            copy_tree(s, d)
        else:
            shutil.copy2(s, d)


def main():
    if not os.path.isdir(SRC):
        sys.exit(f"missing source: {SRC}")

    copy_tree(SRC, REPO)
    print(f"synced -> {REPO}")

    if PREVIEW:
        copy_tree(SRC, PREVIEW)
        print(f"synced -> preview server (http://localhost:8080)")
    else:
        print("preview server root not found, skipped")

    for junk in glob.glob(os.path.join(REPO, "**", ".DS_Store"), recursive=True):
        os.remove(junk)

    if "--status" in sys.argv:
        branch = subprocess.run(["git", "-C", REPO, "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        status = subprocess.run(["git", "-C", REPO, "status", "--short"],
                                capture_output=True, text=True).stdout.strip()
        print(f"\nbranch: {branch}")
        print(status if status else "(no changes)")


if __name__ == "__main__":
    main()
