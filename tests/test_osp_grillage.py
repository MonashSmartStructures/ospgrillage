# -*- coding: utf-8 -*-

from fixtures import *

sys.path.insert(0, os.path.abspath("../"))

# Adopted units: N and m
kilo = 1e3
milli = 1e-3
N = 1
m = 1
mm = milli * m
m2 = m**2
m3 = m**3
m4 = m**4
kN = kilo * N
MPa = N / ((mm) ** 2)
GPa = kilo * MPa


# ---------------------------------------------------------------------------
# Section / parallel-axis-theorem tests
# ---------------------------------------------------------------------------
def test_section_parallel_axis_theorem():
    """Parallel axis theorem shifts Iz and Iy but not J."""
    s1 = og.create_section(A=1.0, Iz=2.0, Iy=0.5, J=0.3)
    assert s1.Iz == 2.0
    assert s1.Iy == 0.5
    assert s1.J == 0.3

    s2 = og.create_section(A=1.0, Iz=2.0, Iy=0.5, J=0.3, offset_y=3.0)
    assert s2.Iz == pytest.approx(2.0 + 1.0 * 9.0)  # 11.0
    assert s2.Iy == pytest.approx(0.5 + 1.0 * 9.0)  # 9.5
    assert s2.J == 0.3  # unchanged


def test_section_parallel_axis_default_iy():
    """When Iy is not given it defaults to 0.2*Iz, then gets the offset."""
    s = og.create_section(A=2.0, Iz=10.0, J=1.0, offset_y=1.5)
    iy_centroid = 0.2 * 10.0  # default
    d_sq = 1.5**2
    assert s.Iz == pytest.approx(10.0 + 2.0 * d_sq)
    assert s.Iy == pytest.approx(iy_centroid + 2.0 * d_sq)


def test_section_parallel_axis_edge_cases():
    """Edge cases: zero offset, negative offset, missing A."""
    # offset_y=0 should leave properties unchanged
    s0 = og.create_section(A=1.0, Iz=2.0, Iy=0.5, J=0.3, offset_y=0.0)
    assert s0.Iz == 2.0
    assert s0.Iy == 0.5

    # negative offset is squared, so same result as positive
    sn = og.create_section(A=1.0, Iz=2.0, Iy=0.5, J=0.3, offset_y=-3.0)
    sp = og.create_section(A=1.0, Iz=2.0, Iy=0.5, J=0.3, offset_y=3.0)
    assert sn.Iz == sp.Iz
    assert sn.Iy == sp.Iy

    # A is None: offset_y should be ignored (no area to shift)
    sa = og.create_section(Iz=2.0, J=0.3, offset_y=5.0)
    assert sa.Iz == 2.0


# ---------------------------------------------------------------------------
# beam_z_spacing deprecation test
# ---------------------------------------------------------------------------
def test_beam_z_spacing_deprecation_warning(ref_bridge_properties):
    """Using the old beam_z_spacing kwarg should emit a DeprecationWarning."""
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties
    with pytest.warns(DeprecationWarning, match="beam_z_spacing is deprecated"):
        og.create_grillage(
            bridge_name="dep_test",
            long_dim=10,
            width=7,
            skew=0,
            num_trans_grid=5,
            mesh_type="Ortho",
            beam_z_spacing=[1, 2, 1, 1, 2],
        )


# --------------------------------
# test creating a basic beam grillage model
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    # og.opsplt.plot_model("nodes") # uncomment to use vfo module
    # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
    # og.plt.show()
    assert og.ops.nodeCoord(18)  # check if model node exist in OpenSees model space
    # og.ops.wipe()
    a = example_bridge.get_element(member="exterior_main_beam_2", options="nodes")
    assert a


#  test creating beam model with rigid links
def test_create_beam_link_model(beam_link_bridge):
    beam_link_model = beam_link_bridge
    # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
    # og.plt.show()
    assert og.ops.eleNodes(100)


# test creating model using shell link
def test_create_shell_link_model(shell_link_bridge):
    shell_link_model = shell_link_bridge
    # og.opsplt.plot_model("nodes")
    assert og.ops.getNodeTags()


