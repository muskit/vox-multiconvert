from os import system, name
import subprocess
from tkinter import ttk
import ffmpeg

import config

MUSIC_DB_PATH = 'data/others/music_db.xml'
MUSIC_PATH = 'data/music'
VERSION_GAME = {
    '1': "SOUND VOLTEX BOOTH",
    '2': "SOUND VOLTEX II -infinite infection-",
    '3': "SOUND VOLTEX III GRAVITY WARS",
    '4': "SOUND VOLTEX IV HEAVENLY HAVEN",
    '5': "SOUND VOLTEX VIVID WAVE",
    '6': "SOUND VOLTEX EXCEED GEAR"
}
DIFF_VOX2KSH = {
    'novice': 'light',
    'advanced': 'challenge',
    'exhaust': 'extended',
    'infinite': 'infinite',
    'maximum': 'infinite'
}

DIFF_ABBRV = {
    'novice': 'nov',
    'advanced': 'adv',
    'exhaust': 'exh',
    'infinite': 'inf',
    'maximum': 'mxm'
}

SONGID_BLACKLIST = ('1438', '1259')

CONVERT_STAT = {
    -1: '',
    0: 'creating directory',
    1: 'converting chart',
    2: 'converting audio'
}

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.field_style = kwargs.pop("style", "TEntry")
        self.placeholder_style = kwargs.pop("placeholder_style", self.field_style)
        self["style"] = self.placeholder_style

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.field_style

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style

def open_contents_db(path: str):
    return open('{}/{}'.format(path, MUSIC_DB_PATH), 'r', encoding='shift_jisx0213')

def content_path_valid(path: str):
    try:
        open_contents_db(path)
    except Exception:
        return False
    return True

def cls():
    # for windows
    if name == 'nt':
        system('cls')
    # for mac and linux (os.name is probably 'posix')
    else:
        system('clear')

# if returns non-zero, raises error
def test_ffmpeg():
    subprocess.check_call(['ffmpeg' if config.ffmpegPath == '' else config.ffmpegPath, '-version'], stdout=subprocess.DEVNULL)