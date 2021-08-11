====================
API reference
====================

This page outlines *ospgrillage*'s API. For detail regarding module design and algorithms, refer to :doc:`ModuleDoc`.


UML diagram overview
----------------------------

..  figure:: ../images/draftUML.PNG
    :align: center
    :scale: 50 %

    Figure 1: UML diagram - draft version 1.


User interface functions - API
------------------------------------------
This module comprised of user interface functions to take user inputs and returns its corresponding object creation.
Here is a summary of these functions.


.. autosummary::
    :toctree: generated/

    ospgrillage.osp_grillage.create_grillage
    ospgrillage.material.create_material
    ospgrillage.members.create_section
    ospgrillage.members.create_member
    ospgrillage.load.create_load_vertices
    ospgrillage.load.create_load
    ospgrillage.load.create_load_case
    ospgrillage.load.create_compound_load
    ospgrillage.load.create_moving_path
    ospgrillage.load.create_moving_load
    ospgrillage.mesh.create_point



OspGrillage class
---------------------------

.. autoclass:: ospgrillage.osp_grillage.OspGrillage
    :members:
    :show-inheritance:

Analysis class
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.osp_grillage.Analysis
    :members:
    :show-inheritance:


Result class
^^^^^^^^^^^^^^^^
.. autoclass:: ospgrillage.osp_grillage.Results
    :members:
    :show-inheritance:


Material class
------------------------------------------
For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`.


.. autoclass:: ospgrillage.material.Material
    :members:
    :show-inheritance:

Section class
------------------------------------------

.. autoclass:: ospgrillage.members.Section
    :members:
    :show-inheritance:

GrillageMember class
------------------------------------------

.. autoclass:: ospgrillage.members.GrillageMember
    :members:
    :show-inheritance:

Mesh class
------------------------------------------

.. autoclass:: ospgrillage.mesh.Mesh
    :members:
    :show-inheritance:

Load class
------------------------------------------
For information regarding definition of :class:`~Loads` class, see
:doc:`Loads`.

NodalLoad
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.NodalLoad
    :members:


PointLoad
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.PointLoad



LineLoading
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.LineLoading



PatchLoading
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.PatchLoading



CompoundLoad
------------------------------------------

.. autoclass:: ospgrillage.load.CompoundLoad
    :members:
    :show-inheritance:

MovingLoad
------------------------------------------

.. autoclass:: ospgrillage.load.MovingLoad
    :members:
    :show-inheritance:


LoadCase
------------------------------------------
For information regarding in :class:`~LoadCase` class, see
:doc:`Loads`.

.. autoclass:: ospgrillage.load.LoadCase
    :members:
    :show-inheritance:

Misc
------------------------------------------

LoadCase
^^^^^^^^^^^^^^^^
.. autoclass:: ospgrillage.load.Path
    :members:
    :show-inheritance:

Shape functions
^^^^^^^^^^^^^^^^
.. autoclass:: ospgrillage.load.ShapeFunction
    :members:
    :show-inheritance: