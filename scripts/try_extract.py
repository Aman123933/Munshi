#!/usr/bin/env python3
"""
scripts/try_extract.py

Test runner for Munshi extraction layer.
Usage:
    python scripts/try_extract.py "8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2."
    python scripts/try_extract.py "8A में आज 3 अनुपस्थित - कबीर, अयान, काव्या। पाठ 4 पढ़ाया। गृहकार्य अभ्यास 4.1।"
    python scripts/try_extract.py "9A: 2 absent the - Arjun, Dev. Aaj chapter 5 Arithmetic Progressions padhaya. Homework exercise 5.1."
"""

import os
import sys
from datetime import date
from pathlib import Path

# Ensure backend is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env if present
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from app.extraction.factory import CompositeExtractionClient
from app.extraction.verifier import verify_fields


def run_extraction(text: str, today_str: str = "2026-11-21"):
    print("\n" + "=" * 65)
    print(f"INPUT MESSAGE:\n  {text}")
    print(f"TODAY: {today_str}")
    print("-" * 65)

    client = CompositeExtractionClient()
    result, mode_used = client.extract_with_mode(text, today=today_str)
    verified = verify_fields(text, result.fields)

    print(f"EXTRACTION MODE USED: {mode_used.upper()}")
    print(f"DETECTED LANGUAGE:    {result.language.upper()}")
    print(f"TOTAL FIELDS:         {len(verified)}")
    print("-" * 65)
    print(f"{'TYPE':<16} | {'OFFSETS':<8} | {'STATUS':<7} | {'QUOTE':<20} | {'VALUE / ROMAN'}")
    print("-" * 65)

    for f in verified:
        offsets = f"[{f.start},{f.end})" if f.start is not None else "[?,?)"
        roman_info = f" (roman: {f.roman})" if f.roman else ""
        val_display = f"{f.value}{roman_info}"
        print(f"{f.type:<16} | {offsets:<8} | {f.status:<7} | {f.quote:<20} | {val_display}")

    print("=" * 65 + "\n")
    return verified


def main():
    if len(sys.argv) > 1:
        message = sys.argv[1]
        run_extraction(message)
    else:
        # Run three representative test messages: English, Devanagari Hindi, and Hinglish
        sample_messages = [
            ("ENGLISH", "8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2."),
            ("DEVANAGARI HINDI", "8A में आज 3 अनुपस्थित - कबीर, अयान, काव्या। पाठ 4 पढ़ाया। गृहकार्य अभ्यास 4.1।"),
            ("HINGLISH", "9A: 2 absent the - Arjun, Dev. Aaj chapter 5 Arithmetic Progressions padhaya. Homework exercise 5.1."),
        ]
        for label, msg in sample_messages:
            print(f">>> DEMO EXTRACTION: {label} <<<")
            run_extraction(msg)


if __name__ == "__main__":
    main()
