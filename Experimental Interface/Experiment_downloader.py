from tkinter import *
from tkinter import filedialog,simpledialog

# ******* A downloader of TDMs + Integrated pre processing tasks
#  1) Download TDMs
#  2) Select types of output
#  3) Conversion of
# - SN__ read.py for the download button

# *******GUI basics*******
from downloadmethod import downloadSSH

class TDMdownloader:
    def __init__(self, master):
        # Main window frame INITALIZE
        self.root = master # GUI initiator
        self.root.geometry("500x300") # gui frame size
        self.root.title("Hamilton Highway TDMs downloader - Alpha ver.") # create the gui's title
        self.toolbar = Frame(root, bg="gray") # the frame's color # make the tool bars and set frame color

        self.menubar()
        # ******* Main body = consist of buttons and functions **********


        self.toolbar.pack(side = TOP)
        #self.progress = Progressbar(self.root,length = 400, mode = 'determinate') #make progress bar
        #self.progress.pack()

        # 2) Dropdownlists for date and bridge
        self.optionboxes()

        # File listing interface - for user selection and download
        self.listbbb = Listbox(self.root)
        self.listbbb.pack(side = RIGHT,expand = 3)

        self.createbuttons()
        #content = StringVar()
        #self.entry = Entry(root, textvariable=content)
        #self.entry.pack()

        # ******* Status bar *******
        self.status_bar()

# =====================================================================================================

    def menubar(self):
        # - Menu bar programs
        self.menu = Menu(self.root) # Menu bar instantiate
        self.root.config(menu=self.menu) # menu bar items instantiate
        self.subMenu = Menu(self.menu)  # menu bar sub items
        # sub icons of menu bar
        # 1.a
        self.menu.add_cascade(label="File", menu=self.subMenu)  # File option instantiate
        # 1.b
        self.subMenu.add_command(label="New Project", command=lambda:self.do_nothing()) # assign method for clickling New Project

    def optionboxes(self):

        self.bridgeno = StringVar() # placeholders
        self.year = StringVar()
        self.month = StringVar()
        self.day = StringVar()

        self.op1 = OptionMenu(self.root,self.bridgeno,"3595","3604","3614","3615")
        self.op1.place(relx=0.0,rely = 0.5)
        self.op2 = OptionMenu(self.root,self.year,"2018","2019")
        self.op2.place(relx=0.1,rely = 0.5)
        self.op3 = OptionMenu(self.root,self.month,*["%.2d" % i for i in range(1,13)])
        self.op3.place(relx=0.2,rely = 0.5)
        self.op4 = OptionMenu(self.root,self.day,*["%.2d" % i for i in range(1,31)])
        self.op4.place(relx=0.3,rely = 0.5)

    def createbuttons(self):
        self.Downloadbutt = Button(self.toolbar, text="Download daily TDMs", command = lambda:self.DownloadFile())
        self.Downloadbutt.pack()

        self.buttonbrowse = Button(self.root,text = 'Select download folder',command = lambda :self.browsepath())
        self.buttonbrowse.pack()

        self.login = Button(self.root,text = 'Login', command=self.popup)
        self.login.pack()

    def status_bar(self):
        self.status = Label(self.root,text = "Select date and click download to download all files of that date"
                            , bd = 1, relief = SUNKEN, anchor = W)
        self.status.pack(side = BOTTOM, fill = X)
    def do_nothing(self):
        print("doing nothing")
        self.listbbb.insert('end',self.year.get()[2:4])
    def popup(self):
        self.username = simpledialog.askstring("input string","Username")
        self.password= simpledialog.askstring("input string","Password")
        self.listbbb.insert('end',self.username)

    def DownloadFile(self):
        rawcommand = 'SN{bridgeno}1{month}-{day}-{year}'
        filedate = rawcommand.format(bridgeno=self.bridgeno.get(), month=self.month.get(), day=self.day.get(), year=self.year.get()[2:4])
        myHostname = "sn{bridgeno}.ddns.net".format(bridgeno=self.bridgeno.get())
        remotepath = '/media/sdb1/SN{bridgeno}'.format(bridgeno=self.bridgeno.get())
        self.listbbb.insert('end','Downloading')
        self.listbbb.insert('end', myHostname)
        self.listbbb.insert('end', filedate)

        downloadSSH(self.username,self.password,myHostname,filedate,remotepath,self.rawlocalpath)

        self.listbbb.insert('end', self.bridgeno.get())

    def SelectFile(self):
        self.listbbb.insert('end', 'Not implemented yet')

    def browsepath(self):
        self.rawlocalpath= filedialog.askdirectory()
        self.labellocalpath = Label(self.root, text="")
        self.labellocalpath.configure(text=self.rawlocalpath)
        self.labellocalpath.pack()

# -- - - - - Activation  - -- - - -

root = Tk()
downloader = TDMdownloader(root)
root.mainloop()