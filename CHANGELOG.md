# Changelog

All notable changes to *ospgrillage* are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and
the project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [0.4.1] — 2026-03-09

### Added
- 30 new tests across `test_load.py`, `test_material.py`, `test_member.py`, and the
  new `test_ospgui.py`; overall coverage rises from 71 % to 75 %.
- `test_ospgui.py`: new test module verifying the PyQt5-absent import guard and
  graceful `main()` exit.

### Changed
- Minimum supported Python version raised from 3.9 to 3.10, allowing use of
  PEP 604 `X | Y` union-type syntax throughout the codebase.
  **Note:** Python 3.9 reached end-of-life in October 2025.
- Sphinx documentation source converted from reStructuredText to Markdown using
  MyST-Parser; `myst-parser` added to the docs-build dependency list.
- `_OpsProxy` dual-mode dispatch pattern: a thin proxy around OpenSeesPy that either
  executes commands live or serialises them to a `.tcl`/`.py` script file, controlled
  by a single `py_file` flag on `create_grillage`.
- `_OpsProxy._dispatch(call)` helper that routes pre-built `(name, args, kwargs)`
  tuples through the proxy, eliminating all `eval()` in the analysis path.
- Load assignment pipeline refactored from format-string building to
  `(func_name, args, kwargs)` tuples throughout `_assign_load_to_four_node()`,
  `_distribute_load_types_to_model()`, `Analysis._time_series_command()`, and
  `Analysis._pattern_command()`; `evaluate_analysis()` dispatches via `_dispatch()`.
- `Envelope.get()` now uses `getattr(da, self.selected_xarray_command)(dim="Loadcase")`
  instead of `eval()`; the dead format-string infrastructure in `Envelope.__init__`
  has been removed.
- `ospgui.py` log output converted from `print()` to `logging.getLogger(__name__)`.
- NumPy-style docstrings added to all public functions and classes across every
  source module (`osp_grillage.py`, `load.py`, `mesh.py`, `members.py`, `utils.py`,
  `postprocessing.py`).
- `sphinx_autodoc_typehints` added to Sphinx extension list so type annotations are
  rendered automatically in the HTML docs.

### Removed
- Nine dead command-string attributes from `Analysis.__init__` that became obsolete
  after the proxy refactor (`wipe_command`, `numberer_command`, `system_command`,
  `constraint_command`, `algorithm_command`, `analyze_command`, `analysis_command`,
  `intergrator_command`, `sensitivity_integrator_command`, `remove_pattern_command`).
- Dead `analysis_arguments` dict from `Analysis.__init__`.
- Unused `scipy.interpolate` imports from `postprocessing.py`.
- Five orphaned RST stub pages that referenced non-existent autodoc targets
  (`Analysis.rst`, `Material.rst`, `Loads.rst`, `GrillageMember.rst`, `OpsGrillage.rst`).

### Fixed
- `Loads.get_magnitude()` crashed with `AttributeError` on `None` items in
  `point_list`; now skips undefined load points.
- `ospgui` crashed on import with `ModuleNotFoundError: No module named 'PyQt5'`
  in environments without the optional GUI dependency; now exits gracefully with
  an actionable error message.
- `_OpsProxy` `str | None` annotation caused `TypeError` on Python ≤ 3.9 at import
  time (resolved by the Python 3.10 minimum bump).
- Compound `NodalLoad` bug in `_distribute_load_types_to_model()` where
  `load_str += string` was spreading individual characters into the list; now
  correctly appends a single tuple.
- `PatchLoading` cyclic-rotation-aware vertex validation via `_is_cyclic_rotation()`
  helper: any valid starting point of the CCW polygon is now accepted.
- `NodalLoad.get_nodal_load_call()` returning a structured tuple instead of a raw
  command string.
- `stitch_slab_x_spacing` typo corrected throughout `ospgui.py` (was `stich`).
- Docs build workflow now installs `myst-parser`; `sphinx_docs_to_gh_pages.yml`
  modernised to use `peaceiris/actions-gh-pages@v4`.

---

## [0.4.0] — 2024-08-06

### Added
- GUI-based geometry generator (`ospgui`) for interactive model creation without
  writing Python code ([#128](https://github.com/MonashSmartStructures/ospgrillage/pull/128)).

### Fixed
- NumPy 2 and upstream dependency compatibility issues
  ([#126](https://github.com/MonashSmartStructures/ospgrillage/pull/126)).
- GitHub Pages deployment workflow
  ([#109](https://github.com/MonashSmartStructures/ospgrillage/pull/109)).

---

## [0.3.2] — 2023-10-20

### Changed
- Replaced deprecated `openseespyvis` visualisation back-end with `vfo`
  ([#74](https://github.com/MonashSmartStructures/ospgrillage/pull/74)).
- Mass and displacement interpolator updated
  ([#72](https://github.com/MonashSmartStructures/ospgrillage/pull/72)).
- Code reformatted with `black`
  ([#73](https://github.com/MonashSmartStructures/ospgrillage/pull/73)).

### Fixed
- Plot module errors following the `vfo` migration
  ([#107](https://github.com/MonashSmartStructures/ospgrillage/pull/107)).

---

## [0.3.1] — 2023-01-04

### Changed
- Package metadata migrated from `setup.cfg` to PEP 621 `pyproject.toml`.
- Documentation build fixed for `src`-layout packages.

---

## [0.3.0] — 2022-11-14

### Added
- Multi-span orthogonal meshing feature.
- Refined member assignment: `set_member()` now supports per-group overrides for
  common grillage elements with multiple groups.
- Rotational spring support via a dedicated `Material` type backed by OpenSeesPy's
  `zeroLength` element.

---

## [0.2.1] — 2022-04-10

### Fixed
- Minor paper / citation tweaks; dependency version pins.

---

## [0.2.0] — 2022-03-xx

### Added
- Multi-span meshing: intermediate edge construction lines and stitch elements
  between spans.
- Curve-mesh support: sweep path can now follow a curved line.
- Custom transverse member spacings for oblique meshes.
- Example Jupyter notebooks restructured under `docs/source/notebooks/`.

---

## [0.1.1] — 2022-02-xx

### Fixed
- Miscellaneous bug fixes and documentation corrections following initial release.

---

## [0.1.0] — 2021-11-xx

### Added
- Initial public release.
- Beam-only, beam-with-rigid-links, and shell-beam hybrid model types.
- Orthogonal and oblique meshing algorithms.
- Full load suite: `PointLoad`, `LineLoading`, `PatchLoading`, `NodalLoad`,
  `CompoundLoad`, `MovingLoad`.
- `LoadCase`, `LoadModel`, and `Path` helpers.
- `Envelope` and `PostProcessor` post-processing utilities.
- Sphinx documentation published to GitHub Pages.
