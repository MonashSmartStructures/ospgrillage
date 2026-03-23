# Contributing to ospgrillage

Thank you for considering a contribution to *ospgrillage*!
This document explains how to set up a development environment, run the test suite,
build the documentation locally, and submit a pull request.

---

## Table of contents

1. [Development setup](#development-setup)
2. [Running the tests](#running-the-tests)
3. [Code style](#code-style)
4. [Docstrings](#docstrings)
5. [Building the documentation](#building-the-documentation)
6. [Submitting a pull request](#submitting-a-pull-request)
7. [Reporting bugs and requesting features](#reporting-bugs-and-requesting-features)

---

## Development setup

*ospgrillage* uses a `src` layout and declares all metadata in `pyproject.toml`.

```bash
# 1. Fork the repository on GitHub, then clone your fork:
git clone https://github.com/<your-username>/ospgrillage.git
cd ospgrillage

# 2. Create and activate a virtual environment (Python 3.9 or later):
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the package in editable mode together with all optional extras:
pip install -e ".[dev,docs]"
```

If `[dev]` or `[docs]` extras are not yet declared in `pyproject.toml`, install the
dependencies manually:

```bash
pip install pytest pytest-cov sphinx pydata-sphinx-theme nbsphinx sphinx-autodoc-typehints
```

---

## Running the tests

The test suite uses [pytest](https://pytest.org/).  Run it from the repository root:

```bash
python -m pytest tests/
```

To see a coverage report:

```bash
python -m pytest tests/ --cov=ospgrillage --cov-report=term-missing
```

All tests must pass before a pull request will be merged.

### Writing effective tests

Line coverage alone is not sufficient.  A test that creates a model and only checks
`assert og.ops.getNodeTags()` tells you the constructor didn't crash — it says nothing
about whether the model actually works.

Every test should exercise the **user-facing operation** it is guarding, not just the
setup step.  Concretely:

| What you changed | Minimum test expectation |
|---|---|
| Mesh generation | Verify node/element counts **and** spot-check coordinates or connectivity |
| `get_element()` | Call it for every relevant member name; assert non-empty results |
| Analysis / loads | Run `analyze()`, then call `get_results()` and check values are finite and non-zero |
| Plotting functions | Call the function (both backends if applicable); assert it returns without error and produces a figure/axes object |
| `pyfile=True` output | Generate the file, read it back, and verify key commands are present |

When adding or modifying a feature, check the coverage matrix below and fill any
adjacent gaps — e.g. if you fix a bug in `shell_beam` meshing, also add a
`get_element()` or `plot_model()` call for that model type if one doesn't exist.

#### Coverage matrix (keep up to date)

| Operation | `beam_only` | `beam_link` | `shell_beam` |
|---|:---:|:---:|:---:|
| Construction | ✅ | ✅ | ✅ |
| `get_element()` | ✅ | ✅ | ✅ |
| `analyze()` + loads | ✅ | ✅ | ✅ |
| `get_results()` | ✅ | ✅ | ✅ |
| `plot_model()` | ✅ | ✅ | ✅ |
| `plot_bmd/sfd/tmd/def()` | ✅ | — | — |
| `plot_force()` | ✅ | — | ✅ |
| Multi-span | ✅ | — | ✅ |
| Oblique mesh | ✅ | — | — |

---

## Code style

*ospgrillage* uses [black](https://black.readthedocs.io/) for formatting.
Before committing, format changed files with:

```bash
black src/ tests/
```

A CI check will fail if the formatting does not match `black`'s output.

---

## Docstrings

All public functions and classes must have docstrings in
[NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html).
A minimal example:

```python
def create_grillage(bridge_name, long_dim, width, **kwargs):
    """Create and return an OspGrillage model object.

    Parameters
    ----------
    bridge_name : str
        Name label for the grillage model.
    long_dim : float
        Longitudinal span length in metres.
    width : float
        Transverse width in metres.
    **kwargs
        Additional keyword arguments forwarded to :class:`OspGrillage`.

    Returns
    -------
    OspGrillage
        Configured grillage model ready for meshing.

    Examples
    --------
    >>> import ospgrillage as og
    >>> bridge = og.create_grillage("My bridge", long_dim=20, width=8,
    ...                             num_long_grid=7, num_trans_grid=5,
    ...                             edge_beam_dist=1, mesh_type="Ortho")
    """
```

---

## Building the documentation

The documentation is built with [Sphinx](https://www.sphinx-doc.org/) and requires
[pandoc](https://pandoc.org/) to convert the Jupyter notebook examples.

Install pandoc via your OS package manager or from https://pandoc.org/installing.html,
then:

```bash
cd docs
pip install -r requirements.txt   # installs Sphinx extensions
make html                          # output appears in docs/build/html/
```

Open `docs/build/html/index.html` in a browser to preview.

If you see nbconvert/pandoc errors, ensure `pandoc` is on your `PATH`:

```bash
pandoc --version
```

---

## Submitting a pull request

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feature/my-improvement
   ```

2. Make your changes, add tests for any new behaviour, and ensure `pytest` passes.

3. Update `CHANGELOG.md` under the `[Unreleased]` section.

4. Push your branch and open a pull request against `MonashSmartStructures/ospgrillage`
   on GitHub.

5. A maintainer will review the PR.  Please be patient — this is a volunteer project.

---

## Reporting bugs and requesting features

Please open an
[issue on GitHub](https://github.com/MonashSmartStructures/ospgrillage/issues).
When reporting a bug, include:

- The *ospgrillage* version (`python -c "import ospgrillage; print(ospgrillage.__version__)"`).
- A minimal reproducible example.
- The full traceback.
