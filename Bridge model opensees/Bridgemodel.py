import openseespy.opensees as ops
import numpy as np
import ast

"""

"""


# --------------------------------------------------------------------------------------------------------------------------------
# Class definition - Black box!!! do not change - -- - --
# --------------------------------------------------------------------------------------------------------------------------------
# ==================================================================================================


class Bridge:
    """
    Class containing bridge informations from Bridge Pickle file for use in Openseespy framework
    """

    #  Inputs: Lz,  skew angle, Zspacing, number of beams,Lx, Xspacing,:
    def __init__(cls, Nodedata, ConnectivityData, beamtype, MemberData, membtrans):
        """ Class constructor - collecting the dataframes for bridge properties """
        cls.Nodedata = Nodedata  # instantiate Node data attribute
        cls.ConnectivityData = ConnectivityData  # instantiate Node connectivity attribute
        cls.MemberData = MemberData
        cls.beameletype = beamtype
        cls.membtrans = membtrans
        # on object init, create members for

    @classmethod
    # bridge member objects (composition class)
    def assign_beam_member_prop(cls, longbeam, LRbeam, edgebeam, slab, diaphragm):
        """
        Setters for bridge properties - structural members

        :param longbeam:
        :param LRbeam:
        :param edgebeam:
        :param slab:
        :param diaphragm:
        :return:
        """
        # arguments are in a list returned by class method of Bridge_member class() - get_beam_prop()
        cls.longbeam = longbeam
        cls.LRbeam = LRbeam
        cls.edgebeam = edgebeam
        cls.slab = slab
        cls.diaphragm = diaphragm

    @classmethod
    def assign_material_prop(cls, concreteprop=None, steelprop=None):
        """
        Setters for bridge properties - Materials

        :param concreteprop:
        :param steelprop:
        :return:
        """
        if concreteprop is None:
            cls.steelprop = steelprop
        else:
            cls.concreteprop = concreteprop

    # ==================================================================================================


