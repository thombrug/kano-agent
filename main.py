#!/usr/bin/env python3
"""Kano Model Feature Prioritization Agent — CLI entry point."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Load .env from the project root (silently ignored if absent)
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from analysis.schema import KanoInput
from orchestrator import run_kano_pipeline
from report.renderer import render_report


_EXAMPLE_INPUT_PATH = Path(__file__).parent / "example_input.json"


def _load_example_input() -> KanoInput:
    with _EXAMPLE_INPUT_PATH.open() as f:
        data = json.load(f)
    return KanoInput(**data)


def _load_input_from_file(path: str) -> KanoInput:
    with open(path) as f:
        data = json.load(f)
    return KanoInput(**data)


def _load_input_from_stdin() -> KanoInput:
    data = json.load(sys.stdin)
    return KanoInput(**data)


def _save_outputs(output, output_dir: Path, json_only: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "kano_output.json"
    output_dict = output.model_dump()
    output_dict.pop("html_report", None)
    json_path.write_text(json.dumps(output_dict, indent=2))
    print(f"JSON saved to {json_path}", file=sys.stderr)

    if not json_only:
        html = render_report(output)
        html_path = output_dir / "kano_report.html"
        html_path.write_text(html)
        print(f"HTML report saved to {html_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kano Model Feature Prioritization Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run built-in TaskFlow example
  python main.py input.json              # Load features from a JSON file
  echo '{"product_name":"..."}' | python main.py   # Read from stdin
  python main.py --example --json-only   # JSON output only, no HTML
  python main.py --no-save               # Print to stdout, don't write files
""",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to input JSON file (omit to use stdin or --example)",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Use the built-in TaskFlow example input",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Skip HTML report generation",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print output to stdout instead of saving files",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write output files (default: current directory)",
    )
    args = parser.parse_args()

    # --- Load input ---
    if args.example:
        kano_input = _load_example_input()
    elif args.input_file:
        kano_input = _load_input_from_file(args.input_file)
    elif not sys.stdin.isatty():
        kano_input = _load_input_from_stdin()
    else:
        # No input provided: run the built-in example
        print("No input provided — running built-in TaskFlow example.", file=sys.stderr)
        kano_input = _load_example_input()

    # --- Run pipeline ---
    print(f"Running Kano analysis for: {kano_input.product_name}", file=sys.stderr)
    output = run_kano_pipeline(kano_input)

    # --- Output ---
    output_dict = output.model_dump()
    output_dict.pop("html_report", None)
    json_str = json.dumps(output_dict, indent=2)

    if args.no_save:
        print(json_str)
    else:
        output_dir = Path(args.output_dir)
        _save_outputs(output, output_dir, args.json_only)
        # Always print JSON to stdout
        print(json_str)


if __name__ == "__main__":
    main()
