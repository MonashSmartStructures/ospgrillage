import pytest
from OpsGrillage import *


# ------------------------------------------------------------------------------------------------------------------
# create reference bridge model
@pytest.fixture
def ref_28m_bridge():
    # reference super T bridge 28m for validation purpose
    # Members
    concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

    # define sections
    super_t_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=1.0447, E=3.47E+10,
                             G=2.00E+10,
                             J=0.230698, Iy=0.231329, Iz=0.533953,
                             Ay=0.397032, Az=0.434351)
    transverse_slab_section = Section(op_ele_type="elasticBeamColumn", A=0.5372, E=3.47E+10, G=2.00E+10,
                           J=2.79e-3, Iy=0.3988, Iz=1.45e-3,
                           Ay=0.447, Az=0.447, unit_width=True)
    end_tranverse_slab_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.5372/2,
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
    end_tranverse_slab = GrillageMember(member_name="exterior I beams", section=end_tranverse_slab_section, material=concrete)
    bridge_28 = OpsGrillage(bridge_name="SuperT_28m", long_dim=28, width=7, skew=0,
                                 num_long_grid=7, num_trans_grid=14, edge_beam_dist=1.0875, mesh_type="Ortho")
    pyfile = False
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



@pytest.fixture
def ref_bridge_properties():
    concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

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
    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)

    # set material to grillage
    example_bridge.set_material(concrete)

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    return example_bridge


