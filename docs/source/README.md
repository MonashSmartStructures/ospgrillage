# Overview

The opsy-grillage module is a python wrapper for ```Openseespy``` module. This module allow 
python users to create py file that generates a grillage model 
using Open System for Earthquake Engineering Simulation (OpenSees) software framework.

In OpenSees, each nodes and elements are defined in lines of code which typically results in a py file with
thousands lines of code for a model. The opsy-grillage module automates py file generation for the required grillage 
information.

The wrapper constructs a Python .py file containing ```Openseespy``` commands for constructing a 
Opensees model. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. It should provide a solid foundation for creating various grillage models in Opensees 
using ```Openseespy```. 

## Setup

To run the wrapper, download from github link() and import the following files
    
    import GrillageGenerator
    
## Example

The grillage module allows user to specify dimensions and properties 
of grillage model as shown in Figure 1.
Notably, users can specify the type of mesh - choose between orthogonal or oblique (skew) mesh. 

Example showing usage of `GrillageGenerator` class:
Creating the object
    
    test_bridge = GrillageGenerator(bridge_name="BenchMark", long_dim=10, width=5, skew=25,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")

See GrillageGenerator page for more information of inputs. 

An example output py file is given as Example_superT_10m_op.py. 




