# PyBridge Openseespy Wrapper

## Overview

The OPmodelwrapper module is a wrapper for ```Openseespy``` module. The aim of this module is to provide
python users a programmable interface in Python interpreter to evaluate structural grillages 
in Open System for Earthquake Engineering Simulation (OpenSees) software framework.

The wrapper constructs a Python .py file containing ```Openseespy``` commands for constructing a 
Opensees model. The wrapper allows quick grillage generation in a few basic command lines in Python 
interface. It should provide a solid foundation for creating various grillage models in Opensees 
using ```Openseespy```. 

## Setup

To run the wrapper, download from github link() and import the following files
    
    import GrillageGenerator
    

## `GrillageGenerator` class

Use `GrillageGenerator` class to construct a python .py file that contains relevant `Openseespy` functions
for model construction. 

The `GrillageGenerator` class contains functions to create the bridge model in `Opensees` software. 
These functions starts with "op" in the function name. 
For example, `GrillageGenerator.op_create_nodes()`.

Example using `GrillageGenerator` class:
First step create the object instance
    
    test_bridge = GrillageGenerator(long_dim=10,width=5,skew=45, num_long_grid=4, num_trans_grid=13, cantilever_edge=1)

Next, input section properties. For skew meshes, define for sections 1 to 4. For orthogonal
meshes, define for sections 1 to 6. Refer following table and figure for section information of
bridge model

| Section tag    | Skew mesh| Orthogonal mesh | Transform tag 
| ----------- | ----------- | ----------- |
| 1   | Longitudinal beam    | Longitudinal beam|  1 |
| 2   | Longitudinal edge beams | Longitudinal edge beams  | 1|
| 3   | Transverse slab        | Transverse region A   | 2  |
| 4   | Transverse edge slab         | Transverse between region A and B | 2 |
| 5   | n/a      | Transverse region B) | 2 |
| 6   | n/a        | Tranverse skew region B1 and B2| 3| 

Example showing section for element is defined:

    longmem = OPMemberProp(1, 1, 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58, principal_angle=0)
    longmem_prop = longmem.get_section_input()
    long_tag = 1
    test_bridge.op_create_elements(longmem_prop, long_tag, longmem.beam_ele_type, expression='long_mem')

Users repeat for the number of tags which corresponds to the mesh type (oblique or orthogonal) shown in
Table 1.

The material properties of grilage model is defined through the class function:

Example showing the procedure to define the material properties of grillage model.

    test_bridge.material_definition(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])
    test_bridge.op_uniaxial_material()

If section is required for the Opensees model, run function to define section and generate code line
in the grillage wizard.

Example showing procedure to define section of grillage model

## ```MovingForceAnalysis``` class

The ```MovingForceAnalysis``` class performs analysis on the input bridge based on the input vehicle 
properties and traverse pattern.

The ```MovingForceAnalysis``` class takes two inputs:
(1) A `GrillageGenerator` object - output file 
(2) A vehicle object
(3) Traverse path 
(4) Option for analysis (e.g. Opensees)

Example: defining a member section properties to a ```MovingForceAnalysis``` class

    longmem = OPMemberProp(1,1,0.896,3.47E+10,2.00E+10,0.133,0.213,0.259,0.233,0.58,principal_angle = 0)
    longmem_prop = longmem.get_section_input()
    trans_tag = 1
    test_bridge.op_create_elements(longmem_prop, trans_tag, longmem.beam_ele_type,expression='long_mem')


Example: using ```MovingForceAnalysis``` class:
____________________

    # Properties of truck
    axlwts = [800, 3200, 3200]
    axlspc = [7, 7]
    axlwidth = 5
    initial_position = [0, 3.0875]
    travel_length = 50
    increment = 2
    direction = "X"

    # create Truck object
    RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)

    # Load bridge properties, or generate new bridge model data 
    with open("save.p","rb") as f:
        refbridge = pickle.load(f)
    
    # create Grillage object
    Analysis_1 = MovingForceAnalysis(refbridge,RefTruck)
    
    # perform moving truck analysis
    Analysis_1.perfromtruckanalysis()