# test get_element() works for all member types on shell_beam model (issue #121)
def test_shell_link_get_element(shell_link_bridge):
    model = shell_link_bridge
    # longitudinal members — should return non-empty node lists
    for member in [
        "edge_beam",
        "exterior_main_beam_1",
        "interior_main_beam",
        "exterior_main_beam_2",
    ]:
        nodes = model.get_element(member=member, options="nodes")
        assert nodes, f"get_element(member={member!r}, options='nodes') returned empty"

    # edge members
    for member in ["start_edge", "end_edge"]:
        nodes = model.get_element(member=member, options="nodes")
        assert nodes, f"get_element(member={member!r}, options='nodes') returned empty"
        elems = model.get_element(member=member, options="elements")
        assert elems, f"get_element(member={member!r}, options='elements') returned empty"

    # transverse slab
    nodes = model.get_element(member="transverse_slab", options="nodes")
    assert nodes, "get_element(member='transverse_slab', options='nodes') returned empty"


# test creating default beam model without specifying edge beam distance
def test_uniform_spacing_no_edge_dist(bridge_model_42_negative_custom_spacing):
    example_bridge = bridge_model_42_negative_custom_spacing
    # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
    # og.plt.show()
    assert all(example_bridge.Mesh_obj.noz == [0.0, 1.0, 2.25, 3.5, 4.75, 6.0, 7.0])


def test_custom_beam_spacing_points(ref_bridge_properties):
    # this test checks if the grillage is correctly created when a customized grillage spacing is provided to
    # create_grillage function

    # create a grillage with
    custom_spacing = [1, 2, 1, 1, 2]  # first spacing starts at z = 0 direction

    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=12,
        num_trans_grid=5,
        mesh_type="Ortho",
        beam_spacing=custom_spacing,
    )

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)
    # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
    # og.plt.show()

    assert example_bridge.Mesh_obj.noz == [0, 1, 3, 4, 5, 7]


def test_custom_transverse_and_long_spacing(ref_bridge_properties):
    # create a grillage with
    custom_transver_spacing = [1, 2, 1, 1, 2]  # first spacing starts at z = 0 direction
    custom_spacing = [1, 2, 1, 1, 2]
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=20,
        mesh_type="Oblique",
        beam_x_spacing=custom_transver_spacing,
        beam_spacing=custom_spacing,
    )

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)
    # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
    # og.plt.show()

    assert example_bridge.Mesh_obj.nox == [0, 1, 3, 4, 5, 7]
    assert example_bridge.Mesh_obj.noz == [0, 1, 3, 4, 5, 7]


def test_inputs_custom_spacings_on_ortho_mesh(ref_bridge_properties):
    # test if ortho mesh is provided , name error is raised. Note to change this if feature for ortho + custom spacing
    # is developed.

    # create a grillage with
    with pytest.raises(Exception) as e_info:
        custom_transver_spacing = [
            1,
            2,
            1,
            1,
            2,
        ]  # first spacing starts at z = 0 direction
        custom_spacing = [1, 2, 1, 1, 2]
        # define material
        I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

        # construct grillage model
        example_bridge = og.create_grillage(
            bridge_name="SuperT_10m",
            long_dim=10,
            width=7,
            skew=20,
            mesh_type="Ortho",
            beam_x_spacing=custom_transver_spacing,
            beam_spacing=custom_spacing,
        )

        # set grillage member to element groups of grillage model
        example_bridge.set_member(I_beam, member="interior_main_beam")
        example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
        example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
        example_bridge.set_member(exterior_I_beam, member="edge_beam")
        example_bridge.set_member(slab, member="transverse_slab")
        example_bridge.set_member(exterior_I_beam, member="start_edge")
        example_bridge.set_member(exterior_I_beam, member="end_edge")

        example_bridge.create_osp_model(pyfile=False)
        # og.opsv.plot_model(az_el=(-90, 0), element_labels=0)
        # og.plt.show()


