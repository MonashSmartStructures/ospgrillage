from Bridgemodel import *
from Vehicle import *
import pickle

class Grillage:
    def __init__(self,bridgepickle,truckclass):
        # assign attributes
        self.bridgepickle = bridgepickle
        self.truckclass = truckclass

        # initialize Bridge class object within Grillage class instance
        self.OPBridge = OpenseesModel(self.bridgepickle["Nodedetail"], self.bridgepickle["Connectivitydetail"],
                                          self.bridgepickle["beamelement"], self.bridgepickle["Memberdetail"])
        self.OPBridge.assign_material_prop(self.bridgepickle["concreteprop"], self.bridgepickle["steelprop"])
        self.OPBridge.create_Opensees_model()

        # in future version expand analysis recorder option
        self.OPBridge.time_series()
        self.OPBridge.loadpattern()
        self.perfromtruckanalysis()
    def perfromtruckanalysis(self):
        self.truckloading()

    # order
    def truckloading(self):
        # create vehicle class
        # inputs:                axlwts, axlspc, axlwidth, start coordinate, increment, travel distance
        self.ModelledTruck = vehicle(self.truckclass.axles_weight, self.truckclass.axles_spacing, self.truckclass.width,
                                     self.truckclass.initial_position, self.truckclass.increment,self.truckclass.travel_length,
                                     self.truckclass.direction)

        # function to call moving force, with switcher depending on travelling direction : either X or Z direction
        if self.ModelledTruck.direction == 'X':
            no_point = (self.truckclass.initial_position[0] + self.truckclass.travel_length
                        + self.truckclass.increment) / self.truckclass.increment
        else: # direction is 'Z'
            no_point = (self.truckclass.initial_position[0] + self.truckclass.travel_length
                        + self.truckclass.increment) / self.truckclass.increment

        self.refPos_X = np.linspace(self.truckclass.initial_position[0], self.truckclass.travel_length,
                                    round(no_point))
        X, Y, weights = self.getaxles()
        # for each position,
        for r in range(len(self.refPos_X)):
            # 1 recreate model instance
            self.recreatemodel_instance()
            # 2 position axle loads at r onto OPmodel
            for i in range(len(X)):
                # for each value is X (Xlist) for truck axle, impose load into model
                currentpos = [X[i] + self.refPos_X[r], Y[i] + self.truckclass.initial_position[1]]
                self.OPBridge.load_position(currentpos, weights[i])

            # 3 run analysis
            runmoving(self)
            # save (BM. SF)

    def getaxles(self):
        # create array of truck axles X and Y lists for plotting
        xList = [0, 0]
        yList = [0, self.truckclass.width]
        weightlist = [self.truckclass.axles_weight[0], self.truckclass.axles_weight[0]]  # first two axles ,first two inputs of axlwts
        for i in range(len(axlspc)):
            last = xList[-1]  # get last element in current xList array
            for ycoor in [0, self.truckclass.width]:
                xList.append(last + self.truckclass.axles_spacing[i])  # add axl spacing to current last element of xList
                yList.append(ycoor)  # add y coord to list
                weightlist.append(self.truckclass.axles_weight[i + 1])
        return xList, yList, weightlist

    def recreatemodel_instance(self):
        # method to run in between each time step of moving truck analysis
        self.OPBridge = OpenseesModel(self.bridgepickle["Nodedetail"], self.bridgepickle["Connectivitydetail"],
                                      self.bridgepickle["beamelement"], self.bridgepickle["Memberdetail"])
        self.OPBridge.assign_material_prop(self.bridgepickle["concreteprop"], self.bridgepickle["steelprop"])
        self.OPBridge.create_Opensees_model()

        # in future version expand analysis recorder option
        self.OPBridge.time_series()
        self.OPBridge.loadpattern()

# static methods
# method to run OP framework - callable from outside of class instance
def runmoving(self):
    # method calls OP instance methods - operating the methods and return outputs back to Grillage instance class

    # wipe analysis
    wipeAnalysis()

    # create SOE
    system("BandSPD")

    # create DOF number
    numberer("RCM")

    # create constraint handler
    constraints("Plain")

    # create integrator
    integrator("LoadControl", 1.0)

    # create algorithm
    algorithm("Linear")

    # create analysis object
    analysis("Static")

    # perform the analysis
    analyze(1)
    print([nodeDisp(1)[1], nodeDisp(2)[1], nodeDisp(3)[1], nodeDisp(4)[1], nodeDisp(5)[1], nodeDisp(6)[1],
           nodeDisp(7)[1], nodeDisp(8)[1], nodeDisp(9)[1], nodeDisp(10)[1], nodeDisp(11)[1]])

#-----------------------------------------------------------------------------------------------------------------------
# Picklefile containing bridge


# refbridge = pickle.load(open( "save.p", "rb" ))
# # Truck properties
# axlwts = [800,3200,3200]
# # axlspc = [7,7]
# axlwidth = 5
# initial_position = [0,3.0875]
# travel_length = 50
# increment = 2
# direction = "X"
#
# # create truck
# RefTruck = vehicle(axlwts,axlspc,axlwidth,initial_position,travel_length, increment,direction)
# # load pickle file of bridge and pass truck class to grillage analysis class.
# Grillage(refbridge,RefTruck)
