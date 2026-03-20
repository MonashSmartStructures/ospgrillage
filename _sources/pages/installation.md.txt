# Installation

## Required dependencies

-   Python (3.9 or later)
-   openseespy (3.3 or later)
-   numpy
-   xarray

## Instructions

The easiest way to install is via the Python Package Index.

```bash
pip install ospgrillage
```

For users wishing to develop or contribute, clone the repository and install in editable mode:

```bash
git clone https://github.com/MonashSmartStructures/ospgrillage.git
cd ospgrillage
pip install -e .
```

See the [contributing guide](https://github.com/MonashSmartStructures/ospgrillage/blob/main/CONTRIBUTING.md) for full guidance including running the test suite and documentation builds.

## Using Jupyter notebooks

**With venv (pip)**

```bash
python -m venv ospg
source ospg/bin/activate          # Windows: ospg\Scripts\activate
pip install jupyterlab ospgrillage
jupyter lab
```

**With conda**

```bash
conda create --name ospg python=3.11
conda activate ospg
conda install -c conda-forge jupyterlab
pip install ospgrillage
jupyter lab
```

## Optional: GUI (ospgui)

The interactive geometry generator `ospgui` requires **PyQt6**, which is a large binary dependency and is therefore not installed by default. To include it:

```bash
pip install "ospgrillage[gui]"
```

If you run `ospgui` without PyQt6 installed you will see a clear error message with the install command above rather than a bare traceback.

## Installing dependencies

All core Python dependencies are declared in `pyproject.toml` and are installed automatically by `pip install ospgrillage`.

## Tests

The test suite uses `pytest`. Run it from the repository root:

```bash
python -m pytest tests/
```
