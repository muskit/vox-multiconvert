# TKinter frontend
import collections
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import ffmpeg

from structs import Difficulty, Song
from util import *
from database import Database
from convert import *
import gbl

# Directory Setting Window
# Once done selecting, access selected path with .path.get()
class InitDirectorySelect(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padding='10 10')
        self.master = master
        self.pack()
        self.okClicked = False
        self.list = None
        self.create_widgets()
    
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

    def dirDialog(self):
        newPath = filedialog.askdirectory()
        if newPath != "":
            self.path.set(newPath)

    def pathChanged(self, *args):
        if len(self.path.get()) > 0:
            self.btnContinue.state(['!disabled'])
        else:
            self.btnContinue.state(['disabled'])

class SongList(ttk.Frame):
    def __init__(self, master, conversion=False):
        super().__init__(master)
        self.master = master
        self.conversion = conversion
        self.create_widgets()
        self.refreshList()

    def create_widgets(self):
        self.tblSong = ttk.Treeview(self, columns=('Title', 'Artist', 'Source'))
        self.tblSong.heading('#0', text='ID')
        self.tblSong.heading('#1', text='Title')
        self.tblSong.heading('#2', text='Artist')
        self.tblSong.heading('#3', text='Source')
        self.tblSong.column('#0', width=80, stretch=NO)
        self.tblSong.column('#1', stretch=YES)
        self.tblSong.column('#2', stretch=YES)
        self.tblSong.column('#3', width=100,stretch=NO)
        
        self.tblSong.bind('<<TreeviewSelect>>', self.onListSel)
        
        self.scrlbrSong = ttk.Scrollbar(self, command=self.tblSong.yview)
        self.tblSong.configure(yscrollcommand = self.scrlbrSong.set)
        self.tblSong.grid(column=0, row=0, sticky='nsew')
        self.scrlbrSong.grid(column=1, row=0, sticky='ns')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def refreshList(self):
        if self.conversion:
            self.list = gbl.songIdSelections
            self.tblSong.configure(selectmode='none')
        else:
            self.list = gbl.songDb.songs
        for elem in self.list:
            song = gbl.songDb[elem]
            self.tblSong.insert('', 'end', text=elem, values=(song.title, song.artist, song.version))

        self.tblSong.tag_configure('done', foreground='gray')
        # itmList = self.tblSong.get_children()
        # self.tblSong.selection_toggle(itmList[0]) <---- CONVERSION: how to mark in-progress conversion
        # self.tblSong.item(itmList[0], tags=('done')) <--- CONVERSION: how to mark item as done visually
    
    def onListSel(self, ev):
        sels = self.tblSong.selection()
        gbl.songIdSelections = []
        for elem in sels:
            gbl.songIdSelections.append(self.tblSong.item(elem, 'text'))

        # for song preview
        selId = self.tblSong.item(self.tblSong.focus(), 'text')
        if selId != '':
            gbl.songSelected = gbl.songDb[selId]
        else:
            gbl.songSelected = None

        self.event_generate('<<selectedSong>>')
    
    def select_all(self):
        self.tblSong.selection_set(self.tblSong.get_children())

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
        if gbl.songSelected == None: return

        self.varTitle.set(gbl.songSelected.title)
        self.varArtist.set(gbl.songSelected.artist)
        self.lblSource.configure(text=VERSION_GAME[gbl.songSelected.version])
        self.lblDate.configure(text=gbl.songSelected.dateReleased.strftime('%Y/%m/%d'))
        
        idx = 0
        for curDiff in gbl.songSelected.diffArr:
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
        self.lblDif.configure(text=newDiff.tag if newDiff != None else '---')
        self.lblLvl.configure(text=newDiff.num if newDiff != None else '---')
        self.varEff.set(newDiff.effector if newDiff != None else '---')

        if newDiff == None:
            img = Image.open("./assets/jacket-placeholder.png")
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        else: # set self.imgTk to be jacket
            img = Image.open("{}/{}/{}/{}".format(gbl.songDb.contentPath, MUSIC_PATH, gbl.songSelected.folder, newDiff.illustPath))
            imgR = img.resize((80,80))
            self.imgTk = ImageTk.PhotoImage(imgR)
        self.lblImg.configure(image=self.imgTk)

class ConvertWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title('Conversion')
        self.pack(expand=YES, fill=BOTH)
        self.create_widgets()
        self.master.master.master.withdraw() # hide main window
    
    def create_widgets(self):
        self.lblMsg = ttk.Label(self, text='The following songs will be converted:', justify='left')
        self.tblList = SongList(self, conversion=True)
        self.progressBar = ttk.Progressbar(self, maximum=len(gbl.songIdSelections), mode='determinate', orient=HORIZONTAL)
        self.strProgress = StringVar()
        self.lblProgress = ttk.Label(self, textvariable=self.strProgress)
        self.pnlOptions = ttk.Frame(self, padding='10 10')
        self.strPath = StringVar(None, gbl.exportDir)
        self.strPath.trace('w', self.path_changed)
        self.lblPath = ttk.Label(self.pnlOptions, text='Export to', justify='left')
        self.entPath = ttk.Entry(self.pnlOptions, width=60, textvariable=self.strPath)
        self.btnBrowse = ttk.Button(self.pnlOptions, text="Browse", command=self.dir_dialog)
        self.btnConvert = ttk.Button(self.pnlOptions, text='Convert', command=self.begin_conversion)
        self.btnCancel = ttk.Button(self.pnlOptions, text='Cancel', command=self.master.destroy)

        self.lblMsg.pack()
        self.tblList.pack(expand=YES, fill=BOTH)
        self.progressBar.pack(fill=X, padx=10)
        self.lblProgress.pack()
        self.pnlOptions.pack(anchor=E, fill=X)
        self.lblPath.pack(anchor=W)
        self.entPath.pack(fill=X)
        self.btnBrowse.pack(side=LEFT)
        self.btnConvert.pack(side=RIGHT)
        self.btnCancel.pack(side=RIGHT)

        if len(self.strPath.get()) > 0:
            self.btnConvert.state(['!disabled'])
        else:
            self.btnConvert.state(['disabled'])

    def dir_dialog(self):
        newPath = filedialog.askdirectory()
        if newPath != "":
            self.strPath.set(newPath)

    def path_changed(self, *pargs):
        gbl.exportDir = self.strPath.get()
        if len(self.strPath.get()) > 0:
            self.btnConvert.state(['!disabled'])
        else:
            self.btnConvert.state(['disabled'])

    def begin_conversion(self):
        # disable window closing
        self.master.winfo_toplevel().protocol("WM_DELETE_WINDOW", lambda: None)
        # disable widgets
        self.entPath.state(['disabled'])
        self.btnBrowse.state(['disabled'])
        self.btnConvert.state(['disabled'])
        self.btnCancel.state(['disabled'])
        # convert files
        for idx, id in enumerate(gbl.songIdSelections):
            self.strProgress.set('Converting ID {} [{}/{}]'.format(id, idx+1, len(gbl.songIdSelections)))
            self.update()
            try:
                create_song_directory(id)
                convert_chart(id)
                convert_audio(id)
            except Exception as ex:
                messagebox.showerror('Error', ex)
            finally:
                self.progressBar['value'] += 1.0
                self.update()
        self.strProgress.set('Done! [{}/{}]'.format(idx+1, len(gbl.songIdSelections)))
        self.update()
        # restore widgets
        self.entPath.state(['!disabled'])
        self.btnBrowse.state(['!disabled'])
        self.btnConvert.state(['!disabled'])
        self.btnCancel.state(['!disabled']) # TODO: stop after current song
        # re-enable window closing
        self.master.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.master.destroy)

    def destroy(self):
        self.master.master.winfo_toplevel().deiconify()
        self.master.master.update()
        super().destroy()

# main application window
class MainApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("vox-multiconvert")
        self.pack(expand=YES, fill=BOTH)
        self.create_widgets()

    def create_widgets(self):
        self.menu = Menu(self)
        self.menuFile = Menu(self.menu, tearoff=0)
        self.menuEdit = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label = 'File', menu = self.menuFile)
        self.menu.add_cascade(label = 'Edit', menu = self.menuEdit)
        self.menuFile.add_command(label='Open contents...')
        self.menuEdit.add_command(label='Preferences')
        self.songList = SongList(self)
        self.songPreview = SongPreview(self)
        self.pnlOptions = ttk.Frame(self, padding='10 10')
        self.pnlOptions.btnSelAll = ttk.Button(self.pnlOptions, text='Select All', command=self.songList.select_all)
        self.pnlOptions.btnConvert = ttk.Button(self.pnlOptions, text='Convert', command=self.on_convert_pressed, state=DISABLED)
        self.pnlOptions.lblSelCnt = ttk.Label(self.pnlOptions, text='Selected 0 songs')

        self.master.winfo_toplevel().config(menu=self.menu)
        self.songList.grid(row=0, column=0, sticky='nsew')
        self.songPreview.grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.pnlOptions.grid(row=2, sticky='we')
        self.pnlOptions.btnConvert.pack(side=RIGHT)
        self.pnlOptions.btnSelAll.pack(side=RIGHT)
        self.pnlOptions.lblSelCnt.pack(side=LEFT)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.songList.bind('<<selectedSong>>', self.on_song_selected)

    def on_song_selected(self, ev):
        self.songPreview.set_song()
        if len(gbl.songIdSelections) > 0:
            self.pnlOptions.btnConvert.state(['!disabled'])
        else:
            self.pnlOptions.btnConvert.state(['disabled'])
        size = '{}/{}'.format(len(gbl.songIdSelections), len(gbl.songDb.tree))
        if len(gbl.songIdSelections) == 1:
            self.pnlOptions.lblSelCnt.configure(text='Selected {} song'.format(size))
        else:
            self.pnlOptions.lblSelCnt.configure(text='Selected {} songs'.format(size))

    def on_convert_pressed(self):
        try:
            ffmpeg.input('').output('').run()
        except FileNotFoundError:
            messagebox.showerror('Error', 'Could not find ffmpeg for conversion. Check that it\'s in your PATH or set its location in Settings.')
            return
        except Exception:
            pass
        cpreTl = Toplevel(self)
        conversionPreview = ConvertWindow(cpreTl)
        cpreTl.mainloop()

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
    gbl.songDb = Database(contentPath)

    # start main application
    root = Tk()
    main = MainApp(root)
    main.mainloop()
    