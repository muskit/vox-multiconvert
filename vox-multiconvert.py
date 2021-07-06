#!/usr/bin/env python3
from util import cls

from database import *
from ui import ui_start
import config

def main():
    # contentPath = input("insert dir here\n")
    # contentPath = '/Users/alex/Desktop/KFC/contents'
    # db = Database(contentPath)
    
    config.init()
    ui_start()

if __name__ == '__main__':
    main()
