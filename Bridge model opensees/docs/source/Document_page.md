# Pybridge - Opensees Module

This page contains the guidelines 
for using the Opensees (OP) module for grillage
analysis.

## Overview

The OPmodelwrapper module is a wrapper for ```Openseespy``` module. The aim of this module is to provide
python users functions and a programmable interface in Python interpreter that generates structural
grillage model in Open System for Earthquake Engineering Simulation (OpenSees) software framework.

The wrapper is designed for quick and easy grillage generation in a few basic command lines in Python 
interface. It should provide a solid foundation for grillage analysis tool using ```Openseespy```. 

## Setup

To run the wrapper, download from github link() and import the following files

.. code-block::python

    test
    

## `Bridge` class

The ```Bridge``` class object contains information of the bridge grillage model.

The ```Bridge``` class object is passed into ```GrillageGenerator``` class object which 
creates an ```OpenseesModel``` object which uses ```Openseespy``` methods to 
create the bridge model within the ```Openseespy``` framework.

The ```Bridge``` class object and ```OpenseesModel``` object is only instantiated through the ```Grillage``` class

The ```OpenseesModel``` object contains internal functions that communicates with ```Openseespy``` framework

Example: Using the bridge class
____________________

.. code-block::python

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


## ```Grillage``` class

The ```Grillage``` class performs analysis on the input bridge based on the input vehicle 
properties and traverse pattern.

The ```Grillage``` class takes two inputs:
(1) bridge class object - created or loaded from GrillageGenerator, 
(2) A ```vehicle``` named tuple
(3) 

An example of using the ```Grillage``` class in Python Interface is presented as follows:
____________________

.. code-block::python

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
    RefBridge = Grillage(refbridge,RefTruck)
    
    # perform moving truck analysis
    RefBridge.perfromtruckanalysis()




