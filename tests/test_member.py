from fixtures import *

sys.path.insert(0, os.path.abspath("../"))


def test_section_command(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
    )

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="shelllink_10m",
        long_dim=10,
        width=7,
        skew=0,
        num_long_grid=6,
        num_trans_grid=11,
        edge_beam_dist=1,
        mesh_type="Orth",
        model_type="shell_beam",
        max_mesh_size_z=1,
        max_mesh_size_x=1,
        offset_beam_y_dist=0.499,
        beam_width=0.89,
    )

    # set beams
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(I_beam, member="exterior_main_beam_2")
    # set shell
    example_bridge.set_shell_members(slab_shell)

    example_bridge.create_osp_model(pyfile=False)
    assert example_bridge.section_command_list == [
        'ops.section("ElasticMembranePlateSection", 1, 34800000000.0, 0.2, 0.2, 2400.0)\n'
    ]


def test_create_section(ref_bridge_properties):
    # test creating sections and grillage members
    concrete = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa"
    )

    # define sections
    I_beam_section = og.create_section(
        A=0.896, J=0.133, Iy=0.213, Iz=0.259, Ay=0.233, Az=0.58
    )
    slab_section = og.create_section(
        A=0.04428,
        J=2.6e-4,
        Iy=1.1e-4,
        Iz=2.42e-4,
        Ay=3.69e-1,
        Az=3.69e-1,
        unit_width=True,
    )

    exterior_I_beam_section = og.create_section(
        A=0.044625, J=2.28e-3, Iy=2.23e-1, Iz=1.2e-3, Ay=3.72e-2, Az=3.72e-2
    )

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)

    # create member without material
    with pytest.raises(TypeError) as error_info:
        I_beam = og.create_member(
            member_name="Intermediate I-beams",
            section=I_beam_section,
        )

    # create member without section
    with pytest.raises(TypeError) as error_info:
        I_beam = og.create_member(
            member_name="Intermediate I-beams",
            material=concrete,
        )

    # create member with inputs to wrong kwarg - here we swap section and material inputs
    with pytest.raises(AttributeError) as error_info:
        I_beam = og.create_member(
            member_name="Intermediate I-beams",
            section=concrete,
            material=I_beam_section,
        )

    # create a shell GrillageMember
    slab_shell = og.create_member(
        member_name="concrete slab", section=slab_shell_section, material=concrete
    )
    exterior_I_beam = og.create_member(
        member_name="exterior I beams",
        section=exterior_I_beam_section,
        material=concrete,
    )
