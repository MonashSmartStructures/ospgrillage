
import pandas as pd
import numpy as np
import math

class GrillageGenerator:
    def __init__(self,longdim,transdim,skew, numlonggrid, numtransgrid, cantileveredge):
        # global dimensions of grillage
        self.longdim = longdim   # span , also c/c between support bearings
        self.transdim = transdim # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        self.skew = skew         # angle in degrees
        # Properties of grillage
        self.numlonggird = numlonggrid      # number of longitudinal beams
        self.numtransgrid = numtransgrid    # number of grids for transverse members
        self.edgewidth = cantileveredge     # width of cantilever edge beam

        # geometric dependent properties
        self.width = None                   # to be calculated automatically based on skew
        self.spclonggirder = None           # to be automated
        self.spctransslab = None            # to be automated
        self.Nodedata = []                  # array like to be populated

        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.minlongspacing = 1
        self.maxlongspacing = 2
        self.mintransspacing = 1
        self.maxtransspacing = 1
        self.transtolongspacing = 1
        self.mingridlong = 9
        self.mingridtrans = 5
        self.orthomesh = False  # boolean for grillages with skew < 15-20 deg

        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.nox = None # array specifying custom coordinate of longitudinal nodes
        self.noz = None # array specifying custom coordinate of transverse nodes
        self.skewthreshold = 20 # threshold for grillage to generate nodes with orthogonal mesh (units degree)


        #run automations
        #1 node
        #2 Connectivity

    # node functions
    def Nodedatageneration(self):
        # calculate grillage width
        self.width = self.transdim * math.cos(self.skew / 180 * math.pi)  # determine width of grillage
        # check for orthogonal mesh requirement
        if self.orthomesh:
            # perform orthogonal meshing
            self.orthogonalmeshAutomation()
        else: # skew mesh requirement
            # perform repeated step generation
            self.skewmeshAutomation()
            pass

    def skewmeshAutomation(self):
        if self.nox == None: # check case where no special rule for slab spacing, proceed automation of node coordinates
            nox = np.linspace(0,self.longdim,self.numtransgrid)  #array like containing node x cooridnate

        # determine coordinate of longitudinal girders
        lastgirder = self.width - self.edgewidth  # coord of last girder
        noxgirder = np.linspace(self.edgewidth, lastgirder, self.numlonggird)
        step = np.hstack(np.hstack(0, noxgirder), self.width)

        #for step in range(0,len(self.longdim)+2): # +2 for edge beam nodes



    def orthogonalmeshAutomation(self):


        pass

    #Nodedata, ConnectivityData, beamtype, MemberData, memtrans

    # Element connectivity functions
    def ConnectivityAutomation(self):
        pass

    def MemberPropertyInput(self):
        pass

    # subfunctions
    def checktestvalues(self):
        pass

    def checkskew(self):
        if self.skew>self.skewthreshold:
            self.orthomesh = True

