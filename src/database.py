import xml.etree.ElementTree as ET
from os.path import exists, isfile, basename
from collections import OrderedDict

from structs import *
from util import open_contents_db

def tempo_str(low, high):
    if(low == high):
        return str(int(int(low)/100))

    nLow = int(int(low)/100)
    nHigh = int(int(high)/100)
    return str('{}-{}'.format(nLow, nHigh))

# DB for song metadata
class Database:
    def __init__(self, contentPath: str):
        fileDB = open_contents_db(contentPath)
        xmlStr = fileDB.read()
        self.tree = ET.fromstring(xmlStr)

        self.songs = OrderedDict()
        for elem in self.tree:
            info = elem.find('info')
            self.songs[elem.get('id')] = Song(elem.get('id'),
                info.find('title_name').text,
                info.find('artist_name').text,
                info.find('version').text,
                tempo_str(info.find('bpm_min').text, info.find('bpm_max').text),
                [])
            diffs = elem.find('difficulty')
            for diff in diffs:
                if diff.find('illustrator').text != 'dummy' and diff.find('effected_by').text != 'dummy':
                    self.songs[elem.get('id')].diffArr.append(Difficulty(diff.find('difnum').text,
                        diff.find('effected_by').text,
                        diff.find('illustrator').text))

    
    # returns array of songs' names
    def get_song_content(self):
        for song in self.tree:
            print('----------------------------------')
            for child in song.find('info'):
                print('{}: {}'.format(child.tag, child.text))