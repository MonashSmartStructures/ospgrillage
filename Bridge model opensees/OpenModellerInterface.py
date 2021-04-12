import tkinter as tk
from tkinter import ttk,filedialog
from Bridgemodel import *                       # bridge opensees model
import pandas as pd                             # pandas for opensees framework
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from Vehicle import *
import pickle
plt.use("TkAgg")


LARGE_FONT = ("Verdana",12)
#-----------------------------------------------------------------------------------------------------------------------
# interface class
class Openseemodeller(tk.Tk):
    def __init__(self, *args,**kwargs):
        # initialize frame
        tk.Tk.__init__(self,*args,**kwargs)
        master = tk.Frame(self)             # master is a frame object
        master.pack(side="top",fill="both",expand=True)
        master.grid_rowconfigure(0,weight=1)
        master.grid_columnconfigure(0,weight=1)
        self.title("Opensees Modeller")
        self.frames={} #empty dict
        for F in [StartPage, TruckPage]:                    #  IMPORTANT< UPDATE PAGES HEREIN
            frame = F(master,self)   # arg is frame object

            self.frames[F]=frame
            frame.grid(row =0,column=0,sticky='nsew')

        self.show_frame(StartPage) # show starting page


    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()
        return frame # return the raised frame

    def get_page(self, classname):
        '''Returns an instance of a page given it's class name as a string'''
        for page in self.frames.values():
            if str(page.__class__.__name__) == classname:
                return page
        return None
# - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Page classes

class StartPage(tk.Frame):
    def __init__(self,parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self,text='Model interface',font=LARGE_FONT)  # label object
        label.grid(row=1,column=1)
        # create button command
        self.createbuttons(controller)
        # initialize menu bar command


        # initialize option bar command

        # miscellaneous


        # Opensees model frame figure - empty widget
        f = Figure(figsize=(5,3),dpi = 100)
        self.a = f.add_subplot(111,projection='3d')
        self.canvas = FigureCanvasTkAgg(f,self)
        self.canvas.get_tk_widget().grid(row=1,column=2,sticky="E")

        # canvas navigation
        toolbarframe = tk.Frame(master=self)
        toolbarframe.grid(row=2,column=2)
        toolbar = NavigationToolbar2Tk(self.canvas,toolbarframe)
        toolbar.update()

        # second widget - truck definition
        #fd = Figure(figsize=(3, 3), dpi=100)
        #self.b = fd.add_subplot(111)
        #self.canvas = FigureCanvasTkAgg(fd, self)
        #self.canvas.get_tk_widget().grid(row=4, column=2, sticky="E")

        # third widget
    def createbuttons(self,controller):
        # button objects
        button1 = tk.Button(self,text="Load Bridge",command= lambda: self.loadbridge())
        button1.grid(row=2,column=1)
        button2 = tk.Button(self,text="Update plot",command= lambda: updateplot(self))
        button2.grid(row=3,column=2)
        button3 = tk.Button(self,text="Run analysis",command= lambda: nothing(self))
        button3.grid(row=4, column=1)
        button4 = tk.Button(self,text="Define Truck",command= lambda: controller.show_frame(TruckPage))
        button4.grid(row=5,column =1)


    def createmenu(self):
        pass
    def createoption(self):
        pass



    # - -  - - -  - - - Opensees methods framework here - - - - -  - - - - - - - - -
    # class/object methods
    # Model generation

    def loadbridge(self):
        # load bridge data on startup
        try:
            self.filepath = filedialog.askopenfilename()
            print("Excel file loaded /n ", self.filepath)
            # read
            self.Nodedetail = pd.read_excel(self.filepath, sheet_name='Node')
            self.Connectivitydetail = pd.read_excel(self.filepath, sheet_name='Connectivity')
            self.Memberdetail = pd.read_excel(self.filepath, sheet_name='Member')
            self.membertrans = pd.read_excel(self.filepath, sheet_name='Member transformation')
            self.concreteprop = [-6.0, -0.004, -6.0, -0.014]
            self.steelprop = []
            self.beamelement = "ElasticTimoshenkoBeam"

            # instantiate OpenseesModel class first, set as attribute of ClassPage.
            #self.Bridge = OpenseesModel(self.Nodedetail, self.Connectivitydetail, self.beamelement, self.Memberdetail
            # ,self.membertrans)

            #self.Bridge.assign_material_prop(self.concreteprop, self.steelprop)
            #self.Bridge.create_Opensees_model()
            bridgeit = {"Name": "Reference Bridge 24.6m",
                        "Nodedetail": self.Nodedetail,
                        "Connectivitydetail":self.Connectivitydetail,
                        "Memberdetail": self.Memberdetail,
                        "Member transformation": self.membertrans,
                        "concreteprop":[-6.0, -0.004, -6.0, -0.014],
                        "steelprop":[],
                        "beamelement":"ElasticTimoshenkoBeam"}
            pickle.dump(bridgeit, open("save.p", "wb"))
            print("bridge loaded and saved as {}".format("save.p"))
        except:
            print("no bridge loaded")


