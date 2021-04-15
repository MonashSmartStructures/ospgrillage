====================
opsy-grillage module
====================

.. automodule:: GrillageGenerator
   :members:


The following contain information about the properties of ``GrillageGenerator``
:doc:`ModuleDoc`

   ================================   ===========================================================================
   ``constraintType`` |str|           constraints type
   ``constraintArgs`` |list|          a list of constraints arguments
   ================================   ===========================================================================

Example: Call structure
---------------------------



.. code-block:: python

    test_bridge = GrillageGenerator(bridge_name="Example_superT_10m", long_dim=10, width=5, skew=25,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="ob")
