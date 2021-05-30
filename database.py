import xml.etree.ElementTree as ET
from os.path import exists, isfile, basename
import os
from collections import OrderedDict
import re
import datetime

from structs import *
from util import *

def tempo_str(low, high):
    if(low == high):
        return str(int(int(low)/100))

    nLow = int(int(low)/100)
    nHigh = int(int(high)/100)
    return str('{}-{}'.format(nLow, nHigh))

# DB for song metadata
class Database:
    def __init__(self, contentPath: str):
        self.contentPath = contentPath
        fileDB = open_contents_db(self.contentPath)
        xmlStr = fileDB.read()
        self.tree = ET.fromstring(xmlStr)

        self.songs = OrderedDict()
        for elem in self.tree:
            info = elem.find('info')
            id = elem.get('id')
            if id in SONGID_BLACKLIST: continue
            self.songs[id] = Song(id,
                '{}_{}'.format(id.zfill(4), info.find('ascii').text),
                info.find('title_name').text,
                info.find('artist_name').text,
                info.find('version').text,
                datetime.datetime.strptime(info.find('distribution_date').text, '%Y%m%d'),
                tempo_str(info.find('bpm_min').text, info.find('bpm_max').text),
                [])
                
            charts = self.get_chart_paths(id)
            chartIdx = 0
            diffs = elem.find('difficulty')
            for diff in diffs:
                if diff.find('illustrator').text != 'dummy' and diff.find('effected_by').text != 'dummy':
                    self.songs[id].diffArr.append(Difficulty(diff.tag,
                        diff.find('difnum').text,
                        charts[chartIdx],
                        diff.find('effected_by').text,
                        None, # TODO: rework; img not indexed correctly (edge case: song ID 223)
                        None,
                        diff.find('illustrator').text))
                    chartIdx += 1

            jackets = self.get_jacket_paths(id)
            if len(jackets) <= 0: return
            jktIdx = len(jackets) - 1
            for idx, diff in reversed(list(enumerate(self.songs[id].diffArr))):
                self.songs[id].diffArr[idx] = diff._replace(illustIdx = jktIdx, illustPath = jackets[jktIdx])
                jktIdx -= 1 if jktIdx > 0 else 0
    
    def __getitem__(self, key):
        return self.songs[key]

    def get_jacket_paths(self, id):
        song = self.songs[id]
        if song == None:
            return []
        path = '{}/{}/{}/'.format(self.contentPath, MUSIC_PATH, song.folder)
        for (root, dirs, files) in os.walk(path):
            return sorted([file for file in files
                if re.search(r'b.png$', file)])

    def get_chart_paths(self, id):
        song = self.songs[id]
        if song == None:
            return []
        path = '{}/{}/{}/'.format(self.contentPath, MUSIC_PATH, song.folder)
        for (root, dirs, files) in os.walk(path):
            return sorted([file for file in files
                if re.search(r'.vox$', file)])
    
    # returns array of songs' names
    def get_song_content(self):
        for song in self.tree:
            print('----------------------------------')
            for child in song.find('info'):
                print('{}: {}'.format(child.tag, child.text))