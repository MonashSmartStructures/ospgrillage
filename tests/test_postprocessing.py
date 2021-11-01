import pytest
import ospgrillage as og
import sys, os
from ospgrillage import __version__ as version

sys.path.insert(0, os.path.abspath("../"))


@pytest.fixture
def ref_bridge_properties():
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

    # define grillage members
    I_beam = og.create_member(
        member_name="Intermediate I-beams", section=I_beam_section, material=concrete
    )
    slab = og.create_member(
        member_name="concrete slab", section=slab_section, material=concrete
    )
    exterior_I_beam = og.create_member(
        member_name="exterior I beams",
        section=exterior_I_beam_section,
        material=concrete,
    )
    return I_beam, slab, exterior_I_beam, concrete


@pytest.fixture
def bridge_model_42_negative(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.OspGrillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=-42,
        num_long_grid=7,
        num_trans_grid=5,
        edge_beam_dist=1,
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

    pyfile = False
    example_bridge.create_osp_model(pyfile=pyfile)
    return example_bridge


def test_envelope(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    # create reference line load
    p = 10000
    p2 = 20000
    p3 = 30000  # duplicate of 2nd but with different mag
    barrierpoint_1 = og.create_load_vertex(x=5, z=1, p=p)
    barrierpoint_2 = og.create_load_vertex(x=10, z=7, p=p)
    barrierpoint_3 = og.create_load_vertex(x=10, z=2, p=p2)
    barrierpoint_4 = og.create_load_vertex(x=5, z=5, p=p2)
    barrierpoint_5 = og.create_load_vertex(x=10, z=2, p=p3)
    barrierpoint_6 = og.create_load_vertex(x=5, z=5, p=p3)
    # add moving load case
    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(2, 0, 2, 50)
    )  # Single point load 50 N
    Barrier = og.create_load(
        loadtype="line",
        name="Barrier curb load",
        point1=barrierpoint_1,
        point2=barrierpoint_2,
    )
    Barrier2 = og.create_load(
        loadtype="line", name="Barrieload", point1=barrierpoint_3, point2=barrierpoint_4
    )
    Barrier3 = og.create_load(
        loadtype="line", name="Barrieload", point1=barrierpoint_5, point2=barrierpoint_6
    )
    Patch1 = og.create_load(
        loadtype="patch",
        point1=barrierpoint_1,
        point2=barrierpoint_3,
        point3=barrierpoint_2,
        point4=barrierpoint_4,
    )

    barrierpoint_1 = og.create_load_vertex(x=6, z=2, p=0)
    barrierpoint_2 = og.create_load_vertex(x=11, z=8, p=0)
    barrierpoint_3 = og.create_load_vertex(x=11, z=3, p=0)
    barrierpoint_4 = og.create_load_vertex(x=6, z=6, p=0)

    Patch2 = og.create_load(
        loadtype="patch",
        point1=barrierpoint_1,
        point2=barrierpoint_3,
        point3=barrierpoint_2,
        point4=barrierpoint_4,
    )
    # create basic load case
    barrier_load_case = og.create_load_case(name="Barrier")
    # barrier_load_case.add_load_groups(Barrier)  # ch
    barrier_load_case.add_load(Patch1)  # ch
    # 2nd
    barrier_load_case2 = og.create_load_case(name="Barrier2")
    # barrier_load_case2.add_load_groups(Barrier2)
    barrier_load_case2.add_load(Patch2)
    # 3rd
    # barrier_load_case3 = og.create_load_case(name="Barrier3")
    # barrier_load_case3.add_load_groups(Barrier3)

    # adding load cases to model
    example_bridge.add_load_case(barrier_load_case)
    example_bridge.add_load_case(barrier_load_case2)
    # example_bridge.add_load_case(barrier_load_case3)

    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3), increments=3
    )  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_load(load_obj=front_wheel)
    example_bridge.add_load_case(move_point)

    example_bridge.analyze()
    results = example_bridge.get_results()
    comb_results = example_bridge.get_results(
        combinations={"Barrier": 1, "single_moving_point": 2}
    )
    # maxY = results.sel(Component='dy').max()
    envelope = og.create_envelope(
        ds=comb_results, load_effect="dy", array="displacements"
    )
    max_disp = envelope.get()
    print(max_disp)
    move_point.query(
        incremental_lc_name="single_moving_point at global position [2.00,0.00,2.00]"
    )
    # print(comb_results)
    print(og.ops.nodeDisp(25)[1])
