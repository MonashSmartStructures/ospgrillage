# -*- coding: utf-8 -*-
"""
This module contains functions and classes related to post processing processes.
The post processing module is an addition to the currently available post processing
module of OpenSeesPy - this module fills in gaps to
* create envelope from xarray DataSet
* plot force and deflection diagrams from xarray DataSets
"""

import enum
import matplotlib.pyplot as plt
import opsvis as opsv
import numpy as np
from typing import TYPE_CHECKING, Union

# if TYPE_CHECKING:
from ospgrillage.load import ShapeFunction
from ospgrillage.utils import solve_zeta_eta

__all__ = [
    "Envelope",
    "Members",
    "PostProcessor",
    "create_envelope",
    "plot_force",
    "plot_bmd",
    "plot_sfd",
    "plot_tmd",
    "plot_def",
    "plot_model",
]


# Sentinel for auto-generated titles.  ``title=_AUTO`` means "use the
# default"; ``title=None`` means "no title"; ``title="..."`` is a custom
# override.
_AUTO = object()


# ---------------------------------------------------------------------------
# Lazy import for optional plotly dependency
# ---------------------------------------------------------------------------
def _import_plotly():
    """Lazy-import plotly; raise a clear error if missing."""
    try:
        import plotly.graph_objects as go

        return go
    except ImportError:
        raise ImportError(
            "plotly is required for interactive plots. "
            "Install it with: pip install ospgrillage[gui]"
        )


def _show_plotly_fig(fig):
    """Display a Plotly figure with output compatible with nbsphinx/Sphinx.

    In a Jupyter/IPython session this emits ``text/html`` using
    ``fig.to_html(include_plotlyjs="cdn")``.  The ``text/html`` MIME type
    is understood by *nbsphinx* so the interactive 3-D plot survives the
    Sphinx build and renders with full rotate/zoom/hover on the
    documentation pages (e.g. GitHub Pages).

    Outside IPython the function falls back to ``fig.show()`` which opens
    the system browser.
    """
    try:
        from IPython.display import display, HTML

        display(HTML(fig.to_html(include_plotlyjs="cdn", full_html=False)))
    except ImportError:
        fig.show()


def create_envelope(**kwargs):
    """
    Create an envelope object for post-processing result envelopes.

    The constructor takes an `xarray` DataSet and kwargs for enveloping options.

    :param ds: Result DataSet from :func:`~ospgrillage.osp_grillage.OspGrillage.get_results`.
    :type ds: xarray.Dataset
    :param load_effect: Specific load effect component to envelope.
    :type load_effect: str, optional
    :param array: Data array to envelope — either ``"displacements"`` or ``"forces"``.
    :type array: str, optional
    :param value_mode: If ``True``, return raw envelope values. Defaults to ``True``.
    :type value_mode: bool, optional
    :param query_mode: If ``True``, return the load case coordinates at the envelope extrema. Defaults to ``False``.
    :type query_mode: bool, optional
    :param extrema: Envelope direction — either ``"min"`` or ``"max"``.
    :type extrema: str, optional
    :param elements: Specific element tags to include in the envelope.
    :type elements: list, optional
    :param nodes: Specific node tags to include in the envelope.
    :type nodes: list, optional
    :returns: :class:`Envelope` object.
    """
    return Envelope(**kwargs)


class Envelope:
    """
    Class for defining envelope of :class:`~ospgrillage.osp_grillage.OspGrillage`'s
    `xarray` of result.

    A :func:`Envelope.get` method is provided that returns an enveloped `xarray` based
    on the specified input parameters of this class.


    """

    def __init__(self, ds, load_effect: str = None, **kwargs):
        """

        :param ds: Data set from
                   :func:`~ospgrillage.osp_grillage.OspGrillage.get_results` . note Combination
        :type ds: Xarray
        :param load_effect: Specific load effect to envelope.
        :type load_effect: str
        :param array: Data array to envelope — either ``"displacements"`` or ``"forces"``.
        :type array: str, optional
        :param value_mode: If ``True``, return raw envelope values. Defaults to ``True``.
        :type value_mode: bool, optional
        :param query_mode: If ``True``, return the load case coordinate at the envelope extrema. Defaults to ``False``.
        :type query_mode: bool, optional
        :param extrema: Envelope direction — either ``"min"`` or ``"max"``.
        :type extrema: str, optional
        :param elements: Specific element tags to include in the envelope.
        :type elements: list, optional
        :param nodes: Specific node tags to include in the envelope.
        :type nodes: list, optional

        """
        self.value = True
        self.ds = ds
        if ds is None:
            return

        # instantiate variables
        self.load_effect = (
            load_effect  # array load effect either displacements or forces
        )
        self.envelope_ds = None
        # default xarray function name
        self.xarray_command = {
            "query": ["idxmax", "idxmin"],
            "minmax value": ["max", "min"],
            "index": ["argmax", "argmin"],
        }
        self.selected_xarray_command = []
        # get keyword args
        self.elements = kwargs.get(
            "elements", None
        )  # specific elements to query/envelope
        self.nodes = kwargs.get("nodes", None)  # specific nodes to query/envelope
        self.component = kwargs.get(
            "load_effect", None
        )  # specific load effect to query
        self.array = kwargs.get("array", "displacements")
        self.value_mode = kwargs.get("value_mode", True)
        self.query_mode = kwargs.get("query_mode", False)  # default query mode
        self.extrema = kwargs.get("extrema", "max")

        # check variables
        if self.load_effect is None:
            raise ValueError(
                "Missing argument for load_effect=: Hint requires a namestring of load"
                "effect type based on the Component dimension of the ospgrillage data"
                "set result format"
            )

        # process variables
        self.extrema_index = 0 if self.extrema == "max" else 1  # minima
        if self.query_mode:
            self.selected_xarray_command = self.xarray_command["query"][
                self.extrema_index
            ]
        elif self.value_mode:
            self.selected_xarray_command = self.xarray_command["minmax value"][
                self.extrema_index
            ]
        else:  # default to argmax/ argmin
            self.selected_xarray_command = self.xarray_command["index"][
                self.extrema_index
            ]

        # NOTE: element/component filtering via self.elements and self.component
        # is not yet implemented — get() currently returns the full reduced array.
        # A future enhancement should build a sel() dict from these kwargs and
        # call .sel(**sel_kwargs) in get().

    def get(self):
        """

        :returns: The enveloped xarray DataArray with envelope values applied.
        :rtype: xarray.DataArray
        """
        da = getattr(self.ds, self.array)
        return getattr(da, self.selected_xarray_command)(dim="Loadcase")


# ---------------------------------------------------------------------------
# Force component lookup tables
# ---------------------------------------------------------------------------
_FORCE_COMP_DICT = {"Fx": 0, "Fy": 1, "Fz": 2, "Mx": 3, "My": 4, "Mz": 5}
_FORCE_COMP_FACTOR = {"Fx": 1, "Fy": 1, "Fz": 1, "Mx": 1, "My": 1, "Mz": -1}

_FORCE_COMPONENTS = [
    "Vx_i",
    "Vy_i",
    "Vz_i",
    "Mx_i",
    "My_i",
    "Mz_i",
    "Vx_j",
    "Vy_j",
    "Vz_j",
    "Mx_j",
    "My_j",
    "Mz_j",
]


# ---------------------------------------------------------------------------
# Data extraction helpers (backend-agnostic)
# ---------------------------------------------------------------------------
def _num_z_groups(ospgrillage_obj, member):
    """Return the number of z-groups for a member.

    Longitudinal members like ``"interior_main_beam"`` may contain several
    parallel beams.  Each is a separate z-group.  Transverse and edge
    member types always return 1.
    """
    z_grp = ospgrillage_obj.common_grillage_element_z_group.get(member)
    if z_grp is None:
        return 1
    return len(z_grp)


