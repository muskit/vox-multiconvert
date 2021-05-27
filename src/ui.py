# TKinter frontend
from tkinter import *
from tkinter import ttk, filedialog, messagebox

from util import *
from database import Database

class InitDirectorySelect(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding='20 20')
        self.master = master
        self.pack()
        self.create_widgets()
    
    def create_widgets(self):
        self.master.title("Set your \"contents\" directory")

        self.path = StringVar()
        self.path.trace('w', self.pathChanged)
        self.txtPath = ttk.Entry(self, width=60, textvariable=self.path)
        self.txtPath.pack()

        self.btnFileDialog = ttk.Button(self, text="Select Folder", command=self.dirDialog, state='focus')
        self.btnFileDialog.pack(side=LEFT)

        self.btnContinue = ttk.Button(self, text="Continue", command=self.continuePressed, state=DISABLED)
        self.btnContinue.pack(side=RIGHT)

    def dirDialog(self):
        newPath = filedialog.askdirectory()
        if newPath != "":
            self.path.set(newPath)

    def continuePressed(self):
        try:
            open_contents_db(self.path.get())
        except FileNotFoundError:
            messagebox.showerror("Error", "{} could not be found. Check that the entered path is correct (should end in \"contents\").".format(MUSIC_DB_PATH))
            return
        except Exception as err:
            print('Unknown error occured: {}'.format(type(err)))
            messagebox.showerror("Error", "Unknown error occured while opening {}.\n{}".format(MUSIC_DB_PATH, err))
            return
        self.master.destroy()

    def pathChanged(self, *args):
        if len(self.path.get()) > 0:
            self.btnContinue.state(['!disabled'])
        else:
            self.btnContinue.state([DISABLED])

class MainApp(ttk.Frame):
    def __init__(self, master, contentPath):
        super().__init__(master, style='BW.TLabel')
        self.master = master
        self.master.title("vox-multiconvert")
        self.grid(sticky='nsew')
        self.db = Database(contentPath)

        self.winfo_toplevel().columnconfigure(0, weight=1)
        self.winfo_toplevel().rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.refreshList()

    def create_widgets(self):
        self.tvList = ttk.Treeview(self.master, columns=('Title', 'Artist', 'Source'))
        self.tvList.heading('#0', text='ID')
        self.tvList.heading('#1', text='Title')
        self.tvList.heading('#2', text='Artist')
        self.tvList.heading('#3', text='Source')
        self.tvList.column('#0', width=80, stretch=NO)
        self.tvList.column('#1', stretch=YES)
        self.tvList.column('#2', stretch=YES)
        self.tvList.column('#3', width=100,stretch=NO)

        self.scrlbrList = ttk.Scrollbar(self.master, command=self.tvList.yview)
        self.tvList.configure(yscrollcommand = self.scrlbrList.set)
        self.tvList.grid(column=0, row=0, sticky='nsew')
        self.scrlbrList.grid(column=1, row=0, sticky='ns')

        self.tvList.bind('<<TreeviewSelect>>', self.onListClick)

    def refreshList(self):
        for elem in self.db.songs:
            song = self.db.songs[elem]
            self.tvList.insert('', 'end', text=elem, values=(song.title, song.artist, song.version))
    
    def onListClick(self, ev):
        sel = self.tvList.selection()
        print('----------')
        for itm in sel:
            print(self.tvList.item(itm, 'text'))

def ui_loop():
    root = Tk()
    root.resizable(False, False)
    
    # set directory
    dirSel = InitDirectorySelect(master=root)
    dirSel.mainloop()
    contentPath = dirSel.path.get()

    if not content_path_valid(contentPath):
        print("Bad path!")
        return
    del root

    root = Tk()
    main = MainApp(root, contentPath)
    main.mainloop()
    