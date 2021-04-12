# -*-encoding: utf-8 -*-
"""
Grillage analysis module containing base class for Opensees Grillage analysis
framework. It also contains methods for moving load analysis which iterates
over the load path of the Vehicle class, which is passed into.
"""
from Bridgemodel import *
from Vehicle import *
import PlotWizard
from itertools import compress


class MovingLoadAnalysis:
    """
    Moving force class. This class handles a given bridge model (either an Opensees model or otherwise specified)
    , a moving vehicle object (class) and a traverse pattern (namedtuple).
    """

    def __init__(self, bridge_obj, truck_class, traverse_prop, analysis_type, op_wizard_obj=None):
        """
        Create the MovingLoadAnalysis class object
        :param bridge_obj: py file name of bridge generation created from GrillageGenerator class
        :param truck_class: vehicle class obj
        """
        # assign attributes
        self.op_wizard_obj = op_wizard_obj
        self.traverse_prop = traverse_prop
        self.truck_class = truck_class
        self.bridge_obj = bridge_obj

        if analysis_type == "Opensees":
            # initialize Bridge class object within Grillage class instance
            self.OPBridge = OpenseesModel(self.bridge_obj["Nodedetail"], self.bridge_obj["Connectivitydetail"],
                                          self.bridge_obj["beamelement"], self.bridge_obj["Memberdetail"],
                                          self.bridge_obj["Member transformation"])
            # assign properties of concrete and steel
            self.OPBridge.assign_material_prop(self.bridge_obj["concreteprop"], self.bridge_obj["steelprop"])
            # send attribute to OP framework to create OP model
            self.OPBridge.create_Opensees_model()

            # time series and load pattern options
            self.OPBridge.time_series(defSeries="Linear")
            self.OPBridge.loadpattern(pat="Plain")
        else:  # Add more options for bridge model types (e.g. matlab)
            __import__(self.bridge_obj)  # run file
            ops.timeSeries("Linear", 1)
            ops.pattern("Plain", 1, 1)

        # plot
        # PlotWizard.plotOPmodel(self)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def run_analysis(self):
        """
        Function to carry out moving load procedure

        :return:
        """
        #
        self.moving_static_analysis()

    # order
    def moving_static_analysis(self):
        """
        Truckloading directions is fixed at "X" and "Z" (orthogonal direction)
        future versions for varying direction (of given angle or customized) needs
        to be implemented
        :return:
        """
        # function to call moving force, with switcher depending on travelling direction : either X or Z direction
        if self.traverse_prop.direction == 'X':
            no_point = (self.traverse_prop.initial_position[0] + self.traverse_prop.length
                        + self.traverse_prop.increment) / self.traverse_prop.increment
            self.refPos_X = np.linspace(self.traverse_prop.initial_position[0], self.traverse_prop.length,
                                        round(no_point))
        else:  # direction is 'Z'
            no_point = (self.traverse_prop.initial_position[1] + self.traverse_prop.length
                        + self.traverse_prop.increment) / self.traverse_prop.increment
            self.refPos_X = np.linspace(self.traverse_prop.initial_position[1], self.traverse_prop.length,
                                        round(no_point))

        # get coordinate of axles with respective to bridge global coordinates
        X, Y, weights = self.get_axles()
        # for each positions in X and Y,
        for index, r in enumerate(self.refPos_X):
            if index != 0:  # not first step
                self.remove_previous_analysis()
            # 2 position axle loads at r onto OPmodel
            for i in range(len(X)):
                # for each value is X (Xlist) for truck axle, impose load into model
                currentpos = [X[i] + self.refPos_X[index], Y[i] + self.traverse_prop.initial_position[1]]

                # set axle load onto bridge                                         #### Note here provide options for
                #                                                                   #### different analysis model option
                try:
                    self.op_load_positioning(currentpos, weights[i])
                    self.OPBridge.load_position(currentpos, weights[i])
                    print("axles position =", currentpos)
                except:
                    print("axle no longer on bridge, move to next")
            # 3 run analysis for current position
            op_run_moving(self)

    def op_load_positioning(self, pos, axlwt):
        # function to implement load onto
        nl = self.op_search_nodes(pos)

    def op_search_nodes(self, pos):
        #            x
        #     1 O - - - - O 2
        #   z   |         |                 # notations and node search numbering
        #       |    x    |
        #     3 O - - - - O 4
        #
        # n1                # x 1                     z 3

        bool_list_2 = []
        for nodes in self.op_wizard_obj.Nodedata:
            # x                       # z
            if nodes[1] <= pos[0] and nodes[3] > pos[1]:
                bool_list_2.append(True)
            else:
                bool_list_2.append(False)

        res = list(compress(self.op_wizard_obj.Nodedata, bool_list_2))
        # pick x is largest, z is smallest
        t = extract(res, 3)
        n1 = max(list(compress(res, t == min(t))))

        bool_list_2 = []
        for nodes in self.op_wizard_obj.Nodedata:
            # x                       # z
            if nodes[1] > pos[0] and nodes[3] <= pos[1]:
                bool_list_2.append(True)
            else:
                bool_list_2.append(False)

        res = list(compress(self.op_wizard_obj.Nodedata, bool_list_2))
        t = extract(res, 3)
        n4 = min(list(compress(res, t == max(t))))
        # search elements which contain common nodes n1 and n2
        ops.eleNodes()
        return n1, n4

    def moving_transient(self):
        """

        :return:
        .. note::

            To be added in future versions
        """
        pass

    #

    def remove_previous_analysis(self):
        ops.remove('loadPattern', 1)

        self.OPBridge.loadpattern(pat="Plain")

    def get_axles(self):
        """
        Function to return the coordinates of truck axles with respect
        to the global coordinate of the bridge model. Callable outside of class for readable axle positions
        :return:
        """
        # create array of truck axles X and Y lists for plotting
        xList = [0, 0]  # starting position of ref axle , X coors
        yList = [0, self.truck_class.width]  # Y coors
        weightlist = [self.truck_class.axles_weight[0],
                      self.truck_class.axles_weight[0]]  # first two axles ,first two inputs of axlwts
        for i in range(len(xList)):
            last = xList[-1]  # get last element in current xList array
            for ycoor in [0, self.truck_class.width]:
                xList.append(
                    last + self.truck_class.axles_spacing[i])  # add axl spacing to current last element of xList
                yList.append(ycoor)  # add y coord to list
                weightlist.append(self.truck_class.axles_weight[i + 1])
        return xList, yList, weightlist


