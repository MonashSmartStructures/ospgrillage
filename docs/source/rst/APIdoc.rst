====================
API documentation
====================

OpsGrillage class
---------------------------

..  autoclass:: OpsGrillage.OpsGrillage
    :noindex:


For information regarding the procedures in ``opGrillage`` class, see
:doc:`ModuleDoc`. For information of all functions and methods in ``opGrillage`` class, see :doc:`OpsGrillage`

Input arguments for Bridge:

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



Material class
------------------------------------------

..  autoclass:: OpsGrillage.Material
    :noindex:

GrillageMember class
------------------------------------------

..  autoclass:: OpsGrillage.GrillageMember
    :noindex:

