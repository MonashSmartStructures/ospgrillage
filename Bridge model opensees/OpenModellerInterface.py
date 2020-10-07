from tkinter import *
import Bridgemodel
from Bridge_member import BridgeMember

# gui class
class Openseemodeller:
    def __init__(self, master):
        self.master = master
        master.title("Opensees Modeller")
        master.geometry("1200x500")

        self.label = Label(master, text="")
        self.label.pack()

        # entries for Bridge class
        # long beam
        self.longbeamentry = Entry(master)
        self.longbeamentry.pack(side = RIGHT)
        # slab
        self.slabentry = Entry(master)
        self.slabentry.pack(side = RIGHT)
        # LR beam

        # edge beam

        # diaphragm





        # buttons
        self.update_button = Button(master, text="Update", command=self.greet)
        self.update_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.default_bridge_entry = Button(master, text="Autofill default bridge properties", command=self.defaultbridge())
        self.default_bridge_entry.pack(padx=(100,10))

        # option to save load bridge properties

    def greet(self):
        print("Greetings!")

    def defaultbridge(self):
        self.longbeamentry.insert(10,"1")


root = Tk()
my_gui = Openseemodeller(root)
root.mainloop()