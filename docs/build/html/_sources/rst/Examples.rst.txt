========================
Examples
========================
Here are some more examples of what you can do with *ops-grillage* module.


28 m super T bridge model with orthogonal mesh
--------------------

.. code-block:: python

    pyfile = False
    # reference super T bridge 28m for validation purpose
    # Members
    concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

    # define sections
    super_t_beam_section = Section(A=1.0447, E=3.47E+10,
                                   G=2.00E+10,
                                   J=0.230698, Iy=0.231329, Iz=0.533953,
                                   Ay=0.397032, Az=0.434351)
    transverse_slab_section = Section(A=0.5372, E=3.47E+10, G=2.00E+10,
                                      J=2.79e-3, Iy=0.3988 / 2, Iz=1.45e-3 / 2,
                                      Ay=0.447 / 2, Az=0.447 / 2, unit_width=True)
    end_tranverse_slab_section = Section(A=0.5372 / 2,
                                         E=3.47E+10,
                                         G=2.00E+10, J=2.68e-3, Iy=0.04985,
                                         Iz=0.725e-3,
                                         Ay=0.223, Az=0.223)
    edge_beam_section = Section(A=0.039375,
                                E=3.47E+10,
                                G=2.00E+10, J=0.21e-3, Iy=0.1e-3,
                                Iz=0.166e-3,
                                Ay=0.0328, Az=0.0328)

    # define grillage members
    super_t_beam = GrillageMember(member_name="Intermediate I-beams", section=super_t_beam_section, material=concrete)
    transverse_slab = GrillageMember(member_name="concrete slab", section=transverse_slab_section, material=concrete)
    edge_beam = GrillageMember(member_name="exterior I beams", section=edge_beam_section, material=concrete)
    end_tranverse_slab = GrillageMember(member_name="edge transverse", section=end_tranverse_slab_section,
                                        material=concrete)

    bridge_28 = OpsGrillage(bridge_name="SuperT_28m", long_dim=28, width=7, skew=0,
                            num_long_grid=7, num_trans_grid=14, edge_beam_dist=1.0875, mesh_type="Ortho")

    bridge_28.create_ops(pyfile=pyfile)

    # set material to grillage
    bridge_28.set_material(concrete)

    # set grillage member to element groups of grillage model
    bridge_28.set_member(super_t_beam, member="interior_main_beam")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_1")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_2")
    bridge_28.set_member(edge_beam, member="edge_beam")
    bridge_28.set_member(transverse_slab, member="transverse_slab")
    bridge_28.set_member(end_tranverse_slab, member="start_edge")
    bridge_28.set_member(end_tranverse_slab, member="end_edge")


The following is printed to terminal

Skewed bridge model
-------------------


