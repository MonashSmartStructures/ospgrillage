========================
Grillage model templates
========================
*ospgrillage* offers several types of grillage models.


Beam grillage
--------------------------------------
The most common form of grillage model. This model comprise of beam elements layed out in a grid pattern with features:
* longitudinal members representing composite section along longitudinal direction (e.g. main beams)
* transverse members representing slabs or secondary beam sections.

Figure 1 shows a beam grillage model type - outlining the elements.

[picture]

Beam grillage with rigid links
--------------------------------------
This model is a modified beam grillage with the following features:

* Offset (in x-z plane) for start and end nodes of transverse members - by introducing joint offset.
* Offset (in vertical y direction) for start and end nodes of longitudinal members - again introducing joint offsets.

Joint offsets are linked via a rigid link. For more information on joint offsets see `geomtransf <https://openseespydoc.readthedocs.io/en/latest/src/LinearTransf.html>`_

Figure 2 shows the aforementioned model type.

[picture]


.. note::
    As of release 0.1.0, `OpenSeesPy` visualization module is unable to visualize the joint offsets.


Shell and beam hybrid model
--------------------------------------
A third model is a more refined model using two element types - shell and beam elements - with the following features:

* Shell elements are layed in a grid to represent bridge decks.
* Beam elements are modelled with an offset to the plane of shell elements to represent longitudinal beam sections.
* Beam elements are linked to shell elements at two correponding locations using constraint equations - `OpenSeesPy`'s **rigidLink** command

This model has advantageous in modelling slabs - shell elements are well-suited to represent two-dimensional slab behaviour.

Figure 3 shows the shell beam hybrid model.

[picture]




