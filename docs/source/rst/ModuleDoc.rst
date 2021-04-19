#####################
Module documentation
#####################

This documentation describes the automated procedures of the opsy-grillage module. In providing the outline procedure,
the developers welcome any improvements to its procedures via pull requests.

====================
Grillage model
====================

A typical two-dimensional (2D) grillage model of a bridge in Opensees is shown in Figure 1.


Coordinate system
---------------------
The module follows the convention for coordinate system in Opensees:

* x direction is allocated to longitudinal members

* z direction is allocated to transverse members

* y direction is the vertical axis of the grillage



============================================
Default settings and rules of grillage model
============================================

Model space
---------------------
The following settings are defaulted for each ```GrillageGenerator``` class object:

* Opensees model space is 3-D with each model node having 6 degrees-of-freedom.

* The opensees model exist as a 2-D model in the 3-D model space, with model located at vertical y coordinate = 0.

meshing rules
---------------------
*

====================
Meshing Procedure
====================
In grillages, transverse members are often arranged orthogonally to longitudinal members. When skew angles are small
(less than 30 degrees angle), orthogonal mesh can be impractical and a skew (Oblique) mesh is usually selected instead.

.. note::
    Up to version 0.0.1, the grillage wizard allow users to freely choose between orthogonal and oblique meshes for
    angles between 10 to 30 degrees. An error exception will be returned when users select "orthogonal mesh"
    but having skew angle less than "10 degrees" - and vice versa.

Oblique mesh
---------------------
Meshing is based on two line meshes in orthogonal direction: (1) an x direction line mesh (typically
longitudinal direction), and (2) a z-direction line mesh (transversely in the direction parallel to skew angle).


Orthogonal mesh
---------------------
The meshing procedure for orthogonal mesh follows the similar procedure as the Oblique mesh. In addition,
Orthogonal meshing is carried out different for three regions of the grillage model:
* Region A -
* Region B1 -
* Region B2 -



====================
Module Commands
====================

The `GrillageGenerator` class is a collection of commands that: (1) evaluate information regarding the model, and (2)
translate and writes information into `Openseespy` commands.

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

   Bridge model call


Opensees references

#. :doc:`node command`
#. :doc:`element command`
#. :doc:`GeoTrans command`
#. :doc:`section command`
#. :doc:`Material command`
#. :doc:`fix command`