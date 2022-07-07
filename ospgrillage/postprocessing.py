# -*- coding: utf-8 -*-
"""
This module contains functions and classes related to post processing processes.
The post processing module is an addition to the currently available post processing
module of OpenSeesPy - this module fills in gaps to
* create envelope from xarray DataSet
* plot force and deflection diagrams from xarray DataSets
"""

import matplotlib.pyplot as plt
import opsvis as opsv
import numpy as np

import openseespyvis.Get_Rendering as opsplt


def create_envelope(**kwargs):
    """
    Interface for users to create an :class:`Envelope` object.

    The constructor takes an `xarray` DataSet and kwargs for enveloping options.

    :param ds: Data set from `get_results()`
    :type ds: Xarray
    :param kwargs: Keyword arguments see below.

    :keyword:

    * array: either 'displacement' or 'forces'
    * value_mode: - True or False
    * query_mode: - True or False
    * extrema: either "min" or "max"
    * elements:
    * nodes
    * array
    * load_effect

    :return: :class:`Envelope` Object
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
        :param kwargs: See below for keyword arguments.

        :keyword:

        * array: either 'displacement' or 'forces'
        * value_mode (`Bool`): Flag for envelope to return raw values - default True
        * query_mode (`Bool`): Flag for envelope to return loadcase coordinate for
                               maxima - default False
        * extrema (`str`): either "min" or "max"
        * elements:
        * nodes
        * array
        * load_effect

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
        self.format_string = None
        # main command strings

        self.eval_string = (
            'self.ds.{array}.{xarray_command}(dim="Loadcase").sel({component_command})'
        )
        self.component_string = "Component={},"
        self.element_string = "Element={},"
        self.load_case_string = ""
        self.component_command = ""  # instantiate command string
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
            raise Exception(
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

        # convert to lists
        if not isinstance(self.elements, list):
            self.elements = [self.elements]
        if not isinstance(self.component, list):
            self.component = [self.component]

        # check if empty
        if None not in self.elements:
            self.element_string.format(self.elements)
        if None not in self.component:
            self.component_string.format(self.component)

        # check the combinations of inputs for query
        if not ("{" in self.element_string and "{" in self.component_string):
            self.component_command = self.component_string + self.element_string
        elif "{" in self.element_string and "{" not in self.component_string:
            self.component_command = self.component_string
        elif not ("{" in self.element_string and "{" in self.component_string):
            self.component_command = self.element_string

        # format xarray command to be eval()
        self.format_string = self.eval_string.format(
            array=self.array,
            xarray_command=self.selected_xarray_command,
            component_command=self.component_command,
        )

    def get(self):
        """

        :return: The enveloped `xarray` object.
        :rtype: xarray
        """

        return eval(self.format_string)


def plot_force(
    ospgrillage_obj,
    result_obj=None,
    component=None,
    member: str = None,
    option: str = "elements",
    loadcase: str = None,
):
    """
    Plots a force diagram of the provided :class:`~ospgrillage.osp_grillage.OspGrillage` and
    :class:`xarray` (result) objects for a specified `component` and
    :class:`~ospgrillage.load.LoadCase`'s.

    .. note::
        For "shell_beam" model type, the function only plots the force diagrams for beam elements only.


    :param ospgrillage_obj: Grillage model object
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of results
    :type result_obj: xarray DataSet
    :param component: Force component to plot
    :type component: str
    :param member: member
    :type member: str
    :param option:
    :type option: str
    :param loadcase: name string of load case to plot. If not provided, plots from first load case in the order of
                     xarray loadcase coordinate
    :type loadcase: str
    :return: Matplotlib figure
    :rtype: (:class:`~matplotlib.figure.Figure`)
    """
    # instantiate component dict
    comp_dict = {"Fx": 0, "Fy": 1, "Fz": 2, "Mx": 3, "My": 4, "Mz": 5}
    comp_factor = {"Fx": 1, "Fy": 1, "Fz": 1, "Mx": 1, "My": 1, "Mz": -1}
    if member is None:
        print("Missing argument member=")
        return
    component_index = component
    if not isinstance(component, int):
        component_index = comp_dict[component]
    factor = comp_factor[component]
    fig, ax = plt.subplots()  # create plot window
    nodes = ospgrillage_obj.get_nodes()  # extract node information of model
    eletag = ospgrillage_obj.get_element(
        member=member, options=option
    )  # get ele tag of grillage elements
    # loop ele tags of ele
    if ospgrillage_obj.model_type == "shell_beam":
        force_result = result_obj.forces_beam
    else:
        force_result = result_obj.forces

    for ele in eletag:
        # get force components
        if loadcase:
            ele_components = force_result.sel(
                Loadcase=loadcase,
                Element=ele,
                Component=[
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
                ],
            ).values
        else:
            ele_components = force_result.sel(
                Element=ele,
                Component=[
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
                ],
            )[0].values
        # get nodes of ele
        if ospgrillage_obj.model_type == "shell_beam":
            ele_node = result_obj.ele_nodes_shell.sel(Element=ele)
            if all(np.isnan(result_obj.ele_nodes_shell.sel(Element=ele))):
                ele_node = result_obj.ele_nodes_beam.sel(Element=ele)
            # remove nans elements in the 4 node list (shell) for beam (2 elements)
            ele_node = ele_node[~np.isnan(ele_node)]
        else:
            ele_node = result_obj.ele_nodes.sel(Element=ele)

        # create arrays for x y and z for plots
        xx = [nodes[n]["coordinate"][0] for n in ele_node.values]
        yy = [nodes[n]["coordinate"][1] for n in ele_node.values]
        zz = [nodes[n]["coordinate"][2] for n in ele_node.values]
        # use ops_vis module to get force distribution on element
        s, al = opsv.section_force_distribution_3d(
            ex=xx, ey=yy, ez=zz, pl=ele_components
        )
        # plot element force component
        ax.plot(xx, s[:, component_index] * factor, "-k")
        # fill area between horizontal axis and line
        ax.fill_between(
            xx, s[:, component_index] * factor, [0, 0], color="k", alpha=0.4
        )
    ax.set_title(member)
    ax.set_xlabel("x (m) ")
    ax.set_ylabel(component)
    fig.tight_layout()
    # fig.show()

    return fig


def plot_defo(
    ospgrillage_obj,
    result_obj=None,
    member: str = None,
    component: str = None,
    option: str = "nodes",
    loadcase: str = None,
):
    """
    Plots displacements of the provided :class:`~ospgrillage.osp_grillage.OspGrillage` and
    :class:`xarray` (result) objects for a specified `component` and
    :class:`~ospgrillage.load.LoadCase`'s.

    .. note::
        For "shell_beam" model type, the function only plots the force diagrams for beam elements only.


    :param ospgrillage_obj: Grillage model object
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of results
    :type result_obj: xarray DataSet
    :param component: Force component to plot
    :type component: str
    :param member: member
    :type member: str
    :param option: option of :func:`~ospgrillage.osp_grillage.OspGrillage.get_element`,
                   either "nodes" or "element" (Default nodes)
    :type option: str
    :param loadcase: name string of load case to plot. If not provided, plots from first load case in the order of
                 xarray loadcase coordinate
    :type loadcase: str
    :return: Matplotlib figure
    :rtype: (:class:`~matplotlib.figure.Figure`)
    """
    # init vars
    previous_def = None
    previous_xx = None
    previous_zz = None

    # check options
    if option is None:
        plot_option = "nodes"
    else:
        plot_option = option
    # check member, if None, return None, Users need to define the member str to plot
    if member is None:
        print("Missing argument for member= - no plot is returned")
        return
    # check if component is provided, else default to
    dis_comp = component
    if component is None:
        dis_comp = "dy"  # default to dy

    fig, ax = plt.subplots()
    # get all node information
    nodes = ospgrillage_obj.get_nodes()  # dictionary containing information of nodes
    # get specific nodes for specific element
    nodes_to_plot = ospgrillage_obj.get_element(member=member, options=plot_option)[
        0
    ]  # list of list
    # loop through nodes to plot
    for node in nodes_to_plot:
        if loadcase:
            disp = result_obj.displacements.sel(
                Component=dis_comp, Node=node, Loadcase=loadcase
            ).values  # get node disp value
        else:
            disp = result_obj.displacements.sel(Component=dis_comp, Node=node)[
                0
            ].values  # get node disp value
        xx = nodes[node]["coordinate"][0]  # get x coord
        zz = nodes[node]["coordinate"][2]  # get z coord (for 3D plots)
        if previous_def is not None:
            ax.plot(
                [previous_xx, xx], [previous_def, disp], "-b"
            )  # plot a 1-D plot of all nodes in grillage element
        previous_def = disp
        previous_xx = xx
        previous_zz = zz
    ax.set_title(member)
    ax.set_xlabel("x (m) ")  # labels
    ax.set_ylabel(dis_comp)  # labels
    fig.tight_layout()
    # fig.show()

    return fig
