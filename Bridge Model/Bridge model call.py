import Bridgemodel as BM
# --------------------------------------------------------------------------------------------------------------------------------
# Model inputs
BM.wipe()  # clear any previous models
#         Inputs: Lx,  skew angle,  Lz, Xspacing, Zspacing, number of beams:
eg = BM.BeamModel(10.175, 0, 28, 2, 2.4, 5)
#(10.175, 0, 28, 2, 2.4, 5) # for 27m model
# (18.288, 0, 10.11 ,2.8448,0.762, 7)

# # define bridge element properties
#        A  E  G  Jx  Iy   Iz                   # N m
longbeam = [0.41631,31.113E9 ,1 ,4.23662E-3,0.0380607,0.0484717]
LRbeam = [0.543153,31.113E9 ,1 ,9.41034E-3 ,0.0634485 ,0.0646434]
edgebeam = [7.5E-3,31.113E9 ,1 ,4.93885E-6 ,1.5625E-6 ,14.0625E-6]
slab = [0.116129,31.113E9 ,1 ,0.392896E-3 ,5.61912E-3,0.224765E-3]
diaphragm = [0.0580644,31.113E9 ,1 ,0.168245E-3 ,0.702391E-3 ,0.112382E-3]

# CONCRETE      f'c    ec0    f'cu   ecu
concreteprop = [-6.0, -0.004, -5.0, -0.014]
# --------------------------------------------------------------------------------------------------------------------------------
# Model generation
#    Inputs:(defaulted) ndm , ndof
eg.generatemodel(3, 6)
eg.createnodes()
eg.boundaryconditions()
print("X coord = ", eg.ele_x)
print("Y coord = ", eg.ele_z)

eg.materialprop(concreteprop)

#        trans: (1)long beam, (2) transverse  [ x y z]
eg.ele_transform([0, 0, 1], [-1, 0, 0])  # insert transformation (default)
# - default values are [0,0,1] for longitudinal, [-1,0,0] for transverse

eg.element_assemble(longbeam, LRbeam, edgebeam, slab, diaphragm)

# --------------------------------------------------------------------------------------------------------------------------------
# Moving load analysis - Combinations of truck position
eg.time_series()
eg.loadpattern()
#eg.loadID()
eg.load_singlepoint(50,[100000,-50000,-50000,0,0,0]) # x y z mx my mz (N m)
#eg.load_position([13.5,5])

# Truck definition
axlwts = [8, 32, 32]  # kN  # length of axlwts dictates how many axles (e.g. a 5 axle truck will have len = 5)
axlspc = [0, 168, 168] # m   # len of axlspc should correspond to len(axlwts) - 1 , since its the spacing
axlwidth = 5 # m    # width of truck

# Enter: "First point",
Xloc = [0]      # initial load location (front tyre heading from X = 0)
Zloc = 0        # top axle with resp to Z axis, starting from Z = 0. (code auto calcs bott axle based on truck width)


# ------------------------------
# Start of analysis generation
# ------------------------------
BM.wipeAnalysis()
# create SOE
BM.system("BandSPD")

# create DOF number
BM.numberer("RCM")

# create constraint handler
BM.constraints("Plain")

# create integrator
BM.integrator("LoadControl", 1.0)

# create algorithm
BM.algorithm("Linear")

# create analysis object
BM.analysis("Static")

# perform the analysis
BM.analyze(1)

ux = BM.nodeDisp(50, 1)
uy = BM.nodeDisp(50, 3)
print(ux)
print(uy)
breakpoint()
print("Operation finished")
