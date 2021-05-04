========================
Using the grillage wizard
========================

The process of using the *ops-grillage* module can be categorized into three steps:

#. Creating the grillage object using the :class:`~opsGrillage` class.
#. Defining elements of grillage model using the :class:`~member` class.
#. Setting the elements of grillage model using ``set_member()`` and ``set_material()`` functions for grillage `sections`
   and `material` properties respectively.

Note these processes have no definite order. For instances, users can define all elements of the grillage model prior to generating the
:class:`~opGrillage` model object.

Creating the grillage model
---------------------------
The grillage model is defined using the :class:`~opGrillage` class. Input arguments of the grillage model is pass to
create the :class:`opGrillage` class object.

..  autoclass:: OpsGrillage.opGrillage
    :noindex:


The following example creates a `opGrillage` class object for a bridge model.

.. code-block:: python

    test_bridge = opGrillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-21,
                         num_long_grid=2, num_trans_grid=17, cantilever_edge=1, mesh_type="Ortho")

This generates a bridge model named "SuperT_10m", which has the following properties:

#. Length = 10 m
#. Width = 5 m
#. skew angle of 21 degree clockwise (negative sign)
#. 2 node grids along the transverse (z axis) direction corresponding to interior beams
#. 13 nodes spaced evenly along the longitudinal (x axis)
#. Edge beam distance of 1 m
#. Orthogonal mesh


Upon running this line, the output file writes model() and node() commands into the output file "Example_superT_10m".
Running the output file at this stage will construct the model space (model command) and generate the nodes of the model
(node command).


Define material properties
------------------------

Material properties are defined using the class method `set_material()`. For most bridges made of steel and concrete,
material properties of either concrete and steel can be defined using the set keyword "steel" or "concrete" passed
as an argument to the function.

.. code-block:: python

    # define material
    test_bridge.set_material(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

Note for variable `mat_type`, users have the option to change the concrete type. The concrete model types are based on
Opensees database.

Creating section object for grillage member
------------------------

.. code-block:: python

    # define sections
    I_beam_section = Section(op_sec_tag='Elastic', A=0.896, E=3.47E+10, G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259,
                         Ay=0.233, Az=0.58)


For skew meshes, the elements are standardized. Table 1 shows the current standard elements of a grillage model along with the
respective str tags for arguments.

 ===================================   ===========================================================================
   1                                    edge_beam
   2                                    exterior_main_beam_1
   3                                    interior_main_beam
   4                                    exterior_main_beam_1
   5                                    edge_slab
   6                                    transverse_slab
 ===================================   ===========================================================================

For orthogonal meshes, nodes in the transverse direction may have varied spacing based on the skew edge region.
The properties of transverse members based on unit metre width is required for its definition section properties.
The module automatically implement the unit width properties based on the spacing of nodes in the skew edge regions.

The module checks if all element groups in the grillages are defined by the user. If missing element groups are detected,
a warning message is printed on the terminal.

Creating a grillage member
-----------------------------


.. code-block:: python
    # define member
    I_beam = GrillageMember(name="Intermediate I-beams", section_obj=I_beam_section, material_obj=concrete)


Setting grillage member to element group in model
-------------------------------------------------

The members of the grillage model is set using the `set_grillage_member()` function. The function takes a `member` class
object,a beam element tag (Openseespy), and a member string tag as arguments. The function the assigns the `member`
object to the element group in the grillage model.

An example showing the assignment of interior main beams:

.. code-block:: python
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="interior_main_beam")


Run grillage for analysis
------------------------

The first step on using the grillage model for analysis is defining Openseespy analysis objects, namely using the
pattern() and constraint() classess. Based on the desired analysis, users can add these lines of code manually to
the output file.

Alternatively, users can run the class function `perform_gravity_analysis()` to conduct a simple gravity load analysis.
The class function is also a good way to test run the model.

Viewing results
------------------------

A set of plotting functions are included as part of the `op-grillage` module - the `PlotWizard` command. To draw and
plot components of the model, users run the following example. In the example, the plot_section() function draws and
plots the longitudinal members of the grillage.

.. code-block:: python

    import PlotWizard
    plot_section(test_bridge, "interior_main_beam", 'r')

The `plot_section()` function is based on matplotlib plotting commands.

Alternatively, result visualization can be achieved using the Openseespy module - ops_vis. The `ops_vis` module is one
of the post-processing modules of Openseespy. The `ops-vis` module has gone through numerous updates and has reach
maturity for many post-processing applications. This is the recommended plotting feature at the current version of
`op-grillage`.

For example users can view the model using the `model()` command. To do this, users add the following command and the
end of the output py file.

.. code-block:: python

    ops.model()

The main commands of ops_vis module can be found `here <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_

