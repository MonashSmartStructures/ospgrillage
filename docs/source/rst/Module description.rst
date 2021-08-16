========================
Creating grillage models
========================
The *ospgrillage* module contains user **interface functions** which can be called after the module syntax. These interface function
has  ``set_``, ``create_`` or ``get_`` in their syntax. For example, users create a material with ``create_material()``.
Alternatively, users can directly interact with the module objects without using interface functions - we recommend the more pythonic interface functions.

Figure 1 summarizes the process of creating grillage models using *ospgrillage*.

..  figure:: ../../_images/flowchart1.png
    :align: center
    :scale: 75 %

    Figure 1: Grillage model creation flow chart


In general, there are three main steps to create a grillage model with *ospgrillage*:

#. Creating elements of a grillage model i.e. members.
#. Creating the grillage model instance (the nodes and mesh).
#. Assigning the defined grillage members to the elements of grillage model instance.


We will detail these main steps by creating a grillage model of a bridge deck as shown in Figure 1.

.. _Figure 2:

..  figure:: ../../_images/42degnegative10m.png
    :align: center
    :scale: 25 %

    Figure 2: Grillage model created using OpenSeesPy


To begin, do import ``ospgrillage`` as either ``ospg`` or ``og``.
As will be needed later, we also prepared the unit convention of variables for this example as shown in the same code block.

.. code-block:: python

    import ospgrillage as ospg
    # create unit signs for variables of example
    N = 1
    m = 1
    Giga = 1e9
    Pa = N/m**2

.. _defining Grillage member:

Defining elements of grillage model
------------------------------------------------------------------
A grillage element is created using the interface function ``create_member()``. The following example code line instantiates
an *I_beam* element to represent some intermediate concrete I-beam, with material and section definitions explained later on.

.. code-block:: python

    I_beam = ospg.create_member(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)

This function parses the keyword inputs and returns a
:class:`GrillageMember` object . A :class:`GrillageMember` object requires two objects as inputs passed
as keyword arguments, namely:

#. *material* = A :class:`Material` class object, and
#. *section* = A :class:`Section` class object.

The *member_name* string input is optional.

When setting up grillage members, it is often a good idea to first instantiate a :class:`~Section` and :class:`~Material` class objects before creating
each :class:`GrillageMember` class objects.

For the example bridge, lets define all its elements i.e. *slab*, *edge_beam*, and *edge_slab*.

.. code-block:: python

    slab = ospg.create_member(member_name="concrete slab", section=slab_section, material=concrete)
    edge_beam = ospg.create_member(member_name="edge beams", section=edge_beam_section,material=concrete)
    edge_slab = ospg.create_member(member_name="edge slab", section=edge_slab_section,material=concrete)

Creating material objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To create a material, users call ``create_material()``  or directly creating a :class:`~Material` object.
The following code line creates the a *concrete* material needed `defining Grillage member`_.

.. code-block:: python

    concrete = ospg.create_material(type="concrete", code="AS5100-2017", grade="50MPa")

For most bridges made of steel and concrete, material properties of either concrete and steel can be defined using
keyword "steel" or "concrete" passed as an argument to :class:`~Material` class.
In addition, *ospgrillage* offers a library of codified material properties for steel and concrete to be selected.
On first release, it has library for two code namely the Australia standard AS5100 and AASHTO LRFD-8th.

As an alternative to material library, users can specify custom properties of steel and concrete by passing in keyword arguments.
The following code shows how a concrete material can be created using keyword arguments:

.. code-block:: python

    concrete = ospg.create_material(E=30*Giga*Pa, G = 20*Giga*Pa, v= 0.2)

This command wraps OpenSees material commands and chooses the appropriate material model in OpenSees to represent the material.
For example, *Concrete01* and *Steel01* of OpenSees library is used to represent most concrete and steel material.

These material model can be found in `OpenSees database for concrete and steel <https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterial.html#steel-reinforcing-steel-materials>`_.
Being a module wrapper, users familiar with this database can directly input the keywords of exact material models to ``create_material()`` function.

Creating section objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Similar to :class:`Material`, a :class:`Section` class object is needed when `defining Grillage member`_.

To create sections, users call the ``create_section()`` function which returns a :class:`Section` class object. Similarly, users can interact with
:class:`Section` class directly.

