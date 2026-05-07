#!/usr/bin/env python3
"""Validate that all EP-XX.md files exist for script/, storyboard/, prompts/ directories.
Usage: python3 validate_batch.py /path/to/project [num_episodes]
Defaults num_episodes to 36 if not provided.
"""
import os
import sys

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    num_eps = int(sys.argv[2]) if len(sys.argv) > 2 else 36

    missing = []
    for i in range(1, num_eps + 1):
        ep = f"EP-{i:02d}"
        for subdir in ["script", "storyboard", "prompts"]:
            fp = os.path.join(base, subdir, f"{ep}.md")
            if not os.path.exists(fp):
                missing.append(f"{subdir}/{ep}.md")

    if missing:
        print(f"\u274c MISSING ({len(missing)} files):")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    else:
        total = num_eps * 3
        print(f"\u2705 All {total} files present ({num_eps} episodes x 3: script + storyboard + prompts)")
        sys.exit(0)

if __name__ == "__main__":
    main()
