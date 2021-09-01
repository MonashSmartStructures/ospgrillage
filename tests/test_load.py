"""

"""
import pytest
import ospgrillage as og
import sys, os

sys.path.insert(0, os.path.abspath('../'))

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

    bridge_28 = og.OspGrillage(bridge_name="SuperT_28m", long_dim=28, width=7, skew=0,
                               num_long_grid=7, num_trans_grid=14, edge_beam_dist=1.0875, mesh_type="Ortho")

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

# test to check compound load position relative to global are correct
def test_compound_load_positions():
    #
    location = og.create_load_vertex(x=5, z=-2, p=20)  # create load point
    Single = og.create_load(type="point", name="single point", point1=location)
    # front_wheel = PointLoad(name="front wheel", localpoint1=LoadPoint(2, 0, 2, 50))
    # Line load
    barrierpoint_1 = og.create_load_vertex(x=-1, z=0, p=2)
    barrierpoint_2 = og.create_load_vertex(x=11, z=0, p=2)
    Barrier = og.LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)

    M1600 = og.create_compound_load(name="Lane and Barrier")
    M1600.add_load(load_obj=Single)
    M1600.add_load(load_obj=Barrier)  # this overwrites the current global pos of line load
    # the expected midpoint (reference point initial is 6,0,0) is now at 9,0,5 (6+3, 0+0, 5+0)
    # when setting the global coordinate, the global coordinate is added with respect to ref point (9,0,5)
    # therefore (3+4, 0+0, 3+5) = (13,0,8)
    # M1600.set_global_coord(og.Point(4, 0, 3))
    a = 2
    # check if point Single is same as point Single's load vertex
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(x=5, y=0, z=-2, p=20)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=-1, y=0, z=0, p=2)
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(x=11.0, y=0, z=0, p=2)

    # now we set global and see if correct
    M1600.set_global_coord(og.Point(4, 0, 3))
    assert M1600.compound_load_obj_list[0].load_point_1 == og.LoadPoint(x=9, y=0, z=1, p=20)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=3, y=0, z=3, p=2)
    assert M1600.compound_load_obj_list[1].load_point_2 == og.LoadPoint(x=15.0, y=0, z=3, p=2)


def test_point_load_getter(bridge_model_42_negative):  # test get_point_load_nodes() function
    # test if setter and getter is correct              # and assign_point_to_node() function

    example_bridge = bridge_model_42_negative
    # create reference point load
    location = og.create_load_vertex(x=5, y=0, z=2, p=20)
    Single = og.create_load(type="point",name="single point", point1=location,shape_function="hermite")
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
    grid_nodes, _ = example_bridge.get_point_load_nodes(point=location)
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
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
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
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
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
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
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
    Barrier = og.LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
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
    Lane = og.PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4,shape_function="hermite")
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
    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(19, *[0, 1.40688131921541, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 1.40688131921534, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 1.40688131921534, 0, 0, 0, 0])\n', 'ops.load(20, *[0, 1.40688131921541, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 1.44420769137308, 0, 0, 0, 0])\n', 'ops.load(60, *[0, 1.44420769137311, 0, 0, 0, 0])\n', 'ops.load(61, *[0, 1.44420769137311, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 1.44420769137308, 0, 0, 0, 0])\n', 'ops.load(13, *[0, 0.00883644799442276, 0, 0.00543781415041401, 0, 0.00549241204442737])\n', 'ops.load(18, *[0, 0.0957938611102078, 0, 0.0589500683755124, 0, -0.0252300768696094])\n', 'ops.load(19, *[0, 0.825300957257174, 0, -0.235800273502050, 0, -0.217366816107404])\n', 'ops.load(14, *[0, 0.0761293981057961, 0, -0.0217512566016560, 0, 0.0473192422289127])\n', 'ops.load(18, *[0, 0.117052525758723, 0, 0.0720323235438296, 0, 0.0585262628793609])\n', 'ops.load(24, *[0, 0.117052525758715, 0, 0.0720323235438248, 0, -0.0585262628793583])\n', 'ops.load(25, *[0, 1.00845252961355, 0, -0.288129294175299, 0, -0.504226264806779])\n', 'ops.load(19, *[0, 1.00845252961361, 0, -0.288129294175319, 0, 0.504226264806802])\n', 'ops.load(24, *[0, 0.120158079922239, 0, 0.0739434337983010, 0, 0.0600790399611199])\n', 'ops.load(59, *[0, 0.120158079922243, 0, 0.0739434337983034, 0, -0.0600790399611212])\n', 'ops.load(60, *[0, 1.03520807317625, 0, -0.295773735193214, 0, -0.517604036588121])\n', 'ops.load(25, *[0, 1.03520807317621, 0, -0.295773735193204, 0, 0.517604036588110])\n', 'ops.load(59, *[0, 0.124942353209710, 0, 0.0768876019752063, 0, 0.0568977744108762])\n', 'ops.load(66, *[0, 0.0760061263237388, 0, 0.0467730008146085, 0, -0.0408801640107090])\n', 'ops.load(67, *[0, 0.654822011404518, 0, -0.187092003258434, 0, -0.352198336092262])\n', 'ops.load(60, *[0, 1.07642642765289, 0, -0.307550407900825, 0, 0.490196210309087])\n', 'ops.load(60, *[0, 1.50171097607824, 0, 0.750855488039121, 0, 0.683867480899951])\n', 'ops.load(67, *[0, 0.913535172160317, 0, 0.456767586080159, 0, -0.491348125128712])\n', 'ops.load(68, *[0, 0.913535172160317, 0, -0.456767586080159, 0, -0.491348125128712])\n', 'ops.load(61, *[0, 1.50171097607824, 0, -0.750855488039121, 0, 0.683867480899951])\n', 'ops.load(61, *[0, 0.583865227499220, 0, 0.0973108712498700, 0, 0.265887676573901])\n', 'ops.load(68, *[0, 0.355182474935931, 0, 0.0591970791559885, 0, -0.191036151050043])\n', 'ops.load(69, *[0, 0.0102315939281955, 0, -0.00657745323955428, 0, -0.00550309900144156])\n', 'ops.load(62, *[0, 0.0168191629320763, 0, -0.0108123190277633, 0, 0.00765931578607944])\n', 'ops.load(15, *[0, 0.08992923272602986, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.36279806628438993, 0, 0.0, 0, 0.0])\n', 'ops.load(21, *[0, 0.05030303322337963, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.546995456910950, 0, 0.0911659094851582, 0, 0.273497728455472])\n', 'ops.load(26, *[0, 0.546995456910913, 0, 0.0911659094851522, 0, -0.273497728455460])\n', 'ops.load(27, *[0, 0.0157570707752115, 0, -0.0101295454983502, 0, -0.00787853538760582])\n', 'ops.load(21, *[0, 0.0157570707752125, 0, -0.0101295454983509, 0, 0.00787853538760616])\n', 'ops.load(26, *[0, 0.561507950405852, 0, 0.0935846584009754, 0, 0.280753975202928])\n', 'ops.load(61, *[0, 0.561507950405871, 0, 0.0935846584009784, 0, -0.280753975202934])\n', 'ops.load(62, *[0, 0.0161751261433790, 0, -0.0103982953778865, 0, -0.00808756307168943])\n', 'ops.load(27, *[0, 0.0161751261433784, 0, -0.0103982953778861, 0, 0.00808756307168926])\n', 'ops.load(14, *[0, 0.106207307625274, 0, 0.0531036538126368, 0, 0.0660145678416751])\n', 'ops.load(19, *[0, 1.15136852295923, 0, 0.575684261479614, 0, -0.303246116221267])\n', 'ops.load(20, *[0, 1.15136852295923, 0, -0.575684261479614, 0, -0.303246116221267])\n', 'ops.load(15, *[0, 0.106207307625274, 0, -0.0531036538126368, 0, 0.0660145678416751])\n']


