## Conversion functions
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
            'somejacket.jpg',
            diff.illustrator,
            DIFF_VOX2KSH[diff.tag],
            diff.num
        )
        chartPath = '{}/{}'.format(songPath, diff.chartPath)
        ksh = vox2ksh(chartPath)[0]
        with open('test{}.ksh'.format(idx), 'w', encoding="utf-8-sig") as f:
            f.write(prependCom + prependDif + PREPEND_CONST + ksh)

# .s3v ---> music.ogg
# TODO: add preview
def convert_audio(song: Song):
    pass