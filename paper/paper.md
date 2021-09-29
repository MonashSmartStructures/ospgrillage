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

affiliations:
 - name: Monash University, Australia
   index: 1

date: 23 August 2021
bibliography: paper.bib


# Summary

`OpenSees` is a simulation framework for structural and geotechnical systems. Due to its robustness and versatility,
it is highly suited for structural analysis such as bridge deck analysis. Before `ospgrillage`, users of `OpenSeesPy` 
are required to write code from scratch to define a section or a mesh of nodes for example. 
Such code can be very length for detailed structural models, most notably a bridge grillage model -
having many elements and features to be defined. With its inherit reliability and robustness, `OpenSees` framework would benefit from having
a module that automatically creates structural through a simpler and non-trivia user interface. 
With `ospgrillage` it is now possible to create a variety of grillage models with 
just a few lines of codes. `ospgrillage` wraps and generates bridge grillage model with the python intepreter of `OpenSees` 
i.e. `OpenSeesPy`. In addition, `ospgrillage` allow users to output an executable python script
containing relevant `OpenSeesPy` command to create the prescribed grillage model. Furthermore,
`ospgrillage` offers load analysis utility using created grillage models, allowing users to perform
static and moving load analysis for example. An online documentation has been provided at 
Ngan et. al. (2021) which includes tutorials and examples for `ospgrillage`.


# Statement of Need

`OpenSees` (Open System for Earthquake Engineering) is a software framework allowing users to create finite element application for simulating
responses of structural and geotechnical systems subjected to earthquake [@Mckenna2011]. It is highly robust and efficient, ideal for 
research studies due to its quick and efficient computational processes. Recently, its python interpreter `OpenSeesPy` have been made
available [@ZHU20186]. Soon after, `OpenSees` has seen increase usage in wider fields of application outside its original geotechnical field.

`OpenSees` has been highly sought after in bridge engineering applications. With its current library of elements, `OpenSees` caters to a wide variety
of bridge modelling techniques; from a simple 1-D line model consisting of linear beam elements (micheal scott) to 
more detailed 3-D () having large number of model elements (José Benjumea). Overall, `OpenSeesPy` is very robust when it comes to 
bridge engineering applications.

However, `OpenSees` requires users to write scripts for its usage. A typical python script of `OpenSeesPy` commands
consist several domains including the construction (e.g. *node*, and *element* commands), and the analysis domain (e.g. *load* commands). 
Such scripts can be lengthy when considering model with many elements and nodes, particularly when bridge models extend beyond
two-dimension (2-D) model space. In turn, numerical modelling process can become tedious especially during code modification or troubleshooting. 
Overall, `OpenSees` would benefit for having a module that creates comprehensive bridge models by wrapping `OpenSeesPy` commands
instead of having users writing from scratch.

`ospgrillage` was designed to provide a simple interface for creating grillage models using `OpenSeesPy`. `ospgrillage`
offer interface functions which wraps `OpenSeesPy` commands in creating grillage model. For example, a single create_grillage() function
automatically generate the model generating commands of `OpenSeesPy` i.e. node(), and element(). `ospgrillage` also automates the domain for 
implementing load cases and analysis to the created grillage models. Overall, these interface feature significantly 
reduces the time required for numerical analysis of bridge grillage models using `OpenSeesPy`.

`ospgrillage` is intended for two groups of users. Firstly, the ability of `ospgrillage` in providing a simple interface for creating grillage
is suited for users who wish to create and analyze grillage models instantaneously in `OpenSees` framework. Secondly, `ospgrillage` has
the ability to generate and export fully-fledged python scripts generates the same grillage model in `OpenSees` framework when executed - good for generating 
multiple model templates. This template creating feature caters for users who wish to create and store multiple grillage models for uses outside of
`ospgrillage`. Overall, having both capabilities to either create model instance or fully-fledged template scripts can open up the software to a wider audience,
lowering the bar for teaching and learning of the `OpenSeesPy` module. 


# Package information

In general, `ospgrillage` wraps `OpenSeesPy` command for:

- creating grillage model, and
- running analysis

Source code, documentation, and issue trackers can be found at `ospgrillage`'s the main repository. Details on the module 
design can be found on the documentation page. Guide and examples for creating grillage models can be found in 
documentation as well. 


For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Acknowledgements

This work is supported by Monash University Australia. 
The authors would like to thank all contributors towards `ospgrillage`'s development.


# References







