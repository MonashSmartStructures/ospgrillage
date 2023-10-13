from fixtures import *

sys.path.insert(0, os.path.abspath("../"))


def test_material_command(ref_bridge_properties):
    # test created material in creating model
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

    example_bridge.create_osp_model(pyfile=False)


def test_create_material():
    # test basic functionality of material module
    E = 1000
    G = 100
    v = 0.3
    rho = 1800

    # specific Concrete01 properties
    fpc = 10
    epsc0 = 10
    fpcu = 10
    epsU = 10

    concrete_code = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa"
    )
    assert concrete_code.density == 2.4e3

    concrete_custom = og.create_material(E=E, G=G, v=v, rho=rho)  # with complete inputs

    concrete_custom_wo_g = og.create_material(E=E, v=v, rho=rho)  # with missing G input
    expect_g = 384.615
    assert og.np.isclose(concrete_custom_wo_g.shear_modulus, expect_g, rtol=0.1)

    concrete_custom_wo_rho = og.create_material(
        E=E, rho=rho
    )  # with missing G and rho input
    expect_v = 0.3
    assert og.np.isclose(concrete_custom_wo_g.poisson_ratio, expect_v, rtol=0.1)
    # concrete_ops = og.create_material(fpc=fpc,epsc0=epsc0,fpcu=fpcu,epsU=epsU)