class OpenseesModel(Bridge):
    """
    Class to create bridge model in Openseespy framework based on input of
    `Bridge` model class
    """

    # set modelbuilder
    def __init__(self, Nodedata, ConnectivityData, beamtype, MemberData, memtrans):
        super().__init__(Nodedata, ConnectivityData, beamtype, MemberData, memtrans)

    def create_Opensees_model(self):
        """
        Code handling the generation of bridge model in Openseespy framework
        :return:
        """
        ops.wipe()  # clear model space prior to model generation
        self.generatemodel(3, 6)  # run model generation # default number 3 D 6 DOF per node
        self.createnodes()  # create nodes of model
        self.boundaryconditions()  # assign boundary conditions to nodes at ends of model (i.e. x = 0 and x = Lx)
        self.concrete_materialprop()  # material properties (default concrete and steel)
        #        trans: (1)long beam, (2) transverse  [ x y z]
        self.ele_transform()  # NEED ABSTRACTION
        # - default values are [0,0,1] for longitudinal, [1,0,0] for transverse
        self.assemble_element()

    def generatemodel(self, ndm, ndf):
        """
        Code handling the start of bridge model generation - Opensees model space properties
        :param ndm: model dimension [Default 3 ]
        :param ndf: degree-of-freedoms for each model nodes [Default 6]

        """
        ops.model('basic', '-ndm', ndm, '-ndf', ndf)
        # print("Model dim ={},Model DOF = {}".format(ndm, ndf))

    # create nodes

    def createnodes(self):
        """
        Code handling generation of nodes in Openseespy. Nodes specified in attribute of `Bridge` class
        :return:
        """
        for eachnode in self.Nodedata.index:
            ops.node(int(self.Nodedata['nodetag'][eachnode]), int(self.Nodedata['x'][eachnode]),
                     int(self.Nodedata['y'][eachnode]), int(self.Nodedata['z'][eachnode]))
            # print("node created ->", int(self.Nodedata['nodetag'][eachnode]))

    # ==================================================================================================
    # set boundary condition
    def boundaryconditions(self):
        """
        Code handling generation of boundary conditions in Openseespy. Boundary conditions specified
        in attribute of `Bridge` class.
        :return:
        """
        countdof = 0  # initialize counter of assigned boundary conditions
        self.supportnode = self.Nodedata[self.Nodedata['support'] != 0].index.values

        # fixvalpin = [1, 1, 1, 0, 0, 0]  # pinned
        # fixvalroller = [0, 1, 1, 0, 0, 0]  # roller
        for supp in self.supportnode:  # loop for each valuein supportnode list

            test = self.Nodedata['fixity code'][supp]
            fixval = self.get_fixity(test)
            ops.fix(int(self.Nodedata['nodetag'][supp]), *fixval)

            # if self.Nodedata['supflag'][supp] == 'F':# pinned
            #    ops.fix(int(self.Nodedata['nodetag'][supp]), *fixvalpin) # x y z, mx my mz
            # print("pinned node ->", int(self.Nodedata['nodetag'][supp]))
            # else: #roller
            #    ops.fix(int(self.Nodedata['nodetag'][supp]), *fixvalroller) # x y z, mx my mz
            # print("roller node ->", int(self.Nodedata['nodetag'][supp]))
            countdof += 1  # counter
        # print('DOF constrained = ', countdof)

    @staticmethod
    def get_fixity(fixity_code):
        """
        Static method to translate fixity code to communicate with Openseespy's boundary definition
        :param fixity_code: list of string containing fixity symbol F for Free, R for restrained
        :return: boundary: list of 1 and 0 for fixity information 1 = fix, 0 = free
        """
        # fixity code is a list contain 6 elements
        # letters F (Free) or R (Restrained)
        boundary = [0, 0, 0, 0, 0, 0]
        for bd in range(len(boundary)):
            if fixity_code[bd] == "R":
                boundary[bd] = 1
        return boundary

    # ==================================================================================================

    # create material tags
    def concrete_materialprop(self):
        """
        Code handling the creation of material tags in Openseespy. Default concrete = 1
        """
        self.concrete = 1  # default number tag for concrete is "1"
        ops.uniaxialMaterial("Concrete01", self.concrete, *self.concreteprop)
        # print('Concrete material defined')

    # ==================================================================================================

    def ele_transform(self, transfType="Linear"):
        """
        Code handling the definition of geometric transformation of members. Transformation
         specified in attribute of `Bridge` class.
        :return:

        """

        for ind in self.membtrans.index:
            tag = int(self.membtrans["Transform tag"][ind])
            vxz = ast.literal_eval(self.membtrans["Vector"][ind])
            ops.geomTransf(transfType, tag, *vxz)

        # ops.geomTransf(self.transfType, self.longitudinalTransf, *zaxis)
        # ops.geomTransf(self.transfType, self.transverseTransf, *xaxis)
        # print('geometrical transform object created')

    # ==================================================================================================
    # define elements
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def assemble_element(self):
        """
        Code specifying generation of grillage elements.
        :return:
        """
        # loop for each element in dataframe ConnectivityData
        for eleind in self.ConnectivityData.index:
            expression = self.ConnectivityData['Section'][eleind]  ###
            # sectioninput = eval("self.{}".format(sectiondict[expression]))
            member = self.MemberData[self.MemberData['Section'] == expression]

            # get sectioninput based on ele type
            sectioninput = self.get_sectioninput(member)

            # get ele nodes- from attribute self.ConnectivityData
            eleNodes = [int(self.ConnectivityData['node_i'][eleind]), int(self.ConnectivityData['node_j'][eleind])]

            # get ele tag from attribute self.ConnectivityData
            eleTag = int(self.ConnectivityData['tag'][eleind])

            # get ele transform tag for current element eleind
            transtag = int(self.MemberData["Trans tag"][self.MemberData["Section"] == expression].max())

            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
            ops.element(self.beameletype, eleTag, *eleNodes, *sectioninput, transtag)  ###
            # print("element created ->", int(self.ConnectivityData['tag'][eleind])) ###
            # print("Total Number of elements = ", cls.totalele)

    def get_sectioninput(self, member):
        """
        Function to obtain member attribute from Bridge class attribute.
        :param member: int/str, section tag
        :return: section input for member section matching section tag
        """
        # assignment input based on ele type
        if self.beameletype == "ElasticTimoshenkoBeam":
            sectioninput = [np.float(member['E(N/m2)'].max()), np.float(member['G(N/m2)'].max()),
                            np.float(member['A(m^2)'].max()),
                            np.float(member['J (m^4)'].max()), np.float(member['Iy (m^4)'].max()),
                            np.float(member['Iz (m^4)'].max()),
                            np.float(member['Ay (m^2)'].max()), np.float(member['Az (m^2)'].max())]
        elif self.beameletype == "elasticBeamColumn":  # eleColumn
            sectioninput = [np.float(member['E(N/m2)'].max()), np.float(member['G(N/m2)'].max()),
                            np.float(member['A(m^2)'].max()),
                            np.float(member['J (m^4)'].max()), np.float(member['Iy (m^4)'].max()),
                            np.float(member['Iz (m^4)'].max())]
        return sectioninput

    # ==================================================================================================
    # ==================================================================================================
    # Following sections contains code for MF implementation - this model needs to be segregated
    # ==================================================================================================
    # ==================================================================================================
    @classmethod
    def time_series(cls, defSeries="Linear"):
        """
        Code handling the time series generation for Openseespy. Default "Constant", tag 1
        :return:
        """
        #           time series type, time series tag
        ops.timeSeries(defSeries, 1)

    # ==================================================================================================

    @classmethod
    def loadpattern(cls, pat="Plain"):
        """
        Code handling the pattern load case for Openseespy. Default "Plain", tag 1, load factor 1
        :return:
        """
        #           load pattern type, load pattern tag, load factor (1) ,
        ops.pattern(pat, 1, 1)

    # ==================================================================================================
    # ==================================================================================================
    # functions for moving loads

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # find load position given load's (x,0, z) coordinate
    def search_nodes(self):
        """
        Function to search grillage element emcompassing load position by
        :return:
        """
        #            x
        #     1 O - - - - O 2
        #   z   |         |                 # notations and node search numbering
        #       |    x    |
        #     3 O - - - - O 4
        #
        # n1
        boolpos = self.Nodedata[(self.Nodedata['x'] <= self.pos[0]) & (self.Nodedata['z'] <= self.pos[1])]  #
        self.n1 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].max()) & (boolpos['z'] == boolpos['z'].max())]

        # n2
        boolpos = self.Nodedata[(self.Nodedata['x'] > self.pos[0]) & (self.Nodedata['z'] <= self.pos[1])]  #
        self.n2 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].min()) & (boolpos['z'] == boolpos['z'].max())]

        # n3
        boolpos = self.Nodedata[(self.Nodedata['x'] <= self.pos[0]) & (self.Nodedata['z'] > self.pos[1])]  #
        self.n3 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].max()) & (boolpos['z'] == boolpos['z'].min())]

        # n4
        boolpos = self.Nodedata[(self.Nodedata['x'] > self.pos[0]) & (self.Nodedata['z'] > self.pos[1])]  #
        self.n4 = boolpos['nodetag'][(boolpos['x'] == boolpos['x'].min()) & (boolpos['z'] == boolpos['z'].min())]
        #
        # returned as a pandas class object with 1x1 dimension [keyindex, value of nodetag] . to return the nodetag val
        # simply call self.n1.max()

    def load_position(self, pos, axlwt):
        """
        Code handling the load definition for Openseespy.
        :param pos:
        :param axlwt:
        :return:
        """
        self.pos = pos
        # inputs, pos is array [1x2] x and z coordinate
        # axlwt is the axle weight units N

        # first get nodes that are less than the position # second return the node that has highest combination
        # returns attributes n1 n2 n3 and n4 assigned to object. e.g. self.n1
        self.search_nodes()  # searches nodes on the grillage
        #
        # pos has a X0 and Z0 , need to find the elements and return tag of nodes in the grid where, X0 resides in

        a = abs(self.Nodedata['x'][self.n1.index].max() - self.Nodedata['x'][self.n2.index].max())  # X dir
        b = abs(self.Nodedata['z'][self.n3.index].max() - self.Nodedata['z'][self.n1.index].max())  # Z Dir
        self.zeta = (self.pos[0] - self.Nodedata['x'][self.n1.index].max()) / a  # X dir
        self.eta = (self.pos[1] - self.Nodedata['z'][self.n1.index].max()) / b  # Z Dir

        # Hermite functions for two orthogonal directions of grillage
        Nzeta = self.hermite_shape_function(self.zeta, a)  # X
        Neta = self.hermite_shape_function(self.eta, b)  # Z

        # linear shape function - 2 node beam element , on two directions
        Nv = [(1 - self.zeta) * (1 - self.eta), (self.zeta) * (1 - self.eta), (1 - self.zeta) * (self.eta),
              (self.zeta) * self.eta]

        # hermite shape function dot multi0
        Nv = [Nzeta[0] * Neta[0], Nzeta[2] * Neta[0], Nzeta[0] * Neta[2], Nzeta[2] * Neta[2]]
        # Nmx = [Nzeta[1]*Neta[0],Nzeta[3]*Neta[0],Nzeta[0]*Neta[3],Nzeta[3]*Neta[2]]
        # Nmz = [Nzeta[0]*Neta[1],Nzeta[2]*Neta[1],Nzeta[0]*Neta[3],Nzeta[2]*Neta[3]]
        #   N1 -> cls.n1 , N2 -> cls.n2 . . . . . N4 -> cls.n4
        # assign forces
        for nn in range(0, 3):
            ops.load(int(eval('self.n%d.max()' % (nn + 1))), *np.dot([0, Nv[nn], 0, 0, 0, 0], axlwt))  # x y z mx my mz

    def op_load_positioning(self, pos, axlwt):
        # function to implement load onto
        self.op_search_nodes()
        pass

    def op_search_nodes(self):
        #            x
        #     1 O - - - - O 2
        #   z   |         |                 # notations and node search numbering
        #       |    x    |
        #     3 O - - - - O 4
        #
        # n1                # x 1                     z 3
        bool_list = self.Nodedata[(self.extract(self.Nodedata, 1) <= self.pos[0]) &
                                  (self.extract(self.Nodedata, 3) <= self.pos[1])]
        bool_list = bool_list[max(self.extract(bool_list, 1)) & max(self.extract(bool_list, 1))]
        n1 = self.extract(bool_list, 0)

        bool_list = self.Nodedata[(self.extract(self.Nodedata, 1) > self.pos[0]) &
                                  (self.extract(self.Nodedata, 3) <= self.pos[1])]
        bool_list = bool_list[max(self.extract(bool_list, 1)) & max(self.extract(bool_list, 1))]
        n2 = self.extract(bool_list, 0)

        bool_list = self.Nodedata[(self.extract(self.Nodedata, 1) <= self.pos[0]) &
                                  (self.extract(self.Nodedata, 3) > self.pos[1])]
        bool_list = bool_list[max(self.extract(bool_list, 1)) & max(self.extract(bool_list, 1))]
        n3 = self.extract(bool_list, 0)

        bool_list = self.Nodedata[(self.extract(self.Nodedata, 1) > self.pos[0]) &
                                  (self.extract(self.Nodedata, 3) > self.pos[1])]
        bool_list = bool_list[max(self.extract(bool_list, 1)) & max(self.extract(bool_list, 1))]
        n4 = self.extract(bool_list, 0)

        return n1, n2, n3, n4

    @staticmethod
    def extract(lst, num):
        # static method to extract an element from a sublist - used for node and element searching procedures
        return [item[num] for item in lst]

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # shape functions for patching truck forces onto grillage nodes
    @staticmethod
    def hermite_shape_function(zeta, a):  # using zeta and a as placeholders for normal coor + length of edge element
        # hermite shape functions
        """

        :param zeta: absolute position in x direction
        :param a: absolute position in x direction
        :return: Four terms [N1, N2, N3, N4] of hermite shape function

        .. note::

            Further validation needed - trial on different bridge models

        """
        N1 = (1 - 3 * zeta ** 2 + 2 * zeta ** 3)
        N2 = (zeta - 2 * zeta ** 2 + zeta ** 3) * a
        N3 = (3 * zeta ** 2 - 2 * zeta ** 3)
        N4 = (-zeta ** 2 + zeta ** 3) * a
        return [N1, N2, N3, N4]

    @staticmethod
    def linear_shape_function(zeta, eta):
        """

        :param zeta: absolute position in x direction
        :param eta: absolute position in z direction
        :return: Four terms [N1, N2, N3, N4] of Linear shape function

        .. note::

            Further validation needed - trial on different bridge models

        """
        N1 = 0.25 * (1 - zeta) * (1 - eta)
        N2 = 0.25 * (1 + zeta) * (1 - eta)
        N3 = 0.25 * (1 + zeta) * (1 + eta)
        N4 = 0.25 * (1 - zeta) * (1 + eta)
        return [N1, N2, N3, N4]

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def load_movingtruck(self, truck_pos, axlwts, axlspc, axlwidth):
        """
        Code handling moving truck simulation. This method loops for each position in the Vehicle class
        This function handles the subfunctions
        - searchnodes()
        - load_positions()
        -
        :param truck_pos: Truck position [x,z]
        :param axlwts: list , axle weights
        :param axlspc:
        :param axlwidth:
        :return:
        """
        # from truck pos(X>0 and Z>0), determine relative location of front top axle on the bridge model
        # truck_pos is a list [X0, Z0]
        # read direction of axlwts and axlspc is from left (i.e. index = 0).
        # first element of axlspc is a placeholder 0, to account for front of vehicle (i.e. first axle)
        zero = 0
        # add placeholder 0 to axlspc
        axlspc.insert(0, zero)

        for n in range(len(axlwts)):  # loop do for each axle
            # axl position with respect to bridge
            # X coor, Z coor

            X1 = truck_pos[0] + axlspc[n]  # X coord of axle

            if X1 > 0:  # check if axle is on bridge
                #   Inputs:                position[x0,z0],        axle weight at position
                self.load_position([X1, truck_pos[1]], axlwts[n])  # one side axle
                self.load_position([X1, truck_pos[1] + axlwidth], axlwts[n])  # other side of axle
                break
            else:
                print("load axle is out of bound of bridge grillage = ", X1)

# --------------------------------------------------------------------------------------------------------------------------------
