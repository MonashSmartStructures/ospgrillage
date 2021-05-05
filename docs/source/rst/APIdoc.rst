====================
API documentation
====================

GrillageGenerator class
---------------------------

..  autoclass:: OpsGrillage.opGrillage
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


Using wrapper module
---------------------------

The following shows the generation of an exemplar bridge model having the following properties:
* long_dim = 10 m
* width = 5
* skew = 11 degrees
* num_long_grid = 4
* num_trans_grid = 13
* cantilever_edge = 1 m
* mesh_type = Orthogonal ("Ortho")

Note: Units of inputs are newton (N), meter (m), and degrees ().

Users use ```GrillageGenerator``` class and input the arguments accordingly.

.. code-block:: python

    test_bridge = opGrillage(bridge_name="SuperT_10m", long_dim=20, width=15, skew=-11,
                         num_long_grid=6, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")




Material class
------------------------------------------

GrillageMember class
------------------------------------------


