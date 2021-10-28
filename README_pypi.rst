.. image:: https://github.com/MonashSmartStructures/ospgrillage/blob/main/docs/source/images/ospgrillage_logo.png
  :width: 100 %
  :alt: ospgrillage
  :align: left


Overview
--------

*ospgrillage* is a python wrapper of *OpenSeesPy* module to create structural grillage models. OpenSeesPy
is a Python interpreter of Open System for Earthquake Engineering Simulation (OpenSees) software framework.
*ospgrillage* provides a simple python API which allow python users to:

1. quickly generate a grillage model in *OpenSeesPy* model space;
2. export an executable py file containing all relevent *OpenSeesPy* command, which on execute,
   creates the prescribed *OpenSeesPy* grillage model model.


Documentation
-------------
*ospgrillage*'s full documentation can be found `here <https://monashsmartstructures.github.io/ospgrillage/index.html>`_.

Installation
-------------
Windows
^^^^^^^
Install using pip.

::

    pip install ospgrillage


For more information on installation, refer to `installation <https://monashsmartstructures.github.io/ospgrillage/rst/Installation.html>`_


Current Capabilities
--------------------
Model types available
^^^^^^^^^^^^^^^^^^^^^
-  [x] Beam elements
-  [x] Beam elements with rigid links
-  [x] Shell and beam elements

Mesh features
^^^^^^^^^^^^^
-  [x] Single-span
-  [x] Skewed (Oblique) and Orthogonal meshes
-  [x] Positive and negative skew angles
-  [x] Allow for skew mesh to be set up to 30 degrees
-  [x] Allow for orthogonal mesh to be set no less than 11 degrees
-  [x] Grillage elements grouped automatically for easy assignment of properties
-  [x] Autodetect edge of spans as supporting nodes
-  [x] Allow for diaphragm / end slab
-  [x] Allow for unit width properties for transverse slab/members
-  [x] Pinned and roller supports

Element types
^^^^^^^^^^^^^
The following OpenSees element types are/will be supported in releases:
-  [x] elasticBeamColumn
-  [x] TimoshenkoBeamColumn
-  [ ] nonlinearBeamColumn
-  [x] Shell elements

Materials
^^^^^^^^^
-  [x] JSON material file for codified material properties


Utilities
---------
Load types definition
^^^^^^^^^^^^^^^^^^^^^
-  [x] Nodal loads
-  [x] Point loads
-  [x] Line loads
-  [x] Patch loads
-  [x] Compound loads (any combination of the above load types)

Analysis utilities
^^^^^^^^^^^^^^^^^^
-  [x] Allow for load case to add multiple load types, including compound loads
-  [x] Allow for moving load case

Post-processing utilities
^^^^^^^^^^^^^^^^^^^^^^^^^
-  [x] Output results utilise python's xarray format
-  [x] Retrieve result envelopes from xarray results
-  [x] Query options for moving load
-  [x] Plotting displacement and force component from xarray results


Contributing guidelines
-----------------------
Check out our [contributing guide][contributing] to learn more on contributing, coding rules and more.
