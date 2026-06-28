import csv
import json

from ospgrillage import __version__ as version
import ospgrillage.osp_grillage as og_model
from fixtures import *
import xarray as xr

sys.path.insert(0, os.path.abspath("../"))


def test_influence_line_from_loadcase_positions():
    ds = xr.Dataset(
        data_vars={
            "displacements": (
                ["Loadcase", "Node", "Component"],
                np.array(
                    [
                        [[1.0, 10.0], [2.0, 20.0]],
                        [[3.0, 30.0], [4.0, 40.0]],
                        [[5.0, 50.0], [6.0, 60.0]],
                    ]
                ),
            )
        },
        coords={
            "Loadcase": [
                "100 kN axle at global position [0.00,0.00,2.00]",
                "100 kN axle at global position [1.00,0.00,2.00]",
                "100 kN axle at global position [2.00,0.00,2.00]",
            ],
            "Node": [1, 2],
            "Component": ["x", "y"],
        },
    )

    influence_line = og.create_influence_line(
        ds=ds,
        array="displacements",
        load_effect="y",
        node=2,
    ).get()

    assert influence_line.dims == ("x",)
    assert np.allclose(influence_line.coords["x"].values, [0.0, 1.0, 2.0])
    assert np.allclose(influence_line.coords["z"].values, [2.0, 2.0, 2.0])
    assert np.allclose(influence_line.values, [20.0, 40.0, 60.0])


def test_influence_surface_from_explicit_positions():
    ds = xr.Dataset(
        data_vars={
            "forces": (
                ["Loadcase", "Element", "Component"],
                np.array(
                    [
                        [[10.0]],
                        [[11.0]],
                        [[12.0]],
                        [[13.0]],
                    ]
                ),
            )
        },
        coords={
            "Loadcase": ["case_a", "case_b", "case_c", "case_d"],
            "Element": [42],
            "Component": ["Mz_i"],
        },
    )

    influence_surface = og.create_influence_surface(
        ds=ds,
        array="forces",
        load_effect="Mz_i",
        element=42,
        values=[
            (0.0, 0.0, 2.0),
            (1.0, 0.0, 2.0),
            (0.0, 0.0, 3.0),
            (1.0, 0.0, 3.0),
        ],
    ).get()

    assert influence_surface.dims == ("x", "z")
    assert np.allclose(influence_surface.coords["x"].values, [0.0, 1.0])
    assert np.allclose(influence_surface.coords["z"].values, [2.0, 3.0])
    assert influence_surface.sel(x=0.0, z=2.0).item() == 10.0
    assert influence_surface.sel(x=1.0, z=2.0).item() == 11.0
    assert influence_surface.sel(x=0.0, z=3.0).item() == 12.0
    assert influence_surface.sel(x=1.0, z=3.0).item() == 13.0


def test_influence_surface_sorts_unsorted_positions():
    ds = xr.Dataset(
        data_vars={
            "forces": (
                ["Loadcase", "Element", "Component"],
                np.array(
                    [
                        [[13.0]],
                        [[10.0]],
                        [[11.0]],
                        [[12.0]],
                    ]
                ),
            )
        },
        coords={
            "Loadcase": ["case_d", "case_a", "case_b", "case_c"],
            "Element": [42],
            "Component": ["Mz_i"],
        },
    )

    influence_surface = og.create_influence_surface(
        ds=ds,
        array="forces",
        load_effect="Mz_i",
        element=42,
        values=[
            (1.0, 0.0, 3.0),
            (0.0, 0.0, 2.0),
            (1.0, 0.0, 2.0),
            (0.0, 0.0, 3.0),
        ],
    ).get()

    assert np.allclose(influence_surface.coords["x"].values, [0.0, 1.0])
    assert np.allclose(influence_surface.coords["z"].values, [2.0, 3.0])
    assert influence_surface.sel(x=0.0, z=2.0).item() == 10.0
    assert influence_surface.sel(x=1.0, z=2.0).item() == 11.0
    assert influence_surface.sel(x=0.0, z=3.0).item() == 12.0
    assert influence_surface.sel(x=1.0, z=3.0).item() == 13.0


def test_influence_line_station_uses_cumulative_path_distance():
    ds = xr.Dataset(
        data_vars={
            "displacements": (
                ["Loadcase", "Node", "Component"],
                np.array([[[1.0]], [[2.0]], [[3.0]]]),
            )
        },
        coords={
            "Loadcase": ["a", "b", "c"],
            "Node": [25],
            "Component": ["y"],
        },
    )

    il = og.create_influence_line(
        ds=ds,
        array="displacements",
        component="y",
        node=25,
        load_coord="station",
        values=[
            (0.0, 0.0, 0.0),
            (3.0, 0.0, 4.0),
            (6.0, 0.0, 8.0),
        ],
    ).get()

    assert il.dims == ("station",)
    assert np.allclose(il.coords["station"].values, [0.0, 5.0, 10.0])
    assert np.allclose(il.coords["x"].values, [0.0, 3.0, 6.0])
    assert np.allclose(il.coords["z"].values, [0.0, 4.0, 8.0])


def test_plot_influence_line_matplotlib():
    il = xr.DataArray(
        data=np.array([1.0, 2.0, 3.0]),
        dims=("x",),
        coords={"x": [0.0, 1.0, 2.0], "z": ("x", [2.0, 2.0, 2.0])},
    )

    ax = og.plot_il(il, title="IL", show=False)

    assert ax.get_title() == "IL"
    assert len(ax.lines) == 1


def test_plot_influence_line_overlay_matplotlib():
    il_a = xr.DataArray(data=np.array([1.0, 2.0, 3.0]), dims=("x",), coords={"x": [0.0, 1.0, 2.0]})
    il_b = xr.DataArray(data=np.array([3.0, 2.0, 1.0]), dims=("x",), coords={"x": [0.0, 1.0, 2.0]})

    ax = og.plot_il({"Lane 1": il_a, "Lane 2": il_b}, title="Overlay", show=False)

    assert ax.get_title() == "Overlay"
    assert len(ax.lines) == 2
    assert ax.get_legend() is not None


def test_plot_influence_surface_matplotlib():
    isurface = xr.DataArray(
        data=np.array([[10.0, 11.0], [12.0, 13.0]]),
        dims=("x", "z"),
        coords={"x": [0.0, 1.0], "z": [2.0, 3.0]},
    )

    ax = og.plot_is(isurface, title="IS", show=False)

    assert ax.get_title() == "IS"
    assert len(ax.collections) > 0


def test_plot_influence_surface_matplotlib_surface3d():
    isurface = xr.DataArray(
        data=np.array([[10.0, 11.0], [12.0, 13.0]]),
        dims=("x", "z"),
        coords={"x": [0.0, 1.0], "z": [2.0, 3.0]},
    )

    ax = og.plot_is(isurface, title="IS 3D", view="surface3d", show=False)

    assert ax.get_title() == "IS 3D"
    assert hasattr(ax, "plot_surface")


def _build_curved_influence_surface():
    data = np.array(
        [
            [10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0],
            [16.0, 17.0, np.nan],
        ]
    )
    x_phys = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 1.1, 1.2],
            [2.0, 2.2, np.nan],
        ]
    )
    z_phys = np.array(
        [
            [0.0, 1.0, 2.0],
            [0.2, 1.2, 2.2],
            [0.5, 1.5, np.nan],
        ]
    )
    return xr.DataArray(
        data=data,
        dims=("longitudinal_station", "transverse_station"),
        coords={
            "longitudinal_station": [0.0, 1.0, 2.0],
            "transverse_station": [0.0, 1.0, 2.0],
            "x": (("longitudinal_station", "transverse_station"), x_phys),
            "z": (("longitudinal_station", "transverse_station"), z_phys),
        },
    )


