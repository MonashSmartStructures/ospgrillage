========================
Creating grillage models
========================
The *ospgrillage* module contains **interface functions** which can be called following the module syntax. 
These interface functions generally have  ``set_``, ``create_`` or ``get_`` in their syntax. 
For example, :func:`~ospgrillage.material.create_material` creates a material object for the grillage model.

A list of all interface functions can be found in :doc:`APIdoc`.
Although users can opt to interact with module objects directly, we recommend the more pythonic interface functions.

Workflow overview
-----------------

Figure 1 summarizes the workflow of creating a grillage model using *ospgrillage*.

..  figure:: ../../_images/grillage_workflow.png
    :align: center
    :scale: 50 %

    Figure 1: Grillage model creation flow chart


In general, there are three steps to create a grillage model with *ospgrillage*:

#. Creating the grillage members.
#. Creating the grillage model object.
#. Assigning the defined grillage members to the elements of grillage model object.


We will detail these steps by creating a grillage model of a bridge deck as shown in Figure 2.

.. _Figure 2:

..  figure:: ../../_images/42degnegative10m.png
    :align: center
    :scale: 25 %

    Figure 2: Grillage model created using `OpenSeesPy`


To begin, import `ospgrillage` as either ``ospg`` or ``og`` as shown in the following code block.
As will be needed later, we also prepared the unit convention of variables for this example as shown in the same code block.

.. code-block:: python

    import ospgrillage as og
    # create unit signs for variables of example
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m ** 2
    m3 = m ** 3
    m4 = m ** 4
    kN = kilo * N
    MPa = N / ((mm) ** 2)
    GPa = kilo * MPa

.. _defining Grillage member:

Defining elements of grillage model
-----------------------------------
A grillage element is created using the :func:`~ospgrillage.members.create_member` interface function.
This function returns a :class:`~ospgrillage.members.GrillageMember` object,
which requires two other objects as inputs, namely:

#. *material* = A :class:`~ospgrillage.material.Material` class object, and
#. *section* = A :class:`~ospgrillage.members.Section` class object.

The following example code instantiates an *I_beam* grillage element to represent some intermediate concrete I-beam, with material and section definitions explained later on.

.. code-block:: python

    I_beam = og.create_member(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)


The *member_name* string input is optional.

When setting up grillage members, it is often a good idea to first instantiate a :class:`~ospgrillage.members.Section`
and :class:`~ospgrillage.material.Material` class objects before creating
each :class:`~ospgrillage.members.GrillageMember` class objects.

For the example bridge of Figure 2, lets define all its elements i.e. *slab*, *edge_beam*, and *edge_slab*.

.. code-block:: python

    slab = og.create_member(member_name="concrete slab", section=slab_section, material=concrete)
    edge_beam = og.create_member(member_name="edge beams", section=edge_beam_section,material=concrete)
    edge_slab = og.create_member(member_name="edge slab", section=edge_slab_section,material=concrete)

Creating material objects
^^^^^^^^^^^^^^^^^^^^^^^^^
The :class:`~ospgrillage.material.Material` object is created using :func:`~ospgrillage.material.create_material`.
The following code line creates the *concrete* material needed in`defining Grillage member`_ previously.

.. code-block:: python

    concrete = og.create_material(material="concrete", code="AS5100-2017", grade="50MPa")

Users can choose between steel or concrete material - by passing
keyword "steel" or "concrete" argument to :func:`~ospgrillage.material.create_material`. 
Users can specify properties of steel and concrete by passing its respective keyword argument to :func:`~ospgrillage.material.create_material`.
In addition, *ospgrillage* offers a library of codified material properties for steel and concrete to be selected.
At the moment, it has library for two code namely the Australia standard AS5100 and AASHTO LRFD-8th.

The following example creates the required *concrete* material for the example bridge.

.. code-block:: python

    concrete = og.create_material(E=30*GPa, G = 20*GPa, v= 0.2)

The :class:`~ospgrillage.material.Material` object wraps `OpenSees` material commands, and selects appropriate `OpenSees` material model to represent the material.
Presently, *Concrete01* and *Steel01* of OpenSees library are used to represent most concrete and steel material respectively.
Other material model can be found in `OpenSees database for concrete and steel <https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterial.html#steel-reinforcing-steel-materials>`_.

Creating section objects
^^^^^^^^^^^^^^^^^^^^^^^^
The :class:`~ospgrillage.members.Section` object for `defining Grillage member`_ is created using
:func:`~ospgrillage.members.create_section` function.

The following code line creates the :class:`~ospgrillage.members.Section` object called *I_beam_section*,
which is earlier passed as input for its corresponding *I_beam* :class:`~ospgrillage.members.GrillageMember` object:

