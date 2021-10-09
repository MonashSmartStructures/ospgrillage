# -*- coding: utf-8 -*-
"""
This module contains functions and classes related to post processing processes
"""

import matplotlib.pyplot as plt
import opsvis as opsv
import openseespyvis as opsplt

import ospgrillage


def create_envelope(**kwargs):
    """
    User interface function to create envelopes from data array
    :param kwargs:
    :return:
    """
    return Envelope(kwargs)


class Envelope:
    """
    Main class for envelope. This class takes a :class:`~ospgrillage.osp_grillage.OspGrillage` result
    `xarray`, enveloping the `xarray` based on user options, return a modified `xarray`.

    """

    def __init__(self, ds, load_effect: str = None, **kwargs):
        """
        The constructor takes an `xarray` DataSet and kwargs for enveloping options.

        :param ds: Data set from `get_results()`
        :type ds: Xarray
        :param kwargs: Keyword arguments see below.

        :keyword:

        * array
        * value_mode
        * query_mode
        * extrema
        * elements
        * nodes
        * array
        * load_effect

        """
        self.value = True
        self.ds = ds
        if ds is None:
            return

        # instantiate variables
        self.load_effect = load_effect  # array load effect either displacements or forces
        self.envelope_ds = None
        self.format_string = None
        # main command strings
        self.eval_string = "self.ds.{array}.{xarray_command}(dim=\"Loadcase\").sel({component_command})"
        self.component_string = "Component={},"
        self.element_string = "Element={},"
        self.load_case_string = ""
        self.component_command = ""  # instantiate command string
        # default xarray function name
        self.xarray_command = {"query": ["idxmax", "idxmin"], "minmax value": ["max", "min"],
                               "index": ["argmax", "argmin"]}
        self.selected_xarray_command = []
        # get keyword args
        self.elements = kwargs.get("elements", None)  # specific elements to query/envelope
        self.nodes = kwargs.get("nodes", None)  # specific nodes to query/envelope
        self.component = kwargs.get("load_effect", None)  # specific load effect to query
        self.array = kwargs.get("array", "displacements")
        self.value_mode = kwargs.get("value_mode", False)
        self.query_mode = kwargs.get("query_mode", True)  # default query mode
        self.extrema = kwargs.get("extrema", "max")

        # check variables
        if self.load_effect is None:
            raise Exception("Missing argument for load_effect=: Hint requires a namestring of load effect type based"
                            "on the Component dimension of the ospgrillage data set result format")

        # process variables
        self.extrema_index = 0 if self.extrema is "max" else 1  # minima
        if self.query_mode:
            self.selected_xarray_command = self.xarray_command["query"][self.extrema_index]
        elif self.value_mode:
            self.selected_xarray_command = self.xarray_command["minmax value"][self.extrema_index]
        else:  # default to argmax/ argmin
            self.selected_xarray_command = self.xarray_command["index"][self.extrema_index]

        # convert to lists
        if not isinstance(self.elements, list):
            self.elements = [self.elements]
        if not isinstance(self.component, list):
            self.component = [self.component]

        # check if empty
        if not None in self.elements:
            self.element_string.format(self.elements)
        if not None in self.component:
            self.component_string.format(self.component)

        # check the combinations of inputs for query
        if not ("{" in self.element_string and "{" in self.component_string):
            self.component_command = self.component_string + self.element_string
        elif "{" in self.element_string and not "{" in self.component_string:
            self.component_command = self.component_string
        elif not ("{" in self.element_string and "{" in self.component_string):
            self.component_command = self.element_string

        # format xarray command to be eval()
        self.format_string = self.eval_string.format(array=self.array, xarray_command=self.selected_xarray_command,
                                                     component_command=self.component_command)

    def get(self):
        """
        Function to return envelope of xarray given data set and enveloping options
        :return:
        """

        return eval(self.format_string)


def plot_bmd(ospgrillage_obj, result_obj=None,component = None,
              member: str = None, option: str = None):
    """
    Function to plot 2D diagrams from force component of :class:`~ospgrillage.osp_grillage.Result` object

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
    :return:
    """
    # TODO
    ax = plt.axes(projection='3d')  # create plot window
    nodes = ospgrillage_obj.get_nodes()  # extract node information of model
    eletag = ospgrillage_obj.get_element(member="exterior_main_beam_2",
                                         options="elements")  # get ele tag of grillage elements
    # loop ele tags of ele
    for ele in eletag:
        # get force components
        ele_components = result_obj.forces.sel(Element=ele,
                                               Component=["Vx_i", "Vy_i", "Vz_i", "Mx_i", "My_i", "Mz_i", "Vx_j",
                                                          "Vy_j", "Vz_j", "Mx_j", "My_j",
                                                          "Mz_j"])[0].values
        # get nodes of ele
        ele_node = result_obj.ele_nodes.sel(Element=ele)
        # create arrays for x y and z for plots
        xx = [nodes[n]['coordinate'][0] for n in ele_node.values]
        yy = [nodes[n]['coordinate'][1] for n in ele_node.values]
        zz = [nodes[n]['coordinate'][2] for n in ele_node.values]
        # use ops_vis module to get force distribution on element
        s, al = opsv.section_force_distribution_3d(ex=xx, ey=yy, ez=zz, pl=ele_components)
        # plot desire element force component
        ax.plot(xx, zz, s[:, 5])  # Here change int accordingly: {0:Fx,1:Fy,2:Fz,3:Mx,4:My,5:Mz}
    plt.xlabel("x (m) ")
    plt.ylabel("Mz (Nm)")
    plt.show()


def plot_defo(ospgrillage_obj, result_obj=None,
              member: str = None, component:str=None,option: str = None):
    """
    Function to plot 2D diagrams of displacement components from result xarray DataSet

    :param ospgrillage_obj: Grillage model object
    :type ospgrillage_obj: OspGrillage
    :param result_obj: xarray DataSet of results
    :type result_obj: xarray DataSet
    :param component: Force component to plot
    :type component: str
    :param member: member
    :type member: str
    :param option: option of :func:`~ospgrillage.osp_grillage.OspGrillage.get_element`, either "nodes" or "element"
                   (Default nodes)
    :type option: str
    """
    # instantiate variables
    previous_def = None
    previous_xx = None
    previous_zz = None

    # check options
    if option is None:
        plot_option = "nodes"
    else:
        plot_option = option
    # check member
    if member is None:
        return
    # check if component is provided, else default to
    dis_comp = component
    if component is None:
        dis_comp = "dy"  # default to dy

    # get all node information
    nodes = ospgrillage_obj.get_nodes()  # dictionary containing information of nodes
    # get specific nodes for specific element
    nodes_to_plot = ospgrillage_obj.get_element(member=member, options=plot_option)[0]  # list of list
    # loop through nodes to plot
    for node in nodes_to_plot:
        disp = result_obj.displacements.sel(Component=dis_comp, Node=node)[0].values  # get node disp value
        xx = nodes[node]['coordinate'][0]  # get x coord
        zz = nodes[node]['coordinate'][2]  # get z coord (for 3D plots)
        if previous_def is not None:
            plt.plot([previous_xx,xx], [previous_def,disp], '-b')  # here plot accordingly, we plot a 1-D plot of all nodes in grillage element
        previous_def = disp
        previous_xx = xx
        previous_zz = zz
    plt.title(member)
    plt.xlabel("x (m) ")  # labels
    plt.ylabel("dy (m)")  # labels
    plt.show()
