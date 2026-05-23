# envdiff

> Compare `.env` files across environments and surface missing or mismatched keys with suggestions.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git && cd envdiff && pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DATABASE_URL       (found in .env.development)
  - DEBUG              (found in .env.development)

Mismatched keys:
  - APP_ENV            development  →  production
  - LOG_LEVEL          debug        →  (not set)

Suggestions:
  → Add DATABASE_URL to .env.production
  → Verify LOG_LEVEL is intentionally unset in production
```

You can also compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

### Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with non-zero code if any differences are found |
| `--ignore KEY` | Exclude a specific key from comparison |
| `--format json` | Output results as JSON |

---

## License

MIT © [yourname](https://github.com/yourname)