def test_plot_influence_surface_curved_physical_matplotlib():
    isurface = _build_curved_influence_surface()

    ax = og.plot_is(
        isurface,
        coordinate_space="physical",
        title="Curved IS",
        show=False,
    )

    assert ax.get_title() == "Curved IS"
    assert len(ax.collections) > 0


def test_plot_influence_line_plotly():
    go = pytest.importorskip("plotly.graph_objects")
    il = xr.DataArray(
        data=np.array([1.0, 2.0, 3.0]),
        dims=("x",),
        coords={"x": [0.0, 1.0, 2.0]},
    )

    fig = og.plot_il(il, backend="plotly", title="IL", show=False)

    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "IL"


def test_plot_influence_line_overlay_plotly():
    go = pytest.importorskip("plotly.graph_objects")
    il_a = xr.DataArray(data=np.array([1.0, 2.0, 3.0]), dims=("x",), coords={"x": [0.0, 1.0, 2.0]})
    il_b = xr.DataArray(data=np.array([3.0, 2.0, 1.0]), dims=("x",), coords={"x": [0.0, 1.0, 2.0]})

    fig = og.plot_il({"Lane 1": il_a, "Lane 2": il_b}, backend="plotly", title="Overlay", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2


def test_plot_model_proxy_includes_shell_mesh_when_available():
    go = pytest.importorskip("plotly.graph_objects")
    ds = xr.Dataset(
        data_vars={
            "node_coordinates": (
                ("Node", "Axis"),
                np.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.0],
                        [1.0, 0.0, 1.0],
                        [0.0, 0.0, 1.0],
                    ]
                ),
            ),
            "ele_nodes_shell": (
                ("Element", "Nodes"),
                np.array([[1.0, 2.0, 3.0, 4.0]]),
            ),
        },
        coords={
            "Node": [1, 2, 3, 4],
            "Axis": ["x", "y", "z"],
            "Element": [1],
            "Nodes": [0, 1, 2, 3],
        },
        attrs={
            "member_elements": "{}",
            "model_type": "shell_beam",
        },
    )
    proxy = og.model_proxy_from_results(ds)
    fig = og.plot_model(proxy, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert any(trace.type == "mesh3d" and trace.name == "shell_slab" for trace in fig.data)


def test_plot_model_proxy_prefers_ele_nodes_connectivity_over_node_order():
    go = pytest.importorskip("plotly.graph_objects")
    member_elements = {
        "interior_main_beam": {
            "elements": [[1, 2]],
            "nodes": [[[1, 3, 2]]],  # intentionally misordered
        }
    }
    ds = xr.Dataset(
        data_vars={
            "node_coordinates": (
                ("Node", "Axis"),
                np.array(
                    [
                        [0.0, 0.0, 0.0],  # node 1
                        [1.0, 0.0, 0.0],  # node 2
                        [2.0, 0.0, 0.0],  # node 3
                    ]
                ),
            ),
            "ele_nodes": (
                ("Element", "Nodes"),
                np.array(
                    [
                        [1, 2],  # element 1
                        [2, 3],  # element 2
                    ]
                ),
            ),
        },
        coords={
            "Node": [1, 2, 3],
            "Axis": ["x", "y", "z"],
            "Element": [1, 2],
            "Nodes": [0, 1],
        },
        attrs={
            "member_elements": json.dumps(member_elements),
            "model_type": "beam_only",
        },
    )
    proxy = og.model_proxy_from_results(ds)
    fig = og.plot_model(proxy, backend="plotly", show=False, show_nodes=True)
    assert isinstance(fig, go.Figure)
    trace = next(t for t in fig.data if getattr(t, "name", "") == "interior_main_beam")
    assert list(trace.x[:6]) == [0.0, 1.0, None, 1.0, 2.0, None]
    non_null_text = [txt for txt in trace.text if txt is not None]
    assert any("element:" in txt for txt in non_null_text)
    assert any("nodes:" in txt for txt in non_null_text)
    node_trace = next(t for t in fig.data if getattr(t, "name", "") == "nodes")
    assert "node:" in str(node_trace.hovertemplate)
    assert set(node_trace.text) == {"1", "2", "3"}


def test_plot_model_plotly_member_filter_limits_visible_members():
    go = pytest.importorskip("plotly.graph_objects")
    member_elements = {
        "interior_main_beam": {
            "elements": [[1]],
            "nodes": [[[1, 2]]],
        },
        "transverse_slab": {
            "elements": [[2]],
            "nodes": [[[2, 3]]],
        },
    }
    ds = xr.Dataset(
        data_vars={
            "node_coordinates": (
                ("Node", "Axis"),
                np.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.0],
                        [2.0, 0.0, 0.0],
                    ]
                ),
            ),
            "ele_nodes": (
                ("Element", "Nodes"),
                np.array(
                    [
                        [1, 2],
                        [2, 3],
                    ]
                ),
            ),
        },
        coords={
            "Node": [1, 2, 3],
            "Axis": ["x", "y", "z"],
            "Element": [1, 2],
            "Nodes": [0, 1],
        },
        attrs={
            "member_elements": json.dumps(member_elements),
            "model_type": "beam_only",
        },
    )
    proxy = og.model_proxy_from_results(ds)
    fig = og.plot_model(
        proxy,
        backend="plotly",
        show=False,
        show_nodes=True,
        members=og.Members.INTERIOR_MAIN_BEAM,
    )
    assert isinstance(fig, go.Figure)
    names = {getattr(t, "name", "") for t in fig.data}
    assert "interior_main_beam" in names
    assert "transverse_slab" not in names
    node_trace = next(t for t in fig.data if getattr(t, "name", "") == "nodes")
    assert set(node_trace.text) == {"1", "2"}


def test_plot_influence_surface_plotly():
    go = pytest.importorskip("plotly.graph_objects")
    isurface = xr.DataArray(
        data=np.array([[10.0, 11.0], [12.0, 13.0]]),
        dims=("x", "z"),
        coords={"x": [0.0, 1.0], "z": [2.0, 3.0]},
    )

    fig = og.plot_is(isurface, backend="plotly", title="IS", show=False)

    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "IS"


def test_plot_influence_surface_plotly_surface3d():
    go = pytest.importorskip("plotly.graph_objects")
    isurface = xr.DataArray(
        data=np.array([[10.0, 11.0], [12.0, 13.0]]),
        dims=("x", "z"),
        coords={"x": [0.0, 1.0], "z": [2.0, 3.0]},
    )

    fig = og.plot_is(isurface, backend="plotly", title="IS 3D", view="surface3d", show=False)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "surface"


def test_normalise_netcdf_filename_semantic_suffixes():
    assert og_model._normalise_netcdf_filename("results", file_tag="res") == "results.res.nc"
    assert og_model._normalise_netcdf_filename("lane", file_tag="il") == "lane.il.nc"
    assert og_model._normalise_netcdf_filename("surface", file_tag="is") == "surface.is.nc"
    assert og_model._normalise_netcdf_filename("already.nc", file_tag="res") == "already.nc"
    assert og_model._normalise_netcdf_filename("bridge.res", file_tag="res") == "bridge.res.nc"


def test_plot_influence_surface_curved_physical_plotly_contour():
    go = pytest.importorskip("plotly.graph_objects")
    isurface = _build_curved_influence_surface()

    fig = og.plot_is(
        isurface,
        backend="plotly",
        coordinate_space="physical",
        title="Curved IS",
        show=False,
    )

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "mesh3d"


