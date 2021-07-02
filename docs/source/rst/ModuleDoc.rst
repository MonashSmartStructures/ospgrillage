#####################
Module documentation
#####################

This page details the processes within *ops-grillage* module. In providing the outline of processes,
the developers welcome any improvements to its procedures via pull requests.

====================
Grillage model
====================

The ops-grillage module generates a two-dimensional (2D) grillage model of a bridge in Opensees - see Figure 1.

..  figure:: ../images/Figure_1.png
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.

Model space
---------------------
The Opensees model space is can be set to either 2-D or 3-D.

By default the :class:`~OpsGrillage` object creates a 2-D grillage model that exist in the 3-D model space.
The model has 6 degrees-of-freedom at each nodes. The grillage model plane lies in the x-z plane of the coordinate system.
For a 2-D model space, the model plane is the x-y plane.


Coordinate system
---------------------

The module adopts the following convention for grillage model:

* x direction defines the length of the bridge model - typically the span of the model.

* z direction defines the width of the bridge model - the slabs elements are layed in this axis direction.

* y direction is the vertical axis - typically the direction of loads

Two reasons behind selecting the coordinate system as such:
#. This coordinate system streamlines section transformation (from local to global). The coordinate systems aligns well with the standard Opensees local coordinate systems for Section definition, with local X being the axial direction
of beam/truss members, while y and z axes being the horizontal and vertical axis of the local coordinate system respectively.
#. To be consistent with 1D problems where the working axis for 1-D models is typically *x* (horizontal axis) and *y* (vertical axis).

====================
Meshing Procedure
====================

The :class:`~OpsGrillage` class has a :class:`~Mesh` class object as a variable. The :class:`~Mesh` object controls
the definition of:

* Nodes
* Element
* Element local transformation of sections and materials
* Grouping of grillage elements for calculating properties and assigning members.


Meshing algorithm
---------------------
Lets use the following bridge mesh as an explanatory example. Herein, the variable names are given in brackets.

..  figure:: ../images/Moduledoc_1.PNG
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.

Meshing algorithm is initiated upon creating the :class:`~Mesh` class object. The following components are generated to
define the nodes and elements of the mesh:

#. Construction line at edge of model @ the start of the span (start_span_edge)
A construction line consisting of the edge of the model is first defined. Construction line consist of nodes that
coincide with the number and position of longitudinal beams in the model. The angle of the construction line is based on skew angle
(skew_1). By default, the reference point of the construction line coincide with the origin [0,0,0] of the model space.

#. Construction line at edge of model @ the end of the span (end_span_edge)
Similar to (1), the construction line at the end of the span is created based on number of longitudinal beam. The
spacing of the nodes in the z direction is identical to that of the first construction line. By default the skew angle
of this second construction (skew_2) can be different. In constrast, the reference point of second construction line
is [L, 0 ,f(L)] where L is the length of the model, and f(L) is the z coordinate of the reference node based on
the defined sweep path of the model - this is next explained

#. Sweep Path
By default, the sweep path of the model is a straight line of y = 0 which starts at the origin [0,0,0] of model space.
A few option

Meshing Rules
---------------------
In grillages, transverse members are often arranged orthogonally to longitudinal members. When skew angles are small
(less than 30 degrees angle), orthogonal mesh can be impractical and a skew (Oblique) mesh is usually selected instead.

.. note::
    Up to version 0.0.1, the grillage wizard allow users to freely choose between orthogonal and oblique meshes for
    angles between 11 to 30 degrees. An error exception will be returned when users select "orthogonal mesh"
    but having skew angle less than "11 degrees" - and vice versa. The numbers of 11 and 30 degrees are selected based
    on common industrial practice of grillage analysis.

Meshing steps
---------------------
#. Starting at first construction line, algorithm checks the angle of the construction line relative to the tangent/slope
of the sweep line at the first position (i.e. @ [0,0,0])

#. If mesh type for the given angle of construction line is permitted, a for loop procedure is initiated.
The iteration: (1) goes through every point in the construction line, (2) find the point on the sweep path whose normal vector
intersects the current point of the construction line, (3) create the nodes bounded between the current point and the intersection
point on the sweep line - see figure below. If mesh type is not valid, the process skips to step 3.

#. If angle is not permitted, the construction line is taken as the sweep node line. An iteration goes
through all points on construction line and assigns them as nodes. Then the process move to the step 4.

#. Similar to step 2, step 4 comprise the process of step 2 but conducted for the second construction line instead.

#. Remaining uniformly spaced nodes between the two construction lines are now defined. The algorithm spaces the nodes
evenly based on the number of transverse beam specified.

While nodes are generated, elements are also created by linking the generated nodes. Node linking is based on the grid numbering
allocated to each node. For example, A node with x grid = 1 and z grid = 1 forms a longitudinal beam element with node having
x grid = 2 and z_grid = 1.

During element generation, elements are characterized into Longitudinal, Transverse, and Edge elements.
Longitudinal elements are linked by recording the nodes with common z grid grouping across the sweep path.


Grid groups
---------------------
Grid groups for elements in the z direct is defined based on the number of longitudinal beams. For the example bridge,
there are 7 longitudinal beams (2 edge, 2 exterior and 3 interior beams). Therefore, starting from 0, the nodes that
conincide with edge beams are numbered 0 and 6, while nodes for exterior beams are 1 and 5. The interior beam consist
of the remaining groups (2,3,4) by this default.

Grid groups for elements in x direction is defined based on the number of times (or loops) through each intersection point
with the sweep path. In other words, the total number of groups for x grid varies depending on the (1) number of long beams
and (2) number of transverse beams.

All nodes defined during an iteration step for an intersecting point is set to have the same x grid group.

Mesh variables
---------------------
Nodes are specified into dictionary

Elements are specified by list. A typical element list is like this [2, 2, 3, 0, 2]
The entries are the element tag, node_i, node_j, grouping (based on list), and geometric transformation tag.

Groups are sorted into dictionary

Common element group as key: return z groups
Z group as key, return longitudinal elements within the z group
X group as key, return transverse elements within the x group
node tag as key, return x spacings between vicinity nodes
node tag as key, return the z spacings between vicinity nodes




====================
Links to module components
====================


#. :doc:`GrillageGenerator`
#. :doc:`Bridge model call`
#. :doc:`node_data_generation`
#. :doc:`OPMemberProp`
#. :doc:`op_create_elements`
#. :doc:`op_create_nodes`
#. :doc:`op_section_generate`
#. :doc:`op_fix`
#. :doc:`section_property_input`
#. :doc:`boundary_cond_input`
#. :doc:`compile_output`

.. toctree::
   :maxdepth: 2
   :hidden:



Grillage modelling references

:ref:`Grillage modelling<http://bridgedesign.org.uk/tutorial/bs-grillage.php>`

Opensees documentation

#. :doc:`node command`
#. :doc:`element command`
#. :doc:`GeoTrans command`
#. :doc:`section command`
#. :doc:`Material command`
#. :doc:`fix command`