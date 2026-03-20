# Troubleshooting

This page collects common errors and their solutions. If your problem is not listed here, please open an [issue on GitHub](https://github.com/MonashSmartStructures/ospgrillage/issues).

---

## Installation problems

### `ospgui` fails with `ModuleNotFoundError: No module named 'PyQt6'`

The GUI requires PyQt6, which is an optional dependency not installed by default. Install it with:

```bash
pip install "ospgrillage[gui]"
```

or, if ospgrillage is already installed:

```bash
pip install PyQt6
```

------------------------------------------------------------------------

### `openseespy` install fails on macOS (Apple Silicon)

OpenSeesPy ships platform-specific wheels. Make sure you are using a native arm64 Python interpreter (not a Rosetta-translated one):

```bash
python -c "import platform; print(platform.machine())"
# should print: arm64
```

If it prints `x86_64` inside an arm64 terminal you are running under Rosetta. Create a new conda environment with a native arm64 Python:

```bash
conda create -n ospg python=3.11
conda activate ospg
pip install ospgrillage
```

### Pandoc not found when building documentation

The Sphinx docs convert Jupyter notebooks via `nbsphinx`, which requires [pandoc](https://pandoc.org) on your system `PATH`.

```bash
# macOS
brew install pandoc

# Ubuntu / Debian
sudo apt-get install pandoc

# Windows — download the installer from https://pandoc.org/installing.html
```

After installing, verify with `pandoc --version` and re-run `make html`.

------------------------------------------------------------------------

## Model creation errors

### `ValueError: vertices of patch load give an invalid patch layout`

This is raised by {class}`~ospgrillage.load.PatchLoading` when the four vertices are not supplied in counter-clockwise (CCW) order, or define a self-intersecting quadrilateral.

Check that:

1.  The vertices form a valid convex (or at least non-self-intersecting) quadrilateral.
2.  The vertices are listed in CCW order when viewed from above (positive *y* looking down).
3.  Any cyclic rotation of the CCW order is accepted --- only the winding direction matters.

```python
# Correct — CCW starting from any corner
patch = og.create_load(loadtype="patch",
                       vertices=[(0,0,0), (2,0,0), (2,0,1), (0,0,1)])

# Also correct — CCW but starting from a different corner
patch = og.create_load(loadtype="patch",
                       vertices=[(2,0,0), (2,0,1), (0,0,1), (0,0,0)])

# Wrong — clockwise order
patch = og.create_load(loadtype="patch",
                       vertices=[(0,0,0), (0,0,1), (2,0,1), (2,0,0)])
```

### `skew angle` meshing rule errors

*ospgrillage* enforces:

-   Orthogonal mesh is **not** allowed when the skew angle is less than 11°.
-   Oblique mesh is **not** allowed when the skew angle is greater than 30°.

For skew angles between 11° and 30° either mesh type is permitted.

```python
# Skew angle too large for oblique mesh — use Ortho
bridge = og.create_grillage(..., skew=35, mesh_type="Ortho")

# Skew angle too small for orthogonal mesh — use Oblique
bridge = og.create_grillage(..., skew=5, mesh_type="Oblique")
```

------------------------------------------------------------------------

## Analysis errors

### `OpenSeesPy` segfault / silent crash

OpenSeesPy maintains global state. If you run multiple grillage models in the same Python process without wiping the OpenSees domain between them, the model tags clash and the solver may crash silently.

Call {meth}`~ospgrillage.osp_grillage.OspGrillage.create_osp_model` on a fresh grillage object, or restart the Python kernel between models.

### Results appear to be all zeros

This usually means the model was not analysed before calling {meth}`~ospgrillage.osp_grillage.OspGrillage.get_results`. Ensure the workflow is:

```python
bridge.create_osp_model(pyfile=False)
bridge.add_load_case(load_case)
bridge.analyze()
results = bridge.get_results()
```

------------------------------------------------------------------------

## Post-processing problems

### `KeyError` in {class}`~ospgrillage.postprocessing.Envelope`

The `array` argument passed to {func}`~ospgrillage.postprocessing.create_envelope` must match a variable name present in the `xarray.Dataset` returned by {meth}`~ospgrillage.osp_grillage.OspGrillage.get_results`. Common valid names are `"N"`, `"Vy"`, `"Vz"`, `"Mx"`, `"My"`, `"Mz"`.

### Visualisation not showing

If using the matplotlib backend, ensure `%matplotlib inline` (or `widget`) is set in
Jupyter.  For the Plotly backend (`backend="plotly"`), plots render inline
automatically in Jupyter notebooks.

------------------------------------------------------------------------

## Documentation build warnings

### `WARNING: document isn't included in any toctree`

This warning appears when an RST file exists under `docs/source/` but is not referenced in any `toctree` directive. Either add the file to the appropriate toctree or delete it if it is no longer needed.

### `WARNING: autodoc: failed to import`

The Sphinx `conf.py` mocks `openseespy` so autodoc can run without the binary. If you see this for an *ospgrillage* module, check that the module path in the `autoclass` or `autosummary` directive is correct, and that any newly added source files have been committed so Sphinx can find them.
