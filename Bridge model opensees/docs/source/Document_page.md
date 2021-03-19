# PyBridge Openseespy Wrapper

## Overview

The OPmodelwrapper module is a wrapper for ```Openseespy``` module. The aim of this module is to provide
python users a programmable interface in Python interpreter to evaluate structural grillages 
in Open System for Earthquake Engineering Simulation (OpenSees) software framework.

The wrapper is designed for quick and easy grillage generation in a few basic command lines in Python 
interface. It should provide a solid foundation for grillage analysis tool using ```Openseespy```. 

## Setup

To run the wrapper, download from github link() and import the following files
    
    test
    

## `GrillageGenerator` class

Use `GrillageGenerator` class to 

The `GrillageGenerator` class contains functions to create the bridge model in `Opensees` software. 
These functions starts with "op" in the function name. 
For example, `GrillageGenerator.op_create_nodes()`.

Example using `GrillageGenerator` class:
First step create the object instance
    
    test_bridge = GrillageGenerator(long_dim=10,width=5,skew=45, num_long_grid=4, num_trans_grid=13, cantilever_edge=1)

Next, input section properties. For skew meshes, define for sections 1 to 4. For orthogonal
meshes, define for sections 1 to 6. Refer following table and figure for section information of
bridge model

| Tags    | Skew mesh| Orthogonal mesh |
| ----------- | ----------- | ----------- |
| 1   | Longitudinal beam    | Longitudinal beam| 
| 2   | Longitudinal edge beams | Longitudinal edge beams  |
| 3   | Transverse slab        | Transverse region A   |
| 4   | Transverse edge slab         | Transverse between region A and B |
| 5   | n/a      | Transverse region B) |
| 6   | n/a        | Tranverse skew region B1 and B2|



## `Bridge` class

A `GrillageGenerator` object has a `Bridge` class object. 

Example: How bridge class is called within Grillage generator
____________________

    # initialize Bridge class object within Grillage class instance
    self.OPBridge = OpenseesModel(self.bridgepickle["Nodedetail"], self.bridgepickle["Connectivitydetail"],
                                        self.bridgepickle["beamelement"], self.bridgepickle["Memberdetail"],
                                      self.bridgepickle["Member transformation"])
    # assign properties of concrete and steel
    self.OPBridge.assign_material_prop(self.bridgepickle["concreteprop"], self.bridgepickle["steelprop"])
    # send attribute to OP framework to create OP model
    self.OPBridge.create_Opensees_model()

    # time series and load pattern options
    self.OPBridge.time_series()
    self.OPBridge.loadpattern()

## ```MovingForceAnalysis``` class

The ```MovingForceAnalysis``` class performs analysis on the input bridge based on the input vehicle 
properties and traverse pattern.

The ```MovingForceAnalysis``` class takes two inputs:
(1) bridge class object - created or loaded from GrillageGenerator, 
(2) A ```vehicle``` named tuple
(3) 

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




