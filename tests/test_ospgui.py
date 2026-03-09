"""
Tests for ospgrillage.ospgui.

The GUI module requires PyQt5, which is an optional dependency.  All tests
here are designed to run in headless / CI environments where PyQt5 is absent.
They verify that:

  1. The module imports cleanly even when PyQt5 is not installed.
  2. main() reports the missing dependency and exits with code 1.
"""

import importlib
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))


def test_ospgui_importable_without_pyqt5():
    """ospgui must import cleanly even when PyQt5 is not installed."""
    mod = importlib.import_module("ospgrillage.ospgui")
    assert hasattr(mod, "_PYQT5_AVAILABLE")
    # In this environment PyQt5 is absent; verify the flag reflects that.
    assert mod._PYQT5_AVAILABLE is False


def test_ospgui_main_exits_when_pyqt5_absent(capsys):
    """main() must call sys.exit(1) and write a helpful message to stderr."""
    from ospgrillage.ospgui import main, _PYQT5_AVAILABLE

    if _PYQT5_AVAILABLE:
        pytest.skip("PyQt5 is installed; this test only applies when it is absent")

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "pip install" in captured.err
