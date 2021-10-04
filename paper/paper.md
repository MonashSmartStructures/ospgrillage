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

`OpenSees` is a simulation framework for structural and geotechnical systems. Due to its robustness and versatility,
it is highly suited for structural analysis such as bridge deck analysis. Before `ospgrillage`, users of `OpenSees` 
are required to write code from scratch to define a section or a mesh of nodes for example. 
Such code can be very length for detailed structural models, most notably a bridge grillage model -
having many elements and features to be defined. In turn, `OpenSees` framework would benefit from having
a module that automatically creates structural through a simpler and non-trivia user interface. 
With `ospgrillage` it is now possible to create a variety of grillage models with 
just a few lines of codes. `ospgrillage` wraps and generates bridge grillage model using the python intepreter of `OpenSees` 
i.e. `OpenSeesPy`. In addition, `ospgrillage` allow users to output an executable python script
containing relevant `OpenSeesPy` command to create the prescribed grillage model. Furthermore,
`ospgrillage` offers load analysis utility using created grillage models, allowing users to perform
static and moving load analysis for example. An online documentation has been provided at 
Ngan et. al. (2021) which includes tutorials and examples for `ospgrillage`.


# Statement of Need

`OpenSees` (Open System for Earthquake Engineering) is a software framework allowing users to create finite element application for simulating
responses of structural and geotechnical systems subjected to earthquake [@Mckenna2011]. The multi-module capability of
`OpenSees` framework is highly robust and efficient, particularly for research studies pertaining combined analysis 
such as post-seismic fire performance [@Elhami2014]. Recently, its python interpreter `OpenSeesPy` have been made
available [@ZHU20186]. This allows users to take advantage of `OpenSees` computational framework while having access features unique to
Python scripting language.  

Recently, `OpenSees` has seen increase usage in bridge engineering studies [@wang2017;@scoot:2008]. The available element library of `OpenSees` 
caters to a wide variety of bridge modelling techniques; from a simple 1-D line model consisting of linear beam 
elements [@Almutairi2016AnalysisOM] to more detailed 3-D () having large number of model elements [@Benjumea].
Furthermore, scripting languages allow users to create either serial or parallel analysis to study multiple bridge models. 
Overall, `OpenSeesPy` is very robust in bridge engineering applications.

One shortcoming that hinders `OpenSees`'s usage in wider field of application is that it requires users to write scripts for its usage.
A typical script of `OpenSeesPy` commands consist several domains including the construction (e.g. *node*, and *element* commands), 
and the analysis domain (e.g. *load* commands). In turn, such scripts can be lengthy when considering model with many elements and nodes such as in
a two-dimension (2-D) bridge model. These numerical modelling process can become tedious especially during code modification or troubleshooting. 
Overall, `OpenSees` would benefit for having a module that creates comprehensive structural models by wrapping `OpenSeesPy` commands
instead of having users writing from scratch.

`ospgrillage` is a Python module designed to provide a simple interface for creating grillage models using `OpenSeesPy`. `ospgrillage`
contains user interface functions which wrap `OpenSeesPy` commands in creating grillage model in `OpenSees` framework. 
For example, a create_grillage() function automatically generate the model generating commands of `OpenSeesPy`, i.e. node(), and element(). 
`ospgrillage` also allow users to create and perform analysis using the created grillage models via simple interface functions - these
function wraps `OpenSeesPy` load commands. Overall, these interface feature significantly 
reduces the time required for numerical analysis of bridge grillage models using `OpenSeesPy`.

`ospgrillage` is intended for two groups of users who would like to utilize `OpenSees` in Python language. Firstly, the ability of `ospgrillage` in providing a simple interface for creating grillage
is suited for users who wish to create and analyze grillage models instantaneously in `OpenSees` framework. Secondly, `ospgrillage`'s
ability to generate and export fully-fledged python scripts caters for users who wish to create and store multiple grillage models 
for uses outside of `ospgrillage`. Overall, `ospgrillage` greatly reduces the time needed to write scripts which open up `OpenSees` framework
to a wider audience by lowering the bar for teaching and learning of the `OpenSeesPy` module. 

Source code, documentation, and issue trackers can be found at `ospgrillage`'s the main repository. Details on the module 
design can be found on the documentation page. Guide and examples for creating grillage models can be found in 
documentation as well. 


# Package information

In general, `ospgrillage` wraps `OpenSeesPy` command for:

- creating grillage model, and
- running analysis


# Acknowledgements

This work is supported by Monash University Australia. 
The authors would like to thank all contributors of `ospgrillage`.


# References







