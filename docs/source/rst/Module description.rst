========================
Creating grillage models
========================
Here is how grillage models are created with *ops-grillage* module. Steps are explained in more detail
throughout the rest of the documentation.

To begin, import :class:`~OpsGrillage` as ``opsg`` or other abbreviation. You can import the whole module's functions using asterisk.
We will also import the *openseespy* visualization tool for visualization purposes.

.. code-block:: python

    import OpsGrillage as opsg
    import openseespy.postprocessing.ops_vis as opsv

In general, there are three main steps to create a grillage model when using the *ops-grillage* module:

#. Defining elements of grillage model using the :class:`~GrillageMember` class; requiring a :class:`~Section` and :class:`~Material` class object.
#. Creating the grillage object using the :class:`~OpsGrillage` class.
#. Assigning the elements of grillage model using ```set_member()``` methods.

This example explains the procedures by creating an example grillage as shown in Figure 1:

.. _Figure 1:

..  figure:: ../images/42degnegative10m.png
    :align: center
    :scale: 75 %

    Figure 1: Instance of the model created in Opensees.

.. _defining Grillage member:

Defining elements of grillage model
------------------------------------------------------------------
A grillage element is created using the :class:`GrillageMember` class. A :class:`GrillageMember` object requires two
objects as inputs, namely:

#. *material* = A :class:`Material` class object, and
#. *section* = A :class:`Section` class object.

A *member_name* string input is optional. The following example code line instantiates a :class:`GrillageMember` object of some intermediate concrete I-beams,
with material and section defintions explained next.

.. code-block:: python

    I_beam = opsg.GrillageMember(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)

When setting up grillage members, it is often a good idea to first instantiate a :class:`~Section` and :class:`~Material` class objects before creating
each :class:`GrillageMember` class objects.

Creating material objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A :class:`~Material` class object is needed when `defining Grillage member`_.

Using the vairable *mat_type*, users have the option to define the material type,
followed by the subsequent inputs required.
The material model types are based on `Opensees database for concrete and steel <https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterial.html#steel-reinforcing-steel-materials>`_.
Therefore, users should be familiar with this database and the subsequent inputs requied.

The following example code line creates the Opensees concrete material Concrete01 for uses in a grillage member.

.. code-block:: python

    concrete = opsg.UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6.0,epsc0=-0.004,fpcu=-6.0,epsU=-0.014)

For most bridges made of steel and concrete, material properties of either concrete and steel can be defined using
keyword "steel" or "concrete" passed as an argument to :class:`~Material` class.

Creating section objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Similar to :class:`Materials`, a :class:`Section` class object is needed when `defining Grillage member`_.

A :class:`Section` class takes in section parameters based on Opensees definition of element types.
Refer to `Opensees element command <https://openseespydoc.readthedocs.io/en/latest/src/element.html>`_ for specifics on
element types.
Using the variable *op_section_type*, users have the option to define the section type,
followed by the subsequent inputs required. The defauly is an *Elastic* section.
Non-prismatic members are currently not supported.

This example we create an *Elastic* section with required input parameters for an Opensees *Elastic* section for use in a grillage member:

.. code-block:: python

    # define sections
    I_beam_section = opsg.Section(op_section_type='Elastic', A=0.896, E=3.47E+10, G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259,
									Ay=0.233, Az=0.58)


Creating the grillage model
-------------------------------------------
Currently, the :class:`OpsGrillage` class creates the grillage model for a simply-supported
beam-and-slab bridge deck. The model comprises of standard grillage members of:

- Two longitudinal edge beams
- Two longitudinal exterior beams
- Remaining longitudinal interior beams
- Two transverse edge slabs
- Remaing transverse slabs

The :class:`~OpsGrillage` class takes:

- ``bridge_name``: A :py:class:`str` of the grillage model name.
- ``long_dim``: A :py:class:`float` of the longitudinal length of the grillage model.
- ``width``: A :py:class:`float` of the transverse width of the grillage model.
- ``skew``: A :py:class:`float` of the skew angle at the ends of grillage model. This variable can take in a :py:class:`list` of of 2 skew angles - this in turn creates the grillage model having edges with different skew angles. Moreover, it is limited to :math:`\arctan`(``long_dim``/``width``)
- ``num_long_grid``: An :py:class:`int` of the number of grid lines along the longitudinal direction - each grid line represents the total number of longitduinal members. Lines are evenly spaced, except for the spacing between the edge beam and exterior beam
- ``num_trans_grid``: An :py:class:`int` of the number of grid lines to be uniformly spaced along the transverse direction - each grid line represents the total number of transverse members.
- ``edge_beam_dist``: A :py:class:`float` of the distance between exterior longitudinal beams to edge beam.
- ``mesh_type``: Mesh type of grillage model. Must take a :py:class:`str` input of either "Ortho" or "Oblique". The default is "Ortho" (an orthogonal mesh). However, "Ortho" is not accepted for certain skew angles.

For the example bridge, the following code line with the prescribed variables creates the :class:`~OpsGrillage` object:

.. code-block:: python

    example_bridge = opsg.OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-21,
                         num_long_grid=7, num_trans_grid=17, edge_beam_dist=1, mesh_type="Ortho")


Coordinate System
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In an orthodonal mesh, longitduinal members run along the :math:`x`-axis direction and tranverse members are in the :math:`z`-axis direction.
Vertical (normal to grid) loads are applied in the :math:`y`-axis.



Assigning grillage members
-------------------------------------------------
The :class:`GrillageMember` objects are assigned to the grillage model using the `set_member()` method of ``OpsGrillage`` class. The function takes a `GrillageMember` class
object, and a member string tag as arguments. 

The member string tag specifies the standard grillage element to assign the ``GrillageMember`` object.

Table 1: Current supported member string tag

===================================   ===========================================================================
   `edge_beam`                           for both edge longitudinal beams
   `exterior_main_beam_1`                for the first exterior longitduinal beam along x-axis (nearest to 0 on z-axis)
   `exterior_main_beam_2`                for the second exterior longitduinal beam along x-axis
   `interior_main_beam`                  for all other longitudinal beams
   `start_edge`                          for the first edge transverse slab along z-axis (0 on x-axis)
   `end_edge`                            for the second edge transverse slab along z-axis
   `transverse_slab`                     for all other transverse slab
 ===================================   ===========================================================================

This example shows the assignment of interior main beams with the example intermediate concrete I-beams:

.. code-block:: python
    
	example_bridge.set_member(I_beam, member="interior_main_beam")


For skew meshes without customized node points, the grillage elements typically comprised of standardized element groups.

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

Creating grillage in Opensees model space or as an executable py file
-----------------------------------------------------------
Only once the object of grillage model is created and members are assigned, we can either: 

(i) create the model in Opensees software space for further grillage analysis, or;
(ii) an executable python file that can be edited and used for a more complex analysis.

These are achieved by calling the `create_ops()` function. 

The `create_ops()` function takes a boolean for `pyfile=` parameter which by default is `False`. 
Setting False creates the
grillage model in Opensees model space to immediately perform further analysis (see more in documentation). 

.. code-block:: python

    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)

Up to this point, users can run any Opensees command (e.g. `ops_vis` commands) within the interface to interact with
the grillage model in Opensees.

Alternatively, when `pyfile=` parameter is set to `True`, an executable py file will be generated instead. 
The executable py file contains all relevent Opensees command from which when executed, 
creates the model instance in Opensees which can edited and later used to perform more complex analysis.
Note that in doing so, the model instance in Opensees space is not created.

Visualize grillage model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To check that we created the model in Opensees space, we can plot the model using Opensees's visualization module `ops_vis`.
Run the following code line and a plot like in `Figure 1`_ will be returned:

.. code-block:: python

    opsplt.plot_model("nodes")
	
Whilst all nodes will be visualized, only the assigned members are visualized.
Failure to not have all members assigned will cause subsequent analysis not to work.

Here are more details of `ops_vis module <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_
