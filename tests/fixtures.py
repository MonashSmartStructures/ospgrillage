import pytest

import ospgrillage
import ospgrillage as og
import sys, os
from typing import Union, Any
import numpy as np

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


@pytest.fixture
def ref_28m_bridge():
    pyfile = False
    # reference super T bridge 28m for validation purpose
    # Members
    concrete = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa"
    )
    # concrete = og.Material(loadtype="concrete", code="AS5100-2017", grade="50MPa")
    # define sections
    super_t_beam_section = og.create_section(
        A=1.0447, J=0.230698, Iy=0.231329, Iz=0.533953, Ay=0.397032, Az=0.434351
    )
    transverse_slab_section = og.create_section(
        A=0.5372,
        J=2.79e-3,
        Iy=0.3988 / 2,
        Iz=1.45e-3 / 2,
        Ay=0.447 / 2,
        Az=0.447 / 2,
        unit_width=True,
    )
    end_tranverse_slab_section = og.create_section(
        A=0.5372 / 2, J=2.68e-3, Iy=0.04985, Iz=0.725e-3, Ay=0.223, Az=0.223
    )
    edge_beam_section = og.create_section(
        A=0.039375, J=0.21e-3, Iy=0.1e-3, Iz=0.166e-3, Ay=0.0328, Az=0.0328
    )

    # define grillage members
    super_t_beam = og.create_member(
        member_name="Intermediate I-beams",
        section=super_t_beam_section,
        material=concrete,
    )
    transverse_slab = og.create_member(
        member_name="concrete slab", section=transverse_slab_section, material=concrete
    )
    edge_beam = og.create_member(
        member_name="exterior I beams", section=edge_beam_section, material=concrete
    )
    end_tranverse_slab = og.create_member(
        member_name="edge transverse",
        section=end_tranverse_slab_section,
        material=concrete,
    )

    bridge_28 = og.OspGrillage(
        bridge_name="SuperT_28m",
        long_dim=28,
        width=7,
        skew=0,
        num_long_grid=7,
        num_trans_grid=14,
        edge_beam_dist=1.0875,
        mesh_type="Ortho",
    )

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


@pytest.fixture
# A straight bridge with mesh where skew angle A is 42 and skew angle b is 0
def bridge_42_0_angle_mesh(ref_bridge_properties):
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties
    example_bridge = og.OspGrillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=[42, 0],
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


@pytest.fixture
def bridge_model_42_positive(ref_bridge_properties):
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.OspGrillage(
        bridge_name="SuperT_10m",
        long_dim=10,
        width=7,
        skew=42,
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


@pytest.fixture
def shell_link_bridge(
    ref_bridge_properties,
) -> Union[ospgrillage.OspGrillageShell, ospgrillage.OspGrillageBeam]:
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
    )

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="shelllink_10m",
        long_dim=10,
        width=7,
        skew=0,
        num_long_grid=7,
        num_trans_grid=11,
        edge_beam_dist=1,
        mesh_type="Orth",
        model_type="shell_beam",
        max_mesh_size_z=1,
        max_mesh_size_x=1,
        offset_beam_y_dist=0.499,
        beam_width=0.89,
    )

    # set beams
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(I_beam, member="exterior_main_beam_2")
    # set shell
    example_bridge.set_shell_members(slab_shell)

    example_bridge.create_osp_model(pyfile=False)
    return example_bridge


# equivalent model for shell_link_bridge but using beam element model type instead
@pytest.fixture
def beam_element_bridge(
    ref_bridge_properties,
) -> Union[ospgrillage.OspGrillageShell, ospgrillage.OspGrillageBeam]:
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="beamlink_10m",
        long_dim=10,
        width=7,
        skew=0,
        num_long_grid=7,
        num_trans_grid=11,
        edge_beam_dist=1,
        mesh_type="Ortho",
    )

    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")

    # example_bridge.create_osp_model(pyfile=False)
    # og.opsplt.plot_model()
    return example_bridge


@pytest.fixture
def bridge_model_42_negative_custom_spacing(
    ref_bridge_properties,
) -> Union[ospgrillage.OspGrillageShell, ospgrillage.OspGrillageBeam]:
    # reference bridge 10m long, 7m wide with common skew angle at both ends
    # define material
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
    return example_bridge


@pytest.fixture
def beam_link_bridge(
    ref_bridge_properties,
) -> Union[ospgrillage.OspGrillageShell, ospgrillage.OspGrillageBeam]:
    # reference bridge 10m long, 7m wide with common skew angle at both ends

    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    # create material of slab shell
    slab_shell_mat = og.create_material(
        material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
    )

    # create section of slab shell
    slab_shell_section = og.create_section(h=0.2)
    # shell elements for slab
    slab_shell = og.create_member(section=slab_shell_section, material=slab_shell_mat)

    # construct grillage model
    example_bridge = og.create_grillage(
        bridge_name="beamlink_10m",
        long_dim=10,
        width=7,
        skew=-12,
        num_long_grid=7,
        num_trans_grid=5,
        edge_beam_dist=1,
        mesh_type="Ortho",
        model_type="beam_link",
        beam_width=1,
        web_thick=0.02,
        centroid_dist_y=0.499,
    )

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


# create and run both comparable beam and shell_beam model to obtain results from a point load analysis
@pytest.fixture
def run_beam_model_point_load(beam_element_bridge, shell_link_bridge):
    # create point load
    P = 1 * kN
    lp1 = og.create_load_vertex(x=5, y=0, z=3.5, p=P)
    mid_point_line_load = og.create_load(
        name="unit load",
        point1=lp1,
    )
    mid_point_line_loadcase = og.create_load_case(name="line")
    mid_point_line_loadcase.add_load(mid_point_line_load)  # ch

    # run beam model

    shell_bridge = shell_link_bridge
    shell_bridge.create_osp_model()
    shell_bridge.add_load_case(mid_point_line_loadcase)
    shell_bridge.analyze()
    result_shell = shell_bridge.get_results()

    # run shell model
    og.ops.wipe()
    og.ops.wipeAnalysis()
    beam_bridge = beam_element_bridge
    beam_bridge.create_osp_model()
    beam_bridge.add_load_case(mid_point_line_loadcase)
    beam_bridge.analyze()
    og.opsv.plot_defo()
    result_beam = beam_bridge.get_results()

    return beam_bridge, result_beam, shell_bridge, result_shell
