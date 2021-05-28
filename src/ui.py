# TKinter frontend
import collections
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from structs import Difficulty, Song
from util import *
from database import Database

# Directory Setting Window
# Once done selecting, access selected path with .path.get()
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
        self.txtPath.grid(row=0, column=0)

        self.btnFileDialog = ttk.Button(self, text="Open Folder", command=self.dirDialog, width=10)
        self.btnFileDialog.grid(row=0, column=1)

        self.btnContinue = ttk.Button(self, text="Continue", command=self.continuePressed, state=DISABLED, width=10)
        self.btnContinue.grid(row=1, column=1)

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

class SongPreview(ttk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.master = master
        self.db = db
        self.create_widgets()

    def create_widgets(self):
        self.lblTitle = ttk.Label(self, text="Title", anchor='w', justify=LEFT)
        self.lblArtist = ttk.Label(self, text="Artist", anchor='w', justify=LEFT)
        self.lblSource = ttk.Label(self, text="Source", anchor='w', justify=LEFT)
        self.lblDate = ttk.Label(self, text="Date released", anchor='w', justify=LEFT)
        self.diff = []
        for idx in range(0,4):
            self.diff.append(SongDifficulty(self, self.db))
            self.diff[idx].grid(column=idx, row=0, rowspan=20) # high rowspan for lazy layout creation
        self.diff[3].configure(padding='0 0 15 0')

        self.lblTitle.grid(column=4, row=4, sticky=W)
        self.lblArtist.grid(column=4, row=5, sticky=W)
        self.lblSource.grid(column=4, row=6, sticky=W)
        self.lblDate.grid(column=4, row=7, sticky=W)

    def set_song(self, ev=None):
        global songClicked
        self.lblTitle.configure(text=songClicked.title)
        self.lblArtist.configure(text=songClicked.artist)
        self.lblSource.configure(text=songClicked.version)
        
        idx = 0
        for curDiff in songClicked.diffArr:
            self.diff[idx].set_diff(curDiff)
            idx += 1
        if idx-1 < 3:
            for i in range (idx, 4):
                self.diff[i].set_diff()

class SongDifficulty(ttk.Frame):
    def __init__(self, master, db: Database):
        super().__init__(master)
        self.master = master
        self.db = db
        self.create_widgets()

    def create_widgets(self):
        img = Image.open("../assets/jacket-placeholder.png")
        imgR = img.resize((80,80))
        self.imgTk = ImageTk.PhotoImage(imgR)
        self.lblDif = ttk.Label(self)
        self.lblImg = ttk.Label(self)
        self.lblLvl = ttk.Label(self)
        self.varEff = StringVar(self)
        self.lblEff = ttk.Entry(self, width=9, justify=CENTER, textvariable=self.varEff, state='readonly')
        self.imgTk = None
        self.set_diff()

        self.lblDif.pack()
        self.lblImg.pack()
        self.lblLvl.pack()
        self.lblEff.pack()
        # self.lblIll.pack()

    def set_diff(self, newDiff: Difficulty = None):
        global songClicked
        self.lblDif.configure(text=newDiff.tag if newDiff != None else 'DIFF')
        self.lblLvl.configure(text=newDiff.num if newDiff != None else 'LVL')
        self.varEff.set(newDiff.effector if newDiff != None else 'EFF')

        if newDiff == None:
            img = Image.open("../assets/jacket-placeholder.png")
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        else: # set self.imgTk to be jacket
            img = Image.open("{}/data/music/{}/{}".format(self.db.contentPath, songClicked.folder, newDiff.illustPath))
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        self.lblImg.configure(image=self.imgTk)

class SongList(ttk.Frame):
    def __init__(self, master, db: Database):
        super().__init__(master)
        self.master = master
        self.db = db
        
        self.create_widgets()
        self.refreshList()

    def create_widgets(self):
        self.songList = ttk.Treeview(self, columns=('Title', 'Artist', 'Source'))
        self.songList.heading('#0', text='ID')
        self.songList.heading('#1', text='Title')
        self.songList.heading('#2', text='Artist')
        self.songList.heading('#3', text='Source')
        self.songList.column('#0', width=80, stretch=NO)
        self.songList.column('#1', stretch=YES)
        self.songList.column('#2', stretch=YES)
        self.songList.column('#3', width=100,stretch=NO)
        
        self.songList.bind('<ButtonRelease-1>', self.onListSel)
        
        self.scrlbrList = ttk.Scrollbar(self, command=self.songList.yview)
        self.songList.configure(yscrollcommand = self.scrlbrList.set)
        self.songList.grid(column=0, row=0, sticky='nsew')
        self.scrlbrList.grid(column=1, row=0, sticky='ns')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def refreshList(self):
        for elem in self.db.songs:
            song = self.db[elem]
            self.songList.insert('', 'end', text=elem, values=(song.title, song.artist, song.version))
    
    def onListSel(self, ev):
        sel = self.songList.selection()
        global songSelected
        songSelected = []
        for _, elem in enumerate(sel):
            songSelected.append(self.songList.item(elem, 'text'))

        clickId = self.songList.item(self.songList.identify_row(ev.y), 'text')
        if clickId != '' and clickId in songSelected:
            global songClicked
            songClicked = self.db[clickId]
            self.event_generate('<<clickedSong>>')

# main application window
class MainApp(ttk.Frame):
    def __init__(self, master, contentPath):
        super().__init__(master)
        self.master = master
        self.master.title("vox-multiconvert")
        self.pack(expand=YES, fill=BOTH)
        self.db = Database(contentPath)
        self.create_widgets()

    def create_widgets(self):
        self.songList = SongList(self, self.db)
        self.songPreview = SongPreview(self, self.db)
        self.pnlOptions = ttk.Frame(self)
        self.pnlOptions.btnSelAll = ttk.Button(self.pnlOptions, text='Select All')
        self.pnlOptions.btnConvert = ttk.Button(self.pnlOptions, text='Convert')
        self.pnlOptions.lblSelCnt = ttk.Label(self.pnlOptions, text='Selected 0 songs')

        self.songList.grid(row=0, column=0, sticky='nsew')
        self.songPreview.grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.pnlOptions.grid(row=2, sticky='we', padx=10, pady=10)
        self.pnlOptions.btnConvert.pack(side=RIGHT)
        self.pnlOptions.btnSelAll.pack(side=RIGHT)
        self.pnlOptions.lblSelCnt.pack(side=LEFT)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.songList.bind('<<clickedSong>>', self.songPreview.set_song)

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
    