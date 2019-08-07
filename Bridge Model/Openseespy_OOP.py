from openseespy.opensees import *
import xlrd
import numpy as np

# --------------------------------------------------------------------------------------------------------------------------------
# Class definition - Black box!!! do not change - -- - --
# --------------------------------------------------------------------------------------------------------------------------------

class BeamModel:

    @classmethod
    def __init__(cls, Lx, skewx, Ly, spacingx, spacingy, numbeam):
        cls.spacingx = spacingx
        cls.spacingy = spacingy
        cls.skewx = skewx
        cls.Lx = Lx
        cls.Ly = Ly
        cls.numbeam = numbeam
        cls.numyele = int((cls.Ly / cls.spacingy) )
        cls.ele_x = [0]  # initialize X coord vector
        cls.ele_y = np.linspace(0, cls.Ly, cls.numyele) # generate uniform y coord vector
        count = 1 # counter for x coord loop
        # generate x and y axis vector of edge points
        for x in range(0, cls.numbeam + 1): # loop for each X coord to insert corrd
            b = (cls.Lx - cls.numbeam * cls.spacingx) / 2  # equal edge [Future versions edit here for flexible b]
            if x == 1 or cls.numbeam:  # for first and last node point, spacing is b distance from regular beam spacing
                count += 1
                cls.ele_x.append(x * cls.spacingx + b * count)  # add X coord to list, output is a vector
            else:
                cls.ele_x.append((x * cls.spacingx + b))
        # future versions consider skew - assemble different vector into matrix list
        cls.xv, cls.yv = np.meshgrid(cls.ele_x, cls.ele_y) # used for element_assemble()

    # set modelbuilder
    @classmethod
    def generatemodel(cls,ndm,ndf):
        model('basic', '-ndm', ndm, '-ndf', ndf)
        print("Model dim ={},Model DOF = {}".format(ndm, ndf))

    # create nodes
    @classmethod
    def createnodes(cls):
        for x in range(len(cls.ele_x)):  # loop each node cord pairs in xv and yv, using ele_X as surrogate
            for y in range(len(cls.ele_y)):
                z1 = 0  # [current version is for plane model, future versions allow z to be input]
                node(x*len(cls.ele_y) + y + 1, cls.xv[y,x], cls.yv[y,x] , z1)  # tag starts from 1
        print('Nodes generated = ', x*len(cls.ele_y) + y + 1)  # number here is the total nodes

    # set boundary condition
    @classmethod
    def boundaryconditions(cls):
        countdof = 0

        for x in range(len(cls.ele_x)):
            if x == 0 or x == len(cls.ele_x):  # first and last row correspond to boundary condition
                for y in range(len(cls.ele_y)): #loop each
                    fixval = [1, 1, 1, 1, 1, 1]
                    fix(x*len(cls.ele_y) + y + 1,fixval)


        for x in range(cls.nnode):  # loop each node input
            # fix translation DOF
            fx1 = int(cls.node_data.cell(x + 2, 4).value)
            fy1 = int(cls.node_data.cell(x + 2, 5).value)
            fz1 = int(cls.node_data.cell(x + 2, 6).value)
            rx1 = int(cls.node_data.cell(x + 2, 7).value)
            ry1 = int(cls.node_data.cell(x + 2, 8).value)
            rz1 = int(cls.node_data.cell(x + 2, 9).value)
            fixval = [fx1, rx1, fy1, ry1, fz1, rz1]  # a list of DOF [x,x,y,y,z,z]
            if not (fz1 == 0):  # detect constraint input while looping
                if cls.ndm == 2:  # for ndm = 2-D model,
                    fix(x + 1, fx1, fy1)  # only fix x and y dimensions
                    countdof += 1
                else:  # for ndm = 3-D model
                    fix(x + 1, *fixval)  # fix x y and z
                    countdof += 1
        print('DOF constrained', countdof)

    # define materials
    @classmethod
    def materialprop(cls):
        uniaxialMaterial("Elastic", 1, 3000.0)
        print('Material defined')

    @classmethod
    def ele_transform(cls,zaxis,xaxis):
        cls.transfType = 'Linear'  # transformation type
        cls.longitudinalTransf = 1  # tags
        cls.transverseTransf = 2  # tags
        geomTransf(cls.transfType, cls.longitudinalTransf, *zaxis)
        geomTransf(cls.transfType, cls.transverseTransf, *xaxis)
        print('geometrical transform object created')

    # define elements
    @classmethod
    def element_assemble(cls):
        # Beam/line elements in X dir                               # default - this is longitudinal beams/Sections
        eletypeB = "elasticBeamColumn"
        eletypeSh = "ShellMITC4"
        for x in range(cls.num_ele_X):
            ne_1 = int(cls.X_beam_ele.cell(x + 2, 1).value)
            ne_2 = int(cls.X_beam_ele.cell(x + 2, 2).value)
            eleNodes = (ne_1, ne_2)                             # list of nodes 1 and 2
            Ag = cls.X_beam_ele.cell(x + 2, 3).value
            Ec = cls.X_beam_ele.cell(x + 2, 4).value
            Gc = cls.X_beam_ele.cell(x + 2, 5).value
            Jx = cls.X_beam_ele.cell(x + 2, 6).value
            Iy1 = cls.X_beam_ele.cell(x + 2, 7).value
            Iz1 = cls.X_beam_ele.cell(x + 2, 8).value
            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
            element(eletypeB, x + 1, *eleNodes, Ag, Ec, Gc, Jx, Iy1, Iz1, cls.longitudinalTransf)
            cls.x = x

        print('X-dir Beam element assigned - beams')

        # Beam/line elements in Y dir               # default - this is transverse beam/slabs
        for y in range(cls.num_ele_Y):
            ne_1 = int(cls.Y_beam_ele.cell(y + 2, 1).value)
            ne_2 = int(cls.Y_beam_ele.cell(y + 2, 2).value)
            eleNodes = (ne_1, ne_2)
            Ag = cls.Y_beam_ele.cell(y + 2, 3).value
            Ec = cls.Y_beam_ele.cell(y + 2, 4).value
            Gc = cls.Y_beam_ele.cell(y + 2, 5).value
            Jx = cls.Y_beam_ele.cell(y + 2, 6).value
            Iy1 = cls.Y_beam_ele.cell(y + 2, 7).value
            Iz1 = cls.Y_beam_ele.cell(y + 2, 8).value
            #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transf
            element(eletypeB, cls.x + y + 2, *eleNodes, Ag, Ec, Gc, Jx, Iy1, Iz1, cls.transverseTransf)

        print('Y-dir Beam element assigned - transverse slabs')

    @classmethod
    def time_series(self):
        timeSeries("Linear", 1)

    @classmethod
    def loadpattern(self):
        pattern("Plain", 1, 1)

    @classmethod
    def loadID(self):
        load(39, 100.0, -50.0,0,0,0,0)

    # analysis methods

# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# Running FE model as objects


wipe()
eg = BeamModel(10.175,0,28,2,2.4,5)
eg.generatemodel(3,6)    # 3 dimension, 6 dof (do not change)
eg.createnodes()
print(eg.xv)
breakpoint()
eg.boundaryconditions()
eg.materialprop()
eg.ele_transform([0, 0, 1],[-1, 0, 0])  # insert transformation (default)
# - default values are [0,0,1] for longitudinal, [-1,0,0] for transverse
eg.element_assemble()

# --------------------------------------------------------------------------------------------------------------------------------

eg.time_series()
eg.loadpattern()
eg.loadID()

# ------------------------------
# Start of analysis generation
# ------------------------------
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

ux = nodeDisp(39,1)
uy = nodeDisp(39,2)
print(ux)
print(uy)

print("Operation finished")
