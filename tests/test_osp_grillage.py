import pytest
import ospgrillage as og
import sys, os
sys.path.insert(0, os.path.abspath('../'))

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

# Fixtures
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
def shell_bridge(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(E=50e9,v=0.3,rho=2400)

    # create section of slab shell
    slab_shell_section = og.create_section(op_ele_type= "ElasticMembranePlateSection",h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section,material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.OspGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=-42,
                                    num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    # example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")
    example_bridge.set_shell_members(slab_shell)

    pyfile = False
    example_bridge.create_osp_model(pyfile=pyfile)
    return example_bridge

# --------------------------------
# Tests here
# test if model instance run is successful
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    # og.opsplt.plot_model("nodes")

    print(og.ops.nodeCoord(18))
    print("pass")
    og.ops.wipe()

def test_create_shell_model(shell_bridge):
    example_shell_bridge = shell_bridge