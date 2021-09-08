import pytest
import ospgrillage as og
import sys, os
sys.path.insert(0, os.path.abspath('../'))

"""
Alpha test module - to be deprecated from CI purposes
"""
# ------------------------------------------------------------------------------------------------------------------
# create reference bridge model




@pytest.fixture
def ref_28m_bridge():
    pyfile = False
    # reference super T bridge 28m for validation purpose
    # Members
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa")
    # concrete = og.Material(type="concrete", code="AS5100-2017", grade="50MPa")
    # define sections
    super_t_beam_section = og.create_section(A=1.0447,
                                      J=0.230698, Iy=0.231329, Iz=0.533953,
                                      Ay=0.397032, Az=0.434351)
    transverse_slab_section = og.create_section(A=0.5372,
                                         J=2.79e-3, Iy=0.3988 / 2, Iz=1.45e-3 / 2,
                                         Ay=0.447 / 2, Az=0.447 / 2, unit_width=True)
    end_tranverse_slab_section = og.create_section(A=0.5372 / 2,
                                            J=2.68e-3, Iy=0.04985,
                                            Iz=0.725e-3,
                                            Ay=0.223, Az=0.223)
    edge_beam_section = og.create_section(A=0.039375,
                                   J=0.21e-3, Iy=0.1e-3,
                                   Iz=0.166e-3,
                                   Ay=0.0328, Az=0.0328)

    # define grillage members
    super_t_beam = og.create_member(member_name="Intermediate I-beams", section=super_t_beam_section,
                                     material=concrete)
    transverse_slab = og.create_member(member_name="concrete slab", section=transverse_slab_section, material=concrete)
    edge_beam = og.create_member(member_name="exterior I beams", section=edge_beam_section, material=concrete)
    end_tranverse_slab = og.create_member(member_name="edge transverse", section=end_tranverse_slab_section,
                                           material=concrete)

    bridge_28 = og.OspGrillage(bridge_name="SuperT_28m", long_dim=28, width=7, skew=25,
                               num_long_grid=7, num_trans_grid=14, edge_beam_dist=1.0875, mesh_type="Orth")

    # set grillage member to element groups of grillage model
    bridge_28.set_member(super_t_beam, member="interior_main_beam")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_1")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_2")
    bridge_28.set_member(edge_beam, member="edge_beam")
    bridge_28.set_member(transverse_slab, member="transverse_slab")
    bridge_28.set_member(end_tranverse_slab, member="start_edge")
    bridge_28.set_member(end_tranverse_slab, member="end_edge")

    bridge_28.create_osp_model(pyfile=pyfile)

    return bridge_28


@pytest.fixture
def ref_bridge_properties():
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa")
    # define sections
    I_beam_section = og.create_section(A=0.896, J=0.133, Iy=0.213, Iz=0.259,
                                Ay=0.233, Az=0.58)
    slab_section = og.create_section(A=0.04428,
                              J=2.6e-4, Iy=1.1e-4, Iz=2.42e-4,
                              Ay=3.69e-1, Az=3.69e-1, unit_width=True)
    exterior_I_beam_section = og.create_section(A=0.044625,
                                         J=2.28e-3, Iy=2.23e-1,
                                         Iz=1.2e-3,
                                         Ay=3.72e-2, Az=3.72e-2)

    # define grillage members
    I_beam = og.create_member(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)
    slab = og.create_member(member_name="concrete slab", section=slab_section, material=concrete)
    exterior_I_beam = og.create_member(member_name="exterior I beams", section=exterior_I_beam_section,
                                        material=concrete)
    return I_beam, slab, exterior_I_beam, concrete


@pytest.fixture
def bridge_model_42_negative(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.OspGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=-42,
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
    example_bridge.create_osp_model(pyfile=pyfile)
    return example_bridge


@pytest.fixture
# A straight bridge with mesh where skew angle A is 42 and skew angle b is 0
def bridge_42_0_angle_mesh(ref_bridge_properties):
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties
    example_bridge = og.OspGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42, 0],
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
    example_bridge.create_osp_model(pyfile=pyfile)

    return example_bridge


