# Releases

Here is the summary change log for *ospgrillage*. Full details of commit logs can be found in the [commit history](https://github.com/MonashSmartStructures/ospgrillage/commits/main). The complete machine-readable changelog is maintained in [CHANGELOG.md](https://github.com/MonashSmartStructures/ospgrillage/blob/main/CHANGELOG.md) at the repository root.

## Unreleased (main)

-   `_OpsProxy` dual-mode dispatch layer: single code path for live execution and script serialisation --- no more parallel string-building branches.
-   Load assignment pipeline refactored from format strings to `(func_name, args, kwargs)` tuples; `eval()` removed from the analysis loop.
-   `PatchLoading` vertex validation is now cyclic-rotation-aware.
-   NumPy-style docstrings added to all public functions and classes.
-   Dead code removed from `Analysis.__init__` (9 obsolete command-string attributes, `analysis_arguments` dict).
-   `Envelope.get()` rewritten without `eval()`.
-   Sphinx documentation overhauled: orphaned stubs removed, `sphinx_autodoc_typehints` enabled, `Installation.rst` and `APIdoc.rst` corrected.

## Version 0.4.0 (Aug 2024)

-   GUI-based geometry generator (`ospgui`) for interactive model creation.
-   NumPy 2 and dependency compatibility fixes.

## Version 0.3.2 (Oct 2023)

-   `openseespyvis` replaced by `vfo` for visualisation.
-   Plot module bug fixes.

## Version 0.3.1 (Jan 2023)

-   Package metadata migrated to PEP 621 `pyproject.toml`.
-   Documentation build fixed for `src`-layout packages.

## Version 0.3.0 (Nov 2022)

-   Multi-span orthogonal meshing.
-   Per-group member assignment via refined `set_member()`.
-   Rotational spring support using OpenSeesPy `zeroLength` elements.

## Version 0.2.1 (Apr 2022)

-   Minor bug fixes and citation updates.

## Version 0.2.0 (Mar 2022)

-   Multi-span meshing with stitch elements.
-   Curve-mesh sweep path support.
-   Custom transverse member spacing for oblique meshes.

## Version 0.1.1 (Feb 2022)

-   Bug fixes and documentation corrections following the initial release.

## Version 0.1.0 (Nov 2021)

-   Initial public release.
-   Beam-only, beam-with-rigid-links, and shell-beam hybrid model types.
-   Full load suite: `PointLoad`, `LineLoading`, `PatchLoading`, `NodalLoad`, `CompoundLoad`, `MovingLoad`.
-   Sphinx documentation published to GitHub Pages.
