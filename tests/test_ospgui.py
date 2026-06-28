"""
Tests for ospgrillage.ospgui.

The GUI module requires PyQt6, which is an optional dependency.  All tests
here are designed to run in headless / CI environments where PyQt6 is absent.
They verify that:

  1. The module imports cleanly even when PyQt6 is not installed.
  2. main() reports the missing dependency and exits with code 1.
"""

import importlib
import sys
import os

import pytest
import xarray as xr

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))


def test_ospgui_importable_without_pyqt6():
    """ospgui must import cleanly even when PyQt6 is not installed."""
    mod = importlib.import_module("ospgrillage.ospgui")
    assert hasattr(mod, "_PYQT6_AVAILABLE")
    # When PyQt6 happens to be installed the flag is True – nothing to
    # assert about absence, but the module still imported cleanly.
    if mod._PYQT6_AVAILABLE:
        pytest.skip("PyQt6 is installed; cannot verify the absent-flag path")


def test_ospgui_main_exits_when_pyqt6_absent(capsys):
    """main() must call sys.exit(1) and write a helpful message to stderr."""
    from ospgrillage.ospgui import main, _PYQT6_AVAILABLE

    if _PYQT6_AVAILABLE:
        pytest.skip("PyQt6 is installed; this test only applies when it is absent")

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "pip install" in captured.err


def test_ospgui_results_kind_classifier():
    """Classification should identify ordinary, IL, and IS datasets robustly."""
    mod = importlib.import_module("ospgrillage.ospgui")

    ordinary = xr.Dataset(
        coords={"Loadcase": ["LC1"], "Node": [1], "Component": ["y"]},
        data_vars={"displacements": (["Loadcase", "Node", "Component"], [[[0.0]]])},
    )
    assert mod._classify_results_kind(ordinary) == "ordinary"

    il_attr = xr.Dataset(coords={"Loadcase": ["LC1"]}, attrs={"influence_type": "line"})
    assert mod._classify_results_kind(il_attr) == "influence_line"

    is_attr = xr.Dataset(coords={"Loadcase": ["LC1"]}, attrs={"influence_type": "surface"})
    assert mod._classify_results_kind(is_attr) == "influence_surface"

    il_dim = xr.Dataset(coords={"InfluenceLine": ["Lane 1"], "Loadcase": [0, 1]})
    assert mod._classify_results_kind(il_dim) == "influence_line"

    is_station = xr.Dataset(
        coords={
            "Loadcase": [0, 1, 2, 3],
            "load_position_longitudinal_station": ("Loadcase", [0, 0, 1, 1]),
            "load_position_transverse_station": ("Loadcase", [0, 1, 0, 1]),
        }
    )
    assert mod._classify_results_kind(is_station) == "influence_surface"

    legacy_line = xr.Dataset(
        coords={
            "Loadcase": [0, 1, 2],
            "load_position_x": ("Loadcase", [0.0, 1.0, 2.0]),
            "load_position_z": ("Loadcase", [0.0, 0.5, 1.0]),
        },
        attrs={"influence_name": "Lane IL"},
    )
    assert mod._classify_results_kind(legacy_line) == "influence_line"


def test_ospgui_resolve_influence_surface_axes():
    mod = importlib.import_module("ospgrillage.ospgui")

    ds_with_station = xr.Dataset(
        coords={
            "Loadcase": [0, 1, 2, 3],
            "load_position_longitudinal_station": ("Loadcase", [0, 0, 1, 1]),
            "load_position_transverse_station": ("Loadcase", [0, 1, 0, 1]),
        }
    )
    assert mod._resolve_influence_surface_axes(ds_with_station, "stations") == (
        "longitudinal_station",
        "transverse_station",
        "station",
    )
    assert mod._resolve_influence_surface_axes(ds_with_station, "physical") == (
        "longitudinal_station",
        "transverse_station",
        "physical",
    )

    ds_without_station = xr.Dataset(
        coords={
            "Loadcase": [0, 1],
            "load_position_x": ("Loadcase", [0.0, 1.0]),
            "load_position_z": ("Loadcase", [2.0, 2.0]),
        }
    )
    assert mod._resolve_influence_surface_axes(ds_without_station, "stations") == (
        "x",
        "z",
        "physical",
    )
    assert mod._resolve_influence_surface_axes(ds_without_station, "physical") == (
        "x",
        "z",
        "physical",
    )


def test_ospgui_nonempty_components_filters_nan_components():
    mod = importlib.import_module("ospgrillage.ospgui")

    da = xr.DataArray(
        data=[
            [[1.0, float("nan"), 2.0], [3.0, float("nan"), 4.0]],
            [[5.0, float("nan"), 6.0], [7.0, float("nan"), 8.0]],
        ],
        dims=("Loadcase", "Node", "Component"),
        coords={
            "Loadcase": [0, 1],
            "Node": [10, 11],
            "Component": ["x", "theta", "y"],
        },
    )
    assert mod._nonempty_components(da) == ["x", "y"]
