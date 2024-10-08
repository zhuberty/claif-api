import sys
import os
import pytest
import importlib.util
from pathlib import Path
from unittest import mock
from utils.env import TEST_USER_USERNAME, TEST_USER_PASSWORD

@pytest.mark.order(900)
def test_login(monkeypatch):
    # Set the directory to ../claif_cli and add it to sys.path
    project_dir = Path(__file__).parent.parent / "claif_cli"
    os.chdir(project_dir)
    sys.path.insert(0, str(project_dir))

    # Dynamically import main from ../claif_cli/main.py
    main_path = project_dir / "main.py"
    spec = importlib.util.spec_from_file_location("main", str(main_path))
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)

    # Patch the input function to simulate the CLI tool input
    inputs = iter([TEST_USER_USERNAME])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    # Patch sys.argv for the command-line arguments, including the password
    monkeypatch.setattr(sys, 'argv', ['main.py', '--use-alt-port', 'login', '--password', TEST_USER_PASSWORD])
    
    # Call the main function from the dynamically loaded module
    main_module.main()
