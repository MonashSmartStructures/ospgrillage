# Releases

Here is the summary change log for *ospgrillage*. Full details of commit logs can be found in the [commit history](https://github.com/MonashSmartStructures/ospgrillage/commits/main). The complete machine-readable changelog is maintained in [CHANGELOG.md](https://github.com/MonashSmartStructures/ospgrillage/blob/main/CHANGELOG.md) at the repository root.

## Version 0.4.1 (March 2026)

**Code changes**

-   `_OpsProxy` dual-mode dispatch layer: single code path for live execution and script serialisation — no more parallel string-building branches.
-   Load assignment pipeline refactored from format strings to `(func_name, args, kwargs)` tuples; `eval()` removed from the analysis loop.
-   `PatchLoading` vertex validation is now cyclic-rotation-aware.
-   NumPy-style docstrings added to all public functions and classes.
-   Dead code removed from `Analysis.__init__` (9 obsolete command-string attributes, `analysis_arguments` dict).
-   `Envelope.get()` rewritten without `eval()`.
-   Minimum supported Python version raised from 3.9 to 3.10.
-   30 new tests added; overall coverage rises from 71 % to 75 %.

**Documentation overhaul**

-   Navigation restructured into four top-level sections: Getting Started, User Guide, API Reference, and Additional Resources.
-   API reference split into per-module pages; Load module further subdivided into load types, load cases, and moving loads.
-   All source files renamed to match their page titles; source folder renamed `rst/` → `pages/`.
-   Pandoc conversion artefacts removed throughout (escaped characters, malformed directives, broken anchors, Pandoc grid tables).
-   Docstrings improved for `PatchLoading`, `LoadCase`, `CompoundLoad`, and `OspGrillage`.
-   *Getting Results* page rewritten with an xarray concept overview and annotated examples.
-   Contributing guidelines page added; JOSS citation added to front page.
-   Jupyter example notebooks cleaned up (version-output cells and trailing empty cells removed).

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
