"""Command-line interface for PHA Tool."""

from __future__ import annotations

import argparse
from pathlib import Path

from pha_tool.io import read_worksheet, write_scored_rows, write_template
from pha_tool.worksheet import score_rows


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level command parser."""

    parser = argparse.ArgumentParser(
        prog="pha-tool",
        description="Create and score Process Hazard Analysis worksheets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    template_parser = subparsers.add_parser("template", help="write an empty worksheet CSV")
    template_parser.add_argument("path", type=Path, help="path for the worksheet template")

    score_parser = subparsers.add_parser("score", help="score a worksheet CSV")
    score_parser.add_argument("path", type=Path, help="worksheet CSV to score")
    score_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="path for the scored worksheet CSV",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "template":
        write_template(args.path)
        return 0

    if args.command == "score":
        rows = read_worksheet(args.path)
        write_scored_rows(args.output, score_rows(rows))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
