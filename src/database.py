import xml.etree.ElementTree as ET
from os.path import exists, isfile, basename

# DB for song metadata
class Database:
    def __init__(self, contentPath: str):
        try:
            fileDB = open('{}/data/others/music_db.xml'.format(contentPath), 'r', encoding='shift_jisx0213')
            xmlStr = fileDB.read()
            self.tree = ET.fromstring(xmlStr)
        except FileNotFoundError:
            print("Couldn't find data/others/music_db.xml")
            return
        except Exception:
            print("Error occured reading data/others/music_db.xml")
    
    # returns array of songs' names
    def get_song_content(self):
        for song in self.tree:
            print('----------------------------------')
            for child in song.find('info'):
                print('{}: {}'.format(child.tag, child.text))