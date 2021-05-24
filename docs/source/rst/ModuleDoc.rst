#####################
Module documentation
#####################

This documentation describes the automated procedures of the opsy-grillage module. In providing the outline procedure,
the developers welcome any improvements to its procedures via pull requests.

====================
Grillage model
====================

A typical two-dimensional (2D) grillage model of a bridge in Opensees is shown in Figure 1.

..  figure:: ../images/Figure_1.png
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.

Model space
---------------------
The Opensees model space is can be set to either 2-D or 3-D.

The :class:`~OpsGrillage` object is a 2-D model that exist in the 3-D model space. By default, each nodes of the model
has 6 degrees-of-freedom.

For the 3-D model space, the grillage model plane lies in the x-z plane of the coordinate system.
For a 2-D model space, the 2-D plane is the x-y plane.


Coordinate system
---------------------
For 3-D model space, the module uses the following convention for coordinate system:

* x direction defines the length of the bridge model.

* z direction defines the width of the bridge model.

* y direction is the vertical axis.


====================
Meshing Procedure
====================
In grillages, transverse members are often arranged orthogonally to longitudinal members. When skew angles are small
(less than 30 degrees angle), orthogonal mesh can be impractical and a skew (Oblique) mesh is usually selected instead.

The :class:`~OpsGrillage` class has a :class:`~Mesh` class object as a variable. The :class:`~Mesh` object controls
the definition of:

* Nodes
* Element
* Element local transformation of sections and materials
* Grouping of grillage elements for calculating properties and assigning members.

Meshing algorithm
---------------------
Meshing requires four components defined based on the input information of the bridge. These components
(given names in bracket) include:

#. Construction line at edge of model @ the start of the span (Start span edge)
#. Construction line at edge of model @ the end of the span (End span edge)
#. A reference nodes
* Region with uniform grid spacing

..  figure:: ../images/Moduledoc_1.PNG
    :align: center
    :scale: 75 %

    Figure 1: Typical grillage model nodes.


Meshing Rules
---------------------
Meshing is based on two line meshes in orthogonal direction: (1) an x direction line mesh (typically
longitudinal direction), and (2) a z-direction line mesh (transversely in the direction parallel to skew angle).


.. note::
    Up to version 0.0.1, the grillage wizard allow users to freely choose between orthogonal and oblique meshes for
    angles between 10 to 30 degrees. An error exception will be returned when users select "orthogonal mesh"
    but having skew angle less than "10 degrees" - and vice versa.

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