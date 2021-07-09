

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

.. autoclass:: OpsGrillage.OpsGrillage
    :members:
    :show-inheritance:


Analysis objects
^^^^^^^^^^^^^^^^
.. autoclass:: OpsGrillage.Analysis
    :members:
    :show-inheritance:


Result objects
^^^^^^^^^^^^^^^^
.. autoclass:: OpsGrillage.Results
    :members:
    :show-inheritance:


Material class
------------------------------------------
For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`.


Opensees Uniaxial Materials
^^^^^^^^^^^^^^^^

.. autoclass:: Material.UniAxialElasticMaterial
    :members:
    :show-inheritance:

Opensees ND materials
^^^^^^^^^^^^^^^^

.. autoclass:: Material.NDmaterial
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



Load class
------------------------------------------
For information regarding in :class:`~Loads` class, see
:doc:`Loads`.

NodalLoad
^^^^^^^^^^^^^^^^

.. autoclass:: Load.NodalLoad
    :members:
    :show-inheritance:

PointLoad
^^^^^^^^^^^^^^^^

.. autoclass:: Load.PointLoad
    :members:
    :show-inheritance:

LineLoading
^^^^^^^^^^^^^^^^

.. autoclass:: Load.LineLoading
    :members:
    :show-inheritance:

PatchLoading
^^^^^^^^^^^^^^^^

.. autoclass:: Load.PatchLoading
    :members:
    :show-inheritance:

CompoundLoad
^^^^^^^^^^^^^^^^

.. autoclass:: Load.CompoundLoad
    :members:
    :show-inheritance:

MovingLoad
^^^^^^^^^^^^^^^^

.. autoclass:: Load.MovingLoad
    :members:
    :show-inheritance:

Load case class
------------------------------------------
For information regarding in :class:`~LoadCase` class, see
:doc:`Loads`.

LoadCase
^^^^^^^^^^^^^^^^

.. autoclass:: Load.LoadCase
    :members:
    :show-inheritance:

Misc
------------------------------------------

.. autoclass:: Load.Path
    :members:
    :show-inheritance:

.. autoclass:: Load.ShapeFunction
    :members:
    :show-inheritance: