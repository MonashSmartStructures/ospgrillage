import openseespy.postprocessing.Get_Rendering as opsplt
import matplotlib.pyplot as plt
import openseespy.postprocessing.ops_vis as opsv
# file containing functions adopting plot/visualization features
# from Opensees post processing package version 3.2.2.6

def plotOPmodel(self):
    # Display active model with Node tags and elements
    opsplt.plot_model("nodes")

def plotBending(self):
    pass

def plotDeformation(self):
    fig_wi_he = 30., 20.
    sfac = 2
    nep =17
    opsv.plot_defo()