def test_multispan_feature(ref_bridge_properties):
    # test multispan feature
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 11.565 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 10  # degree
    mesh_type = "Oblique"

    # multispan specific vars
    spans = [9 * m, 12 * m, 9 * m]
    nl_multi = [3, 5, 10]
    stich_slab_x_spacing = 1 * m
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stich_slab = og.create_member(section=stitch_slab_section, material=concrete)

    variant_one_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=True,
        # non_cont_spacing_x=stich_slab_x_spacing,
    )

    # assign grillage member to element groups of grillage model
    variant_one_model.set_member(I_beam, member="interior_main_beam")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
    variant_one_model.set_member(exterior_I_beam, member="edge_beam")
    variant_one_model.set_member(slab, member="transverse_slab")
    variant_one_model.set_member(slab, member="start_edge")
    variant_one_model.set_member(slab, member="end_edge")
    # variant_one_model.set_member(stich_slab, member="stitch_elements")

    variant_one_model.create_osp_model(pyfile=False)
    # og.opsv.plot_model(element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
    # og.plt.show()
    assert all(
        og.np.isclose(
            variant_one_model.Mesh_obj.nox,
            [
                0.0,
                4.5,
                9.0,
                12.0,
                15.0,
                18.0,
                21.0,
                22.0,
                23.0,
                24.0,
                25.0,
                26.0,
                27.0,
                28.0,
                29.0,
                30.0,
            ],
        )
    )


def test_member_assignment_for_specific_span_feature(ref_bridge_properties):
    # model is based on tst_multispan_feature
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 11.565 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 10  # degree
    mesh_type = "Oblique"

    # multispan specific vars
    spans = [9 * m, 12 * m, 9 * m]
    nl_multi = [3, 5, 10]
    stich_slab_x_spacing = 1 * m
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stich_slab = og.create_member(section=stitch_slab_section, material=concrete)

    variant_one_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=True,
        # non_cont_spacing_x=stich_slab_x_spacing,
    )

    # assign grillage member to element groups of grillage model
    variant_one_model.set_member(I_beam, member="interior_main_beam")
    # variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
    # variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
    variant_one_model.set_member(exterior_I_beam, member="edge_beam")
    variant_one_model.set_member(slab, member="transverse_slab")
    variant_one_model.set_member(slab, member="start_edge")
    variant_one_model.set_member(slab, member="end_edge")
    # variant_one_model.set_member(stich_slab, member="stitch_elements")

    variant_one_model.set_member(I_beam, member="interior_main_beam", specific_span=0)
    variant_one_model.set_member(I_beam, member="exterior_main_beam_1", specific_span=0)
    variant_one_model.set_member(I_beam, member="exterior_main_beam_2", specific_span=0)

    variant_one_model.create_osp_model(pyfile=False)
    # og.opsv.plot_model(element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
    # og.plt.show()


def test_member_reassignment_feature(ref_bridge_properties):
    # test model is a multispan model based on test_multi_span_feature()
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 11.565 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 10  # degree
    mesh_type = "Oblique"

    # multispan specific vars
    spans = [9 * m, 12 * m, 9 * m]
    nl_multi = [3, 5, 10]
    stich_slab_x_spacing = 1 * m
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stich_slab = og.create_member(section=stitch_slab_section, material=concrete)

    variant_one_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=True,
        # non_cont_spacing_x=stich_slab_x_spacing,
    )

    # assign grillage member to element groups of grillage model
    variant_one_model.set_member(I_beam, member="interior_main_beam")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
    variant_one_model.set_member(exterior_I_beam, member="edge_beam")
    variant_one_model.set_member(slab, member="transverse_slab")
    variant_one_model.set_member(slab, member="start_edge")
    variant_one_model.set_member(slab, member="end_edge")
    # variant_one_model.set_member(stich_slab, member="stitch_elements")

    # reassign
    variant_one_model.set_member(exterior_I_beam, member="interior_main_beam")

    variant_one_model.create_osp_model(pyfile=False)
    # og.opsv.plot_model(element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
    # og.plt.show()
    import re

    def parse_elastic_beam_cmd(cmd_str):
        # Remove trailing newline
        cmd_str = cmd_str.strip()
        pattern = (
            r'ops\.element\(\s*"elasticBeamColumn"\s*,\s*(\d+)\s*,\s*\*\[(.*?)\]\s*,'
            r'\s*\*\[(.*?)\]\s*,\s*(\d+)\s*,\s*"[-]?mass"\s*,\s*([\deE.+-]+)\s*\)'
        )

        # Match the command pattern
        match = re.match(
            pattern,
            cmd_str,
        )
        assert match, f"Failed to parse command: {cmd_str}"

        elem_id = int(match.group(1))
        nodes = list(map(int, match.group(2).split(",")))
        section_vals = list(map(float, match.group(3).split(",")))
        transf_tag = int(match.group(4))
        mass = float(match.group(5))

        return elem_id, nodes, section_vals, transf_tag, mass

    # Expected values — edge transverse element now correctly gets
    # start_edge section properties (unit_width with edge_ele_width=0.5)
    # instead of being treated as transverse_slab.
    expected_elem_id = 2
    expected_nodes = [2, 3]
    expected_section_vals = [
        2.214e-02,
        3.480e10,
        1.450e10,
        1.300e-04,
        5.500e-05,
        1.210e-04,
    ]
    expected_transf_tag = 1
    expected_mass = 106272.0

    cmd = variant_one_model.element_command_list[2]
    elem_id, nodes, section_vals, transf_tag, mass = parse_elastic_beam_cmd(cmd)

    assert elem_id == expected_elem_id
    assert nodes == expected_nodes
    for actual, expected in zip(section_vals, expected_section_vals):
        assert abs(actual - expected) < 1e-9
    assert transf_tag == expected_transf_tag
    assert abs(mass - expected_mass) < 1e-6


