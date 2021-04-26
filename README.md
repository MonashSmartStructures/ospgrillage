# Overview

The opsy-grillage module is a python wrapper for ```Openseespy``` module. ```Openseespy``` 
is a Python interpreter of Open System for Earthquake Engineering Simulation (OpenSees) software framework.
`opsy-grillage` allow python users to create py file that generates a grillage model in Openseespy.

A typical output py file from the wizard contains relevant ```Openseespy``` commands for constructing a 
model in Opensees domain. The commands are automatically generated based on user specified inputs 
regarding the bridge model. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. This module lowers the bar for research, education, and training of the software for structural
analysis purposes.

## Installation

To run the wrapper, download from github link() and import the following files:
    
    import GrillageGenerator
    
For detailed information on installation, refer to [documentation]



## Documentation

See :ref:Structure description page for more information of inputs. 

## Current Capabilities

### Bridge types 
- [x] Skew Mesh
- [x] Orthogonal mesh
- [x] Positive and negative skew angles
- [x] Multiple member definition 




