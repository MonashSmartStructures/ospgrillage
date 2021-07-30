

====================
API reference
====================

This page includes the technical content deliverables of the documentation. Instructions on variables and function
showing their interactions, both within and across various classes, are presented herein.

UML diagram overview
----------------------------

..  figure:: ../images/draftUML.PNG
    :align: center
    :scale: 50 %

    Figure 1: UML diagram - draft version 1.


What functions are considered public API?
------------------------------------------
To put it simply, any functions documented in this API reference page are considered part of *ops-grillage*'s public API.
There are many more functions which are lower level - these listed functions are the top level functions accessible
from classes shown in UML diagram.


OpsGrillage class
---------------------------

.. autoclass:: opsgrillage.OpsGrillage
    :members:
    :show-inheritance:


Analysis objects
^^^^^^^^^^^^^^^^
.. autoclass:: opsgrillage.Analysis
    :members:
    :show-inheritance:


Result objects
^^^^^^^^^^^^^^^^
.. autoclass:: opsgrillage.Results
    :members:
    :show-inheritance:


Material class
------------------------------------------
For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`.


Opensees Uniaxial Materials
^^^^^^^^^^^^^^^^

.. autoclass:: material.Material
    :members:
    :show-inheritance:

Opensees ND materials
^^^^^^^^^^^^^^^^

.. autoclass:: material.NDmaterial
    :members:
    :show-inheritance:

Section class
------------------------------------------

.. autoclass:: member_sections.Section
    :members:
    :show-inheritance:

GrillageMember class
------------------------------------------
.. autoclass:: member_sections.GrillageMember
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

.. autoclass:: load.Path
    :members:
    :show-inheritance:

.. autoclass:: load.ShapeFunction
    :members:
    :show-inheritance: