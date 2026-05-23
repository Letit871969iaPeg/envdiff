"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys

from envdiff.comparator import compare_env_files, has_differences
from envdiff.exporter import ExportFormat, export_result
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument("first", help="Path to the first .env file")
    parser.add_argument("second", help="Path to the second .env file")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv", "markdown"],
        metavar="FORMAT",
        help="Export diff result to FORMAT (json, csv, markdown) and print to stdout",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write exported output to FILE instead of stdout (requires --export)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: D401
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output and not args.export:
        parser.error("--output requires --export")

    try:
        result = compare_env_files(args.first, args.second)
    except FileNotFoundError as exc:
        print(f"envdiff error: {exc}", file=sys.stderr)
        return 2

    if args.export:
        text = export_result(result, args.export)  # type: ignore[arg-type]
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            print(text)
    else:
        print_report(result, use_color=not args.no_color)

    return 1 if has_differences(result) else 0


if __name__ == "__main__":
    sys.exit(main())
