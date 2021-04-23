# Overview

The opsy-grillage module is a python wrapper for ```Openseespy``` module. This module allow 
python users to create py file that generates a grillage model using the Python interpreter of
 Open System for Earthquake Engineering Simulation (OpenSees) software framework - i.e. Openseespy

The wrapper constructs a Python .py file containing ```Openseespy``` commands for constructing a 
model in Opensees domain. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. 

## Setup

To run the wrapper, download from github link() and import the following files
    
    import GrillageGenerator
    

A quick example showing the application of `op-grillage` is presented as follows:
    
    test_bridge = GrillageGenerator(bridge_name="BenchMark", long_dim=10, width=5, skew=25,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")

See :ref:Structure description page for more information of inputs. 


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   rst/installation
   rst/structure
   rst/geom_mesh
   rst/analysis
   rst/post
   rst/examples
   rst/api
   rst/theory




