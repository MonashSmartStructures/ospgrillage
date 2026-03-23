# Releases

Here is the summary change log for *ospgrillage*. Full details of commit logs can be found in the [commit history](https://github.com/MonashSmartStructures/ospgrillage/commits/main). The complete machine-readable changelog is maintained in [CHANGELOG.md](https://github.com/MonashSmartStructures/ospgrillage/blob/main/CHANGELOG.md) at the repository root.

## Version 0.6.0 (March 2026)

A visualisation and post-processing release: shell element stress
resultant contour plots, self-contained results files, and a GUI results
viewer make it possible to inspect shell-beam hybrid models end-to-end.

**Shell contour plots (`plot_srf`)**

-   New {func}`~ospgrillage.postprocessing.plot_srf` function renders
    contour plots over the shell mesh for three families of component:
    shell forces (`Vx`–`Mz`), nodal displacements (`Dx`, `Dy`, `Dz`),
    and section stress resultants (`N11`, `N22`, `N12`, `M11`, `M22`,
    `M12`, `Q13`, `Q23`).
-   Supports both Plotly (interactive 3-D) and matplotlib (2-D) backends.
-   Shell contours can be composed with beam diagrams by passing the
    Plotly figure as `ax=` to `plot_bmd` / `plot_sfd` / `plot_tmd` /
    `plot_def`.
-   Configurable colorscale, opacity, and colorbar display.

**Stress extraction pipeline**

-   `extract_grillage_responses()` now queries `eleResponse(tag, "stresses")`
    for shell elements, capturing 8 stress resultants at 4 Gauss points
    (32 values per element).
-   New `stresses_shell` DataArray in the results Dataset (dimensions:
    Loadcase × Element × Stress) with a dedicated `Stress` coordinate to
    avoid dimension conflicts with `forces_shell`.

**Self-contained results files**

-   `.nc` files saved via `get_results(save_filename=...)` now embed node
    coordinates and member-element connectivity, making them fully
    self-contained.
-   {func}`~ospgrillage.postprocessing.model_proxy_from_results` creates a
    lightweight `_ModelProxy` from a saved Dataset — all plotting
    functions work without the original `OspGrillage` object.

**GUI results viewer**

-   **File > Open Results (.nc)** loads saved results into an interactive
    viewer with BMD, SFD, TMD, Deflection, and Shell Contour tabs.
-   Shell Contour tab provides component, colorscale, and overlay
    controls (compose shell contours with beam diagrams).
-   Contour controls grey out when a non-contour tab is active and hide
    entirely for non-shell models.

**GUI fixes**

-   Disabled combo-box pseudo-state styles for better visual feedback.
-   3-D lighting disabled on shell contours to remove specular artefacts.
-   BMD title no longer overwrites SRF title when composing; colorbar
    moved to the left.
-   Support markers handled gracefully with `_ModelProxy`.
-   `fig.show()` works correctly in IPython terminal sessions.

## Version 0.5.0 (March 2026)

A usability-focused release: every result the model produces can now be
visualised in one or two lines of code, the public API is cleaner and more
consistent, and the documentation has been substantially rewritten.

**Plotting — new functions and interactive backend**

-   New convenience functions `plot_bmd()`, `plot_sfd()`, `plot_tmd()`, and `plot_def()` wrap `plot_force()` with the correct component pre-selected.
-   All plotting functions accept `backend="plotly"` for interactive 3-D force and deflection diagrams with rotation, zoom, and hover. Diagrams are rendered alongside the grillage mesh for immediate spatial context. Install with `pip install ospgrillage[gui]`.
-   `plot_model()` visualises the grillage mesh geometry (`backend="matplotlib"` for a 2-D plan view, `backend="plotly"` for interactive 3-D). Replaces `og.opsv.plot_model()` / `og.opsplt.plot_model()`.
-   Common keyword arguments across all plot functions: `figsize`, `ax` (existing matplotlib Axes), `scale`, `title`, `color`, `fill`, `alpha`, and `show`.
-   `Members` bitflag enum for filtering which member groups appear in a plot — combine with `|`, e.g. `Members.EDGE_BEAM | Members.INTERIOR_MAIN_BEAM`, or use the pre-defined composites `Members.LONGITUDINAL`, `Members.TRANSVERSE`, `Members.ALL`.
-   Plotly 3-D plots render supports, rigid links, shell quad elements, and transverse/edge beams alongside the longitudinal members.

**API improvements**

-   `load_obj` → `load` and `load_case_obj` → `load_case` in `CompoundLoad.add_load()`, `LoadCase.add_load()`, `MovingLoad.add_load()`, and `OspGrillage.add_load_case()`. The change is positional-compatible; only code using the old keyword names needs updating.
-   `LoadVertex` namedtuple replaces `LoadPoint` as the preferred name for load coordinate+magnitude tuples. `LoadPoint` is kept as a backwards-compatible alias.
-   `beam_z_spacing` renamed to `beam_spacing` with a `DeprecationWarning` (old name still accepted).
-   `Section(offset_y=…)` — users can now supply centroidal section properties and let ospgrillage apply the parallel axis theorem automatically (``I_offset = I_centroid + A * d²``). No more hand-calculating transferred second moments of area when the beam centroid is offset from the grillage model plane.
-   `Section(E=…)` / `Section(G=…)` now raise `ValueError` (elastic moduli belong on `Material`).
-   `get_results(load_case=…)` accepts a name or list of names to retrieve only specific load cases — avoids compiling every moving-load increment.
-   `plot_deflection` renamed to `plot_def` (consistent with `plot_bmd` / `plot_sfd`).
-   `Mesh.orthogonal` attribute added (previously raised `AttributeError` on oblique meshes).
-   Edge transverse elements (start/end edges on oblique meshes) are now correctly assigned to their own member groups.

**Dependencies**

-   `vfo` is no longer a required dependency. Use `og.plot_model()` instead of `og.opsplt.plot_model()`.
-   `og.opsv` and `og.opsplt` re-exports now emit `DeprecationWarning`.
-   Generated pyfiles no longer import `vfo`.

**GUI**

-   Code generation updated: uses `og.plot_model()` instead of `og.opsv.plot_model()`.
-   `ext_to_int_dist` spinner replaced with a `beam_spacing` text input for full control over transverse member layout.
-   Fixed `set_member()` code generation (member names were unquoted).

**Documentation**

-   Super-T bridge tutorial rewritten as a step-by-step walkthrough; advanced results split into a separate notebook.
-   `performing_analysis.md` split into `defining_loads.md`; "Running analysis" merged into `getting_results.md` ("Analysis and results").
-   `get_results()` docstring now recommends the `load_case=` parameter for models with moving loads.
-   15+ content fixes: removed non-existent `set_material()`, corrected `link_nodes_width` → `beam_width`, `NodalForce` → `NodeForces`, `type=` → `loadtype=`, duplicate member assignments, Sphinx cross-references throughout, missing API methods added.
-   Removed stale `html_static_path` / `html_theme_path` from `conf.py`.

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
