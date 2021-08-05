====================
API reference
====================

This page presents the technical content deliverables of the module. Instructions on variables and function
showing their interactions, both within and across various classes, are presented herein.

UML diagram overview
----------------------------

..  figure:: ../images/draftUML.PNG
    :align: center
    :scale: 50 %

    Figure 1: UML diagram - draft version 1.


What functions are considered public API?
------------------------------------------
This module comprised of user interface functions to take user inputs and returns its corresponding object creation



OpsGrillage class
---------------------------


.. currentmodule:: osp_grillage

.. autoclass:: OpsGrillage
    :members:
    :show-inheritance:

Analysis class
^^^^^^^^^^^^^^^^




.. autoclass:: osp_grillage.Analysis
    :members:
    :show-inheritance:


Result class
^^^^^^^^^^^^^^^^
.. autoclass:: osp_grillage.Results
    :members:
    :show-inheritance:


Material class
------------------------------------------
For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`.


.. autoclass:: material.Material
    :members:
    :show-inheritance:

Section class
------------------------------------------

.. autoclass:: members.Section
    :members:
    :show-inheritance:

GrillageMember class
------------------------------------------

.. automodule:: members
    :members:
    :show-inheritance:


Mesh class
------------------------------------------

.. autoclass:: mesh.Mesh
    :members:
    :show-inheritance:

Load class
------------------------------------------
For information regarding definition of :class:`~Loads` class, see
:doc:`Loads`.

NodalLoad
^^^^^^^^^^^^^^^^

.. autoclass:: load.NodalLoad
    :members:
    :show-inheritance:

PointLoad
^^^^^^^^^^^^^^^^

.. autoclass:: load.PointLoad
    :members:
    :show-inheritance:

LineLoading
^^^^^^^^^^^^^^^^

.. autoclass:: load.LineLoading
    :members:
    :show-inheritance:

PatchLoading
^^^^^^^^^^^^^^^^

.. autoclass:: load.PatchLoading
    :members:
    :show-inheritance:

CompoundLoad
^^^^^^^^^^^^^^^^

.. autoclass:: load.CompoundLoad
    :members:
    :show-inheritance:

MovingLoad
^^^^^^^^^^^^^^^^

.. autoclass:: load.MovingLoad
    :members:
    :show-inheritance:

Load case class
------------------------------------------
For information regarding in :class:`~LoadCase` class, see
:doc:`Loads`.

LoadCase
^^^^^^^^^^^^^^^^

.. autoclass:: load.LoadCase
    :members:
    :show-inheritance:

Misc
------------------------------------------

LoadCase
^^^^^^^^^^^^^^^^
.. autoclass:: load.Path
    :members:
    :show-inheritance:

Shape functions
^^^^^^^^^^^^^^^^
.. autoclass:: load.ShapeFunction
    :members:
    :show-inheritance: