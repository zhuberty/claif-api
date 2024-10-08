import os
import pytest
import subprocess
import getpass
from pathlib import Path
from utils.env import (
    CLAIF_API_HOST,
    CLAIF_API_PORT,
    TEST_USER_USERNAME,
    TEST_USER_PASSWORD,
)


@pytest.mark.order(900)
def test_login(monkeypatch):
    inputs = iter([
        TEST_USER_USERNAME,
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr(getpass, 'getpass', lambda _: TEST_USER_PASSWORD)

    # Prepare the environment by copying the current environment and adding PYTHONPATH
    env = os.environ.copy()

    # Set PYTHONPATH to include your project root directory
    project_root = str(Path(__file__).parent.parent)
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{project_root}:{pythonpath}"

    # Use the virtual environment's Python interpreter
    python_executable = Path(env.get("VIRTUAL_ENV", "")) / "bin" / "python"
    if not python_executable.exists():
        python_executable = "python"  # Fallback if not running in a virtual environment

    # Run the CLI tool using subprocess
    result = subprocess.run(
        ["python", "main.py", "--use-alt-port", "login"],
        text=True,
        capture_output=True,
        cwd=str(Path(__file__).parent.parent / "claif_cli"),
    )
    
    assert result.returncode == 0
    assert "Login successful! Access token saved." in result.stdout
