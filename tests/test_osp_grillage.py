import pytest
import ospgrillage as og
import sys, os

sys.path.insert(0, os.path.abspath('../'))


# Fixtures
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

    example_bridge.create_osp_model(pyfile=False)
    return example_bridge


@pytest.fixture
def shell_bridge(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa", rho=2400)

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(bridge_name="Shell_10m", long_dim=10, width=7, skew=12,
                                        num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_shell_members(slab_shell)
    # set grillage member to element groups of grillage model

    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    # example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)
    return example_bridge


# This creates space gass model - see Influence of transverse member spacing to torsion and torsionless designs
# of Super-T decks T.M.T.Lui, C. Caprani, S. Zhang
@pytest.fixture
def beam_link_bridge(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa", rho=2400)

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(bridge_name="beamlink_10m", long_dim=10, width=7, skew=-12,
                                        num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho",
                                        model_type="beam_link",
                                        beam_width=1, web_thick=0.02, centroid_dist_y=0.499)

    example_bridge.set_member(I_beam, member="interior_main_beam")
    # example_bridge.set_shell_members(slab_shell)
    # set grillage member to element groups of grillage model

    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    example_bridge.create_osp_model(pyfile=False)
    return example_bridge

@pytest.fixture
def shell_link_bridge(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa", rho=2400)

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(bridge_name="shelllink_10m", long_dim=10, width=7, skew=12,
                                        num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Orth",
                                        model_type="shell",max_mesh_size_z=0.9,offset_beam_y_dist=0.6,
                                        link_nodes_width=0.5)


    # set shell
    #example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_shell_members(slab_shell)

    # set beams
    example_bridge.set_member(I_beam,member="offset_beam")
    example_bridge.create_osp_model(pyfile=False)



# --------------------------------
# test creating a basic beam grillage model
def test_model_instance(bridge_model_42_negative):
    example_bridge = bridge_model_42_negative
    #og.opsplt.plot_model("nodes")
    og.opsv.plot_model(az_el=(-90, 0))
    og.plt.show()
    assert og.ops.nodeCoord(18)  # check if model node exist in OpenSees model space
    og.ops.wipe()
    a = example_bridge.get_element(member="exterior_main_beam_2",options="nodes")
    print(a)

#  test creating shell model procedure successful
def test_create_shell_model(shell_bridge):
    shell_model = shell_bridge
    og.opsplt.plot_model("nodes")
    print(og.ops.eleNodes(195))
    assert og.ops.eleNodes(195)  # if element exist - for orthogonal mesh only


#  test creating beam model with rigid links
def test_create_beam_link_model(beam_link_bridge):
    beam_link_model = beam_link_bridge
    og.opsplt.plot_model("nodes")
    # print(og.ops.eleNodes(195))
    assert og.ops.eleNodes(195)


def test_create_shell_link_model(shell_link_bridge):
    shell_link_model = shell_link_bridge
    og.opsplt.plot_model("nodes")
