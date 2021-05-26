from collections import namedtuple

song = namedtuple('song', 'id title artist version tempo diffArr')
# num: 0=nov, 1=adv, 2=exh, 3=inf/mxm
difficulty = namedtuple('difficulty', 'num effector illustrator')