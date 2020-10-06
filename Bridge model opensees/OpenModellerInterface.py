from tkinter import Tk, Label, Button, Entry
import Bridgemodel
from Bridge_member import BridgeMember


# gui class
class Openseemodeller:
    def __init__(self, master):
        self.master = master
        master.title("Opensees Modeller")
        master.geometry("500x200")

        self.label = Label(master, text="")
        self.label.pack()

        # entries for Bridge class
        # long beam

        # slab

        # LR beam

        # edge beam

        # diaphragm




        # buttons
        self.update_button = Button(master, text="Update", command=self.greet)
        self.update_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.default_bridge_entry = Button(master, text="Autofill default bridge properties", command=self.greet)
        self.default_bridge_entry.pack()

        # option to save load bridge properties

    def greet(self):
        print("Greetings!")

root = Tk()
my_gui = Openseemodeller(root)
root.mainloop()