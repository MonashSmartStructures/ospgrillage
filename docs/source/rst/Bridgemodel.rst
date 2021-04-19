====================
API documentation
====================

GrillageGenerator class
---------------------------

.. automodule:: GrillageGenerator
   :members:


For information on the ``GrillageGenerator`` class, see
:doc:`ModuleDoc`

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

    test_bridge = GrillageGenerator(bridge_name="Example_superT_10m", long_dim=10, width=5, skew=25,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")




Defining concrete and steel properties
------------------------------------------

Defining element and section properties
------------------------------------------


Execute output py file
------------------------------------------
And output .py file named "Example_superT_10m_op.py" is created simultaneously in the current directory.
The py file is and executable file which upon execution creates the required bridge model in Opensees software.