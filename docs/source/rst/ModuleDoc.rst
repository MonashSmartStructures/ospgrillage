#####################
Module design
#####################

This page details the processes within *ops-grillage* module. In providing the outline of processes,
the developers welcome any improvements to its procedures via pull requests.

====================
Grillage model
====================

The *ops-grillage* module generates a two-dimensional (2D) grillage model of a bridge in Opensees - see Figure 1.

..  figure:: ../../_images/Figure_1.png
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.

Model space
---------------------
The Opensees model space can be set to either 2-D or 3-D.

By default the :class:`~OpsGrillage` object creates a 2-D grillage model that exist in the 3-D model space.
The model has 6 degrees-of-freedom at each nodes. The grillage model plane lies in the x-z plane of the coordinate system.
For a 2-D model space, the model plane is the x-y plane.


Coordinate system
---------------------

The module adopts the following coordinate convention for grillage model:

* x direction defines the length of the bridge model - typically the span of the model.

* z direction defines the width of the bridge model - the slabs elements are layed in this axis direction.

* y direction is the vertical axis - typically the direction of loads

Two reasons behind selecting the coordinate system are as such:
#. This coordinate system is consistent with geometric transformation (from local to global) in Opensees. The geometric transformation is used in Section definition, with local X being the axial direction
of beam/truss members; y and z axes being the vertical and horizontal axis of the local coordinate system respectively.
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

..  figure:: ../../_images/Moduledoc_1.PNG
    :align: center
    :scale: 75 %

    Figure 2: Meshing construction lines, showing start edge construction line (Blue), end edge construction line (Green), sweep path (Black) and sweeping nodes (Red).

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
Local vs global coordinate system
====================
In *ops-grillage*, local coordinate system refers to a basic coordinate system of components which is independent of the global coordinate system i.e. the coordinate system of the
grillage model space.

The definition of the following components within *ops-grillage* requires attention between basic and global coordinate system

* Load objects (Point, Line, Patch) - takes either local or global coordinate.
* Path objects (Path for moving load)
* Compound load object - takes either local or global coordinates.


For :class:`~LoadCase`, all load object inputs can be either local or global. Note when local coordinate is defined for a load object, a global reference coordinate needs to be defined or else
the module raises an Error regarding its point/vertices values.

..  figure:: ../../_images/coordinate_system_mapping.PNG
    :align: center
    :scale: 75 %

    Figure 3: Mapping of local coordinate of Load/Path objects to global coordinate.

====================
Links to module components
====================


#. :doc:`Module description`
#. :doc:`Examples`
#. :doc:`OpsGrillage`
#. :doc:`Running_analysis`


.. toctree::
   :maxdepth: 2
   :hidden:


====================
Links to useful resources
====================
Use the following links for more on:

* `Grillage modelling <http://bridgedesign.org.uk/tutorial/bs-grillage.php>`_

* `Openseespy documentation <https://openseespydoc.readthedocs.io/en/latest/>`_

====================
Further development
====================
The initial release of *ops-grillage* contains core algorithms to generate meshes of grillage models. However the
release comes with limitations and further development are required to extend beyond these limitations.

The current version of *ops-grillage* is limited to straight meshes. However, the developers coded the module in a way
where curve mesh is possible in future developments. Specifically, `SweepPath` class in meshing procedure can be introduced with
curved lines instead of straight (current version). This makes curve mesh possible with the sweep nodes been coded to be always orthogonal
to sweep path.

Current version of *ops-grillage* is limited to a single span mesh, where the support edges lies on the start and end
edge of the mesh. Multi-span mesh is possible with a few more developements. This is done by introducing intermediate
edge construction lines. This is done by developing the `EdgeConstructionLine` class. However,
this requires a bit more development as current edge construction lines are only recognized as end
supports - catering meshing procedures for one span.

The developers also acknowledges that there is minor conflict between the coordinate system of *ops-grillage* and the default
coordinate system for the `ops_vis` module of `Openseespy`. The `ops_vis` module default isotropic angle is x - y with z axis plane
being the model plane of a 2-D model in 3-D space. Currently the easiest solution is to further develop `ops_vis` to allow
multi isotropic views of the model space. If developers were to program *ops-grillage* to fit `ops_vis` current default axis,
it would require substantial rework of the entire module - since the module assume the model plane of the 2D grillage is the
y axis.

