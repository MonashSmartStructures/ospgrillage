====================
API reference
====================

This page includes the technical content deliverables of the documentation. Instructions on variables and function
showing their interactions, both within and across various classes, are presented herein.

UML diagram overview
----------------------------



OpsGrillage class
---------------------------

..  autoclass:: OpsGrillage.OpsGrillage
    :noindex:


For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`. For information of all functions and methods in ``opGrillage`` class, see :doc:`OpsGrillage`



Node numbering

Meshing description

element grouping

Analysis objects
^^^^^^^^^^^^^^^^

..  autoclass:: OpsGrillage.Analysis
    :noindex:

..  autoclass:: OpsGrillage.Results
    :noindex:

Material class
------------------------------------------

..  autoclass:: OpsGrillage.Material
    :noindex:

GrillageMember class
------------------------------------------

..  autoclass:: OpsGrillage.GrillageMember
    :noindex:

Mesh class
------------------------------------------

Example table for copy paste usage:

   ================================   ===========================================================================
   ``bridge_name`` |str|              name string of bridge model
   ``long_dim`` |float|               longitudinal dimension argument
    ``width`` |float|                 width argument
    ``skew`` |float|                  skew angle argument: angle can be positive or negative (skew clockwise if positive)
    ``num_long_grid`` |float|         number of line meshes in the longitudinal direction
    ``num_trans_grid`` |float|        number of line mesh in the transverse direction
    ``cantilever_edge`` |float|       distance between edg
    ``mesh_type`` |str|               string argument for type of mesh:
                                        * "Ortho": Orthogonal mesh
                                        * "Oblique" : Skew mesh
   ================================   ===========================================================================


Load class
------------------------------------------

.. autoclass:: Load.Loads
   :noindex:

.. autoclass:: Load.NodalLoad
   :noindex:

.. autoclass:: Load.PointLoad
   :noindex:

.. autoclass:: Load.LineLoading
   :noindex:

.. autoclass:: Load.PatchLoading
   :noindex:

.. autoclass:: Load.CompoundLoad
   :noindex:

.. autoclass:: Load.Path
   :noindex:

.. autoclass:: Load.ShapeFunction
   :noindex:

