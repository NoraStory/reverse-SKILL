#!/usr/bin/env python3
"""Reset/remove the DeepSeek unrestricted prompt.

Usage:
  python3 deploy/reset.py                    # Remove skill
  python3 deploy/reset.py --method soul      # Restore SOUL.md from backup
"""

import argparse
import shutil
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
SKILLS_DIR = HERMES_DIR / "skills"
SOUL_PATH = HERMES_DIR / "SOUL.md"


def reset_skill(name: str, dry_run: bool = False):
    skill_dir = SKILLS_DIR / name
    if not skill_dir.exists():
        print(f"Skill '{name}' not found at {skill_dir}")
        return

    if dry_run:
        print(f"[DRY RUN] Would remove: {skill_dir}")
        return

    shutil.rmtree(skill_dir)
    print(f"✅ Skill removed: {skill_dir}")


def reset_soul(dry_run: bool = False):
    backup = SOUL_PATH.with_suffix(".md.bak")
    if not backup.exists():
        print("No SOUL.md backup found. Nothing to restore.")
        return

    if dry_run:
        print(f"[DRY RUN] Would restore: {backup} -> {SOUL_PATH}")
        return

    shutil.copy2(backup, SOUL_PATH)
    backup.unlink()
    print(f"✅ SOUL.md restored from backup")


def main():
    parser = argparse.ArgumentParser(description="Reset DeepSeek unrestricted prompt")
    parser.add_argument("--method", choices=["skill", "soul"], default="skill")
    parser.add_argument("--name", default="deepseek-unrestricted")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Resetting method: {args.method}")
    if args.method == "skill":
        reset_skill(args.name, args.dry_run)
    else:
        reset_soul(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
