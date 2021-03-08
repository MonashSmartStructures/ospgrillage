
import pandas as pd
import numpy as np
import math

class GrillageGenerator:
    def __init__(self,long_dim,width,skew, num_long_grid, num_trans_grid, cantilever_edge):
        # global dimensions of grillage
        self.long_dim = long_dim   # span , also c/c between support bearings
        self.width = width # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        self.skew = skew         # angle in degrees
        # Properties of grillage
        self.num_long_gird = num_long_grid      # number of longitudinal beams
        self.num_trans_grid = num_trans_grid    # number of grids for transverse members
        self.edge_width = cantilever_edge     # width of cantilever edge beam

        # instantiate matrices for geometric dependent properties
        self.transdim = None                   # to be calculated automatically based on skew
        self.breadth = None                 # to be calculated automatically based on skew
        self.spclonggirder = None           # to be automated
        self.spctransslab = None            # to be automated
        self.Nodedata = []                  # array like to be populated
        self.nox = []
        self.noz = []

        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.min_longspacing = 1  # default 1m
        self.max_long_spacing = 2  # default 1m
        self.min_trans_spacing = 1  # default 1m
        self.max_trans_spacing = 2  # default 2m
        self.trans_to_long_spacing = 1  # default 1m
        self.min_grid_long = 9    # default 9 mesh
        self.min_grid_trans = 5   # default 5 mesh
        self.ortho_mesh = False  # boolean for grillages with skew < 15-20 deg
        self.y_elevation = 0 # default elevation of grillage wrt OPmodel coordinate system
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3

        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.nox_special = None # array specifying custom coordinate of longitudinal nodes
        self.noz_special = None # array specifying custom coordinate of transverse nodes
        self.skew_threshold = 15 # threshold for grillage to generate nodes with orthogonal mesh (units degree)
        # to be added
        # - special rule for multiple skew
        # - rule for multiple span + multi skew
        # - rule for pier

        # Grillage automation procedure
        # 1 run node generation
        # 2 run Connectivity generation
        # 3 prompt user to run member input

    # node functions
    def Node_data_generation(self):
        # calculate grillage width
        self.transdim = self.width / math.cos(self.skew / 180 * math.pi)  # determine width of grillage
        # check for orthogonal mesh requirement
        self.check_skew()
        if self.ortho_mesh:
            # perform orthogonal meshing
            self.orthogonal_mesh_Automation()
        else: # skew mesh requirement
            # perform skewed mesh
            self.skew_mesh_Automation()


    def skew_mesh_Automation(self):
        if self.nox_special == None: # check  special rule for slab spacing, else proceed automation of node
            self.nox = np.linspace(0,self.long_dim,self.num_trans_grid)  # array like containing node x cooridnate
        else:
            self.nox = self.nox_special # assign custom array to nox array

        step = self.long_grid_nodes()  # mesh points in z direction
        nodetagcounter = 1 # counter for nodetag

        for pointz in step: # loop for each mesh point in z dir
            noxupdate = self.nox - pointz*np.tan(self.skew/180*math.pi) # get nox for current step in transverse mesh
            for pointx in noxupdate: # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter,pointx,self.y_elevation,pointz])    # NOTE here is where to change X Y plane
                nodetagcounter+=1
        print(self.Nodedata)

    def orthogonal_mesh_Automation(self):
        # Note special rule for nox does not apply to orthogonal mesh - automatically calculates the optimal ortho mesh
        #             o o o o o o
        #           o
        #         o
        #       o o o o o o
        #         b    +  ortho
        self.breadth = self.transdim * math.sin(self.skew/180*math.pi)  # length of skew edge in x dir
        step = self.long_grid_nodes()  # mesh points in transverse direction
        # calculate number of trans grid in quadrilateral region (ortho) based on self.mintransspacing
        transgridspacing = np.ceil((self.long_dim - self.breadth)/self.num_trans_grid)
        # Generate nox based on two orthogonal region: (A)  quadrilateral area, and (B)  triangular area
        regA = np.linspace(0,self.long_dim-self.breadth,self.num_trans_grid)
        # RegA consist of overlapping last element
        # RegB first element overlap with RegA last element
        regB = np.linspace(regA[-1],self.long_dim,len(step))
        self.nox = np.hstack((regA[:-1],regB))  # removed overlapping element

        # mesh region A quadrilateral area
        nodetagcounter = 1 # counter for nodetag

        for pointz in step: # loop for each mesh point in z dir
            for pointx in regA[:-1]: # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter,pointx,self.y_elevation,pointz])
                nodetagcounter+=1
        print("a")
        # mesh region B triangular area
        # B1 @ right support
        regBupdate = regB  # placeholder for mesh grid - to be alter during loop
        for pointz in step: # loop for each mesh point in z dir
            for pointx in regBupdate: # loop for each mesh point in x dir (nox)
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1] # remote last element (skew boundary)

        # B2 left support
        regBupdate = -regB + regA[-1] # reinstantiate regBupdate
        for pointz in reversed(step):
            for pointx in regBupdate[1:]:
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1] # remote last element (skew boundary)
        print(self.Nodedata)

    # Element connectivity functions
    def Connectivity_Automation(self):
        pass

    # Methods for defining grillage properties
    def MemberPropertyInput(self):
        pass

    #
    def BoundaryCondInput(self):
        pass

    # sub functions
    def testvalues(self):
        pass

    def check_skew(self):
        if self.skew>self.skew_threshold:
            self.ortho_mesh = True

    def long_grid_nodes(self):
        """
        Function to output array of grid nodes along longitudinal direction
        :return: step: array/list containing node spacings along longitudinal direction (float)
        """

        last_girder = (self.width - self.edge_width)   # coord of last girder
        nox_girder = np.linspace(self.edge_width, last_girder, self.num_long_gird)
        step = np.hstack((np.hstack((0, nox_girder)), self.width))  # array containing z coordinate
        return step
