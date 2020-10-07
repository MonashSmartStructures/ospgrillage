import Bridgemodel
from Bridge_member import BridgeMember
# ---------------------------------------------------------------------------------------------------------------------
# Opensees model generation for Bridge class
# ---------------------------------------------------------------------------------------------------------------------

# Model inputs
Bridgemodel.wipe()  # clear all previous model

# CONCRETE      f'c    ec0    f'cu   ecu
concreteprop = [-6.0, -0.004, -6.0, -0.014]
steelprop = []
# # define bridge element properties

# = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = =
beamelement = "ElasticTimoshenkoBeam"
#beamelement = "elasticBeamColumn"
#                           A  E  G  Jx  Iy   Iz     Avy  Avz       # N m
longbeam = BridgeMember(0.896,34.6522E9 ,20E9 ,0.133,0.214,0.259,0.233,0.58,beamelement)
LRbeam = longbeam
edgebeam = BridgeMember(0.044625,34.6522E9 ,20E9 ,0.26E-3 ,0.114E-3,0.242E-3,0.0371875,0.0371875,beamelement)
slab = BridgeMember(0.4428,34.6522E9 ,20E9 ,2.28E-3 ,0.2233,1.19556E-3,0.369,0.369,beamelement)
diaphragm = BridgeMember(0.2214,34.6522E9,20E9 ,2.17E-3 ,0.111,0.597E-3,0.1845,0.1845,beamelement)
# = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = =
#  Inputs: Lz,  skew angle, Zspacing, number of beams, Lx, Xspacing,:
Bridge2 = Bridgemodel.Bridge(10.175, 0, 2, 5, 24.6, 2.46,beamelement)
#  Inputs: Lz,  skew angle, Zspacing, number of beams, Lx, Xspacing,:
#Bridge2 = Bridgemodel.OpenseesModel(10.11, 0, 1.4224 , 7, 18.288, 0.762)
Bridge2.assign_beam_member_prop(longbeam.get_beam_prop,LRbeam.get_beam_prop,edgebeam.get_beam_prop,slab.get_beam_prop, diaphragm.get_beam_prop)
Bridge2.assign_material_prop(concreteprop,steelprop)
breakpoint()
# Notes
# ---------------------------------------------------------------------------------------------------------------------
# Model generation
Bridge2_OS = Bridgemodel.OpenseesModel()
breakpoint()
#Bridge2.create_Opensees_model()
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Moving load analysis - Combinations of truck position
Bridge2_OS.time_series()
Bridge2_OS.loadpattern()
#                           x y z mx my mz (N m)
#  eg.load_singlepoint(50,[100000,-50000,-50000,0,0,0])

# Truck definition
axlwts = [8, 32, 32]  # kN  # length of axlwts dictates how many axles (e.g. a 5 axle truck will have len = 5)
axlspc = [0, 168, 168]  # m   # len of axlspc should correspond to len(axlwts) - 1 , since its the spacing
axlwidth = 5  # m    # width of truck

# Enter: "First point",
Xloc = [0]      # initial load location (front tyre heading from X = 0)
Zloc = 0        # top axle with resp to Z axis, starting from Z = 0. (code auto calcs bott axle based on truck width)

#Bridge2.load_position([13.5,5],2)
Bridge2_OS.loadID()
#Bridge2.load_movingtruck([13.5,5],axlwts,axlspc,axlwidth)
#breakpoint()
# ------------------------------
# Start of analysis generation
# ------------------------------
Bridgemodel.wipeAnalysis()

# create SOE
Bridgemodel.system("BandSPD")

# create DOF number
Bridgemodel.numberer("RCM")

# create constraint handler
Bridgemodel.constraints("Plain")

# create integrator
Bridgemodel.integrator("LoadControl", 1.0)

# create algorithm
Bridgemodel.algorithm("Linear")

# create analysis object
Bridgemodel.analysis("Static")

# perform the analysis
Bridgemodel.analyze(1)

# Print node displacement results
print(Bridgemodel.nodeDisp(6))
print(Bridgemodel.nodeDisp(17))
print(Bridgemodel.nodeDisp(28))
print(Bridgemodel.nodeDisp(39, 0))
print(Bridgemodel.nodeDisp(50, 0))
print(Bridgemodel.nodeDisp(61, 0))
print(Bridgemodel.nodeDisp(72, 0))


print("Operation finished")
