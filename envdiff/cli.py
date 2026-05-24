"""Command-line interface for envdiff."""
from __future__ import annotations

import sys
from typing import List

import click

from envdiff.comparator import compare_env_files, has_differences
from envdiff.reporter import print_report
from envdiff.exporter import export_result
from envdiff.validator import validate_env_file
from envdiff.validation_reporter import print_multi_validation_report
from envdiff.merger import merge_env_files, render_merged_template
from envdiff.merge_reporter import print_merge_report
from envdiff.differ import diff_env_files
from envdiff.diff_reporter import print_diff_report
from envdiff.diff_exporter import export_diff
from envdiff.linter import lint_env_file
from envdiff.lint_reporter import print_multi_lint_report
from envdiff.sorter import sort_env_files
from envdiff.redactor import redact_env
from envdiff.redact_reporter import print_redact_report
from envdiff.grouper import group_env_keys
from envdiff.profiler import profile_env_file
from envdiff.profile_reporter import print_multi_profile_report


def build_parser():
    return main


@click.group()
def main():
    """envdiff – compare and analyse .env files."""


# ── compare ──────────────────────────────────────────────────────────────────
@main.command()
@click.argument("base")
@click.argument("compare")
@click.option("--export", type=click.Choice(["json", "csv", "markdown"]), default=None)
@click.option("--output", "-o", default=None, help="Write export to file instead of stdout")
def compare(base: str, compare: str, export, output):
    """Compare BASE env file against COMPARE env file."""
    result = compare_env_files(base, compare)
    if export:
        text = export_result(result, fmt=export)
        if output:
            with open(output, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            click.echo(text)
    else:
        print_report(result)
    if has_differences(result):
        sys.exit(1)


# ── validate ─────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
def validate(files: List[str]):
    """Validate one or more .env files for syntax issues."""
    results = [validate_env_file(f) for f in files]
    print_multi_validation_report(results)
    if any(r.has_errors for r in results):
        sys.exit(1)


# ── merge ─────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--strategy", type=click.Choice(["last", "first"]), default="last")
@click.option("--output", "-o", default=None)
def merge(files: List[str], strategy: str, output):
    """Merge multiple .env files into a template."""
    result = merge_env_files(list(files), strategy=strategy)
    print_merge_report(result)
    rendered = render_merged_template(result)
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
    else:
        click.echo(rendered)


# ── diff ──────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("left")
@click.argument("right")
@click.option("--export", type=click.Choice(["json", "csv", "markdown"]), default=None)
@click.option("--output", "-o", default=None)
def diff(left: str, right: str, export, output):
    """Show a line-by-line diff between two .env files."""
    result = diff_env_files(left, right)
    if export:
        text = export_diff(result, fmt=export)
        if output:
            with open(output, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            click.echo(text)
    else:
        print_diff_report(result)


# ── lint ──────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
def lint(files: List[str]):
    """Lint one or more .env files for style and correctness."""
    results = [lint_env_file(f) for f in files]
    print_multi_lint_report(results)
    if any(r.has_issues for r in results):
        sys.exit(1)


# ── sort ───────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--output", "-o", default=None)
def sort(files: List[str], output):
    """Check or sort .env files alphabetically."""
    results = sort_env_files(list(files))
    for r in results:
        click.echo(f"{r.path}: {'sorted' if r.is_sorted else 'unsorted'}")
    if output and results:
        from envdiff.sorter import render
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(render(results[0]))


# ── redact ─────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
def redact(files: List[str]):
    """Show redacted view of sensitive keys in .env files."""
    from envdiff.parser import parse_env_file
    for path in files:
        env = parse_env_file(path)
        result = redact_env(path, env)
        print_redact_report(result)


# ── profile ────────────────────────────────────────────────────────────────────
@main.command()
@click.argument("files", nargs=-1, required=True)
def profile(files: List[str]):
    """Profile .env files: key counts, duplicates, value lengths."""
    results = []
    for path in files:
        try:
            results.append(profile_env_file(path))
        except FileNotFoundError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)
    print_multi_profile_report(results)
