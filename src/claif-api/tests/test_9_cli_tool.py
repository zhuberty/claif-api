import sys
import os
import pytest
import importlib.util
from pathlib import Path
from unittest import mock
from io import StringIO
from utils.env import TEST_USER_USERNAME, TEST_USER_PASSWORD
from conftest import logger


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
    
    # Redirect stdout to capture print output
    captured_output = StringIO()
    monkeypatch.setattr(sys, 'stdout', captured_output)
    
    access_token_path = project_dir / "access_token.json"

    # Check if access_token.json exists and delete it
    if os.path.exists(access_token_path):
        logger.info("Removing existing access token file")
        os.remove(access_token_path)

    # Call the main function from the dynamically loaded module
    main_module.main()

    # Retrieve the captured output
    output = captured_output.getvalue()

    # Assertions to check if the expected output is in the captured output
    assert output == "Login successful! Access token saved.\n"
    assert os.path.exists(access_token_path)
