import sys
import importlib.util
from pathlib import Path
from io import StringIO

def load_cli_module(project_dir):
    """
    Dynamically loads the CLI main module from the specified project directory.
    """
    main_path = project_dir / "main.py"
    spec = importlib.util.spec_from_file_location("main", str(main_path))
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    return main_module

def set_input_prompts(monkeypatch, inputs):
    """
    Sets up input prompts using monkeypatch for CLI input simulation.
    """
    input_iter = iter(inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_iter))

def capture_output(monkeypatch):
    """
    Captures CLI output to a StringIO object.
    """
    captured_output = StringIO()
    monkeypatch.setattr(sys, 'stdout', captured_output)
    return captured_output


def assert_output(expected_output, captured_output):
    """
    Asserts if the expected output is part of the captured output.
    """
    output = captured_output.getvalue()
    assert expected_output in output

def patch_sys_argv(monkeypatch, command):
    """
    Patches sys.argv with the given command.
    """
    monkeypatch.setattr(sys, 'argv', ['main.py'] + command)
