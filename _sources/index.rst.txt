.. ospgrillage documentation master file, created by
   sphinx-quickstart on Fri Jan 29 17:42:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. image:: http://raw.githubusercontent.com/MonashSmartStructures/ospgrillage/main/docs/source/images/ospgrillage_logo.png
  :width: 80 %
  :alt: ospgrillage
  :align: center

|Code style: black|
|License: MIT|
|version|
|Github issues|
|Github pull requests|
|PyPI|
|GitHub Workflow Deploy|
|GitHub Workflow Build|
|GitHub Workflow Status|
|GitHub commit activity|
|GitHub last commit|
|Contributor Covenant|
|codecov|
|JOSS|
|Zenodo|

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg 
   :target: https://github.com/psf/black

.. |License: MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg 
   :target: https://opensource.org/licenses/MIT

.. |version| image:: https://img.shields.io/github/downloads/MonashSmartStructures/ospgrillage/total?label=version

.. |GitHub issues| image:: https://img.shields.io/github/issues/MonashSmartStructures/ospgrillage?logoColor=yellowgreen

.. |GitHub pull requests| image:: https://img.shields.io/github/issues-pr/MonashSmartStructures/ospgrillage?color=yellowgreen

.. |PyPI| image:: https://img.shields.io/pypi/v/ospgrillage

.. |GitHub Workflow Deploy| image:: https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Build%20and%20deploy

.. |GitHub Workflow Build| image:: https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Deploy%20to%20GitHub%20Pages?label=gh%20page%20build

.. |GitHub Workflow Status| image:: https://img.shields.io/github/workflow/status/MonashSmartStructures/ospgrillage/Tests?label=Tests

.. |GitHub commit activity| image:: https://img.shields.io/github/commit-activity/m/MonashSmartStructures/ospgrillage

.. |GitHub last commit| image:: https://img.shields.io/github/last-commit/MonashSmartStructures/ospgrillage?color=ff69b4

.. |Contributor Covenant| image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg 
   :target: code_of_conduct.md

.. |codecov| image:: https://codecov.io/gh/MonashSmartStructures/ospgrillage/branch/main/graph/badge.svg?token=dUTOmPBnyP 
   :target: https://codecov.io/gh/MonashSmartStructures/ospgrillage

.. |JOSS| image:: https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de/status.svg
   :target: https://joss.theoj.org/papers/d44339b03dc4f1add2678167c1a1b6de

.. |Zenodo| image:: https://zenodo.org/badge/365436121.svg
   :target: https://zenodo.org/badge/latestdoi/365436121
 

===========================================
OpenSeesPy Grillage wizard - *ospgrillage*
===========================================

*ospgrillage* is a python wrapper of the *OpenSeesPy* package to speed up the creation of bridge deck grillage models.
`OpenSeesPy <openseespydoc.readthedocs.io>`_ is a python interpreter of the well-know Open System for Earthquake Engineering Simulation (`OpenSees <https://opensees.berkeley.edu/>`_) software framework.
*ospgrillage* provides a simple python API which allows users to:

1. Quickly generate and analyze a bridge deck grillage model in the *OpenSeesPy* model space, including many forms of loading and load cases;
2. Export a :code:`*.py` file containing the *OpenSeesPy* commands, which on execution, creates the prescribed *OpenSeesPy* grillage model.

The ability to use *ospgrillage* directly to do bridge deck analysis, or to export the *OpenSeesPy* command file for further editing, facilities an enormous range of use-cases in both bridge engineering practice and research.

Documentation
=============

.. toctree::
   :maxdepth: 1
   

   rst/user_guide
   rst/APIdoc
   rst/ModuleDoc
   rst/ChangeLog
   rst/ospgui



Support
=======
For technical support, please raise an issue at the `Github repository <https://github.com/MonashSmartStructures/ospgrillage>`_

Contributing
============
We really value and welcome contributions to the *ospgrillage* package.
Please check out our `contributing guidelines <https://github.com/MonashSmartStructures/ospgrillage/blob/main/.github/CONTRIBUTING.md>`_.

Credits
=======
* Mayer Melhem for producing the documentation illustrations and the design of the *ospgrillage* logo.