def test_create_offset_support(ref_bridge_properties):
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model - here without specifying edge distance
    example_bridge = og.create_grillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=-42,
        num_long_grid=7,
        num_trans_grid=5,
        mesh_type="Ortho",
        support_rigid_dist_y=1,
    )

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)

    # og.opsplt.plot_model("nodes")


def test_multispan_feat_shell(ref_bridge_properties):
    # test multispan feature compatibility with shell model
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 11.565 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 20  # degree
    mesh_type = "Oblique"
    model_type = "shell_beam"
    # multispan specific vars
    spans = [9 * m, 12 * m, 9 * m]
    nl_multi = [20, 10, 20]
    stich_slab_x_spacing = 0.5 * m

    variant_one_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        model_type=model_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=False,
        non_cont_spacing_x=stich_slab_x_spacing,
        max_mesh_size_z=1,
        max_mesh_size_x=1,
        offset_beam_y_dist=0.499,
        beam_width=0.89,
    )

    # create material of slab shell
    slab_shell_mat = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
    )

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # create stitch slab connecting elements
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stitch_slab = og.create_member(section=stitch_slab_section, material=concrete)

    # set shell
    variant_one_model.set_shell_members(slab_shell)

    # assign grillage member to element groups of grillage model
    variant_one_model.set_member(I_beam, member="interior_main_beam")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_1")
    variant_one_model.set_member(I_beam, member="exterior_main_beam_2")
    variant_one_model.set_member(exterior_I_beam, member="edge_beam")
    # variant_one_model.set_member(stitch_slab, member="stitch_elements")

    variant_one_model.create_osp_model(pyfile=False)
    # og.opsplt.plot_model()
    # og.opsv.plot_model(element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
    # og.plt.show()
    assert all(
        og.np.isclose(
            variant_one_model.Mesh_obj.nox,
            [
                0.0,
                0.44736842,
                0.89473684,
                1.34210526,
                1.78947368,
                2.23684211,
                2.68421053,
                3.13157895,
                3.57894737,
                4.02631579,
                4.47368421,
                4.92105263,
                5.36842105,
                5.81578947,
                6.26315789,
                6.71052632,
                7.15789474,
                7.60526316,
                8.05263158,
                8.5,
                9.5,
                10.72222222,
                11.94444444,
                13.16666667,
                14.38888889,
                15.61111111,
                16.83333333,
                18.05555556,
                19.27777778,
                20.5,
                21.5,
                21.94736842,
                22.39473684,
                22.84210526,
                23.28947368,
                23.73684211,
                24.18421053,
                24.63157895,
                25.07894737,
                25.52631579,
                25.97368421,
                26.42105263,
                26.86842105,
                27.31578947,
                27.76315789,
                28.21052632,
                28.65789474,
                29.10526316,
                29.55263158,
                30.0,
            ],
        )
    )


