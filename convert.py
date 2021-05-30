## Conversion functions
import os
import errno
import ffmpeg
import shutil

from VOX2KSH.v2k import vox2ksh

import gbl
from structs import *
from util import *

PREPEND_COMMON = \
'''title={}
artist={}
icon=../../sdvx{}.png
t={}
'''
PREPEND_DIFF = \
'''effect={}
jacket={}
illustrator={}
difficulty={}
level={}
'''
PREPEND_CONST = \
'''m=music.ogg
ver=167
bg=deepsea
layer=wave
mvol=91
pfiltergain=46
filtertype=peak
chokkakuautovol=0
chokkakuvol=65
'''

'''
=====PREPEND PROPERTIES=====
title=
artist=
icon=../../sdvxN.png
t=<str>
po=<preview offset>
plength=<preview length>
=====DIFFICULTY DEPENDENT=====
effect=
jacket=
illustrator=
difficulty=
level=
=====CONSTANT FOOTER=====
m=music.ogg
ver=167
bg=deepsea
layer=wave
mvol=91
pfiltergain=46
filtertype=peak
chokkakuautovol=0
chokkakuvol=65
'''

def create_song_directory(songId):
    newDir = '{}/{}/'.format(gbl.exportDir, gbl.songDb[songId].folder)
    if not os.path.exists(os.path.dirname(newDir)):
        try:
            os.makedirs(os.path.dirname(newDir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

# 1. convert notes
# 2. prepend metadata
# 3. copy jacket(s)
def convert_chart(songId):
    song = gbl.songDb[songId]
    songPath = '{}/{}/{}'.format(gbl.songDb.contentPath, MUSIC_PATH, song.folder)
    prependCom = PREPEND_COMMON.format(
        song.title,
        song.artist,
        song.version,
        song.tempo
    )
    for idx, diff in enumerate(song.diffArr):
        prependDif = PREPEND_DIFF.format(
            diff.effector,
            '{}.png'.format(diff.illustIdx),
            diff.illustrator,
            DIFF_VOX2KSH[diff.tag],
            diff.num
        )
        chartPath = '{}/{}'.format(songPath, diff.chartPath)
        ksh: str = vox2ksh(chartPath)[0]
        ksh.replace
        with open('{}/{}/{}.ksh'.format(gbl.exportDir, song.folder, DIFF_ABBRV[diff.tag]), 'w', encoding="utf-8-sig", newline='\r\n') as f:
            f.write(prependCom + prependDif + PREPEND_CONST + ksh)
        illustExPath = '{}/{}/{}.png'.format(gbl.exportDir, song.folder, diff.illustIdx)
        if not os.path.exists(illustExPath):
            shutil.copy('{}/{}'.format(songPath, diff.illustPath), illustExPath)

# .s3v ---> music.ogg
# TODO: add preview
def convert_audio(songId):
    songText = gbl.songDb[songId].folder
    fullSongFolder = '{}/{}/{}'.format(gbl.songDb.contentPath, MUSIC_PATH, songText)
    inFile = '{}/{}.s3v'.format(fullSongFolder, songText)
    outFile = '{}/{}/music.ogg'.format(gbl.exportDir, songText)
    ffmpeg.input(inFile) \
        .audio \
        .output(outFile) \
        .global_args('-loglevel', 'error') \
        .run()