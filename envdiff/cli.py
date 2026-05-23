"""Command-line interface for envdiff."""

import argparse
import sys

from envdiff.comparator import compare_env_files
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument(
        "base",
        help="Base .env file (e.g., .env.example)",
    )
    parser.add_argument(
        "compare",
        help="Target .env file to compare against the base",
    )
    parser.add_argument(
        "--check-values",
        action="store_true",
        default=False,
        help="Also report keys that exist in both files but have different values",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = compare_env_files(
            base_path=args.base,
            compare_path=args.compare,
            check_values=args.check_values,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print_report(result, use_color=not args.no_color)
    sys.exit(1 if result.has_differences else 0)


if __name__ == "__main__":
    main()
