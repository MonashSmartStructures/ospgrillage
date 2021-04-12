# Overview

The opmodule is a wrapper for ```Openseespy``` module. This module provides 
python users a programmable interface in Python interpreter to create py file that generates 
bridge grillage models in Open System for Earthquake Engineering Simulation (OpenSees) software framework.

The wrapper constructs a Python .py file containing the core ```Openseespy``` commands for constructing a 
Opensees model. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. It should provide a solid foundation for creating various grillage models in Opensees 
using ```Openseespy```. 

## Setup

To run the wrapper, download from github link() and import the following files
    
    import GrillageGenerator
    

## `GrillageGenerator` class

The `GrillageGenerator` class outputs an executable py file containing the `Openseespy` functions
for constructing the prescribed bridge grillage input data.

Users are required to specify the keyworded inputs - see GrillageGenerator page for more information.

Users have the option to generate either: (1) skew, or (2) orthogonal mesh grillages.
Each mesh type have different sections to be defined by the users. 

Example showing usage of `GrillageGenerator` class:
Creating the object

Inputs to be specified includes filename ("BenchMark"), global dimensions of grillage (e.g. width)
and mesh properties (number of meshes in orthogonal dimensions).
    
    test_bridge = GrillageGenerator(bridge_name="BenchMark", long_dim=10, width=5, skew=25,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")

Next, users define the member properties of the grillage model. Properties are defined through
the ```OPMemberProp``` class. The object then automatically sorts the output of the members into 
format compatible with the Opensees framework through ```.get_section_input()``` method. Following,
this output member properties are passed into ```GrillageGenerator``` object.

Example showing definition of bridge members.

    longmem = OPMemberProp(1, 1, 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58, principal_angle=0)
    longmem_prop = longmem.get_section_input()
    long_tag = 1
    test_bridge.op_create_elements(longmem_prop, long_tag, longmem.beam_ele_type, expression='long_mem')


For skew meshes, define for sections 1 to 4. For orthogonal
meshes, define for sections 1 to 6. Refer following table and figure for section information of
bridge model

| Section tag    | Skew mesh| Orthogonal mesh | Transform tag |
| ----------- |: ----------- :| ----------- | ----- 
| 1   | Longitudinal beam    | Longitudinal beam|  1 |
| 2   | Longitudinal edge beams | Longitudinal edge beams  | 1|
| 3   | Transverse slab        | Transverse region A   | 2  |
| 4   | Transverse edge slab         | Transverse between region A and B | 2 |
| 5   | n/a      | Transverse region B | 2 |
| 6   | n/a        | Tranverse skew region B1 and B2| 3| 


The material properties of grillage model is defined through the class function `material_definition()`
Material properties should follow conventions for Opensees framework.

Example showing the procedure to define the material properties of grillage model.

    test_bridge.material_definition(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])
    test_bridge.op_uniaxial_material()


## ```MovingForceAnalysis``` class

The ```MovingForceAnalysis``` class performs analysis on the input bridge based on the input vehicle 
properties and traverse pattern.

The ```MovingForceAnalysis``` class takes two inputs:
(1) A `GrillageGenerator` object - output file 
(2) A vehicle object
(3) Traverse path 
(4) Option for analysis (e.g. Opensees)
(5) The `GrillageGenerator` object (optional)

Example: using ```MovingForceAnalysis``` class:
____________________

    refbridge = "BenchMark_op"
    from RunScript import test_bridge  # import GrillageGenerator object created for op file
    # 1.1 Procedure to create bridge model in Opensees
    
    # 2 Define truck properties
    axlwts = [800, 3200, 3200]  # axle weights
    axlspc = [2, 2]  # axl spacings
    axlwidth = 2  # axl widths
    
    initial_position = [2, 0]  # start position of truck (ref point axle)
    travel_length = 50  # distance (m)
    increment = 2  # truck location increment
    direction = "X"  # travel direction (global)
    # model_option= "Opensees"
    model_option = "Custom"
    # 2.1 traverse properties
    move_path = namedtuple('Travel_path', ('initial_position', 'length', 'increment', 'direction'))
    move_1 = move_path([5, 2], 50, 2, "X")
    
    # 3 create truck object
    RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)
    # 4 pass py file of bridge and truck object to MovingLoadAnalysis.
    analysis = MovingLoadAnalysis(refbridge, RefTruck, move_1, model_option, test_bridge)
    # 5 run method to perform analysis
    analysis.run_analysis()





