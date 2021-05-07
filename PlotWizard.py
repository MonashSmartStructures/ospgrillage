import openseespy.postprocessing.Get_Rendering as opsplt
import matplotlib.pyplot as plt
import openseespy.postprocessing.ops_vis as opsv

# file containing functions adopting plot/visualization features
# from Opensees post processing package version 3.2.2.6
"""
Module containing static methods that handles Openseespy/postprocessing.ops_vis moodule

Note: Development of plot wizard is in alpha phase. To date, the wizard wrap certain basic ops_vis module commands.
User may opt to use the main ops_vis module for more comprehensive plotting features. 
"""


def plotOPmodel(self):
    """
    Function to plot model - showing options for nodes,
    test2
    """
    # Display active model with Node tags and elements
    opsplt.plot_model("nodes")


def plotBending(self):
    """
    Function to plot bending moment of model

    """
    Ew = {}
    sfacMy = 1.e-2
    minY, maxY = opsv.section_force_diagram_3d('Mz', Ew, sfacMy)
    plt.title(f'Bending moments Mz, max = {maxY:.2f}, min = {minY:.2f}')
    plt.show()


def plotShear(self):
    """

    :param self:
    :return:
    """
    Ew = {}
    sfacMy = 1.e-2
    minY, maxY = opsv.section_force_diagram_3d('Vy', Ew, sfacMy)
    plt.title(f'Bending moments My, max = {maxY:.2f}, min = {minY:.2f}')
    plt.show()


def plotDeformation(self):
    """

    :param self:
    :return:
    """
    fig_wi_he = 30., 20.
    sfac = 1
    nep = 17
    opsv.plot_defo(sfac, nep, fmt_interp='b-', az_el=(-68., 39.),
                   fig_wi_he=fig_wi_he, endDispFlag=0)
    plt.show()
    breakpoint()


def plot_section(op_gril_obj, list_input, char):
    """
    Function to plot element groups of model.
    :param op_gril_obj: an OpsGrillage class object
    :param list_input: str of element group following definitions in OpsGrillage
    :param char: str commands for matplotlib
    :return: plot all element groups with format according to str command parameter
    """
    if type(list_input) == int:
        listed = list_input
    else:  # list input is string
        listed = op_gril_obj.group_ele_dict[list_input]  # get the tag number of group
    for num, ele in enumerate(op_gril_obj.global_element_list):
        if ele[2] == listed:
            matches_i_x = [x[1] for x in op_gril_obj.Nodedata if ele[0] == x[0]]
            matches_i_z = [x[3] for x in op_gril_obj.Nodedata if ele[0] == x[0]]
            matches_j_x = [x[1] for x in op_gril_obj.Nodedata if ele[1] == x[0]]
            matches_j_z = [x[3] for x in op_gril_obj.Nodedata if ele[1] == x[0]]
            plt.plot([matches_i_x, matches_j_x], [matches_i_z, matches_j_z], char)

        else:
            pass


def plot_nodes(op_gril_ob, plot_args):
    # plot by accessing Nodedata attribute
    x = [sub[1] for sub in op_gril_ob.Nodedata]
    y = [sub[3] for sub in op_gril_ob.Nodedata]
    tag = [sub[0] for sub in op_gril_ob.Nodedata]
    model = plt.scatter(x, y)
    for point in range(0, len(x)):
        plt.text(x[point], y[point], tag[point], fontsize='xx-small')
    plt.axis('equal')
    return model
