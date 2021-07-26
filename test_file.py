import pytest
from OpsGrillage import *

# ------------------------------------------------------------------------------------------------------------------
# create reference bridge model
@pytest.fixture
def ref_28m_bridge():
    pyfile = False
    # reference super T bridge 28m for validation purpose
    # Members
    concrete = UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6, epsc0=-0.004, fpcu=-6, epsU=-0.014)

    # define sections
    super_t_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=1.0447, E=3.47E+10,
                                   G=2.00E+10,
                                   J=0.230698, Iy=0.231329, Iz=0.533953,
                                   Ay=0.397032, Az=0.434351)
    transverse_slab_section = Section(op_ele_type="elasticBeamColumn", A=0.5372, E=3.47E+10, G=2.00E+10,
                                      J=2.79e-3, Iy=0.3988 / 2, Iz=1.45e-3 / 2,
                                      Ay=0.447 / 2, Az=0.447 / 2, unit_width=True)
    end_tranverse_slab_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.5372 / 2,
                                         E=3.47E+10,
                                         G=2.00E+10, J=2.68e-3, Iy=0.04985,
                                         Iz=0.725e-3,
                                         Ay=0.223, Az=0.223)
    edge_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.039375,
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

    # set grillage member to element groups of grillage model
    bridge_28.set_member(super_t_beam, member="interior_main_beam")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_1")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_2")
    bridge_28.set_member(edge_beam, member="edge_beam")
    bridge_28.set_member(transverse_slab, member="transverse_slab")
    bridge_28.set_member(end_tranverse_slab, member="start_edge")
    bridge_28.set_member(end_tranverse_slab, member="end_edge")

    bridge_28.create_ops(pyfile=pyfile)

    return bridge_28


@pytest.fixture
def ref_bridge_properties():
    concrete = UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6, epsc0=-0.004, fpcu=-6, epsU=-0.014)

    # define sections
    I_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.896, E=3.47E+10,
                             G=2.00E+10,
                             J=0.133, Iy=0.213, Iz=0.259,
                             Ay=0.233, Az=0.58)
    slab_section = Section(op_ele_type="elasticBeamColumn", A=0.04428, E=3.47E+10, G=2.00E+10,
                           J=2.6e-4, Iy=1.1e-4, Iz=2.42e-4,
                           Ay=3.69e-1, Az=3.69e-1, unit_width=True)
    exterior_I_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.044625,
                                      E=3.47E+10,
                                      G=2.00E+10, J=2.28e-3, Iy=2.23e-1,
                                      Iz=1.2e-3,
                                      Ay=3.72e-2, Az=3.72e-2)

    # define grillage members
    I_beam = GrillageMember(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)
    slab = GrillageMember(member_name="concrete slab", section=slab_section, material=concrete)
    exterior_I_beam = GrillageMember(member_name="exterior I beams", section=exterior_I_beam_section, material=concrete)
    return I_beam, slab, exterior_I_beam, concrete


@pytest.fixture
def bridge_model_42_negative(ref_bridge_properties) -> OpsGrillage:
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=-42,
                                 num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)
    return example_bridge


@pytest.fixture
# A straight bridge with mesh where skew angle A is 42 and skew angle b is 0
def bridge_42_0_angle_mesh(ref_bridge_properties) -> OpsGrillage:
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties
    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42, 0],
                                 num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)

    return example_bridge


@pytest.fixture
def bridge_model_42_positive(ref_bridge_properties) -> OpsGrillage:
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=42,
                                 num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")
    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)
    return example_bridge


# ------------------------------------------------------------------------------------------------------------------
# tests for mesh class object
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    opsplt.plot_model("nodes")

    ops.nodeCoord(2)
    print("pass")
    ops.wipe()


