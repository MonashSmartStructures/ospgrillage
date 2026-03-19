```{toctree}
:hidden:
:maxdepth: 1

pages/getting_started
pages/user_guide
pages/tutorials
pages/ospgui
pages/api_reference
pages/additional_resources
```

```{image} http://raw.githubusercontent.com/MonashSmartStructures/ospgrillage/main/docs/source/images/ospgrillage_logo.png
:width: 80%
:alt: ospgrillage
:align: center
```

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/ospgrillage)](https://pypi.org/project/ospgrillage/)
[![codecov](https://codecov.io/gh/MonashSmartStructures/ospgrillage/branch/main/graph/badge.svg?token=dUTOmPBnyP)](https://codecov.io/gh/MonashSmartStructures/ospgrillage)
[![JOSS](https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de/status.svg)](https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de)
[![Zenodo](https://zenodo.org/badge/365436121.svg)](https://zenodo.org/badge/latestdoi/365436121)

# OpenSeesPy Grillage wizard — *ospgrillage*

*ospgrillage* is a Python wrapper around *OpenSeesPy* to speed up the creation of
bridge deck grillage models.
[OpenSeesPy](https://openseespydoc.readthedocs.io) is a Python interpreter of the
well-known Open System for Earthquake Engineering Simulation
([OpenSees](https://opensees.berkeley.edu/)) framework.

*ospgrillage* lets you:

1. Quickly generate and analyse a bridge deck grillage model in the *OpenSeesPy*
   model space, with many forms of loading and load cases.
2. Export a `.py` file containing the *OpenSeesPy* commands which, on execution,
   recreates the prescribed grillage model.

## Citing ospgrillage

If you use *ospgrillage* in your work, please cite:

> Ngan, J.W. and Caprani, C.C. (2022), "*ospgrillage*: A bridge deck grillage analysis
> preprocessor for OpenSeesPy", *Journal of Open Source Software*, 7(77), 4404.
> [doi.org/10.21105/joss.04404](https://doi.org/10.21105/joss.04404)

## Support

For technical support please raise an issue at the
[GitHub repository](https://github.com/MonashSmartStructures/ospgrillage).

## Contributing

We welcome contributions to *ospgrillage*.
Please read the {doc}`contributing guidelines <pages/contributing>`
before submitting a pull request.

## Credits

Mayer Melhem produced the documentation illustrations and designed the *ospgrillage* logo.
