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
        self.okClicked = False
    
    def create_widgets(self):
        self.master.title("Set your \"contents\" directory")

        self.path = StringVar()
        self.path.trace('w', self.pathChanged)
        self.txtPath = ttk.Entry(self, width=60, textvariable=self.path)
        self.txtPath.pack()

        self.btnContinue = ttk.Button(self, text="Continue", command=self.continuePressed, state=DISABLED)
        self.btnContinue.pack(side=RIGHT)

        self.btnFileDialog = ttk.Button(self, text="Browse", command=self.dirDialog)
        self.btnFileDialog.pack(side=RIGHT)

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
        self.okClicked = True
        self.master.destroy()

    def pathChanged(self, *args):
        if len(self.path.get()) > 0:
            self.btnContinue.state(['!disabled', 'focus'])
            self.btnFileDialog.state(['!focus', 'disabled'])
        else:
            self.btnFileDialog.state(['!focus'])
            self.btnContinue.state(['disabled'])

class SongPreview(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.varTitle = StringVar(self, 'Title')
        self.varArtist = StringVar(self, 'Artist')
        # self.lblTitle = ttk.Label(self, text="Title", anchor='w', justify=LEFT)
        self.entTitle = ttk.Entry(self, textvariable=self.varTitle, state='readonly')
        # self.lblArtist = ttk.Label(self, text="Artist", anchor='w', justify=LEFT)
        self.entArtist = ttk.Entry(self, textvariable=self.varArtist, state='readonly')
        self.lblSource = ttk.Label(self, text="Source", anchor='w', justify=LEFT)
        self.lblDate = ttk.Label(self, text="Date released", anchor='w', justify=LEFT)
        self.diff = []
        for idx in range(0,4):
            self.diff.append(SongDifficulty(self))
            self.diff[idx].grid(column=idx, row=0, rowspan=20) # high rowspan for lazy layout creation
        self.diff[3].configure(padding='0 0 15 0')

        self.entTitle.grid(column=4, row=4, sticky='we')
        self.entArtist.grid(column=4, row=5, sticky='we')
        self.lblSource.grid(column=4, row=6, sticky=W)
        self.lblDate.grid(column=4, row=7, sticky=W)

    def set_song(self, ev=None):
        global songSelected
        if songSelected == None: return

        self.varTitle.set(songSelected.title)
        self.varArtist.set(songSelected.artist)
        self.lblSource.configure(text=VERSION_GAME[songSelected.version])
        self.lblDate.configure(text=songSelected.dateReleased.strftime('%Y/%m/%d'))
        
        idx = 0
        for curDiff in songSelected.diffArr:
            self.diff[idx].set_diff(curDiff)
            idx += 1
        if idx-1 < 3:
            for i in range (idx, 4):
                self.diff[i].set_diff()

class SongDifficulty(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.lblDif = ttk.Label(self)
        self.lblImg = ttk.Label(self)
        self.lblLvl = ttk.Label(self)
        self.varEff = StringVar(self)
        self.entEff = ttk.Entry(self, width=9, justify=CENTER, textvariable=self.varEff, state='readonly')
        self.imgTk = None
        self.set_diff()

        self.lblDif.pack()
        self.lblImg.pack()
        self.lblLvl.pack()
        self.entEff.pack()

    def set_diff(self, newDiff: Difficulty = None):
        global songDb
        global songSelected
        self.lblDif.configure(text=newDiff.tag if newDiff != None else '---')
        self.lblLvl.configure(text=newDiff.num if newDiff != None else '---')
        self.varEff.set(newDiff.effector if newDiff != None else '---')

        if newDiff == None:
            img = Image.open("./assets/jacket-placeholder.png")
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        else: # set self.imgTk to be jacket
            img = Image.open("{}/data/music/{}/{}".format(songDb.contentPath, songSelected.folder, newDiff.illustPath))
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        self.lblImg.configure(image=self.imgTk)

class SongList(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        self.create_widgets()
        self.refreshList()

    def create_widgets(self):
        self.trelSong = ttk.Treeview(self, columns=('Title', 'Artist', 'Source'))
        self.trelSong.heading('#0', text='ID')
        self.trelSong.heading('#1', text='Title')
        self.trelSong.heading('#2', text='Artist')
        self.trelSong.heading('#3', text='Source')
        self.trelSong.column('#0', width=80, stretch=NO)
        self.trelSong.column('#1', stretch=YES)
        self.trelSong.column('#2', stretch=YES)
        self.trelSong.column('#3', width=100,stretch=NO)
        
        self.trelSong.bind('<<TreeviewSelect>>', self.onListSel)
        
        self.scrlbrSong = ttk.Scrollbar(self, command=self.trelSong.yview)
        self.trelSong.configure(yscrollcommand = self.scrlbrSong.set)
        self.trelSong.grid(column=0, row=0, sticky='nsew')
        self.scrlbrSong.grid(column=1, row=0, sticky='ns')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def refreshList(self):
        global songDb
        for elem in songDb.songs:
            song = songDb[elem]
            self.trelSong.insert('', 'end', text=elem, values=(song.title, song.artist, song.version))
    
    def onListSel(self, ev):
        global songDb
        global songSelections
        global songSelected
        sels = self.trelSong.selection()
        songSelections = []
        for _, elem in enumerate(sels):
            songSelections.append(self.trelSong.item(elem, 'text'))

        # for song preview
        selId = self.trelSong.item(self.trelSong.focus(), 'text')
        if selId != '':
            songSelected = songDb[selId]
        else:
            songSelected = None
        
        self.event_generate('<<selectedSong>>')
    
    def select_all(self, *pargs):
        self.trelSong.selection_set(self.trelSong.get_children())

# main application window
class MainApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("vox-multiconvert")
        self.pack(expand=YES, fill=BOTH)
        self.create_widgets()

    def create_widgets(self):
        self.songList = SongList(self)
        self.songPreview = SongPreview(self)
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

        self.songList.bind('<<selectedSong>>', self.on_song_selected)
        self.pnlOptions.btnSelAll.bind('<ButtonRelease>', self.songList.select_all)

    def on_song_selected(self, ev):
        global songDb
        self.songPreview.set_song()
        global songSelections
        size = '{}/{}'.format(len(songSelections), len(songDb.tree))
        if len(songSelections) == 1:
            self.pnlOptions.lblSelCnt.configure(text='Selected {} song'.format(size))
        else:
            self.pnlOptions.lblSelCnt.configure(text='Selected {} songs'.format(size))

def ui_loop():
    root = Tk()
    root.resizable(False, False)
    
    # set directory
    dirSel = InitDirectorySelect(master=root)
    dirSel.mainloop()
    del root
    if not dirSel.okClicked: return

    contentPath = dirSel.path.get()
    if not content_path_valid(contentPath):
        print("Bad path!")
        return

    global songDb
    songDb = Database(contentPath)
    root = Tk()
    main = MainApp(root)
    main.mainloop()
    