# ------------------------------------------------------------------------------------------------------------------
# tests for load assignments
# tests point load return correct nodes
def test_point_load_getter(bridge_model_42_negative):  # test get_point_load_nodes() function
    # test if setter and getter is correct              # and assign_point_to_node() function

    example_bridge = bridge_model_42_negative
    # create reference point load
    location = LoadPoint(5, 0, 2, 20)
    Single = PointLoad(name="single point", point1=location)
    ULS_DL = LoadCase(name="Point")
    ULS_DL.add_load_groups(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    ops.wipe()

    assert example_bridge.load_case_list[0]['load_command'] == [
        'ops.load(12, *[0, 1.43019976273292, 0, 0.373895820491562, 0, '
        '0.341669431327021])\n', 'ops.load(17, *[0, 2.56980023726709, 0, '
                                 '0.906104179508438, 0, '
                                 '-0.613915767971677])\n', 'ops.load(18, *[0, '
                                                           '10.2792009490683, '
                                                           '0, '
                                                           '-3.62441671803375, '
                                                           '0, '
                                                           '-5.28912046252521'
                                                           '])\n',
        'ops.load(13, *[0, 5.72079905093166, 0, -1.49558328196625, 0, '
        '2.94361356220202])\n']


# test point load returning None when point (loadpoint) is outside of mesh
def test_point_load_outside_straight_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    location = LoadPoint(5, 0, -2, 20)
    Single = PointLoad(name="single point", point1=location)
    ULS_DL = LoadCase(name="Point")
    ULS_DL.add_load_groups(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    grid_nodes, _ = example_bridge.get_point_load_nodes(point=location)
    assert grid_nodes is None


# test general line with line load in the bounds of the mesh
def test_line_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(3, 0, 3, 2)
    barrierpoint_2 = LoadPoint(10, 0, 3, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)
    ref_answer = [{7: {'long_intersect': [], 'trans_intersect': [[3.1514141550424406, 0, 3.0]], 'edge_intersect': [], 'ends': [[3, 0, 3]]}, 8: {'long_intersect': [], 'trans_intersect': [[3.1514141550424406, 0, 3.0], [4.276919210414739, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 11: {'long_intersect': [], 'trans_intersect': [[4.276919210414739, 0, 3.0], [5.4024242657870385, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 16: {'long_intersect': [], 'trans_intersect': [[5.4024242657870385, 0, 3.0], [6.302828310084881, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 22: {'long_intersect': [], 'trans_intersect': [[6.302828310084881, 0, 3.0], [7.227121232563658, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 31: {'long_intersect': [], 'trans_intersect': [[10.0, 0, 3.0]], 'edge_intersect': [], 'ends': [[10, 0, 3]]}, 32: {'long_intersect': [], 'trans_intersect': [[10.0, 0, 3.0], [9.075707077521221, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 56: {'long_intersect': [], 'trans_intersect': [[7.227121232563658, 0, 3.0], [8.15141415504244, 0, 3.0]], 'edge_intersect': [], 'ends': []}, 62: {'long_intersect': [], 'trans_intersect': [[8.15141415504244, 0, 3.0], [9.075707077521221, 0, 3.0]], 'edge_intersect': [], 'ends': []}}]

    assert example_bridge.global_line_int_dict == ref_answer


# test line load function with line load is vertical (slope = infinite) and start end points
def test_line_load_vertical_and_cross_outside_mesh(bridge_model_42_negative):
    ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(2, 0, -3, 2)
    barrierpoint_2 = LoadPoint(2, 0, 8, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    ref_ans = {
        1: {'long_intersect': [[2, 0, 0.0], [2, 0, 1.0]], 'trans_intersect': [], 'edge_intersect': [], 'ends': []},
        3: {'long_intersect': [[2, 0, 1.0]], 'trans_intersect': [], 'edge_intersect': [[2.0, 0, 2.2212250296583864]],
            'ends': []}}
    assert example_bridge.global_line_int_dict[0] == ref_ans


# test a line load which coincide with edge z = 0 or z = 7
def test_line_load_coincide_long_edge(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(4, 0, 1, 2)
    barrierpoint_2 = LoadPoint(10, 0, 1, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{6: {'long_intersect': [],
                                                        'trans_intersect': [[4.276919210414739, 0, 1.0]],
                                                        'edge_intersect': [], 'ends': [[4, 0, 1]]},
                                                    9: {'long_intersect': [],
                                                        'trans_intersect': [[4.276919210414739, 0, 1.0],
                                                                            [5.402424265787039, 0, 1.0]],
                                                        'edge_intersect': [], 'ends': []}, 14: {'long_intersect': [],
                                                                                                'trans_intersect': [
                                                                                                    [5.402424265787039,
                                                                                                     0, 1.0],
                                                                                                    [6.302828310084879,
                                                                                                     0, 1.0]],
                                                                                                'edge_intersect': [],
                                                                                                'ends': []},
                                                    20: {'long_intersect': [],
                                                         'trans_intersect': [[6.302828310084879, 0, 1.0],
                                                                             [7.227121232563659, 0, 1.0]],
                                                         'edge_intersect': [], 'ends': []}, 30: {'long_intersect': [],
                                                                                                 'trans_intersect': [
                                                                                                     [9.07570707752122,
                                                                                                      0, 1.0]],
                                                                                                 'edge_intersect': [],
                                                                                                 'ends': [[10, 0, 1]]},
                                                    54: {'long_intersect': [],
                                                         'trans_intersect': [[7.227121232563659, 0, 1.0],
                                                                             [8.15141415504244, 0, 1.0]],
                                                         'edge_intersect': [], 'ends': []}, 60: {'long_intersect': [],
                                                                                                 'trans_intersect': [
                                                                                                     [8.15141415504244,
                                                                                                      0, 1.0],
                                                                                                     [9.07570707752122,
                                                                                                      0, 1.0]],
                                                                                                 'edge_intersect': [],
                                                                                                 'ends': []}}]


def test_line_load_coincide_transverse_member(bridge_42_0_angle_mesh):
    example_bridge = bridge_42_0_angle_mesh
    #opsplt.plot_model("nodes")

    # create reference line load
    barrierpoint_1 = LoadPoint(7.5, 0, 1, 2)
    barrierpoint_2 = LoadPoint(7.5, 0, 6, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(2, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(8, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(1, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(52, *[0, 1.25000000000000, 0, 0.625000000000000, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(32, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(53, *[0, 1.25000000000000, 0, -0.625000000000000, 0, 0])\n',
                                                                'ops.load(53, *[0, 1.25000000000000, 0, 0.625000000000000, 0, 0])\n',
                                                                'ops.load(32, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(33, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(54, *[0, 1.25000000000000, 0, -0.625000000000000, 0, 0])\n',
                                                                'ops.load(2, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(8, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(1, *[0, 0.0, 0, 0.0, 0, 0.0])\n',
                                                                'ops.load(51, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(30, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(52, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(51, *[0, 1.25000000000000, 0, 0.625000000000000, 0, 0])\n',
                                                                'ops.load(30, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(52, *[0, 1.25000000000000, 0, -0.625000000000000, 0, 0])\n',
                                                                'ops.load(54, *[0, 1.25000000000000, 0, 0.625000000000000, 0, 0])\n',
                                                                'ops.load(33, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(34, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(55, *[0, 1.25000000000000, 0, -0.625000000000000, 0, 0])\n']


def test_line_load_coincide_edge_beam(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(5, 0, 1, 2)
    barrierpoint_2 = LoadPoint(10, 0, 1, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{0: {'long_intersect': [],
                                                        'trans_intersect': [[0.9004040442978399, 0, 0.0]],
                                                        'edge_intersect': [[-0.0, 0, -0.0]], 'ends': []},
                                                    1: {'long_intersect': [],
                                                        'trans_intersect': [[0.9004040442978399, 0, 0.0],
                                                                            [2.0259090996701397, 0, 0.0]],
                                                        'edge_intersect': [], 'ends': []}, 2: {'long_intersect': [],
                                                                                               'trans_intersect': [
                                                                                                   [2.0259090996701397,
                                                                                                    0, 0.0],
                                                                                                   [3.1514141550424397,
                                                                                                    0, 0.0]],
                                                                                               'edge_intersect': [],
                                                                                               'ends': []},
                                                    5: {'long_intersect': [],
                                                        'trans_intersect': [[3.1514141550424397, 0, 0.0],
                                                                            [4.276919210414739, 0, 0.0]],
                                                        'edge_intersect': [], 'ends': []}, 9: {'long_intersect': [],
                                                                                               'trans_intersect': [
                                                                                                   [4.276919210414739,
                                                                                                    0, 0.0],
                                                                                                   [5.402424265787039,
                                                                                                    0, 0.0]],
                                                                                               'edge_intersect': [],
                                                                                               'ends': []},
                                                    14: {'long_intersect': [],
                                                         'trans_intersect': [[5.402424265787039, 0, 0.0],
                                                                             [6.302828310084879, 0, 0.0]],
                                                         'edge_intersect': [], 'ends': []}, 20: {'long_intersect': [],
                                                                                                 'trans_intersect': [
                                                                                                     [6.302828310084879,
                                                                                                      0, 0.0],
                                                                                                     [7.227121232563659,
                                                                                                      0, 0.0]],
                                                                                                 'edge_intersect': [],
                                                                                                 'ends': []},
                                                    27: {'long_intersect': [],
                                                         'trans_intersect': [[9.07570707752122, 0, 0.0]],
                                                         'edge_intersect': [], 'ends': [[10, 0, 0]]},
                                                    54: {'long_intersect': [],
                                                         'trans_intersect': [[7.227121232563659, 0, 0.0],
                                                                             [8.15141415504244, 0, 0.0]],
                                                         'edge_intersect': [], 'ends': []}, 60: {'long_intersect': [],
                                                                                                 'trans_intersect': [
                                                                                                     [8.15141415504244,
                                                                                                      0, 0.0],
                                                                                                     [9.07570707752122,
                                                                                                      0, 0.0]],
                                                                                                 'edge_intersect': [],
                                                                                                 'ends': []}}]


def test_line_load_outside_of_mesh(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(3, 0, -1, 2)
    barrierpoint_2 = LoadPoint(10, 0, -1, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    assert example_bridge.global_line_int_dict == [{}]


# test a default patch load - patch is within the mesh and sufficiently larger than a single grid
def test_patch_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = LoadPoint(5, 0, 3, 5)
    lane_point_2 = LoadPoint(8, 0, 3, 5)
    lane_point_3 = LoadPoint(8, 0, 5, 5)
    lane_point_4 = LoadPoint(5, 0, 5, 5)
    Lane = PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)
    ULS_DL = LoadCase(name="Lane")
    ULS_DL.add_load_groups(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)

    assert example_bridge.global_load_str == [
        'ops.load(19, *[0, 1.40688131921541, 0, 0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.40688131921534, 0, 0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(26, *[0, 1.40688131921534, 0, -0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(20, *[0, 1.40688131921541, 0, -0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.44420769137308, 0, 0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(60, *[0, 1.44420769137311, 0, 0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(61, *[0, 1.44420769137311, 0, -0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(26, *[0, 1.44420769137308, 0, -0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(13, *[0, 0.0359716930904111, 0, 0.00543781415041401, 0, 0.00549241204442737])\n',
        'ops.load(18, *[0, 0.165240439803109, 0, 0.0589500683755124, 0, -0.0252300768696094])\n',
        'ops.load(19, *[0, 0.660961759212436, 0, -0.235800273502050, 0, -0.217366816107404])\n',
        'ops.load(14, *[0, 0.143886772361645, 0, -0.0217512566016560, 0, 0.0473192422289127])\n',
        'ops.load(18, *[0, 0.225101011074466, 0, 0.0720323235438299, 0, 0.0585262628793611])\n',
        'ops.load(24, *[0, 0.225101011074456, 0, 0.0720323235438251, 0, -0.0585262628793586])\n',
        'ops.load(25, *[0, 0.900404044297824, 0, -0.288129294175300, 0, -0.504226264806781])\n',
        'ops.load(19, *[0, 0.900404044297864, 0, -0.288129294175320, 0, 0.504226264806804])\n',
        'ops.load(24, *[0, 0.231073230619692, 0, 0.0739434337983010, 0, 0.0600790399611199])\n',
        'ops.load(59, *[0, 0.231073230619697, 0, 0.0739434337983034, 0, -0.0600790399611212])\n',
        'ops.load(60, *[0, 0.924292922478787, 0, -0.295773735193214, 0, -0.517604036588121])\n',
        'ops.load(25, *[0, 0.924292922478767, 0, -0.295773735193204, 0, 0.517604036588110])\n',
        'ops.load(59, *[0, 0.224872207710820, 0, 0.0768876019752060, 0, 0.0568977744108760])\n',
        'ops.load(66, *[0, 0.161567176007350, 0, 0.0467730008146082, 0, -0.0408801640107088])\n',
        'ops.load(67, *[0, 0.646268704029400, 0, -0.187092003258433, 0, -0.352198336092261])\n',
        'ops.load(60, *[0, 0.899488830843278, 0, -0.307550407900824, 0, 0.490196210309085])\n',
        'ops.load(60, *[0, 1.40545129819262, 0, 0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(67, *[0, 1.00979485004594, 0, 0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(68, *[0, 1.00979485004594, 0, -0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(61, *[0, 1.40545129819262, 0, -0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(61, *[0, 0.505962467349344, 0, 0.0973108712498700, 0, 0.265887676573901])\n',
        'ops.load(68, *[0, 0.363526146016537, 0, 0.0591970791559885, 0, -0.191036151050043])\n',
        'ops.load(69, *[0, 0.0403917940018375, 0, -0.00657745323955428, 0, -0.00550309900144156])\n',
        'ops.load(62, *[0, 0.0562180519277049, 0, -0.0108123190277633, 0, 0.00765931578607944])\n',
        'ops.load(15, *[0, 0.08992923272603146, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.36279806628439637, 0, 0.0, 0, 0.0])\n',
        'ops.load(21, *[0, 0.05030303322338052, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.506477274917540, 0, 0.0911659094851582, 0, 0.273497728455472])\n',
        'ops.load(26, *[0, 0.506477274917518, 0, 0.0911659094851522, 0, -0.273497728455460])\n',
        'ops.load(27, *[0, 0.0562752527686131, 0, -0.0101295454983502, 0, -0.00787853538760582])\n',
        'ops.load(21, *[0, 0.0562752527686156, 0, -0.0101295454983509, 0, 0.00787853538760616])\n',
        'ops.load(26, *[0, 0.519914768894311, 0, 0.0935846584009754, 0, 0.280753975202928])\n',
        'ops.load(61, *[0, 0.519914768894322, 0, 0.0935846584009784, 0, -0.280753975202934])\n',
        'ops.load(62, *[0, 0.0577683076549246, 0, -0.0103982953778865, 0, -0.00808756307168943])\n',
        'ops.load(27, *[0, 0.0577683076549234, 0, -0.0103982953778861, 0, 0.00808756307168926])\n',
        'ops.load(14, *[0, 0.224823081815069, 0, 0.0531036538126366, 0, 0.0660145678416749])\n',
        'ops.load(19, *[0, 1.03275274876943, 0, 0.575684261479612, 0, -0.303246116221266])\n',
        'ops.load(20, *[0, 1.03275274876943, 0, -0.575684261479612, 0, -0.303246116221266])\n',
        'ops.load(15, *[0, 0.224823081815069, 0, -0.0531036538126366, 0, 0.0660145678416749])\n']


# ----------------------------------------------------------------------------------------------------------------------
# test sub functions
# ----------------------------------------------------------------------------------------------------------------------
# test if sort vertice function returns a clockwise
def test_sort_vertices():
    point_list = [LoadPoint(x=8, y=0, z=3, p=5), LoadPoint(x=8, y=0, z=5, p=5), LoadPoint(x=5, y=0, z=3, p=5),
                  LoadPoint(x=5, y=0, z=5, p=5)]
    ref_ans = [LoadPoint(x=5, y=0, z=3, p=5), LoadPoint(x=8, y=0, z=3, p=5),
                                         LoadPoint(x=8, y=0, z=5, p=5), LoadPoint(x=5, y=0, z=5, p=5)]
    actual,_ = sort_vertices(point_list)
    assert actual == ref_ans


# ----------------------------------------------------------------------------------------------------------------------
# tests for Loadcase, compound load, and moving load objects
# test to check if compound load gives correct coordinates for encompassed load objects
def test_compound_load_correct_position():
    location = LoadPoint(5, 0, -2, 20)  # create load point
    Single = PointLoad(name="single point", point1=location)
    # front_wheel = PointLoad(name="front wheel", localpoint1=LoadPoint(2, 0, 2, 50))
    # Line load
    barrierpoint_1 = LoadPoint(-1, 0, 0, 2)
    barrierpoint_2 = LoadPoint(11, 0, 0, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)

    M1600 = CompoundLoad("Lane and Barrier")
    M1600.add_load(load_obj=Single, local_coord=Point(5, 0, 5))
    M1600.add_load(load_obj=Barrier, local_coord=Point(3, 0, 5))  # this overwrites the current global pos of line load
    # the expected midpoint (reference point initial is 6,0,0) is now at 9,0,5 (6+3, 0+0, 5+0)
    # when setting the global coordinate, the global coordinate is added with respect to ref point (9,0,5)
    # therefore (3+4, 0+0, 3+5) = (13,0,8)
    M1600.set_global_coord(Point(4, 0, 3))
    assert M1600.compound_load_obj_list[1].load_point_2 == LoadPoint(x=13.0, y=0, z=8.0, p=2)  # test if last point
    # of line load obj within compounded load moves to correct position


# test for when compound load does not received a local_coord input parameter, checks if returned coordinates are
# correct given the load points of the load object itself are treated as the current local coordinates
def test_local_vs_global_coord_settings():
    location = LoadPoint(5, 0, -2, 20)  # create load point
    local_point = PointLoad(name="single point", localpoint1=location)  # defined for local coordinate
    global_point = PointLoad(name="single point", point1=location)  # defined for local coordinate

    M1600 = CompoundLoad("Lane and Barrier")
    M1600.add_load(load_obj=local_point)  # if local_coord is set, append the local coordinate of the point load
    # check
    assert M1600.compound_load_obj_list[0].load_point_1 == LoadPoint(x=5, y=0, z=-2, p=20)


# test if compound load distributes to nodes, pass if runs
def test_compound_load_distribution_to_nodes(bridge_model_42_negative):
    ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = CompoundLoad("M1600 LM")
    back_wheel = PointLoad(name="single point", point1=LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=back_wheel, local_coord=Point(6, 0, 5))
    M1600.add_load(load_obj=front_wheel, local_coord=Point(5, 0, 5))
    M1600.set_global_coord(Point(0, 0, 0))

    static_truck = LoadCase("static M1600")
    static_truck.add_load_groups(M1600)
    example_bridge.add_load_case(static_truck)
    example_bridge.analyze(all=True)
    ba, ma = example_bridge.get_results()
    pass


# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_case(bridge_model_42_negative):
    ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = Path(start_point=Point(2, 0, 2), end_point=Point(4, 0, 3))  # create path object
    move_point = MovingLoad(name="single_moving_point")
    move_point.add_loads(load_obj=front_wheel, path_obj=single_path.get_path_points())
    #move_point.parse_moving_load_cases()
    example_bridge.add_moving_load_case(move_point)

    example_bridge.analyze(all=True)
    ba, ma = example_bridge.get_results()


# test moving compound load, test pass if no errors are returned
def test_moving_compound_load(bridge_model_42_negative):
    ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = CompoundLoad("M1600 LM")
    back_wheel = PointLoad(name="single point", point1=LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=back_wheel, local_coord=Point(5, 0, 5))
    M1600.add_load(load_obj=front_wheel, local_coord=Point(3, 0, 5))
    M1600.set_global_coord(Point(0, 0, 0))

    truck = MovingLoad(name="Truck 1")
    single_path = Path(start_point=Point(2, 0, 2), end_point=Point(4, 0, 2))  # Path object
    truck.add_loads(load_obj=M1600, path_obj=single_path.get_path_points())
    #truck.parse_moving_load_cases()

    example_bridge.add_moving_load_case(truck)
    example_bridge.analyze(all=True)
    ba, ma = example_bridge.get_results()
    print("finish test compound moving load")


# test when users add a load type defined using local coordinates, and passed as inputs to loadcase without,
# setting a global_coordinate, a ValueError is raised.
def test_add_a_loadcase_with_local_coordinate(bridge_model_42_negative):
    with pytest.raises(ValueError):
        example_bridge = bridge_model_42_negative
        lane_point_1 = LoadPoint(5, 0, 3, 5)
        lane_point_2 = LoadPoint(8, 0, 3, 5)
        lane_point_3 = LoadPoint(8, 0, 5, 5)
        lane_point_4 = LoadPoint(5, 0, 5, 5)
        Lane = PatchLoading("Lane 1", localpoint1=lane_point_1, localpoint2=lane_point_2, localpoint3=lane_point_3,
                            localpoint4=lane_point_4)
        ULS_DL = LoadCase(name="Lane")
        ULS_DL.add_load_groups(Lane)  # ch
        example_bridge.add_load_case(ULS_DL)


# counter to previous test, this time the load obj (local coord) has an input parameter global coord
def test_add_load_case_with_local_coord_and_global_set_cord(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    lane_point_1 = LoadPoint(5, 0, 3, 5)
    lane_point_2 = LoadPoint(8, 0, 3, 5)
    lane_point_3 = LoadPoint(8, 0, 5, 5)
    lane_point_4 = LoadPoint(5, 0, 5, 5)
    Lane = PatchLoading("Lane 1", localpoint1=lane_point_1, localpoint2=lane_point_2, localpoint3=lane_point_3,
                        localpoint4=lane_point_4)
    ULS_DL = LoadCase(name="Lane")
    global_point = Point(0, 0, 0)
    ULS_DL.add_load_groups(Lane, global_coord_of_load_obj=global_point)  # HERE exist the global coord kwargs
    example_bridge.add_load_case(ULS_DL)


def test_patch_partially_outside_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    lane_point_1 = LoadPoint(-5, 0, 3, 5)
    lane_point_2 = LoadPoint(8, 0, 3, 5)
    lane_point_3 = LoadPoint(8, 0, 5, 5)
    lane_point_4 = LoadPoint(-5, 0, 5, 5)
    Lane = PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)
    ULS_DL = LoadCase(name="Lane")
    ULS_DL.add_load_groups(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)
    ba, ma = example_bridge.get_results()

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(14, *[0, 1.1724010993461413, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(10, *[0, 1.1724010993461444, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(15, *[0, 1.172401099346146, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(14, *[0, 1.75860164901919, 0, 0.879300824509587, 0, 0.879300824509594])\n',
                                                        'ops.load(19, *[0, 1.75860164901925, 0, 0.879300824509634, 0, -0.879300824509626])\n',
                                                        'ops.load(20, *[0, 1.75860164901925, 0, -0.879300824509634, 0, -0.879300824509626])\n',
                                                        'ops.load(15, *[0, 1.75860164901919, 0, -0.879300824509587, 0, 0.879300824509594])\n',
                                                        'ops.load(19, *[0, 1.40688131921541, 0, 0.703440659607712, 0, 0.703440659607704])\n',
                                                        'ops.load(25, *[0, 1.40688131921534, 0, 0.703440659607665, 0, -0.703440659607672])\n',
                                                        'ops.load(26, *[0, 1.40688131921534, 0, -0.703440659607665, 0, -0.703440659607672])\n',
                                                        'ops.load(20, *[0, 1.40688131921541, 0, -0.703440659607712, 0, 0.703440659607704])\n',
                                                        'ops.load(25, *[0, 1.44420769137308, 0, 0.722103845686536, 0, 0.722103845686540])\n',
                                                        'ops.load(60, *[0, 1.44420769137311, 0, 0.722103845686560, 0, -0.722103845686556])\n',
                                                        'ops.load(61, *[0, 1.44420769137311, 0, -0.722103845686560, 0, -0.722103845686556])\n',
                                                        'ops.load(26, *[0, 1.44420769137308, 0, -0.722103845686536, 0, 0.722103845686540])\n',
                                                        'ops.load(9, *[0, 0.07503367035815386, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(6, *[0, 0.07503367035815336, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(10, *[0, 0.412685186969845, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(9, *[0, 0.281376263843069, 0, 0.0900404044297814, 0, 0.0731578285991981])\n',
                                                        'ops.load(13, *[0, 0.281376263843079, 0, 0.0900404044297862, 0, -0.0731578285992007])\n',
                                                        'ops.load(14, *[0, 1.12550505537232, 0, -0.360161617719145, 0, -0.630282831008498])\n',
                                                        'ops.load(10, *[0, 1.12550505537228, 0, -0.360161617719126, 0, 0.630282831008475])\n',
                                                        'ops.load(13, *[0, 0.281376263843070, 0, 0.0900404044297817, 0, 0.0731578285991983])\n',
                                                        'ops.load(18, *[0, 0.281376263843080, 0, 0.0900404044297865, 0, -0.0731578285992009])\n',
                                                        'ops.load(19, *[0, 1.12550505537232, 0, -0.360161617719146, 0, -0.630282831008500])\n',
                                                        'ops.load(14, *[0, 1.12550505537228, 0, -0.360161617719127, 0, 0.630282831008477])\n',
                                                        'ops.load(18, *[0, 0.225101011074466, 0, 0.0720323235438299, 0, 0.0585262628793611])\n',
                                                        'ops.load(24, *[0, 0.225101011074456, 0, 0.0720323235438251, 0, -0.0585262628793586])\n',
                                                        'ops.load(25, *[0, 0.900404044297824, 0, -0.288129294175300, 0, -0.504226264806781])\n',
                                                        'ops.load(19, *[0, 0.900404044297864, 0, -0.288129294175320, 0, 0.504226264806804])\n',
                                                        'ops.load(24, *[0, 0.231073230619692, 0, 0.0739434337983010, 0, 0.0600790399611199])\n',
                                                        'ops.load(59, *[0, 0.231073230619697, 0, 0.0739434337983034, 0, -0.0600790399611212])\n',
                                                        'ops.load(60, *[0, 0.924292922478787, 0, -0.295773735193214, 0, -0.517604036588121])\n',
                                                        'ops.load(25, *[0, 0.924292922478767, 0, -0.295773735193204, 0, 0.517604036588110])\n',
                                                        'ops.load(59, *[0, 0.224872207710820, 0, 0.0768876019752060, 0, 0.0568977744108760])\n',
                                                        'ops.load(66, *[0, 0.161567176007350, 0, 0.0467730008146082, 0, -0.0408801640107088])\n',
                                                        'ops.load(67, *[0, 0.646268704029400, 0, -0.187092003258433, 0, -0.352198336092261])\n',
                                                        'ops.load(60, *[0, 0.899488830843278, 0, -0.307550407900824, 0, 0.490196210309085])\n',
                                                        'ops.load(60, *[0, 1.40545129819262, 0, 0.750855488039121, 0, 0.683867480899951])\n',
                                                        'ops.load(67, *[0, 1.00979485004594, 0, 0.456767586080159, 0, -0.491348125128712])\n',
                                                        'ops.load(68, *[0, 1.00979485004594, 0, -0.456767586080159, 0, -0.491348125128712])\n',
                                                        'ops.load(61, *[0, 1.40545129819262, 0, -0.750855488039121, 0, 0.683867480899951])\n',
                                                        'ops.load(61, *[0, 0.505962467349344, 0, 0.0973108712498700, 0, 0.265887676573901])\n',
                                                        'ops.load(68, *[0, 0.363526146016537, 0, 0.0591970791559885, 0, -0.191036151050043])\n',
                                                        'ops.load(69, *[0, 0.0403917940018375, 0, -0.00657745323955428, 0, -0.00550309900144156])\n',
                                                        'ops.load(62, *[0, 0.0562180519277049, 0, -0.0108123190277633, 0, 0.00765931578607944])\n',
                                                        'ops.load(20, *[0, 0.5697869342822274, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(15, *[0, 0.5697869342822279, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(21, *[0, 0.12661931872938303, 0, 0.0, 0, 0.0])\n',
                                                        'ops.load(20, *[0, 0.506477274917540, 0, 0.0911659094851582, 0, 0.273497728455472])\n',
                                                        'ops.load(26, *[0, 0.506477274917518, 0, 0.0911659094851522, 0, -0.273497728455460])\n',
                                                        'ops.load(27, *[0, 0.0562752527686131, 0, -0.0101295454983502, 0, -0.00787853538760582])\n',
                                                        'ops.load(21, *[0, 0.0562752527686156, 0, -0.0101295454983509, 0, 0.00787853538760616])\n',
                                                        'ops.load(26, *[0, 0.519914768894311, 0, 0.0935846584009754, 0, 0.280753975202928])\n',
                                                        'ops.load(61, *[0, 0.519914768894322, 0, 0.0935846584009784, 0, -0.280753975202934])\n',
                                                        'ops.load(62, *[0, 0.0577683076549246, 0, -0.0103982953778865, 0, -0.00808756307168943])\n',
                                                        'ops.load(27, *[0, 0.0577683076549234, 0, -0.0103982953778861, 0, 0.00808756307168926])\n']

# example super t 28 m  ref bridge
# test for comparing max deflection with a numerical comparison model in Lusas
def test_28m_bridge(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    opsplt.plot_model("nodes")
    ops.wipeAnalysis()
    lane_point_1 = LoadPoint(20.89, 0, 3, 5)
    lane_point_2 = LoadPoint(20.89, 0, 7, 5)
    line_load_middle = LineLoading("Ref mid_point_load", point1=lane_point_1, point2=lane_point_2)
    # 57 to 63
    point_load_case = LoadCase("point_load_case")
    line_load_case = LoadCase("line_load_case")
    line_load_case.add_load_groups(line_load_middle)
    ref_node_force = NodeForces(0, -1000, 0, 0, 0, 0)
    p1 = NodalLoad(name="point", node_tag=57, node_force=ref_node_force)
    p2 = NodalLoad(name="point", node_tag=58, node_force=ref_node_force)
    p3 = NodalLoad(name="point", node_tag=59, node_force=ref_node_force)
    p4 = NodalLoad(name="point", node_tag=60, node_force=ref_node_force)
    p5 = NodalLoad(name="point", node_tag=61, node_force=ref_node_force)
    p6 = NodalLoad(name="point", node_tag=62, node_force=ref_node_force)
    p7 = NodalLoad(name="point", node_tag=63, node_force=ref_node_force)
    point_load_case.add_load_groups(p1)
    point_load_case.add_load_groups(p2)
    point_load_case.add_load_groups(p3)
    point_load_case.add_load_groups(p4)
    point_load_case.add_load_groups(p5)
    point_load_case.add_load_groups(p6)
    point_load_case.add_load_groups(p7)

    bridge_28.add_load_case(point_load_case)
    # add a load combination
    bridge_28.add_load_combination(load_combination_name="factored_point",
                                   load_case_and_factor_dict={"point_load_case": 1.5})
    bridge_28.analyze(all=True)

    ba, ma = bridge_28.get_results(get_combinations=False)
    print(ops.nodeDisp(57))
    print(ops.nodeDisp(63))
    print(ops.nodeDisp(60))
    # opsv.plot_defo(unDefoFlag=0, endDispFlag=0)
    # plt.show()
    # opsv.section_force_distribution_3d()
    minY, maxY = opsv.section_force_diagram_3d('Vy', {}, 1)
    plt.show()
    pass

# test for 28 m ref bridge, using a moving load
def test_28m_bridge_moving_load(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    # create moving load case
    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = Path(start_point=Point(0, 0, 2), end_point=Point(29, 0, 3))  # create path object
    move_point = MovingLoad(name="single_moving_point")
    move_point.add_loads(load_obj=front_wheel, path_obj=single_path.get_path_points())
    #move_point.parse_moving_load_cases()
    bridge_28.add_moving_load_case(move_point)

    bridge_28.analyze(all=True)
    ba, ma = bridge_28.get_results()
    moving = ma[0]
    moving.sel(Node=63, Component='dy')
    print(ma)

# test for 28 m  bridge using a moving compound load
def test_28m_brdige_moving_compound_load(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    # create moving load case

    M1600 = CompoundLoad("M1600 LM")
    back_wheel = PointLoad(name="single point", point1=LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=front_wheel, local_coord=Point(5, 0, 5))
    M1600.add_load(load_obj=back_wheel, local_coord=Point(3, 0, 5))
    M1600.add_load(load_obj=back_wheel, local_coord=Point(3, 0, 3))
    M1600.add_load(load_obj=front_wheel, local_coord=Point(5, 0, 3))
    M1600.set_global_coord(Point(-6, 0, 0))

    truck = MovingLoad(name="4 wheel truck")
    single_path = Path(start_point=Point(0, 0, 0), end_point=Point(29, 0, 0))  # create path object
    truck.add_loads(load_obj=M1600, path_obj=single_path.get_path_points())
    #truck.parse_moving_load_cases() # process inputs to create incremental static load cases correspond to each position
    # of moving truck

    bridge_28.add_moving_load_case(truck)

    bridge_28.analyze(all=True)
    ba, ma = bridge_28.get_results()
    moving = ma[0]
    moving.sel(Node=63, Component='dy')
    maxY = moving.sel(Component='Vy').max(dim='Loadcase')
    minY = moving.sel(Component='Mz').max(dim='Loadcase')
    print(ma)


# Simple 2 x 3 Grid example
def test_simple_grid():
    L = 3
    w = 2
    n_l = 5  # when 2, edge_beam not needed; when 3, only one exterior_main_beam is needed, when 4...
    n_t = 3  # when 2, grid not complete and analysis fails

    simply_grid = OpsGrillage(bridge_name="Simple", long_dim=L, width=w, skew=0,
                              num_long_grid=n_l, num_trans_grid=n_t, edge_beam_dist=[0.3], mesh_type="Ortho")

    concrete = UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6.0, epsc0=-0.004, fpcu=-6.0, epsU=-0.014)
    # define sections
    super_t_beam_section = Section(A=1.0447, E=3.47E+10, G=2.00E+10,
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
    super_t_beam = GrillageMember(member_name="Intermediate beams", section=super_t_beam_section,
                                  material=concrete)
    transverse_slab = GrillageMember(member_name="concrete slab",
                                     section=transverse_slab_section, material=concrete)
    edge_beam = GrillageMember(member_name="exterior beams",
                               section=edge_beam_section, material=concrete)
    end_tranverse_slab = GrillageMember(member_name="edge transverse",
                                        section=end_tranverse_slab_section, material=concrete)

    # set grillage member to element groups of grillage model
    simply_grid.set_member(super_t_beam, member="interior_main_beam")
    simply_grid.set_member(super_t_beam, member="exterior_main_beam_1")
    simply_grid.set_member(super_t_beam, member="exterior_main_beam_2")
    # simply_grid.set_member(super_t_beam, member="edge_beam")
    simply_grid.set_member(edge_beam, member="edge_beam")
    simply_grid.set_member(transverse_slab, member="transverse_slab")
    simply_grid.set_member(end_tranverse_slab, member="start_edge")
    simply_grid.set_member(end_tranverse_slab, member="end_edge")

    pyfile = False
    simply_grid.create_ops(pyfile=pyfile)
    opsv.plot_model("nodes")
    plt.show()

    # loading
    # Line load (100 load at midspan)
    point_1 = LoadPoint(L/2, 0, 0, 1e3)
    point_2 = LoadPoint(L / 2, 0, w, 1e3)
    # test_load = opsg.LineLoading("Test Load", point1=point_1, point2=point_2)
    test_load = LineLoading("Test Load", point1=point_1, point2=point_2)  #

    # Load case creating and assign
    test_case = LoadCase(name="Test Case")
    test_case.add_load_groups(test_load)
    simply_grid.add_load_case(test_case)  # adding load case to grillage model
    simply_grid.add_load_combination("ULS",{test_case.name:2})
    print(simply_grid.load_case_list[0]['load_command'])
    simply_grid.analyze(all=True)
    minY, maxY = opsv.section_force_diagram_3d('Vy', {}, 1)
    plt.show()
    results = simply_grid.get_results(get_combinations=False)
    #results[0]
    print(results[0])
    print(maxY,minY)
    pass
