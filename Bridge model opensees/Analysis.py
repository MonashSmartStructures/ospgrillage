# -*-encoding: utf-8 -*-
"""
Grillage analysis module containing base class for Opensees Grillage analysis
framework. It also contains methods for moving load analysis which iterates
over the load path of the Vehicle class, which is passed into.
"""
from Bridgemodel import *
from Vehicle import *
import pickle
import PlotWizard


class MovingLoadAnalysis:
    """
    Moving force class. This class handles a given bridge model (either an Opensees model or otherwise specified)
    , a moving vehicle object (class) and a traverse pattern (namedtuple).
    """

    def __init__(self, bridge_obj, truck_class, traverse_prop, analysis_type):
        """
        Create the MovingLoadAnalysis class object
        :param bridge_obj:
        :param truckclass:
        """
        # assign attributes
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
        else:
            pass

        # plot
        # PlotWizard.plotOPmodel(self)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def perfromtruckanalysis(self):
        """
        Code runs truck loading input
        :return:
        """
        self.truckloading()

    # order
    def truckloading(self):
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
        X, Y, weights = self.getaxles()
        # for each positions in X and Y,
        for index, r in enumerate(self.refPos_X):
            # 1 recreate model instance
            # self.recreatemodel_instance()
            if index != 0:  # not first step
                self.remove_previous_analysis()
            # 2 position axle loads at r onto OPmodel
            for i in range(len(X)):
                # for each value is X (Xlist) for truck axle, impose load into model
                currentpos = [X[i] + self.refPos_X[index], Y[i] + self.traverse_prop.initial_position[1]]

                # set axle load onto bridge
                try:
                    self.OPBridge.load_position(currentpos, weights[i])
                    print("axles position =", currentpos)
                except:
                    print("axle no longer on bridge, move to next")

            # 3 run analysis for current position

            op_run_moving(self)


    def remove_previous_analysis(self):
        ops.remove('loadPattern',1)

        self.OPBridge.loadpattern(pat="Plain")

    def getaxles(self):
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
# method to run OP framework - callable from outside of class instance

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

    # PlotWizard.py commands
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

with open("save.p", "rb") as f:
    refbridge = pickle.load(f)

refbridge["beamelement"] = 'elasticBeamColumn'

# 1.1 Procedure to create bridge pickle file + save

# 2 Define truck properties
axlwts = [800, 3200, 3200]  # axle weights
axlspc = [2, 2]  # axl spacings
axlwidth = 2  # axl widths

initial_position = [2, 0]  # start position of truck (ref point axle)
travel_length = 50  # distance (m)
increment = 2  # truck location increment
direction = "X"  # travel direction (global)
analysis_type = "Opensees"

# 2.1 traverse properties
move_path = namedtuple('Travel_path', ('initial_position', 'length', 'increment', 'direction'))
move_1 = move_path([2, 0],50,2,"X")
# 3 create truck object
RefTruck = vehicle(axlwts, axlspc, axlwidth, initial_position, travel_length, increment, direction)
# 4 pass pickle file of bridge and truck object to grillage class.
RefBridge = MovingLoadAnalysis(refbridge, RefTruck, move_1,analysis_type)
# 5 run method to perform analysis
RefBridge.perfromtruckanalysis()
breakpoint()
# 5 plots and save results
