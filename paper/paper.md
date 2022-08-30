---
title: '`ospgrillage`: A bridge deck grillage analysis preprocessor for `OpenSeesPy`'
tags:
  - Python
  - Bridge
  - grillage
  - finite element
  - load analysis

authors:
  - name: J.W. Ngan^[co-first author]
    orcid: 0000-0001-7514-0065 
    affiliation: 1
  - name: C.C. Caprani^[corresponding author]
    orcid: 0000-0001-6166-0895
    affiliation: 1

affiliations:
 - name: Monash University, Australia
   index: 1

date: 1 February 2022
bibliography: paper.bib

---

# Summary

The structural analysis of bridge decks is a vital part of the design and assessment of bridges.
`ospgrillage` is an open source Python package that extends the `OpenSeesPy` package to create bridge deck grillage models using the Open System for Earthquake Engineering Solution (`OpenSees`) framework. 
The `OpenSees` framework combines the power of scripting languages (either Tcl or Python) with cutting-edge finite element analysis for various structural and geotechnical systems.
As such, the `OpenSees` framework has significant potential for both practitioners and researchers in creating and analyzing advanced bridge deck grillage models. 
However, directly using the low-level `OpenSees` framework is time-consuming and tedious for the creation of comprehensive grillage models.
A main motivation for `ospgrillage` is that the `OpenSees` framework would benefit greatly from having a pre-processing package that automates the bridge deck grillage modelling process for common model types.
Similarly, users of `ospgrillage` can benefit from the vast library of elements and computational modules available now and in future, from `OpenSees`.

`ospgrillage` provides a simple user interface for making grillage models based on the `OpenSeesPy` package (itself a Python wrapper to `OpenSees`).
The `ospgrillage` interface consist of API functions that wrap `OpenSeesPy` commands as tailored to bridge deck analysis. 
For example, a single `create_section()` command runs all relevant `OpenSeesPy` commands to create a section representing a structural member.
With `ospgrillage`, it is possible to create a variety of complex grillage models with far fewer lines of codes.
In addition, `ospgrillage` allows users to output an executable Python script containing the relevant `OpenSeesPy` commands to create the prescribed grillage model when executed.
This secondary feature of `ospgrillage` is useful for users who wishes to further develop these models and leverage the full power of `OpenSees`.
Alongside model generation, `ospgrillage` also contains comprehensive load analysis utilities, allowing users to perform multiple loadcase analyses on the created grillage model.
Detailed online documentation is provided which includes tutorials and examples for `ospgrillage`.
Overall, `ospgrillage` should reduce the time needed to create bridge deck grillage models in terms of the scripting process; which not only opens up the powerful `OpenSees` framework to a wider audience but also lowers the bar for users to adopt and learn the `OpenSeesPy` package in their workflow. 


# Statement of Need

`OpenSees` is a software framework allowing users to create advanced finite element applications for simulating the static and dynamic linear and non-linear responses of structural and geotechnical systems [@Mckenna2011].
The modularized `OpenSees` framework is highly robust and efficient, particularly for research studies pertaining to combined analyses such as post-seismic fire performance [@Elhami2014].
Initially available to interface through the Tcl language, a Python interpreter `OpenSeesPy` has recently been made available and has seen a large uptake [@ZHU20186].
This allows users to take advantage of `OpenSees` computational framework while integrating their analysis with other tools from the enormous Python eco-system.

In recent years, `OpenSees` has seen an increase usage in bridge engineering research studies [@wang2017;@scott:2008].
The element library of `OpenSees` caters to a wide variety of bridge modelling techniques; from a simple one-dimensional (1-D) line model consisting of linear beam elements [@Almutairi2016AnalysisOM], to comprehensive nonlinear three-dimensional (3-D) models [@Benjumea].
On the other hand, bridge deck analysis is a vital part of both research and practice in bridge design and assessment.
As the structure is subjected to many sources of moving and dynamic loads, the three-dimensional behaviour is complex.
However, it is critical for public safety that this behaviour is properly modelled and understood.
The most popular bridge deck modelling approach is grillage modelling, as it has been used for many decades around the world [@carlross].
Previously, grillage modelling was restricted to one-dimensional elements, but now shell elements are increasingly accepted, all of which is readily accommodated in `OpenSees`.
In addition to modelling, the scripting nature of `OpenSees`---as compared with the graphical interfaces prevalent in commercial engineering practice software---is well-suited to performing a series of analyses for parametric studies in bridge engineering.

A significant shortcoming of `OpenSees` in bridge engineering application is that the low-level scripting is extremely voluminous and time-consuming for grillage modelling and analysis. 
A typical script for a model consists of `OpenSeesPy` commands under several domains including the construction (e.g. *node*, and *element* commands), and the analysis domain (e.g. *load* commands).
In turn, such scripts are usually very lengthy when considering model with many elements and nodes, let alone adding multiple subsequent analyses within the same script.
Hence these numerical models are very error prone, and become tedious to modify or troubleshoot.
Furthermore, there is no established interface to import such models into `OpenSees` framework.
In other words, users wishing to model a specific bridge deck would be required to create its scripts from scratch. 
Therefore, `OpenSees` users would enormously benefit from having a package that creates grillage models instead of having users writing scripts from scratch.

`ospgrillage` is a Python package designed to address the aforementioned gap by providing users a simple interface for creating bridge grillage models without needing to script from scratch.
`ospgrillage` contains simple user interface functions that wrap `OpenSeesPy` commands for creating models in `OpenSees` framework.
For example, a single `create_grillage()` function automatically executes the model generating commands of `OpenSeesPy`, i.e. `node()`, and `element()`.
Furthermore, the simple interface functions provided by `ospgrillage` also allow users to create and add analyses onto the created grillage models - these functions wrap `OpenSeesPy`'s load module commands.
`opsgrillage` automates the generation of three types of grillage models, the enveloping of moving load analyses results, and the combination of multiple load cases.
Consequently, `ospgrillage` significantly reduces the time required for numerical analysis of bridge grillage models using `OpenSeesPy` and opens up the potential for massive parametric analysis of bridge families to researchers, for example.

`ospgrillage` is intended for two groups of users who would like to utilize `OpenSees` in the Python language.
Firstly, the interface for creating grillage model instantaneously in `OpenSees` framework is suited for users who wish to quickly create and analyze grillage models (i.e. practitioners).
Secondly, `ospgrillage`'s ability to generate and export fully-fledged Python scripts caters for users who wish to create and store multiple grillage models for uses outside of `ospgrillage`.
For example, these users could opt to leverage `ospgrillage`'s meshing capabilities to quickly generate command lines of nodes and elements which they can then use as the basis for more advanced analysis (e.g. seismic nonlinear material and geometric analysis).
Finally, `ospgrillage` is written to be easily extensible, and the roadmap allows for curved and multi-span bridge decks, for example.


# Availability
The `ospgrillage` package is available at [ospgrillage](https://monashsmartstructures.github.io/ospgrillage/index.html), where the source code, issue trackers, and documentation can be found.
Guides and examples for creating grillage models have been provided in the documentation.
Additionally, details of `ospgrillage`'s package design can also be found on the *Package Design* section of documentation.
Furthermore, a workshop on `ospgrillage` was held on 30 November 2021 and the recording is available on [YouTube](https://www.youtube.com/watch?v=8idPqdT_AhI&ab_channel=ColinCaprani).

# Acknowledgements

The authors would like to thank all contributors of `ospgrillage`.
In particular, the authors would like to thank Dr. Mayer Melhem for his contributions to testing the package and producing illustrations for the documentation, including the `ospgrillage` logo.

# References







