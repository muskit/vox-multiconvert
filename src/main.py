from util import cls
from database import *
from ui import ui_loop

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

def main():
    # contentPath = input("insert dir here\n")
    # contentPath = '/Users/alex/Desktop/KFC/contents'
    # db = Database(contentPath)
    ui_loop()

if __name__ == '__main__':
    main()
