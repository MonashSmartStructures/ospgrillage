========================================
Model types available
========================================

For all example code in this page, *ospgrillage* is imported as ``ospg``

.. code-block:: python
    import ospgrillage as ospg

Beam grillage
--------------------------------------
This is the most common form of grillage model which comprise of beam elements lay out in a grid pattern, with:

* longitudinal members representing composite section along longitudinal direction (e.g. main beams)
* transverse members representing slabs or secondary beam sections.

This is the default model type when we :func:`~ospgrillage.osp_grillage.OspGrillage.create_grillage`

.. code-block:: python

    example_bridge = ospg.create_grillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=-42,
                                    num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")


Information on beam grillage model can be found `here<https://www.steelconstruction.info/Modelling_and_analysis_of_beam_bridges>`_.


Beam grillage with rigid links
--------------------------------------
This model is a modified version of beam grillage with the following features:

* Offsets (in x-z plane) for start and end nodes along direction of transverse members - using joint offset.
* Offsets (in vertical y direction) for start and end nodes of longitudinal members - again using joint offsets.

To create this model, have :func:`~ospgrillage.osp_grillage.OspGrillage.create_grillage` keyword for ``model_type`` set to **beam_link**.

.. code-block:: python

    example_bridge = ospg.create_grillage(bridge_name="beamlink_10m", long_dim=10, width=7, skew=-12,
                                        num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho",
                                        model_type="beam_link",
                                        beam_width=1, web_thick=0.02, centroid_dist_y=0.499)

Figure 2 shows the details of the aforementioned model type. Figure 3 shows the model type created in an external
software - i.e. SPACEGASS.

..  figure:: ../../_images/beam_link_idealization.PNG
    :align: center
    :scale: 75 %

    Figure 2: Beam grillage with rigid links - idealization.

..  figure:: ../../_images/spacegass.PNG
    :align: center
    :scale: 75 %

    Figure 3: Beam grillage with rigid links model from SPACEGASS software.

Joint offsets are linked via a rigid link. Information for joint offsets can be found in `OpenSeesPy`'s `geomtransf <https://openseespydoc.readthedocs.io/en/latest/src/LinearTransf.html>`_


.. note::
    As of release 0.1.0, `OpenSeesPy` visualization module ops_vis is unable to visualize the joint offsets.

.. _shell hybrid model:

Shell and beam hybrid model
--------------------------------------
This is a more refined model using two element types - shell and beam elements - with the following features:

* Shell elements lay in grids to represent bridge decks.
* Beam elements modelled with an offset to the plane of shell elements to represent longitudinal beam sections.
* Beam elements linked to shell elements at two corresponding locations using constraint equations - `OpenSeesPy`'s **rigidLink** command

Figure 4 shows the details of the shell beam hybrid model.

..  figure:: ../../_images/shell_link_idealization.PNG
    :align: center
    :scale: 75 %

    Figure 4: Shell beam hybrid model idealization


This model has advantageous in modelling slabs using shell elements which are well-suited to represent two-dimensional slab behaviour.

To create this model, have :func:`~ospgrillage.osp_grillage.OspGrillage.create_grillage` keyword for ``model_type`` set to **shell**.

.. code-block:: python

    example_bridge = ospg.create_grillage(bridge_name="shelllink_10m", long_dim=10, width=7, skew=0,
                                        num_long_grid=6, num_trans_grid=11, edge_beam_dist=1, mesh_type="Orth",
                                        model_type="shell", max_mesh_size_z=0.5, offset_beam_y_dist=0.499,
                                        link_nodes_width=0.89)






