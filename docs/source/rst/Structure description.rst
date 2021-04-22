========================
Using the grillage wizard
========================

The process of using the *opGrillage* module can be categorized into three steps:

#. Creating the grillage object using the :class:`~opGrillage` class.
#. Defining elements of grillage model using the :class:`~member` class.
#. Specifying section and material properties using :class:`~material` and :class:`~section` class


Creating the grillage
------------------------
The first process is carried out using the `opGrillage` class. Input arguments of the grillage model is pass to
create the `GrillageGenerator` class object.

The following example creates a `GrillageGenerator` class object for a bridge model.

.. code-block:: python

    test_bridge = opGrillage(bridge_name="Example_superT_10m", long_dim=10, width=5, skew=-11,
                         num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="Ortho")




Define members of grillage model
------------------------
The members of the grillage model is set using the `set_grillage_member()` function.

Table 1 shows the standard elements of a grillage model

 ===================================   ===========================================================================
   1                                    longitudinal edge 1 (z = 0)
   2                                    longitudinal LR 1
   3                                    longitudinal
   4                                    longitudinal LR 2
   5                                    longitudinal edge 2 (z /= 0)
   6                                    Transverse edge 1
   7                                    Transverse LR 1
   8                                    Transverse
   9                                    Transverse LR 2
   10                                   Transverse edge 2
 ===================================   ===========================================================================



Setting material and section properties
------------------------


.. code-block:: python

    # define material
    test_bridge.set_uniaxial_material(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])




Assign material and section to grillage model
------------------------

.. code-block:: python

    longmem_prop = Member("I-grider", 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58)


Using generated grillage for analysis
------------------------

A simple

Viewing results
------------------------

Alternatively, result visualization can be achieved using the Openseespy module - ops_vis. The `ops_vis` module is one
of the post-processing modules of Openseespy.

The main commands of ops_vis module can be found `here <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_