"""M1600 geometry and an independent simply supported influence-line benchmark.

Geometry: AS 5100.2:2017 Figure 7.2.4. The 30 m midspan example is
also worked in CIV4280/CIV5170, BridgeLoading, ex:m1600midspan.
"""

import numpy as np
import pytest

import ospgrillage as og


def vertices(vehicle):
    return [load.load_point_1 for load in vehicle.compound_load_obj_list]


@pytest.mark.parametrize("gap", [6.25, 8.75, 15.0, 30.0])
def test_m1600_clear_group_spacings(gap):
    points = vertices(og.create_load_model(model_type="M1600", gap=gap).create())
    x = np.unique([p.x for p in points])
    # Dimensions between successive axles, read directly from Figure 7.2.4.
    np.testing.assert_allclose(
        np.diff(x), [1.25, 1.25, 3.75, 1.25, 1.25, gap, 1.25, 1.25, 5, 1.25, 1.25]
    )
    assert len(points) == 24
    assert sum(p.p for p in points) == pytest.approx(1440e3)
    assert sorted({p.z for p in points}) == [-1, 1]
    assert all(p.p == 60e3 for p in points)


def test_m1600_default_is_minimum_clear_gap():
    points = vertices(og.create_load_model(model_type="M1600").create())
    np.testing.assert_allclose(
        np.unique([p.x for p in points]),
        [0, 1.25, 2.5, 6.25, 7.5, 8.75, 15, 16.25, 17.5, 22.5, 23.75, 25],
    )


@pytest.mark.parametrize("gap", [0, -1, 5.0, 6.249, np.nan, np.inf, -np.inf])
def test_m1600_rejects_invalid_clear_gap(gap):
    with pytest.raises(ValueError, match="gap"):
        og.create_load_model(model_type="M1600", gap=gap).create()


def test_m1600_direct_generator_rejects_invalid_gap():
    with pytest.raises(ValueError, match="gap"):
        og.LoadModel(model_type="M1600").create_m1600_vehicle(0)


def test_m1600_gap_and_wheel_track_convert_with_geometry():
    origin = og.Point(10, 0, 20)
    points = vertices(
        og.create_load_model(
            model_type="M1600", gap=10, units="imperial", origin=origin
        ).create()
    )
    x = np.unique([p.x for p in points])
    np.testing.assert_allclose(
        np.diff(x) / 3.28084,
        [1.25, 1.25, 3.75, 1.25, 1.25, 10, 1.25, 1.25, 5, 1.25, 1.25],
    )
    assert x[0] == pytest.approx(origin.x)
    np.testing.assert_allclose(
        sorted({p.z for p in points}), [20 - 3.28084, 20 + 3.28084]
    )


def test_m1600_30m_midspan_influence_line():
    points = vertices(og.create_load_model(model_type="M1600", gap=6.25).create())
    x = np.array([p.x for p in points])
    loads = np.array([p.p for p in points])
    # The response is piecewise linear in translation. Its exact maximum
    # occurs when an axle crosses a support or the midspan influence-line peak.
    shifts = np.unique(np.concatenate([-x, 15 - x, 30 - x]))
    positions = shifts[:, None] + x
    ordinates = np.where(
        (positions >= 0) & (positions <= 30),
        np.minimum(positions, 30 - positions) / 2,
        0,
    )
    axle_moment = np.max(ordinates @ loads)
    lane_udl_moment = 6e3 * 30**2 / 8
    assert axle_moment == pytest.approx(5250e3)
    assert axle_moment + lane_udl_moment == pytest.approx(5925e3)
    assert 1.8 * 1.3 * (axle_moment + lane_udl_moment) == pytest.approx(13864.5e3)


def test_m1600_30m_grillage_recovers_total_midspan_moment():
    """Run the generated wheel loads through OpenSees and sum girder moments."""
    material = og.create_material(E=30e9, G=12.5e9, rho=2400)
    section = og.create_section(A=1, Iz=1, Iy=1, J=0.1)
    member = og.create_member(section=section, material=material)
    grid = og.create_grillage(
        bridge_name="M1600 benchmark",
        long_dim=30,
        width=4,
        skew=0,
        num_long_grid=5,
        num_trans_grid=7,
        edge_beam_dist=1,
        mesh_type="Ortho",
    )
    for name in (
        "edge_beam",
        "exterior_main_beam_1",
        "interior_main_beam",
        "exterior_main_beam_2",
        "transverse_slab",
        "start_edge",
        "end_edge",
    ):
        grid.set_member(member, member=name)
    grid.create_osp_model(pyfile=False)
    # Axle 6 at midspan gives the independent influence-line maximum.
    vehicle = og.create_load_model(
        model_type="M1600", gap=6.25, origin=og.Point(6.25, 0, 2)
    ).create()
    case = og.create_load_case(name="M1600 axles")
    case.add_load(vehicle)
    grid.add_load_case(case)
    grid.analyze()
    results = grid.get_results()
    nodes = grid.get_nodes()
    moments = []
    for element in results.Element.values:
        node_i, node_j = results.ele_nodes.sel(Element=element).values
        start = nodes[int(node_i)]["coordinate"]
        end = nodes[int(node_j)]["coordinate"]
        if np.isclose(start[0], 15) and end[0] > start[0]:
            moments.append(
                float(results.forces.sel(Element=element, Component="Mz_i").item())
            )
    assert len(moments) == 5
    assert np.all(np.isfinite(moments))
    assert abs(sum(moments)) == pytest.approx(5250e3, rel=1e-8)