@pytest.fixture
def bridge_model_42_positive(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.OspGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=42,
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
    example_bridge.create_osp_model(pyfile=pyfile)
    return example_bridge


# ------------------------------------------------------------------------------------------------------------------
# tests for mesh class object
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    og.opsplt.plot_model("nodes")

    print(og.ops.nodeCoord(18))
    print("pass")
    og.ops.wipe()


# ------------------------------------------------------------------------------------------------------------------
# tests for load assignments
# tests point load return correct nodes
def test_point_load_getter(bridge_model_42_negative):  # test get_point_load_nodes() function
    # test if setter and getter is correct              # and assign_point_to_node() function

    example_bridge = bridge_model_42_negative
    # create reference point load
    location = og.create_load_vertex(x=5, y=0, z=2, p=20)
    Single = og.create_load(type="point",name="single point", point1=location)
    ULS_DL = og.create_load_case(name="Point")
    ULS_DL.add_load_groups(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    og.ops.wipe()

    assert example_bridge.load_case_list[0]['load_command'] == [
        'ops.load(12, *[0, 0.607580708298788, 0, 0.373895820491562, 0, 0.341669431327021])\n',
        'ops.load(17, *[0, 1.47241929170121, 0, 0.906104179508438, 0, -0.613915767971677])\n',
        'ops.load(18, *[0, 12.6854585131181, 0, -3.62441671803375, 0, -5.28912046252521])\n',
        'ops.load(13, *[0, 5.23454148688186, 0, -1.49558328196625, 0, 2.94361356220202])\n']


# test point load returning None when point (loadpoint) is outside of mesh
def test_point_load_outside_straight_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)
    Single = og.create_load(type="point",name="single point", point1=location)
    ULS_DL = og.create_load_case(name="Point")
    ULS_DL.add_load_groups(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    grid_nodes, _ = example_bridge._get_point_load_nodes(point=location)
    assert grid_nodes is None


# test general line with line load in the bounds of the mesh
def test_line_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=3, y=0, z=3, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=3, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)
    example_bridge.get_results()
    ref_answer = [{7: {'long_intersect': [], 'trans_intersect': [[3.1514141550424406, 0, 3.0]], 'edge_intersect': [],
                       'ends': [[3, 0, 3]]}, 8: {'long_intersect': [], 'trans_intersect': [[3.1514141550424406, 0, 3.0],
                                                                                           [4.276919210414739, 0, 3.0]],
                                                 'edge_intersect': [], 'ends': []}, 11: {'long_intersect': [],
                                                                                         'trans_intersect': [
                                                                                             [4.276919210414739, 0,
                                                                                                3.0],
                                                                                             [5.4024242657870385, 0,
                                                                                              3.0]],
                                                                                         'edge_intersect': [],
                                                                                         'ends': []},
                   16: {'long_intersect': [],
                        'trans_intersect': [[5.4024242657870385, 0, 3.0], [6.302828310084881, 0, 3.0]],
                        'edge_intersect': [], 'ends': []}, 22: {'long_intersect': [],
                                                                'trans_intersect': [[6.302828310084881, 0, 3.0],
                                                                                    [7.227121232563658, 0, 3.0]],
                                                                'edge_intersect': [], 'ends': []},
                   31: {'long_intersect': [], 'trans_intersect': [[10.0, 0, 3.0]], 'edge_intersect': [],
                        'ends': [[10, 0, 3]]},
                   32: {'long_intersect': [], 'trans_intersect': [[10.0, 0, 3.0], [9.075707077521221, 0, 3.0]],
                        'edge_intersect': [], 'ends': []}, 56: {'long_intersect': [],
                                                                'trans_intersect': [[7.227121232563658, 0, 3.0],
                                                                                    [8.15141415504244, 0, 3.0]],
                                                                'edge_intersect': [], 'ends': []},
                   62: {'long_intersect': [],
                        'trans_intersect': [[8.15141415504244, 0, 3.0], [9.075707077521221, 0, 3.0]],
                        'edge_intersect': [], 'ends': []}}]

    assert example_bridge.global_line_int_dict == ref_answer


# test line load function with line load is vertical (slope = infinite) and start end points
def test_line_load_vertical_and_cross_outside_mesh(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=2, y=0, z=-3, p=2)
    barrierpoint_2 = og.create_load_vertex(x=2, y=0, z=8, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.create_load_case(name="Barrier")
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
    barrierpoint_1 = og.create_load_vertex(x=4, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{}]


def test_line_load_coincide_transverse_member(bridge_42_0_angle_mesh):
    example_bridge = bridge_42_0_angle_mesh
    # opsplt.plot_model("nodes")

    # create reference line load

    barrierpoint_1 = og.create_load_vertex(x=7.5, y=0, z=1, p=2)
    #barrierpoint_1 = og.create_load_vertices(x=7.5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=7.5, y=0, z=6, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(51, *[0, 2.00000000000000, 0, 0, 0, 0])\n',
                                                                'ops.load(30, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(52, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(51, *[0, 1.00000000000000, 0, 0.500000000000000, 0, 0])\n',
                                                                'ops.load(30, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(52, *[0, 1.00000000000000, 0, -0.500000000000000, 0, 0])\n',
                                                                'ops.load(52, *[0, 1.00000000000000, 0, 0.500000000000000, 0, 0])\n',
                                                                'ops.load(31, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(32, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(53, *[0, 1.00000000000000, 0, -0.500000000000000, 0, 0])\n',
                                                                'ops.load(53, *[0, 1.00000000000000, 0, 0.500000000000000, 0, 0])\n',
                                                                'ops.load(32, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(33, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(54, *[0, 1.00000000000000, 0, -0.500000000000000, 0, 0])\n',
                                                                'ops.load(54, *[0, 1.00000000000000, 0, 0.500000000000000, 0, 0])\n',
                                                                'ops.load(33, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(34, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(55, *[0, 1.00000000000000, 0, -0.500000000000000, 0, 0])\n',
                                                                'ops.load(55, *[0, 2.00000000000000, 0, 0, 0, 0])\n',
                                                                'ops.load(34, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(35, *[0, 0, 0, 0, 0, 0])\n',
                                                                'ops.load(56, *[0, 0, 0, 0, 0, 0])\n']


def test_line_load_coincide_edge_beam(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{}]


def test_line_load_outside_of_mesh(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=3, y=0, z=-1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=-1, p=2)
    Barrier = og.LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    ULS_DL = og.LoadCase(name="Barrier")
    ULS_DL.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    assert example_bridge.global_line_int_dict == [{}]


# test a default patch load - patch is within the mesh and sufficiently larger than a single grid
def test_patch_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
    Lane = og.PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)
    ULS_DL = og.LoadCase(name="Lane")
    ULS_DL.add_load_groups(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)

    assert example_bridge.global_load_str == [
        'ops.load(19, *[0, 1.40688131921542, 0, 0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.40688131921533, 0, 0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(26, *[0, 1.40688131921533, 0, -0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(20, *[0, 1.40688131921542, 0, -0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.44420769137307, 0, 0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(60, *[0, 1.44420769137312, 0, 0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(61, *[0, 1.44420769137312, 0, -0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(26, *[0, 1.44420769137307, 0, -0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(13, *[0, 0.00883644799442276, 0, 0.00543781415041401, 0, 0.00549241204442737])\n',
        'ops.load(18, *[0, 0.0957938611102078, 0, 0.0589500683755124, 0, -0.0252300768696094])\n',
        'ops.load(19, *[0, 0.825300957257174, 0, -0.235800273502050, 0, -0.217366816107404])\n',
        'ops.load(14, *[0, 0.0761293981057961, 0, -0.0217512566016560, 0, 0.0473192422289127])\n',
        'ops.load(18, *[0, 0.117052525758723, 0, 0.0720323235438296, 0, 0.0585262628793609])\n',
        'ops.load(24, *[0, 0.117052525758715, 0, 0.0720323235438248, 0, -0.0585262628793583])\n',
        'ops.load(25, *[0, 1.00845252961355, 0, -0.288129294175299, 0, -0.504226264806779])\n',
        'ops.load(19, *[0, 1.00845252961361, 0, -0.288129294175319, 0, 0.504226264806802])\n',
        'ops.load(24, *[0, 0.120158079922239, 0, 0.0739434337983010, 0, 0.0600790399611199])\n',
        'ops.load(59, *[0, 0.120158079922243, 0, 0.0739434337983034, 0, -0.0600790399611212])\n',
        'ops.load(60, *[0, 1.03520807317625, 0, -0.295773735193214, 0, -0.517604036588121])\n',
        'ops.load(25, *[0, 1.03520807317621, 0, -0.295773735193204, 0, 0.517604036588110])\n',
        'ops.load(59, *[0, 0.124942353209710, 0, 0.0768876019752063, 0, 0.0568977744108762])\n',
        'ops.load(66, *[0, 0.0760061263237388, 0, 0.0467730008146085, 0, -0.0408801640107090])\n',
        'ops.load(67, *[0, 0.654822011404518, 0, -0.187092003258434, 0, -0.352198336092262])\n',
        'ops.load(60, *[0, 1.07642642765289, 0, -0.307550407900825, 0, 0.490196210309087])\n',
        'ops.load(60, *[0, 1.50171097607824, 0, 0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(67, *[0, 0.913535172160317, 0, 0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(68, *[0, 0.913535172160317, 0, -0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(61, *[0, 1.50171097607824, 0, -0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(61, *[0, 0.583865227499220, 0, 0.0973108712498700, 0, 0.265887676573901])\n',
        'ops.load(68, *[0, 0.355182474935931, 0, 0.0591970791559885, 0, -0.191036151050043])\n',
        'ops.load(69, *[0, 0.0102315939281955, 0, -0.00657745323955428, 0, -0.00550309900144156])\n',
        'ops.load(62, *[0, 0.0168191629320763, 0, -0.0108123190277633, 0, 0.00765931578607944])\n',
        'ops.load(15, *[0, 0.08992923272602986, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.36279806628438993, 0, 0.0, 0, 0.0])\n',
        'ops.load(21, *[0, 0.05030303322337963, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.546995456910950, 0, 0.0911659094851582, 0, 0.273497728455472])\n',
        'ops.load(26, *[0, 0.546995456910913, 0, 0.0911659094851522, 0, -0.273497728455460])\n',
        'ops.load(27, *[0, 0.0157570707752115, 0, -0.0101295454983502, 0, -0.00787853538760582])\n',
        'ops.load(21, *[0, 0.0157570707752125, 0, -0.0101295454983509, 0, 0.00787853538760616])\n',
        'ops.load(26, *[0, 0.561507950405852, 0, 0.0935846584009754, 0, 0.280753975202928])\n',
        'ops.load(61, *[0, 0.561507950405871, 0, 0.0935846584009784, 0, -0.280753975202934])\n',
        'ops.load(62, *[0, 0.0161751261433790, 0, -0.0103982953778865, 0, -0.00808756307168943])\n',
        'ops.load(27, *[0, 0.0161751261433784, 0, -0.0103982953778861, 0, 0.00808756307168926])\n',
        'ops.load(14, *[0, 0.106207307625274, 0, 0.0531036538126368, 0, 0.0660145678416751])\n',
        'ops.load(19, *[0, 1.15136852295923, 0, 0.575684261479614, 0, -0.303246116221267])\n',
        'ops.load(20, *[0, 1.15136852295923, 0, -0.575684261479614, 0, -0.303246116221267])\n',
        'ops.load(15, *[0, 0.106207307625274, 0, -0.0531036538126368, 0, 0.0660145678416751])\n']