def _extract_force_data(
    ospgrillage_obj,
    result_obj,
    component,
    member,
    loadcase=None,
    option="elements",
    z_group_num=0,
):
    """Extract force distribution data for a single member.

    Iterates over every element in the requested *member* group, calls
    :func:`opsvis.section_force_distribution_3d` for each, and collects the
    results into three parallel lists.

    :param ospgrillage_obj: Grillage model object.
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of analysis results.
    :param component: Force component name (``"Fx"``, ``"Fy"``, ``"Fz"``,
        ``"Mx"``, ``"My"``, ``"Mz"``) or integer index.
    :param member: Member group name string.
    :param loadcase: Load case name.  ``None`` uses the first load case.
    :param option: Element query option passed to
        :meth:`~ospgrillage.osp_grillage.OspGrillage.get_element`.
    :returns: ``(all_xx, all_zz, all_values)`` — each a list of
        per-element :class:`numpy.ndarray`.  ``all_values`` entries are
        already multiplied by the component sign factor.
    :rtype: tuple[list, list, list]
    """
    comp_index = (
        component if isinstance(component, int) else _FORCE_COMP_DICT[component]
    )
    factor = _FORCE_COMP_FACTOR[component] if isinstance(component, str) else 1

    nodes = ospgrillage_obj.get_nodes()
    eletag = ospgrillage_obj.get_element(
        member=member,
        options=option,
        z_group_num=z_group_num,
    )

    if ospgrillage_obj.model_type == "shell_beam":
        force_result = result_obj.forces_beam
    else:
        force_result = result_obj.forces

    all_xx, all_zz, all_values = [], [], []

    for ele in eletag:
        # get force components for this element
        if loadcase:
            ele_components = force_result.sel(
                Loadcase=loadcase,
                Element=ele,
                Component=_FORCE_COMPONENTS,
            ).values
        else:
            ele_components = force_result.sel(
                Element=ele,
                Component=_FORCE_COMPONENTS,
            )[0].values

        # get nodes of element
        if ospgrillage_obj.model_type == "shell_beam":
            ele_node = result_obj.ele_nodes_shell.sel(Element=ele)
            if all(np.isnan(result_obj.ele_nodes_shell.sel(Element=ele))):
                ele_node = result_obj.ele_nodes_beam.sel(Element=ele)
            ele_node = ele_node[~np.isnan(ele_node)]
        else:
            ele_node = result_obj.ele_nodes.sel(Element=ele)

        node_tags = ele_node.values.flatten().astype(int).tolist()
        xx = [nodes[n]["coordinate"][0] for n in node_tags]
        yy = [nodes[n]["coordinate"][1] for n in node_tags]
        zz = [nodes[n]["coordinate"][2] for n in node_tags]

        # opsvis section force distribution
        s, *_ = opsv.section_force_distribution_3d(
            ecrd=np.column_stack([xx, yy, zz]),
            pl=ele_components,
        )

        all_xx.append(np.array(xx))
        all_zz.append(np.array(zz))
        all_values.append(s[:, comp_index] * factor)

    return all_xx, all_zz, all_values


def _extract_def_data(
    ospgrillage_obj,
    result_obj,
    member,
    component="y",
    loadcase=None,
    option="nodes",
    z_group_num=0,
):
    """Extract displacement data for a single member.

    Iterates over the nodes belonging to *member* and collects their
    coordinates and displacement values.

    :param ospgrillage_obj: Grillage model object.
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of analysis results.
    :param member: Member group name string.
    :param component: Displacement component (``"x"``, ``"y"``, ``"z"``).
        Defaults to ``"y"`` (vertical deflection).
    :param loadcase: Load case name.  ``None`` uses the first load case.
    :param option: Node query option passed to
        :meth:`~ospgrillage.osp_grillage.OspGrillage.get_element`.
    :returns: ``(xx_list, zz_list, values_list)`` — node x-coordinates,
        z-coordinates, and displacement scalars.
    :rtype: tuple[list, list, list]
    """
    plot_option = option if option is not None else "nodes"
    dis_comp = component if component is not None else "y"

    nodes = ospgrillage_obj.get_nodes()
    node_result = ospgrillage_obj.get_element(
        member=member,
        options=plot_option,
        z_group_num=z_group_num,
    )
    # Longitudinal members return [[node_list]], others return [node_list]
    nodes_to_plot = (
        node_result[0]
        if node_result and isinstance(node_result[0], list)
        else node_result
    )

    xx_list, zz_list, values_list = [], [], []

    for node in nodes_to_plot:
        if loadcase:
            disp = result_obj.displacements.sel(
                Component=dis_comp,
                Node=node,
                Loadcase=loadcase,
            ).values
        else:
            disp = result_obj.displacements.sel(
                Component=dis_comp,
                Node=node,
            )[0].values
        xx_list.append(nodes[node]["coordinate"][0])
        zz_list.append(nodes[node]["coordinate"][2])
        values_list.append(float(disp))

    return xx_list, zz_list, values_list


# ---------------------------------------------------------------------------
# Plotly 3D figure builders
# ---------------------------------------------------------------------------
def _spatial_aspect_ratio(fig):
    """Compute a Plotly aspectratio that keeps the x–y (plan) axes
    proportional while letting the z (value) axis scale freely.

    Scans all ``Scatter3d`` traces already added to *fig* and returns a
    ``dict(x=…, y=…, z=1)`` where x and y reflect the true span-to-width
    ratio of the bridge, and z is normalised to 1 so Plotly auto-scales
    the value axis to fill the available space.
    """
    all_x, all_y = [], []
    for trace in fig.data:
        if hasattr(trace, "x") and trace.x is not None:
            all_x.extend([v for v in trace.x if v is not None])
        if hasattr(trace, "y") and trace.y is not None:
            all_y.extend([v for v in trace.y if v is not None])

    if not all_x or not all_y:
        return dict(x=1, y=1, z=1)

    dx = max(all_x) - min(all_x)
    dy = max(all_y) - min(all_y)

    if dx == 0 and dy == 0:
        return dict(x=1, y=1, z=1)

    # Normalise so the larger spatial dimension = 1
    dmax = max(dx, dy, 1e-12)
    return dict(x=dx / dmax, y=dy / dmax, z=1)


def _plotly_3d_force(
    ospgrillage_obj,
    result_obj,
    component,
    members,
    loadcase=None,
    comp_label=None,
    *,
    fig=None,
    figsize=None,
    scale=1.0,
    title=_AUTO,
    alpha=1.0,
    fill=True,
    fill_alpha=None,
    show_supports=True,
):
    """Build an interactive 3D Plotly figure of force diagrams.

    Each member is drawn as a ``Scatter3d`` trace with:

    * x = longitudinal position (m)
    * y = transverse position (z-coordinate from the grillage model, m)
    * z = force component value

    A semi-transparent ``Mesh3d`` ribbon fills between the diagram curve
    and the zero baseline.  Set *fill=False* to suppress the fill.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of analysis results.
    :param component: Force component name (e.g. ``"Mz"``, ``"Fy"``).
    :param members: List of member group name strings to include.
    :param loadcase: Load case name.  ``None`` uses the first load case.
    :param comp_label: Axis / title label.  Defaults to *component*.
    :param fig: Existing Plotly ``Figure`` to add traces to.
    :param figsize: Figure size in inches ``(width, height)``.
    :param scale: Multiply plotted values by this factor.
    :param title: Plot title.  Default auto-generates from component.
        ``None`` suppresses the title.
    :param alpha: Trace opacity (0–1).
    :param fill: If ``True`` (default), draw a semi-transparent filled
        ribbon between the diagram and zero baseline.
    :param fill_alpha: Opacity of the Mesh3d fill ribbon (0–1).
        Defaults to ``alpha * 0.4`` when ``None``.
    :returns: Interactive 3D figure.
    :rtype: :class:`plotly.graph_objects.Figure`
    """
    go = _import_plotly()
    if fig is None:
        fig = go.Figure()
    label = comp_label or component

    # Resolve fill opacity: user-specified fill_alpha takes precedence,
    # otherwise default to alpha * 0.5 for a clearly visible fill.
    _fill_alpha = fill_alpha if fill_alpha is not None else alpha * 0.5

    # Negate z-axis so that sagging BM and downward shear plot below
    # the baseline (structural engineering convention).
    sign = -1.0

    colours = ["black", "blue", "red", "green", "orange", "purple", "brown", "grey"]
    trace_idx = 0

    for member in members:
        n_groups = _num_z_groups(ospgrillage_obj, member)
        for zg in range(n_groups):
            try:
                all_xx, all_zz, all_vals = _extract_force_data(
                    ospgrillage_obj,
                    result_obj,
                    component,
                    member,
                    loadcase,
                    z_group_num=zg,
                )
            except (KeyError, ValueError, IndexError):
                continue  # member not available for this model type
            colour = colours[trace_idx % len(colours)]
            trace_name = member if n_groups == 1 else f"{member} [{zg+1}]"

            # Accumulate fill vertices across all elements of this member
            # so we emit ONE Mesh3d per member (renders far better than
            # many tiny per-element meshes in WebGL).
            mesh_vx, mesh_vy, mesh_vz = [], [], []
            mesh_ii, mesh_jj, mesh_kk = [], [], []
            voffset = 0

            for ex, ez, ev in zip(all_xx, all_zz, all_vals):
                sv = ev * scale * sign
                # Force diagram line
                fig.add_trace(
                    go.Scatter3d(
                        x=ex,
                        y=ez,
                        z=sv,
                        mode="lines",
                        line=dict(color=colour, width=4),
                        opacity=alpha,
                        name=trace_name,
                        showlegend=False,
                    )
                )
                # Baseline (zero) line
                fig.add_trace(
                    go.Scatter3d(
                        x=ex,
                        y=ez,
                        z=np.zeros_like(sv),
                        mode="lines",
                        line=dict(color=colour, width=1, dash="dot"),
                        opacity=alpha,
                        showlegend=False,
                    )
                )
                # Vertical drop-lines from each node to the baseline
                drop_x, drop_y, drop_z = [], [], []
                for xi, zi, vi in zip(ex, ez, sv):
                    drop_x.extend([xi, xi, None])
                    drop_y.extend([zi, zi, None])
                    drop_z.extend([vi, 0.0, None])
                fig.add_trace(
                    go.Scatter3d(
                        x=drop_x,
                        y=drop_y,
                        z=drop_z,
                        mode="lines",
                        line=dict(color=colour, width=1),
                        opacity=alpha * 0.6,
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )
                # Collect fill vertices for the combined ribbon
                if fill:
                    n_pts = len(ex)
                    if n_pts >= 2:
                        mesh_vx.extend(list(ex) + list(ex))
                        mesh_vy.extend(list(ez) + list(ez))
                        mesh_vz.extend(list(sv) + [0.0] * n_pts)
                        for idx in range(n_pts - 1):
                            mesh_ii.extend([voffset + idx, voffset + idx + 1])
                            mesh_jj.extend(
                                [voffset + idx + 1, voffset + n_pts + idx + 1]
                            )
                            mesh_kk.extend(
                                [voffset + n_pts + idx, voffset + n_pts + idx]
                            )
                        voffset += 2 * n_pts

            # One combined Mesh3d ribbon per member
            if fill and mesh_vx:
                fig.add_trace(
                    go.Mesh3d(
                        x=mesh_vx,
                        y=mesh_vy,
                        z=mesh_vz,
                        i=mesh_ii,
                        j=mesh_jj,
                        k=mesh_kk,
                        color=colour,
                        opacity=_fill_alpha,
                        flatshading=True,
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

            # One legend entry per beam
            fig.add_trace(
                go.Scatter3d(
                    x=[None],
                    y=[None],
                    z=[None],
                    mode="lines",
                    line=dict(color=colour, width=4),
                    name=trace_name,
                )
            )
            trace_idx += 1

    # Support markers on the zero-baseline
    if show_supports:
        supports = _extract_support_data(ospgrillage_obj)
        from collections import defaultdict

        by_type = defaultdict(list)
        for sup in supports:
            by_type[sup["fixity_type"]].append(sup)
        for ftype, sups in sorted(by_type.items()):
            symbol, colour, sz = _SUPPORT_STYLE_PLOTLY.get(ftype, ("x", "purple", 6))
            sx = [s["x"] for s in sups]
            sy = [s["z"] for s in sups]
            sz_vals = [0.0] * len(sups)
            fig.add_trace(
                go.Scatter3d(
                    x=sx,
                    y=sy,
                    z=sz_vals,
                    mode="markers",
                    marker=dict(
                        symbol=symbol,
                        size=sz,
                        color=colour,
                        line=dict(color="black", width=1),
                    ),
                    name=f"support ({ftype})",
                )
            )

    # Compute spatial data ranges so the plan-view (x vs z) axes are
    # proportional while the force axis scales freely.
    aspect = _spatial_aspect_ratio(fig)
    _no_bg = dict(showbackground=False)
    layout_kw = dict(
        scene=dict(
            xaxis=dict(title="x (m)", **_no_bg),
            yaxis=dict(title="z (m)", **_no_bg),
            zaxis=dict(title=label, **_no_bg),
            aspectmode="manual",
            aspectratio=aspect,
        ),
        legend_title="Member",
    )
    if title is _AUTO:
        layout_kw["title"] = f"{label} Diagram"
    elif title is not None:
        layout_kw["title"] = title
    if figsize is not None:
        layout_kw["width"] = figsize[0] * 100
        layout_kw["height"] = figsize[1] * 100

    fig.update_layout(**layout_kw)
    return fig


def _plotly_3d_def(
    ospgrillage_obj,
    result_obj,
    members,
    component="y",
    loadcase=None,
    *,
    fig=None,
    figsize=None,
    scale=1.0,
    title=_AUTO,
    show_supports=True,
):
    """Build an interactive 3D Plotly figure of deflected shapes.

    Each member is drawn as a ``Scatter3d`` trace with markers, accompanied
    by a dotted zero-baseline.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of analysis results.
    :param members: List of member group name strings to include.
    :param component: Displacement component (default ``"y"``).
    :param loadcase: Load case name.  ``None`` uses the first load case.
    :param fig: Existing Plotly ``Figure`` to add traces to.
    :param figsize: Figure size in inches ``(width, height)``.
    :param scale: Multiply plotted values by this factor.
    :param title: Plot title.  Default auto-generates from component.
        ``None`` suppresses the title.
    :returns: Interactive 3D figure.
    :rtype: :class:`plotly.graph_objects.Figure`
    """
    go = _import_plotly()
    if fig is None:
        fig = go.Figure()

    # Negate so downward deflection plots below the baseline.
    sign = -1.0

    colours = ["blue", "red", "green", "orange", "black", "purple", "brown", "grey"]
    trace_idx = 0
    _TRANSVERSE = ("transverse_slab", "start_edge", "end_edge")

    for member in members:
        n_groups = _num_z_groups(ospgrillage_obj, member)

        if member in _TRANSVERSE:
            # Transverse members: extract per-element displacement at end
            # nodes and draw short line segments across the deck width.
            try:
                colour = colours[trace_idx % len(colours)]
                nodes_dict = ospgrillage_obj.get_nodes()
                eletags = ospgrillage_obj.get_element(
                    member=member,
                    options="elements",
                )
                if ospgrillage_obj.model_type == "shell_beam":
                    ele_node_da = result_obj.ele_nodes_beam
                else:
                    ele_node_da = result_obj.ele_nodes

                all_x, all_y, all_v = [], [], []
                for ele in eletags:
                    en = ele_node_da.sel(Element=ele).values
                    node_tags = en.flatten().astype(int).tolist()
                    for nd in node_tags:
                        c = nodes_dict[nd]["coordinate"]
                        if loadcase:
                            d = float(
                                result_obj.displacements.sel(
                                    Component=component,
                                    Node=nd,
                                    Loadcase=loadcase,
                                ).values
                            )
                        else:
                            d = float(
                                result_obj.displacements.sel(
                                    Component=component,
                                    Node=nd,
                                )[0].values
                            )
                        all_x.append(c[0])
                        all_y.append(c[2])
                        all_v.append(d * scale * sign)
                    # Insert None to break line between elements
                    all_x.append(None)
                    all_y.append(None)
                    all_v.append(None)

                fig.add_trace(
                    go.Scatter3d(
                        x=all_x,
                        y=all_y,
                        z=all_v,
                        mode="lines",
                        line=dict(color=colour, width=3),
                        name=member,
                    )
                )
                trace_idx += 1
            except (KeyError, ValueError, IndexError):
                pass  # member not available for this model type
            continue

        for zg in range(n_groups):
            try:
                xx, zz, vals = _extract_def_data(
                    ospgrillage_obj,
                    result_obj,
                    member,
                    component,
                    loadcase,
                    z_group_num=zg,
                )
            except (KeyError, ValueError, IndexError):
                continue  # member not available for this model type
            colour = colours[trace_idx % len(colours)]
            trace_name = member if n_groups == 1 else f"{member} [{zg+1}]"
            sv = np.array(vals) * scale * sign

            fig.add_trace(
                go.Scatter3d(
                    x=xx,
                    y=zz,
                    z=sv.tolist(),
                    mode="lines+markers",
                    line=dict(color=colour, width=4),
                    marker=dict(size=3, color=colour),
                    name=trace_name,
                )
            )
            # Baseline
            fig.add_trace(
                go.Scatter3d(
                    x=xx,
                    y=zz,
                    z=[0.0] * len(vals),
                    mode="lines",
                    line=dict(color=colour, width=1, dash="dot"),
                    showlegend=False,
                )
            )
            trace_idx += 1

    # Support markers on the zero-baseline
    if show_supports:
        supports = _extract_support_data(ospgrillage_obj)
        from collections import defaultdict

        by_type = defaultdict(list)
        for sup in supports:
            by_type[sup["fixity_type"]].append(sup)
        for ftype, sups in sorted(by_type.items()):
            symbol, colour, sz = _SUPPORT_STYLE_PLOTLY.get(ftype, ("x", "purple", 6))
            sx = [s["x"] for s in sups]
            sy = [s["z"] for s in sups]
            sz_vals = [0.0] * len(sups)  # supports sit on the baseline
            fig.add_trace(
                go.Scatter3d(
                    x=sx,
                    y=sy,
                    z=sz_vals,
                    mode="markers",
                    marker=dict(
                        symbol=symbol,
                        size=sz,
                        color=colour,
                        line=dict(color="black", width=1),
                    ),
                    name=f"support ({ftype})",
                )
            )

    aspect = _spatial_aspect_ratio(fig)
    _no_bg = dict(showbackground=False)
    layout_kw = dict(
        scene=dict(
            xaxis=dict(title="x (m)", **_no_bg),
            yaxis=dict(title="z (m)", **_no_bg),
            zaxis=dict(title=f"displacement ({component})", **_no_bg),
            aspectmode="manual",
            aspectratio=aspect,
        ),
        legend_title="Member",
    )
    if title is _AUTO:
        layout_kw["title"] = f"Deflection ({component})"
    elif title is not None:
        layout_kw["title"] = title
    if figsize is not None:
        layout_kw["width"] = figsize[0] * 100
        layout_kw["height"] = figsize[1] * 100

    fig.update_layout(**layout_kw)
    return fig


# ---------------------------------------------------------------------------
# Matplotlib plotting functions
# ---------------------------------------------------------------------------
def plot_force(
    ospgrillage_obj,
    result_obj=None,
    component=None,
    member: str = None,
    option: str = "elements",
    loadcase: str = None,
    *,
    figsize=None,
    ax=None,
    scale: float = 1.0,
    title=_AUTO,
    color: str = "k",
    fill: bool = True,
    alpha: float = 0.4,
    show: bool = False,
    show_supports: bool = False,
):
    """
    Plot a force diagram for a grillage model result for a specified component and load case.

    .. note::
        For "shell_beam" model type, the function only plots the force diagrams for beam elements only.

    :param ospgrillage_obj: Grillage model object.
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of results.
    :type result_obj: xarray DataSet
    :param component: Force component to plot (e.g. ``"Mz"``, ``"Fy"``).
    :type component: str
    :param member: Member group name (required).
    :type member: str
    :param option: Element query option.
    :type option: str
    :param loadcase: Load case name.  If ``None``, uses the first load case.
    :type loadcase: str
    :param figsize: Figure size in inches ``(width, height)``.
        Ignored when *ax* is provided.
    :type figsize: tuple, optional
    :param ax: Existing matplotlib Axes to plot on.  When provided the
        function draws on this axes instead of creating a new figure.
    :type ax: :class:`~matplotlib.axes.Axes`, optional
    :param scale: Multiply plotted values by this factor (e.g. ``0.001``
        to convert N to kN).
    :type scale: float
    :param title: Plot title.  Default (``_AUTO``) uses the member name.
        Pass a string to override, or ``None`` to suppress the title.
    :type title: str or None
    :param color: Line / fill colour.
    :type color: str
    :param fill: If ``True`` (default), shade the area under the diagram.
    :type fill: bool
    :param alpha: Fill transparency (0 = transparent, 1 = opaque).
    :type alpha: float
    :param show: If ``True``, call ``plt.show()`` before returning.
    :type show: bool
    :param show_supports: If ``True``, draw support markers on the zero
        baseline.  Default ``False``.
    :type show_supports: bool
    :returns: Matplotlib axes (use ``ax.get_figure()`` to obtain the figure).
    :rtype: :class:`~matplotlib.axes.Axes`
    """
    if member is None:
        raise ValueError("Missing argument: member= is required")

    all_xx, _all_zz, all_values = _extract_force_data(
        ospgrillage_obj,
        result_obj,
        component,
        member,
        loadcase,
        option,
    )

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    for xx, vals in zip(all_xx, all_values):
        scaled = vals * scale
        ax.plot(xx, scaled, "-", color=color)
        if fill:
            ax.fill_between(xx, scaled, np.zeros_like(scaled), color=color, alpha=alpha)

    if title is _AUTO:
        ax.set_title(member)
    elif title is not None:
        ax.set_title(title)
    if show_supports:
        supports = _extract_support_data(ospgrillage_obj)
        for sup in supports:
            marker, colour, sz = _SUPPORT_STYLE_MPL.get(
                sup["fixity_type"], ("D", "purple", 7)
            )
            ax.plot(
                sup["x"],
                0,
                marker=marker,
                color=colour,
                markersize=sz,
                markeredgecolor="black",
                markeredgewidth=0.5,
                zorder=5,
            )

    ax.set_xlabel("x (m) ")
    ax.set_ylabel(component)
    fig.tight_layout()

    if show:
        plt.show()

    return ax


def _plot_def_mpl(
    ospgrillage_obj,
    result_obj=None,
    member: str = None,
    component: str = None,
    option: str = "nodes",
    loadcase: str = None,
    *,
    figsize=None,
    ax=None,
    scale: float = 1.0,
    title=_AUTO,
    color: str = "b",
    show: bool = False,
    show_supports: bool = False,
):
    """
    Plot a displacement diagram for a grillage model result for a specified component and load case.

    .. note::
        For "shell_beam" model type, the function only plots the force diagrams for beam elements only.

    :param ospgrillage_obj: Grillage model object.
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of results.
    :type result_obj: xarray DataSet
    :param component: Displacement component (default ``"y"``).
    :type component: str
    :param member: Member group name (required).
    :type member: str
    :param option: Node query option, either ``"nodes"`` or ``"element"``.
    :type option: str
    :param loadcase: Load case name.  If ``None``, uses the first load case.
    :type loadcase: str
    :param figsize: Figure size in inches ``(width, height)``.
        Ignored when *ax* is provided.
    :type figsize: tuple, optional
    :param ax: Existing matplotlib Axes to plot on.  When provided the
        function draws on this axes instead of creating a new figure.
    :type ax: :class:`~matplotlib.axes.Axes`, optional
    :param scale: Multiply plotted values by this factor.
    :type scale: float
    :param title: Plot title.  Default (``_AUTO``) uses the member name.
        Pass a string to override, or ``None`` to suppress the title.
    :type title: str or None
    :param color: Line colour.
    :type color: str
    :param show: If ``True``, call ``plt.show()`` before returning.
    :type show: bool
    :returns: Matplotlib axes (use ``ax.get_figure()`` to obtain the figure).
    :rtype: :class:`~matplotlib.axes.Axes`
    """
    if member is None:
        raise ValueError("Missing argument: member= is required")

    dis_comp = component if component is not None else "y"
    xx_list, _zz_list, values_list = _extract_def_data(
        ospgrillage_obj,
        result_obj,
        member,
        dis_comp,
        loadcase,
        option,
    )

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    scaled = np.array(values_list) * scale
    ax.plot(xx_list, scaled, "-", color=color)

    if show_supports:
        supports = _extract_support_data(ospgrillage_obj)
        for sup in supports:
            marker, colour, sz = _SUPPORT_STYLE_MPL.get(
                sup["fixity_type"], ("D", "purple", 7)
            )
            ax.plot(
                sup["x"],
                0,
                marker=marker,
                color=colour,
                markersize=sz,
                markeredgecolor="black",
                markeredgewidth=0.5,
                zorder=5,
            )

    if title is _AUTO:
        ax.set_title(member)
    elif title is not None:
        ax.set_title(title)
    ax.set_xlabel("x (m) ")
    ax.set_ylabel(dis_comp)
    fig.tight_layout()

    if show:
        plt.show()

    return ax


# ---------------------------------------------------------------------------
# Member selection (bitflag enum)
# ---------------------------------------------------------------------------
class Members(enum.Flag):
    """Bitflag enum for selecting which grillage member groups to plot.

    Individual members can be combined with ``|``::

        og.Members.EDGE_BEAM | og.Members.INTERIOR_MAIN_BEAM

    Pre-defined composites are available for convenience::

        og.Members.LONGITUDINAL   # all four longitudinal member types
        og.Members.TRANSVERSE     # transverse slab + start/end edges
        og.Members.ALL            # everything
    """

    EDGE_BEAM = enum.auto()
    EXTERIOR_MAIN_BEAM_1 = enum.auto()
    INTERIOR_MAIN_BEAM = enum.auto()
    EXTERIOR_MAIN_BEAM_2 = enum.auto()
    START_EDGE = enum.auto()
    END_EDGE = enum.auto()
    TRANSVERSE_SLAB = enum.auto()

    # Convenience composites
    LONGITUDINAL = (
        EDGE_BEAM | EXTERIOR_MAIN_BEAM_1 | INTERIOR_MAIN_BEAM | EXTERIOR_MAIN_BEAM_2
    )
    TRANSVERSE = START_EDGE | END_EDGE | TRANSVERSE_SLAB
    ALL = LONGITUDINAL | TRANSVERSE


# Mapping between flag values and internal member name strings.
_MEMBER_NAME_MAP = {
    Members.EDGE_BEAM: "edge_beam",
    Members.EXTERIOR_MAIN_BEAM_1: "exterior_main_beam_1",
    Members.INTERIOR_MAIN_BEAM: "interior_main_beam",
    Members.EXTERIOR_MAIN_BEAM_2: "exterior_main_beam_2",
    Members.START_EDGE: "start_edge",
    Members.END_EDGE: "end_edge",
    Members.TRANSVERSE_SLAB: "transverse_slab",
}

# Reverse map: name string → flag (for backward-compatible str input).
_NAME_TO_MEMBER = {v: k for k, v in _MEMBER_NAME_MAP.items()}


def _resolve_members(member, backend="plotly"):
    """Convert a *member* argument into a list of member-name strings.

    Parameters
    ----------
    member : str, Members, or None
        * ``None`` — use default set (backend-dependent).
        * ``str``  — single member name (backward-compatible).
        * ``Members`` flag — one or more members combined with ``|``.
    backend : str
        ``"plotly"`` defaults to :attr:`Members.ALL`; ``"matplotlib"``
        defaults to :attr:`Members.LONGITUDINAL`.

    Returns
    -------
    list[str]
        Ordered list of member name strings.
    """
    if member is None:
        flag = Members.ALL if backend == "plotly" else Members.LONGITUDINAL
    elif isinstance(member, str):
        if member not in _NAME_TO_MEMBER:
            raise ValueError(
                f"Unknown member {member!r}. "
                f"Valid names: {list(_NAME_TO_MEMBER.keys())}"
            )
        flag = _NAME_TO_MEMBER[member]
    elif isinstance(member, Members):
        flag = member
    else:
        raise TypeError(
            f"member must be str, Members, or None, got {type(member).__name__}"
        )

    # Decompose the composite flag into individual members, preserving
    # the declaration order of the enum.
    return [_MEMBER_NAME_MAP[m] for m in Members if m in flag and m in _MEMBER_NAME_MAP]


# ---------------------------------------------------------------------------
# Convenience plotting wrappers
# ---------------------------------------------------------------------------


def plot_bmd(
    ospgrillage_obj,
    result_obj=None,
    members=None,
    loadcase=None,
    backend="matplotlib",
    **kwargs,
):
    """Plot bending moment diagram (Mz) for selected member groups.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of results.
    :param members: Which members to plot.

        * ``None`` (default) — all members (plotly) or longitudinal only
          (matplotlib).
        * A member name string such as ``"interior_main_beam"`` — single
          member (backward-compatible).
        * A :class:`Members` flag such as ``Members.LONGITUDINAL`` or
          ``Members.EDGE_BEAM | Members.INTERIOR_MAIN_BEAM`` — any
          combination.
    :type members: str, Members, or None
    :param loadcase: Load case name. If ``None``, uses the first load case.
    :param backend: ``"matplotlib"`` (default, static) or ``"plotly"``
        (interactive 3D).
    :param \\**kwargs: Forwarded to the underlying renderer.  See
        :func:`plot_force` (matplotlib) or the Plotly builder for accepted
        keyword arguments such as *figsize*, *ax*, *scale*, *title*,
        *color*, *fill*, *alpha*, and *show*.
    :returns: Single axes when *members* is a string, else list of axes.
        For ``backend="plotly"``, returns a single
        :class:`plotly.graph_objects.Figure`.
    """
    resolved = _resolve_members(members, backend)
    if backend == "plotly":
        show = kwargs.pop("show", True)
        plotly_kw = {
            k: v
            for k, v in kwargs.items()
            if k
            in (
                "figsize",
                "scale",
                "title",
                "alpha",
                "fill",
                "fill_alpha",
                "show_supports",
            )
        }
        plotly_kw["fig"] = kwargs.get("ax", None)
        fig = _plotly_3d_force(
            ospgrillage_obj,
            result_obj,
            component="Mz",
            members=resolved,
            loadcase=loadcase,
            comp_label="Mz",
            **plotly_kw,
        )
        if show:
            _show_plotly_fig(fig)
            return None
        return fig
    # matplotlib path — single string returns one axes (backward compat)
    if isinstance(members, str):
        return plot_force(
            ospgrillage_obj,
            result_obj,
            component="Mz",
            member=members,
            loadcase=loadcase,
            **kwargs,
        )
    figs = []
    for m in resolved:
        try:
            figs.append(
                plot_force(
                    ospgrillage_obj,
                    result_obj,
                    component="Mz",
                    member=m,
                    loadcase=loadcase,
                    **kwargs,
                )
            )
        except (ValueError, KeyError, IndexError):
            pass
    return figs


def plot_sfd(
    ospgrillage_obj,
    result_obj=None,
    members=None,
    loadcase=None,
    backend="matplotlib",
    **kwargs,
):
    """Plot shear force diagram (Fy) for selected member groups.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of results.
    :param members: Which members to plot.

        * ``None`` (default) — all members (plotly) or longitudinal only
          (matplotlib).
        * A member name string such as ``"interior_main_beam"`` — single
          member (backward-compatible).
        * A :class:`Members` flag such as ``Members.LONGITUDINAL`` or
          ``Members.EDGE_BEAM | Members.INTERIOR_MAIN_BEAM`` — any
          combination.
    :type members: str, Members, or None
    :param loadcase: Load case name. If ``None``, uses the first load case.
    :param backend: ``"matplotlib"`` (default, static) or ``"plotly"``
        (interactive 3D).
    :param \\**kwargs: Forwarded to the underlying renderer.  See
        :func:`plot_force` for accepted keyword arguments.
    :returns: Single axes when *members* is a string, else list of axes.
        For ``backend="plotly"``, returns a single
        :class:`plotly.graph_objects.Figure`.
    """
    resolved = _resolve_members(members, backend)
    if backend == "plotly":
        show = kwargs.pop("show", True)
        plotly_kw = {
            k: v
            for k, v in kwargs.items()
            if k
            in (
                "figsize",
                "scale",
                "title",
                "alpha",
                "fill",
                "fill_alpha",
                "show_supports",
            )
        }
        plotly_kw["fig"] = kwargs.get("ax", None)
        fig = _plotly_3d_force(
            ospgrillage_obj,
            result_obj,
            component="Fy",
            members=resolved,
            loadcase=loadcase,
            comp_label="Fy",
            **plotly_kw,
        )
        if show:
            _show_plotly_fig(fig)
            return None
        return fig
    # matplotlib path — single string returns one axes (backward compat)
    if isinstance(members, str):
        return plot_force(
            ospgrillage_obj,
            result_obj,
            component="Fy",
            member=members,
            loadcase=loadcase,
            **kwargs,
        )
    figs = []
    for m in resolved:
        try:
            figs.append(
                plot_force(
                    ospgrillage_obj,
                    result_obj,
                    component="Fy",
                    member=m,
                    loadcase=loadcase,
                    **kwargs,
                )
            )
        except (ValueError, KeyError, IndexError):
            pass
    return figs


def plot_def(
    ospgrillage_obj,
    result_obj=None,
    members=None,
    loadcase=None,
    backend="matplotlib",
    **kwargs,
):
    """Plot vertical deflection (y-displacement) for selected member groups.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of results.
    :param members: Which members to plot.

        * ``None`` (default) — all members (plotly) or longitudinal only
          (matplotlib).
        * A member name string such as ``"interior_main_beam"`` — single
          member (backward-compatible).
        * A :class:`Members` flag such as ``Members.LONGITUDINAL`` or
          ``Members.EDGE_BEAM | Members.INTERIOR_MAIN_BEAM`` — any
          combination.
    :type members: str, Members, or None
    :param loadcase: Load case name. If ``None``, uses the first load case.
    :param backend: ``"matplotlib"`` (default, static) or ``"plotly"``
        (interactive 3D).
    :param \\**kwargs: Forwarded to the underlying renderer.  See
        :func:`plot_force` for accepted keyword arguments.
    :returns: Single axes when *members* is a string, else list of axes.
        For ``backend="plotly"``, returns a single
        :class:`plotly.graph_objects.Figure`.
    """
    resolved = _resolve_members(members, backend)
    if backend == "plotly":
        show = kwargs.pop("show", True)
        plotly_kw = {
            k: v
            for k, v in kwargs.items()
            if k in ("figsize", "scale", "title", "show_supports")
        }
        plotly_kw["fig"] = kwargs.get("ax", None)
        fig = _plotly_3d_def(
            ospgrillage_obj,
            result_obj,
            members=resolved,
            component="y",
            loadcase=loadcase,
            **plotly_kw,
        )
        if show:
            _show_plotly_fig(fig)
            return None
        return fig
    # matplotlib path — filter to def-compatible kwargs (no fill/alpha)
    def_kw = {
        k: v
        for k, v in kwargs.items()
        if k in ("figsize", "ax", "scale", "title", "color", "show", "show_supports")
    }
    # Single string returns one axes (backward compat)
    if isinstance(members, str):
        return _plot_def_mpl(
            ospgrillage_obj,
            result_obj,
            member=members,
            component="y",
            loadcase=loadcase,
            **def_kw,
        )
    figs = []
    for m in resolved:
        try:
            figs.append(
                _plot_def_mpl(
                    ospgrillage_obj,
                    result_obj,
                    member=m,
                    component="y",
                    loadcase=loadcase,
                    **def_kw,
                )
            )
        except (ValueError, KeyError, IndexError):
            pass
    return figs


def plot_tmd(
    ospgrillage_obj,
    result_obj=None,
    members=None,
    loadcase=None,
    backend="matplotlib",
    **kwargs,
):
    """Plot torsion moment diagram (Mx) for selected member groups.

    :param ospgrillage_obj: Grillage model object.
    :param result_obj: xarray DataSet of results.
    :param members: Which members to plot.

        * ``None`` (default) — all members (plotly) or longitudinal only
          (matplotlib).
        * A member name string such as ``"interior_main_beam"`` — single
          member (backward-compatible).
        * A :class:`Members` flag such as ``Members.LONGITUDINAL`` or
          ``Members.EDGE_BEAM | Members.INTERIOR_MAIN_BEAM`` — any
          combination.
    :type members: str, Members, or None
    :param loadcase: Load case name. If ``None``, uses the first load case.
    :param backend: ``"matplotlib"`` (default, static) or ``"plotly"``
        (interactive 3D).
    :param \\**kwargs: Forwarded to the underlying renderer.  See
        :func:`plot_force` (matplotlib) or the Plotly builder for accepted
        keyword arguments such as *figsize*, *ax*, *scale*, *title*,
        *color*, *fill*, *alpha*, and *show*.
    :returns: Single axes when *members* is a string, else list of axes.
        For ``backend="plotly"``, returns a single
        :class:`plotly.graph_objects.Figure`.
    """
    resolved = _resolve_members(members, backend)
    if backend == "plotly":
        show = kwargs.pop("show", True)
        plotly_kw = {
            k: v
            for k, v in kwargs.items()
            if k
            in (
                "figsize",
                "scale",
                "title",
                "alpha",
                "fill",
                "fill_alpha",
                "show_supports",
            )
        }
        plotly_kw["fig"] = kwargs.get("ax", None)
        fig = _plotly_3d_force(
            ospgrillage_obj,
            result_obj,
            component="Mx",
            members=resolved,
            loadcase=loadcase,
            comp_label="Mx",
            **plotly_kw,
        )
        if show:
            _show_plotly_fig(fig)
            return None
        return fig
    # matplotlib path — single string returns one axes (backward compat)
    if isinstance(members, str):
        return plot_force(
            ospgrillage_obj,
            result_obj,
            component="Mx",
            member=members,
            loadcase=loadcase,
            **kwargs,
        )
    figs = []
    for m in resolved:
        try:
            figs.append(
                plot_force(
                    ospgrillage_obj,
                    result_obj,
                    component="Mx",
                    member=m,
                    loadcase=loadcase,
                    **kwargs,
                )
            )
        except (ValueError, KeyError, IndexError):
            pass
    return figs


# ---------------------------------------------------------------------------
# Model geometry plotting
# ---------------------------------------------------------------------------

# Support type classification from fixity vectors.
_FIXITY_CLASSIFICATION = {
    (1, 1, 1, 0, 0, 0): "pin",
    (0, 1, 1, 0, 0, 0): "roller",
    (1, 1, 1, 1, 1, 1): "fixed",
}

# Visual style per support type — (marker, colour, size).
_SUPPORT_STYLE_MPL = {
    "pin": ("^", "green", 10),
    "roller": ("o", "orange", 8),
    "fixed": ("s", "red", 8),
    "spring": ("v", "magenta", 9),
    "other": ("D", "purple", 7),
}
_SUPPORT_STYLE_PLOTLY = {
    "pin": ("diamond", "green", 8),
    "roller": ("circle", "orange", 7),
    "fixed": ("square", "red", 8),
    "spring": ("diamond-open", "magenta", 8),
    "other": ("x", "purple", 6),
}


def _extract_support_data(grillage_obj):
    """Return node positions and support types for boundary-condition drawing.

    Mirrors the logic of
    :meth:`~ospgrillage.osp_grillage.OspGrillage._write_op_fix` so the
    visualisation matches the actual constraints applied to the model.

    Returns
    -------
    list[dict]
        Each dict has keys ``node_tag``, ``x``, ``y``, ``z``,
        ``fixity_type`` (``"pin"`` / ``"roller"`` / ``"fixed"`` /
        ``"other"``).
    """
    mesh = grillage_obj.Mesh_obj
    node_spec = mesh.node_spec
    support_type_dict = grillage_obj.edge_support_type_dict

    # Determine which attribute stores the node → edge-group mapping.
    edge_recorder = getattr(mesh, "edge_node_recorder", {})

    # Nodes to skip — mirrors the condition in _write_op_fix:
    #   z_group in common_z_group_element[0]  →  pass (no fix applied)
    skip_z_groups = set()
    czge = getattr(mesh, "common_z_group_element", None)
    if czge and 0 in czge:
        skip_z_groups = set(czge[0])

    # Identify nodes that have spring supports.  spring_node_pairs maps
    # support_node → original_node; the *support* nodes are the ones that
    # carry the fixity and sit in edge_node_recorder after set_spring_support.
    spring_support_nodes = set(getattr(grillage_obj, "spring_node_pairs", {}).keys())

    supports = []
    for node_tag, edge_group_num in edge_recorder.items():
        if node_tag not in node_spec:
            continue
        # Skip nodes that _write_op_fix skips.
        z_grp = node_spec[node_tag].get("z_group")
        if z_grp is not None and z_grp in skip_z_groups:
            continue

        coord = node_spec[node_tag]["coordinate"]

        if node_tag in spring_support_nodes:
            fixity_type = "spring"
        else:
            fixity_vec = support_type_dict.get(edge_group_num, [0] * 6)
            fixity_tuple = tuple(int(v) for v in fixity_vec)
            fixity_type = _FIXITY_CLASSIFICATION.get(fixity_tuple, "other")

        supports.append(
            {
                "node_tag": node_tag,
                "x": coord[0],
                "y": coord[1],
                "z": coord[2],
                "fixity_type": fixity_type,
            }
        )

    return supports


# Colour palette for member groups (one per member type).
_MEMBER_COLOURS = {
    "edge_beam": "grey",
    "exterior_main_beam_1": "blue",
    "interior_main_beam": "green",
    "exterior_main_beam_2": "blue",
    "start_edge": "red",
    "end_edge": "red",
    "transverse_slab": "orange",
}
_DEFAULT_COLOUR = "black"


def _extract_mesh_data(grillage_obj):
    """Return element geometry grouped by member name.

    Returns
    -------
    data : dict[str, list[tuple]]
        ``{member_name: [(node_i_xyz, node_j_xyz, ele_tag), ...]}``
    all_nodes : dict[int, list]
        ``{node_tag: [x, y, z]}``
    quads : list[tuple]
        ``[(c1, c2, c3, c4), ...]`` where each ``ci`` is ``[x, y, z]``.
        Non-empty only for shell-type meshes.
    """
    mesh = grillage_obj.Mesh_obj
    node_spec = mesh.node_spec
    z_group_map = grillage_obj.common_grillage_element_z_group

    data = {}  # member_name -> list of (coord_i, coord_j, ele_tag)
    all_nodes = {}  # node_tag -> [x, y, z]

    def _add_elements(member_name, ele_list):
        entries = data.setdefault(member_name, [])
        for ele in ele_list:
            tag, ni, nj = ele[0], ele[1], ele[2]
            ci = node_spec[ni]["coordinate"]
            cj = node_spec[nj]["coordinate"]
            entries.append((ci, cj, tag))
            all_nodes[ni] = ci
            all_nodes[nj] = cj

    # Longitudinal members (edge_beam, exterior_main_beam_1, interior, exterior_2)
    for member_name in [
        "edge_beam",
        "exterior_main_beam_1",
        "interior_main_beam",
        "exterior_main_beam_2",
    ]:
        if member_name not in z_group_map:
            continue
        for z_idx in z_group_map[member_name]:
            if z_idx in mesh.z_group_to_ele:
                _add_elements(member_name, mesh.z_group_to_ele[z_idx])

    # Start / end edges
    for member_name in ["start_edge", "end_edge"]:
        if member_name not in z_group_map:
            continue
        for edge_idx in z_group_map[member_name]:
            if edge_idx in mesh.edge_group_to_ele:
                _add_elements(member_name, mesh.edge_group_to_ele[edge_idx])

    # Transverse slab
    _add_elements("transverse_slab", mesh.trans_ele)

    # Shell quad elements and rigid links (only present for ShellLinkMesh)
    quads = []
    links = []  # list of (slab_coord, beam_coord) pairs
    if hasattr(grillage_obj, "shell_element_command_list"):
        grid = getattr(mesh, "grid_number_dict", {})
        for node_list in grid.values():
            # Each entry is [n1, n2, n3, n4] (may contain [] for degenerate grids)
            valid = [n for n in node_list if isinstance(n, (int, float))]
            if len(valid) >= 3:
                coords = [node_spec[n]["coordinate"] for n in valid]
                quads.append(tuple(coords))
                for n in valid:
                    all_nodes[n] = node_spec[n]["coordinate"]

        # Rigid links: link_dict maps offset beam node → [slab_node1, slab_node2]
        link_dict = getattr(mesh, "link_dict", {})
        for beam_node, slab_nodes in link_dict.items():
            bc = node_spec[beam_node]["coordinate"]
            all_nodes[beam_node] = bc
            for sn in slab_nodes:
                sc = node_spec[sn]["coordinate"]
                links.append((sc, bc))
                all_nodes[sn] = sc

    return data, all_nodes, quads, links


def _plot_model_matplotlib(
    grillage_obj,
    *,
    figsize=None,
    ax=None,
    title=_AUTO,
    show_nodes=True,
    show_node_labels=False,
    show_element_labels=False,
    color_by_member=True,
    show_supports=True,
    show_rigid_links=True,
    show=False,
):
    """Render a 2-D plan view (x vs z) of the grillage mesh."""
    data, all_nodes, quads, links = _extract_mesh_data(grillage_obj)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    # Draw shell quad patches (if shell model)
    if quads:
        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection

        patches = []
        for coords in quads:
            # coords is tuple of [x,y,z] lists — plot in x-z plane
            verts = [(c[0], c[2]) for c in coords]
            patches.append(Polygon(verts, closed=True))
        pc = PatchCollection(
            patches,
            facecolor="lightblue",
            edgecolor="steelblue",
            linewidth=0.4,
            alpha=0.5,
        )
        ax.add_collection(pc)

    # Draw beam elements grouped by member
    for member_name, elements in data.items():
        colour = (
            _MEMBER_COLOURS.get(member_name, _DEFAULT_COLOUR)
            if color_by_member
            else "k"
        )
        for ci, cj, etag in elements:
            ax.plot([ci[0], cj[0]], [ci[2], cj[2]], "-", color=colour, linewidth=1)
            if show_element_labels:
                mx = 0.5 * (ci[0] + cj[0])
                mz = 0.5 * (ci[2] + cj[2])
                ax.text(
                    mx, mz, str(etag), fontsize=6, color="red", ha="center", va="center"
                )

    # Draw nodes
    if show_nodes or show_node_labels:
        for ntag, coord in all_nodes.items():
            if show_nodes:
                ax.plot(coord[0], coord[2], ".", color="k", markersize=3)
            if show_node_labels:
                ax.text(
                    coord[0],
                    coord[2],
                    f" {ntag}",
                    fontsize=5,
                    color="blue",
                    ha="left",
                    va="bottom",
                )

    # Draw support symbols
    if show_supports:
        supports = _extract_support_data(grillage_obj)
        plotted_types = set()
        for sup in supports:
            marker, colour, sz = _SUPPORT_STYLE_MPL.get(
                sup["fixity_type"], ("D", "purple", 7)
            )
            ax.plot(
                sup["x"],
                sup["z"],
                marker=marker,
                color=colour,
                markersize=sz,
                markeredgecolor="black",
                markeredgewidth=0.5,
                linestyle="none",
                zorder=5,
            )
            plotted_types.add(sup["fixity_type"])

    # Add legends — members and supports are separated for clarity.
    from matplotlib.lines import Line2D

    member_handles = []
    if quads:
        member_handles.append(
            Line2D(
                [0],
                [0],
                color="steelblue",
                linewidth=1,
                marker="s",
                markerfacecolor="lightblue",
                markersize=6,
                label="shell_slab",
            )
        )
    for member_name in data:
        colour = (
            _MEMBER_COLOURS.get(member_name, _DEFAULT_COLOUR)
            if color_by_member
            else "k"
        )
        member_handles.append(
            Line2D([0], [0], color=colour, linewidth=1, label=member_name)
        )
    if member_handles and color_by_member:
        leg1 = ax.legend(
            handles=member_handles,
            fontsize=7,
            loc="upper left",
            title="Members",
            title_fontsize=7,
        )
        ax.add_artist(leg1)

    if show_supports and plotted_types:
        sup_handles = []
        for ftype in sorted(plotted_types):
            marker, colour, sz = _SUPPORT_STYLE_MPL.get(ftype, ("D", "purple", 7))
            sup_handles.append(
                Line2D(
                    [0],
                    [0],
                    linestyle="none",
                    marker=marker,
                    color=colour,
                    markeredgecolor="black",
                    markeredgewidth=0.5,
                    markersize=sz,
                    label=ftype,
                )
            )
        ax.legend(
            handles=sup_handles,
            fontsize=7,
            loc="upper right",
            title="Supports",
            title_fontsize=7,
        )

    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m)")
    ax.set_aspect("equal")

    if title is _AUTO:
        ax.set_title("Grillage Model")
    elif title is not None:
        ax.set_title(title)

    fig.tight_layout()
    if show:
        plt.show()

    return ax


def _plot_model_plotly(
    grillage_obj,
    *,
    fig=None,
    figsize=None,
    title=_AUTO,
    show_nodes=True,
    show_node_labels=False,
    show_element_labels=False,
    color_by_member=True,
    show_supports=True,
    show_rigid_links=True,
    show=False,
):
    """Render an interactive 3-D model view with Plotly."""
    go = _import_plotly()
    if fig is None:
        fig = go.Figure()

    data, all_nodes, quads, links = _extract_mesh_data(grillage_obj)

    colours = ["grey", "blue", "green", "blue", "red", "red", "orange"]
    colour_map = dict(zip(_MEMBER_COLOURS.keys(), colours))

    # Draw elements grouped by member
    for member_name, elements in data.items():
        colour = colour_map.get(member_name, "black") if color_by_member else "black"
        xs, ys, zs = [], [], []
        for ci, cj, etag in elements:
            xs.extend([ci[0], cj[0], None])
            ys.extend([ci[2], cj[2], None])
            zs.extend([-ci[1], -cj[1], None])
        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="lines",
                line=dict(color=colour, width=3),
                name=member_name,
            )
        )

    # Shell quad surface (if shell model)
    if quads:
        # Build a flat vertex list and triangle indices (each quad → 2 triangles)
        vx, vy, vz = [], [], []
        i_idx, j_idx, k_idx = [], [], []
        base = 0
        for coords in quads:
            for c in coords:
                vx.append(c[0])
                vy.append(c[2])  # z → plotly y
                vz.append(-c[1])  # y → plotly z (negated: beams below slab)
            n = len(coords)
            if n == 4:
                i_idx.extend([base, base])
                j_idx.extend([base + 1, base + 2])
                k_idx.extend([base + 2, base + 3])
            elif n == 3:
                i_idx.append(base)
                j_idx.append(base + 1)
                k_idx.append(base + 2)
            base += n
        fig.add_trace(
            go.Mesh3d(
                x=vx,
                y=vy,
                z=vz,
                i=i_idx,
                j=j_idx,
                k=k_idx,
                color="lightblue",
                opacity=0.5,
                name="shell_slab",
            )
        )

    # Rigid links (slab ↔ offset beam)
    if show_rigid_links and links:
        lx, ly, lz = [], [], []
        for sc, bc in links:
            lx.extend([sc[0], bc[0], None])
            ly.extend([sc[2], bc[2], None])  # z → plotly y
            lz.extend([-sc[1], -bc[1], None])  # y → plotly z (negated)
        fig.add_trace(
            go.Scatter3d(
                x=lx,
                y=ly,
                z=lz,
                mode="lines",
                line=dict(color="grey", width=1),
                name="rigid_link",
                showlegend=True,
            )
        )

    # Node markers
    if show_nodes:
        ntags = list(all_nodes.keys())
        nx = [all_nodes[n][0] for n in ntags]
        ny = [all_nodes[n][2] for n in ntags]
        nz = [-all_nodes[n][1] for n in ntags]
        text = [str(n) for n in ntags] if show_node_labels else None
        mode = "markers+text" if show_node_labels else "markers"
        fig.add_trace(
            go.Scatter3d(
                x=nx,
                y=ny,
                z=nz,
                mode=mode,
                marker=dict(size=2, color="black"),
                text=text,
                textposition="top center",
                textfont=dict(size=8),
                name="nodes",
                showlegend=False,
            )
        )

    # Element labels at midpoints
    if show_element_labels:
        ex, ey, ez, etexts = [], [], [], []
        for member_name, elements in data.items():
            for ci, cj, etag in elements:
                ex.append(0.5 * (ci[0] + cj[0]))
                ey.append(0.5 * (ci[2] + cj[2]))
                ez.append(-0.5 * (ci[1] + cj[1]))
                etexts.append(str(etag))
        fig.add_trace(
            go.Scatter3d(
                x=ex,
                y=ey,
                z=ez,
                mode="text",
                text=etexts,
                textfont=dict(size=7, color="red"),
                showlegend=False,
            )
        )

    # Support markers
    if show_supports:
        supports = _extract_support_data(grillage_obj)
        from collections import defaultdict

        by_type = defaultdict(list)
        for sup in supports:
            by_type[sup["fixity_type"]].append(sup)
        for ftype, sups in sorted(by_type.items()):
            symbol, colour, sz = _SUPPORT_STYLE_PLOTLY.get(ftype, ("x", "purple", 6))
            sx = [s["x"] for s in sups]
            sy = [s["z"] for s in sups]  # model z → plotly y
            sz_vals = [-s["y"] for s in sups]  # model y → plotly z (negated)
            fig.add_trace(
                go.Scatter3d(
                    x=sx,
                    y=sy,
                    z=sz_vals,
                    mode="markers",
                    marker=dict(
                        symbol=symbol,
                        size=sz,
                        color=colour,
                        line=dict(color="black", width=1),
                    ),
                    name=f"support ({ftype})",
                )
            )

    # Layout — equal axis scaling (true proportions)
    _no_bg = dict(showbackground=False)
    layout_kw = dict(
        scene=dict(
            xaxis=dict(title="x (m)", **_no_bg),
            yaxis=dict(title="z (m)", **_no_bg),
            zaxis=dict(title="y (m)", **_no_bg),
            aspectmode="data",
        ),
        legend_title="Member",
    )
    if title is _AUTO:
        layout_kw["title"] = "Grillage Model"
    elif title is not None:
        layout_kw["title"] = title
    if figsize is not None:
        layout_kw["width"] = figsize[0] * 100
        layout_kw["height"] = figsize[1] * 100

    fig.update_layout(**layout_kw)

    if show:
        _show_plotly_fig(fig)
        return None  # avoid Jupyter double-display via _repr_html_

    return fig


