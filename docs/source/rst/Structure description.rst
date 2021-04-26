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

Upon running this line, the output file writes model() and node() commands into the output file "Example_superT_10m".
Running the output file at this stage will construct the model space (model command) and generate the nodes of the model
(node command).


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

.. code-block:: python
    test_bridge.set_grillage_long_mem(longmem_prop, longmem_prop.beam_ele_type, group=3)



Setting material and section properties of grillage members
------------------------


.. code-block:: python

    # define material
    test_bridge.set_uniaxial_material(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])




Creating grillage members
------------------------

.. code-block:: python

    longmem_prop = Member("I-grider", 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58)


Using generated grillage for analysis
------------------------

The first step on using the grillage model for analysis is defining Openseespy analysis objects, namely using the
pattern() and constraint() classess. Based on the desired analysis, users can add these lines of code manually to
the output file.

Alternatively, users can run the class function `perform_gravity_analysis()` to conduct a simple gravity load analysis.
The class function is also a good way to test run the model.

Viewing results
------------------------

The following example displays the deflected shape for the example bridge.

.. code-block:: python

    import PlotWizard
    plot_section(test_bridge, test_bridge.long_edge_1, 'b')

Alternatively, result visualization can be achieved using the Openseespy module - ops_vis. The `ops_vis` module is one
of the post-processing modules of Openseespy.

The main commands of ops_vis module can be found `here <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_