# ---------------------------------------------------------------------------------------------------------------------
class TruckPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Moving Truck Definition', font=LARGE_FONT)  # label object
        label.grid(row=1, column=1)

        # initialize attributes
        self.value=[] # handler for opensees data from StartPage

        # create button command
        self.createbuttons(controller)
        # create entry widgets
        self.create_entry_wid()
        # initialize menu bar command
        self.dropdownwid()
        # initialize option bar command

        # Opensees model frame figure - empty widget

        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.get_tk_widget().grid(row=1, column=2, sticky="E")


    def createbuttons(self, controller):
        # button objects
        button1 = tk.Button(self, text="Return to main page", command=lambda: controller.show_frame(StartPage))
        button1.grid(row=2, column=1)
        button2 = tk.Button(self, text="Update plot", command=lambda: self.get_data())
        button2.grid(row=3, column=2)
        button3 = tk.Button(self, text="Run analysis", command=lambda: runmoving(self))
        button3.grid(row=4, column=2)
        button4 = tk.Button(self, text="Auto fill truck", command=lambda: autofill_truck(self))
        button4.grid(row=11,column = 1)
        button5 = tk.Button(self, text="Process Truck", command=lambda: truckloading(self) )
        button5.grid(row=11, column=2)

    def get_data(self):
        # object method to get
        self.value = self.controller.get_page("StartPage")  # value is handler for properties from StarPage object
        print(self.value.Nodedetail)        # value handler is assigned as an attribute in object - self.value
        print(self.value.Bridge)

    def create_entry_wid(self):
        self.entry1 = tk.Entry(self)
        self.entry1.insert(0, "Axle weights")
        self.entry1.grid(row=4,column=1)

        self.entry2 = tk.Entry(self)
        self.entry2.insert(0, "Axle spacings")
        self.entry2.grid(row=5, column=1)

        self.entry3 = tk.Entry(self)
        self.entry3.insert(0, "Axle widths")
        self.entry3.grid(row=6, column=1)

        self.entry4 = tk.Entry(self)
        self.entry4.insert(0, "Initial position")
        self.entry4.grid(row=8, column=1)

        self.entry5 = tk.Entry(self)
        self.entry5.insert(0, "Travel distance")
        self.entry5.grid(row=9, column=1)

        self.entry6 = tk.Entry(self)
        self.entry6.insert(0, "Increment")
        self.entry6.grid(row=10, column=2)

        self.entry7 = tk.Entry(self)
        self.entry7.insert(0,"Start coordinate")
        self.entry7.grid(row=9,column=2)


    def dropdownwid(self):
        self.directionbox = ttk.Combobox(self,width = 17,values=["X","Z"])
        self.directionbox.grid(column=2,row=8)

# - -  - - -  - - - Opensees methods for moving force analysis - - - - -  - - - - - - - - -
f = Figure(figsize=(3, 3), dpi=100)
truckplot = f.add_subplot(111)

    # static methods
def truckloading(self):
    # convert entry strings to int
    self.axlwts = commasplitting(self.entry1.get())
    self.axlspc =  commasplitting(self.entry2.get())
    self.axlwidth = float(self.entry3.get())
    X,Y,weights = truckplotting(self.axlspc,self.axlwidth,self.axlwts)
    # update graphical representation of truck model
    truckplot.clear()
    truckplot.scatter(X,Y)
    self.canvas.draw_idle()
    #
    # create vehicle class
    self.ModelledTruck = vehicle(self.axlwts,self.axlspc,self.axlwidth,
                                 commasplitting(self.entry7.get()),float(self.entry5.get()),float(self.entry6.get()),
                                 self.directionbox.get())
    # create vehicle movement class
    # inputs:                start coordinate, increment, travel distance

    #self.value.Bridge.load_movingtruck()
    #function to call moving force, with switcher depending on travelling direction : either X or Z direction

    no_point = (self.ModelledTruck.initial_position[0] + self.ModelledTruck.travel_length
                + self.ModelledTruck.increment) / self.ModelledTruck.increment
    self.refPos_X = np.linspace(self.ModelledTruck.initial_position[0], self.ModelledTruck.travel_length, round(no_point))

    # order of moving force analysis
    # for loop,
    # for each position,
    for r in range(len(self.refPos_X)):
        # 1 recreate model instance
        recreatemodel_instance(self)
        # 2 position load at r onto model

        for i in range(len(X)):

            # for each value is X (Xlist) for truck axle, impose load into model
            currentpos = [X[i]+self.refPos_X[r],Y[i]+self.ModelledTruck.initial_position[1]]
            self.value.Bridge.load_position(currentpos,weights[i])

        # 3 run runmoving()
        runmoving(self)
        # save (BM. SF)

