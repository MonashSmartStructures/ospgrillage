from ospgrillage import __version__ as version
from fixtures import *

sys.path.insert(0, os.path.abspath("../"))


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
