from collections import namedtuple

Song = namedtuple('Song', 'id folder title artist version tempo diffArr')
# num: 0=nov, 1=adv, 2=exh, 3=inf/mxm
Difficulty = namedtuple('Difficulty', 'tag num effector illustPath illustrator')