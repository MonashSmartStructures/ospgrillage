#####################
Module design
#####################

This page details the design decisions of *ospgrillage* module. In outlining these processes,
the developers welcome any improvements to its procedures via pull requests. Also, any issues with each process can
be reported by raising an issue in the main repository.

====================
Grillage model
====================

The *ospgrillage* module generates a two-dimensional (2D) grillage model of a bridge deck in OpenSees - see Figure 1.

..  figure:: ../../_images/Figure_1.png
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.

Model space
---------------------

By default the :class:`~ospgrillage.osp_grillage.OpsGrillage` object creates a 2-D grillage model that exist in the 3-D model space.
The model has 6 degrees-of-freedom at each nodes. The grillage model plane lies in the x-z plane of the coordinate system.
For a 2-D model, the model plane is the x-y plane.

Development for 1-D models in 2-D space is yet to complete in release 0.1.0 but we welcome any pull request for it.

Coordinate system
---------------------

The module adopts the following coordinate system for grillage models:

* global x direction defines the length of the bridge model - typically the span of the model.

* global z direction defines the width of the bridge model - the slabs elements are layed in this axis direction.

* global y direction is the vertical axis - typically the direction of loads

Two reasons behind selecting the coordinate system:

#. To be consistent with geometric transformation (from local to global) of OpenSees. The geometric transformation is used in Section definition, with local X being the axial direction
   of beam/truss members; where y and z axes being the vertical and horizontal axis of the local coordinate system respectively.

#. To be consistent with 1D problems where the working axis for 1-D models is typically *x* (horizontal axis) and *y* (vertical axis).

====================
Meshing
====================

The :class:`~ospgrillage.osp_grillage.OspGrillage` class handles a :class:`~ospgrillage.mesh.Mesh` class object which stores information of the grillage mesh, such as:

* Nodes
* Elements
* Transformation of sections and materials
* Grouping of grillage elements for calculating properties and assigning members.
* Dimensions of mesh


Meshing algorithm
---------------------

Figure 2 shows an bridge mesh nodes as an explanatory example.

..  figure:: ../../_images/Moduledoc_1.PNG
    :align: center
    :scale: 75 %

    Figure 2: Meshing construction lines, showing start control line (Blue), end end control line (Green), sweep path (Black) and sweeping nodes (Red).

Meshing algorithm is controlled by the :class:`~ospgrillage.mesh.Mesh` class object. The following components are generated to
define the nodes and elements of the mesh:

#. **Line of control points at start of the span (start_span_edge)**
   A construction line consisting of the edge of the model is first defined. Construction line consist of nodes that
   coincide with the number and position of longitudinal beams in the model. The angle of the construction line is based on skew angle
   (skew_1). By default, the reference point of the construction line coincide with the origin [0,0,0] of the model space.

#. **Line of control points at the end of the span (end_span_edge)**
   Similar to (1), the construction line at the end of the span is created based on number of longitudinal beam. The
   spacing of the nodes in the z direction is identical to that of the first construction line. By default the skew angle
   of this second construction (skew_2) can be different. In contrast, the reference point of second construction line
   is [L, 0 ,f(L)] where L is the length of the model, and f(L) is the z coordinate of the reference node based on
   the defined sweep path of the model - this is next explained

#. **Sweep Path** By default, the sweep path of the model is a straight line of y = 0 which starts at the origin [0,0,0] of model space.
   Addition of options for sweep path is favourable.


Meshing Rules
---------------------
In grillages, transverse members are often arranged orthogonally to longitudinal members. When skew angles are small
(less than 30 degrees angle), orthogonal mesh can be impractical and a skew (Oblique) mesh is usually selected instead.

.. note::
    Up to version 0.1.0, the grillage wizard allow users to freely choose between orthogonal and oblique meshes for
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
coincide with edge beams are numbered 0 and 6, while nodes for exterior beams are 1 and 5. The interior beam consist
of the remaining groups (2,3,4) by this default.

Grid groups for elements in x direction is defined based on the number of times (or loops) through each intersection point
with the sweep path. In other words, the total number of groups for x grid varies depending on the (1) number of long beams
and (2) number of transverse beams.

All nodes defined during an iteration step for an intersecting point is set to have the same x grid group.

Mesh variables
---------------------
* Nodes information are stored as dictionaries

