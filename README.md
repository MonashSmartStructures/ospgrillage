![ospgrillage logo](https://raw.githubusercontent.com/MonashSmartStructures/ospgrillage/main/docs/source/images/ospgrillage_logo.png)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![version](https://img.shields.io/github/downloads/MonashSmartStructures/ospgrillage/total?label=version)]() 
![GitHub issues](https://img.shields.io/github/issues/MonashSmartStructures/ospgrillage?logoColor=yellowgreen)
![GitHub pull requests](https://img.shields.io/github/issues-pr/MonashSmartStructures/ospgrillage?color=yellowgreen)
[![PyPI](https://img.shields.io/pypi/v/ospgrillage)]()
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Build%20and%20deploy)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Deploy%20to%20GitHub%20Pages?label=gh%20page%20build)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Tests?label=Tests)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/MonashSmartStructures/ospgrillage)
![GitHub last commit](https://img.shields.io/github/last-commit/MonashSmartStructures/ospgrillage?color=ff69b4)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![codecov](https://codecov.io/gh/MonashSmartStructures/ospgrillage/branch/main/graph/badge.svg?token=dUTOmPBnyP)](https://codecov.io/gh/MonashSmartStructures/ospgrillage)
[![status](https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de/status.svg)](https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de)


# Overview

*ospgrillage* is a python wrapper of the *OpenSeesPy* package to speed up the creation of bridge deck grillage models. [OpenSeesPy](openseespydoc.readthedocs.io) is a python interpreter of the well-know Open System for Earthquake Engineering Simulation ([OpenSees](https://opensees.berkeley.edu/)) software framework. *ospgrillage* provides a simple python API which allows users to:

1. Quickly generate and analyze a bridge deck grillage model in the *OpenSeesPy* model space, including many forms of loading and load cases;
2. Export a py file containing the *OpenSeesPy* commands, which on execution, creates the prescribed *OpenSeesPy* grillage model.

The ability to use *ospgrillage* directly to do bridge deck analysis, or to export the *OpenSeesPy* command file for further editing, facilites an enormous range of use cases in both practice and research.

## Documentation

*ospgrillage*'s full documentation can be found [here](https://monashsmartstructures.github.io/ospgrillage/index.html).

## Installation

Install using pip:
```bash
    pip install ospgrillage
```
    
Refer to [installation](https://monashsmartstructures.github.io/ospgrillage/rst/Installation.html) for more information.

## Contributions

Check out our [contributing guide](https://github.com/MonashSmartStructures/ospgrillage/blob/main/.github/CONTRIBUTING.md) to learn more on contributing, coding rules, community Code of Conduct and more.


# Capabilities

## Modelling

### Bridge Deck Models
-  Beam elements only - a traditional form of model
-  Beam elements with rigid links - a modification of the traditional form for box sections
-  Shell and beam elements - the modern form of modelling, but with more complex results interpretation

### Meshing
-  Single-span decks
-  Skewed (Oblique) and Orthogonal meshes
-  Positive and negative skew angles
-  Allows for skew mesh to be set up to 30 degrees
-  Allows for orthogonal mesh to be set no less than 11 degrees
-  Grillage elements grouped automatically for easy assignment of properties
-  Autodetect edges of spans as supporting nodes
-  Allows for diaphragms / end slabs
-  Allows for unit width properties for transverse slab/members
-  Pinned and roller supports

### Element types
The following *OpenSees* element types are supported:
-  `elasticBeamColumn`
-  `TimoshenkoBeamColumn`  
-  Shell elements

## Materials
-  A JSON materials library file for codified common material properties

## Utilities

### Load types
-  Nodal loads
-  Point loads
-  Line loads
-  Patch loads
-  Compound loads (any combination of the above load types) 

### Analysis
-  Load cases contain arbitrary multiple load types, including compound loads
-  Moving load analysis of arbitrary load types through compound loads

### Post-processing
-  Output results utilise python's `xarray` format
-  Retrieve result envelopes from `xarray` results
-  Query options for moving load 
-  Plotting displacement and force component from the results

# Credits
- Mayer Melhem for producing the documentation illustrations and the design of the *ospgrillage* logo.
