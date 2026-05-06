import pytest

from src.helen_readonly_executor import (
    ReadOnlyExecutionRejected,
    validate_readonly_command,
    run_readonly,
)


def test_git_status_allowed():
    assert validate_readonly_command("git status -sb") == ["git", "status", "-sb"]


def test_pwd_allowed():
    assert validate_readonly_command("pwd") == ["pwd"]


def test_rm_rejected():
    with pytest.raises(ReadOnlyExecutionRejected):
        validate_readonly_command("rm -rf .")


def test_git_commit_rejected():
    with pytest.raises(ReadOnlyExecutionRejected):
        validate_readonly_command("git commit -m nope")


def test_shell_operators_rejected():
    with pytest.raises(ReadOnlyExecutionRejected):
        validate_readonly_command("ls | cat")


def test_find_must_be_bounded_to_known_root():
    with pytest.raises(ReadOnlyExecutionRejected):
        validate_readonly_command("find / -maxdepth 2 -type f")


def test_run_pwd_returns_output():
    result = run_readonly("pwd")
    assert result.returncode == 0
    assert result.stdout.strip()
