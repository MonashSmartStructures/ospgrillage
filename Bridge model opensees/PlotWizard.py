import openseespy.postprocessing.Get_Rendering as opsplt
import matplotlib.pyplot as plt
import openseespy.postprocessing.ops_vis as opsv
# file containing functions adopting plot/visualization features
# from Opensees post processing package version 3.2.2.6

def plotOPmodel(self):
    # Display active model with Node tags and elements
    opsplt.plot_model("nodes")

def plotBending(self):
    Ew = {}
    sfacMy = 1.e-2
    minY, maxY = opsv.section_force_diagram_3d('Mz', Ew, sfacMy)
    plt.title(f'Bending moments Mz, max = {maxY:.2f}, min = {minY:.2f}')
    plt.show()

def plotShear(self):
    Ew = {}
    sfacMy = 1.e-2
    minY, maxY = opsv.section_force_diagram_3d('Vy', Ew, sfacMy)
    plt.title(f'Bending moments My, max = {maxY:.2f}, min = {minY:.2f}')
    plt.show()

def plotDeformation(self):
    fig_wi_he = 30., 20.
    sfac = 1
    nep =17
    opsv.plot_defo(sfac, nep, fmt_interp='b-', az_el=(-68., 39.),
               fig_wi_he=fig_wi_he, endDispFlag=0)
    plt.show()
    breakpoint()