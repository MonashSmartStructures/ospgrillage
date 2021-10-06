---
title: 'ospgrillage: A grillage wizard for OpenSeesPy'
tags:
  - Python
  - grillage model
  - finite element
  - load analysis

authors:
  - name: J.W. Ngan
    affiliation: 1
  - name: C.C. Caprani 
    affiliation: 1
  - name: M. Melhem
    affiliation: 1

affiliations:
 - name: Monash University, Australia
   index: 1

date: 23 August 2021
bibliography: paper.bib


# Summary

`ospgrillage` is an open source Python package that extends the `OpenSeesPy` module to create structural grillage models in `OpenSees` framework. 
In the past, `OpenSees` framework - the simulation framework for structural and geotechnical systems - allow users to
create and perform finite element analysis using a scripting language (either Tcl or Python). Having inherited a vast library of elements and computational modules, `OpenSees`
would benefit greatly from having a module that simplifies the scripting procedure for various structural models. 

`ospgrillage` provides a simple user interface for making grillage models using `OpenSeesPy` module.
The interface consist of functions that wraps `OpenSeesPy` commands. 
For example, a single `create_section()` command will automatically define a Section object representing a bridge beam. 
With `ospgrillage` it is possible to create a variety of complex grillage models with 
just a few lines of codes. In addition to creating grillage models in the `OpenSees` framework, `ospgrillage` allow users to output an executable 
python script containing relevant `OpenSeesPy` command which creates the prescribed grillage model when executed. This secondary 
feature of `ospgrillage` is useful for users who wishes to use these models for external analysis. Furthermore,
`ospgrillage` also contains load analysis utility, allowing users to perform static and moving load analysis on the created grillage model.
 A full-fledged online documentation has been provided which includes tutorials and examples for `ospgrillage`.
 Overall, `ospgrillage` should reduce the time needed to write scripts which not only opens up `OpenSees` framework to a wider 
audience but also lowering the bar for teaching and learning of the `OpenSeesPy` module. 


# Statement of Need

`OpenSees` (Open System for Earthquake Engineering) is a software framework allowing users to create finite element application for simulating
responses of structural and geotechnical systems subjected to earthquake [@Mckenna2011]. The multi-module capability of
`OpenSees` framework is highly robust and efficient, particularly for research studies pertaining combined analysis 
such as post-seismic fire performance [@Elhami2014]. Initially available in Tcl language, its python interpreter `OpenSeesPy` have recently been made
available [@ZHU20186]. This allows users to take advantage of `OpenSees` computational framework while having access features unique to different
scripting languages. 

Recently, `OpenSees` has seen increase usage in bridge engineering research studies [@wang2017;@scoot:2008]. The available element library of `OpenSees` 
caters to a wide variety of bridge modelling techniques; from a simple one-dimensional (1-D) line model consisting of linear beam 
elements [@Almutairi2016AnalysisOM] to the more detailed three-dimensional (3-D) model [@Benjumea].
Furthermore, the scripting nature of `OpenSees` is well-suited to create a series of analysis to study multiple bridge models. 
Overall, `OpenSeesPy` is very robust in bridge engineering especially in research applications.

One shortcoming of `OpenSees` in bridge engineering application is that the scripting procedure for creating models and analysis can be time-consuming.
A typical script of `OpenSeesPy` commands consist several domains including the construction (e.g. *node*, and *element* commands), 
and the analysis domain (e.g. *load* commands). In turn, such scripts can be lengthy when considering model with many elements and nodes, let alone 
adding multiple subsequent analysis within the same script. These numerical models can become tedious to modify or troubleshoot. Furthermore, 
there is no definite way to import models into `OpenSees` framework. In other words, users wishing to model a specific bridge deck would be required to create its
`OpenSees` scripts from scratch - which is time-consuming and inefficient. 
Therefore, `OpenSees` would benefit for having a module that creates comprehensive structural models instead of having users writing scripts from scratch.

`ospgrillage` is a Python module designed to address the aforementioned gap by providing users a simple interface for creating 
bridge grillage models without needing to script from scratch. `ospgrillage` contains simple user interface functions that wrap `OpenSeesPy` commands for creating
models in `OpenSees` framework. For example, a create_grillage() function automatically executes the model generating 
commands of `OpenSeesPy`, i.e. node(), and element(). Furthermore, the simple interface functions provided by
`ospgrillage` also allow users to create and add analysis onto the created grillage models - these functions
wraps `OpenSeesPy`'s load module commands. Overall, `ospgrillage` should significantly 
reduce the time required for numerical analysis of bridge grillage models using `OpenSeesPy`.

`ospgrillage` is intended for two groups of users who would like to utilize `OpenSees` in Python language. Firstly, the interface for creating
grillage model instantaneously in `OpenSees` framework is suited for users who wish to quickly create and analyze grillage models.
Secondly, `ospgrillage`'s ability to generate and export fully-fledged python scripts caters for users who wish to create and store 
multiple grillage models for uses outside of `ospgrillage`. For example, these users could opt to leverage `ospgrillage`'s
meshing capabilities to quickly generate command lines of nodes and elements for their perusal.


# Module information

Source code, documentation, and issue trackers can be found at `ospgrillage`'s the main [repository](https://monashsmartstructures.github.io/ospgrillage/index.html). 
Guide and examples for creating grillage models have been provided in the documentation. 
Further, `ospgrillage`'s module design details can also be found on the *Module Design* page in documentation.

# Acknowledgements

This work is supported by Monash University Australia. The authors would like to thank all contributors of `ospgrillage`.


# References