def commasplitting(axl_list):
    axl_list = [float(i) for i in axl_list.split(',')]
    return axl_list

def recreatemodel_instance(self):
    # method to run in between each time step of moving truck analysis
    self.value.Bridge = OpenseesModel(self.value.Nodedetail, self.value.Connectivitydetail, self.value.beamelement, self.value.Memberdetail)
    self.value.Bridge.assign_material_prop(self.value.concreteprop, self.value.steelprop)
    self.value.Bridge.create_Opensees_model()
    self.value.Bridge.time_series()
    self.value.Bridge.loadpattern()

def runmoving(self):
    # method to run after recreatemodel_instance
    # self.value attribute is a handler for getdata function
    # Input: "Bridge" is object of OpenseesModel Class - an attribute of StartPage class

    #self.value.Bridge.load_position([10, 8], -2000)

    # wipe analysis
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
    print([nodeDisp(1)[1], nodeDisp(2)[1], nodeDisp(3)[1], nodeDisp(4)[1], nodeDisp(5)[1], nodeDisp(6)[1],
           nodeDisp(7)[1], nodeDisp(8)[1], nodeDisp(9)[1], nodeDisp(10)[1], nodeDisp(11)[1]])

def recordmoving(self):
    self.BM = np.zeros((round(no_point), Bridgemodel.OpenseesModel.totalnodes))  # Array for bending moment
    self.SF = np.zeros((round(no_point), Bridgemodel.OpenseesModel.totalnodes))  # Array for shear force

def autofill_truck(self):
    self.entry1.delete(first=0,last=len(self.entry1.get()))
    self.entry1.insert(0,"800, 3200, 3200")
    self.entry2.delete(first=0, last=len(self.entry2.get()))
    self.entry2.insert(0, "7, 7")
    self.entry3.delete(first=0, last=len(self.entry3.get()))
    self.entry3.insert(0, "5")
    self.entry4.delete(first=0, last=len(self.entry4.get()))
    self.entry4.insert(0, "0, 3.0875")
    self.entry5.delete(first=0, last=len(self.entry5.get()))
    self.entry5.insert(0, "50")
    self.entry6.delete(first=0, last=len(self.entry6.get()))
    self.entry6.insert(0, "2")
    self.entry7.delete(first=0, last=len(self.entry7.get()))
    self.entry7.insert(0, "0, 3.0875")

def truckplotting(axlspc,axlwidth,axlwts):
    # create array of truck axles X and Y lists for plotting
    xList=[0, 0]
    yList = [0, axlwidth]
    weightlist =[axlwts[0],axlwts[0]] # first two axles ,first two inputs of axlwts
    for i in range(len(axlspc)):
        last = xList[-1] # get last element in current xList array
        for ycoor in [0, axlwidth]:
            xList.append(last+axlspc[i]) # add axl spacing to current last element of xList
            yList.append(ycoor)         # add y coord to list
            weightlist.append(axlwts[i+1])
    return xList,yList,weightlist
# ---------------------------------------------------------------------------------------------------------------------
# ============================================================================================================

# ============================================================================================================
# Functions and methods - for global class - masters

def nothing():
    print("do nothing")

def updateplot(self):
    # Generate and update plot for bridge
    self.a.scatter(self.Nodedetail['x'], self.Nodedetail['z'], self.Nodedetail['y'], c='k', edgecolor='k')
    self.a.set_xlabel('x (m)')
    self.a.set_ylabel('z (m)')
    self.a.set_zlabel('y (m)')
    print("nodes plotted")
    # plot beam element lines
    for index, row in self.Connectivitydetail.iterrows():
        # print(index,row['node_i'],row['node_j'],row['tag'])

        # search x z y for first point
        x1 = self.Nodedetail['x'][self.Nodedetail['nodetag'] == row['node_i']].max()
        y1 = self.Nodedetail['y'][self.Nodedetail['nodetag'] == row['node_i']].max()
        z1 = self.Nodedetail['z'][self.Nodedetail['nodetag'] == row['node_i']].max()

        # search x z y for second point
        x2 = self.Nodedetail['x'][self.Nodedetail['nodetag'] == row['node_j']].max()
        y2 = self.Nodedetail['y'][self.Nodedetail['nodetag'] == row['node_j']].max()
        z2 = self.Nodedetail['z'][self.Nodedetail['nodetag'] == row['node_j']].max()

        self.a.plot([x1, x2], [z1, z2], [y1, y2], color='k')  # plot line for two nodes
    print("elements plotted")
    self.canvas.draw_idle()


# ======================================================================================================================


my_gui = Openseemodeller()
#ani = animation.FuncAnimation
my_gui.mainloop()
