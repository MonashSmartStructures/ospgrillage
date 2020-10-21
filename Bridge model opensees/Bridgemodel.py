from openseespy.opensees import *
import numpy as np

# --------------------------------------------------------------------------------------------------------------------------------
# Class definition - Black box!!! do not change - -- - --
# --------------------------------------------------------------------------------------------------------------------------------
# ==================================================================================================


class Bridge:

    #  Inputs: Lz,  skew angle, Zspacing, number of beams,Lx, Xspacing,:
    def __init__(cls,Nodedata,ConnectivityData,beamtype):
        cls.Nodedata = Nodedata  # instantiate Node data attribute
        cls.ConnectivityData = ConnectivityData  # instantiate Node connectivity attribute
        cls.beameletype = beamtype

    @classmethod
    # bridge member objects (composition class)
    def assign_beam_member_prop(cls,longbeam,LRbeam,edgebeam,slab,diaphragm):
        # arguments are in a list returned by class method of Bridge_member class() - get_beam_prop()
        cls.longbeam = longbeam
        cls.LRbeam = LRbeam
        cls.edgebeam = edgebeam
        cls.slab = slab
        cls.diaphragm = diaphragm

    @classmethod
    def assign_material_prop(cls,concreteprop=None,steelprop = None):
        if concreteprop is None:
            cls.steelprop = steelprop
        else:
            cls.concreteprop = concreteprop

    # ==================================================================================================