def test_basic_curve_mesh(ref_bridge_properties):
    # checks basic functionality of curve mesh generation

    # standard model with oblique
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model - here without specifying edge distance
    example_bridge = og.create_grillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=0,
        num_long_grid=7,
        num_trans_grid=15,
        mesh_type="Ortho",
        mesh_radius=20,
    )

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)

    # og.opsv.plot_model(element_labels=0, az_el=(-90, 0))
    # og.plt.show()

    # checks sweep points are correct
    assert all(
        og.np.isclose(
            example_bridge.Mesh_obj.nox,
            [
                0.0,
                0.71428571,
                1.42857143,
                2.14285714,
                2.85714286,
                3.57142857,
                4.28571429,
                5.0,
                5.71428571,
                6.42857143,
                7.14285714,
                7.85714286,
                8.57142857,
                9.28571429,
                10.0,
            ],
        )
    )


def test_spring_support(ref_bridge_properties):
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=-42,
        num_long_grid=7,
        num_trans_grid=5,
        edge_beam_dist=0.5,
        mesh_type="Ortho",
    )

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    # spring support
    e_spring = 1e9
    # example_bridge.set_spring_support(rotational_spring_stiffness=e_spring,edge_num=0)
    example_bridge.set_spring_support(rotational_spring_stiffness=e_spring, edge_num=1)

    example_bridge.create_osp_model(pyfile=False)
    # og.opsplt.plot_model()

    # print(og.ops.nodeDisp(20))


def test_multispan_with_ortho_40deg_skew(ref_bridge_properties):
    # test multispan feature
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # parameters of bridge grillage
    L = 33.5 * m  # span
    w = 10 * m  # width
    n_l = 7  # number of longitudinal members
    n_t = 11  # number of transverse members
    edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
    bridge_name = "multi span showcase"
    angle = 40  # degree
    mesh_type = "Ortho"

    # multispan specific vars
    spans = [10.67 * m, 10.67 * m, 10.67 * m]
    nl_multi = [3, 3, 3]
    stich_slab_x_spacing = 1 * m
    stitch_slab_section = og.create_section(
        A=0.504 * m2,
        J=5.22303e-3 * m3,
        Iy=0.32928 * m4,
        Iz=1.3608e-3 * m4,
        Ay=0.42 * m2,
        Az=0.42 * m2,
    )
    stich_slab = og.create_member(section=stitch_slab_section, material=concrete)

    skew_multi_span_ortho_model = og.create_grillage(
        bridge_name=bridge_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
        mesh_type=mesh_type,
        multi_span_dist_list=spans,
        multi_span_num_points=nl_multi,
        continuous=True,
        # non_cont_spacing_x=stich_slab_x_spacing,
    )

    # assign grillage member to element groups of grillage model
    skew_multi_span_ortho_model.set_member(I_beam, member="interior_main_beam")
    skew_multi_span_ortho_model.set_member(I_beam, member="exterior_main_beam_1")
    skew_multi_span_ortho_model.set_member(I_beam, member="exterior_main_beam_2")
    skew_multi_span_ortho_model.set_member(exterior_I_beam, member="edge_beam")
    skew_multi_span_ortho_model.set_member(slab, member="transverse_slab")
    skew_multi_span_ortho_model.set_member(exterior_I_beam, member="start_edge")
    skew_multi_span_ortho_model.set_member(exterior_I_beam, member="end_edge")
    skew_multi_span_ortho_model.set_member(
        exterior_I_beam, member="end_edge", specific_group=2
    )
    skew_multi_span_ortho_model.set_member(
        exterior_I_beam, member="end_edge", specific_group=3
    )

    # variant_one_model.set_member(stich_slab, member="stitch_elements")

    skew_multi_span_ortho_model.create_osp_model(pyfile=False)
    # og.opsv.plot_model(node_labels=1, element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
    # og.plt.show()
    assert all(
        og.np.isclose(
            skew_multi_span_ortho_model.Mesh_obj.nox,
            [0.0, 5.335, 10.67, 16.005, 21.34, 26.675, 32.01],
        )
    )