def plot_model(grillage_obj, *, backend="matplotlib", **kwargs):
    """Plot the grillage mesh geometry.

    :param grillage_obj: Grillage model (must have been created with
        :meth:`~ospgrillage.osp_grillage.OspGrillage.create_osp_model`).
    :type grillage_obj: OspGrillage
    :param backend: ``"matplotlib"`` (default, 2-D plan view) or
        ``"plotly"`` (interactive 3-D).
    :type backend: str
    :param figsize: Figure size in inches ``(width, height)``.
        Ignored when *ax* is provided.
    :type figsize: tuple, optional
    :param ax: Existing matplotlib Axes to plot on (matplotlib backend only).
    :type ax: :class:`~matplotlib.axes.Axes`, optional
    :param fig: Existing Plotly Figure to add traces to (plotly backend only).
    :type fig: :class:`plotly.graph_objects.Figure`, optional
    :param title: Plot title.  Default auto-generates ``"Grillage Model"``.
        Pass a string to override, or ``None`` to suppress.
    :type title: str or None
    :param show_nodes: Show node markers.  Default ``True``.
    :type show_nodes: bool
    :param show_node_labels: Annotate node tags.  Default ``False``.
    :type show_node_labels: bool
    :param show_element_labels: Annotate element tags.  Default ``False``.
    :type show_element_labels: bool
    :param color_by_member: Colour elements by member group.  Default ``True``.
    :type color_by_member: bool
    :param show_supports: Draw support symbols at restrained nodes.
        Default ``True``.
    :type show_supports: bool
    :param show_rigid_links: Draw rigid-link connections (shell-beam models
        only).  Default ``True``.
    :type show_rigid_links: bool
    :param show: If ``True``, display the plot immediately.
        Defaults to ``True`` for plotly, ``False`` for matplotlib
        (matplotlib inline backends auto-display).
    :type show: bool
    :returns: Matplotlib axes (use ``ax.get_figure()`` for the figure) or
        Plotly figure (``None`` when ``show=True``).
    :rtype: :class:`~matplotlib.axes.Axes` or
        :class:`plotly.graph_objects.Figure` or None
    """
    if backend == "plotly":
        plotly_kw = {
            k: v
            for k, v in kwargs.items()
            if k
            in (
                "fig",
                "figsize",
                "title",
                "show_nodes",
                "show_node_labels",
                "show_element_labels",
                "color_by_member",
                "show_supports",
                "show_rigid_links",
                "show",
            )
        }
        # Default show=True for plotly (Jupyter doesn't always auto-render)
        plotly_kw.setdefault("show", True)
        # Map ax → fig for consistency with other convenience wrappers
        if "ax" in kwargs and "fig" not in plotly_kw:
            plotly_kw["fig"] = kwargs["ax"]
        return _plot_model_plotly(grillage_obj, **plotly_kw)
    elif backend == "matplotlib":
        mpl_kw = {
            k: v
            for k, v in kwargs.items()
            if k
            in (
                "figsize",
                "ax",
                "title",
                "show_nodes",
                "show_node_labels",
                "show_element_labels",
                "color_by_member",
                "show_supports",
                "show_rigid_links",
                "show",
            )
        }
        return _plot_model_matplotlib(grillage_obj, **mpl_kw)
    else:
        raise ValueError(f"Unknown backend: {backend!r}. Use 'matplotlib' or 'plotly'.")