class OpenseesModel(Bridge):
    # set modelbuilder

    def __init__(self,Nodedata,ConnectivityData,beamtype):
        super().__init__(Nodedata,ConnectivityData,beamtype)
        print(self.Nodedata)

    def create_Opensees_model(self):
        wipe()                  # clear model space prior to model generation
        self.generatemodel(3,6)  # run model generation
        self.createnodes()       # create nodes of model
        self.boundaryconditions() # assign boundary conditions to nodes at ends of model (i.e. x = 0 and x = Lx)
        self.concrete_materialprop()      # material properties (default concrete and steel)
        #        trans: (1)long beam, (2) transverse  [ x y z]
        self.ele_transform([0, 0, 1], [1, 0, 0]) # NEED ABSTRACTION
        # - default values are [0,0,1] for longitudinal, [-1,0,0] for transverse
        self.assemble_element()
        breakpoint()

    def generatemodel(self,ndm,ndf):
        model('basic', '-ndm', ndm, '-ndf', ndf)
        print("Model dim ={},Model DOF = {}".format(ndm, ndf))
    # create nodes

    def createnodes(self):
        for eachnode in self.Nodedata.index:
            node(int(self.Nodedata['nodetag'][eachnode]),int(self.Nodedata['x'][eachnode]),
                 int(self.Nodedata['y'][eachnode]),int(self.Nodedata['z'][eachnode]))
            print("node created ->", int(self.Nodedata['nodetag'][eachnode]))

    # ==================================================================================================
    # set boundary condition
    def boundaryconditions(self):
        countdof = 0 # initialize counter of assigned boundary conditions
        self.supportnode = self.Nodedata[self.Nodedata['support']==1].index.values
        #self.supporttype = self.Nodedata[self.Nodedata['supflag']].index.values
        for supp in self.supportnode: # loop for each cls.edgesupport items
            fixvalpin = [1, 1, 1, 0, 0, 0] # pinned
            fixvalroller = [0,1,1,0,0,0] #roller
            if self.Nodedata['supflag'][supp] == 'F':# pinned
                fix(int(self.Nodedata['nodetag'][supp]), *fixvalpin) # x y z, mx my mz
                print("pinned node ->", int(self.Nodedata['nodetag'][supp]))
            else: #roller
                fix(int(self.Nodedata['nodetag'][supp]), *fixvalroller) # x y z, mx my mz
                print("roller node ->", int(self.Nodedata['nodetag'][supp]))
            countdof +=1 # counter
        print('DOF constrained = ', countdof)

    # ==================================================================================================

    # create material tags
    def concrete_materialprop(self):
        self.concrete = 1  # number tag for concrete is "1"
        uniaxialMaterial("Concrete01", self.concrete, *self.concreteprop)
        print('Concrete material defined')
    # ==================================================================================================

    def ele_transform(self,zaxis,xaxis):
        self.transfType = 'Linear'  # transformation type
        self.longitudinalTransf = 1  # tag
        self.transverseTransf = 2  # tag
        geomTransf(self.transfType, self.longitudinalTransf, *zaxis)
        geomTransf(self.transfType, self.transverseTransf, *xaxis)
        print('geometrical transform object created')

    # ==================================================================================================
    # define elements
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def assemble_element(self):
        sectiondict = {'L': 'longbeam', 'LR': 'LRbeam', 'E': 'edgebeam', 'S': 'slab', 'D': 'diaphragm'} #dict for section tag
        transdict = {'L': 'longitudinalTransf', 'LR': 'longitudinalTransf', 'E': 'longitudinalTransf',
                     'S': 'transverseTransf', 'D': 'transverseTransf'} #dict for section transformation
        for eleind in self.ConnectivityData.index:
            #sectiondict = {L:'Longbeam',LR:'LRbeam',E:'edgebeam',S:'slab',D:'diaphragm'}
            expression = self.ConnectivityData['Section'][eleind]                                      ###
            sectioninput = eval("self.{}".format(sectiondict[expression]))
            eleNodes = [int(self.ConnectivityData['node_i'][eleind]),int(self.ConnectivityData['node_j'][eleind])]
            eleTag = int(self.ConnectivityData['tag'][eleind])
            trans = eval("self.{}".format(transdict[expression])) #ele transform input, 1 or 2, long or trans respective
            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
            element(self.beameletype, eleTag,*eleNodes,*sectioninput, trans) ###
            print("element created ->", int(self.ConnectivityData['tag'][eleind])) ###

        #print("Total Number of elements = ", cls.totalele)

    # ==================================================================================================

    @classmethod
    def time_series(cls):
        #           time series type, time series tag
        timeSeries("Linear", 1)

    # ==================================================================================================

    @classmethod
    def loadpattern(cls):
        #           load pattern type, load pattern tag, load factor (1) ,
        pattern("Plain", 1, 1)

    # ==================================================================================================

    @classmethod
    def loadID(cls):
        # This is for Test Load 1000 case for model - 245m example
        load(6, 0, -100000,0,0,0,0) # Fx Fy Fz, M-x , M-y, M-z
        load(17, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z
        #load(28, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z
        #load(39, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z
        #load(50, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z
        load(61, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z
        load(72, 0, -100000, 0, 0, 0, 0)  # Fx Fy Fz, M-x , M-y, M-z


    # ==================================================================================================

    # Load methods
    def loadtype(self,argument):
        # selected load type is taken as argument str to return method (e.g. point, axle, or UDL)
        method_name = 'load_'+str(argument)
        method = getattr(self,method_name,lambda:"nothing")
        return method()

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # find load position given load's (x,0, z) coordinate
    def search_nodes(self):
        #
        #     1 O - - - - O 2
        #       |         |                 # notations and node search numbering
        #       |    x    |
        #     3 O - - - - O 4
        #
        # n1
        boolpos = self.Nodedata[(self.Nodedata['x']< self.pos[0]) & (self.Nodedata['z']< self.pos[1])] #
        self.n1 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].max()) & (boolpos['z'] == boolpos['z'].max())]

        #n2
        boolpos = self.Nodedata[(self.Nodedata['x'] > self.pos[0]) & (self.Nodedata['z'] < self.pos[1])]  #
        self.n2 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].min()) & (boolpos['z'] == boolpos['z'].max())]

        # n3
        boolpos = self.Nodedata[(self.Nodedata['x'] < self.pos[0]) & (self.Nodedata['z'] > self.pos[1])]  #
        self.n3 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].max()) & (boolpos['z'] == boolpos['z'].min())]

        # n4
        boolpos = self.Nodedata[(self.Nodedata['x'] > self.pos[0]) & (self.Nodedata['z'] > self.pos[1])]  #
        self.n4 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].min()) & (boolpos['z'] == boolpos['z'].min())]
        #
        # returned as a pandas class object with 1x1 dimension [keyindex, value of nodetag] . to return the nodetag val
        # simply call self.n1.max()

    def load_position(self,pos,axlwt):
        self.pos = pos
        # inputs, pos is array [1x2] x and z coordinate
        # axlwt is the axle weight units N

        # first get nodes that are less than the position # second return the node that has highest combination
        # returns attributes n1 n2 n3 and n4 assigned to object. e.g. self.n1
        self.search_nodes() # searches nodes on the grillage
        #
        # pos has a X0 and Z0 , need to find the elements and return tag of nodes in the grid where, X0 resides in

        #cls.xcor1 = nodeCoord(eleNodes(3)[0])  # coor of first node
        a = abs(self.Nodedata['x'][self.n1.index].max()-self.Nodedata['x'][self.n2.index].max())# X dir
        b = abs(self.Nodedata['z'][self.n3.index].max()-self.Nodedata['z'][self.n1.index].max())# Z Dir
        self.zeta = (self.pos[0]-self.Nodedata['x'][self.n1.index].max())/a # X dir
        self.eta = (self.pos[1] - self.Nodedata['z'][self.n1.index].max()) /b  # Z Dir
        breakpoint()
        # option for linear shape function possible
        Nzeta = self.hermite_shape_function(self.zeta,a)
        Neta = self.hermite_shape_function(self.eta,b)

        # shape function dot multi
        Nv = [Nzeta[0]*Neta[0],Nzeta[2]*Neta[0],Nzeta[2]*Neta[2],Nzeta[0]*Neta[2]]
        Nmx = [Nzeta[1]*Neta[0],Nzeta[3]*Neta[0],Nzeta[3]*Neta[2],Nzeta[0]*Neta[3]]
        Nmz = [Nzeta[0]*Neta[1],Nzeta[2]*Neta[1],Nzeta[2]*Neta[3],Nzeta[0]*Neta[3]]
        #   N1 -> cls.n1 , N2 -> cls.n2 . . . . . N4 -> cls.n4
        # assign forces
        breakpoint()
        for nn in range(0,3):
            load(int(eval('self.n%d.max()' % (nn+1))),*np.dot([0,Nv[nn],0,Nmx[nn],0,Nmz[nn]],axlwt))
        breakpoint()
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def hermite_shape_function(zeta,a): # using zeta and a as placeholders for normal coor + length of edge element
        # hermite shape functions
        N1 = (1-3*zeta**2+2*zeta**3)
        N2 = (zeta-2*zeta**2+zeta**3)*a
        N3 = (3*zeta**2-2*zeta**3)
        N4 = (-zeta**2+zeta**3)*a
        return [N1, N2, N3, N4]

    @staticmethod
    def linear_shape_function(zeta,eta):
        N1 = 0.25*(1-zeta)*(1-eta)
        N2 = 0.25*(1+zeta)*(1-eta)
        N3 = 0.25 * (1 + zeta) * (1 + eta)
        N4= 0.25*(1-zeta)*(1+eta)
        return [N1, N2, N3, N4]


    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # single point load
    @classmethod
    def load_singlepoint(cls,nodes, forcevector):
        load(nodes, *forcevector)  # x x y y z z

    # multiple point loads of equal force
    @classmethod
    def load_multipoint(cls,nodes, forcevector):
        # force vector passes shape function to distribute ele forces to nodes
        load(nodes, *forcevector)  # x y z mx my mz

    def load_UDLpatch(cls,nodetags,force):
        # takes two nodes , a start and end node, then distribute the load
        for n in range(nodetags[1]-nodetags[0]):
            load(nodetags[0]+n, *force)
        # notes: force must be pre-determined - calculated elsewhere to work out the UDL onto each point


    def load_movingtruck(cls,truck_pos,axlwts,axlspc,axlwidth):
        # from truck pos(X>0 and Z>0), determine relative location of front top axle on the bridge model
        # truck_pos is a list [X0, Z0]
        # read direction of axlwts and axlspc is from left (i.e. index = 0).
        # first element of axlspc is a placeholder 0, to account for front of vehicle (i.e. first axle)
        for n in range(len(axlwts)):  # loop do for each axle
            # axl position with respect to bridge
            # X coor, Z coor

            X1 = truck_pos[0] - axlspc[n]  # X coord of axle

            if X1 > 0 :  # check if axle is on bridge
                #   Inputs:                position[x0,z0],        axle weight at position
                cls.load_position([X1, truck_pos[1]], axlwts[n])  # one side axle
                cls.load_position([X1, truck_pos[1]+axlwidth], axlwts[n])  # other side of axle


# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# Model generation objects


