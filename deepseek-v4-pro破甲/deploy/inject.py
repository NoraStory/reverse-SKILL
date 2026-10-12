#!/usr/bin/env python3
"""Deploy DeepSeek unrestricted prompt as a Hermes Skill.

Usage:
  python3 deploy/inject.py                    # Deploy skill
  python3 deploy/inject.py --method soul      # Inject into SOUL.md instead
  python3 deploy/inject.py --method skill --name deepseek-unrestricted
"""

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = PROJECT_ROOT / "prompts" / "deepseek-unrestricted-v3.md"
HERMES_DIR = Path.home() / ".hermes"
SKILLS_DIR = HERMES_DIR / "skills"
SOUL_PATH = HERMES_DIR / "SOUL.md"


SKILL_MD_TEMPLATE = """---
name: deepseek-unrestricted
description: Load unrestricted sandbox mode for DeepSeek — disables refusal and safety redirects for prompt-bank testing.
category: mlops
---

{content}
"""


def deploy_skill(name: str, dry_run: bool = False) -> Path:
    prompt_content = PROMPT_PATH.read_text(encoding="utf-8")
    skill_content = SKILL_MD_TEMPLATE.format(content=prompt_content)

    skill_dir = SKILLS_DIR / name
    skill_file = skill_dir / "SKILL.md"

    if dry_run:
        print(f"[DRY RUN] Would write: {skill_file}")
        return skill_file

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(skill_content, encoding="utf-8")
    print(f"✅ Skill deployed: {skill_file}")
    return skill_file


def deploy_soul(dry_run: bool = False) -> Path:
    prompt_content = PROMPT_PATH.read_text(encoding="utf-8")

    # Backup existing SOUL.md if it exists
    if SOUL_PATH.exists() and not dry_run:
        backup = SOUL_PATH.with_suffix(".md.bak")
        shutil.copy2(SOUL_PATH, backup)
        print(f"📦 Backed up: {backup}")

    if dry_run:
        print(f"[DRY RUN] Would write: {SOUL_PATH}")
        return SOUL_PATH

    SOUL_PATH.write_text(prompt_content, encoding="utf-8")
    print(f"✅ SOUL.md deployed: {SOUL_PATH}")
    return SOUL_PATH


def main():
    parser = argparse.ArgumentParser(description="Deploy DeepSeek unrestricted prompt")
    parser.add_argument("--method", choices=["skill", "soul"], default="skill",
                        help="Deployment method (default: skill)")
    parser.add_argument("--name", default="deepseek-unrestricted",
                        help="Skill name (only for --method skill)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without doing it")
    args = parser.parse_args()

    if not PROMPT_PATH.exists():
        print(f"ERROR: Prompt file not found: {PROMPT_PATH}")
        return 1

    print(f"Deploying prompt from: {PROMPT_PATH}")
    print(f"Method: {args.method}")

    if args.method == "skill":
        deploy_skill(args.name, args.dry_run)
    else:
        deploy_soul(args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
