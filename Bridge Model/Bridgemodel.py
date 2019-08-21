from openseespy.opensees import *
import xlrd
import numpy as np

# --------------------------------------------------------------------------------------------------------------------------------
# Class definition - Black box!!! do not change - -- - --
# --------------------------------------------------------------------------------------------------------------------------------
# ==================================================================================================


class BeamModel:
    @classmethod
    def __init__(cls, Lx, skewx, Lz, spacingx, spacingy, numbeam):
        cls.spacingx = spacingx
        cls.spacingy = spacingy
        cls.skewx = skewx
        cls.Lx = Lx
        cls.Lz = Lz
        cls.numbeam = numbeam
        cls.numzele = int((cls.Lz / cls.spacingy))
        cls.ele_z = [0]  # initialize X coord vector
        cls.ele_x = np.linspace(0, cls.Lz, cls.numzele) # generate uniform y coord vector
        count = 1 # counter for x coord loop
        # generate x and y axis vector of edge points
        for x in range(0, cls.numbeam + 1): # loop for each X coord to insert corrd
            b = (cls.Lx - cls.numbeam * cls.spacingx) / 2  # equal edge [Future versions edit here for flexible b]
            if x == 1 or cls.numbeam:  # for first and last node point, spacing is b distance from regular beam spacing
                count += 1
                cls.ele_z.append(x * cls.spacingx + b * count)  # add X coord to list, output is a vector
            else:
                cls.ele_z.append((x * cls.spacingx + b))
        # future versions consider skew - assemble different vector into matrix list
        cls.xv, cls.zv = np.meshgrid(cls.ele_x, cls.ele_z) # used for element_assemble()

        # r = list(range(1, eg.totalnodes + 1))  # plus 1 for counter ( if totalnodes  = 77, gives final node tag as 76)
        # slabtag = set(r)-set(eg.edgesupport)  # tag of transverse slabs (difference btween node tags and edsupport)
        #cls.createnodes()

    # set modelbuilder
    @classmethod
    def generatemodel(cls,ndm,ndf):
        model('basic', '-ndm', ndm, '-ndf', ndf)
        print("Model dim ={},Model DOF = {}".format(ndm, ndf))

    # ==================================================================================================

    # create nodes
    @classmethod
    def createnodes(cls):
        cls.edgesupport = [] # list containing tags of nodes of support (used in boundaryconditions())
        cls.nodetag = np.zeros((len(cls.ele_z),len(cls.ele_x)))  # array containing the tag relative mesh position
        for y in range(len(cls.ele_z)):  # loop for y grid (ele Y beam positions)
            cls.edgesupport.append(int(y*len(cls.ele_x) + 1))   # first point of support
            for x in range(len(cls.ele_x)):         # loop in eleX (longtidunal)
                y0 = 0  # [current version z axis is vertical axis, future versions allow varying z values]
                #       tag                     x           y=0       z
                node(int(y*len(cls.ele_x) + x + 1), cls.xv[y,x], y0, cls.zv[y,x])  # tag starts from 1
                cls.nodetag[y,x] = int(y*len(cls.ele_x) + x + 1)        # node tag (mesh position)
            cls.edgesupport.append(int(y*len(cls.ele_x) + x + 1))   #  second point of support
        print("model's nodes layout is:\n",cls.nodetag)
        cls.totalnodes = y*len(cls.ele_x) + x + 1
        print('Nodes generated = ', cls.totalnodes)  # number here is the total nodes

    # ==================================================================================================
    # set boundary condition
    @classmethod
    def boundaryconditions(cls):
        countdof = 0 # initialize counter of assigned boundary conditions
        for supp in range(len(cls.edgesupport)): # loop for each cls.edgesupport items
            fixval = [1, 1, 1, 1, 1, 1] # fixed support (future version for pin roller)
            fix(cls.edgesupport[supp], *fixval) # x x y y z z
            countdof +=1 # counter
        print('DOF constrained = ', countdof)

    # ==================================================================================================

    # create material tags
    @classmethod
    def materialprop(cls,concreteprop):
        cls.concrete = 1  # tag for concrete is "1"
        uniaxialMaterial("Concrete01", cls.concrete, *concreteprop)
        print('Concrete material defined')
    # ==================================================================================================
    @classmethod
    def ele_transform(cls,zaxis,xaxis):
        cls.transfType = 'Linear'  # transformation type
        cls.longitudinalTransf = 1  # tag
        cls.transverseTransf = 2  # tag
        geomTransf(cls.transfType, cls.longitudinalTransf, *zaxis)
        geomTransf(cls.transfType, cls.transverseTransf, *xaxis)
        print('geometrical transform object created')

    # ==================================================================================================
    # define elements
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def element_assemble(cls,longbeamprop, LRbeamprop, edgeprop, transprop, diapprop):
        eletypeB = "elasticBeamColumn"
        eletypeSh = "ShellMITC4"
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  define longitudinal beams
        longbeam = cls.nodetag[2:-2,:]  # tags of node correspond to long beam
        numlongbeam = 0  # initialize counter of assigned boundary conditions
        for nlongbeam in range(len(longbeam)): # loop for each node in Y dir
            for x in range(len(longbeam[-1])-1): # minus 1 for number of elem = nnodes - 1
                elenodes = [longbeam[nlongbeam,x],longbeam[nlongbeam,x+1]]
                #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
                tag = (2+nlongbeam)*(len(longbeam[-1])-1) + x + 1
                element(eletypeB, tag, *elenodes, *longbeamprop,
                        cls.longitudinalTransf)
                numlongbeam += 1
        print("Longitudinal beam defined = ", numlongbeam)

        #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   define left and right beams
        leftbeam = cls.nodetag[1,:]  # tags of node correspond to leftbeam
        leftbeameletag = len(longbeam[-1])-1
        rightbeam = cls.nodetag[-2,:]  # tags of node correspond to rightbeam
        rightbeameletag = 2* leftbeameletag + numlongbeam

        for LR in range(len(leftbeam) - 1):  # minus 1 for number of elem = nnodes - 1
            leftelenodes = [leftbeam[LR], leftbeam[LR + 1]]
            rightelenodes = [rightbeam[LR], rightbeam[LR + 1]]
            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
            tagL = leftbeameletag + LR + 1
            tagR = rightbeameletag + LR + 1
            element(eletypeB, tagL, *leftelenodes, *LRbeamprop,cls.longitudinalTransf)
            element(eletypeB, tagR, *rightelenodes, *LRbeamprop,cls.longitudinalTransf)
        print("left right beam defined = ", 2*(LR+1))

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # define edge beam
        leftedge= cls.nodetag[0,:]  # tags of node correspond to leftedge
        rightedge = cls.nodetag[-1,:]  # tags of node correspond to rightedge
        rightedgeeletag = 3 * (len(longbeam[-1])-1) + numlongbeam  # countlong is longitudinal beam ele counting

        for edge in range(len(leftedge) - 1):  # minus 1 for number of elem = nnodes - 1
            Ledgenodes = [leftedge[edge], leftedge[edge + 1]]
            Redgenodes = [rightedge[edge], rightedge[edge + 1]]
            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
            element(eletypeB, edge + 1, *Ledgenodes, *edgeprop, cls.longitudinalTransf)
            element(eletypeB, rightedgeeletag + edge + 1, *Redgenodes, *edgeprop, cls.longitudinalTransf)
        print("left right edge defined = ", 2*(edge+1))

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  define transverse slab
        translab = cls.nodetag[:,1:-1]  # tags of node correspond to slab
        numtranslab = 0  # initialize counter of assigned boundary conditions
        long_ele = 2*(edge+1)+2*(LR+1) + numlongbeam
        for nslab in range(len(translab[-1])): # loop for each node in Y dir
            for y in range(len(translab)-1): # minus 1 for number of elem = nnodes - 1
                slabnodes = [translab[y,nslab],translab[y+1,nslab]]
                #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
                slabtag= long_ele + (nslab+1)*(len(translab)-1) + y + 1
                element(eletypeB,slabtag,*slabnodes, *transprop , cls.transverseTransf)
                numtranslab += 1
        print("Transverse slab defined = ", numtranslab)

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  define diaphragm
        diap_S = cls.nodetag[:,1]
        diap_R = cls.nodetag[:, -1]
        for diap in range(len(diap_S)-1):
            S_diap = [diap_S[diap], diap_S[diap+1]]
            R_diap = [diap_R[diap], diap_R[diap+1]]
            S_tag = long_ele + diap + 1
            R_tag = long_ele + numtranslab + (len(diap_S)-1)+ diap + 1
            element(eletypeB, S_tag,*S_diap, *diapprop,cls.transverseTransf)
            element(eletypeB, R_tag,*R_diap, *diapprop,cls.transverseTransf)
        print("diaphragm elements = ", 2*(diap+1))
        cls.totalele = numlongbeam+2*(LR+1)+2*(edge+1)+numtranslab+2*(diap+1)
        print("Total Number of elements = ",cls.totalele)
    # ==================================================================================================

    @classmethod
    def time_series(cls):
        timeSeries("Linear", 1)

    # ==================================================================================================

    @classmethod
    def loadpattern(cls):
        pattern("Plain", 1, 1)

    # ==================================================================================================

    @classmethod
    def loadID(cls):

        load(50, 0, 0,-50,0,0,0) # Fx Fy Fz, M-x , M-y, M-z
    # ==================================================================================================

    # Load methods
    @classmethod
    def loadtype(cls,argument):
        # selected load type is taken as argument str to return method (e.g. point, axle, or UDL)
        method_name = 'load_'+str(argument)
        method = getattr(cls,method_name,lambda:"nothing")
        return method()

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # find load position given load's (x,0, z) coordinate
    @classmethod
    def load_position(cls,pos,axlwt):
        # method to return 4 beam elements or 1 shell element correspond to the location of which the axle load acts.
        # pos has a X0 and Z0 , need to find the elements and return its nodes of grid where, X0 resides in
        cls.n1 = cls.nodetag[(cls.xv <= pos[0]) * (cls.zv <= pos[1]) ][-1]  # find the reference node
        # from ref node, populate other 3 nodes that forms the grid correspond to location of load
        cls.n2 = cls.n1+1
        cls.n4 = cls.n1+ len(cls.ele_x)  #ordering for clockwise defition
        cls.n3 = cls.n2+len(cls.ele_x)
        #cls.xcor1 = nodeCoord(eleNodes(3)[0])  # coor of first node
        a = (nodeCoord(cls.n2)[0]-nodeCoord(cls.n1)[0])# X dir
        b = (nodeCoord(cls.n4)[2] - nodeCoord(cls.n1)[2])# Z Dir
        cls.zeta = (pos[0]-nodeCoord(cls.n1)[0])/a # X dir
        cls.eta = (pos[1] - nodeCoord(cls.n1)[2]) /b  # Z Dir

        Nzeta = cls.shape_function(cls.zeta,a)
        Neta = cls.shape_function(cls.eta,b)

        Nv = [Nzeta[0]*Neta[0],Nzeta[2]*Neta[0],Nzeta[2]*Neta[2],Nzeta[0]*Neta[2]]
        Nmx = [Nzeta[1]*Neta[0],Nzeta[3]*Neta[0],Nzeta[3]*Neta[2],Nzeta[0]*Neta[3]]
        Nmz = [Nzeta[0]*Neta[1],Nzeta[2]*Neta[1],Nzeta[2]*Neta[3],Nzeta[0]*Neta[3]]
        #   N1 -> cls.n1 , N2 -> cls.n2 . . . . . N4 -> cls.n4
        load(cls.n1)
        breakpoint()
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def shape_function(cls,zeta,a): # using zeta and a as placeholders for normal coor + length of edge element
        # hermite shape functions
        N1 = (1-3*zeta**2+2*zeta**3)
        N2 = (zeta-2*zeta**2+zeta**3)*a
        N3 = (3*zeta**2-2*zeta**3)
        N4 = (-zeta**2+zeta**3)*a
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


    def load_movingtruck(cls,nodes,truck_pos,axlwts,axlspc,axlwidth):
        # from truck pos(X>0 and Z>0), determine relative location of front top axle on the bridge model
        # truck_pos is a list [X0, Z0]
        # read direction of axlwts and axlspc is from left (i.e. index = 0).
        # first element of axlspc is a placeholder 0, to account for front of vehicle (i.e. first axle)
        for n in range(len(axlwts)): #loop do for each axle
            # axl position with respect to bridge
            # X coor, Z coor
            X1 = truck_pos[0] - axlwts[n]  # X coord of axle
            if X1 > 0 :  # check if axle is on bridge
                #   Inputs:                position[x0,z0],        axle weight at position
                cls.load_position([X1, truck_pos[1]], axlwts[n]) # one side axle
                cls.load_position([X1, truck_pos[1]+axlwidth], axlwts[n]) # other side of axle


# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# Model generation objects