class PostProcessor:
    """Class to post-process the results from an of ospgrillage analysis result.

    As of version 0.2.0, ospgrillage compiles results using Xarray module.
    """

    def __init__(self, grillage, result):  # Union[xr.DataArray, xr.Dataset]
        """Init the class"""
        # store main vars
        self.grillage = grillage
        self.result = result

        # init vars
        self.shape_function_obj = ShapeFunction()

    def get_arbitrary_displacements(
        self, point: list, shape_function_type: str = "linear", component: str = "y"
    ):
        """Returns displacement (translation and rotational) from an arbitrary point by interpolation

        param point: list of coordinate. Default three elements [x,y=0,z]
        type point: list
        param component: Displacement component. Default "y"
        type component: str
        param shape_function_type: The shape function for interpolation. Default "linear"
        type shape_function_type: str
        """
        node_displacements = []
        node_coordinate = []

        # get the list of four nodes where arbitrary point lies
        nodes, grid_number = self.grillage._get_point_load_nodes(
            point=point
        )  # list of nodes
        if nodes is None:
            raise ValueError("Point is outside bridge mesh")

        # get results of each node of four nodes
        for node in nodes:
            node_displacements.append(
                self.result.sel(
                    Component=component,
                    Node=node,
                )
                .displacements.to_numpy()
                .tolist()[0]
            )
            node_coordinate.append(self.grillage.get_nodes(number=node))

        # interpolate for vertical displacement
        x = np.array([coord[0] for coord in node_coordinate])
        z = np.array([coord[2] for coord in node_coordinate])

        # get natural coordinate of point in grid
        eta, zeta = solve_zeta_eta(
            xp=point[0],
            zp=point[2],
            x1=x[0],
            z1=z[0],
            x2=x[1],
            z2=z[1],
            x3=x[2],
            z3=z[2],
            x4=x[3],
            z4=z[3],
        )
        if shape_function_type == "linear":
            shape_func = self.shape_function_obj.linear_shape_function(
                eta=eta, zeta=zeta
            )
        else:
            shape_func, _, _ = self.shape_function_obj.hermite_shape_function_2d(
                eta=eta, zeta=zeta
            )

        return sum([a * b for a, b, in zip(shape_func, node_displacements)])