The following code line creates a :class:`Section` object called *I_beam_section*, which is earlier passed as input for its corresponding grillage element, *I_beam*:

.. code-block:: python

    I_beam_section = ospg.create_section(A=0.896*m**2, J=0.133*m**4, Iy=0.213*m**4, Iz=0.259*m**4, Ay=0.233*m**2, Az=0.58*m**2)

The module's :class:`Section` object wraps OpenSees's `element()` command.
Similar to :class:`Material`, users familiar with certain OpenSees element can pass its input parameters as keyword arguments
based on OpenSees definition of element types.
Heres a link to `OpenSees element command <https://openseespydoc.readthedocs.io/en/latest/src/element.html>`_ for specifics on the
element types and inputs.

Creating the rest of the sections for the aforementioned grillage elements:

.. code-block:: python

    slab_section = ospg.create_section(A=0.04428*m**2, J=2.6e-4*m**4, Iy=1.1e-4*m**4, Iz=2.42e-4*m**4,Ay=3.69e-1*m**2, Az=3.69e-1*m**2, unit_width=True)
    edge_beam_section = ospg.create_section(A=0.044625*m**2,J=2.28e-3*m**4, Iy=2.23e-1*m**4,Iz=1.2e-3*m**4, Ay=3.72e-2*m**2, Az=3.72e-2*m**2)
    edge_slab_section = ospg.create_section(A=0.039375*m**2,J=0.21e-3*m**4, Iy=0.1e-3*m**2,Iz=0.166e-3*m**2,Ay=0.0328*m**2, Az=0.0328*m**2))


.. note::

    For release 0.1.0, Non-prismatic members are currently not supported.


Creating the grillage model
-------------------------------------------
To create the grillage model instance, users run the ``create_grillage()`` function. Again, users can directly interact with
:class:`OpsGrillage` class, which is also returned by ``create_grillage()``.

Currently, *ospgrillage* module creates grillage model representing a simply-supported
beam-and-slab bridge deck. The model comprises of standard grillage members of:

- Two longitudinal edge beams
- Two longitudinal exterior beams
- Remaining longitudinal interior beams
- Two transverse edge slabs
- Remaining transverse slabs

Figure 3 illustrates the standard grillage members and their position on an exemplar orthogonal grillage mesh.

..  figure:: ../../_images/Standard_elements.PNG
    :align: center
    :scale: 75 %

    Figure 3: Standard elements supported by *ospgrillage*

The :class:`~OpsGrillage` class takes the following keyword arguments:

- ``bridge_name``: A :py:class:`str` of the grillage model name.
- ``long_dim``: A :py:class:`float` of the longitudinal length of the grillage model.
- ``width``: A :py:class:`float` of the transverse width of the grillage model.
- ``skew``: A :py:class:`float` of the skew angle at the ends of grillage model. This variable can take in a :py:class:`list` of of 2 skew angles - this in turn creates the grillage model having edges with different skew angles. Moreover, it is limited to :math:`\arctan`(``long_dim``/``width``)
- ``num_long_grid``: An :py:class:`int` of the number of grid lines along the longitudinal direction - each grid line represents the total number of longitduinal members. Lines are evenly spaced, except for the spacing between the edge beam and exterior beam
- ``num_trans_grid``: An :py:class:`int` of the number of grid lines to be uniformly spaced along the transverse direction - each grid line represents the total number of transverse members.
- ``edge_beam_dist``: A :py:class:`float` of the distance between exterior longitudinal beams to edge beam.
- ``mesh_type``: Mesh type of grillage model. Must take a :py:class:`str` input of either "Ortho" or "Oblique". The default is "Ortho" (an orthogonal mesh). However, "Ortho" is not accepted for certain skew angles.

Figure 3 shows how the grid numbers and skew angles affects the output mesh of grillage model.

..  figure:: ../../_images/edge_angles.PNG
    :align: center
    :scale: 75 %

    Figure 3: Grid numbers and edge angles


For the example bridge in Figure 2, the following code line creates its :class:`~OpsGrillage` object i.e. *example_bridge*:

.. code-block:: python

    example_bridge = ospg.create_grillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-21,
                         num_long_grid=7, num_trans_grid=17, edge_beam_dist=1, mesh_type="Ortho")


