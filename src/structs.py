from collections import namedtuple

Song = namedtuple('Song', 'id title artist version tempo diffArr')
# num: 0=nov, 1=adv, 2=exh, 3=inf/mxm
Difficulty = namedtuple('Difficulty', 'num effector illustrator')