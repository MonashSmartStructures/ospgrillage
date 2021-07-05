
# Overview

The `ops-grillage` module is a python wrapper for ```Openseespy``` module. ```Openseespy``` 
is a Python interpreter of Open System for Earthquake Engineering Simulation (OpenSees) software framework.
`ops-grillage` allow python users to create py file that generates a grillage model in Openseespy.

A typical output py file from the wizard contains relevant ```Openseespy``` commands for constructing a 
model in Opensees domain. The commands are automatically generated based on user specified inputs 
regarding the bridge model. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. This module lowers the bar for research, education, and training of the software for structural
analysis purposes.

## Installation

To run the wrapper, download from github link() and import the following files:
    
    import OpsGrillage as og
    
For detailed information on installation, refer to [installation]


## Documentation

See :ref:Structure description page for more information of inputs. 

## Current Capabilities

### Bridge model features
- [x] Single-span 
- [x] Allow for transverse secondary beams 
- [x] Allow for diaphragm
- [x] Allow for unit width properties for transverse slab

### Mesh features
- [x] Skewed and Orthogonal meshes
- [x] Positive and negative skew angle
- [x] Allow for skew mesh to be set up to 30 degrees
- [x] Allow for orthogonal mesh to be set down to 11 degrees
- [x] Grillage elements grouped automatically for easy definition
- [x] Autodetect edge of spans as supporting nodes

### Element types
The following Opensees element types are supported by ops-grillage
- [x] elasticBeamColumn
- [x] TimoshenkoBeamColumn  
- [ ] nonlinearBeamColumn
- [x] Elements that utilize Elastic and RC_section


### Utilities
#### Loading Utilities
- [x] Nodal loads
- [x] Line loads
- [x] Patch loads
- [x] Compound loads (any combination of the above load types) 
#### Load cases
- [x] Multiple load utilities in single load case
- [x] Moving load cases
#### Result output
- [x] Utilise python's xarray features i.e. dataArrays


### In the works
- [ ] Curved meshes
- [x] Definition of mesh control points - e.g. ability to shift origin of mesh generation
- [ ] Enable multi-span definition (50%)
- [ ] Allow user input for custom node points