* Elements are specified by list. A typical element list is like this [2, 2, 3, 0, 2]
  The entries are the element tag, node_i, node_j, grouping (based on list), and geometric transformation tag.

Dictionaries are used to store information of mesh:

* Common element group as key: return z groups
* Z group as key, return longitudinal elements within the z group
* X group as key, return transverse elements within the x group
* node tag as key, return x spacings between vicinity nodes
* node tag as key, return the z spacings between vicinity nodes

====================
Local vs global coordinate system
====================
In *ospgrillage*, local coordinate system refers to a basic coordinate system of components which is independent of the global coordinate system i.e. the coordinate system of the
grillage model space.

The definition of the following components within *ops-grillage* requires attention between basic and global coordinate system

* Load objects (Point, Line, Patch) - takes either local or global coordinate.
* Path objects (Path for moving load)
* Compound load object - defined in local and set to global via :func:`~ospgrillage.load.CompoundLoad.set_global_coord`


For :class:`~ospgrillage.load.LoadCase`, all load object inputs can be either local or global. Note when local coordinate is defined for a load object, a global reference coordinate needs to be defined or else
the module raises an Error regarding its point/vertices values.

..  figure:: ../../_images/coordinate_system_mapping.PNG
    :align: center
    :scale: 75 %

    Figure 3: Mapping of local coordinate of Load/Path objects to global coordinate.

==========================
Links to module components
==========================


#. :doc:`Module description`
#. :doc:`Examples`
#. :doc:`OpsGrillage`
#. :doc:`Running_analysis`


.. toctree::
   :maxdepth: 2
   :hidden:


==========================
Links to useful resources
==========================
Use the following links for more on:

* `Grillage modelling <http://bridgedesign.org.uk/tutorial/bs-grillage.php>`_

* `OpenSeesPy documentation <https://openseespydoc.readthedocs.io/en/latest/>`_

* `Example bridge with skew edges <https://www.researchgate.net/publication/289736527_Effect_of_skew_angle_on_behavior_of_simply_supported_R_C_T-beam_bridge_decks>`_


References
---------------------

* Caprani, Colin & Melhem, Mayer & Siamphukdee, Kanjana. (2017). Reliability analysis of a Super-T prestressed concrete
  girder at serviceability limit state to AS 5100:2017. Australian Journal of Structural Engineering. 18. 1-13. 10.1080/13287982.2017.1332843.

====================
Further development
====================
*ospgrillage* is developed as a open-source package. In turn, the developers welcome contributors to add/improve on
the current release of *ospgrillage*.

**Update Sept 2021**

The initial release of *ospgrillage* contains core algorithms to generate meshes of grillage models. However the
release comes with limitations and further development are required to extend beyond these limitations.

The current version of *ospgrillage* is limited to straight meshes. However, the developers have coded the module in a way
where adding in curve meshing in future developments is just a matter of adding **curve line** functionality to
the :class:`~ospgrillage.load.SweepPath` class. Notably, the curve mesh is also possible with the current meshing rules
- i.e. the sweep nodes have been coded to be always orthogonal to the gradient of the sweep path (straight or curve).

Current version of *ospgrillage* is limited to a single span mesh, where the support edges lies on the start and end
edge of the mesh. Multi-span mesh is possible with a few more developments. This can be done by introducing intermediate
edge construction lines, a feature to be introduced to :class:`ospgrillage.mesh.Mesh`.
In tandem with this, the :class:`~ospgrillage.mesh.EdgeControlPoints` class will need to be reviewed as current edge control points
are only recognized as end supports - catering to current meshing procedures for single span configuration.

The developers also acknowledges that there are conflicts between the adopted coordinate system of *ospgrillage* and the default
coordinate system for the OpenSees's `ops_vis` module. The `ops_vis` module default isotropic angle is x - y with z axis plane
being the model plane of a 2-D model in 3-D space. Currently it is not easy to alter the coordinate system of
*ospgrillage*. However, the developers are hoping that `ops_vis` can cater to
multi isotropic views of the model space as oppose to the current fixed coordinate system.
It would require substantial rework of the entire *ospgrillage* module if one decides to "fit"
*ospgrillage* 's coordinate system to `ops_vis` - since the module assume the model plane of the 2D grillage is the
y axis.

