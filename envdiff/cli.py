"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_env_files, has_differences
from envdiff.exporter import export_result
from envdiff.merger import merge_env_files, render_merged_template
from envdiff.merge_reporter import print_merge_report
from envdiff.reporter import print_report
from envdiff.validator import validate_env_file
from envdiff.validation_reporter import print_multi_validation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare, validate, and merge .env files.",
    )
    sub = parser.add_subparsers(dest="command")

    # ── compare ──────────────────────────────────────────────────────────────
    cmp = sub.add_parser("compare", help="Compare two .env files.")
    cmp.add_argument("base", help="Base .env file")
    cmp.add_argument("compare", help=".env file to compare against base")
    cmp.add_argument(
        "--export",
        choices=["json", "csv", "markdown"],
        help="Export format",
    )
    cmp.add_argument("--output", "-o", help="Write export to this file instead of stdout")

    # ── validate ─────────────────────────────────────────────────────────────
    val = sub.add_parser("validate", help="Validate one or more .env files.")
    val.add_argument("files", nargs="+", help=".env files to validate")

    # ── merge ─────────────────────────────────────────────────────────────────
    mrg = sub.add_parser("merge", help="Merge multiple .env files into a unified template.")
    mrg.add_argument("files", nargs="+", help=".env files to merge (at least 2 required)")
    mrg.add_argument(
        "--strategy",
        choices=["first", "last"],
        default="last",
        help="Value resolution strategy (default: last)",
    )
    mrg.add_argument("--output", "-o", help="Write merged template to this file")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "compare":
        result = compare_env_files(args.base, args.compare)
        if args.export:
            text = export_result(result, fmt=args.export)
            if args.output:
                with open(args.output, "w") as fh:
                    fh.write(text)
            else:
                print(text, end="")
        else:
            print_report(result, args.base, args.compare)
        sys.exit(1 if has_differences(result) else 0)

    elif args.command == "validate":
        results = {path: validate_env_file(path) for path in args.files}
        print_multi_validation_report(results)
        any_errors = any(r.has_errors() for r in results.values())
        sys.exit(1 if any_errors else 0)

    elif args.command == "merge":
        if len(args.files) < 2:
            parser.error("merge requires at least 2 .env files")

        result = merge_env_files(args.files, strategy=args.strategy)
        print_merge_report(result)

        if args.output:
            template = render_merged_template(result)
            with open(args.output, "w") as fh:
                fh.write(template)
            print(f"Template written to {args.output}")

        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)