def test_local_vs_global_coord_settings():
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)  # create load point
    local_point = og.create_load(type="point", name="single point",
                                 localpoint1=location,shape_function="hermite")  # defined for local coordinate
    global_point = og.create_load(type="point", name="single point",
                                  point1=location,shape_function="hermite")  # defined for local coordinate

    M1600 = og.CompoundLoad("Truck model")
    M1600.add_load(load_obj=local_point)  # if local_coord is set, append the local coordinate of the point load

    assert M1600.compound_load_obj_list[0].load_point_1 is None
    M1600.add_load(load_obj=global_point)
    assert M1600.compound_load_obj_list[1].load_point_1 == og.LoadPoint(x=5, y=0, z=-2, p=20)

# test analysis of moving load case, test pass if no errors are returned
def test_moving_load_case(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50),shape_function="hermite")  # Single point load 50 N

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
    barrierpoint_1 = og.create_load_vertex(x=5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
    barrier_load_case = og.create_load_case(name="Barrier")
    barrier_load_case.add_load_groups(Barrier)  # ch
    example_bridge.add_load_case(barrier_load_case)
    # add moving load case
    front_wheel = og.PointLoad(name="front wheel", point1=og.LoadPoint(2, 0, 2, 50),shape_function="hermite")  # Single point load 50 N

    single_path = og.create_moving_path(start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    # example_bridge.analyze(all=True)
    example_bridge.analyze(all=True)
    results = example_bridge.get_results(load_case="single_moving_point")
    #results = example_bridge.get_results()
    print(results)


# test moving compound load, test pass if no errors are returned
def test_moving_compound_load(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    M1600 = og.CompoundLoad("M1600 LM")
    back_wheel = og.create_load(type="point",name="single point", point1=og.LoadPoint(5, 0, 2, 20),shape_function="hermite")  # Single point load 20 N
    front_wheel = og.create_load(type="point",name="front wheel", point1=og.LoadPoint(2, 0, 2, 50),shape_function="hermite")  # Single point load 50 N
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


# test check correct distribution of a patch defined with bounds outside of grillage
def test_patch_partially_outside_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    lane_point_1 = og.create_load_vertex(x=-5, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=-5, z=5, p=5)
    Lane = og.create_load(type="patch",name="Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4,shape_function="hermite")
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

