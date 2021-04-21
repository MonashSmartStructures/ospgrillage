========================
Structure of Analysis
========================

The process of using the `op-grillage` module can be categorized into three steps:

#. Creating the nodes and elements of the grillage model.
#. User specifying section and material properties for different members within the grillage model.
#. Usage of output executable file.

Define material and section properties
------------------------


Creating the grillage
------------------------
The first process is carried out using the `GrillageGenerator` class. Input arguments of the grillage model is pass to
create the `GrillageGenerator` class object.

The following example creates a `GrillageGenerator` class object for a bridge model.

.. code-block:: python

    test_bridge = GrillageGenerator(bridge_name="Example_superT_10m", long_dim=10, width=5, skew=25,
                    num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")



The

Set properties of grillage elements
------------------------

Table 1 shows the standard elements of a grillage model

 ===================================   ===========================================================================
   1                                    longitudinal
   2                                    longitudinal edge 1 (z = 0)
   3                                    longitudinal edge 2 (z /= 0)
   4                                    Transverse
   5                                    Transverse edge 1
   6                                        torsional moment of inertia of cross section
 ===================================   ===========================================================================


Performing analysis
------------------------

Viewing results
------------------------