def test_plot_influence_surface_curved_physical_plotly_surface3d():
    go = pytest.importorskip("plotly.graph_objects")
    isurface = _build_curved_influence_surface()

    fig = og.plot_is(
        isurface,
        backend="plotly",
        coordinate_space="physical",
        title="Curved IS 3D",
        view="surface3d",
        show=False,
    )

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "mesh3d"


def test_plot_influence_surface_plotly_overlay_on_model(bridge_model_42_negative):
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    iss = example_bridge.analyze_influence_surfaces(name="Deck IS Default")
    isurface = iss.get_surface(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
    )
    proxy = og.model_proxy_from_results(iss.dataset)
    model_fig = og.plot_model(proxy, backend="plotly", show=False, show_nodes=False)
    fig = og.plot_is(
        isurface,
        backend="plotly",
        show=False,
        ax=model_fig,
        coordinate_space="physical",
        opacity=0.6,
    )
    assert isinstance(fig, go.Figure)
    assert any(trace.type == "scatter3d" for trace in fig.data)
    assert any(trace.type == "mesh3d" for trace in fig.data)
    assert fig.layout.scene.aspectmode == "manual"
    is_trace = next(
        trace
        for trace in fig.data
        if trace.type == "mesh3d" and getattr(trace, "name", "") == "Influence Surface"
    )
    assert float(is_trace.colorbar.x) < 0.0
    assert getattr(is_trace, "hoverinfo", None) == "skip"


