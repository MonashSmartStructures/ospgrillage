#####################
Module documentation
#####################

In OpenSees, each nodes and elements are defined in lines of code which can end up with a file with
thousands of lines for a very detailed model. The opsy-grillage wizard automates the py file that generates a given
grillage model in Opensees using python (Openseespy). The following section describes the automation procedure,
from which future improvements can be added upon it.

====================
Grillage model
====================

A typical two-dimensional (2D) grillage model of a bridge in Opensees is shown in Figure 1.


Coordinate system
---------------------
The grillage model comprise the following convention for coordinate system of Opensees:

* x direction is allocated to longtidinal members

* z direction is allocated to transverse members

* y direction is the vertical axis of the grillage

============================================
Default settings and rules of grillage model
============================================



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


Module commands

#. :doc:`constraints`
#. :doc:`numberer`
#. :doc:`system`
#. :doc:`test`
#. :doc:`algorithm`
#. :doc:`integrator`

Opensees references

#. :doc:`constraints`
#. :doc:`numberer`
#. :doc:`system`
#. :doc:`test`
#. :doc:`algorithm`
#. :doc:`integrator`