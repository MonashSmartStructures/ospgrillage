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
# =====================================================================================================================
# Tests
# =====================================================================================================================
# test to check compound load position relative to global are correct
def test_compound_load_positions():
    #
    location = og.create_load_vertex(x=5, z=-2, p=20)  # create load point
    Single = og.create_load(type="point", name="single point", point1=location)
    # front_wheel = PointLoad(name="front wheel", localpoint1=LoadPoint(2, 0, 2, 50))
    # Line load
    barrierpoint_1 = og.create_load_vertex(x=-1, z=0, p=2)
    barrierpoint_2 = og.create_load_vertex(x=11, z=0, p=2)
    Barrier = og.LineLoading(point1=barrierpoint_1, point2=barrierpoint_2)

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
    ULS_DL.add_load(Single)  # ch
    example_bridge.add_load_case(ULS_DL)
    og.ops.wipe()

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(12, *[0, 0.6075807082987861, 0, 0.3738958204915605, 0, 0.3416694313270197])\n', 'ops.load(17, *[0, 1.4724192917012147, 0, 0.9061041795084396, 0, -0.6139157679716769])\n', 'ops.load(18, *[0, 12.685458513118153, 0, -3.6244167180337588, 0, -5.289120462525214])\n', 'ops.load(13, *[0, 5.234541486881847, 0, -1.4955832819662427, 0, 2.9436135622020148])\n']



# test point load returning None when point (loadpoint) is outside of mesh
def test_point_load_outside_straight_mesh(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    location = og.create_load_vertex(x=5, y=0, z=-2, p=20)
    Single = og.create_load(type="point",name="single point", point1=location)
    ULS_DL = og.create_load_case(name="Point")
    ULS_DL.add_load(Single)  # ch
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
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
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
                        'edge_intersect': [], 'ends': [[10, 0, 3]]}, 56: {'long_intersect': [],
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
    ULS_DL.add_load(Barrier)  # ch
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
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{5: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[4, 0, 1]]}, 6: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[4, 0, 1]]}, 27: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 28: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 29: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 30: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}}]



def test_line_load_coincide_transverse_member(bridge_42_0_angle_mesh):
    example_bridge = bridge_42_0_angle_mesh
    og.opsplt.plot_model("nodes")

    # create reference line load

    barrierpoint_1 = og.create_load_vertex(x=7.5, y=0, z=1, p=2)
    #barrierpoint_1 = og.create_load_vertices(x=7.5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=7.5, y=0, z=6, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(51, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(30, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(31, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(52, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(51, *[0, 1.25, 0, 0, 0, 0])\n', 'ops.load(30, *[0, 2.775557561562892e-16, 0, 0, 0, 0])\n', 'ops.load(31, *[0, 2.775557561562891e-16, 0, 0, 0, 0])\n', 'ops.load(52, *[0, 1.2499999999999996, 0, 0, 0, 0])\n', 'ops.load(52, *[0, 1.2499999999999996, 0, 0, 0, 0])\n', 'ops.load(31, *[0, 2.775557561562891e-16, 0, 0, 0, 0])\n', 'ops.load(32, *[0, 2.775557561562892e-16, 0, 0, 0, 0])\n', 'ops.load(53, *[0, 1.25, 0, 0, 0, 0])\n', 'ops.load(53, *[0, 1.2499999999999996, 0, 0, 0, 0])\n', 'ops.load(32, *[0, 2.775557561562891e-16, 0, 0, 0, 0])\n', 'ops.load(33, *[0, 2.775557561562892e-16, 0, 0, 0, 0])\n', 'ops.load(54, *[0, 1.25, 0, 0, 0, 0])\n', 'ops.load(54, *[0, 1.250000000000001, 0, 0, 0, 0])\n', 'ops.load(33, *[0, 2.7755575615628943e-16, 0, 0, 0, 0])\n', 'ops.load(34, *[0, 2.775557561562888e-16, 0, 0, 0, 0])\n', 'ops.load(55, *[0, 1.2499999999999982, 0, 0, 0, 0])\n', 'ops.load(55, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(34, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(35, *[0, 0.0, 0, 0, 0, 0])\n', 'ops.load(56, *[0, 0.0, 0, 0, 0, 0])\n']



def test_line_load_coincide_edge_beam(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines

    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=5, y=0, z=1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=1, p=2)
    Barrier = og.create_load(type="line",name="Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)

    assert example_bridge.global_line_int_dict == [{9: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[5, 0, 1]]}, 10: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[5, 0, 1]]}, 27: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 28: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 29: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}, 30: {'long_intersect': [], 'trans_intersect': [], 'edge_intersect': [], 'ends': [[10, 0, 1]]}}]



def test_line_load_outside_of_mesh(bridge_model_42_negative):
    # when set line load z coordinate to z = 0 , test if line returns correct coincide node lines
    example_bridge = bridge_model_42_negative
    # create reference line load
    barrierpoint_1 = og.create_load_vertex(x=3, y=0, z=-1, p=2)
    barrierpoint_2 = og.create_load_vertex(x=10, y=0, z=-1, p=2)
    Barrier = og.create_load(type="line",point1=barrierpoint_1, point2=barrierpoint_2,shape_function="hermite")
    ULS_DL = og.create_load_case(name="Barrier")
    ULS_DL.add_load(Barrier)  # ch
    example_bridge.add_load_case(ULS_DL)
    assert example_bridge.global_line_int_dict == [{}]


# test a default patch load - patch is within the mesh and sufficiently larger than a single grid
def test_patch_load(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, z=5, p=5)
    Lane = og.create_load(type="patch",point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4,shape_function="hermite")
    ULS_DL = og.create_load_case(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(19, *[0, 1.4068813192153744, 0, 0.7034406596076872, 0, 0.7034406596076874])\n', 'ops.load(25, *[0, 1.406881319215377, 0, 0.7034406596076888, 0, -0.7034406596076882])\n', 'ops.load(26, *[0, 1.4068813192153784, 0, -0.703440659607689, 0, -0.7034406596076889])\n', 'ops.load(20, *[0, 1.4068813192153753, 0, -0.7034406596076875, 0, 0.703440659607688])\n', 'ops.load(25, *[0, 1.4442076913730983, 0, 0.7221038456865494, 0, 0.7221038456865487])\n', 'ops.load(60, *[0, 1.444207691373093, 0, 0.7221038456865465, 0, -0.7221038456865468])\n', 'ops.load(61, *[0, 1.4442076913730937, 0, -0.7221038456865468, 0, -0.7221038456865473])\n', 'ops.load(26, *[0, 1.4442076913730992, 0, -0.7221038456865496, 0, 0.7221038456865492])\n', 'ops.load(13, *[0, 0.008836447994423183, 0, 0.005437814150414265, 0, 0.005492412044427625])\n', 'ops.load(18, *[0, 0.09579386111020732, 0, 0.05895006837551218, 0, -0.02523007686960981])\n', 'ops.load(19, *[0, 0.8253009572571705, 0, -0.23580027350204877, 0, -0.2173668161074075])\n', 'ops.load(14, *[0, 0.0761293981057997, 0, -0.021751256601657065, 0, 0.047319242228914905])\n', 'ops.load(18, *[0, 0.11705252575871952, 0, 0.07203232354382738, 0, 0.058526262879359726])\n', 'ops.load(24, *[0, 0.11705252575871895, 0, 0.07203232354382702, 0, -0.05852626287935953])\n', 'ops.load(25, *[0, 1.0084525296135782, 0, -0.28812929417530814, 0, -0.5042262648067896])\n', 'ops.load(19, *[0, 1.0084525296135833, 0, -0.2881292941753096, 0, 0.5042262648067912])\n', 'ops.load(24, *[0, 0.12015807992224105, 0, 0.07394343379830216, 0, 0.06007903996112054])\n', 'ops.load(59, *[0, 0.12015807992224112, 0, 0.0739434337983022, 0, -0.06007903996112056])\n', 'ops.load(60, *[0, 1.0352080731762308, 0, -0.2957737351932089, 0, -0.5176040365881154])\n', 'ops.load(25, *[0, 1.03520807317623, 0, -0.2957737351932087, 0, 0.5176040365881152])\n', 'ops.load(59, *[0, 0.12494235320970946, 0, 0.0768876019752058, 0, 0.05689777441087614])\n', 'ops.load(66, *[0, 0.07600612632374013, 0, 0.0467730008146093, 0, -0.040880164010709624])\n', 'ops.load(67, *[0, 0.6548220114045282, 0, -0.18709200325843686, 0, -0.3521983360922664])\n', 'ops.load(60, *[0, 1.076426427652878, 0, -0.3075504079008228, 0, 0.4901962103090852])\n', 'ops.load(60, *[0, 1.5017109760782246, 0, 0.7508554880391124, 0, 0.6838674808999476])\n', 'ops.load(67, *[0, 0.9135351721603335, 0, 0.45676758608016677, 0, -0.4913481251287189])\n', 'ops.load(68, *[0, 0.9135351721603342, 0, -0.45676758608016704, 0, -0.4913481251287192])\n', 'ops.load(61, *[0, 1.5017109760782257, 0, -0.7508554880391126, 0, 0.6838674808999482])\n', 'ops.load(61, *[0, 0.5838652274992159, 0, 0.09731087124986945, 0, 0.2658876765739001])\n', 'ops.load(68, *[0, 0.3551824749359356, 0, 0.059197079155989346, 0, -0.19103615105004493])\n', 'ops.load(69, *[0, 0.010231593928195719, 0, -0.00657745323955438, 0, -0.005503099001441646])\n', 'ops.load(62, *[0, 0.016819162932076248, 0, -0.010812319027763287, 0, 0.007659315786079458])\n', 'ops.load(15, *[0, 0.08992923272602986, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.36279806628438993, 0, 0.0, 0, 0.0])\n', 'ops.load(21, *[0, 0.05030303322337963, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.5469954569109343, 0, 0.09116590948515578, 0, 0.27349772845546666])\n', 'ops.load(26, *[0, 0.5469954569109284, 0, 0.09116590948515481, 0, -0.2734977284554647])\n', 'ops.load(27, *[0, 0.01575707077521196, 0, -0.01012954549835055, 0, -0.007878535387605993])\n', 'ops.load(21, *[0, 0.01575707077521213, 0, -0.01012954549835066, 0, 0.00787853538760605])\n', 'ops.load(26, *[0, 0.5615079504058661, 0, 0.09358465840097775, 0, 0.2807539752029323])\n', 'ops.load(61, *[0, 0.5615079504058568, 0, 0.0935846584009762, 0, -0.28075397520292916])\n', 'ops.load(62, *[0, 0.016175126143378623, 0, -0.010398295377886262, 0, -0.008087563071689334])\n', 'ops.load(27, *[0, 0.01617512614337889, 0, -0.010398295377886436, 0, 0.008087563071689424])\n', 'ops.load(14, *[0, 0.1062073076252783, 0, 0.05310365381263916, 0, 0.06601456784167795])\n', 'ops.load(19, *[0, 1.151368522959222, 0, 0.5756842614796112, 0, -0.30324611622127134])\n', 'ops.load(20, *[0, 1.1513685229592228, 0, -0.5756842614796114, 0, -0.3032461162212715])\n', 'ops.load(15, *[0, 0.10620730762527836, 0, -0.05310365381263918, 0, 0.06601456784167799])\n']



# test for patch load with linear shape function for load distribution
def test_patch_load_using_linear_shape_function(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative

    lane_point_1 = og.create_load_vertex(x=5, y=0, z=3, p=5)
    lane_point_2 = og.create_load_vertex(x=8, y=0, z=3, p=5)
    lane_point_3 = og.create_load_vertex(x=8, y=0, z=5, p=5)
    lane_point_4 = og.create_load_vertex(x=5, y=0, z=5, p=5)
    Lane = og.PatchLoading(point1=lane_point_1, point2=lane_point_2, point3=lane_point_3,
                           point4=lane_point_4, shape_function="linear")
    ULS_DL = og.LoadCase(name="Lane")
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(19, *[0, 1.4068813192153748, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 1.4068813192153768, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 1.4068813192153775, 0, 0, 0, 0])\n', 'ops.load(20, *[0, 1.4068813192153755, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 1.4442076913730977, 0, 0, 0, 0])\n', 'ops.load(60, *[0, 1.444207691373094, 0, 0, 0, 0])\n', 'ops.load(61, *[0, 1.4442076913730946, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 1.4442076913730983, 0, 0, 0, 0])\n', 'ops.load(13, *[0, 0.035971693090412066, 0, 0, 0, 0])\n', 'ops.load(18, *[0, 0.16524043980310807, 0, 0, 0, 0])\n', 'ops.load(19, *[0, 0.6609617592124323, 0, 0, 0, 0])\n', 'ops.load(14, *[0, 0.14388677236164826, 0, 0, 0, 0])\n', 'ops.load(18, *[0, 0.22510101107446043, 0, 0, 0, 0])\n', 'ops.load(24, *[0, 0.22510101107445965, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 0.9004040442978386, 0, 0, 0, 0])\n', 'ops.load(19, *[0, 0.9004040442978417, 0, 0, 0, 0])\n', 'ops.load(24, *[0, 0.2310732306196943, 0, 0, 0, 0])\n', 'ops.load(59, *[0, 0.2310732306196944, 0, 0, 0, 0])\n', 'ops.load(60, *[0, 0.9242929224787776, 0, 0, 0, 0])\n', 'ops.load(25, *[0, 0.9242929224787771, 0, 0, 0, 0])\n', 'ops.load(59, *[0, 0.22487220771081937, 0, 0, 0, 0])\n', 'ops.load(66, *[0, 0.1615671760073524, 0, 0, 0, 0])\n', 'ops.load(67, *[0, 0.6462687040294085, 0, 0, 0, 0])\n', 'ops.load(60, *[0, 0.8994888308432759, 0, 0, 0, 0])\n', 'ops.load(60, *[0, 1.4054512981926102, 0, 0, 0, 0])\n', 'ops.load(67, *[0, 1.0097948500459482, 0, 0, 0, 0])\n', 'ops.load(68, *[0, 1.0097948500459486, 0, 0, 0, 0])\n', 'ops.load(61, *[0, 1.4054512981926108, 0, 0, 0, 0])\n', 'ops.load(61, *[0, 0.5059624673493412, 0, 0, 0, 0])\n', 'ops.load(68, *[0, 0.36352614601654, 0, 0, 0, 0])\n', 'ops.load(69, *[0, 0.04039179400183784, 0, 0, 0, 0])\n', 'ops.load(62, *[0, 0.05621805192770466, 0, 0, 0, 0])\n', 'ops.load(15, *[0, 0.08992923272602986, 0, 0, 0, 0])\n', 'ops.load(20, *[0, 0.36279806628438993, 0, 0, 0, 0])\n', 'ops.load(21, *[0, 0.05030303322337963, 0, 0, 0, 0])\n', 'ops.load(20, *[0, 0.5064772749175308, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 0.5064772749175271, 0, 0, 0, 0])\n', 'ops.load(27, *[0, 0.056275252768614184, 0, 0, 0, 0])\n', 'ops.load(21, *[0, 0.056275252768614586, 0, 0, 0, 0])\n', 'ops.load(26, *[0, 0.5199147688943191, 0, 0, 0, 0])\n', 'ops.load(61, *[0, 0.5199147688943133, 0, 0, 0, 0])\n', 'ops.load(62, *[0, 0.05776830765492375, 0, 0, 0, 0])\n', 'ops.load(27, *[0, 0.0577683076549244, 0, 0, 0, 0])\n', 'ops.load(14, *[0, 0.22482308181507504, 0, 0, 0, 0])\n', 'ops.load(19, *[0, 1.0327527487694255, 0, 0, 0, 0])\n', 'ops.load(20, *[0, 1.0327527487694261, 0, 0, 0, 0])\n', 'ops.load(15, *[0, 0.2248230818150751, 0, 0, 0, 0])\n']



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

    example_bridge.analyze()
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
    barrier_load_case.add_load(Barrier)  # ch
    example_bridge.add_load_case(barrier_load_case)
    # add moving load case
    front_wheel = og.PointLoad(name="front wheel", point1=og.LoadPoint(2, 0, 2, 50),shape_function="hermite")  # Single point load 50 N

    single_path = og.create_moving_path(start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    # example_bridge.analyze(all=True)
    example_bridge.analyze()
    #results = example_bridge.get_results(load_case="single_moving_point")
    results = example_bridge.get_results(combinations={"Barrier":1,"single_moving_point":2})
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
    example_bridge.analyze()
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
    ULS_DL.add_load(Lane)  # ch
    example_bridge.add_load_case(ULS_DL)
    example_bridge.analyze()
    results = example_bridge.get_results()

    assert example_bridge.load_case_list[0]['load_command'] == ['ops.load(10, *[0, 1.1724010993461413, 0, 0.0, 0, 0.0])\n', 'ops.load(14, *[0, 1.1724010993461444, 0, 0.0, 0, 0.0])\n', 'ops.load(15, *[0, 1.172401099346146, 0, 0.0, 0, 0.0])\n', 'ops.load(14, *[0, 1.7586016490192178, 0, 0.879300824509609, 0, 0.8793008245096092])\n', 'ops.load(19, *[0, 1.7586016490192211, 0, 0.8793008245096107, 0, -0.8793008245096103])\n', 'ops.load(20, *[0, 1.7586016490192222, 0, -0.8793008245096111, 0, -0.8793008245096109])\n', 'ops.load(15, *[0, 1.758601649019219, 0, -0.8793008245096094, 0, 0.8793008245096097])\n', 'ops.load(19, *[0, 1.4068813192153744, 0, 0.7034406596076872, 0, 0.7034406596076874])\n', 'ops.load(25, *[0, 1.406881319215377, 0, 0.7034406596076888, 0, -0.7034406596076882])\n', 'ops.load(26, *[0, 1.4068813192153784, 0, -0.703440659607689, 0, -0.7034406596076889])\n', 'ops.load(20, *[0, 1.4068813192153753, 0, -0.7034406596076875, 0, 0.703440659607688])\n', 'ops.load(25, *[0, 1.4442076913730912, 0, 0.7221038456865457, 0, 0.7221038456865464])\n', 'ops.load(60, *[0, 1.4442076913731, 0, 0.7221038456865502, 0, -0.7221038456865492])\n', 'ops.load(61, *[0, 1.444207691373101, 0, -0.7221038456865505, 0, -0.7221038456865496])\n', 'ops.load(26, *[0, 1.4442076913730921, 0, -0.7221038456865461, 0, 0.7221038456865467])\n', 'ops.load(6, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n', 'ops.load(9, *[0, 0.07503367035815302, 0, 0.0, 0, 0.0])\n', 'ops.load(10, *[0, 0.41268518696984174, 0, 0.0, 0, 0.0])\n', 'ops.load(9, *[0, 0.14631565719839879, 0, 0.09004040442978384, 0, 0.0731578285991994])\n', 'ops.load(13, *[0, 0.1463156571983991, 0, 0.09004040442978403, 0, -0.07315782859919952])\n', 'ops.load(14, *[0, 1.2605656620169763, 0, -0.3601616177191362, 0, -0.6302828310084878])\n', 'ops.load(10, *[0, 1.2605656620169736, 0, -0.3601616177191354, 0, 0.630282831008487])\n', 'ops.load(13, *[0, 0.14631565719839917, 0, 0.09004040442978407, 0, 0.07315782859919959])\n', 'ops.load(18, *[0, 0.14631565719839917, 0, 0.09004040442978407, 0, -0.07315782859919959])\n', 'ops.load(19, *[0, 1.260565662016977, 0, -0.3601616177191364, 0, -0.6302828310084885])\n', 'ops.load(14, *[0, 1.260565662016977, 0, -0.3601616177191364, 0, 0.6302828310084885])\n', 'ops.load(18, *[0, 0.11705252575871884, 0, 0.07203232354382695, 0, 0.05852626287935949])\n', 'ops.load(24, *[0, 0.11705252575871963, 0, 0.07203232354382744, 0, -0.058526262879359754])\n', 'ops.load(25, *[0, 1.0084525296135842, 0, -0.2881292941753098, 0, -0.5042262648067914])\n', 'ops.load(19, *[0, 1.0084525296135773, 0, -0.28812929417530786, 0, 0.5042262648067892])\n', 'ops.load(24, *[0, 0.12015807992224073, 0, 0.07394343379830196, 0, 0.06007903996112042])\n', 'ops.load(59, *[0, 0.12015807992224145, 0, 0.07394343379830241, 0, -0.06007903996112066])\n', 'ops.load(60, *[0, 1.0352080731762336, 0, -0.2957737351932097, 0, -0.5176040365881163])\n', 'ops.load(25, *[0, 1.0352080731762274, 0, -0.2957737351932079, 0, 0.5176040365881142])\n', 'ops.load(59, *[0, 0.12494235320970946, 0, 0.0768876019752058, 0, 0.05689777441087614])\n', 'ops.load(66, *[0, 0.07600612632374013, 0, 0.0467730008146093, 0, -0.040880164010709624])\n', 'ops.load(67, *[0, 0.6548220114045282, 0, -0.18709200325843686, 0, -0.3521983360922664])\n', 'ops.load(60, *[0, 1.076426427652878, 0, -0.3075504079008228, 0, 0.4901962103090852])\n', 'ops.load(60, *[0, 1.5017109760782212, 0, 0.7508554880391107, 0, 0.683867480899947])\n', 'ops.load(67, *[0, 0.913535172160337, 0, 0.4567675860801685, 0, -0.4913481251287203])\n', 'ops.load(68, *[0, 0.9135351721603376, 0, -0.45676758608016876, 0, -0.4913481251287206])\n', 'ops.load(61, *[0, 1.5017109760782223, 0, -0.7508554880391111, 0, 0.6838674808999475])\n', 'ops.load(61, *[0, 0.5838652274992141, 0, 0.09731087124986883, 0, 0.26588767657389983])\n', 'ops.load(68, *[0, 0.35518247493593774, 0, 0.059197079155989506, 0, -0.19103615105004593])\n', 'ops.load(69, *[0, 0.010231593928195705, 0, -0.006577453239554367, 0, -0.005503099001441635])\n', 'ops.load(62, *[0, 0.01681916293207607, 0, -0.010812319027763166, 0, 0.007659315786079394])\n', 'ops.load(15, *[0, 0.5697869342822274, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.5697869342822279, 0, 0.0, 0, 0.0])\n', 'ops.load(21, *[0, 0.12661931872938303, 0, 0.0, 0, 0.0])\n', 'ops.load(20, *[0, 0.5469954569109322, 0, 0.09116590948515516, 0, 0.273497728455466])\n', 'ops.load(26, *[0, 0.5469954569109307, 0, 0.0911659094851549, 0, -0.27349772845546544])\n', 'ops.load(27, *[0, 0.01575707077521191, 0, -0.010129545498350498, 0, -0.00787853538760596])\n', 'ops.load(21, *[0, 0.015757070775211955, 0, -0.010129545498350526, 0, 0.007878535387605974])\n', 'ops.load(26, *[0, 0.5615079504058661, 0, 0.09358465840097775, 0, 0.2807539752029323])\n', 'ops.load(61, *[0, 0.5615079504058568, 0, 0.0935846584009762, 0, -0.28075397520292916])\n', 'ops.load(62, *[0, 0.016175126143378623, 0, -0.010398295377886262, 0, -0.008087563071689334])\n', 'ops.load(27, *[0, 0.01617512614337889, 0, -0.010398295377886436, 0, 0.008087563071689424])\n']


