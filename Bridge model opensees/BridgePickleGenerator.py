
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

        # instantiate matrices for geometric dependent properties
        self.width = None                   # to be calculated automatically based on skew
        self.breadth = None                 # to be calculated automatically based on skew
        self.spclonggirder = None           # to be automated
        self.spctransslab = None            # to be automated
        self.Nodedata = []                  # array like to be populated
        self.nox = []
        self.noz = []

        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.minlongspacing = 1  # default 1m
        self.maxlongspacing = 2  # default 1m
        self.mintransspacing = 1  # default 1m
        self.maxtransspacing = 1  # default 1m
        self.transtolongspacing = 1  # default 1m
        self.mingridlong = 9    # default 9 mesh
        self.mingridtrans = 5   # default 5 mesh
        self.orthomesh = False  # boolean for grillages with skew < 15-20 deg
        self.yelevation = 0 # default elevation of grillage wrt OPmodel coordinate system
        self.mingridortho = 3  # for orthogonal mesh (skew>skewthreshold) region of orthogonal area default 3

        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.noxspecial = None # array specifying custom coordinate of longitudinal nodes
        self.nozspecial = None # array specifying custom coordinate of transverse nodes
        self.skewthreshold = 20 # threshold for grillage to generate nodes with orthogonal mesh (units degree)


        #run automations
        #1 node
        #2 Connectivity

    # node functions
    def Nodedatageneration(self):
        # calculate grillage width
        self.width = self.transdim * math.cos(self.skew / 180 * math.pi)  # determine width of grillage
        # check for orthogonal mesh requirement
        self.checkskew()
        if self.orthomesh:
            # perform orthogonal meshing
            self.orthogonalmeshAutomation()
        else: # skew mesh requirement
            # perform repeated step generation
            self.skewmeshAutomation()


    def skewmeshAutomation(self):
        if self.noxspecial == None: # check case where no special rule for slab spacing, proceed automation of node coordinates
            self.nox = np.linspace(0,self.longdim,self.numtransgrid)  #array like containing node x cooridnate
        else:
            self.nox = self.noxspecial # assign custom array to nox array

        step = self.long_grid_nodes()  # mesh points in z direction
        nodetagcounter = 1 # counter for nodetag

        for pointz in step: # loop for each mesh point in z dir
            for pointx in self.nox: # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter,pointx,self.yelevation,pointz])
                nodetagcounter+=1
        print(self.Nodedata)

    def orthogonalmeshAutomation(self):
        # Note special rule for nox does not apply to orthogonal mesh - automatically calculates the optimal ortho mesh
        self.breadth = self.transdim * math.sin(self.skew/180*math.pi)

        step = self.long_grid_nodes()  # mesh points in z direction
        # Generate nox based on two region: (A) orthogonal area, and (B) support triangular area
        regA = np.linspace(0, self.breadth, self.mingridortho)
        regB = np.linspace(regA[-1],self.longdim,len(step))
        self.nox = np.hstack((regA[:-1],regB))

        # mesh region A
        nodetagcounter = 1 # counter for nodetag

        for pointz in step: # loop for each mesh point in z dir
            for pointx in regA[:-1]: # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter,pointx,self.yelevation,pointz])
                nodetagcounter+=1
        print("a")
        # mesh region B
        # B1
        regBupdate = regB  # placeholder for mesh grid - to be alter during loop
        for pointz in step: # loop for each mesh point in z dir
            for pointx in regBupdate: # loop for each mesh point in x dir (nox)
                self.Nodedata.append([nodetagcounter, pointx, self.yelevation, pointz])
            regBupdate = regBupdate[:-1]
        # B2


    #Nodedata, ConnectivityData, beamtype, MemberData, memtrans

    # Element connectivity functions
    def ConnectivityAutomation(self):
        pass

    def MemberPropertyInput(self):
        pass

    # subfunctions
    def testvalues(self):
        pass

    def checkskew(self):
        if self.skew>self.skewthreshold:
            self.orthomesh = True

    def long_grid_nodes(self):
        # determine coordinate of longitudinal girders
        lastgirder = self.width - self.edgewidth  # coord of last girder
        noxgirder = np.linspace(self.edgewidth, lastgirder, self.numlonggird)
        step = np.hstack((np.hstack((0, noxgirder)), self.width))  # array containing z coordinate
        return step
    # utility functions
    def generatePickle(self):
        pass