def test_analyze_influence_line_separate_results(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    result_set = example_bridge.analyze_influence_line(
        name="Lane IL",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )
    influence_results = example_bridge.get_influence_results("Lane IL")

    assert result_set.kind == "line"
    assert influence_results.attrs["influence_type"] == "line"
    assert influence_results.attrs["shape_function"] == "linear"
    assert "Lane IL" in example_bridge.influence_result_set
    assert influence_results.sizes["Loadcase"] == 3
    assert np.allclose(influence_results.coords["load_position_x"].values, [2.0, 3.0, 4.0])
    assert "node_coordinates" in influence_results
    assert influence_results.attrs["model_type"] == example_bridge.model_type


def test_analyze_influence_lines_returns_result_object(bridge_model_42_negative, tmp_path):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    ils = example_bridge.analyze_influence_lines(
        name="Lane IL",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )

    assert isinstance(ils, og.InfluenceLineResults)
    assert ils.dataset.attrs["influence_type"] == "line"
    assert ils.dataset.attrs["influence_name"] == "Lane IL"
    assert np.allclose(ils.dataset.coords["load_position_x"].values, [2.0, 3.0, 4.0])

    save_path = tmp_path / "lane_il.nc"
    assert ils.save(save_path.as_posix()) == save_path.as_posix()
    assert save_path.exists()

    stem_path = tmp_path / "lane_il_export"
    saved = ils.to_netcdf(stem_path.as_posix())
    assert saved.endswith(".il.nc")
    assert os.path.exists(saved)


def test_analyze_influence_lines_combines_named_paths(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    path_1 = og.Path(
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )
    path_2 = og.Path(
        start_point=og.Point(2, 0, 4),
        end_point=og.Point(4, 0, 4),
        increments=3,
    )

    ils = example_bridge.analyze_influence_lines(
        paths={"Lane 1": path_1, "Lane 2": path_2}
    )

    assert isinstance(ils, og.InfluenceLineResults)
    assert "InfluenceLine" in ils.dataset.dims
    assert list(ils.dataset.coords["InfluenceLine"].values) == ["Lane 1", "Lane 2"]

    overlay = ils.get_line(array="displacements", component="y", node=25)
    assert sorted(overlay) == ["Lane 1", "Lane 2"]
    ax = ils.plot(array="displacements", component="y", node=25, show=False)
    assert len(ax.lines) == 2
    go = pytest.importorskip("plotly.graph_objects")
    fig = ils.plot(
        array="displacements",
        component="y",
        node=25,
        backend="plotly",
        view="path",
        show=False,
    )
    assert isinstance(fig, go.Figure)
    assert any(trace.type == "scatter3d" for trace in fig.data)
    assert any(trace.type == "mesh3d" for trace in fig.data)
    lane_2_trace = next(trace for trace in fig.data if getattr(trace, "name", "") == "Lane 2")
    lane_2_base = next(trace for trace in fig.data if getattr(trace, "name", "") == "Lane 2 baseline")
    assert lane_2_trace.mode == "lines"
    assert lane_2_base.mode == "lines+markers"
    assert np.allclose(np.asarray(lane_2_trace.y, dtype=float), [4.0, 4.0, 4.0])
    assert np.allclose(np.asarray(lane_2_base.z, dtype=float), [0.0, 0.0, 0.0])


def test_plot_il_path_fill_ignores_noise_and_gaps(bridge_model_42_negative):
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    ils = example_bridge.analyze_influence_lines(
        name="Lane IL",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(8, 0, 2),
        increments=7,
    )
    il = ils.get_line(array="displacements", component="y", node=25)
    il_with_noise = il.copy(
        data=np.asarray([1e-13, -1e-13, 5e-14, np.nan, np.nan, 0.1, -0.2], dtype=float)
    )
    x_vals = np.asarray(il_with_noise.coords["x"].values, dtype=float)

    fig = og.plot_il(
        il_with_noise,
        backend="plotly",
        view="path",
        dataset=ils.dataset,
        show=False,
    )

    mesh_traces = [trace for trace in fig.data if isinstance(trace, go.Mesh3d)]
    assert len(mesh_traces) == 1
    x_mesh = np.asarray(mesh_traces[0].x, dtype=float)
    expected_min = min(x_vals[5], x_vals[6]) - 1e-9
    expected_max = max(x_vals[5], x_vals[6]) + 1e-9
    assert np.nanmin(x_mesh) >= expected_min
    assert np.nanmax(x_mesh) <= expected_max


def test_get_combined_influence_line_results(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    example_bridge.analyze_influence_line(
        name="Lane 1",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )
    example_bridge.analyze_influence_line(
        name="Lane 2",
        start_point=og.Point(2, 0, 4),
        end_point=og.Point(4, 0, 4),
        increments=3,
    )

    combined = example_bridge.get_influence_results(names=["Lane 1", "Lane 2"])

    assert combined.attrs["influence_type"] == "line"
    assert combined.attrs["influence_overlay"] == "multi"
    assert "InfluenceLine" in combined.dims
    assert list(combined.coords["InfluenceLine"].values) == ["Lane 1", "Lane 2"]
    assert "loadcase_label" in combined.coords
    assert np.allclose(
        combined.sel(InfluenceLine="Lane 1").coords["load_position_z"].values[:3],
        [2.0, 2.0, 2.0],
        equal_nan=False,
    )


def test_create_influence_line_from_combined_results(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    example_bridge.analyze_influence_line(
        name="Lane 1",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )
    example_bridge.analyze_influence_line(
        name="Lane 2",
        start_point=og.Point(2, 0, 4),
        end_point=og.Point(4, 0, 4),
        increments=3,
    )

    combined = example_bridge.get_influence_results(names=["Lane 1", "Lane 2"])

    with pytest.raises(ValueError, match="multiple InfluenceLine studies"):
        og.create_influence_line(
            ds=combined,
            array="displacements",
            component="y",
            node=25,
        ).get()

    il_lane_1 = og.create_influence_line(
        ds=combined,
        array="displacements",
        component="y",
        node=25,
        influence_line="Lane 1",
    ).get()
    il_lane_2 = og.create_influence_line(
        ds=combined,
        array="displacements",
        component="y",
        node=25,
        influence_line="Lane 2",
    ).get()

    assert list(il_lane_1.coords["x"].values) == [2.0, 3.0, 4.0]
    assert list(il_lane_2.coords["z"].values) == [4.0, 4.0, 4.0]


def test_analyze_influence_line_preserves_hermite_shape_function(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    example_bridge.analyze_influence_line(
        name="Lane IL Hermite",
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
        shape_function="hermite",
    )
    influence_results = example_bridge.get_influence_results("Lane IL Hermite")

    assert influence_results.attrs["shape_function"] == "hermite"


def test_analyze_influence_surface_separate_results(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    result_set = example_bridge.analyze_influence_surface(
        name="Deck IS",
        x=[2, 4],
        z=[2, 3],
    )
    influence_results = example_bridge.get_influence_results("Deck IS")

    assert result_set.kind == "surface"
    assert influence_results.attrs["influence_type"] == "surface"
    assert influence_results.attrs["shape_function"] == "linear"
    assert "Deck IS" in example_bridge.influence_result_set
    assert influence_results.sizes["Loadcase"] == 4
    assert np.allclose(influence_results.coords["load_position_x"].values, [2.0, 2.0, 4.0, 4.0])
    assert np.allclose(influence_results.coords["load_position_z"].values, [2.0, 3.0, 2.0, 3.0])


def test_analyze_influence_surfaces_returns_result_object(bridge_model_42_negative, tmp_path):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    iss = example_bridge.analyze_influence_surfaces(
        name="Deck IS",
        x=[2, 4],
        z=[2, 3],
    )

    assert isinstance(iss, og.InfluenceSurfaceResults)
    assert iss.dataset.attrs["influence_type"] == "surface"
    assert iss.dataset.attrs["influence_name"] == "Deck IS"

    isurface = iss.get_surface(array="forces", component="Mz_i", element=1)
    assert isurface.dims == ("x", "z")
    ax = iss.plot(array="forces", component="Mz_i", element=1, show=False)
    assert len(ax.collections) > 0

    save_path = tmp_path / "deck_is.nc"
    assert iss.to_netcdf(save_path.as_posix()) == save_path.as_posix()
    assert save_path.exists()

    stem_path = tmp_path / "deck_is_export"
    saved = iss.to_netcdf(stem_path.as_posix())
    assert saved.endswith(".is.nc")
    assert os.path.exists(saved)


def test_analyze_influence_surfaces_defaults_to_mesh_station_grid(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    iss = example_bridge.analyze_influence_surfaces(name="Deck IS Default")

    longitudinal = iss.dataset.coords["load_position_longitudinal_station"].values
    transverse = iss.dataset.coords["load_position_transverse_station"].values

    assert np.all(np.isin(np.unique(longitudinal), np.asarray(example_bridge.Mesh_obj.nox)))
    assert np.all(np.isin(np.unique(transverse), np.asarray(example_bridge.Mesh_obj.noz)))
    assert len(longitudinal) == iss.dataset.sizes["Loadcase"]

    station_surface = iss.get_surface(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
    )
    assert station_surface.dims == ("longitudinal_station", "transverse_station")


@pytest.mark.parametrize(
    "bridge_fixture",
    ["bridge_model_42_negative", "bridge_42_0_angle_mesh"],
)
def test_influence_surface_station_mapping_preserves_longitudinal_order(request, bridge_fixture):
    og.ops.wipeAnalysis()
    example_bridge = request.getfixturevalue(bridge_fixture)

    iss = example_bridge.analyze_influence_surfaces(name="Deck IS Station Ordering")
    station_surface = iss.get_surface(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
    )

    transverse_stations = np.asarray(
        station_surface.coords["transverse_station"].values,
        dtype=float,
    )
    longitudinal_stations = np.asarray(
        station_surface.coords["longitudinal_station"].values,
        dtype=float,
    )
    assert transverse_stations.size > 0
    assert longitudinal_stations.size > 1

    first_transverse = float(transverse_stations[0])
    x_line = np.asarray(
        station_surface.sel(transverse_station=first_transverse).coords["x"].values,
        dtype=float,
    )
    finite = np.isfinite(x_line)
    assert np.count_nonzero(finite) == longitudinal_stations.size
    assert np.all(np.diff(x_line[finite]) >= -1e-9)


@pytest.mark.parametrize("mesh_radius", [20.0, 1000.0])
def test_analyze_influence_surfaces_curved_mesh_station_mapping(ref_bridge_properties, mesh_radius):
    og.ops.wipeAnalysis()
    I_beam, slab, exterior_I_beam, _ = ref_bridge_properties

    example_bridge = og.create_grillage(
        bridge_name=f"Curved IS R={mesh_radius:g}",
        long_dim=10,
        width=7,
        skew=0,
        num_long_grid=7,
        num_trans_grid=7,
        mesh_type="Ortho",
        mesh_radius=mesh_radius,
    )
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")
    example_bridge.create_osp_model(pyfile=False)

    iss = example_bridge.analyze_influence_surfaces(name="Curved Deck IS")
    station_surface = iss.get_surface(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
    )

    longitudinal_stations = np.asarray(
        station_surface.coords["longitudinal_station"].values,
        dtype=float,
    )
    transverse_stations = np.asarray(
        station_surface.coords["transverse_station"].values,
        dtype=float,
    )
    assert station_surface.shape == (len(longitudinal_stations), len(transverse_stations))
    assert len(longitudinal_stations) == len(np.asarray(example_bridge.Mesh_obj.nox, dtype=float))
    assert len(transverse_stations) == len(np.asarray(example_bridge.Mesh_obj.noz, dtype=float))

    for z_station in transverse_stations:
        x_line = np.asarray(
            station_surface.sel(transverse_station=float(z_station)).coords["x"].values,
            dtype=float,
        )
        finite = np.isfinite(x_line)
        assert np.count_nonzero(finite) == len(longitudinal_stations)
        assert np.all(np.diff(x_line[finite]) >= -1e-9)

    for longitudinal_station in longitudinal_stations:
        z_line = np.asarray(
            station_surface.sel(longitudinal_station=float(longitudinal_station)).coords["z"].values,
            dtype=float,
        )
        finite = np.isfinite(z_line)
        assert np.count_nonzero(finite) == len(transverse_stations)
        assert np.all(np.diff(z_line[finite]) >= -1e-9)


def test_influence_line_results_to_csv_combined_paths(bridge_model_42_negative, tmp_path):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    path_1 = og.Path(
        start_point=og.Point(2, 0, 2),
        end_point=og.Point(4, 0, 2),
        increments=3,
    )
    path_2 = og.Path(
        start_point=og.Point(2, 0, 4),
        end_point=og.Point(4, 0, 4),
        increments=3,
    )
    ils = example_bridge.analyze_influence_lines(paths={"Lane 1": path_1, "Lane 2": path_2})

    csv_file = tmp_path / "lane_ils.csv"
    assert (
        ils.to_csv(
            csv_file.as_posix(),
            array="displacements",
            component="y",
            node=25,
            load_coord="x",
        )
        == csv_file.as_posix()
    )
    assert csv_file.exists()

    with open(csv_file, newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 6
    assert {row["influence_line"] for row in rows} == {"Lane 1", "Lane 2"}
    assert all("x" in row and "ordinate" in row for row in rows)

    lane_1_x = sorted(
        [float(row["x"]) for row in rows if row["influence_line"] == "Lane 1"]
    )
    assert lane_1_x == [2.0, 3.0, 4.0]


def test_influence_surface_results_to_csv_grid_and_points(bridge_model_42_negative, tmp_path):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    iss = example_bridge.analyze_influence_surfaces(name="Deck IS Default")

    grid_file = tmp_path / "deck_is_grid.csv"
    exported = iss.to_csv(
        grid_file.as_posix(),
        array="forces",
        component="Mz_i",
        element=1,
        include_physical_coords=True,
    )

    assert isinstance(exported, dict)
    assert exported["grid"] == grid_file.as_posix()
    points_file = tmp_path / "deck_is_grid_points.csv"
    assert exported["points"] == points_file.as_posix()
    assert grid_file.exists()
    assert points_file.exists()

    with open(grid_file, newline="") as fh:
        grid_rows = list(csv.reader(fh))
    assert grid_rows[0][0] == "longitudinal_station"
    assert len(grid_rows) > 1

    with open(points_file, newline="") as fh:
        point_rows = list(csv.reader(fh))
    assert point_rows[0] == [
        "longitudinal_station",
        "transverse_station",
        "x",
        "z",
        "ordinate",
    ]
    assert len(point_rows) > 1

    long_file = tmp_path / "deck_is_long.csv"
    assert (
        iss.to_csv(
            long_file.as_posix(),
            array="forces",
            component="Mz_i",
            element=1,
            layout="long",
            include_physical_coords=True,
        )
        == long_file.as_posix()
    )
    with open(long_file, newline="") as fh:
        long_rows = list(csv.reader(fh))
    assert long_rows[0] == [
        "longitudinal_station",
        "transverse_station",
        "x",
        "z",
        "ordinate",
    ]
    assert len(long_rows) > 1


def test_influence_surface_results_plot_defaults_auto_space(
    bridge_model_42_negative,
    monkeypatch,
):
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    iss = example_bridge.analyze_influence_surfaces(name="Deck IS Default")

    captured = {}

    def _fake_plot(isurface, **kwargs):
        captured["coordinate_space"] = kwargs.get("coordinate_space", None)
        return kwargs.get("coordinate_space", None)

    monkeypatch.setattr("ospgrillage.osp_grillage.plot_influence_surface", _fake_plot)

    iss.plot(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
        show=False,
    )
    assert captured["coordinate_space"] is None

    iss.plot(
        array="forces",
        component="Mz_i",
        element=1,
        x_coord="longitudinal_station",
        y_coord="transverse_station",
        coordinate_space="physical",
        show=False,
    )
    assert captured["coordinate_space"] == "physical"


def test_influence_line_midspan_moment_matches_l_over_4(ref_bridge_properties):
    og.ops.wipeAnalysis()
    I_beam, slab, exterior_I_beam, concrete = ref_bridge_properties

    L = 10.0
    bridge = og.create_grillage(
        bridge_name="IL_simple_beam",
        long_dim=L,
        width=2.0,
        skew=0,
        num_long_grid=3,
        num_trans_grid=3,
        edge_beam_dist=1.0,
        mesh_type="Ortho",
    )
    bridge.set_member(I_beam, member="interior_main_beam")
    bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    bridge.set_member(exterior_I_beam, member="edge_beam")
    bridge.set_member(slab, member="transverse_slab")
    bridge.set_member(exterior_I_beam, member="start_edge")
    bridge.set_member(exterior_I_beam, member="end_edge")
    bridge.create_osp_model(pyfile=False)

    interior_elements = bridge.get_element(member="interior_main_beam", options="elements")
    assert len(interior_elements) == 2

    bridge.analyze_il(
        name="unit_axle_il",
        start_point=og.Point(0, 0, 1.0),
        end_point=og.Point(L, 0, 1.0),
        step=0.5,
        axle_load=1.0,
    )
    il = bridge.get_il(
        name="unit_axle_il",
        array="forces",
        component="Mz_j",
        element=interior_elements[0],
        load_coord="x",
    )

    midspan_ordinate = float(il.sel(x=L / 2, method="nearest"))
    assert np.isclose(midspan_ordinate, -L / 4, atol=0.15)


def test_hermite_triangle_region_uses_dkt_style_distribution(bridge_model_42_negative):
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative

    tri_grid_nodes = None
    for nodes in bridge.Mesh_obj.grid_number_dict.values():
        if len(nodes) == 3:
            tri_grid_nodes = nodes
            break

    assert tri_grid_nodes is not None
    coords = [bridge.Mesh_obj.node_spec[node]["coordinate"] for node in tri_grid_nodes]
    point = [
        sum(coord[0] for coord in coords) / 3,
        0,
        sum(coord[2] for coord in coords) / 3,
    ]

    load_cmd = bridge._assign_load_to_four_node(point=point, mag=1.0, shape_func="hermite")

    assert len(load_cmd) == 3
    vertical_sum = sum(command[1][2] for command in load_cmd)
    mx_sum = sum(command[1][4] for command in load_cmd)
    mz_sum = sum(command[1][6] for command in load_cmd)
    assert any(abs(command[1][4]) > 0 for command in load_cmd)
    assert any(abs(command[1][6]) > 0 for command in load_cmd)
    assert np.isclose(vertical_sum, 1.0)
    assert np.isclose(mx_sum, 0.0)
    assert np.isclose(mz_sum, 0.0)


def test_envelope(bridge_model_42_negative):
    # test functionality of Envelope class and output
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
    # barrier_load_case.add_load(Barrier)  # ch
    barrier_load_case.add_load(Patch1)  # ch
    # 2nd
    barrier_load_case2 = og.create_load_case(name="Barrier2")
    # barrier_load_case2.add_load(Barrier2)
    barrier_load_case2.add_load(Patch2)
    # 3rd
    # barrier_load_case3 = og.create_load_case(name="Barrier3")
    # barrier_load_case3.add_load(Barrier3)

    # adding load cases to model
    example_bridge.add_load_case(barrier_load_case)
    example_bridge.add_load_case(barrier_load_case2)
    # example_bridge.add_load_case(barrier_load_case3)

    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3), increments=3
    )  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_load(front_wheel)
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


def test_plot_force(bridge_model_42_negative):
    # test functionality of plot_force and its output
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    # og.opsv.plot_model()
    # og.plt.show()
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
    # barrier_load_case.add_load(Barrier)  # ch
    barrier_load_case.add_load(Patch1)  # ch
    # 2nd
    barrier_load_case2 = og.create_load_case(name="Barrier2")
    # barrier_load_case2.add_load(Barrier2)
    barrier_load_case2.add_load(Patch2)
    # 3rd
    # barrier_load_case3 = og.create_load_case(name="Barrier3")
    # barrier_load_case3.add_load(Barrier3)

    # adding load cases to model
    example_bridge.add_load_case(barrier_load_case)
    example_bridge.add_load_case(barrier_load_case2)
    # example_bridge.add_load_case(barrier_load_case3)

    single_path = og.create_moving_path(
        start_point=og.Point(2, 0, 2), end_point=og.Point(4, 0, 3), increments=3
    )  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_load(front_wheel)
    example_bridge.add_load_case(move_point)

    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    # og.opsv.section_force_diagram_3d("Mz",{})

    f = og.plot_force(
        ospgrillage_obj=example_bridge,
        result_obj=results,
        component="Mz",
        member="interior_main_beam",
        loadcase="single_moving_point at global position [4.00,0.00,3.00]",
    )


def test_shell_plot_force(shell_link_bridge):
    # test functionality of plot_force on a shell_beam model type
    shell_link_model = shell_link_bridge
    # create and add load case comprise of single point load
    P = 20e3
    point_load_location = og.create_load_vertex(
        x=4.5, y=0, z=6.5, p=P
    )  # about midspan of span 1
    point_load = og.create_load(
        loadtype="point", name="single point", point1=point_load_location
    )
    point_lc = og.create_load_case(name="pointload")
    point_lc.add_load(point_load)
    shell_link_model.add_load_case(point_lc)
    shell_link_model.analyze()
    # extract results
    result = shell_link_model.get_results()
    print(result)
    f = og.plot_force(
        ospgrillage_obj=shell_link_model,
        result_obj=result,
        component="Mx",
        member="exterior_main_beam_1",
    )


def test_displacement_getter(bridge_model_42_negative):
    # test functionality of plot_force and its output
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative
    # og.opsv.plot_model()
    # og.plt.show()

    # add moving load case
    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )

    point_load_case = og.create_load_case(name="Point")
    point_load_case.add_load(front_wheel)
    example_bridge.add_load_case(point_load_case)

    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    processor = og.PostProcessor(grillage=example_bridge, result=results)

    arbitrary_disp = processor.get_arbitrary_displacements(point=[5, 0, 3])  # bigger

    assert all(np.isclose(arbitrary_disp * 1e6, [3.1289e-05 * 1e6]))


# ---------------------------------------------------------------------------
# og.plt accessibility
# ---------------------------------------------------------------------------
def test_og_plt_accessible():
    """og.plt should be matplotlib.pyplot."""
    assert hasattr(og, "plt")
    fig = og.plt.figure()
    assert fig is not None
    og.plt.close(fig)


# ---------------------------------------------------------------------------
# Convenience plotting wrappers
# ---------------------------------------------------------------------------
def test_plot_bmd(bridge_model_42_negative):
    """plot_bmd returns a figure for a single member and a list for all."""
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    # single member
    ax = og.plot_bmd(example_bridge, results, members="interior_main_beam")
    assert ax is not None

    # all main beams (returns list)
    axes = og.plot_bmd(example_bridge, results)
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_sfd(bridge_model_42_negative):
    """plot_sfd returns a figure for a single member and a list for all."""
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    ax = og.plot_sfd(example_bridge, results, members="interior_main_beam")
    assert ax is not None

    axes = og.plot_sfd(example_bridge, results)
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_def(bridge_model_42_negative):
    """plot_def returns a figure for a single member and a list for all."""
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    ax = og.plot_def(example_bridge, results, members="interior_main_beam")
    assert ax is not None

    axes = og.plot_def(example_bridge, results)
    assert isinstance(axes, list)
    assert len(axes) >= 1


# ---------------------------------------------------------------------------
# Plotly backend tests
# ---------------------------------------------------------------------------
def test_plot_bmd_plotly(bridge_model_42_negative):
    """plot_bmd with backend='plotly' returns a plotly Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    fig = og.plot_bmd(example_bridge, results, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0  # has traces


def test_plot_sfd_plotly(bridge_model_42_negative):
    """plot_sfd with backend='plotly' returns a plotly Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    fig = og.plot_sfd(example_bridge, results, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plot_def_plotly(bridge_model_42_negative):
    """plot_def with backend='plotly' returns a plotly Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    fig = og.plot_def(example_bridge, results, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plotly_single_member(bridge_model_42_negative):
    """plot_bmd with plotly and a single member should return a Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    example_bridge = bridge_model_42_negative

    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    example_bridge.add_load_case(lc)
    example_bridge.analyze()
    results = example_bridge.get_results(local_forces=False)

    fig = og.plot_bmd(
        example_bridge,
        results,
        members="interior_main_beam",
        backend="plotly",
        show=False,
    )
    assert isinstance(fig, go.Figure)


def test_plotly_import_error():
    """When plotly is unavailable, backend='plotly' should raise ImportError."""
    from unittest.mock import patch
    from ospgrillage.postprocessing import _import_plotly

    with patch.dict("sys.modules", {"plotly": None, "plotly.graph_objects": None}):
        with pytest.raises(ImportError, match="ospgrillage\\[gui\\]"):
            _import_plotly()


# ---------------------------------------------------------------------------
# Plotting kwargs tests
# ---------------------------------------------------------------------------
def _make_analyzed_bridge(bridge_model_42_negative):
    """Helper: set up a load case, analyse, and return (bridge, results)."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    bridge.add_load_case(lc)
    bridge.analyze()
    results = bridge.get_results(local_forces=False)
    return bridge, results


def test_plot_force_figsize(bridge_model_42_negative):
    """figsize is forwarded to plt.subplots."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    ax = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        figsize=(10, 4),
    )
    w, h = ax.get_figure().get_size_inches()
    assert abs(w - 10) < 0.1
    assert abs(h - 4) < 0.1


def test_plot_force_ax(bridge_model_42_negative):
    """Passing an existing Axes should reuse the axes."""
    import matplotlib.pyplot as plt

    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    fig_ext, ax_ext = plt.subplots(figsize=(12, 3))
    returned_ax = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        ax=ax_ext,
    )
    assert returned_ax is ax_ext


def test_plot_force_scale(bridge_model_42_negative):
    """scale=2.0 should double the plotted y-values."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    ax1 = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        scale=1.0,
    )
    ax2 = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        scale=2.0,
    )
    # Compare the first line's y-data
    import numpy as np

    y1 = ax1.lines[0].get_ydata()
    y2 = ax2.lines[0].get_ydata()
    np.testing.assert_allclose(y2, y1 * 2, rtol=1e-10)


def test_plot_force_styling(bridge_model_42_negative):
    """Smoke test: color, fill, alpha, title, show kwargs don't error."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    ax = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        color="r",
        fill=False,
        alpha=0.8,
        title="Custom Title",
        show=False,
    )
    assert ax.get_title() == "Custom Title"
    # fill=False means no PolyCollection (only lines)
    assert len(ax.collections) == 0


def test_plot_force_title_none(bridge_model_42_negative):
    """title=None should suppress the title."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    ax = og.plot_force(
        bridge,
        results,
        component="Mz",
        member="interior_main_beam",
        title=None,
    )
    assert ax.get_title() == ""


def test_plot_bmd_kwargs_passthrough(bridge_model_42_negative):
    """plot_bmd forwards kwargs to plot_force without error."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    ax = og.plot_bmd(
        bridge,
        results,
        members="interior_main_beam",
        figsize=(12, 4),
        scale=0.001,
        title="BMD (kNm)",
    )
    assert ax is not None
    assert ax.get_title() == "BMD (kNm)"


def test_plot_def_kwargs_passthrough(bridge_model_42_negative):
    """plot_def forwards kwargs to the deflection renderer without error."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    ax = og.plot_def(
        bridge,
        results,
        members="interior_main_beam",
        figsize=(12, 4),
        scale=1000,
        color="g",
    )
    assert ax is not None


def test_plotly_kwargs(bridge_model_42_negative):
    """Plotly backend accepts figsize, scale, title kwargs."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    fig = og.plot_bmd(
        bridge,
        results,
        backend="plotly",
        show=False,
        figsize=(12, 8),
        scale=0.5,
        title="Custom Plotly BMD",
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Custom Plotly BMD"
    assert fig.layout.width == 1200
    assert fig.layout.height == 800


# ---------------------------------------------------------------------------
# plot_model tests
# ---------------------------------------------------------------------------
def test_plot_model_matplotlib(bridge_model_42_negative):
    """plot_model with matplotlib returns an Axes showing the mesh."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    ax = og.plot_model(bridge)
    assert ax is not None
    assert len(ax.lines) > 0


def test_plot_model_matplotlib_labels(bridge_model_42_negative):
    """plot_model shows node/element labels when requested."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    ax = og.plot_model(bridge, show_node_labels=True, show_element_labels=True)
    assert len(ax.texts) > 0


def test_plot_model_matplotlib_kwargs(bridge_model_42_negative):
    """plot_model accepts figsize, title, ax kwargs."""
    import matplotlib.pyplot as plt

    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    ax = og.plot_model(bridge, figsize=(12, 6), title="Test Model")
    w, h = ax.get_figure().get_size_inches()
    assert abs(w - 12) < 0.1
    assert ax.get_title() == "Test Model"


def test_plot_model_plotly(bridge_model_42_negative):
    """plot_model with plotly returns a plotly Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    fig = og.plot_model(bridge, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plot_model_invalid_backend(bridge_model_42_negative):
    """plot_model raises ValueError for unknown backend."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    with pytest.raises(ValueError, match="Unknown backend"):
        og.plot_model(bridge, backend="vtk")


# ---------------------------------------------------------------------------
# Members enum tests
# ---------------------------------------------------------------------------
def test_members_enum_composites():
    """Members composites resolve to expected individual flags."""
    assert og.Members.LONGITUDINAL == (
        og.Members.EDGE_BEAM
        | og.Members.EXTERIOR_MAIN_BEAM_1
        | og.Members.INTERIOR_MAIN_BEAM
        | og.Members.EXTERIOR_MAIN_BEAM_2
    )
    assert og.Members.TRANSVERSE == (
        og.Members.START_EDGE | og.Members.END_EDGE | og.Members.TRANSVERSE_SLAB
    )
    assert og.Members.ALL == og.Members.LONGITUDINAL | og.Members.TRANSVERSE


def test_resolve_members_none_plotly():
    """member=None with plotly backend resolves to all 7 members."""
    from ospgrillage.postprocessing import _resolve_members

    result = _resolve_members(None, backend="plotly")
    assert len(result) == 7
    assert "transverse_slab" in result
    assert "start_edge" in result


def test_resolve_members_none_matplotlib():
    """member=None with matplotlib backend resolves to 4 longitudinal members."""
    from ospgrillage.postprocessing import _resolve_members

    result = _resolve_members(None, backend="matplotlib")
    assert len(result) == 4
    assert "transverse_slab" not in result


def test_resolve_members_string():
    """A string member name resolves to a single-element list."""
    from ospgrillage.postprocessing import _resolve_members

    result = _resolve_members("interior_main_beam")
    assert result == ["interior_main_beam"]


def test_resolve_members_flag_combination():
    """A combined flag resolves in declaration order."""
    from ospgrillage.postprocessing import _resolve_members

    result = _resolve_members(og.Members.TRANSVERSE_SLAB | og.Members.EDGE_BEAM)
    assert result == ["edge_beam", "transverse_slab"]


def test_resolve_members_invalid_string():
    """An unknown member name raises ValueError."""
    from ospgrillage.postprocessing import _resolve_members

    with pytest.raises(ValueError, match="Unknown member"):
        _resolve_members("nonexistent_beam")


def test_resolve_members_invalid_type():
    """An unsupported type raises TypeError."""
    from ospgrillage.postprocessing import _resolve_members

    with pytest.raises(TypeError, match="must be str, Members, or None"):
        _resolve_members(42)


def test_plot_bmd_with_members_flag(bridge_model_42_negative):
    """plot_bmd matplotlib backend accepts a Members flag."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    axes = og.plot_bmd(
        bridge,
        results,
        members=og.Members.INTERIOR_MAIN_BEAM | og.Members.EDGE_BEAM,
    )
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_sfd_with_members_flag(bridge_model_42_negative):
    """plot_sfd matplotlib backend accepts a Members flag."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    axes = og.plot_sfd(
        bridge,
        results,
        members=og.Members.LONGITUDINAL,
    )
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_def_with_members_flag(bridge_model_42_negative):
    """plot_def matplotlib backend accepts a Members flag."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    axes = og.plot_def(
        bridge,
        results,
        members=og.Members.INTERIOR_MAIN_BEAM,
    )
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_bmd_plotly_members_flag(bridge_model_42_negative):
    """plot_bmd plotly backend accepts a Members flag."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    fig = og.plot_bmd(
        bridge,
        results,
        members=og.Members.LONGITUDINAL,
        backend="plotly",
        show=False,
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plot_def_plotly_members_flag(bridge_model_42_negative):
    """plot_def plotly backend accepts a Members flag."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)
    fig = og.plot_def(
        bridge,
        results,
        members=og.Members.ALL,
        backend="plotly",
        show=False,
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


# ---------------------------------------------------------------------------
# Torsion moment diagram tests
# ---------------------------------------------------------------------------
def test_plot_tmd(bridge_model_42_negative):
    """plot_tmd returns a figure for a single member and a list for all."""
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    # single member
    ax = og.plot_tmd(bridge, results, members="interior_main_beam")
    assert ax is not None

    # all main beams (returns list)
    axes = og.plot_tmd(bridge, results)
    assert isinstance(axes, list)
    assert len(axes) >= 1


def test_plot_tmd_plotly(bridge_model_42_negative):
    """plot_tmd with backend='plotly' returns a plotly Figure."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    fig = og.plot_tmd(bridge, results, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


# ---------------------------------------------------------------------------
# Plotly fill (Mesh3d ribbon) tests
# ---------------------------------------------------------------------------
def test_plotly_force_fill(bridge_model_42_negative):
    """Plotly BMD includes Mesh3d fill traces by default."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    fig = og.plot_bmd(
        bridge,
        results,
        members="interior_main_beam",
        backend="plotly",
        show=False,
    )
    mesh_traces = [t for t in fig.data if isinstance(t, go.Mesh3d)]
    assert len(mesh_traces) >= 1


def test_plotly_force_no_fill(bridge_model_42_negative):
    """fill=False suppresses Mesh3d traces."""
    go = pytest.importorskip("plotly.graph_objects")
    bridge, results = _make_analyzed_bridge(bridge_model_42_negative)

    fig = og.plot_bmd(
        bridge,
        results,
        members="interior_main_beam",
        backend="plotly",
        show=False,
        fill=False,
    )
    mesh_traces = [t for t in fig.data if isinstance(t, go.Mesh3d)]
    assert len(mesh_traces) == 0


# ---------------------------------------------------------------------------
# Support drawing tests
# ---------------------------------------------------------------------------
def test_plot_model_supports_matplotlib(bridge_model_42_negative):
    """plot_model with show_supports=True draws support markers."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    ax = og.plot_model(bridge, show_supports=True)
    assert ax is not None


def test_plot_model_supports_plotly(bridge_model_42_negative):
    """plot_model plotly with show_supports=True includes support traces."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    fig = og.plot_model(bridge, backend="plotly", show=False, show_supports=True)
    assert isinstance(fig, go.Figure)
    support_traces = [t for t in fig.data if "support" in (t.name or "")]
    assert len(support_traces) >= 1


def test_plot_model_no_supports(bridge_model_42_negative):
    """plot_model with show_supports=False omits support markers."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    fig = og.plot_model(bridge, backend="plotly", show=False, show_supports=False)
    support_traces = [t for t in fig.data if "support" in (t.name or "")]
    assert len(support_traces) == 0


# ---------------------------------------------------------------------------
# Shell contour plotting
# ---------------------------------------------------------------------------
def _shell_results(shell_link_bridge):
    """Helper: run a point load on a shell_beam model and return results."""
    og.ops.wipeAnalysis()
    model = shell_link_bridge
    P = 20e3
    pt = og.create_load_vertex(x=4.5, y=0, z=6.5, p=P)
    load = og.create_load(loadtype="point", name="single point", point1=pt)
    lc = og.create_load_case(name="pointload")
    lc.add_load(load)
    model.add_load_case(lc)
    model.analyze()
    return model.get_results()


def test_extract_shell_contour_data(shell_link_bridge):
    """_extract_shell_contour_data returns correct structure."""
    result = _shell_results(shell_link_bridge)
    from ospgrillage.postprocessing import _extract_shell_contour_data

    node_values, element_quads = _extract_shell_contour_data(result, "Mx")
    assert len(node_values) > 0
    assert all(isinstance(v, float) for v in node_values.values())
    assert len(element_quads) > 0
    assert all(len(q) >= 3 for q in element_quads)


def test_extract_shell_contour_all_components(shell_link_bridge):
    """All 6 components extract without error."""
    result = _shell_results(shell_link_bridge)
    from ospgrillage.postprocessing import _extract_shell_contour_data

    for comp in ("Vx", "Vy", "Vz", "Mx", "My", "Mz"):
        node_values, element_quads = _extract_shell_contour_data(result, comp)
        assert len(node_values) > 0


def test_extract_shell_contour_invalid_component(shell_link_bridge):
    """Invalid component raises ValueError."""
    result = _shell_results(shell_link_bridge)
    from ospgrillage.postprocessing import _extract_shell_contour_data

    with pytest.raises(ValueError, match="Unknown"):
        _extract_shell_contour_data(result, "Fxx")


def test_triangulate_shell_mesh():
    """Triangulation of a single quad produces 4 vertices and 2 triangles."""
    from ospgrillage.postprocessing import _triangulate_shell_mesh

    node_coords = {1: [0, 0, 0], 2: [1, 0, 0], 3: [1, 0, 1], 4: [0, 0, 1]}
    quads = [(1, 2, 3, 4)]
    vx, vy, vz, i_idx, j_idx, k_idx, tag_map = _triangulate_shell_mesh(
        node_coords, quads
    )
    assert len(vx) == 4
    assert len(i_idx) == 2
    assert len(tag_map) == 4


def test_plot_srf_plotly(shell_link_bridge):
    """plot_srf with plotly backend returns a Figure with Mesh3d."""
    go = pytest.importorskip("plotly.graph_objects")
    result = _shell_results(shell_link_bridge)
    fig = og.plot_srf(result, "Mx", backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    mesh_traces = [t for t in fig.data if isinstance(t, go.Mesh3d)]
    assert len(mesh_traces) >= 1
    assert mesh_traces[0].intensity is not None


def test_plot_srf_mpl(shell_link_bridge):
    """plot_srf with matplotlib backend returns Axes."""
    import matplotlib.pyplot as plt

    result = _shell_results(shell_link_bridge)
    ax = og.plot_srf(result, "Mx", backend="matplotlib")
    assert isinstance(ax, plt.Axes)
    plt.close("all")


def test_plot_srf_beam_only_raises(bridge_model_42_negative):
    """Calling plot_srf on a beam-only dataset raises ValueError."""
    og.ops.wipeAnalysis()
    bridge = bridge_model_42_negative
    front_wheel = og.PointLoad(
        name="front wheel", point1=og.LoadPoint(7.5, 0, 4.5, 160e3)
    )
    lc = og.create_load_case(name="Point")
    lc.add_load(front_wheel)
    bridge.add_load_case(lc)
    bridge.analyze()
    result = bridge.get_results()
    with pytest.raises(ValueError, match="shell"):
        og.plot_srf(result, "Mx")


def test_plot_srf_custom_colorscale(shell_link_bridge):
    """Custom colorscale is applied to the Mesh3d trace."""
    go = pytest.importorskip("plotly.graph_objects")
    result = _shell_results(shell_link_bridge)
    fig = og.plot_srf(
        result, "Mx", backend="plotly", show=False, colorscale="Viridis"
    )
    mesh = [t for t in fig.data if isinstance(t, go.Mesh3d)][0]
    assert mesh.colorscale is not None


def test_srf_coexistence_with_bmd(shell_link_bridge):
    """SRF contour and BMD can coexist on one Plotly figure."""
    go = pytest.importorskip("plotly.graph_objects")
    result = _shell_results(shell_link_bridge)
    proxy = og.model_proxy_from_results(result)
    fig = og.plot_srf(result, "Mx", backend="plotly", show=False)
    fig2 = og.plot_bmd(
        proxy, result, backend="plotly", show=False, show_supports=False, ax=fig
    )
    assert fig2 is fig
    has_mesh = any(isinstance(t, go.Mesh3d) for t in fig.data)
    has_scatter = any(isinstance(t, go.Scatter3d) for t in fig.data)
    assert has_mesh and has_scatter
# Cross-model-type coverage (beam_link, shell_beam)
# ---------------------------------------------------------------------------
def test_plot_model_beam_link_matplotlib(beam_link_bridge):
    """plot_model matplotlib works for beam_link models."""
    og.ops.wipeAnalysis()
    ax = og.plot_model(beam_link_bridge)
    assert ax is not None
    assert len(ax.lines) > 0


def test_plot_model_beam_link_plotly(beam_link_bridge):
    """plot_model plotly works for beam_link models."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    fig = og.plot_model(beam_link_bridge, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plot_model_shell_beam_matplotlib(shell_link_bridge):
    """plot_model matplotlib works for shell_beam models."""
    og.ops.wipeAnalysis()
    ax = og.plot_model(shell_link_bridge)
    assert ax is not None
    assert len(ax.lines) > 0


def test_plot_model_shell_beam_plotly(shell_link_bridge):
    """plot_model plotly works for shell_beam models including rigid links."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    fig = og.plot_model(shell_link_bridge, backend="plotly", show=False)
    assert isinstance(fig, go.Figure)
    # shell_beam should have rigid link traces
    link_traces = [t for t in fig.data if "rigid_link" in (t.name or "")]
    assert len(link_traces) >= 1


def test_plot_model_shell_beam_hide_rigid_links(shell_link_bridge):
    """show_rigid_links=False suppresses rigid link traces."""
    go = pytest.importorskip("plotly.graph_objects")
    og.ops.wipeAnalysis()
    fig = og.plot_model(
        shell_link_bridge, backend="plotly", show=False, show_rigid_links=False
    )
    link_traces = [t for t in fig.data if "rigid_link" in (t.name or "")]
    assert len(link_traces) == 0


def test_beam_link_get_results(beam_link_bridge):
    """beam_link model produces finite results under a point load."""
    og.ops.wipeAnalysis()
    model = beam_link_bridge
    P = 10000
    lp = og.create_load_vertex(x=5, y=0, z=3.5, p=P)
    load = og.create_load(name="unit", point1=lp)
    lc = og.create_load_case(name="point")
    lc.add_load(load)

    model.add_load_case(lc)
    model.analyze()
    results = model.get_results()
    assert results is not None

    disp_y = np.array(results["displacements"].sel(Component="y").values, dtype=float)
    assert np.all(np.isfinite(disp_y)), "Non-finite displacement values"
    assert np.any(
        disp_y != 0.0
    ), "All displacements are zero — analysis produced no results"