.. code-block:: python

    I_beam_section = og.create_section(A=0.896*m2, J=0.133*m4, Iy=0.213*m4, Iz=0.259*m4, Ay=0.233*m2, Az=0.58*m2)

The module's :class:`~ospgrillage.members.Section` object wraps
`OpenSees element command <https://openseespydoc.readthedocs.io/en/latest/src/element.html>`_.

The following codes creates the sections for the other grillage elements specified previously:

.. code-block:: python

    edge_beam_section = og.create_section(A=0.044625*m2,J=2.28e-3*m4, Iy=2.23e-1*m4,Iz=1.2e-3*m4, Ay=3.72e-2*m2, Az=3.72e-2*m2)
    edge_slab_section = og.create_section(A=0.039375*m2,J=0.21e-3*m4, Iy=0.1e-3*m2,Iz=0.166e-3*m2,Ay=0.0328*m2, Az=0.0328*m2))

For transverse members, there is an option to define **unit width properties**. 
This is done by passing True to keyword argument ``unit_width``.
When enabled, *ospgrillage* will automatically assigns these properties of slab section based on the spacing of transverse members.

.. code-block:: python

    slab_section = og.create_section(A=0.04428*m2, J=2.6e-4*m4, Iy=1.1e-4*m4, Iz=2.42e-4*m4,Ay=3.69e-1*m2, Az=3.69e-1*m2, unit_width=True)

.. note::

    **unit width** is required when creating grillages with skewed angle edges.

    For release 0.1.0, Non-prismatic members are currently not supported.


Creating the grillage model
---------------------------
After creating the grillage elements, users create the grillage model using :func:`~ospgrillage.osp_grillage.create_grillage` interface function.

Presently, grillage models typically represent a simply-supported
beam-and-slab bridge deck.
The model comprises of standard grillage members which includes:

- Two longitudinal edge beams
- Two longitudinal exterior beams
- Remaining longitudinal interior beams
- Two transverse edge slabs
- Remaining transverse slabs

Figure 3 illustrates these standard grillage members and their position on an exemplar orthogonal grillage mesh.

.. figure:: ../../_images/grillage_elements.png
    :align: center
    :scale: 75 %

    Figure 3: Standard elements supported by *ospgrillage*

**Supports are automatically set at nodes  along grid A (2 to 6) and grid E (9 to 13)  as pinned and roller respectively.**

The :class:`~ospgrillage.osp_grillage.OspGrillage` class takes the following keyword arguments:

- ``bridge_name``: A :py:class:`str` of the grillage model name.
- ``long_dim``: A :py:class:`float` of the longitudinal length of the grillage model.
- ``width``: A :py:class:`float` of the transverse width of the grillage model.
- ``skew``: A :py:class:`float` of the skew angle at the ends of grillage model.
This variable can take in a :py:class:`list` of of 2 skew angles - this in turn creates the grillage model having edges with different skew angles.
Moreover, it is limited to :math:`\arctan`(``long_dim``/``width``) - ``num_long_grid``: An :py:class:`int` of the number of grid lines along the longitudinal direction - each grid line represents the total number of longitduinal members. 
Lines are evenly spaced, except for the spacing between the edge beam and exterior beam
- ``num_trans_grid``: An :py:class:`int` of the number of grid lines to be uniformly spaced along the transverse direction - each grid line represents the total number of transverse members.
- ``edge_beam_dist``: A :py:class:`float` of the distance between exterior longitudinal beams to edge beam.
- ``mesh_type``: Mesh type of grillage model.
- ``ext_to_int_dist``: A :py:class:`float` of the distance between exterior longitudinal beams to adjacent interior beams.

Must take a :py:class:`str` input of either "Ortho" or "Oblique".
The default is "Ortho" (an orthogonal mesh).
However, "Ortho" is not accepted for certain skew angles.
The threshold for orthogonal mesh is greater than 11 degree- less than 11 degree the mesh will change to Oblique

Figure 4 shows how the grid numbers and skew angles affects the output mesh of grillage model.

..  figure:: ../../_images/grillage_dimensions.png
    :align: center
    :scale: 75 %

    Figure 4: Example grid numbers and edge angles


For the example bridge in Figure 2, the following code line creates its :class:`~ospgrillage.osp_grillage.OspGrillage` object i.e. *example_bridge*:

.. code-block:: python

    example_bridge = og.create_grillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-21,
                         num_long_grid=7, num_trans_grid=17, edge_beam_dist=1, mesh_type="Ortho")


Coordinate System
^^^^^^^^^^^^^^^^^
In an orthogonal mesh, longitudinal members run along the :math:`x`-axis direction and transverse members are in the :math:`z`-axis direction.
Vertical (normal to grid) loads are applied in the :math:`y`-axis.