# test for patch load with linear shape function for load distribution
def test_patch_load_using_linear_shape_function(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
    Lane = og.PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3,
                           point4=lane_point_4, shape_function="linear")
    ULS_DL = og.LoadCase(name="Lane")
    ULS_DL.add_load_groups(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)
# ----------------------------------------------------------------------------------------------------------------------
# test sub functions
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------


# test for when compound load does not received a local_coord input parameter, checks if returned coordinates are
# correct given the load points of the load object itself are treated as the current local coordinates
def test_local_vs_global_coord_settings():
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)  # create load point
    local_point = og.create_load(type="point",name="single point", localpoint1=location)  # defined for local coordinate
    global_point = og.create_load(type="point",name="single point", point1=location)  # defined for local coordinate

    M1600 = og.CompoundLoad("Truck model")
    M1600.add_load(load_obj=local_point)  # if local_coord is set, append the local coordinate of the point load

    assert M1600.compound_load_obj_list[0].load_point_1 is None
    M1600.add_load(load_obj=global_point)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=5, y=0, z=-2, p=20)


# test if compound load distributes to nodes, pass if runs
def test_compound_load_distribution_to_nodes(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = og.CompoundLoad("M1600 LM")
    back_wheel = og.create_load(type="point", name="single point", point1=og.LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=back_wheel)
    M1600.add_load(load_obj=front_wheel)
    M1600.set_global_coord(og.Point(0, 0, 0))

    static_truck = og.create_load_case(name="static M1600")
    static_truck.add_load_groups(M1600)
    example_bridge.add_load_case(static_truck)
    example_bridge.analyze(all=True)
    results = example_bridge.get_results()
    pass


# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_case(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = og.create_moving_path(start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    example_bridge.analyze(all=True)
    results = example_bridge.get_results()
    print(results)


# test moving load + basic load case
# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_and_basic_load_together(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    # create reference line load
    p = 10000
    p2 = 20000
    p3 = 30000   # duplicate of 2nd but with different mag
    barrierpoint_1 = og.create_load_vertex(x=5,z=1, p=p)
    barrierpoint_2 = og.create_load_vertex(x=10,z=7, p=p)
    barrierpoint_3 = og.create_load_vertex(x=10, z=2, p=p2)
    barrierpoint_4 = og.create_load_vertex(x=5, z=5, p=p2)
    barrierpoint_5 = og.create_load_vertex(x=10,  z=2, p=p3)
    barrierpoint_6 = og.create_load_vertex(x=5, z=5, p=p3)
    # add moving load case
    front_wheel = og.PointLoad(name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)
    Barrier2 = og.create_load(type="line",name="Barrieload", point1=barrierpoint_3, point2=barrierpoint_4)
    Barrier3 = og.create_load(type="line",name="Barrieload", point1=barrierpoint_5, point2=barrierpoint_6)
    Patch1 = og.create_load(type="patch",point1 = barrierpoint_1,point2 = barrierpoint_3,point3=barrierpoint_2,point4=barrierpoint_4)

    barrierpoint_1 = og.create_load_vertex(x=6,z=2, p=0)
    barrierpoint_2 = og.create_load_vertex(x=11,z=8, p=0)
    barrierpoint_3 = og.create_load_vertex(x=11, z=3, p=0)
    barrierpoint_4 = og.create_load_vertex(x=6, z=6, p=0)

    Patch2 = og.create_load(type="patch",point1 = barrierpoint_1,point2 = barrierpoint_3,point3=barrierpoint_2,point4=barrierpoint_4)
    # create basic load case
    barrier_load_case = og.create_load_case(name="Barrier")
    #barrier_load_case.add_load_groups(Barrier)  # ch
    barrier_load_case.add_load_groups(Patch1)  # ch
    # 2nd
    barrier_load_case2 = og.create_load_case(name="Barrier2")
    #barrier_load_case2.add_load_groups(Barrier2)
    barrier_load_case2.add_load_groups(Patch2)
    # 3rd
    #barrier_load_case3 = og.create_load_case(name="Barrier3")
    #barrier_load_case3.add_load_groups(Barrier3)

    # adding load cases to model
    example_bridge.add_load_case(barrier_load_case)
    example_bridge.add_load_case(barrier_load_case2)
    #example_bridge.add_load_case(barrier_load_case3)

    single_path = og.create_moving_path(start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    #example_bridge.add_load_case(move_point)

    # example_bridge.analyze(all=True)
    example_bridge.analyze()
    og.opsv.plot_defo()
    og.plt.show()
    results = example_bridge.get_results(load_case="Barrier2")
    #maxY = results.sel(Component='dy').max()
    print(results)
    print(og.ops.nodeDisp(25)[1])


# test moving compound load, test pass if no errors are returned
def test_moving_compound_load(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = og.CompoundLoad("M1600 LM")
    back_wheel = og.create_load(type="point",name="single point", point1=og.LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=back_wheel)
    M1600.add_load(load_obj=front_wheel)
    M1600.set_global_coord(og.Point(0, 0, 0))

    truck = og.create_moving_load(name="Truck 1")
    single_path = og.create_moving_path(start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 2))  # Path object
    truck.set_path(path_obj=single_path)
    truck.add_loads(load_obj=M1600)

    example_bridge.add_load_case(truck)
    example_bridge.analyze(all=True)
    results = example_bridge.get_results()
    print("finish test compound moving load")


# test when users add a load type defined using local coordinates, and passed as inputs to loadcase without,
# setting a global_coordinate, a ValueError is raised.
# def test_add_a_loadcase_with_local_coordinate(bridge_model_42_negative):
#     with pytest.raises(ValueError):
#         example_bridge = bridge_model_42_negative
#         lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
#         lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
#         lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
#         lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
#         Lane = og.create_load(type="patch",name="Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3,
#                                point4=lane_point_4)
#         ULS_DL = og.create_load_case(name="Lane")
#         ULS_DL.add_load_groups(Lane)  # ch
#         example_bridge.add_load_case(ULS_DL)


# # counter to previous test, this time the load obj (local coord) has an input parameter global coord
# def test_add_load_case_with_local_coord_and_global_set_cord(bridge_model_42_negative):
#     example_bridge = bridge_model_42_negative
#     lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
#     lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
#     lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
#     lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
#     Lane = og.create_load(type="patch",name="Lane 1", localpoint1=lane_point_1, localpoint2=lane_point_2, localpoint3=lane_point_3,
#                            localpoint4=lane_point_4)
#     ULS_DL = og.create_load_case(name="Lane")
#     global_point = og.Point(0, 0, 0)
#     ULS_DL.add_load_groups(Lane, global_coord_of_load_obj=global_point)  # HERE exist the global coord kwargs
#     example_bridge.add_load_case(ULS_DL)
#     assert ULS_DL.load_groups


def test_patch_partially_outside_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    lane_point_1 = og.create_load_vertex(x=-5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=-5, y=0, z=5, p=5)
    Lane = og.create_load(type="patch",name="Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)
    ULS_DL = og.create_load_case(name="Lane")
    ULS_DL.add_load_groups(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze(all=True)
    results = example_bridge.get_results()

    assert example_bridge.load_case_list[0]['load_command'] == [
        'ops.load(10, *[0, 1.1724010993461413, 0, 0.0, 0, 0.0])\n',
        'ops.load(14, *[0, 1.1724010993461444, 0, 0.0, 0, 0.0])\n',
        'ops.load(15, *[0, 1.172401099346146, 0, 0.0, 0, 0.0])\n',
        'ops.load(14, *[0, 1.75860164901917, 0, 0.879300824509587, 0, 0.879300824509594])\n',
        'ops.load(19, *[0, 1.75860164901927, 0, 0.879300824509634, 0, -0.879300824509626])\n',
        'ops.load(20, *[0, 1.75860164901927, 0, -0.879300824509634, 0, -0.879300824509626])\n',
        'ops.load(15, *[0, 1.75860164901917, 0, -0.879300824509587, 0, 0.879300824509594])\n',
        'ops.load(19, *[0, 1.40688131921542, 0, 0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.40688131921533, 0, 0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(26, *[0, 1.40688131921533, 0, -0.703440659607665, 0, -0.703440659607672])\n',
        'ops.load(20, *[0, 1.40688131921542, 0, -0.703440659607712, 0, 0.703440659607704])\n',
        'ops.load(25, *[0, 1.44420769137307, 0, 0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(60, *[0, 1.44420769137312, 0, 0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(61, *[0, 1.44420769137312, 0, -0.722103845686560, 0, -0.722103845686556])\n',
        'ops.load(26, *[0, 1.44420769137307, 0, -0.722103845686536, 0, 0.722103845686540])\n',
        'ops.load(6, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n',
        'ops.load(9, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n',
        'ops.load(10, *[0, 0.41268518696984174, 0, 0.0, 0, 0.0])\n',
        'ops.load(9, *[0, 0.146315657198395, 0, 0.0900404044297815, 0, 0.0731578285991982])\n',
        'ops.load(13, *[0, 0.146315657198403, 0, 0.0900404044297863, 0, -0.0731578285992008])\n',
        'ops.load(14, *[0, 1.26056566201701, 0, -0.360161617719145, 0, -0.630282831008499])\n',
        'ops.load(10, *[0, 1.26056566201694, 0, -0.360161617719126, 0, 0.630282831008476])\n',
        'ops.load(13, *[0, 0.146315657198395, 0, 0.0900404044297817, 0, 0.0731578285991983])\n',
        'ops.load(18, *[0, 0.146315657198403, 0, 0.0900404044297865, 0, -0.0731578285992009])\n',
        'ops.load(19, *[0, 1.26056566201701, 0, -0.360161617719146, 0, -0.630282831008500])\n',
        'ops.load(14, *[0, 1.26056566201694, 0, -0.360161617719127, 0, 0.630282831008477])\n',
        'ops.load(18, *[0, 0.117052525758723, 0, 0.0720323235438296, 0, 0.0585262628793609])\n',
        'ops.load(24, *[0, 0.117052525758715, 0, 0.0720323235438248, 0, -0.0585262628793583])\n',
        'ops.load(25, *[0, 1.00845252961355, 0, -0.288129294175299, 0, -0.504226264806779])\n',
        'ops.load(19, *[0, 1.00845252961361, 0, -0.288129294175319, 0, 0.504226264806802])\n',
        'ops.load(24, *[0, 0.120158079922239, 0, 0.0739434337983010, 0, 0.0600790399611199])\n',
        'ops.load(59, *[0, 0.120158079922243, 0, 0.0739434337983034, 0, -0.0600790399611212])\n',
        'ops.load(60, *[0, 1.03520807317625, 0, -0.295773735193214, 0, -0.517604036588121])\n',
        'ops.load(25, *[0, 1.03520807317621, 0, -0.295773735193204, 0, 0.517604036588110])\n',
        'ops.load(59, *[0, 0.124942353209710, 0, 0.0768876019752063, 0, 0.0568977744108762])\n',
        'ops.load(66, *[0, 0.0760061263237388, 0, 0.0467730008146085, 0, -0.0408801640107090])\n',
        'ops.load(67, *[0, 0.654822011404518, 0, -0.187092003258434, 0, -0.352198336092262])\n',
        'ops.load(60, *[0, 1.07642642765289, 0, -0.307550407900825, 0, 0.490196210309087])\n',
        'ops.load(60, *[0, 1.50171097607824, 0, 0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(67, *[0, 0.913535172160317, 0, 0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(68, *[0, 0.913535172160317, 0, -0.456767586080159, 0, -0.491348125128712])\n',
        'ops.load(61, *[0, 1.50171097607824, 0, -0.750855488039121, 0, 0.683867480899951])\n',
        'ops.load(61, *[0, 0.583865227499220, 0, 0.0973108712498700, 0, 0.265887676573901])\n',
        'ops.load(68, *[0, 0.355182474935931, 0, 0.0591970791559885, 0, -0.191036151050043])\n',
        'ops.load(69, *[0, 0.0102315939281955, 0, -0.00657745323955428, 0, -0.00550309900144156])\n',
        'ops.load(62, *[0, 0.0168191629320763, 0, -0.0108123190277633, 0, 0.00765931578607944])\n',
        'ops.load(15, *[0, 0.5697869342822274, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.5697869342822279, 0, 0.0, 0, 0.0])\n',
        'ops.load(21, *[0, 0.12661931872938303, 0, 0.0, 0, 0.0])\n',
        'ops.load(20, *[0, 0.546995456910950, 0, 0.0911659094851582, 0, 0.273497728455472])\n',
        'ops.load(26, *[0, 0.546995456910913, 0, 0.0911659094851522, 0, -0.273497728455460])\n',
        'ops.load(27, *[0, 0.0157570707752115, 0, -0.0101295454983502, 0, -0.00787853538760582])\n',
        'ops.load(21, *[0, 0.0157570707752125, 0, -0.0101295454983509, 0, 0.00787853538760616])\n',
        'ops.load(26, *[0, 0.561507950405852, 0, 0.0935846584009754, 0, 0.280753975202928])\n',
        'ops.load(61, *[0, 0.561507950405871, 0, 0.0935846584009784, 0, -0.280753975202934])\n',
        'ops.load(62, *[0, 0.0161751261433790, 0, -0.0103982953778865, 0, -0.00808756307168943])\n',
        'ops.load(27, *[0, 0.0161751261433784, 0, -0.0103982953778861, 0, 0.00808756307168926])\n']


def test_28m_bridge_compound_point_load_midspan(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    edge_dist = 0.3
    P = 1000
    test_point_load = og.create_compound_load(name="Point test case")
    p_list = [0,edge_dist,edge_dist+2,edge_dist+4,edge_dist+6,bridge_28.width-edge_dist,bridge_28.width]
    for p in p_list:
        point = og.create_load(type="point",name="compound point",point1=og.LoadPoint(bridge_28.long_dim/2,0,p,P))
        test_point_load.add_load(load_obj=point)
    point_case = og.LoadCase(name="Compound point load case")
    point_case.add_load_groups(test_point_load)

    bridge_28.add_load_case(point_case)
    bridge_28.load_case_list


# example super t 28 m  ref bridge
# test for comparing max deflection with a numerical comparison model in Lusas
def test_28m_bridge(ref_28m_bridge):
    bridge_28 = ref_28m_bridge

    og.opsplt.plot_model("nodes")
    og.ops.wipeAnalysis()
    lane_point_1 = og.create_load_vertex(x=20.89, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=20.89, y=0, z=7, p=5)
    line_load_middle = og.create_load(type="line",name="Ref mid_point_load", point1=lane_point_1, point2=lane_point_2)
    # 57 to 63
    point_load_case = og.create_load_case(name="point_load_case")
    line_load_case = og.create_load_case(name="line_load_case")
    line_load_case.add_load_groups(line_load_middle)
    ref_node_force = og.NodeForces(0, -1000, 0, 0, 0, 0)
    p1 = og.NodalLoad(name="point", node_tag=57, node_force=ref_node_force)
    p2 = og.NodalLoad(name="point", node_tag=58, node_force=ref_node_force)
    p3 = og.NodalLoad(name="point", node_tag=59, node_force=ref_node_force)
    p4 = og.NodalLoad(name="point", node_tag=60, node_force=ref_node_force)
    p5 = og.NodalLoad(name="point", node_tag=61, node_force=ref_node_force)
    p6 = og.NodalLoad(name="point", node_tag=62, node_force=ref_node_force)
    p7 = og.NodalLoad(name="point", node_tag=63, node_force=ref_node_force)
    point_load_case.add_load_groups(p1)
    point_load_case.add_load_groups(p2)
    point_load_case.add_load_groups(p3)
    point_load_case.add_load_groups(p4)
    point_load_case.add_load_groups(p5)
    point_load_case.add_load_groups(p6)
    point_load_case.add_load_groups(p7)

    bridge_28.add_load_case(line_load_case)
    # add a load combination
    bridge_28.add_load_combination(load_combination_name="factored_point",
                                   load_case_and_factor_dict={"point_load_case": 1.5})
    bridge_28.analyze(all=True)

    results = bridge_28.get_results(get_combinations=False)
    # extract points along mid span, compare dY with those from Lusas model
    print(og.ops.nodeDisp(57))
    print(og.ops.nodeDisp(63))
    print(og.ops.nodeDisp(60))
    # opsv.plot_defo(unDefoFlag=0, endDispFlag=0)
    # plt.show()
    # opsv.section_force_distribution_3d()
    minY, maxY = og.opsv.section_force_diagram_3d('Mz', {}, 1)
    og.plt.show()
    pass


# test for 28 m ref bridge, using a moving load
def test_28m_bridge_moving_load(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    # create moving load case
    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = og.create_moving_path(start_point=og.Point(0, 0, 2), end_point=og.Point(29, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    bridge_28.add_load_case(move_point)

    bridge_28.analyze(all=True)
    results = bridge_28.get_results()
    results.sel(Node=63, Component='dy')
    print(results)


# test for 28 m  bridge using a moving compound load
def test_28m_bridge_moving_compound_load(ref_28m_bridge):
    bridge_28 = ref_28m_bridge
    # create moving load case

    M1600 = og.CompoundLoad("M1600 LM")
    back_wheel = og.create_load(type="point",name="single point", point1=og.LoadPoint(5, 0, 2, 20))  # Single point load 20 N
    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50))  # Single point load 50 N
    # compound the point loads
    M1600.add_load(load_obj=front_wheel)
    M1600.add_load(load_obj=back_wheel)
    M1600.add_load(load_obj=back_wheel)
    M1600.add_load(load_obj=front_wheel)
    M1600.set_global_coord(og.Point(-6, 0, 0))

    truck = og.create_moving_load(name="4 wheel truck")
    single_path = og.create_moving_path(start_point=og.Point(0, 0, 0), end_point=og.Point(29, 0, 0))  # create path object
    truck.set_path(single_path)
    truck.add_loads(load_obj=M1600)

    bridge_28.add_load_case(truck)

    bridge_28.analyze(all=True)
    results = bridge_28.get_results()
    results.sel(Node=63, Component='dy')
    maxY = results.sel(Component='Vy_i').max(dim='Loadcase')
    minY = results.sel(Component='Mz_i').max(dim='Loadcase')
    print(results)


# Simple 2 x 3 Grid example
def test_simple_grid():
    L = 3
    w = 2
    n_l = 5  # when 2, edge_beam not needed; when 3, only one exterior_main_beam is needed, when 4...
    n_t = 3  # when 2, grid not complete and analysis fails

    simply_grid = og.create_grillage(bridge_name="Simple", long_dim=L, width=w, skew=0,
                                 num_long_grid=n_l, num_trans_grid=n_t, edge_beam_dist=[0.3], mesh_type="Ortho")
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa")

    # define sections
    super_t_beam_section = og.create_section(A=1.0447,
                                      J=0.230698, Iy=0.231329, Iz=0.533953,
                                      Ay=0.397032, Az=0.434351)
    transverse_slab_section = og.create_section(A=0.5372,
                                         J=2.79e-3, Iy=0.3988 / 2, Iz=1.45e-3 / 2,
                                         Ay=0.447 / 2, Az=0.447 / 2, unit_width=True)
    end_tranverse_slab_section = og.create_section(A=0.5372 / 2, J=2.68e-3, Iy=0.04985,
                                            Iz=0.725e-3,
                                            Ay=0.223, Az=0.223)
    edge_beam_section = og.create_section(A=0.039375, J=0.21e-3, Iy=0.1e-3,
                                   Iz=0.166e-3,
                                   Ay=0.0328, Az=0.0328)
    # define grillage members
    super_t_beam = og.create_member(member_name="Intermediate beams", section=super_t_beam_section,
                                     material=concrete)
    transverse_slab = og.create_member(member_name="concrete slab",
                                        section=transverse_slab_section, material=concrete)
    edge_beam = og.create_member(member_name="exterior beams",
                                  section=edge_beam_section, material=concrete)
    end_tranverse_slab = og.create_member(member_name="edge transverse",
                                           section=end_tranverse_slab_section, material=concrete)

    # set grillage member to element groups of grillage model
    simply_grid.set_member(super_t_beam, member="interior_main_beam")
    simply_grid.set_member(super_t_beam, member="exterior_main_beam_1")
    simply_grid.set_member(super_t_beam, member="exterior_main_beam_2")
    simply_grid.set_member(edge_beam, member="edge_beam")
    simply_grid.set_member(transverse_slab, member="transverse_slab")
    simply_grid.set_member(end_tranverse_slab, member="start_edge")
    simply_grid.set_member(end_tranverse_slab, member="end_edge")

    pyfile = False
    simply_grid.create_osp_model(pyfile=False)
    # opsv.plot_model("nodes")
    # plt.show()

    # loading
    # Line load (100 load at midspan)
    point_1 = og.create_load_vertex(x=L / 2, y= 0, z=0, p=1e3)
    point_2 = og.create_load_vertex(x=L / 2, y=0, z=w, p=1e3)
    # test_load = opsg.LineLoading("Test Load", point1=point_1, point2=point_2)
    test_load = og.create_load(type="line",name="Test Load", point1=point_1, point2=point_2)  #
    #test_load = og.PointLoad("Test Point", point1=og.LoadPoint(L / 2, 0, w / 2, 1e3))

    # Load case creating and assign
    test_case = og.create_load_case(name="Test Case")
    test_case.add_load_groups(test_load)
    #test_load2 = og.PointLoad("Test Point", point1=og.LoadPoint(L / 2, 0, 1.7, 1e3))
    # test_load3 = PointLoad("Test Point", point1 = LoadPoint(L/2,0,w,1e3))
    #test_load4 = og.PointLoad("Test Point", point1=og.LoadPoint(L / 2, 0, 0.3, 1e3))
    # test_load5 = PointLoad("Test Point", point1 = LoadPoint(L/2,0,0,1e3))
    #test_case.add_load_groups(test_load2)
    # test_case.add_load_groups(test_load3)
    #test_case.add_load_groups(test_load4)
    # test_case.add_load_groups(test_load5)
    simply_grid.add_load_case(test_case)  # adding load case to grillage model
    simply_grid.add_load_combination("ULS", {test_case.name: 2})
    print(simply_grid.load_case_list[0]['load_command'])
    simply_grid.analyze(all=True)
    og.opsv.plot_defo()

    og.plt.show()
    minY, maxY = og.opsv.section_force_diagram_3d('Mz', {}, 1)
    og.plt.show()
    results = simply_grid.get_results(get_combinations=False)
    print(results)
    #print(results.sel(Node=12))
    print(maxY, minY)
    pass

# def test_create_shell_link_model(shell_link_bridge):
#     shell_link_model = shell_link_bridge
#     point_1 = og.create_load_vertex(x=2, z=3, p=1e3)
#     point_2 = og.create_load_vertex(x=5, z=4, p=1e3)
#     # test_load = opsg.LineLoading("Test Load", point1=point_1, point2=point_2)
#     test_load = og.create_load(type="point",name="Test Load", point1=point_1, point2=point_2)  #
#     #test_load = og.PointLoad("Test Point", point1=og.LoadPoint(L / 2, 0, w / 2, 1e3))
#
#     # Load case creating and assign
#     test_case = og.create_load_case(name="Test Case")
#     test_case.add_load_groups(test_load)
#
#     shell_link_model.add_load_case(test_case)
#     shell_link_model.analyze(all=True)
#     results = shell_link_model.get_results(get_combinations=False)
#     #og.opsv.plot_defo()
#     #og.plt.show()
#     minY, maxY = og.opsv.section_force_diagram_3d('Mz', {}, 1)
#     og.plt.show()