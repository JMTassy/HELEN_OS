import pytest
from helen.policy import check_shell_command, PolicyViolation


def test_allowed_command():
    check_shell_command("pwd", policy={
        "shell": {"allow": ["pwd", "ls"], "deny": ["rm"]}
    })


def test_denied_command():
    with pytest.raises(PolicyViolation):
        check_shell_command("rm -rf /", policy={
            "shell": {"allow": ["pwd"], "deny": ["rm"]}
        })


def test_unknown_command_denied():
    with pytest.raises(PolicyViolation):
        check_shell_command("git status", policy={
            "shell": {"allow": ["pwd", "ls"], "deny": ["rm"]}
        })
