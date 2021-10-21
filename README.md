
# Overview

The `ospgrillage` module is a python wrapper of ```OpenSeesPy``` module  to create structural grillage models. ```OpenSeesPy``` 
is a Python interpreter of Open System for Earthquake Engineering Simulation (OpenSees) software framework.
`ospgrillage` allow python users to generate grillage model in ```OpenSeesPy``` model space or create an output executable py file 
which on execute, creates the prescribed ```OpenSeesPy``` model instead.

A typical output py file from the wizard contains relevant ```OpenSeesPy``` commands for constructing a 
model in OpenSees domain. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. This module lowers the bar for research, education, and training of the software for structural
analysis purposes.

## Installation

Install using pip

    pip install git+https://github.com/MonashSmartStructures/ops-grillage.git

    
For more information on installation, refer to [installation](https://monashsmartstructures.github.io/ospgrillage/rst/Installation.html)


## Documentation

See [link](https://monashsmartstructures.github.io/ospgrillage/index.html) to docs

## Current Capabilities

### Model types available
- [x] Beam elements
- [x] Beam elements with rigid links
- [x] Shell and beam elements

### Mesh features
- [x] Single-span
- [x] Skewed (Oblique) and Orthogonal meshes
- [x] Positive and negative skew angles
- [x] Allow for skew mesh to be set up to 30 degrees
- [x] Allow for orthogonal mesh to be set no less than 11 degrees
- [x] Grillage elements grouped automatically for easy assignment of properties
- [x] Autodetect edge of spans as supporting nodes
- [x] Allow for diaphragm / end slab
- [x] Allow for unit width properties for transverse slab/members
- [x] Pinned and roller supports

### Element types
The following OpenSees element types are/will be supported in releases:
- [x] elasticBeamColumn
- [x] TimoshenkoBeamColumn  
- [ ] nonlinearBeamColumn
- [ ] Shell elements

## Materials
- [x] JSON material file for codified material properties


### Utilities
#### Load types definition
- [x] Nodal loads
- [x] Point loads
- [x] Line loads
- [x] Patch loads
- [x] Compound loads (any combination of the above load types) 

#### Analysis utilities
- [x] Allow for load case to add multiple load types, including compound loads
- [x] Allow for moving load case

#### Post-processing utilities
- [x] Output results utilise python's xarray DataSet
- [x] Retrieve envelopes from xarray results
- [x] Query options for moving load 
- [x] Plotting displacement and force component from xarray results

### Development wishlist
- [ ] Curved meshes
- [ ] Definition of mesh control points - e.g. ability to shift origin of mesh generation
- [ ] Enabling multi-span definition 


