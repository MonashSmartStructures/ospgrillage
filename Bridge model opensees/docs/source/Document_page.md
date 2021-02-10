# Pybridge - Opensees Module

This page contains the guidelines 
for using the Opensees (OP) module for grillage
analysis.

   

## `Bridge` class

The ```Bridge``` class object contains all information from bridge pickle file
and hold it. 

The class then creates an ```OpenseesModel``` object which uses ```Openseespy``` methods to 
create the bridge model within the ```Openseespy``` framework.

The ```Bridge``` class object and ```OpenseesModel``` object is only instantiated through the ```Grillage``` class

## ```Grillage``` class

The ```Grillage``` class takes two inputs: (1) a bridge pickle file, and (2) a ```vehicle``` class object.

## Guidelines for bridge pickle file

A bridge model is loaded through a pickle
file which contain the bridge information.

The pickle file is formatted to communicate with the classes and methods of the module. Note: no modifications should be 
 performed with respect to the bridge pickle fill unless reviewed with changes in the classes and methods. 
 
The pickle file contains a dictionary of dataframas (pandas), each details the properties
of the bridge. The entries include:
1) Node data
2) Connectivity data
3) Member properties
4) Material properties

For more information of the data frame and its content please refer to the 
example excel file - ReferenceBridge.xlsx