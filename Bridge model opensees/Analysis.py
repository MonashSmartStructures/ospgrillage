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

class Grillage:
    """
    Grillage class
    """
    def __init__(self,bridgepickle,truckclass):
        """

        :param bridgepickle:
        :param truckclass:
        """
        # assign attributes
        self.bridgepickle = bridgepickle
        self.truckclass = truckclass

        # initialize Bridge class object within Grillage class instance
        self.OPBridge = OpenseesModel(self.bridgepickle["Nodedetail"], self.bridgepickle["Connectivitydetail"],
                                        self.bridgepickle["beamelement"], self.bridgepickle["Memberdetail"],
                                      self.bridgepickle["Member transformation"])
        # assign properties of concrete and steel
        self.OPBridge.assign_material_prop(self.bridgepickle["concreteprop"], self.bridgepickle["steelprop"])
        # send attribute to OP framework to create OP model
        self.OPBridge.create_Opensees_model()

        # time series and load pattern options
        self.OPBridge.time_series()
        self.OPBridge.loadpattern()

        # plot
        #PlotWizard.plotOPmodel(self)

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
        if self.truckclass.direction == 'X':
            no_point = (self.truckclass.initial_position[0] + self.truckclass.travel_length
                        + self.truckclass.increment) / self.truckclass.increment
            self.refPos_X = np.linspace(self.truckclass.initial_position[0], self.truckclass.travel_length,
                                        round(no_point))
        else:  # direction is 'Z'
            no_point = (self.truckclass.initial_position[1] + self.truckclass.travel_length
                        + self.truckclass.increment) / self.truckclass.increment
            self.refPos_X = np.linspace(self.truckclass.initial_position[1], self.truckclass.travel_length,
                                        round(no_point))

        # get coordinate of axles with respective to bridge global coordinates
        X, Y, weights = self.getaxles()
        # for each positions in X and Y,
        for r in range(len(self.refPos_X)):
            # 1 recreate model instance
            self.recreatemodel_instance()
            # 2 position axle loads at r onto OPmodel
            for i in range(len(X)):
                # for each value is X (Xlist) for truck axle, impose load into model
                currentpos = [X[i] + self.refPos_X[r], Y[i] + self.truckclass.initial_position[1]]

                # set axle load onto bridge
                try:
                    self.OPBridge.load_position(currentpos, weights[i])
                    print("axles position =",currentpos)
                except:
                    print("axle no longer on bridge, move to next")

            # 3 run analysis for current position
            runmoving(self)
            # save (BM. SF)

    def getaxles(self):
        """
        Function to return the coordinates of truck axles with respect
        to the global coordinate of the bridge model
        :return:
        """
        # create array of truck axles X and Y lists for plotting
        xList = [0, 0] # starting position of ref axle , X coors
        yList = [0, self.truckclass.width] # Y coors
        weightlist = [self.truckclass.axles_weight[0], self.truckclass.axles_weight[0]]  # first two axles ,first two inputs of axlwts
        for i in range(len(xList)):
            last = xList[-1]  # get last element in current xList array
            for ycoor in [0, self.truckclass.width]:
                xList.append(last + self.truckclass.axles_spacing[i])  # add axl spacing to current last element of xList
                yList.append(ycoor)  # add y coord to list
                weightlist.append(self.truckclass.axles_weight[i + 1])
        return xList, yList, weightlist

    def recreatemodel_instance(self):
        """
        Function for moving load analysis:
        Due to the single instance of bridge model in Openseespy, the model
        has to be recreated after each time increment of analysis.

        Warning:
        This is only limited for static grillage analysis. For dynamic analysis
        (with time integration) this method is not feasible

        :return:
        """
        # method to run in between each time step of moving truck analysis
        self.OPBridge = OpenseesModel(self.bridgepickle["Nodedetail"], self.bridgepickle["Connectivitydetail"],
                                      self.bridgepickle["beamelement"], self.bridgepickle["Memberdetail"],
                                      self.bridgepickle["Member transformation"])
        self.OPBridge.assign_material_prop(self.bridgepickle["concreteprop"], self.bridgepickle["steelprop"])
        self.OPBridge.create_Opensees_model()

        # in future version expand analysis recorder option
        self.OPBridge.time_series()
        self.OPBridge.loadpattern()

# static methods
# method to run OP framework - callable from outside of class instance

def runmoving(self):
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

    # create SOE
    ops.system("BandGeneral")
    ops.test('NormDispIncr', 1.0e-6, 6,2,0)
    # create DOF number
    ops.numberer("RCM")

    # create constraint handler
    ops.constraints("Transformation")

    # create integrator
    ops.integrator("LoadControl", 1.0)

    # create ODB object to record analysis results
    #postproc.Get_Rendering.createODB("testbridge","loadcase")

    # create algorithm
    ops.algorithm("Linear")

    # create analysis object
    ops.analysis("Static")

    # perform the analysis
    ops.analyze(1)
    # print features of model
    #printModel()
    #PlotWizard.plotOPmodel(self)
    print([ops.nodeDisp(1)[1], ops.nodeDisp(2)[1], ops.nodeDisp(3)[1],
           ops.nodeDisp(4)[1], ops.nodeDisp(5)[1], ops.nodeDisp(6)[1],
           ops.nodeDisp(7)[1], ops.nodeDisp(8)[1], ops.nodeDisp(9)[1],
           ops.nodeDisp(10)[1], ops.nodeDisp(11)[1]])
    print(ops.eleResponse(1, 'xlocal'))

    # PlotWizard.py commands
    #PlotWizard.plotBending(self)
    #PlotWizard.plotShear(self)

    PlotWizard.plotDeformation(self)
    breakpoint()
#-----------------------------------------------------------------------------------------------------------------------
# Procedure to run grillage analysis (OP framework)
# imports
# - Analysis.py, Bridgemodel.py,PlotWizard.py,Vehicle.py
# 1 load bridge pickle file

with open("save.p","rb") as f:
    refbridge = pickle.load(f)

refbridge["beamelement"] = 'elasticBeamColumn'

# 1.1 Procedure to create bridge pickle file + save

 # 2 Define truck properties
axlwts = [800,3200,3200] # axle weights
axlspc = [2,2]          # axl spacings
axlwidth = 2            #axl widths

initial_position = [2,0]    # start position of truck (ref point axle)
travel_length = 50          # distance (m)
increment = 2               # truck location increment
direction = "X"             # travel direction (global)

# 3 create truck object
RefTruck = vehicle(axlwts,axlspc,axlwidth,initial_position,travel_length, increment,direction)
# 4 pass pickle file of bridge and truck object to grillage class.
RefBridge = Grillage(refbridge,RefTruck)
# 5 run method to perform analysis
RefBridge.perfromtruckanalysis()
breakpoint()
# 5 plots and save results