Assigning grillage members
--------------------------
The :class:`~ospgrillage.members.GrillageMember` objects are assigned to the grillage model using :class:`~ospgrillage.osp_grillage.OspGrillage` object's
:func:`~ospgrillage.osp_grillage.OspGrillage.set_member` function.
In addition to a :class:`~ospgrillage.members.GrillageMember` argument, the function requires a member name string argument.

The member string specifies the standard grillage element for which the :class:`~ospgrillage.members.GrillageMember` is assigned.
Table 1 summarizes the name strings available for *ospgrillage*.


.. list-table:: Table: 1 Current supported member string and tags
   :widths: 50 50
   :header-rows: 0

   * - Grillage name String
     - Description
   * - ``edge_beam``
     - Elements along x axis at top and bottom edges of mesh (z = 0, z = width)
   * - ``exterior_main_beam_1``
     - Elements along first grid line after bottom edge (z = 0)
   * - ``exterior_main_beam_2``
     - Elements along first grid line after top edge (z = width)
   * - ``interior_main_beam``
     - For all elements in x direction between grid lines of exterior_main_beam_1 and exterior_main_beam_2
   * - ``start_edge``
     - Elements along z axis where longitudinal grid line x = 0
   * - ``end_edge``
     - Elements along z axis where longitudinal grid line x = Length
   * - ``transverse_slab``
     - For all elements in transverse direction between start_edge and end_edge


The following example assigns the interior main beams of the grillage model with the earlier object of intermediate concrete *I-beam*:

.. code-block:: python

    example_bridge.set_member(I_beam, member="interior_main_beam")

For the example in Figure 1, the rest of grillage elements are assigned as such:

.. code-block:: python

    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(edge_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(edge_slab, member="start_edge")
    example_bridge.set_member(edge_slab, member="end_edge")

For orthogonal meshes, nodes in the transverse direction have varied spacing based on the skew edge region.
The properties of transverse members based on unit metre width is required for its definition section properties.
The module automatically implement the unit width properties based on the spacing of nodes in the skew edge regions.

The module checks if all element groups in the grillages are defined by the user. 
If missing element groups are detected, a warning message is printed on the terminal.

The :class:`~ospgrillage.osp_grillage.OspGrillage` class also allows for global material definition - e.g. an entire bridge made of the same
material. 
To do this, users run the function :func:`~set_material` passing the :class:`~Material` class object as the
input.

.. code-block:: python

    example_bridge.set_material(concrete)


This is a useful tool for switching all grillage members to the same material after previously defining with perhaps a different material.

Creating/exporting OpenSees Model
---------------------------------
Only once the :class:`~ospgrillage.osp_grillage.OspGrillage` is created and members are assigned, we can either:

(i) create the model in `OpenSees` software space for further grillage analysis, or;
(ii) export an executable python file that can be edited and used for a more complex analysis.

These are achieved by calling the :func:`~ospgrillage.osp_grillage.OspGrillage.create_osp_model` function.

The :func:`~ospgrillage.osp_grillage.OspGrillage.create_osp_model` function takes a boolean for `pyfile=` (default is `False`).
Setting this parameter to ``False`` creates the grillage model in `OpenSees` model space.

.. code-block:: python

    example_bridge.create_osp_model(pyfile=False)

After model is instantiated in `OpenSees`, users can run any `OpenSeesPy` command (e.g. `ops_vis` commands) within the current workflow
to interact with the `OpenSees` grillage model.

When `pyfile=` parameter is set to `True`, an executable py file will be generated instead.
The executable py file contains all relevant `OpenSeesPy` command from which when executed, creates the model instance in OpenSees which can edited and later used to perform more complex analysis.
Note that in doing so, the model instance in `OpenSees` space is not created.

Visualize grillage model
^^^^^^^^^^^^^^^^^^^^^^^^
To check that we created the model in `OpenSees` space, we can plot the model using `OpenSeesPy`'s visualization module `ops_vis`.
The *ospgrillage* module already imports the `ops_vis` module.
Therefore, one can run access `ops_vis` by running the following code line and a plot like in `Figure 2`_ will be returned:

.. code-block:: python

    og.opsplt.plot_model(show_nodes="yes",show_nodetags="yes") # using Vfo module
    og.opsv.plot_model(az_el=(-90, 0)) # using osp_vis

Whilst all nodes will be visualized, only the assigned members are visualized.
This is a good way to check if desired members are assigned and hence, shown on the plot.
Failure to not have all members assigned will affect subsequent analysis.

Here are more details of `ops_vis module <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_
