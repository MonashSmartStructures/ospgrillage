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

`ospgrillage` is a Python package that wraps `OpenSeesPy` module in creating structural grillage models for performing
grillage analysis in `OpenSees` framework. In the past, `OpenSees` - the open-source simulation framework for structural and geotechnical systems -
allow users to create and perform finite element analysis by writing scripts. The robustness of `OpenSees` robustness when combined,
with scripting language (such as Python) allow users to perform parallel structural analysis. However, `OpenSees` require users to write code
from scratch which can be time-consuming. Having inherit a vast library of elements and computational modules, `OpenSees`
would benefit greatly from having a module that automatically creates structural models through a simple user interface.

`ospgrillage` is designed to fill the aforementioned gap by providing users a simple interface which consist of
interface functions. For example, users only need to run a single `create_section` command instead of creating a Section object representing a bridge beam from scratch 
(i.e. defining and instantiating objects). With `ospgrillage` it is possible to create a variety of complex grillage models with 
just a few lines of codes. In addition to creating grillage models in the `OpenSees` framework, `ospgrillage` allow users to output an executable 
python script containing relevant `OpenSeesPy` command which creates the prescribed grillage model when executed. Furthermore,
`ospgrillage` offers load analysis utility using created grillage models, allowing users to perform
static and moving load analysis for example. An online documentation has been provided at 
Ngan et. al. (2021) which includes tutorials and examples for `ospgrillage`. Overall, `ospgrillage` should reduce the time needed 
to write scripts which open up `OpenSees` framework to a wider audience while also lowering the bar for teaching and learning of the `OpenSeesPy` module. 


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
for uses outside of `ospgrillage`. 


# Module information

In general, `ospgrillage` wraps `OpenSeesPy` command for:

- creating grillage model, and
- running analysis

Source code, documentation, and issue trackers can be found at `ospgrillage`'s the main [repository](https://monashsmartstructures.github.io/ospgrillage/index.html). 
Further details on the module design can be found on the documentation Module design page. Guide and examples for creating grillage models are also presented in the 
documentation as well. 

# Acknowledgements

This work is supported by Monash University Australia. 
The authors would like to thank all contributors of `ospgrillage`.


# References







