========================
Creating grillage models
========================
Here are the some examples of what you can do with *ops-grillage* module. Examples are explained in more detail
throughout the rest of the documentation.

To begin, import :class:`~OpsGrillage` and Opensees using abbrevations or as a whole using asterisk. For this example,
we import the entire module's components to showcase the various functions and classes. In addition, we import the Opensees visualization module
to plot the grillage model.

.. code-block:: python

    from OpsGrillage import *
    import openseespy.postprocessing.ops_vis as opsv

There are three main stages when using the *ops-grillage* module:

#. Defining elements of grillage model using the :class:`~Member` class, and :class:`~Material` class.
#. Creating the grillage object using the :class:`~OpsGrillage` class.
#. Setting the elements of grillage model using ```~set_member()``` and ```~set_material()``` functions.

In this example we will detail the steps in order to create an example grillage as shown in Figure 1:

..  figure:: ../images/Module_description_1.png
    :align: center
    :scale: 75 %

    Figure 1: Instance of the model created in Opensees.


Creating the grillage model
-------------------------------------------
The :class:`~OpsGrillage` class takes:

- ``bridge_name``: A string of the grillage model name.
- ``long_dim``: An :py:class:`float` of the longitudinal length of the grillage model.
- ``width``: An :py:class:`float` of the transverse width of the grillage model.
- ``skew``: A :py:class:`float` of the skew angle at the ends of grillage model. This variable can take in a :py:class:`list` of of 2 skew angles - this in turn creates the grillage model having edges with different skew angles.
- ``num_long_grid``: An :py:class:`int` of the number of grids to be uniformly spaced along the longitudinal direction - each grid line represents the transverse members.
- ``num_trans_grid``: An :py:class:`int` of the number of grids to be uniformly spaced along the transverse direction - each grid line represents the longitudinal members
- ``edge_beam_dist``: A :py:class:`float` of the distance between exterior longitudinal beams to edge beam.
- ``mesh_type``: Mesh type of grillage model. Must take a :py:class:`str` input of either "Orthogonal" or "Oblique".

Users run the following code line with the prescribed variables to create the :class:`~OpsGrillage` object of the example bridge:

.. code-block:: python

    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-21,
                         num_long_grid=2, num_trans_grid=17, edge_beam_dist=1, mesh_type="Ortho")


Creating and defining elements of grillage model
------------------------------------------------------------------
A grillage element is created using the :class:`GrillageMember` class. A :class:`GrillageMember` object has two
properties, namely:

*. Material - defined by a :class:`Material` class object, and
*. Section - defined by a :class:`Section` class object.

.. code-block:: python

    I_beam = GrillageMember(name="Intermediate I-beams", section=I_beam_section, material=concrete)
    Material properties are defined in two steps:


Creating material objects
------------------------------------------------------------------

#. Creating a :class:`~Material` class object of the bridge material.
#. Setting the :class:`~Material` class object to a :class:`~GrillageMember` class object.

For most bridges made of steel and concrete, material properties of either concrete and steel can be defined using
keyword "steel" or "concrete" passed as an argument to :class:`~Material` class. For currently available material
types see

.. code-block:: python

    concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

The :class:`~OpsGrillage` class also allows for global material definition - e.g. an entire bridge made of the same
material. To do this, users run the function ```set_material()``` passing the :class:`~Material` class object as the
input.

.. code-block:: python

    test_bridge.set_material(concrete)

Note for variable `mat_type`, users have the option to change the concrete type. The concrete model types are based on
Opensees database.

Creating section objects
------------------------------------------------
A section is created using the :class:`Section` class which takes:


An example section creation is shown as follows:

.. code-block:: python

    # define sections
    I_beam_section = Section(op_sec_tag='Elastic', A=0.896, E=3.47E+10, G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259,
                         Ay=0.233, Az=0.58)



For skew meshes without customized node points, the grillage elements typically comprised of standardized element groups.
Table 1 shows the standard elements of a grillage model along with the respective str arguments. Users

 ===================================   ===========================================================================
   1                                    edge_beam
   2                                    exterior_main_beam_1
   3                                    interior_main_beam
   4                                    exterior_main_beam_1
   5                                    edge_slab
   6                                    transverse_slab
 ===================================   ===========================================================================

For orthogonal meshes, nodes in the transverse direction have varied spacing based on the skew edge region.
The properties of transverse members based on unit metre width is required for its definition section properties.
The module automatically implement the unit width properties based on the spacing of nodes in the skew edge regions.

The module checks if all element groups in the grillages are defined by the user. If missing element groups are detected,
a warning message is printed on the terminal.



Setting grillage member to element group in model
-------------------------------------------------
The members of the grillage model is set using the `set_member()` function of ``opGrillage`` class. The function takes a `member` class
object, and a member string tag as arguments. The function the assigns the `member`
object to the element group in the grillage model.

An example showing the assignment of interior main beams:

.. code-block:: python
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="interior_main_beam")

The following is printed to the terminal

The main commands of ops_vis module can be found `here <https://openseespydoc.readthedocs.io/en/latest/src/ops_vis.html>`_

Opensees model space or executable py file
-----------------------------------------------------------
Once the object of grillage model is created, we can create the model in Opensees software space using the function:

.. code-block:: python

    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)

Here, the `create_ops` function takes a boolean as parameter which by default is `False`. If set to `True`, an executable py file will be generated instead of the model instance in Opensees space. The executable py file contains all relevent Opensees command from which when executed, creates the model instance in Opensees.
In this example, we do not want the executable py file so we proceed with flagging False for the parameter.


Alternatively, users have the option to create an executable py file (output by OpsGrillage) which when executed,
creates the grillage model instance in Opensees software. This is done by flagging the input variable `pyfile=`
as True. In general, the executable py file contains all necessary commands to create the Opensees model instance.

Up to this point, the model in Opensees space and its corresponding executable py file only have the following
commands defined:

#. command to instantiate the model space in Opensees.
#. node() commands
#. Created the geometric transformation object of Opensees for the element definition later on.


Visualize grillage model
---------------------------------

To check the created the model in Opensees space, we can plot the model using the Opensees's visualization module. Before visualization, grillage members needs to be first defined.

.. code-block:: python

    opsplt.plot_model("nodes")
