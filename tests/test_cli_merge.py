"""CLI integration tests for the --merge / merge sub-command."""

from __future__ import annotations

import textwrap

import pytest

from envdiff.cli import main


@pytest.fixture()
def env_files(tmp_path):
    a = tmp_path / "a.env"
    a.write_text(textwrap.dedent("""\
        SHARED=hello
        ONLY_A=1
    """))
    b = tmp_path / "b.env"
    b.write_text(textwrap.dedent("""\
        SHARED=world
        ONLY_B=2
    """))
    return str(a), str(b)


def test_merge_exits_zero(env_files, capsys):
    a, b = env_files
    with pytest.raises(SystemExit) as exc:
        main(["merge", a, b])
    assert exc.value.code == 0


def test_merge_output_contains_all_keys(env_files, capsys):
    a, b = env_files
    with pytest.raises(SystemExit):
        main(["merge", a, b])
    out = capsys.readouterr().out
    assert "SHARED" in out
    assert "ONLY_A" in out
    assert "ONLY_B" in out


def test_merge_write_template(env_files, tmp_path, capsys):
    a, b = env_files
    out_file = tmp_path / "merged.env"
    with pytest.raises(SystemExit):
        main(["merge", a, b, "--output", str(out_file)])
    assert out_file.exists()
    content = out_file.read_text()
    assert "ONLY_A" in content
    assert "ONLY_B" in content


def test_merge_first_strategy(env_files, capsys):
    a, b = env_files
    with pytest.raises(SystemExit):
        main(["merge", a, b, "--strategy", "first"])
    out = capsys.readouterr().out
    # report should still list all keys
    assert "SHARED" in out


def test_merge_requires_at_least_two_files(tmp_path, capsys):
    single = tmp_path / "only.env"
    single.write_text("KEY=val\n")
    with pytest.raises(SystemExit) as exc:
        main(["merge", str(single)])
    # argparse or our validation should reject fewer than 2 files
    assert exc.value.code != 0
