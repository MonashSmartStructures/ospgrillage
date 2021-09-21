
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

To run the wrapper, download from github [link](https://github.com/MonashSmartStructures/ospgrillage.git) and import the following files:
    
    import ospgrillage as og
    
For detailed information on installation, refer to [installation](https://monashsmartstructures.github.io/ospgrillage/rst/Installation.html)


## Documentation

See [link](https://monashsmartstructures.github.io/ospgrillage/index.html) to docs

## Current Capabilities

### Bridge model features
- [x] Single-span
- [x] Longitudinal beam elements
- [x] Edge beams
- [x] Transverse slabs
- [x] Allow for diaphragm / end slab
- [x] Allow for unit width properties for transverse slab
- [x] Pinned and roller supports

### Mesh features
- [x] Skewed(Oblique) and Orthogonal meshes
- [x] Positive and negative skew angle
- [x] Allow for skew mesh to be set up to 30 degrees
- [x] Allow for orthogonal mesh to be set no less than 11 degrees
- [x] Grillage elements grouped automatically for easy assignment of properties
- [x] Autodetect edge of spans as supporting nodes
- [ ] Mesh with offset beam elements tied with rigid links

### Element types
The following OpenSees element types are/will be supported in releases:
- [x] elasticBeamColumn
- [x] TimoshenkoBeamColumn  
- [ ] nonlinearBeamColumn
- [ ] Shell elements


### Utilities
#### Loading Utilities
- [x] Nodal loads
- [x] Point loads
- [x] Line loads
- [x] Patch loads
- [x] Compound loads (any combination of the above load types) 

#### Load cases
- [x] Assign multiple load utilities in single load case
- [x] Moving load cases

#### Result output
- [x] Utilise python's xarray features i.e. dataArrays
- [x] Envelope function
- [x] Query options for load types

### Development wishlist
- [ ] Curved meshes
- [ ] Definition of mesh control points - e.g. ability to shift origin of mesh generation
- [ ] Enabling multi-span definition 


