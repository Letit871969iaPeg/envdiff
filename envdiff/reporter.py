"""Formats and prints EnvDiffResult to the terminal."""

from envdiff.comparator import EnvDiffResult

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def print_report(result: EnvDiffResult, use_color: bool = True) -> None:
    """Print a human-readable diff report to stdout."""
    c = (lambda t, code: _color(t, code)) if use_color else (lambda t, _: t)

    print(c(f"\n=== envdiff: {result.base_file} vs {result.compare_file} ===", BOLD))

    if not result.has_differences:
        print(c("✔  No differences found.", GREEN))
        return

    if result.missing_in_compare:
        print(c(f"\n✘  Keys missing in '{result.compare_file}':", RED))
        for key in result.missing_in_compare:
            print(f"   {c('-', RED)} {key}")
            suggestion = _suggest(key)
            if suggestion:
                print(f"       {c('Suggestion:', CYAN)} {suggestion}")

    if result.missing_in_base:
        print(c(f"\n⚠  Extra keys in '{result.compare_file}' (not in base):", YELLOW))
        for key in result.missing_in_base:
            print(f"   {c('+', YELLOW)} {key}")

    if result.value_mismatches:
        print(c("\n~  Value mismatches:", CYAN))
        for key, (base_val, compare_val) in result.value_mismatches.items():
            print(f"   {c('~', CYAN)} {key}")
            print(f"       base:    {base_val!r}")
            print(f"       compare: {compare_val!r}")

    print()


def _suggest(key: str) -> str:
    """Provide a simple suggestion for a missing key."""
    lower = key.lower()
    if "url" in lower or "uri" in lower:
        return "Set a valid URL, e.g. https://example.com"
    if "secret" in lower or "key" in lower or "token" in lower:
        return "Generate a secure random string (e.g. openssl rand -hex 32)"
    if "port" in lower:
        return "Set a numeric port value, e.g. 8080"
    if "debug" in lower:
        return "Set to 'true' or 'false'"
    return ""