@pytest.fixture
def bridge_model_42_positive(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=42,
                                 num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")
    pyfile = False
    example_bridge.create_ops(pyfile=pyfile)

    # set material to grillage
    example_bridge.set_material(concrete)

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    return example_bridge


# ------------------------------------------------------------------------------------------------------------------
# tests for mesh class object
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
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
    ref_answer = {7: [[3.1514141550424397, 0, 3.0], [3, 0, 3]],
                  8: [[3.1514141550424397, 0, 3.0], [4.276919210414739, 0, 3.0]],
                  11: [[4.276919210414739, 0, 3.0], [5.402424265787039, 0, 3.0]],
                  16: [[5.402424265787039, 0, 3.0], [6.302828310084879, 0, 3.0]],
                  22: [[6.302828310084879, 0, 3.0], [7.227121232563659, 0, 3.0]],
                  32: [[9.07570707752122, 0, 3.0], [10, 0, 3]],
                  56: [[7.227121232563659, 0, 3.0], [8.15141415504244, 0, 3.0]],
                  62: [[8.15141415504244, 0, 3.0], [9.07570707752122, 0, 3.0]]}
    assert example_bridge.global_line_int_dict[0] == ref_answer


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
    ref_ans = {1: [[2, 0, 0.0], [2, 0, 1.0]], 3: [[2, 0, 1.0], [2.0, 0, 2.2212250296583864]]}
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

    assert example_bridge.global_line_int_dict == [{6: [[4.276919210414739, 0, 1.0], [4, 0, 1]],
                                                    9: [[4.276919210414739, 0, 1.0], [5.402424265787039, 0, 1.0]],
                                                    14: [[5.402424265787039, 0, 1.0], [6.302828310084879, 0, 1.0]],
                                                    20: [[6.302828310084879, 0, 1.0], [7.227121232563659, 0, 1.0]],
                                                    30: [[9.07570707752122, 0, 1.0], [10, 0, 1]],
                                                    54: [[7.227121232563659, 0, 1.0], [8.15141415504244, 0, 1.0]],
                                                    60: [[8.15141415504244, 0, 1.0], [9.07570707752122, 0, 1.0]]}]


def test_line_load_coincide_edge_beam(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = LoadPoint(-1, 0, 0, 2)
    barrierpoint_2 = LoadPoint(10, 0, 0, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{0: [[0.9004040442978399, 0, 0.0], [-0.0, 0, -0.0]],
                                                    1: [[0.9004040442978399, 0, 0.0], [2.0259090996701397, 0, 0.0]],
                                                    2: [[2.0259090996701397, 0, 0.0], [3.1514141550424397, 0, 0.0]],
                                                    5: [[3.1514141550424397, 0, 0.0], [4.276919210414739, 0, 0.0]],
                                                    9: [[4.276919210414739, 0, 0.0], [5.402424265787039, 0, 0.0]],
                                                    14: [[5.402424265787039, 0, 0.0], [6.302828310084879, 0, 0.0]],
                                                    20: [[6.302828310084879, 0, 0.0], [7.227121232563659, 0, 0.0]],
                                                    27: [[9.07570707752122, 0, 0.0], [10, 0, 0]],
                                                    54: [[7.227121232563659, 0, 0.0], [8.15141415504244, 0, 0.0]],
                                                    60: [[8.15141415504244, 0, 0.0], [9.07570707752122, 0, 0.0]]}]


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
    assert example_bridge.global_load_str == ['ops.load(19, *[0, 1.40688131921541, 0, 0.703440659607711, 0, '
                                              '0.703440659607703])\n', 'ops.load(25, *[0, 1.40688131921534, 0, '
                                                                       '0.703440659607664, 0, '
                                                                       '-0.703440659607672])\n', 'ops.load(26, *[0, '
                                                                                                 '1.40688131921534, '
                                                                                                 '0, '
                                                                                                 '-0.703440659607664, '
                                                                                                 '0, '
                                                                                                 '-0.703440659607672'
                                                                                                 '])\n',
                                              'ops.load(20, *[0, 1.40688131921541, 0, -0.703440659607711, 0, '
                                              '0.703440659607703])\n', 'ops.load(25, *[0, 1.44420769137308, 0, '
                                                                       '0.722103845686535, 0, 0.722103845686539])\n',
                                              'ops.load(60, *[0, 1.44420769137311, 0, 0.722103845686558, 0, '
                                              '-0.722103845686555])\n', 'ops.load(61, *[0, 1.44420769137311, 0, '
                                                                        '-0.722103845686558, 0, '
                                                                        '-0.722103845686555])\n', 'ops.load(26, *[0, '
                                                                                                  '1.44420769137308, '
                                                                                                  '0, '
                                                                                                  '-0.722103845686535, 0, 0.722103845686539])\n',
                                              'ops.load(13, *[0, 0.0359716930904111, 0, 0.00543781415041399, 0, 0.00549241204442736])\n',
                                              'ops.load(18, *[0, 0.165240439803109, 0, 0.0589500683755123, 0, -0.0252300768696094])\n',
                                              'ops.load(19, *[0, 0.660961759212434, 0, -0.235800273502049, 0, -0.217366816107404])\n',
                                              'ops.load(14, *[0, 0.143886772361644, 0, -0.0217512566016560, 0, 0.0473192422289126])\n',
                                              'ops.load(18, *[0, 0.225101011074465, 0, 0.0720323235438296, 0, 0.0585262628793609])\n',
                                              'ops.load(24, *[0, 0.225101011074455, 0, 0.0720323235438248, 0, -0.0585262628793583])\n',
                                              'ops.load(25, *[0, 0.900404044297820, 0, -0.288129294175299, 0, -0.504226264806779])\n',
                                              'ops.load(19, *[0, 0.900404044297860, 0, -0.288129294175319, 0, 0.504226264806802])\n',
                                              'ops.load(24, *[0, 0.231073230619692, 0, 0.0739434337983012, 0, 0.0600790399611201])\n',
                                              'ops.load(59, *[0, 0.231073230619698, 0, 0.0739434337983036, 0, -0.0600790399611214])\n',
                                              'ops.load(60, *[0, 0.924292922478790, 0, -0.295773735193214, 0, -0.517604036588122])\n',
                                              'ops.load(25, *[0, 0.924292922478770, 0, -0.295773735193205, 0, 0.517604036588111])\n',
                                              'ops.load(59, *[0, 0.224872207710820, 0, 0.0768876019752062, 0, 0.0568977744108761])\n',
                                              'ops.load(66, *[0, 0.161567176007350, 0, 0.0467730008146084, 0, -0.0408801640107089])\n',
                                              'ops.load(67, *[0, 0.646268704029401, 0, -0.187092003258433, 0, -0.352198336092261])\n',
                                              'ops.load(60, *[0, 0.899488830843280, 0, -0.307550407900825, 0, 0.490196210309086])\n',
                                              'ops.load(60, *[0, 1.40545129819263, 0, 0.750855488039122, 0, 0.683867480899953])\n',
                                              'ops.load(67, *[0, 1.00979485004594, 0, 0.456767586080160, 0, -0.491348125128713])\n',
                                              'ops.load(68, *[0, 1.00979485004594, 0, -0.456767586080160, 0, -0.491348125128713])\n',
                                              'ops.load(61, *[0, 1.40545129819263, 0, -0.750855488039122, 0, 0.683867480899953])\n',
                                              'ops.load(61, *[0, 0.505962467349345, 0, 0.0973108712498703, 0, 0.265887676573902])\n',
                                              'ops.load(68, *[0, 0.363526146016538, 0, 0.0591970791559887, 0, -0.191036151050044])\n',
                                              'ops.load(69, *[0, 0.0403917940018376, 0, -0.00657745323955430, 0, -0.00550309900144157])\n',
                                              'ops.load(62, *[0, 0.0562180519277050, 0, -0.0108123190277634, 0, 0.00765931578607946])\n',
                                              'ops.load(20, *[0, 0.08992923272602966, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(15, *[0, 0.36279806628438915, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(21, *[0, 0.05030303322337952, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(20, *[0, 0.506477274917546, 0, 0.0911659094851593, 0, 0.273497728455475])\n',
                                              'ops.load(26, *[0, 0.506477274917524, 0, 0.0911659094851532, 0, -0.273497728455463])\n',
                                              'ops.load(27, *[0, 0.0562752527686137, 0, -0.0101295454983504, 0, -0.00787853538760591])\n',
                                              'ops.load(21, *[0, 0.0562752527686162, 0, -0.0101295454983510, 0, 0.00787853538760626])\n',
                                              'ops.load(26, *[0, 0.519914768894308, 0, 0.0935846584009749, 0, 0.280753975202926])\n',
                                              'ops.load(61, *[0, 0.519914768894319, 0, 0.0935846584009780, 0, -0.280753975202932])\n',
                                              'ops.load(62, *[0, 0.0577683076549244, 0, -0.0103982953778864, 0, -0.00808756307168940])\n',
                                              'ops.load(27, *[0, 0.0577683076549231, 0, -0.0103982953778861, 0, 0.00808756307168922])\n',
                                              'ops.load(14, *[0, 0.224823081815069, 0, 0.0531036538126367, 0, 0.0660145678416750])\n',
                                              'ops.load(19, *[0, 1.03275274876943, 0, 0.575684261479612, 0, -0.303246116221267])\n',
                                              'ops.load(20, *[0, 1.03275274876943, 0, -0.575684261479612, 0, -0.303246116221267])\n',
                                              'ops.load(15, *[0, 0.224823081815069, 0, -0.0531036538126367, 0, 0.0660145678416750])\n']


# ----------------------------------------------------------------------------------------------------------------------
# test sub functions
# ----------------------------------------------------------------------------------------------------------------------
# test if sort vertice function returns a clockwise
def test_sort_vertices():
    point_list = [LoadPoint(x=8, y=0, z=3, p=5), LoadPoint(x=8, y=0, z=5, p=5), LoadPoint(x=5, y=0, z=3, p=5),
                  LoadPoint(x=5, y=0, z=5, p=5)]
    assert sort_vertices(point_list) == [LoadPoint(x=5, y=0, z=3, p=5), LoadPoint(x=8, y=0, z=3, p=5),
                                         LoadPoint(x=8, y=0, z=5, p=5), LoadPoint(x=5, y=0, z=5, p=5)]


# ----------------------------------------------------------------------------------------------------------------------
# test Loadcase, compound load, and moving load objects
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


# test when compound load does not received a local_coord input parameter, if returned coordinates are correct
# given the load points of the load object itself are treated as the current local coordinates
def test_local_vs_global_coord_settings():
    location = LoadPoint(5, 0, -2, 20)  # create load point
    local_point = PointLoad(name="single point", localpoint1=location)  # defined for local coordinate
    global_point = PointLoad(name="single point", point1=location)  # defined for local coordinate

    M1600 = CompoundLoad("Lane and Barrier")
    M1600.add_load(load_obj=local_point)  # if local_coord is set, append the local coordinate of the point load
    # check
    assert M1600.compound_load_obj_list[0].load_point_1 == LoadPoint(x=5, y=0, z=-2, p=20)


def test_compound_load_distribution_to_nodes():
    pass


def test_moving_load_case(bridge_model_42_negative):
    ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = Path(start_point=Point(2, 0, 2), end_point=Point(4, 0, 3))  # create path object
    move_point = MovingLoad(name="single_moving_point")
    move_point.add_loads(load_obj=front_wheel, path_obj=single_path.get_path_points())
    move_point.parse_moving_load_cases()
    example_bridge.add_moving_load_case(move_point)

    example_bridge.analyse_moving_load_case()
    pass


def test_moving_compound_load():
    M1600 = CompoundLoad("Lane and Barrier")
    back_wheel = PointLoad(name="single point", point1=LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    M1600.add_load(load_obj=back_wheel, local_coord=Point(5, 0, 5))
    M1600.add_load(load_obj=front_wheel, local_coord=Point(3, 0, 5))
    M1600.set_global_coord(Point(4, 0, 3))

    move_point = MovingLoad(name="Truck 1")
    single_path = Path(start_point=Point(2, 0, 2), end_point=Point(4, 0, 3))  # Path object
    move_point.add_loads(load_obj=M1600, path_obj=single_path.get_path_points())
    pass


def test_add_a_loadcase_with_local_coordinate(bridge_model_42_negative):
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
    assert example_bridge.global_load_str == ['ops.load(19, *[0, 1.40688131921541, 0, 0.703440659607711, 0, '
                                              '0.703440659607703])\n', 'ops.load(25, *[0, 1.40688131921534, 0, '
                                                                       '0.703440659607664, 0, '
                                                                       '-0.703440659607672])\n', 'ops.load(26, *[0, '
                                                                                                 '1.40688131921534, '
                                                                                                 '0, '
                                                                                                 '-0.703440659607664, '
                                                                                                 '0, '
                                                                                                 '-0.703440659607672'
                                                                                                 '])\n',
                                              'ops.load(20, *[0, 1.40688131921541, 0, -0.703440659607711, 0, '
                                              '0.703440659607703])\n', 'ops.load(25, *[0, 1.44420769137308, 0, '
                                                                       '0.722103845686535, 0, 0.722103845686539])\n',
                                              'ops.load(60, *[0, 1.44420769137311, 0, 0.722103845686558, 0, '
                                              '-0.722103845686555])\n', 'ops.load(61, *[0, 1.44420769137311, 0, '
                                                                        '-0.722103845686558, 0, '
                                                                        '-0.722103845686555])\n', 'ops.load(26, *[0, '
                                                                                                  '1.44420769137308, '
                                                                                                  '0, '
                                                                                                  '-0.722103845686535, 0, 0.722103845686539])\n',
                                              'ops.load(13, *[0, 0.0359716930904111, 0, 0.00543781415041399, 0, 0.00549241204442736])\n',
                                              'ops.load(18, *[0, 0.165240439803109, 0, 0.0589500683755123, 0, -0.0252300768696094])\n',
                                              'ops.load(19, *[0, 0.660961759212434, 0, -0.235800273502049, 0, -0.217366816107404])\n',
                                              'ops.load(14, *[0, 0.143886772361644, 0, -0.0217512566016560, 0, 0.0473192422289126])\n',
                                              'ops.load(18, *[0, 0.225101011074465, 0, 0.0720323235438296, 0, 0.0585262628793609])\n',
                                              'ops.load(24, *[0, 0.225101011074455, 0, 0.0720323235438248, 0, -0.0585262628793583])\n',
                                              'ops.load(25, *[0, 0.900404044297820, 0, -0.288129294175299, 0, -0.504226264806779])\n',
                                              'ops.load(19, *[0, 0.900404044297860, 0, -0.288129294175319, 0, 0.504226264806802])\n',
                                              'ops.load(24, *[0, 0.231073230619692, 0, 0.0739434337983012, 0, 0.0600790399611201])\n',
                                              'ops.load(59, *[0, 0.231073230619698, 0, 0.0739434337983036, 0, -0.0600790399611214])\n',
                                              'ops.load(60, *[0, 0.924292922478790, 0, -0.295773735193214, 0, -0.517604036588122])\n',
                                              'ops.load(25, *[0, 0.924292922478770, 0, -0.295773735193205, 0, 0.517604036588111])\n',
                                              'ops.load(59, *[0, 0.224872207710820, 0, 0.0768876019752062, 0, 0.0568977744108761])\n',
                                              'ops.load(66, *[0, 0.161567176007350, 0, 0.0467730008146084, 0, -0.0408801640107089])\n',
                                              'ops.load(67, *[0, 0.646268704029401, 0, -0.187092003258433, 0, -0.352198336092261])\n',
                                              'ops.load(60, *[0, 0.899488830843280, 0, -0.307550407900825, 0, 0.490196210309086])\n',
                                              'ops.load(60, *[0, 1.40545129819263, 0, 0.750855488039122, 0, 0.683867480899953])\n',
                                              'ops.load(67, *[0, 1.00979485004594, 0, 0.456767586080160, 0, -0.491348125128713])\n',
                                              'ops.load(68, *[0, 1.00979485004594, 0, -0.456767586080160, 0, -0.491348125128713])\n',
                                              'ops.load(61, *[0, 1.40545129819263, 0, -0.750855488039122, 0, 0.683867480899953])\n',
                                              'ops.load(61, *[0, 0.505962467349345, 0, 0.0973108712498703, 0, 0.265887676573902])\n',
                                              'ops.load(68, *[0, 0.363526146016538, 0, 0.0591970791559887, 0, -0.191036151050044])\n',
                                              'ops.load(69, *[0, 0.0403917940018376, 0, -0.00657745323955430, 0, -0.00550309900144157])\n',
                                              'ops.load(62, *[0, 0.0562180519277050, 0, -0.0108123190277634, 0, 0.00765931578607946])\n',
                                              'ops.load(20, *[0, 0.08992923272602966, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(15, *[0, 0.36279806628438915, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(21, *[0, 0.05030303322337952, 0, 0.0, 0, 0.0])\n',
                                              'ops.load(20, *[0, 0.506477274917546, 0, 0.0911659094851593, 0, 0.273497728455475])\n',
                                              'ops.load(26, *[0, 0.506477274917524, 0, 0.0911659094851532, 0, -0.273497728455463])\n',
                                              'ops.load(27, *[0, 0.0562752527686137, 0, -0.0101295454983504, 0, -0.00787853538760591])\n',
                                              'ops.load(21, *[0, 0.0562752527686162, 0, -0.0101295454983510, 0, 0.00787853538760626])\n',
                                              'ops.load(26, *[0, 0.519914768894308, 0, 0.0935846584009749, 0, 0.280753975202926])\n',
                                              'ops.load(61, *[0, 0.519914768894319, 0, 0.0935846584009780, 0, -0.280753975202932])\n',
                                              'ops.load(62, *[0, 0.0577683076549244, 0, -0.0103982953778864, 0, -0.00808756307168940])\n',
                                              'ops.load(27, *[0, 0.0577683076549231, 0, -0.0103982953778861, 0, 0.00808756307168922])\n',
                                              'ops.load(14, *[0, 0.224823081815069, 0, 0.0531036538126367, 0, 0.0660145678416750])\n',
                                              'ops.load(19, *[0, 1.03275274876943, 0, 0.575684261479612, 0, -0.303246116221267])\n',
                                              'ops.load(20, *[0, 1.03275274876943, 0, -0.575684261479612, 0, -0.303246116221267])\n',
                                              'ops.load(15, *[0, 0.224823081815069, 0, -0.0531036538126367, 0, 0.0660145678416750])\n']


def test_load_combination():
    pass