Coordinate System
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In an orthodonal mesh, longitduinal members run along the :math:`x`-axis direction and transverse members are in the :math:`z`-axis direction.
Vertical (normal to grid) loads are applied in the :math:`y`-axis.


Assigning grillage members
-------------------------------------------------
The :class:`GrillageMember` objects are assigned to the grillage model using the ``set_member()`` interface function. The function takes a :class:`GrillageMember` class
object, and a member string tag as arguments. 

The member string tag specifies the standard grillage element to assign the :class:`GrillageMember` object.


.. list-table:: Table: 1 Current supported member string and tags
   :widths: 50 50
   :header-rows: 0

   * - `edge_beam`
     - Elements along x axis at top and bottom edges of mesh (z = 0, z = width)
   * - `exterior_main_beam_1`
     - Elements along first grid line after bottom edge (z = 0)
   * - `exterior_main_beam_2`
     - Elements along first grid line after top edge (z = width)
   * - `interior_main_beam`
     - For all elements in x direction between grid lines of exterior_main_beam_1 and exterior_main_beam_2
   * - `start_edge`
     - Elements along z axis where longitudinal grid line x = 0
   * - `end_edge`
     - Elements along z axis where longitudinal grid line x = Length
   * - `transverse_slab`
     - For all elements in transverse direction between start_edge and end_edge


Heres the codeline that assigns interior main beams of the grillage model with the earlier object of intermediate concrete *I-beam*:

.. code-block:: python
    
	example_bridge.set_member(I_beam, member="interior_main_beam")

And the rest of grillage elements are assigned as such

.. code-block:: python

	example_bridge.set_member(I_beam, member="interior_main_beam")
	example_bridge.set_member(I_beam, member="exterior_main_beam_1")
	example_bridge.set_member(I_beam, member="exterior_main_beam_1")
	example_bridge.set_member(edge_beam, member="edge_beam")
	example_bridge.set_member(slab, member="transverse_slab")
	example_bridge.set_member(edge_slab, member="edge_slab")


For orthogonal meshes, nodes in the transverse direction have varied spacing based on the skew edge region.
The properties of transverse members based on unit metre width is required for its definition section properties.
The module automatically implement the unit width properties based on the spacing of nodes in the skew edge regions.

The module checks if all element groups in the grillages are defined by the user. If missing element groups are detected,
a warning message is printed on the terminal.

The :class:`~OpsGrillage` class also allows for global material definition - e.g. an entire bridge made of the same
material. To do this, users run the function ```set_material()``` passing the :class:`~Material` class object as the
input.

.. code-block:: python

    example_bridge.set_material(concrete)


This is a useful tool for switching all grillage members to the same material after previously defining with perhaps a different material.

Creating grillage in OpenSees model space or as an executable py file
-----------------------------------------------------------
Only once the object of grillage model is created and members are assigned, we can either: 

(i) create the model in OpenSees software space for further grillage analysis, or;
(ii) an executable python file that can be edited and used for a more complex analysis.

These are achieved by calling the ``create_ops()`` function.

The ``create_osp_model()`` function takes a boolean for `pyfile=` parameter which by default is `False`.
Setting False creates the
grillage model in OpenSees model space to immediately perform further analysis (see more in documentation).

.. code-block:: python

    example_bridge.create_osp_model(pyfile=False)

Up to this point, users can run any ``OpenSeesPy`` command (e.g. `ops_vis` commands) within the interface to interact with
the grillage model in OpenSees.

Alternatively, when `pyfile=` parameter is set to `True`, an executable py file will be generated instead. 
The executable py file contains all relevant OpenSees command from which when executed,
creates the model instance in OpenSees which can edited and later used to perform more complex analysis.
Note that in doing so, the model instance in OpenSees space is not created.

Visualize grillage model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To check that we created the model in OpenSees space, we can plot the model using ``OpenSeesPy``'s visualization module `ops_vis`.
The *ospgrillage* module already wraps and import ``OpenSeesPy``'s `ops_vis` module. Therefore, one can run access `ops_vis` by running
the following code line and a plot like in `Figure 2`_ will be returned:

.. code-block:: python

    ospg.opsplt.plot_model("nodes")
	
Whilst all nodes will be visualized, only the assigned members are visualized. This is a good way to check if desired members are assigned
and hence, shown on the plot. Failure to not have all members assigned will affect subsequent analysis.

Here are more details of `ops_vis module <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_