# static methods
# method to access Opensees software - callable from outside of class instance
def op_define_recorder():
    pass


def extract(lst, num):
    # static method to extract an element from a sublist - used for node and element searching procedures
    return [item[num] for item in lst]


def op_run_moving(self):
    """
    Code to call after Code implementing truck load onto bridge model
    (recreate_model and truck loading)
    The method communicates with Openseespy, running the inbuilt
    functions for static analysis

    :param self:
    :return:
    """
    # method calls OP instance methods - operating the methods and return outputs back to Grillage instance class

    # wipe analysis
    ops.wipeAnalysis()
    # ops.remove('loadPattern',1)
    # create recorder
    ops.recorder('Node', '-file', 'Disp.txt', '-time', '-node', 41, '-dof', 2, 'disp')
    # create SOE
    ops.system("BandGeneral")
    ops.test('NormDispIncr', 1.0e-6, 6, 2, 0)
    # create DOF number
    ops.numberer("RCM")

    # create constraint handler
    ops.constraints('Plain')

    # create integrator
    ops.integrator("LoadControl", 1.0)

    # create ODB object to record analysis results

    # create algorithm
    ops.algorithm("Linear")

    # create analysis object
    ops.analysis("Static")

    # perform the analysis
    ops.analyze(10)
    # Plotting features
    # printModel()
    # PlotWizard.plotOPmodel(self)
    # get readable displacements
    print([ops.nodeDisp(1)[1], ops.nodeDisp(2)[1], ops.nodeDisp(3)[1],
           ops.nodeDisp(4)[1], ops.nodeDisp(5)[1], ops.nodeDisp(6)[1],
           ops.nodeDisp(7)[1], ops.nodeDisp(8)[1], ops.nodeDisp(9)[1],
           ops.nodeDisp(10)[1], ops.nodeDisp(11)[1]])

    # Plotting command wrapper
    # PlotWizard.plotBending(self)
    # PlotWizard.plotShear(self)
    # ops.wipeAnalysis()
    PlotWizard.plotDeformation(self)

    breakpoint()


# -----------------------------------------------------------------------------------------------------------------------
# Procedure to run grillage analysis (OP framework)
# imports
# - Analysis.py, Bridgemodel.py,PlotWizard.py,Vehicle.py
# 1 load bridge pickle file

# with open("save.p", "rb") as f:
# refbridge = pickle.load(f)

# refbridge["beamelement"] = 'elasticBeamColumn'
# 1 Provide bridge model
refbridge = "BenchMark_op"
from RunScript import test_bridge  # import GrillageGenerator object created for op file

# 1.1 Procedure to create bridge model in Opensees

# 2 Define truck properties
axlwts = [800, 3200, 3200]  # axle weights
axlspc = [2, 2]  # axl spacings
axlwidth = 2  # axl widths

initial_position = [2, 0]  # start position of truck (ref point axle)
travel_length = 50  # distance (m)
increment = 2  # truck location increment
direction = "X"  # travel direction (global)
# model_option= "Opensees"
model_option = "Custom"
# 2.1 traverse properties
move_path = namedtuple('Travel_path', ('initial_position', 'length', 'increment', 'direction'))
move_1 = move_path([5, 2.5], 50, 2, "X")

# 3 create truck object
RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)
# 4 pass py file of bridge and truck object to MovingLoadAnalysis.
analysis = MovingLoadAnalysis(refbridge, RefTruck, move_1, model_option, test_bridge)
# 5 run method to perform analysis
analysis.run_analysis()
breakpoint()
# 5 plots and save results
