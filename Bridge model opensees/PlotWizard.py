import openseespy.postprocessing.Get_Rendering as opsplt
# file containing functions adopting plot/visualization features
# from Opensees post processing package version 3.2.2.6

def plotOPmodel(self):
    # Display active model with Node tags and elements
    opsplt.plot_model("nodes")

def plotBending(self):
    pass


