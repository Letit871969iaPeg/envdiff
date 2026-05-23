"""Command-line interface for envdiff."""

import sys
import argparse

from envdiff.parser import parse_env_file
from envdiff.comparator import compare_env_files
from envdiff.reporter import print_report
from envdiff.exporter import export_result
from envdiff.validator import validate_env_file
from envdiff.validation_reporter import print_multi_validation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- compare sub-command (default behaviour) ---
    compare_p = subparsers.add_parser("compare", help="Compare two or more .env files")
    compare_p.add_argument("files", nargs="+", metavar="FILE", help=".env files to compare")
    compare_p.add_argument("--base", default=None, help="Treat this file as the reference baseline")
    compare_p.add_argument(
        "--export",
        choices=["json", "csv", "markdown"],
        default=None,
        help="Export format",
    )
    compare_p.add_argument("--output", "-o", default=None, help="Output file path (default: stdout)")
    compare_p.add_argument("--no-color", action="store_true", help="Disable colored output")

    # --- validate sub-command ---
    validate_p = subparsers.add_parser("validate", help="Validate one or more .env files")
    validate_p.add_argument("files", nargs="+", metavar="FILE", help=".env files to validate")
    validate_p.add_argument("--no-color", action="store_true", help="Disable colored output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        results = [validate_env_file(f) for f in args.files]
        print_multi_validation_report(results, use_color=not args.no_color)
        return 1 if any(r.has_errors for r in results) else 0

    # Default: compare
    if args.command is None or args.command == "compare":
        if not hasattr(args, "files") or not args.files:
            parser.print_help()
            return 1

        base_file = args.base or args.files[0]
        other_files = [f for f in args.files if f != base_file]

        if not other_files:
            print("envdiff: need at least two files to compare.", file=sys.stderr)
            return 1

        base_env = parse_env_file(base_file)
        for other in other_files:
            other_env = parse_env_file(other)
            result = compare_env_files(base_env, other_env, base_path=base_file, other_path=other)
            if args.export:
                export_result(result, fmt=args.export, output_path=args.output)
            else:
                print_report(result, use_color=not args.no_color)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
